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




@router.get("/check-nickname")
async def check_artist_nickname(nickname: str = Query(...)) -> IGetResponseBase[None]:
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


