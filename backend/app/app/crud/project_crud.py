
import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.models.project_model import Project

from app.models.user_model import User
from app.schemas.project_schema import IProjectCreate, IProjectUpdate
from app.crud.base_crud import CRUDBase
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession


class CRUDProject(CRUDBase[Project, IProjectCreate, IProjectUpdate]):
    
    async def get_project_by_id(
        self, *, id: UUID, db_session: AsyncSession | None = None
    ) -> Project:
        db_session = db_session or super().get_db().session
        project = await db_session.execute(select(Project).where(Project.id == id))
        return project.scalar_one_or_none()


    


    async def get_project_by_leader_user_id(
        self, *, leader_user_id: UUID, db_session: AsyncSession | None = None
    ) -> Project:
        db_session = db_session or super().get_db().session
        project = await db_session.execute(select(Project).where(Project.leader_user_id == leader_user_id))
        return project.scalar_one_or_none()
    
    
    async def add_user_to_project(self, *, user: User, project_id: UUID) -> Project:
        db_session = super().get_db().session
        project = await super().get(id=project_id)
        project.users.append(user)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        return project
    
    async def delete_user_from_project(self, *, user: User, project_id: UUID) -> Project:
        db_session = super().get_db().session
        project = await super().get(id=project_id)

        if user not in project.users:
            return None
        
        project.users.remove(user)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        return project

    async def add_users_to_project(
        self,
        *,
        users: list[User],
        project_id: UUID,
        db_session: AsyncSession | None = None,
    ) -> Project:
        db_session = db_session or super().get_db().session
        project = await super().get(id=project_id, db_session=db_session)
        project.users.extend(users)
        db_session.add(project)
        await db_session.commit()
        await db_session.refresh(project)
        return project
    
    async def pre_content_to_html(self, *, project: Project):
        if project.pre_content is None:
            return None
        
        env = Environment(
            loader=FileSystemLoader('templates'),
            autoescape=select_autoescape(['html', 'xml'])
        )
        template = env.get_template(f'pre_content_format.html')
        

        pre_content = json.loads(project.pre_content)
        render_data = {
            "leader_data": {
                "name": project.leader_user.name,
                "group_list" : ", ".join([x.name for x in project.leader_user.groups]),
            },
            "date_string" : project.created_at.strftime("%Y.%m.%d"),
            "project_user_list" : [{
                "name": user.name,
                "group_list" : ", ".join([x.name for x in user.groups]),
            } for user in project.users],
            "project_title" : project.title,
            "motive" : pre_content["motive"],
            "description" : pre_content["description"],
        }
        print(render_data)

        return template.render(render_data = render_data)
        


project = CRUDProject(Project)
