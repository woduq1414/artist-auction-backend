from app.utils.partial import optional
from app.models.user_model import UserBase
from app.models.group_model import GroupBase
from app.schemas.common_schema import ILoginTypeEnum
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from .image_media_schema import IImageMediaRead
from .role_schema import IRoleRead
from sqlmodel import SQLModel

class IUserCreate(UserBase):
    
    login_type : ILoginTypeEnum

    password: str | None
    kakao_access_token : str | None

    class Config:
        # pass
        hashed_password = None





# All these fields are optional
@optional
class IUserUpdate(UserBase):
    pass


# This schema is used to avoid circular import
class IGroupReadBasic(GroupBase):
    id: UUID


class IUserRead(UserBase):
    id: UUID
    role: IRoleRead | None = None
    groups: list[IGroupReadBasic] | None = []
    image: IImageMediaRead | None
    follower_count: int | None = 0
    following_count: int | None = 0


class IUserReadTrivial(SQLModel):
    id: UUID
    name : str
    groups: list[IGroupReadBasic] | None = []


class IUserReadWithoutGroups(UserBase):
    id: UUID
    role: IRoleRead | None = None
    image: IImageMediaRead | None
    follower_count: int | None = 0
    following_count: int | None = 0


class IUserReadWithoutProjects(UserBase):
    id: UUID
    role: IRoleRead | None = None
    groups: list[IGroupReadBasic] | None = []
    image: IImageMediaRead | None
    follower_count: int | None = 0
    following_count: int | None = 0




class IUserBasicInfo(BaseModel):
    id: UUID

    


class IUserStatus(str, Enum):
    active = "active"
    inactive = "inactive"
