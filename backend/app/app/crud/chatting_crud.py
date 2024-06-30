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
from app.models.chatting_model import Chatting
from app.schemas.chatting_schema import IChattingCreate, IChattingUpdate
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


class CRUDChatting(CRUDBase[Chatting, IChattingCreate, IChattingUpdate]):

    async def get_by_artist_id(
        self, *, artist_id: UUID, db_session: AsyncSession | None = None
    ) -> list[Chatting] | None:
        db_session = db_session or super().get_db().session
        chatting = await db_session.execute(select(Chatting).where(Chatting.artist_id == artist_id))
        return chatting.scalars().all()
    
    
    async def get_by_company_id(
        self, *, company_id: UUID, db_session: AsyncSession | None = None
    ) -> list[Chatting] | None:
        db_session = db_session or super().get_db().session
        chatting = await db_session.execute(select(Chatting).where(Chatting.company_id == company_id))
        return chatting.scalars().all()
    
    
    
    
    async def get_by_users(
        self, *, artist_id: UUID, company_id: UUID, db_session: AsyncSession | None = None
    ) -> Chatting | None:
        db_session = db_session or super().get_db().session
        chatting = await db_session.execute(select(Chatting).where(and_(Chatting.artist_id == artist_id, Chatting.company_id == company_id)))
        return chatting.scalars().first()
    
    

    async def create(
        self, *, obj_in: IChattingCreate | IChattingUpdate,
        is_update : bool = False,
        db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        
  
        
        
        new_chatting = Chatting(
            content=obj_in.content,
            status="created",
            artist_id=obj_in.artist_id,
            company_id=obj_in.company_id,
            redis_key=obj_in.redis_key,
        )
     
        if not is_update:
            db_session.add(new_chatting)
            await db_session.commit()
            await db_session.refresh(new_chatting)
            return new_chatting
        else:
            
            pass
                
        
        
 
    
    
    # async def update(
    #       self, *, obj_in: IChattingCreate | IChattingUpdate, artist_id : UUID,
       
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


chatting = CRUDChatting(Chatting)
