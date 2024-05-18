from app import crud
from app.models.role_model import Role
from app.models.user_model import User
from app.schemas.user_schema import IUserCreate
from app.schemas.user_schema import IUserRead
from app.utils.exceptions.common_exception import IdNotFoundException
from uuid import UUID
from app.models.account_model import Account
from fastapi import HTTPException, Path, status
from typing_extensions import Annotated

import requests
import json
from jose import jwt
import base64

from datetime import timedelta
import json
from redis.asyncio import Redis
import requests
from app.core import security
from app.core.config import Settings

from app.models.user_model import User
from app.schemas.common_schema import TokenType
from app.schemas.token_schema import Token
from app.utils.token import add_token_to_redis, get_valid_tokens

from app.core.config import settings




async def social_kakao_verify(code : str) -> IUserCreate:
    pass


async def email_exists(email: str) -> str:
    user = await crud.account.get_by_email(email=email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same email",
        )

    return email


async def social_id_exists(social_id: str) -> str:
    user = await crud.account.get_by_social_id(social_id=social_id)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="There is already a user with same social id",
        )

    return social_id


async def get_token_by_account(account: Account, redis_client: Redis):
    access_token_expires = timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
    refresh_token_expires = timedelta(
        minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    paylaod_data = {
        "id": str(account.id),
        "nickname" : account.artist.nickname,
        # "profileImage" : account.artist.profile_image.url,
    }
    access_token = security.create_access_token(
        paylaod_data, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        paylaod_data, expires_delta=refresh_token_expires
    )
    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        account=account,
    )
    valid_access_tokens = await get_valid_tokens(
        redis_client, account.id, TokenType.ACCESS
    )
    if valid_access_tokens:
        await add_token_to_redis(
            redis_client,
            account,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    valid_refresh_tokens = await get_valid_tokens(
        redis_client, account.id, TokenType.REFRESH
    )
    if valid_refresh_tokens:
        await add_token_to_redis(
            redis_client,
            account,
            refresh_token,
            TokenType.REFRESH,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )
    return data