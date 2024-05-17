from app import crud
from app.models.purchase_model import Purchase
from app.models.user_model import User
from app.utils.exceptions.common_exception import (
    NameNotFoundException,
    IdNotFoundException,
)
from uuid import UUID
from fastapi import Query, Path
from typing_extensions import Annotated


async def get_purchase_by_leader_id(
    leader_user_id: Annotated[
        UUID, Query(description="The UUID id of the purchase leader user")
    ] = ""
) -> str:
    purchase = await crud.purchase.get_purchase_by_leader_user_id(leader_user_id= leader_user_id)
    if not purchase:
        raise IdNotFoundException(User, id=leader_user_id)
    return purchase


async def get_purchase_by_id(
    purchase_id: Annotated[UUID, Path(description="The UUID id of the purchase")]
) -> Purchase:
    purchase = await crud.purchase.get(id=purchase_id)
    if not purchase:
        raise IdNotFoundException(Purchase, id=purchase_id)
    return purchase
