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


class CompanyBase(SQLModel):

    
    nickname: str | None = Field(nullable=False)
   
    favorite_category: str | None = Field(default=None, nullable=True)
    
    description : str | None = Field(nullable=True)

    content : str | None = Field(nullable=True)
   
    
    



    




class Company(BaseUUIDModel, CompanyBase, table=True):
    profile_image_id: UUID | None = Field(default=None, foreign_key="ImageMedia.id")
    profile_image: ImageMedia = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Company.profile_image_id==ImageMedia.id",
        }
    )

    

