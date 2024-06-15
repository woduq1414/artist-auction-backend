from app.schemas.media_schema import IMediaCreate
from app.schemas.artist_schema import IArtistCreate, IArtistUpdate
from app.models.artist_model import Artist
from app.models.media_model import Media
from app.models.image_media_model import ImageMedia
from app.core.security import verify_password, get_password_hash
from app.models.artist_goods_model import ArtistGoods
from pydantic.networks import EmailStr
from typing import Any
from app.crud.base_crud import CRUDBase
from app.crud.user_follow_crud import user_follow as UserFollowCRUD
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

from app.utils.login import verify_kakao_access_token


class CRUDArtist(CRUDBase[Artist, IArtistCreate, IArtistUpdate]):

    async def get_artist_by_nickname(
        self, *, nickname: str, db_session: AsyncSession | None = None
    ) -> Artist | None:
        db_session = db_session or super().get_db().session
        artists = await db_session.execute(select(Artist).where(Artist.nickname == nickname))
        return artists.scalar_one_or_none()
    
    
    async def get_artist_by_artist_goods_id(
        self, *, artist_goods_id: UUID, db_session: AsyncSession | None = None
    ) -> Artist | None:
        db_session = db_session or super().get_db().session
        artist = await db_session.execute(select(Artist).where(ArtistGoods.id == artist_goods_id))
        return artist.scalar_one_or_none()


    async def create(
        self, *, obj_in: IArtistCreate, db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        db_obj = Artist.from_orm(obj_in)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj
    
    
    

    async def update(
        self,
        *,
        obj_in: IArtistUpdate,
        db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        
        db_session.add(obj_in)
        await db_session.commit()
        await db_session.refresh(obj_in)
        
        return obj_in
 

    async def update_photo(
        self,
        *,
        artist : Artist,
        image_media : ImageMedia,
        db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        print(db_session)
        artist.profile_image = image_media
        db_session.add(artist)
        await db_session.commit()
        await db_session.refresh(artist)
        return artist


artist = CRUDArtist(Artist)
