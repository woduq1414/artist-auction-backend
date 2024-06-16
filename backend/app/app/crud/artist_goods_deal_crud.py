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

from sqlalchemy import select, and_


class CRUDArtistGoodsDeal(CRUDBase[ArtistGoodsDeal, IArtistGoodsDealCreate, IArtistGoodsDealUpdate]):

    async def get_artist_goods_list_by_artist_id(
        self, *, artist_id: UUID, db_session: AsyncSession | None = None
    ) -> list[ArtistGoodsDeal] | None:
        db_session = db_session or super().get_db().session
        artist_goods = await db_session.execute(select(ArtistGoods).where(ArtistGoods.artist_id == artist_id))
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
            company_id=company_id
        )
        
        example_image_url_list = []
        for example_image_id in obj_in.request_image_list:
            image = await crud.image.get_image_media_by_id(id = example_image_id)
            if image:
                example_image_url_list.append({
                    'id' : str(image.id),
                    'url' : image.media.path
                })    
        
        print(example_image_url_list)
        
        new_artist_goods_deal.request_image_list = json.dumps(example_image_url_list)
        
        
        db_session.add(new_artist_goods_deal)
        await db_session.commit()
        await db_session.refresh(new_artist_goods_deal)
        return new_artist_goods_deal
        
        
 
    
    
    # async def update(
    #       self, *, obj_in: IArtistGoodsCreate | IArtistGoodsUpdate, artist_id : UUID,
       
    #     db_session: AsyncSession | None = None
    # ) -> Artist:
        
    #     return await self.create(obj_in=obj_in, artist_id=artist_id, is_update=True, db_session=db_session)
        
    
        


 

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
