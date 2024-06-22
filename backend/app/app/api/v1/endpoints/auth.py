from app.schemas.artist_schema import IArtistInfoEdit, IArtistInfoRead, IArtistRegister
from app.schemas.common_schema import IAccountTypeEnum, ILoginTypeEnum
from app.schemas.account_schema import IAccountBasicInfo, IAccountRead
from app.schemas.company_schema import (
    ICompanyInfoEdit,
    ICompanyInfoRead,
    ICompanyRegister,
)
from fastapi import HTTPException
from io import BytesIO
from typing import Annotated, Any
from uuid import UUID

from redis.asyncio import Redis
from app.api.v1.endpoints.role import update_role
from app.models.group_model import Group
from app.models.links_model import LinkGroupUser
from app.utils.exceptions import (
    IdNotFoundException,
    SelfFollowedException,
    UserFollowedException,
    UserNotFollowedException,
    UserSelfDeleteException,
)
from app import crud
from app.api import deps
from app.deps import user_deps, role_deps, auth_deps
from app.models import User, UserFollow
from app.models.role_model import Role
from app.utils.login import verify_kakao_access_token
from app.utils.minio_client import MinioClient
from app.utils.resize_image import modify_image
from app.utils.email import send_security_code_mail, verify_security_code
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Query,
    Response,
    UploadFile,
    status,
)
from app.schemas.media_schema import IMediaCreate
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum, IRoleRead, IRoleUpdate
from app.schemas.user_follow_schema import IUserFollowRead
from app.schemas.user_schema import (
    IUserCreate,
    IUserRead,
    IUserReadTrivial,
    IUserReadWithoutGroups,
    IUserStatus,
)
from app.schemas.user_follow_schema import (
    IUserFollowReadCommon,
)
from fastapi_pagination import Params
from sqlmodel import and_, select, col, or_, text

import requests
from jose import jwt
import base64
import json
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse

from datetime import timedelta
import json
from redis.asyncio import Redis
import requests
from app.core import security
from app.core.config import Settings

from app.models.user_model import User
from app.models.account_model import Account
from app.schemas.common_schema import TokenType
from app.schemas.token_schema import Token, TokenRead
from app.utils.token import add_token_to_redis, get_valid_tokens
from app.deps import user_deps, role_deps, auth_deps
from app.core.config import settings

from fastapi.security import OAuth2PasswordRequestForm


router = APIRouter()


@router.get("/check-nickname")
async def check_nickname_api(nickname: str = Query(...)) -> IGetResponseBase[None]:
    """
    Check if nickname exists
    """

    await auth_deps.nickname_exists(nickname)

    return create_response(data=None)


@router.put("/profile-image")
async def update_profile_image(
    image_media_id: UUID,
    current_account: Account = Depends(deps.get_current_account()),
    db_session=Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
):
    """
    Updates the profile image of the user
    """
    print(image_media_id)

    image_media = await crud.image.get_image_media_by_id(
        id=image_media_id, db_session=db_session
    )

    if current_account.artist_id:
        artist = current_account.artist
        artist.profile_image = image_media
        db_session.add(artist)
    elif current_account.company_id:
        company = current_account.company
        company.profile_image = image_media
        db_session.add(company)
    await db_session.commit()

    data = await auth_deps.get_token_by_account(
        account=current_account, redis_client=redis_client
    )

    response = create_response(data={"accessToken": data.access_token})

    return response


@router.get("/me")
async def get_me(
    current_account: Account = Depends(deps.get_current_account()),
) -> IGetResponseBase[IArtistInfoRead]:
    """
    Get current user
    """

    if current_account.account_type == IAccountTypeEnum.artist:
        artist = current_account.artist
        result = IArtistInfoRead(
            id=current_account.id,
            account_type=current_account.account_type,
            name=current_account.name,
            email=current_account.email,
            nickname=artist.nickname,
            profile_image=artist.profile_image,
        )
        return create_response(data=result)


