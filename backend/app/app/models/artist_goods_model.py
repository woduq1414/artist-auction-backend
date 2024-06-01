from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from app.models.artist_model import Artist
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class ArtistGoodsBase(SQLModel):

    title : str = Field(nullable=False)
    description : str = Field(nullable=False)
    
    category : str = Field(nullable=False)
    price : int = Field(nullable=False)

    

    
    content : str = Field(nullable=False)

    start_date : datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    end_date : datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    ) 
    
    duration : int | None = Field(nullable=True)

 




class ArtistGoods(BaseUUIDModel, ArtistGoodsBase, table=True):
    max_price : int = Field(nullable=True)
    status : str = Field(nullable=False)
    artist_id: UUID | None = Field(default=None, foreign_key="Artist.id")
    artist: Artist = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "ArtistGoods.artist_id==Artist.id",
        }
    )
    
    
    main_image_id: UUID | None = Field(default=None, foreign_key="ImageMedia.id")
    image: ImageMedia = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "ArtistGoods.main_image_id==ImageMedia.id",
        }
    )
    
    example_image_url_list : str | None = Field(nullable=False)