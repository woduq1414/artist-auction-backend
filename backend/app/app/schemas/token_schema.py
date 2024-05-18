from pydantic import BaseModel
from .user_schema import IUserRead
from .account_schema import IAccountRead


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    account: IAccountRead


class TokenRead(BaseModel):
    access_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str