@router.get("/social/kakao")
async def social_kakao_redirect(
    params: Params = Depends(),
    code: str = Query(...),
    redis_client: Redis = Depends(deps.get_redis_client),
):
    """
    Redirect
    """

    res = requests.post(
        "https://kauth.kakao.com/oauth/token",
        {
            "grant_type": "authorization_code",
            "client_id": "9a022bf07d96f5bd196f5223293c1f0e",
            "redirect_uri": settings.BACKEND_URL + "/api/v1/auth/social/kakao",
            "code": code,
        },
    )

    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Kakao login failed")
    else:
        access_token = res.json()["access_token"]
        kakao_id = verify_kakao_access_token(kakao_access_token=access_token)

        account = await crud.account.get_by_social_id(social_id=kakao_id)

        if account:
            response = RedirectResponse(url=settings.FRONTEND_URL + "/")

            data = await auth_deps.get_token_by_account(
                account=account, redis_client=redis_client
            )
            print(account)

            response.set_cookie(
                key="accessToken",
                value=data.access_token,
                domain=(
                    "127.0.0.1"
                    if ("127.0.0.1" in settings.BACKEND_URL)
                    else ".artistauction.kro.kr"
                ),
            )

            return response
        else:
            response = RedirectResponse(
                url=settings.FRONTEND_URL + "/auth/new?loginType=kakao"
            )
            response.set_cookie(
                key="socialLoginInfo",
                value=base64.b64encode(
                    json.dumps(
                        {"loginType": "kakao", "accessToken": access_token}
                    ).encode("utf-8")
                ).decode("utf-8"),
                domain=(
                    "127.0.0.1"
                    if ("127.0.0.1" in settings.BACKEND_URL)
                    else ".artistauction.kro.kr"
                ),
            )
            return response


