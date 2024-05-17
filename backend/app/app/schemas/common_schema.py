from pydantic import BaseModel
from enum import Enum
from app.schemas.role_schema import IRoleRead


class IAccountTypeEnum(str, Enum):
    artist = "artist"
    company = "company"

class ILoginTypeEnum(str, Enum):
    password = "password"
    kakao = "kakao"
    google = "google"

class IGenderEnum(str, Enum):
    female = "female"
    male = "male"
    other = "other"


class IMetaGeneral(BaseModel):
    roles: list[IRoleRead]


class IOrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"
