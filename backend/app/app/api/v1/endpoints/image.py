import datetime
import random
import string
import uuid
from app.models.image_media_model import ImageMedia
from app.models.media_model import Media
from app.schemas.image_media_schema import IImageMediaRead
from app.models.account_model import Account
from fastapi import HTTPException
from io import BytesIO
from typing import Annotated
from uuid import UUID

import cloudinary.uploader


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
    IUserReadWithoutGroups,
    IUserStatus,
)
from app.schemas.user_follow_schema import (
    IUserFollowReadCommon,
)
from fastapi_pagination import Params
from sqlmodel import and_, select, col, or_, text

router = APIRouter()


def generate_random_string(length: int = 6) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


@router.post("/")
async def upload_images(
    type: str | None = Query(None),
    # title: str | None = Body(None),
    # description: str | None = Body(None),
    to_db: bool = Query(True),
    files: list[UploadFile] = File(...),
   
    current_account: Account = Depends(deps.get_current_account()),
    db_session=Depends(deps.get_db),
) -> IPostResponseBase[list[IImageMediaRead]]:
    """
    Uploads images
    """


    account_id = current_account.id



    result = await crud.image.upload_images(
        image_list=files, account_id=account_id, db_session=db_session, to_db = to_db
    )
    
    print(result)


    return create_response(data=result)  # type: ignore
