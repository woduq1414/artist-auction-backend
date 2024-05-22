from datetime import datetime
from app.models.artist_goods_model import ArtistGoods, ArtistGoodsBase
from app.utils.partial import optional
from uuid import UUID
from .user_schema import IUserReadWithoutGroups
import json
from datetime import datetime
import base64



class IArtistGoodsCreate(ArtistGoodsBase):

    main_image : UUID
    example_image_list : list[UUID]

    

class IArtistGoodsRead(ArtistGoodsBase):
    id: UUID



@optional
class IArtistGoodsUpdate(ArtistGoodsBase):
    
    pass
            

