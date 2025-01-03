from app.utils.minio_client import MinioClient
from app.models.media_model import MediaBase
from pydantic import validator, AnyHttpUrl
from app.core.config import settings
from app.utils.partial import optional
from app import api
from typing import Any
from uuid import UUID

from sqlmodel import Field, SQLModel

class IMediaCreate(MediaBase):
    pass


# All these fields are optional
@optional
class IMediaUpdate(MediaBase):
    pass


class IMediaRead(SQLModel):
    id: UUID | str
    link: str | None = None
    path: str | None
    