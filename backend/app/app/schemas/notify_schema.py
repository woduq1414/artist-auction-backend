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

class INotifyCreate(BaseModel):

    receiver_id : list[UUID] | str
    title : str
    description : str
    type : str
    action : str
    created_at : datetime
    
    
class INotifyRead(BaseModel):

    title : str | None
    description : str | None
    type : str | None
    action : str | None
    created_at : datetime | None