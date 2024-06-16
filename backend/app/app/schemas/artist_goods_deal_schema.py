from datetime import datetime
from app.models.artist_goods_model import ArtistGoods, ArtistGoodsBase
from app.models.artist_goods_deal_model import ArtistGoodsDeal, ArtistGoodsDealBase
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

class IArtistGoodsDealCreate(ArtistGoodsDealBase):

    title : str
    description : str
    
    request_image_list : str | list | None
    

    
    price : int
    
    artist_goods_id : UUID
    
    
    

class IArtistGoodsDealRead(ArtistGoodsDealBase):
    
    title : str
    description : str
    
    request_image_list : str | list | None
    
    status : str
    
    price : int
    
    artist_goods_id : UUID | None
    
    
    
    


@optional
class IArtistGoodsDealUpdate(IArtistGoodsDealCreate):
    
    id : UUID
            

