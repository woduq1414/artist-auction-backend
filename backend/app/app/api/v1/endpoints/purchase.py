from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from app import crud
from app.api import deps
from app.deps import purchase_deps, user_deps
from app.models.purchase_model import Purchase
from app.models.user_model import User
from app.schemas.purchase_schema import (
    IPurchaseCreate,
    IPurchaseRead,
    IPurchaseReadWithUsers,
    IPurchaseUpdate,
)
from app.schemas.response_schema import (
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum
from app.utils.exceptions import (
    IdNotFoundException,
    NameExistException,
)
from sqlmodel import and_, select, col, or_, text

router = APIRouter()


@router.get("")
async def get_purchases(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IPurchaseRead]:
    """
    Gets a paginated list of purchases
    """
    purchases = await crud.purchase.get_multi_paginated(params=params)
    return create_response(data=purchases)


@router.get("/project/{project_id}")
async def get_purchases_by_project_id(
    project_id : UUID,
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IPurchaseRead]:
    """
    Gets a paginated list of purchases by project_id
    """

    # query = (
    #     select(User)
    #     .join(Group)
    #     .where(
    #         and_(
    #             G.id == group_id,
    #             User.is_active == user_status,
    #         )
    #     )

    # )
    query = None

    purchases = await crud.purchase.get_multi_paginated(params=params, query= query)
    return create_response(data=purchases)



@router.get("/{purchase_id}")
async def get_purchase_by_id(
    purchase_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IPurchaseReadWithUsers]:
    """
    Gets a purchase by its id
    """
    purchase = await crud.purchase.get(id=purchase_id)
    if purchase:
        return create_response(data=purchase)
    else:
        raise IdNotFoundException(Purchase, purchase_id)


@router.post("")
async def create_purchase(
    purchase: IPurchaseCreate,
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPostResponseBase[IPurchaseRead]:
    """
    Creates a new purchase

    Required roles:
    - admin
    - manager
    """

    new_purchase = await crud.purchase.create(obj_in=purchase, created_by_id=current_user.id)

    return create_response(data=new_purchase)




@router.put("/{purchase_id}")
async def update_purchase(
    purchase: IPurchaseUpdate,
    current_purchase: Purchase = Depends(purchase_deps.get_purchase_by_id),
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPutResponseBase[IPurchaseRead]:
    """
    Updates a purchase by its id

    Required roles:
    - admin
    - manager
    """
    purchase_updated = await crud.purchase.update(obj_current=current_purchase, obj_new=purchase)
    return create_response(data=purchase_updated)



