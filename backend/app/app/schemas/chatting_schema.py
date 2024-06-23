from app.utils.partial import optional
from app.models.user_model import UserBase
from app.models.group_model import GroupBase
from app.schemas.common_schema import IGenderEnum, ILoginTypeEnum
from app.schemas.account_schema import AccountBase, IAccountCreate
from app.models.chatting_model import ChattingBase
from app.models.account_model import Account
from app.models.chatting_model import ChattingBase
from app.schemas.artist_schema import IArtistSimpleInfoRead
from app.schemas.company_schema import ICompanySimpleInfoRead
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


class IChattingMessageCreate(BaseModel):

    type : str
    message : str



class IChattingCreate(ChattingBase):

    content : str | None
    artist_id : UUID
    company_id : UUID
    redis_key : str | None


class IChattingRead(ChattingBase):

    content : str | list | None
    id : UUID | None
    redis_key : str | None
    artist : IArtistSimpleInfoRead | None
    company : ICompanySimpleInfoRead | None
    last_message : str | None


class IChattingRegister(IChattingCreate, IAccountCreate):
    pass


# All these fields are optional
@optional
class IChattingUpdate(AccountBase):
    pass


# # This schema is used to avoid circular import
# class IGroupReadBasic(GroupBase):
#     id: UUID


class IChattingBase(ChattingBase):
    profile_image_id: UUID | None 
    id: UUID


