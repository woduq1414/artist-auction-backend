from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser, LinkProjectUser
from app.models.project_model import Project
# from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class PurchaseBase(SQLModel):

    product_info : str = Field(nullable=False)
    
    status : str = Field(nullable=False)
    project_id: UUID | None = Field(default=None, foreign_key="Project.id")

    product_image_list : str | None = Field(nullable=False)

    status_log : str | None = Field(nullable=False)

class Purchase(BaseUUIDModel, PurchaseBase, table=True):


    created_by_id: UUID | None = Field(default=None, foreign_key="User.id")
    created_by: "User" = Relationship(  # noqa: F821
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Purchase.created_by_id==User.id",
        }
    )

    # product_image_list: list["ImageMedia"] = Relationship(  # noqa: F821
    #     back_populates="purchase", sa_relationship_kwargs={"lazy": "selectin"}
    # )



    project: Project = Relationship(  # noqa: F821
        back_populates="purchases", sa_relationship_kwargs={"lazy": "joined"}
    )