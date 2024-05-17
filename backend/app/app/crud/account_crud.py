from app.schemas.media_schema import IMediaCreate
from app.schemas.user_schema import IUserCreate, IUserUpdate
from app.schemas.account_schema import IAccountCreate, IAccountUpdate
from app.models.user_model import User
from app.models.account_model import Account
from app.models.media_model import Media
from app.models.image_media_model import ImageMedia
from app.core.security import verify_password, get_password_hash
from pydantic.networks import EmailStr
from typing import Any
from app.crud.base_crud import CRUDBase
from app.crud.user_follow_crud import user_follow as UserFollowCRUD
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.login import verify_kakao_access_token


class CRUDACcount(CRUDBase[Account, IAccountCreate, IAccountUpdate]):
    async def get_by_email(
        self, *, email: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db().session
        accounts = await db_session.execute(select(Account).where(Account.email == email))
        return accounts.scalar_one_or_none()
    
    
    async def get_by_artist_id(
        self, *, artist_id: UUID, db_session: AsyncSession | None = None
    ) -> Account | None:
        db_session = db_session or super().get_db().session
        accounts = await db_session.execute(select(Account).where(Account.artist_id == artist_id))
        return accounts.scalar_one_or_none()



    async def make_active(
        self, *, db_obj: Account, kakao_id: str,  db_session: AsyncSession | None = None
    ) -> None:
        db_session = db_session or super().get_db().session
        db_obj.is_active = True
        db_obj.login_type = "kakao"
        db_obj.kakao_id = kakao_id

        await db_session.commit()
        await db_session.refresh(db_obj)

    async def create(
        self, *, obj_in: IAccountCreate, db_session: AsyncSession | None = None
    ) -> Account:
        db_session = db_session or super().get_db().session
        db_obj = Account.from_orm(obj_in)
        db_obj.password = get_password_hash(obj_in.password)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    async def update_is_active(
        self, *, db_obj: list[Account], obj_in: int | str | dict[str, Any]
    ) -> Account | None:
        response = None
        db_session = super().get_db().session
        for x in db_obj:
            x.is_active = obj_in.is_active
            db_session.add(x)
            await db_session.commit()
            await db_session.refresh(x)
            response.append(x)
        return response

    async def authenticate(self, *, email: EmailStr, password: str) -> Account | None:
        account = await self.get_by_email(email=email)
        if not Account:
            return None
        if not verify_password(password, account.hashed_password):
            return None
        return Account

    async def authenticate_kakao(self, *, kakao_access_token: str) -> Account | None:
        kakao_id = verify_kakao_access_token(
            kakao_access_token=kakao_access_token)
        if kakao_id is None:
            return None
        Account = await self.get_by_kakao_id(kakao_id=kakao_id)
        if not Account:
            return None
        return Account



account = CRUDACcount(Account)