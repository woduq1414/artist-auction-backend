import json
from uuid import UUID
from fastapi import APIRouter, Depends
from fastapi_pagination import Params
from app import crud
from app.api import deps
from app.deps import project_deps, user_deps
from app.models.project_model import Project
from app.models.user_model import User
from app.schemas.project_schema import (
    IProjectCreate,
    IProjectRead,
    IProjectReadWithUsers,
    IProjectUpdate,
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
async def get_projects(
    params: Params = Depends(),
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponsePaginated[IProjectRead]:
    """
    Gets a paginated list of projects
    """
    projects = await crud.project.get_multi_paginated(params=params)
    return create_response(data=projects)


@router.get("/{project_id}")
async def get_project_by_id(
    project_id: UUID,
    current_user: User = Depends(deps.get_current_user()),
) -> IGetResponseBase[IProjectReadWithUsers]:
    """
    Gets a project by its id
    """
    project = await crud.project.get(id=project_id)
    if project:
        return create_response(data=project)
    else:
        raise IdNotFoundException(Project, project_id)


@router.post("")
async def create_project(
    project: IProjectCreate,
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPostResponseBase[IProjectRead]:
    """
    Creates a new project

    Required roles:
    - admin
    - manager
    """

    if len(project.project_users) == 0:
        project.project_users.append(current_user.id)    


    project_users_row_list = []
    for user_id in project.project_users:
        user = await crud.user.get(id=user_id)
        if user:
            project_users_row_list.append(user)

    new_project = await crud.project.create(obj_in=project, created_by_id=current_user.id)
    await crud.project.add_users_to_project(users=project_users_row_list, project_id=new_project.id)
    
    print(project.project_users)


    return create_response(data=new_project)


@router.post("/pdf/pre_content/{project_id}")
async def pre_content_to_pdf(
    project: Project = Depends(project_deps.get_project_by_id),
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPostResponseBase[str]:
    """
    Adds a user into a project

    Required roles:
    - admin
    - manager
    """
    html = await crud.project.pre_content_to_html(project = project)

    if html is None:
        raise ValueError("No pre content found")
    
    f = open("/code/test.html", "w")
    f.write(html)
    f.close()
    


    
    return create_response(data=html)


@router.put("/{project_id}")
async def update_project(
    project: IProjectUpdate,
    current_project: Project = Depends(project_deps.get_project_by_id),
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPutResponseBase[IProjectRead]:
    """
    Updates a project by its id

    Required roles:
    - admin
    - manager
    """
    print(project, "!!")
    if hasattr(project, "pre_content_json"):
        project.pre_content = json.dumps(project.pre_content_json)

    project_updated = await crud.project.update(obj_current=current_project, obj_new=project)
    return create_response(data=project_updated)






@router.post("/add_user/{user_id}/{project_id}")
async def add_user_into_a_project(
    user: User = Depends(user_deps.is_valid_user),
    project: Project = Depends(project_deps.get_project_by_id),
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPostResponseBase[IProjectRead]:
    """
    Adds a user into a project

    Required roles:
    - admin
    - manager
    """
    project = await crud.project.add_user_to_project(user=user, project_id=project.id)
    return create_response(message="User added to project", data=project)



@router.delete("/delete_user/{user_id}/{project_id}")
async def delete_user_into_a_project(
    user: User = Depends(user_deps.is_valid_user),
    project: Project = Depends(project_deps.get_project_by_id),
    current_user: User = Depends(
        deps.get_current_user()
    ),
) -> IPostResponseBase[IProjectRead]:
    """
    Removves a user into a project

    Required roles:
    - admin
    - manager
    """
    deleted_project = await crud.project.delete_user_from_project(user=user, project_id=project.id)
    if project is None:
        raise IdNotFoundException(Project, project.id)

    return create_response(message="User deleted to project", data=project)
