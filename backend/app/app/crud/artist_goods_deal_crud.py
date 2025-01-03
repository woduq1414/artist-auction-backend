import json
from app.schemas.media_schema import IMediaCreate
from app.schemas.artist_schema import IArtistCreate, IArtistUpdate
from app.schemas.artist_goods_schema import IArtistGoodsCreate, IArtistGoodsUpdate
from app.models.artist_goods_model import ArtistGoods
from app.models.artist_model import Artist
from app.models.media_model import Media
from app.models.image_media_model import ImageMedia
from app.core.security import verify_password, get_password_hash
from app import crud
from app.schemas.artist_goods_deal_schema import IArtistGoodsDealCreate, IArtistGoodsDealUpdate
from app.models.artist_goods_deal_model import ArtistGoodsDeal
from pydantic.networks import EmailStr
from typing import Any
from app.crud.base_crud import CRUDBase
from app.crud.user_follow_crud import user_follow as UserFollowCRUD
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
import datetime
from app.utils.login import verify_kakao_access_token

from sqlalchemy import select, and_, or_


class CRUDArtistGoodsDeal(CRUDBase[ArtistGoodsDeal, IArtistGoodsDealCreate, IArtistGoodsDealUpdate]):

    async def get_artist_goods_deal_list_by_artist_id(
        self, *, artist_id: UUID, db_session: AsyncSession | None = None
    ) -> list[ArtistGoodsDeal] | None:
        db_session = db_session or super().get_db().session
        artist_goods = await db_session.execute(select(ArtistGoodsDeal).where(ArtistGoodsDeal.artist_id == artist_id))
        return artist_goods.scalars().all()
    
    async def get_paid_artist_goods_deal_list_by_artist_goods_id(
        self, *, artist_goods_id: UUID, db_session: AsyncSession | None = None
    ) -> list[ArtistGoodsDeal] | None:
        db_session = db_session or super().get_db().session
        artist_goods = await db_session.execute(select(ArtistGoodsDeal).where(ArtistGoodsDeal.artist_goods_id == artist_goods_id).where(or_(ArtistGoodsDeal.status == 'paid', ArtistGoodsDeal.status == 'completed'))
                                                .order_by(ArtistGoodsDeal.created_at.asc()))
        return artist_goods.scalars().all()
    
    
    async def get_artist_goods_deal_list_by_artist_id(
        self, *, artist_id: UUID, db_session: AsyncSession | None = None
    ) -> list[ArtistGoodsDeal] | None:
        db_session = db_session or super().get_db().session
        artist_goods_deal = await db_session.execute(select(ArtistGoodsDeal).where(ArtistGoodsDeal.artist_id == artist_id))
        return artist_goods_deal.scalars().all()
    
    async def get_artist_goods_deal_list_by_company_id(
        
        self, *, company_id: UUID, db_session: AsyncSession | None = None
    ) -> list[ArtistGoodsDeal] | None:
        db_session = db_session or super().get_db().session
        artist_goods_deal = await db_session.execute(select(ArtistGoodsDeal).where(ArtistGoodsDeal.company_id == company_id))
        return artist_goods_deal.scalars().all()
    
    

    async def create(
        self, *, obj_in: IArtistGoodsDealCreate | IArtistGoodsDealUpdate, company_id : UUID,
        is_update : bool = False,
        db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        
        
        artist = await crud.artist.get_artist_by_artist_goods_id(artist_goods_id=obj_in.artist_goods_id)
        if artist is None:
            raise Exception("artist is not exist")
        
        artist_id = artist.id
        
        
        new_artist_goods_deal = ArtistGoodsDeal(
            title=obj_in.title,
            description=obj_in.description,

            status='pending',
            price=obj_in.price,
            artist_goods_id=obj_in.artist_goods_id,
            artist_id=artist_id,
            company_id=company_id,
            payment_id=None
        )
        
        example_image_url_list = []
        for example_image_id in obj_in.request_image_list:
            image = await crud.image.get_image_media_by_id(id = example_image_id)
            if image:
                example_image_url_list.append({
                    'id' : str(image.id),
                    'url' : image.media.path
                })    
                
        
        request_file_list = []
        for request_file_id in obj_in.request_file_list:
            file = await crud.file.get_file_by_id(id = request_file_id)
            if file:
                request_file_list.append({
                    'id' : str(file.id),
                    'url' : file.path,
                    "title" : file.title,
                })
        
        print(example_image_url_list)
        
        new_artist_goods_deal.request_image_list = json.dumps(example_image_url_list)
        new_artist_goods_deal.request_file_list = json.dumps(request_file_list)
        
        
        if not is_update:
            db_session.add(new_artist_goods_deal)
            await db_session.commit()
            await db_session.refresh(new_artist_goods_deal)
            return new_artist_goods_deal
        else:
            
            target_artist_goods_deal = await db_session.execute(select(ArtistGoodsDeal).where(and_(ArtistGoodsDeal.company_id == company_id, ArtistGoodsDeal.id == obj_in.id)))
            target_artist_goods_deal = target_artist_goods_deal.scalars().first()
            
            if not target_artist_goods_deal:
                raise Exception('해당 상품이 존재하지 않습니다.')
            
            # update with new_artist_goods instance
            
            target_artist_goods_deal.title = new_artist_goods_deal.title
            target_artist_goods_deal.description = new_artist_goods_deal.description
            target_artist_goods_deal.price = new_artist_goods_deal.price
            target_artist_goods_deal.request_image_list = new_artist_goods_deal.request_image_list
            target_artist_goods_deal.request_file_list = new_artist_goods_deal.request_file_list
            
            await db_session.commit()
            await db_session.refresh(target_artist_goods_deal)
            
            return target_artist_goods_deal
        
        
 
    
    
    async def update(
          self, *, obj_in: IArtistGoodsDealCreate | IArtistGoodsDealUpdate, company_id : UUID,
       
        db_session: AsyncSession | None = None
    ) -> ArtistGoodsDeal:
        
        return await self.create(obj_in=obj_in, company_id=company_id, is_update=True, db_session=db_session)
        
    
    async def update_by_dict(
         self,
        *,
        obj_current: ArtistGoodsDeal,
        obj_new: IArtistGoodsDealUpdate | dict[str, Any] | ArtistGoodsDeal,
        db_session: AsyncSession | None = None,
    ) -> ArtistGoodsDeal:
        
        return await super().update(obj_current=obj_current, obj_new=obj_new, db_session=db_session)


    async def get_price_data(
        self,
        *,
        artist_goods_id: UUID,
        start_date: datetime.datetime,
        start_price: int,
        db_session: AsyncSession | None = None
    ) -> dict | None:
        db_session = db_session or super().get_db().session
        artist_goods_deal_list = await crud.artist_goods_deal.get_paid_artist_goods_deal_list_by_artist_goods_id(artist_goods_id=artist_goods_id)
    
        sum_price = 0
        price_by_day = {}
        
        price_by_day[start_date.strftime("%Y-%m-%d")] = [start_price]
        
        if artist_goods_deal_list:
            for artist_goods_deal in artist_goods_deal_list:
        
                sum_price += artist_goods_deal.price

                day = artist_goods_deal.created_at.strftime("%Y-%m-%d")
            
                if day in price_by_day:
                    price_by_day[day].append(artist_goods_deal.price)
                else:
                    price_by_day[day] = [artist_goods_deal.price]
            
        values = []
        keys = []
        for day in price_by_day:
            price_by_day[day] = sum(price_by_day[day]) / len(price_by_day[day])
            
            values.append(price_by_day[day])
            keys.append(day)
            
        if not artist_goods_deal_list:
            keys = keys * 2
            values = values * 2
            
        return {
            "average_price" : sum_price / len(artist_goods_deal_list) if  len(artist_goods_deal_list) > 0 else None,
            "price_by_day" : values,
            "day_list" : keys
        }

    # async def update_photo(
    #     self,
    #     *,
    #     user: User,
    #     image: IMediaCreate,
    #     heigth: int,
    #     width: int,
    #     file_format: str,
    # ) -> User:
    #     db_session = super().get_db().session
    #     user.image = ImageMedia(
    #         media=Media.from_orm(image),
    #         height=heigth,
    #         width=width,
    #         file_format=file_format,
    #     )
    #     db_session.add(user)
    #     await db_session.commit()
    #     await db_session.refresh(user)
    #     return user

    # async def remove(
    #     self, *, id: UUID | str, db_session: AsyncSession | None = None
    # ) -> User:
    #     db_session = db_session or super().get_db().session
    #     response = await db_session.execute(
    #         select(self.model).where(self.model.id == id)
    #     )
    #     obj = response.scalar_one()

    #     followings = await UserFollowCRUD.get_follow_by_user_id(user_id=obj.id)
    #     if followings:
    #         for following in followings:
    #             user = await self.get(id=following.target_user_id)
    #             user.follower_count -= 1
    #             db_session.add(user)
    #             await db_session.delete(following)

    #     followeds = await UserFollowCRUD.get_follow_by_target_user_id(
    #         target_user_id=obj.id
    #     )
    #     if followeds:
    #         for followed in followeds:
    #             user = await self.get(id=followed.user_id)
    #             user.following_count -= 1
    #             db_session.add(user)
    #             await db_session.delete(followed)

    #     await db_session.delete(obj)
    #     await db_session.commit()
    #     return obj


artist_goods_deal = CRUDArtistGoodsDeal(ArtistGoodsDeal)
