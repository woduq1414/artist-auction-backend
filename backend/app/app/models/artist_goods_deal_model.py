from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from app.models.artist_model import Artist
from app.models.artist_goods_model import ArtistGoods
from app.models.company_model import Company
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class ArtistGoodsDealBase(SQLModel):

    title : str = Field(nullable=False)
    description : str = Field(nullable=False)
    
    request_image_list : str = Field(nullable=False)
    

    price : int = Field(nullable=False)
    
    

 




class ArtistGoodsDeal(BaseUUIDModel, ArtistGoodsDealBase, table=True):
    
    status : str = Field(nullable=False)
    artist_goods_id: UUID | None = Field(default=None, foreign_key="ArtistGoods.id")
    
    artist_goods: ArtistGoods = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "ArtistGoodsDeal.artist_goods_id==ArtistGoods.id",
        }
    )
    
    
    company_id : UUID | None = Field(default=None, foreign_key="Company.id")
    company: Company = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "ArtistGoodsDeal.company_id==Company.id",
        }
    )
    
    artist_id: UUID | None = Field(default=None, foreign_key="Artist.id")
    artist: Artist = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "ArtistGoodsDeal.artist_id==Artist.id",
        }
    )
    
    
