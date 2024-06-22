from datetime import timedelta
from typing import Any, List, Optional
from app.schemas.notify_schema import INotifyCreate, INotifyRead
from app.models.account_model import Account
from fastapi import APIRouter, Body, Depends, HTTPException
from redis.asyncio import Redis
from app.utils.login import create_login_token
from app.utils.token import get_valid_tokens
from app.utils.token import delete_tokens
from app.utils.token import add_token_to_redis
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.models.user_model import User
from app.api.deps import get_redis_client
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import EmailStr
from pydantic import ValidationError
from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.common_schema import ILoginTypeEnum, TokenType, IMetaGeneral
from app.schemas.token_schema import TokenRead, Token, RefreshToken
from app.schemas.response_schema import (
    IGetResponseBase,
    IPostResponseBase,
    create_response,
)
from app.utils.notify import delete_notify, delete_notify_all, get_notify
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Query,
    Response,
    UploadFile,
    status,
)


router = APIRouter()


@router.get("")
async def get_noitfy_api(
    is_read: Optional[str] = Query(False),
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(get_redis_client),
) -> IGetResponseBase[dict[str, Any]]:
    """
    get notify
    """
    notify_read_key = f"notify:read:{current_account.id}"
    notify_read = await redis_client.get(notify_read_key)

    user_id = current_account.id
    if current_account.company_id:
        user_id = current_account.company_id
    elif current_account.artist_id:
        user_id = current_account.artist_id

    notify_list = await get_notify(redis=redis_client, user_id=user_id, is_read=is_read)

    return create_response(
        data={"notify_list": notify_list, "notify_read": notify_read},
        message="get notify list",
    )


@router.delete("")
async def delete_notify_api(
    notify: INotifyCreate,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(get_redis_client),
) -> IPostResponseBase[None]:
    """
    delete notify
    """
    user_id = current_account.id
    if current_account.company_id:
        user_id = current_account.company_id
    elif current_account.artist_id:
        user_id = current_account.artist_id

    await delete_notify(redis=redis_client, user_id=user_id, notify=notify)

    return create_response(data=None, message="delete notify list")


@router.delete("/all")
async def delete_notify_all_api(
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(get_redis_client),
) -> IPostResponseBase[None]:
    """
    delete notify
    """
    user_id = current_account.id
    if current_account.company_id:
        user_id = current_account.company_id
    elif current_account.artist_id:
        user_id = current_account.artist_id
    await delete_notify_all(redis=redis_client, user_id=user_id)

    return create_response(data=None, message="delete all notify list")
