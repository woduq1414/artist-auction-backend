from app.utils.partial import optional
from app.models.user_model import UserBase
from app.models.group_model import GroupBase
from app.schemas.common_schema import IGenderEnum, ILoginTypeEnum
from app.models.artist_model import ArtistBase
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from .image_media_schema import IImageMediaRead
from .role_schema import IRoleRead
from sqlmodel import SQLModel

from datetime import datetime

class IArtistCreate(ArtistBase):
    
    nickname: str | None
    birthdate: datetime | None

    gender: IGenderEnum | None 
    favorite_category: str | None
    
   
    
    





# All these fields are optional
@optional
class IArtistUpdate(UserBase):
    pass


# # This schema is used to avoid circular import
# class IGroupReadBasic(GroupBase):
#     id: UUID


class IArtistRead(UserBase):
    id: UUID





class IUserBasicInfo(BaseModel):
    id: UUID

