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

from pydantic import validator

class IArtistGoodsCreate(ArtistGoodsBase):

    main_image : UUID
    example_image_list : list[UUID]
    
    type : str
    
    @validator("title")
    def check_title(cls, value) -> str:
        if len(value) > 20:
            raise ValueError("Title should be under 20 characters")
        return value
    
    @validator("description")
    def check_description(cls, value) -> str:
        if len(value) > 40:
            raise ValueError("Description should be under 40 characters")
        return value
    
    @validator("duration")
    def check_duration(cls, value) -> int:
        if not (1 <= value <= 14):
            raise ValueError("Duration should be between 1 and 14")
        return value
    
    
    @validator("price")
    def check_price(cls, value) -> int:
        if not (1 <= value <= 9999):
            raise ValueError("Price should be between 1 and 9999")
        return value

    

class IArtistGoodsRead(ArtistGoodsBase):
    
    id: UUID
    main_image_id: UUID
    image : IImageMediaRead
    example_image_url_list : str | list | None
    example_image_list : list[IImageMediaRead] | None
    artist: IArtistInfoRead
    max_price : int
    image : IImageMediaRead
    
    price_data : dict | None
    
    



class IArtistGoodsListRead(SQLModel):
    
    id: UUID
    main_image_id: UUID
    example_image_url_list : list | str
    artist: IArtistInfoRead

    title : str 
    description : str 
    
    category : str 
    price : int
    max_price : int

    start_date : datetime | None
    end_date : datetime | None 
    duration : int | None
    
    image : IImageMediaRead
    
    created_at : datetime
    
    status : str
    
    # @validator("example_image_url_list")
    # def example_image_url_list_to_list(cls, value):
    #     print(json.loads(value) , value, type(value))
    #     return value


@optional
class IArtistGoodsUpdate(IArtistGoodsCreate):
    
    id : UUID
            

