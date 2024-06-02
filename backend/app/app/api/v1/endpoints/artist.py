import datetime
import json
import time
import uuid
from app.schemas.artist_goods_schema import (
    IArtistGoodsCreate,
    IArtistGoodsListRead,
    IArtistGoodsRead,
    IArtistGoodsUpdate,
)
from app.models.account_model import Account
from app.schemas.artist_schema import IArtistRead
from app.models.artist_goods_model import ArtistGoods
from app.models.image_media_model import ImageMedia
from fastapi import HTTPException
from io import BytesIO
from typing import Annotated, Optional
from uuid import UUID
from fastapi import Form
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
from app.deps import user_deps, role_deps
from app.models import User, UserFollow, Media
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
from pydantic import BaseModel, ValidationError
from app.deps import user_deps, role_deps, auth_deps
import cloudinary.uploader
from app.core.config import settings


router = APIRouter()


class Base(BaseModel):
    name: str
    point: Optional[float] = None
    is_accepted: Optional[bool] = False


@router.get("/goods")
async def get_artist_goods_list(
    params: Params = Depends(),
    category: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
) -> IGetResponsePaginated[IArtistGoodsListRead]:
    """
    Gets a paginated list of projects
    """
    time.sleep(1)
    query = None

    query = select(crud.artist_goods.model).where(
        crud.artist_goods.model.status == "start"
    )

    if category:
        query = query.where(crud.artist_goods.model.category == category)
    else:
        pass

    if search:
        # query by title and description
        query = query.where(
            or_(
                crud.artist_goods.model.title.ilike(f"%{search}%"),
                crud.artist_goods.model.description.ilike(f"%{search}%"),
            )
        )

    available_sort = ["recent", "highPrice", "lowPrice", "end_date"]

    if sort:
        if sort in available_sort:
            if sort == "recent":
                query = query.order_by(crud.artist_goods.model.created_at.desc())
            elif sort == "highPrice":
                query = query.order_by(crud.artist_goods.model.price.desc())
            elif sort == "lowPrice":
                query = query.order_by(crud.artist_goods.model.price.asc())
            elif sort == "end_date":
                query = query.order_by(crud.artist_goods.model.end_date.asc())

    artist_goods_list = await crud.artist_goods.get_multi_paginated(
        params=params, query=query
    )

    for artist_goods in artist_goods_list.data.items:
        artist_goods.example_image_url_list = json.loads(
            artist_goods.example_image_url_list
        )

    # time.sleep(5)

    print(artist_goods_list)
    # artist_goods_list.example_image_url_list = json.loads(artist_goods_list.example_image_url_list)
    # print("!@#!@#", json.loads(artist_goods_list.example_image_url_list))

    return create_response(data=artist_goods_list)


@router.post("/goods", status_code=status.HTTP_201_CREATED)
async def create_artist_goods(
    new_artist_goods: IArtistGoodsCreate,
    current_account: Account = Depends(deps.get_current_account()),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    print(new_artist_goods)

    artist_goods = await crud.artist_goods.create(
        obj_in=new_artist_goods, artist_id=current_account.artist.id
    )

    return create_response(data=artist_goods)


@router.put("/goods",)
async def update_artist_goods(
    # artist_goods_id: UUID,
    new_artist_goods: IArtistGoodsUpdate,
    current_account: Account = Depends(deps.get_current_account()),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    print(new_artist_goods)

    artist_goods = await crud.artist_goods.update(
        obj_in=new_artist_goods, artist_id=current_account.artist.id
    )

    return create_response(data=artist_goods)


@router.get("/goods/my")
async def get_my_artist_goods_list(
    params: Params = Depends(),
    current_account: Account = Depends(deps.get_current_account()),
) -> IGetResponsePaginated[IArtistGoodsListRead]:
    """
    Gets a paginated list of projects
    """

    query = select(crud.artist_goods.model).where(
        crud.artist_goods.model.artist_id == current_account.artist.id
    )

    artist_goods_list = await crud.artist_goods.get_multi_paginated(
        params=params, query=query
    )

    for artist_goods in artist_goods_list.data.items:
        artist_goods.example_image_url_list = json.loads(
            artist_goods.example_image_url_list
        )

    return create_response(data=artist_goods_list)


@router.get("/goods/{artist_goods_id}")
async def get_artist_goods_by_id(
    artist_goods_id: UUID,
    is_edit: bool = Query(False),
    current_account: Account = Depends(
        deps.get_current_account(is_login_required=False)
    ),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Gets a project by its id
    """
    time.sleep(1)

    artist_goods = await crud.artist_goods.get(id=artist_goods_id)

    if artist_goods:

        if is_edit:
            # print(current_account.artist.id, artist_goods.artist_id)
            if (
                current_account is None
                or artist_goods.artist_id != current_account.artist.id
            ):
                raise IdNotFoundException(ArtistGoods, artist_goods_id)

        artist_goods.example_image_url_list = json.loads(
            artist_goods.example_image_url_list
        )

        return create_response(data=artist_goods)
    else:
        raise IdNotFoundException(ArtistGoods, artist_goods_id)


@router.get("/check-nickname")
async def check_artist_nickname(nickname: str = Query(...)) -> IGetResponseBase[None]:
    """
    Check if nickname exists
    """

    await auth_deps.artist_nickname_exists(nickname)

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
    artist = current_account.artist

    image_media = await crud.image.get_image_media_by_id(
        id=image_media_id, db_session=db_session
    )
    artist.profile_image = image_media

    db_session.add(artist)
    await db_session.commit()

    data = await auth_deps.get_token_by_account(
        account=current_account, redis_client=redis_client
    )

    response = create_response(data={"accessToken": data.access_token})

    return response
