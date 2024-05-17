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




def verify_kakao_access_token(
        kakao_access_token : str
) -> str | None:
    res = requests.get("https://kapi.kakao.com/v1/user/access_token_info", headers={
        "Authorization": "Bearer " + kakao_access_token
    })

    print(res.text)

    if res.status_code != 200:
        return None

    kakao_id = str(json.loads(res.text)["id"])
    return kakao_id


async def create_login_token(
    redis_client : Redis, user : User
) -> Token | None :
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    refresh_token = security.create_refresh_token(
        user.id, expires_delta=refresh_token_expires
    )
    data = Token(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_token,
        user=user,
    )
    valid_access_tokens = await get_valid_tokens(
        redis_client, user.id, TokenType.ACCESS
    )
    if valid_access_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            access_token,
            TokenType.ACCESS,
            settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
    valid_refresh_tokens = await get_valid_tokens(
        redis_client, user.id, TokenType.REFRESH
    )
    if valid_refresh_tokens:
        await add_token_to_redis(
            redis_client,
            user,
            refresh_token,
            TokenType.REFRESH,
            settings.REFRESH_TOKEN_EXPIRE_MINUTES,
        )

    return data
