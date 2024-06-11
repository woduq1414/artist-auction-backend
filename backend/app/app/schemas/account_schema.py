from app.utils.partial import optional
from app.models.user_model import UserBase
from app.models.group_model import GroupBase
from app.schemas.common_schema import ILoginTypeEnum
from app.models.account_model import AccountBase

from app.utils.validators import check_password
from pydantic import BaseModel
from uuid import UUID
from enum import Enum
from .image_media_schema import IImageMediaRead
from .role_schema import IRoleRead
from sqlmodel import SQLModel
from pydantic import validator

import re


class IAccountCreate(AccountBase):
    
    login_type : ILoginTypeEnum
    

    
    

    password: str | None
    social_id: str | None
    artist_id: UUID | None = None
    company_id: UUID | None = None
    
    @validator("password")
    def check_password_val(cls, value) -> str | None:
        return check_password(cls, value)
    
    
    

    class Config:
        # pass
        hashed_password = None





# All these fields are optional
@optional
class IAccountUpdate(AccountBase):
    pass


# # This schema is used to avoid circular import
# class IGroupReadBasic(GroupBase):
#     id: UUID


class IAccountRead(AccountBase):
    id: UUID






class IUserBasicInfo(BaseModel):
    id: UUID

