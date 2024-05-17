from app import crud
from app.models.project_model import Project
from app.models.user_model import User
from app.utils.exceptions.common_exception import (
    NameNotFoundException,
    IdNotFoundException,
)
from uuid import UUID
from fastapi import Query, Path
from typing_extensions import Annotated


async def get_project_by_leader_id(
    leader_user_id: Annotated[
        UUID, Query(description="The UUID id of the project leader user")
    ] = ""
) -> str:
    project = await crud.project.get_project_by_leader_user_id(leader_user_id= leader_user_id)
    if not project:
        raise IdNotFoundException(User, id=leader_user_id)
    return project


async def get_project_by_id(
    project_id: Annotated[UUID, Path(description="The UUID id of the project")]
) -> Project:
    project = await crud.project.get(id=project_id)
    if not project:
        raise IdNotFoundException(Project, id=project_id)
    return project
