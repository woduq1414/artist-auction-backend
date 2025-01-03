from collections.abc import AsyncGenerator
from app.models.account_model import Account
from fastapi import Depends, HTTPException, status
from app.utils.token import get_valid_tokens
from app.utils.minio_client import MinioClient
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from app.models.user_model import User
from pydantic import ValidationError
from app import crud
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal, SessionLocalCelery
from sqlmodel.ext.asyncio.session import AsyncSession
from app.schemas.common_schema import IMetaGeneral, TokenType
import redis.asyncio as aioredis
from redis.asyncio import Redis


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/access-token",
   auto_error=False
)


async def get_redis_client() -> Redis:
    redis = await aioredis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}",
        max_connections=10,
        encoding="utf8",
        decode_responses=True,
    )
    return redis


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session


async def get_jobs_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocalCelery() as session:
        yield session


async def get_general_meta() -> IMetaGeneral:
    current_roles = await crud.role.get_multi(skip=0, limit=100)
    return IMetaGeneral(roles=current_roles)


def get_current_account(
    required_roles: list[str] = None, is_login_required: bool = True
) -> Account | None:
    async def current_account(
        token = Depends(reusable_oauth2),
        redis_client: Redis = Depends(get_redis_client),
        db_session: AsyncSession = Depends(get_db),
    ) -> Account | None:

        if not token:
            if is_login_required:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials",
                )
            else:
                return None
     
        
        db_session = db_session or SessionLocal()

        try:
            print(token)
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
        except (jwt.JWTError, ValidationError) as e:
            print(e)
            
            if is_login_required:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials1",
                )
            else:
                return None
        account_id = payload["sub"]

        valid_access_tokens = await get_valid_tokens(
            redis_client, account_id, TokenType.ACCESS
        )
        if valid_access_tokens and token not in valid_access_tokens:
            if is_login_required:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials2",
                )
        account: Account = await crud.account.get(id=account_id, db_session=db_session)
       
        if not account:
            if is_login_required:
                raise HTTPException(status_code=404, detail="User not found")
            else:
                return None

        return account

    return current_account


def get_current_account_data_without_db(
    required_roles: list[str] = None, is_login_required: bool = True
) -> dict | None:
    async def current_account(
        token = Depends(reusable_oauth2),

    ) -> dict | None:

        if not token:
            if is_login_required:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials",
                )
            else:
                return None
     
 
        try:
            print(token)
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
            )
        except (jwt.JWTError, ValidationError) as e:
            print(e)
            
            if is_login_required:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials1",
                )
            else:
                return None
        data = payload["data"]
        
        

        

        return data

    return current_account



def minio_auth() -> MinioClient:
    minio_client = MinioClient(
        access_key=settings.MINIO_ROOT_USER,
        secret_key=settings.MINIO_ROOT_PASSWORD,
        bucket_name=settings.MINIO_BUCKET,
        minio_url=settings.MINIO_URL,
    )
    return minio_client
