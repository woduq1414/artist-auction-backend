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
from pydantic.networks import EmailStr
from typing import Any
from app.crud.base_crud import CRUDBase
from app.crud.user_follow_crud import user_follow as UserFollowCRUD
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
import datetime
from app.utils.login import verify_kakao_access_token

from sqlalchemy import select, and_


class CRUDArtistGoods(CRUDBase[ArtistGoods, IArtistGoodsCreate, IArtistGoodsUpdate]):

    async def get_artist_goods_list_by_artist_id(
        self, *, artist_id: UUID, db_session: AsyncSession | None = None
    ) -> list[ArtistGoods] | None:
        db_session = db_session or super().get_db().session
        artist_goods = await db_session.execute(select(ArtistGoods).where(ArtistGoods.artist_id == artist_id))
        return artist_goods.scalars().all()
    
    

    async def create(
        self, *, obj_in: IArtistGoodsCreate | IArtistGoodsUpdate, artist_id : UUID,
        is_update : bool = False,
        db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        
        
        # 원래는 검수 후 start_date, end_date가 설정.
        
        # start_date는 오늘 날짜 자정으로
        obj_in.start_date = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # end_date는 start_date에서 duration을 더한 시간으로
        obj_in.end_date = obj_in.start_date + datetime.timedelta(days=obj_in.duration)
        
        status = ''
        if obj_in.type == 'submit':
            status = 'start'
        else:
            status = 'draft'
        
        
        new_artist_goods = ArtistGoods(
            title=obj_in.title,
            description=obj_in.description,
            category=obj_in.category,
            price=obj_in.price * 10000,
            content=obj_in.content,
            duration=obj_in.duration,
            start_date=obj_in.start_date,
            end_date=obj_in.end_date,
            # status='pending',
            status=status,
            max_price = obj_in.price * 10000
        )
        new_artist_goods.main_image_id = obj_in.main_image
        
        new_artist_goods.artist_id = artist_id
        
        example_image_url_list = []
        print(obj_in.example_image_list)
        for example_image_id in obj_in.example_image_list:
            image = await crud.image.get_image_media_by_id(id = example_image_id)
            if image:
                example_image_url_list.append({
                    'id' : str(image.id),
                    'url' : image.media.path
                })    
        
        print(example_image_url_list)
        
        new_artist_goods.example_image_url_list = json.dumps(example_image_url_list)
        
        if not is_update:
            db_session.add(new_artist_goods)
            await db_session.commit()
            await db_session.refresh(new_artist_goods)
            return new_artist_goods
        else:
            
            target_artist_goods = await db_session.execute(select(ArtistGoods).where(and_(ArtistGoods.artist_id == artist_id, ArtistGoods.id == obj_in.id)))
            target_artist_goods = target_artist_goods.scalars().first()
            
            if not target_artist_goods:
                raise Exception('해당 상품이 존재하지 않습니다.')
            
            # update with new_artist_goods instance
            
            target_artist_goods.title = new_artist_goods.title
            target_artist_goods.description = new_artist_goods.description
            target_artist_goods.category = new_artist_goods.category
            target_artist_goods.price = new_artist_goods.price
            target_artist_goods.content = new_artist_goods.content
            target_artist_goods.duration = new_artist_goods.duration
            target_artist_goods.start_date = new_artist_goods.start_date
            target_artist_goods.end_date = new_artist_goods.end_date
            target_artist_goods.status = new_artist_goods.status
            target_artist_goods.max_price = new_artist_goods.max_price
            target_artist_goods.main_image_id = new_artist_goods.main_image_id
            target_artist_goods.example_image_url_list = new_artist_goods.example_image_url_list
            
            await db_session.commit()
            await db_session.refresh(target_artist_goods)
            
            return target_artist_goods
                
        
        
 
    
    
    async def update(
          self, *, obj_in: IArtistGoodsCreate | IArtistGoodsUpdate, artist_id : UUID,
       
        db_session: AsyncSession | None = None
    ) -> Artist:
        
        return await self.create(obj_in=obj_in, artist_id=artist_id, is_update=True, db_session=db_session)
        
    
        


 

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


artist_goods = CRUDArtistGoods(ArtistGoods)
