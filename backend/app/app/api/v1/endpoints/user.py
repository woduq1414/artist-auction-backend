from fastapi import HTTPException
from io import BytesIO
from typing import Annotated
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
from app.deps import user_deps, role_deps
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

router = APIRouter()


@router.get("/list")
async def read_users_list(
    params: Params = Depends(),
    current_user: User = Depends(
        deps.get_current_user(
            required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IGetResponsePaginated[IUserRead]:
    """
    Retrieve users. Requires admin or manager role

    Required roles:
    - admin
    - manager
    """
    users = await crud.user.get_multi_paginated(params=params)
    return create_response(data=users)


@router.get("/list/trivial")
async def read_users_list_trivial(
    params: Params = Depends(),
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IGetResponsePaginated[IUserReadTrivial]:
    """
    Retrieve trivial info of users
    """
    users = await crud.user.get_multi_paginated(params=params)
    return create_response(data=users)







@router.get("/list/by_group_id/{group_id}")
async def read_users_list_by_group_name(
    group_id: UUID,
    user_status: Annotated[
        IUserStatus,
        Query(
            title="User status",
            description="User status, It is optional. Default is active",
        ),
    ] = IUserStatus.active,
    params: Params = Depends(),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IGetResponsePaginated[IUserReadWithoutGroups]:
    """
    Retrieve users by role name and status. Requires admin role

    Required roles:
    - admin
    """
    user_status = True if user_status == IUserStatus.active else False
    # query = (
    #     select(User)
    #     .join(Role, User.role_id == Group.id)
    #     .where(
    #         and_(
    #             col(Role.name).ilike(f"%{role_name}%"),
    #             User.is_active == user_status,
    #         )
    #     )
    #     .order_by(User.first_name)
    # )

    target_group = await crud.group.get_group_by_id(group_id=group_id)
    if not target_group:
        raise IdNotFoundException(model=Group, id=group_id)

    query = (
        select(User)
        .join(LinkGroupUser)
        .join(Group)
        .where(
            and_(
                Group.id == group_id,
                User.is_active == user_status,
            )
        )

    )

    users = await crud.user.get_multi_paginated(query=query, params=params)
    return create_response(data=users)




# @router.get("/order_by_created_at")
# async def get_hero_list_order_by_created_at(
#     params: Params = Depends(),
#     current_user: User = Depends(
#         deps.get_current_user(
#             required_roles=[IRoleEnum.admin, IRoleEnum.manager])
#     ),
# ) -> IGetResponsePaginated[IUserReadWithoutGroups]:
#     """
#     Gets a paginated list of users ordered by created datetime

#     Required roles:
#     - admin
#     - manager
#     """
#     users = await crud.user.get_multi_paginated_ordered(
#         params=params, order_by="created_at"
#     )
#     return create_response(data=users)



# (카톡)로그인 프로세스 : 관리자가 미리 정보를 등록 -> 사용자가 카카오 로그인 버튼을 클릭하여 카카오 access token 받음 -> db에 있는 kakao id면 로그인, 없으면 회원가입 페이지로
# 회원가입 프로세스 : 사용자가 email을 입력 -> db에 있는 non active User이면 인증 메일 전송 -> 인증 번호 정확히 입력하면 해당 이메일 유저의 is_active, kakao_id 값 변경 후 로그인
  

@router.get("/check-email")
async def get_is_valid_email(
    email: str = Depends(user_deps.is_valid_email),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IGetResponseBase[dict]:
    """
    Check if email is registered but not active.
    If email is registerd but not active, send security code to email.
    """

    security_code = await send_security_code_mail(email=email, redis_client=redis_client)

    return create_response(data={
        "email": email,
        "security_code": security_code  # 메일 전송 구현 전까지 임시로

    })


@router.post("/verify-email")
async def verify_email(
    email: str = Body(...),
    security_code: str = Body(...),
    kakao_access_token: str = Body(...),
    redis_client: Redis = Depends(deps.get_redis_client),
    # security_code : str = Depends(),
) -> IGetResponseBase[str]:
    """
    Verify email by security code.
    """

    if await verify_security_code(email=email, security_code=security_code, redis_client=redis_client):

        current_user = await crud.user.get_by_email(
            email=email
        )

        kakao_id = verify_kakao_access_token(kakao_access_token)

        if kakao_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid kakao access token")

        await crud.user.make_active(db_obj=current_user, kakao_id=kakao_id)

        return create_response(data="success")
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid security code")



@router.put("/role/{user_id}/{role_id}")
async def update_user_role(
    role_id: UUID,
    target_user: User = Depends(user_deps.is_valid_user),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IPutResponseBase[IRoleRead]:
    """
    Updates a role by its id

    Required roles:
    - admin
    """
    
    updated_role = await crud.role.add_role_to_user(user = target_user, role_id = role_id)

    return create_response(data=updated_role)




@router.get("/{user_id}")
async def get_user_by_id(
    user: User = Depends(user_deps.is_valid_user),
    current_user: User = Depends(
        deps.get_current_user(
            required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IGetResponseBase[IUserRead]:
    """
    Gets a user by his/her id

    Required roles:
    - admin
    - manager
    """
    return create_response(data=user)


@router.get("")
async def get_my_data(
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IUserRead]:
    """
    Gets my user profile information
    """
    return create_response(data=current_user)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_user(
    new_user: IUserCreate = Depends(user_deps.user_exists),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IPostResponseBase[IUserRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """
    user = await crud.user.create_with_role(obj_in=new_user)
    return create_response(data=user)


@router.delete("/{user_id}")
async def remove_user(
    user_id: UUID = Depends(user_deps.is_valid_user_id),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
) -> IDeleteResponseBase[IUserRead]:
    """
    Deletes a user by his/her id

    Required roles:
    - admin
    """
    if current_user.id == user_id:
        raise UserSelfDeleteException()

    user = await crud.user.remove(id=user_id)
    return create_response(data=user, message="User removed")


@router.post("/image")
async def upload_my_image(
    title: str | None = Body(None),
    description: str | None = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_user()),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[IUserRead]:
    """
    Uploads a user image
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(
            title=title, description=description, path=data_file.file_name
        )
        user = await crud.user.update_photo(
            user=current_user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        return create_response(data=user)
    except Exception as e:
        print(e)
        return Response("Internal server error", status_code=500)


@router.post("/{user_id}/image")
async def upload_user_image(
    user: User = Depends(user_deps.is_valid_user),
    title: str | None = Body(None),
    description: str | None = Body(None),
    image_file: UploadFile = File(...),
    current_user: User = Depends(
        deps.get_current_user(required_roles=[IRoleEnum.admin])
    ),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[IUserRead]:
    """
    Uploads a user image by his/her id

    Required roles:
    - admin
    """
    try:
        image_modified = modify_image(BytesIO(image_file.file.read()))
        data_file = minio_client.put_object(
            file_name=image_file.filename,
            file_data=BytesIO(image_modified.file_data),
            content_type=image_file.content_type,
        )
        media = IMediaCreate(
            title=title, description=description, path=data_file.file_name
        )
        user = await crud.user.update_photo(
            user=user,
            image=media,
            heigth=image_modified.height,
            width=image_modified.width,
            file_format=image_modified.file_format,
        )
        return create_response(data=user)
    except Exception as e:
        print(e)
        return Response("Internal server error", status_code=500)
