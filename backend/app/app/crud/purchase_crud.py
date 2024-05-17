
from app.models.purchase_model import Purchase

from app.models.user_model import User
from app.schemas.purchase_schema import IPurchaseCreate, IPurchaseUpdate

from app.crud.base_crud import CRUDBase
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession


class CRUDPurchase(CRUDBase[Purchase, IPurchaseCreate, IPurchaseUpdate]):
    
    async def get_purchase_by_id(
        self, *, id: UUID, db_session: AsyncSession | None = None
    ) -> Purchase:
        db_session = db_session or super().get_db().session
        purchase = await db_session.execute(select(Purchase).where(Purchase.id == id))
        return purchase.scalar_one_or_none()


    


    async def get_purchase_by_created_by_id(
        self, *, leader_user_id: UUID, db_session: AsyncSession | None = None
    ) -> Purchase:
        db_session = db_session or super().get_db().session
        purchase = await db_session.execute(select(Purchase).where(Purchase.created_by_id == leader_user_id))
        return purchase.scalar_one_or_none()
    
    



purchase = CRUDPurchase(Purchase)
