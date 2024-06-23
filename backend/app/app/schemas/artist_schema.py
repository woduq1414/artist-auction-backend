from app.utils.partial import optional
from app.models.user_model import UserBase
from app.models.group_model import GroupBase
from app.schemas.common_schema import IGenderEnum, ILoginTypeEnum
from app.schemas.account_schema import AccountBase, IAccountCreate
from app.models.artist_model import ArtistBase
from app.models.account_model import Account
from app.utils.validators import check_account_description, check_nickname, check_password
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from .image_media_schema import IImageMediaRead
from .role_schema import IRoleRead
from sqlmodel import SQLModel

from datetime import datetime

from pydantic import validator
import re

from pytz import timezone

class IArtistCreate(ArtistBase):

    nickname: str | None
    birthdate: datetime | None

    gender: IGenderEnum | None
    favorite_category: str | None

    @validator("nickname")
    def check_nickname_val(cls, value) -> str | None:

        return check_nickname(cls, value)

    @validator("birthdate")
    def check_birthdate(cls, value) -> datetime | None:
        if value > datetime.now(tz=timezone("Asia/Seoul")):
            raise ValueError("Birthdate should be past")

        if value < datetime(1900, 1, 1, tzinfo=timezone("Asia/Seoul")):
            raise ValueError("Birthdate is too old")
        return value


class IArtistRegister(IArtistCreate, IAccountCreate):
    pass


# All these fields are optional
@optional
class IArtistUpdate(UserBase):
    pass


# # This schema is used to avoid circular import
# class IGroupReadBasic(GroupBase):
#     id: UUID


class IArtistRead(ArtistBase):
    profile_image_id: UUID | None 
    id: UUID


class IArtistInfoRead(SQLModel):
    id: UUID
    nickname: str
    profile_image: IImageMediaRead | None
    description: str | None
    content : str | None


class IUserBasicInfo(BaseModel):
    id: UUID


class IArtistSimpleInfoRead(SQLModel):
    id: UUID
    nickname: str
    profile_image: IImageMediaRead | None


class IArtistInfoEdit(SQLModel):
    email : str | None
    name : str | None
    nickname : str | None
    password : str | None
    content : str | None
    description : str | None
    
    @validator("nickname")
    def check_nickname_val(cls, value) -> str | None:

        return check_nickname(cls, value)
        
        
    @validator("password")
    def check_password_val(cls, value) -> str | None:
        return check_password(cls, value)
    
    @validator("description")
    def check_description_val(cls, value) -> str | None:
        return check_account_description(cls, value)