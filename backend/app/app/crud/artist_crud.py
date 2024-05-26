from app.schemas.media_schema import IMediaCreate
from app.schemas.artist_schema import IArtistCreate, IArtistUpdate
from app.models.artist_model import Artist
from app.models.media_model import Media
from app.models.image_media_model import ImageMedia
from app.core.security import verify_password, get_password_hash
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


    async def create(
        self, *, obj_in: IArtistCreate, db_session: AsyncSession | None = None
    ) -> Artist:
        db_session = db_session or super().get_db().session
        db_obj = Artist.from_orm(obj_in)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj
    
    
    



 

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
 

artist = CRUDArtist(Artist)
