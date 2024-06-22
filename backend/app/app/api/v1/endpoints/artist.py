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







