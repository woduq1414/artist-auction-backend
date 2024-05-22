from datetime import datetime
from app.models.artist_goods_model import ArtistGoods, ArtistGoodsBase
from app.utils.partial import optional
from uuid import UUID

from app.schemas.artist_schema import IArtistRead, IArtistInfoRead
from .user_schema import IUserReadWithoutGroups
import json
from datetime import datetime
import base64



class IArtistGoodsCreate(ArtistGoodsBase):

    main_image : UUID
    example_image_list : list[UUID]

    

class IArtistGoodsRead(ArtistGoodsBase):
    
    id: UUID
    main_image_id: UUID
    example_image_url_list : str | list[str]
    artist: IArtistInfoRead



@optional
class IArtistGoodsUpdate(ArtistGoodsBase):
    
    pass
            

