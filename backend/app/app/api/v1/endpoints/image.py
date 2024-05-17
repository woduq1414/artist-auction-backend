
import datetime
import random
import string
import uuid
from app.models.image_media_model import ImageMedia
from app.models.media_model import Media
from app.schemas.image_media_schema import IImageMediaRead
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
    return "".join(
        random.choices(string.ascii_letters + string.digits, k=length)
    )


@router.post("/")
async def upload_images(
    # title: str | None = Body(None),
    # description: str | None = Body(None),
    files: list[UploadFile] = File(...),
    # current_user: User = Depends(deps.get_current_user()),
    minio_client: MinioClient = Depends(deps.minio_auth),
) -> IPostResponseBase[list[IImageMediaRead]]:
    """
    Uploads images
    """

    result = []

    for image_file in files:
 
        try:
            description = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            image_modified = modify_image(BytesIO(image_file.file.read()))
            data_file = minio_client.put_object(
                file_name= str(uuid.uuid4()) + "." + image_modified.file_format,
                file_data=BytesIO(image_modified.file_data),
                content_type=image_file.content_type,
            )
            media = IMediaCreate(
                title=image_file.filename, description=description, path=data_file.file_name
            )

            image_media = ImageMedia(
                media=Media.from_orm(media),
                height=image_modified.height,
                width=image_modified.width,
                file_format=image_modified.file_format,
            )
            result.append(image_media)

        except Exception as e:
            print(e)
            return Response("Internal server error", status_code=500)
    return create_response(data=result) # type: ignore

