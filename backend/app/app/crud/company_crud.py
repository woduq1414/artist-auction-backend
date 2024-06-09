from app.schemas.media_schema import IMediaCreate
from app.schemas.company_schema import ICompanyCreate, ICompanyUpdate
from app.models.company_model import Company
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


class CRUDCompany(CRUDBase[Company, ICompanyCreate, ICompanyUpdate]):

    async def get_company_by_nickname(
        self, *, nickname: str, db_session: AsyncSession | None = None
    ) -> Company | None:
        db_session = db_session or super().get_db().session
        companies = await db_session.execute(select(Company).where(Company.nickname == nickname))
        return companies.scalar_one_or_none()


    async def create(
        self, *, obj_in: ICompanyCreate, db_session: AsyncSession | None = None
    ) -> Company:
        db_session = db_session or super().get_db().session
        db_obj = Company.from_orm(obj_in)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj
    
    
    



 

    async def update_photo(
        self,
        *,
        company : Company,
        image_media : ImageMedia,
        db_session: AsyncSession | None = None
    ) -> Company:
        db_session = db_session or super().get_db().session
        print(db_session)
        company.profile_image = image_media
        db_session.add(company)
        await db_session.commit()
        await db_session.refresh(company)
        return company


company = CRUDCompany(Company)
