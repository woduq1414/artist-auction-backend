from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from app.models.artist_model import Artist
from app.models.artist_goods_model import ArtistGoods
from app.models.company_model import Company
from app.models.artist_goods_deal_model import ArtistGoodsDeal
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class PaymentBase(SQLModel):


    amount : int = Field(nullable=False)
    payment_key : str = Field(nullable=False)
    payment_type : str = Field(nullable=False)
    order_id : str = Field(nullable=False)
    
    
    

 




class Payment(BaseUUIDModel, PaymentBase, table=True):
    
    status : str = Field(nullable=True)
    detail : str = Field(nullable=True)
    
    
    artist_goods_deal_id: UUID | None = Field(default=None, foreign_key="ArtistGoodsDeal.id")
    
    artist_goods_deal: ArtistGoodsDeal = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Payment.artist_goods_deal_id==ArtistGoodsDeal.id",
        }
    )
    
    
    company_id : UUID | None = Field(default=None, foreign_key="Company.id")
    company: Company = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Payment.company_id==Company.id",
        }
    )
    
    artist_id: UUID | None = Field(default=None, foreign_key="Artist.id")
    artist: Artist = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "Payment.artist_id==Artist.id",
        }
    )
    
    
