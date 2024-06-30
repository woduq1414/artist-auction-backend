from datetime import datetime
from app.models.artist_goods_model import ArtistGoods, ArtistGoodsBase
from app.models.artist_goods_deal_model import ArtistGoodsDeal, ArtistGoodsDealBase
from app.utils.partial import optional
from uuid import UUID

from app.schemas.artist_schema import IArtistRead, IArtistInfoRead
from app.schemas.image_media_schema import IImageMediaRead
from app.schemas.artist_goods_schema import IArtistGoodsRead
from app.schemas.company_schema import ICompanyInfoRead
from app.models.payment_model import PaymentBase
from .user_schema import IUserReadWithoutGroups
import json
from datetime import datetime
import base64
from sqlmodel import BigInteger, Field, SQLModel

from pydantic import validator

class IPaymentCreate(PaymentBase):
    order_id : str
    amount : int
    payment_key : str | None
    payment_type : str | None
    detail : str | None
    company_id : UUID | None
    artist_id : UUID | None
   
    
    
    

class IPaymentRead(PaymentBase):
    id : UUID | None
   
   
    
    status : str | None

    
    artist_goods_id : UUID | None
    artist_goods : IArtistGoodsRead | None
    
    company : ICompanyInfoRead | None
    artist : IArtistInfoRead | None
    
    
    
    


@optional
class IPaymentUpdate(IPaymentCreate):
    
    id : UUID
            