@router.post("/artist", status_code=status.HTTP_201_CREATED)
async def register_artist(
    register_data: IArtistRegister,
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[Any]:
    """
    Register a new user
    """

    await auth_deps.email_exists(register_data.email)
    await auth_deps.nickname_exists(register_data.nickname)

    if register_data.login_type != ILoginTypeEnum.password:
        await auth_deps.social_id_exists(register_data.social_id)

    if register_data.login_type == ILoginTypeEnum.kakao:
        kakao_id = verify_kakao_access_token(kakao_access_token=register_data.social_id)
        if not kakao_id:
            raise HTTPException(status_code=400, detail="Kakao login failed")
        else:
            register_data.social_id = kakao_id

    artist = await crud.artist.create(obj_in=register_data)
    register_data.artist_id = artist.id

    account = await crud.account.create(obj_in=register_data)

    data = await auth_deps.get_token_by_account(
        account=account, redis_client=redis_client
    )
    response = create_response(data={"accessToken": data.access_token})

    return response


@router.post("/company", status_code=status.HTTP_201_CREATED)
async def register_company(
    register_data: ICompanyRegister,
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[Any]:
    """
    Register a new user
    """

    await auth_deps.email_exists(register_data.email)
    await auth_deps.nickname_exists(register_data.nickname)

    if register_data.login_type != ILoginTypeEnum.password:
        await auth_deps.social_id_exists(register_data.social_id)

    if register_data.login_type == ILoginTypeEnum.kakao:
        kakao_id = verify_kakao_access_token(kakao_access_token=register_data.social_id)
        if not kakao_id:
            raise HTTPException(status_code=400, detail="Kakao login failed")
        else:
            register_data.social_id = kakao_id

    artist = await crud.company.create(obj_in=register_data)
    register_data.company_id = artist.id

    account = await crud.account.create(obj_in=register_data)

    data = await auth_deps.get_token_by_account(
        account=account, redis_client=redis_client
    )
    response = create_response(data={"accessToken": data.access_token})

    return response


@router.post("/login")
async def login(
    email: str = Body(...),
    password: str = Body(...),
    redis_client: Redis = Depends(deps.get_redis_client),
):
    """
    Login
    """

    account = await crud.account.authenticate(email=email, password=password)

    if not account:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    data = await auth_deps.get_token_by_account(
        account=account, redis_client=redis_client
    )

    # response = RedirectResponse(url=settings.FRONTEND_URL + "/")
    response = create_response(data={"accessToken": data.access_token})

    # response.set_cookie(
    #     key = "accessToken",
    #     value = data.access_token
    # )

    return response


@router.post("/access-token")
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> TokenRead:
    """
    OAuth2 compatible token login, get an access token for future requests
    """

    account = await crud.account.authenticate(
        email=form_data.username, password=form_data.password
    )

    if not account:
        raise HTTPException(
            status_code=400, detail="Email or Password incorrect | Not Kakao Registered"
        )

    data = await auth_deps.get_token_by_account(
        account=account, redis_client=redis_client
    )

    return {
        "access_token": data.access_token,
        "token_type": "bearer",
    }


@router.get("/check-email")
async def check_email(email: str = Query(...)) -> IGetResponseBase[None]:
    """
    Check if email exists
    """

    await auth_deps.email_exists(email)

    return create_response(data=None)


@router.get("/edit-profile")
async def edit_profile_form(
    current_account: Account = Depends(deps.get_current_account()),
) -> IGetResponseBase[IArtistInfoEdit | ICompanyInfoEdit]:
    """
    Get current user
    """

    if current_account.account_type == IAccountTypeEnum.artist:
        artist = current_account.artist
        print(artist.nickname, "!@#!@#")
        result = IArtistInfoEdit(
            id=current_account.id,
            account_type=current_account.account_type,
            name=current_account.name,
            email=current_account.email,
            nickname=artist.nickname,
            content=artist.content,
            # content = '123132',
            description=artist.description,
        )
        return create_response(data=result)

    elif current_account.account_type == IAccountTypeEnum.company:
        company = current_account.company
        result = ICompanyInfoEdit(
            id=current_account.id,
            account_type=current_account.account_type,
            name=current_account.name,
            email=current_account.email,
            nickname=company.nickname,
            content=company.content,
            description=company.description,
        )
        return create_response(data=result)


@router.put("/edit-profile")
async def edit_profile(
    edit_data: IArtistInfoEdit | ICompanyInfoEdit,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
    db_session=Depends(deps.get_db),
):
    """
    Edit profile
    """

    if current_account.account_type == IAccountTypeEnum.artist:
        artist = current_account.artist
        current_nickname = artist.nickname
        if edit_data.nickname is not None and current_nickname != edit_data.nickname:
            await auth_deps.nickname_exists(edit_data.nickname)
            artist.nickname = edit_data.nickname

        if edit_data.password is not None:
            artist.password = security.get_password_hash(edit_data.password)

        if edit_data.content is not None:
            artist.content = edit_data.content

        if edit_data.description is not None:
            artist.description = edit_data.description

        await crud.artist.update(obj_in=artist, db_session=db_session)

        data = await auth_deps.get_token_by_account(
            account=current_account, redis_client=redis_client
        )

        response = create_response(data={"accessToken": data.access_token})
        return response

    elif current_account.account_type == IAccountTypeEnum.company:

        company = current_account.company
        current_nickname = company.nickname
        if edit_data.nickname is not None and current_nickname != edit_data.nickname:
            await auth_deps.nickname_exists(edit_data.nickname)
            company.nickname = edit_data.nickname

        if edit_data.password is not None:
            company.password = security.get_password_hash(edit_data.password)

        if edit_data.content is not None:
            company.content = edit_data.content

        if edit_data.description is not None:
            company.description = edit_data.description

        await crud.company.update(obj_in=company, db_session=db_session)

        data = await auth_deps.get_token_by_account(
            account=current_account, redis_client=redis_client
        )

        response = create_response(data={"accessToken": data.access_token})
        return response


@router.get("/profile/{account_id}")
async def get_account_profile(
    account_id: UUID,
) -> IGetResponseBase[IArtistInfoRead | ICompanyInfoRead]:
    """
    Gets the profile of the user
    """

    account = await crud.account.get(id=account_id)
    if account is None:
        raise IdNotFoundException(Account, account_id)
    if account.artist_id:
        artist = await crud.artist.get(id=account.artist_id)
        return create_response(data=artist)
    elif account.company_id:
        company = await crud.company.get(id=account.company_id)
        return create_response(data=company)


@router.get("/artist/{artist_id}")
async def get_account_id_by_artist_id(
    artist_id: UUID,
) -> IGetResponseBase[IAccountBasicInfo]:
    """
    Gets the profile of the user
    """

    account = await crud.account.get_by_artist_id(artist_id=artist_id)
    if account is None:
        raise IdNotFoundException(Account, artist_id)
    return create_response(data=account)


@router.get("/company/{company_id}")
async def get_account_id_by_company_id(
    company_id: UUID,
) -> IGetResponseBase[IAccountBasicInfo]:
    """
    Gets the profile of the user
    """

    account = await crud.account.get_by_company_id(company_id=company_id)
    if account is None:
        raise IdNotFoundException(Account, company_id)

    return create_response(data=account)
