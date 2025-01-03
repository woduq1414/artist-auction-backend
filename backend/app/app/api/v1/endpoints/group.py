from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from app import crud
from app.api import deps
from app.deps import group_deps, user_deps
from app.models.group_model import Group
from app.models.user_model import User
from app.schemas.group_schema import (
    IGroupCreate,
    IGroupRead,
    IGroupReadWithUsers,
    IGroupUpdate,
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

router = APIRouter()


@router.get("")
async def get_groups(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_account()),
) -> IGetResponsePaginated[IGroupRead]:
    """
    Gets a paginated list of groups
    """
    groups = await crud.group.get_multi_paginated(params=params)
    return create_response(data=groups)


@router.get("/{group_id}")
async def get_group_by_id(
    group_id: UUID,
    current_user: User = Depends(deps.get_current_account()),
) -> IGetResponseBase[IGroupReadWithUsers]:
    """
    Gets a group by its id
    """
    group = await crud.group.get(id=group_id)
    if group:
        return create_response(data=group)
    else:
        raise IdNotFoundException(Group, group_id)


@router.post("")
async def create_group(
    group: IGroupCreate,
    current_user: User = Depends(
        deps.get_current_account(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPostResponseBase[IGroupRead]:
    """
    Creates a new group

    Required roles:
    - admin
    - manager
    """
    group_current = await crud.group.get_group_by_name(name=group.name)
    if group_current:
        raise NameExistException(Group, name=group.name)
    new_group = await crud.group.create(obj_in=group, created_by_id=current_user.id)
    return create_response(data=new_group)


@router.put("/{group_id}")
async def update_group(
    group: IGroupUpdate,
    current_group: Group = Depends(group_deps.get_group_by_id),
    current_user: User = Depends(
        deps.get_current_account(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPutResponseBase[IGroupRead]:
    """
    Updates a group by its id

    Required roles:
    - admin
    - manager
    """
    group_updated = await crud.group.update(obj_current=current_group, obj_new=group)
    return create_response(data=group_updated)


@router.post("/add_user/{user_id}/{group_id}")
async def add_user_into_a_group(
    user: User = Depends(user_deps.is_valid_user),
    group: Group = Depends(group_deps.get_group_by_id),
    current_user: User = Depends(
        deps.get_current_account(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPostResponseBase[IGroupRead]:
    """
    Adds a user into a group

    Required roles:
    - admin
    - manager
    """
    group = await crud.group.add_user_to_group(user=user, group_id=group.id)
    return create_response(message="User added to group", data=group)



@router.delete("/delete_user/{user_id}/{group_id}")
async def delete_user_into_a_group(
    user: User = Depends(user_deps.is_valid_user),
    group: Group = Depends(group_deps.get_group_by_id),
    current_user: User = Depends(
        deps.get_current_account(required_roles=[IRoleEnum.admin, IRoleEnum.manager])
    ),
) -> IPostResponseBase[IGroupRead]:
    """
    Removves a user into a group

    Required roles:
    - admin
    - manager
    """
    deleted_group = await crud.group.delete_user_from_group(user=user, group_id=group.id)
    if group is None:
        raise IdNotFoundException(Group, group.id)

    return create_response(message="User deleted to group", data=group)
