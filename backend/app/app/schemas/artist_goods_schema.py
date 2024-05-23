from datetime import datetime
from app.models.artist_goods_model import ArtistGoods, ArtistGoodsBase
from app.utils.partial import optional
from uuid import UUID

from app.schemas.artist_schema import IArtistRead, IArtistInfoRead
from app.schemas.image_media_schema import IImageMediaRead
from .user_schema import IUserReadWithoutGroups
import json
from datetime import datetime
import base64
from sqlmodel import BigInteger, Field, SQLModel


class IArtistGoodsCreate(ArtistGoodsBase):

    main_image : UUID
    example_image_list : list[UUID]

    

class IArtistGoodsRead(ArtistGoodsBase):
    
    id: UUID
    main_image_id: UUID
    example_image_url_list : str | list[str]
    artist: IArtistInfoRead
    max_price : int

class IArtistGoodsListRead(SQLModel):
    
    id: UUID
    main_image_id: UUID
    example_image_url_list : str | list[str]
    artist: IArtistInfoRead

    title : str 
    description : str 
    
    category : str 
    price : int
    max_price : int

    end_date : datetime | None 
    
    image : IImageMediaRead


@optional
class IArtistGoodsUpdate(ArtistGoodsBase):
    
    pass
            

