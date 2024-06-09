from app.utils.partial import optional
from app.models.user_model import UserBase
from app.models.group_model import GroupBase
from app.schemas.common_schema import IGenderEnum, ILoginTypeEnum
from app.schemas.account_schema import AccountBase, IAccountCreate
from app.models.company_model import CompanyBase
from app.models.account_model import Account
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

class ICompanyCreate(CompanyBase):

    nickname: str | None

    favorite_category: str | None

    @validator("nickname")
    def check_nickname(cls, value) -> str | None:

        print(cls, value)

        reg = re.compile(r"[가-힣a-zA-Z0-9_]+")

        if not reg.match(value):
            raise ValueError(
                "Nickname should have korean or english or number or underbar"
            )

        # korean : 2byte, english : 1byte, number : 1byte, underbar : 1byte
        # calculate byte length and check if under 16

        def korlen(str):
            korP = re.compile("[\u3131-\u3163\uAC00-\uD7A3]+", re.U)
            temp = re.findall(korP, str)
            temp_len = 0
            for item in temp:
                temp_len = temp_len + len(item)
            return len(str) + temp_len
        print(korlen(value))
        if korlen(value) > 16:
            raise ValueError("Nickname should be under 16 bytes")

        return value



class ICompanyRegister(ICompanyCreate, IAccountCreate):
    pass


# All these fields are optional
@optional
class ICompanyUpdate(AccountBase):
    pass


# # This schema is used to avoid circular import
# class IGroupReadBasic(GroupBase):
#     id: UUID


class ICompanyBase(CompanyBase):
    profile_image_id: UUID | None 
    id: UUID


class ICompanyInfoRead(SQLModel):
    id: UUID
    nickname: str
    profile_image: IImageMediaRead | None


