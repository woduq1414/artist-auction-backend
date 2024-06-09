from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia

from app.models.artist_model import Artist
from app.models.company_model import Company
from app.schemas.common_schema import IAccountTypeEnum, IGenderEnum
from datetime import datetime
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class AccountBase(SQLModel):
    name: str = Field(nullable=False) 
    email: EmailStr = Field(
        nullable=False, index=True, sa_column_kwargs={"unique": True}
    )
   
    account_type: IAccountTypeEnum | None = Field(default=None, nullable=False)
    
   



class Account(BaseUUIDModel, AccountBase, table=True):

    login_type: str | None = Field(default=None, nullable=False)
    password: str | None = Field(nullable=True)
    social_id: str | None = Field(nullable=True)
    
    artist_id: UUID | None = Field(default=None, foreign_key="Artist.id", nullable=True)
    
    artist : Artist = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Account.artist_id==Artist.id",
        },
    )
    
    company_id: UUID | None = Field(default=None, foreign_key="Company.id", nullable=True)
    
    company : Company = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Account.company_id==Company.id",
        },
    )

