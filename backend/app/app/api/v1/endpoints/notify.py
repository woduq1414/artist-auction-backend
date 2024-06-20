from datetime import timedelta
from typing import Any, List, Optional
from app.schemas.notify_schema import INotifyRead
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
from app.schemas.response_schema import IGetResponseBase, IPostResponseBase, create_response
from app.utils.notify import get_notify

router = APIRouter()


@router.get("")
async def get_noitfy_api(
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(get_redis_client),
) -> IGetResponseBase[List[INotifyRead]]:
    """
    get notify
    """
    
    notify_list = await get_notify(
        redis=redis_client,
        account_id=current_account.id
    )
    
    return create_response(data=notify_list, message="get notify list")
    
    
 