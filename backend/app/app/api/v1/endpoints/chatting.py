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
from app.schemas.chatting_schema import (
    IChattingCreate,
    IChattingMessageCreate,
    IChattingRead,
)
from app.models.artist_model import Artist
from app.models.company_model import Company
from app.schemas.notify_schema import INotifyCreate
from app.utils.notify import make_notify
from fastapi import HTTPException
from io import BytesIO
from typing import Annotated, Any, Optional
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


@router.get("/list")
async def get_chatting_list(
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IGetResponseBase[list[IChattingRead]]:
    """
    Get a user by id
    """

    current_account_type = current_account.account_type
    chatting_list = []
    if current_account_type == "artist":
        chatting_list = await crud.chatting.get_by_artist_id(
            artist_id=current_account.artist_id,
        )

    elif current_account_type == "company":
        chatting_list = await crud.chatting.get_by_company_id(
            company_id=current_account.company_id,
        )

    return create_response(data=chatting_list)


@router.get("/{target_user_id}")
async def get_chatting_room(
    target_user_id: UUID,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> Any:
    """
    Get a user by id
    """

    current_account_type = current_account.account_type
    target_user = None
    chatting = None
    if current_account_type == "artist":
        chatting = await crud.chatting.get_by_users(
            artist_id=current_account.artist_id,
            company_id=target_user_id,
        )

    elif current_account_type == "company":
        chatting = await crud.chatting.get_by_users(
            artist_id=target_user_id,
            company_id=current_account.company_id,
        )

    if not chatting:
        raise IdNotFoundException(User, target_user_id)

    redis_key = f"chatting:{chatting.artist_id}-{chatting.company_id}"

    chatting_data = await redis_client.lrange(redis_key, 0, -1)

    def processChattingData(data):

        data["sender"] = "you" if data["from"] == str(target_user_id) else "me"
        return data

    if not chatting_data:
        chatting_data = []
    else:
        chatting_data = [
            processChattingData(json.loads(data)) for data in chatting_data
        ]

    result = IChattingRead(
        id=chatting.id,
        artist=chatting.artist if current_account_type == "company" else None,
        company=chatting.company if current_account_type == "artist" else None,
        created_at=chatting.created_at,
        content=chatting_data,
    )

    return create_response(data=result)


@router.post("/{target_user_id}")
async def make_chatting_room(
    target_user_id: UUID,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> Any:
    """
    Get a user by id
    """

    current_account_type = current_account.account_type
    target_user = None
    chatting = None

    if current_account_type == "artist":

        target_user = await crud.company.get(id=target_user_id)
        if not target_user:
            raise IdNotFoundException(Artist, target_user_id)

        old_chatting = await crud.chatting.get_by_users(
            artist_id=current_account.artist_id,
            company_id=target_user_id,
        )
        if old_chatting:
            # raise 409 conflict error
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chatting room already exist",
            )

        chatting = await crud.chatting.create(
            obj_in=IChattingCreate(
                artist_id=current_account.artist_id,
                company_id=target_user_id,
            ),
            is_update=False,
        )

    elif current_account_type == "company":
        target_user = await crud.artist.get(id=target_user_id)

        if not target_user:
            raise IdNotFoundException(Company, target_user_id)
        old_chatting = await crud.chatting.get_by_users(
            artist_id=target_user_id,
            company_id=current_account.company_id,
        )
        if old_chatting:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chatting room already exist",
            )

        chatting = await crud.chatting.create(
            obj_in=IChattingCreate(
                artist_id=target_user_id,
                company_id=current_account.company_id,
            ),
            is_update=False,
        )

    chatting_data = []

    return create_response(data=chatting)


@router.put("/{target_user_id}")
async def add_chat(
    target_user_id: UUID,
    data: IChattingMessageCreate,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> Any:
    """
    Get a user by id
    """

    message, type = data.message, data.type

    current_account_type = current_account.account_type
    target_user = None
    chatting = None
    my_user_id = None
    if current_account_type == "artist":
        chatting = await crud.chatting.get_by_users(
            artist_id=current_account.artist_id,
            company_id=target_user_id,
        )
        my_user_id = current_account.artist_id

    elif current_account_type == "company":
        chatting = await crud.chatting.get_by_users(
            artist_id=target_user_id,
            company_id=current_account.company_id,
        )
        my_user_id = current_account.company_id

    if not chatting:
        raise IdNotFoundException(User, target_user_id)

    redis_key = f"chatting:{chatting.artist_id}-{chatting.company_id}"

    data = {
        "created_at": int(time.time() * 1000),
        "from": str(my_user_id),
        "type": type,
        "message": message,
    }

    await redis_client.rpush(redis_key, json.dumps(data))

    data["sender"] = "you"

    await make_notify(
        is_save=False,
        redis=redis_client,
        message=INotifyCreate(
            receiver_id=[target_user_id],
            title=f"[{current_account.artist.nickname if current_account_type == 'artist' else current_account.company.nickname}]님으로부터 새로운 메시지가 도착했습니다.",
            description=json.dumps(data),
            type="chatting_message",
            action=f"",
            created_at=int(time.time() * 1000),
        ),
    )

    return create_response(data=data)
