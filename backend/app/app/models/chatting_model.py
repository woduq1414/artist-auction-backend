from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from app.models.artist_model import Artist
from app.models.company_model import Company
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class ChattingBase(SQLModel):


    
    content : str = Field(nullable=True)


 




class Chatting(BaseUUIDModel, ChattingBase, table=True):
    
    status : str = Field(nullable=False)
    
    artist_id: UUID | None = Field(default=None, foreign_key="Artist.id")
    artist: Artist = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Chatting.artist_id==Artist.id",
        }
    )
    
    company_id: UUID | None = Field(default=None, foreign_key="Company.id")
    company: Company = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Chatting.company_id==Company.id",
        }
    )
    
    redis_key : str = Field(nullable=True)
    
    
    