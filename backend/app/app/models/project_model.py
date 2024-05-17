from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class ProjectBase(SQLModel):

    title : str = Field(nullable=False, index=True)

    status : str = Field(nullable=False)


    start_date : datetime | None = Field(nullable = True)
    end_date : datetime | None = Field(nullable = True, )
 
    
    pre_content : str | None = Field(nullable=True)

    final_content : str | None = Field(nullable=True)



class Project(BaseUUIDModel, ProjectBase, table=True):

    leader_user_id: UUID | None = Field(default=None, foreign_key="User.id")
    leader_user: "User" = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Project.leader_user_id==User.id",
        }
    )
    users: list["User"] = Relationship(
        back_populates="projects",
        link_model=LinkProjectUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    purchases: list["Purchase"] = Relationship(  # noqa: F821
        back_populates="project", sa_relationship_kwargs={"lazy": "selectin"}
    )