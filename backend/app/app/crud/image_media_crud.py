from io import BytesIO
import uuid

from app.crud.base_crud import CRUDBase
from app.models.image_media_model import ImageMedia
from app.schemas.image_media_schema import IImageMediaCreate, IImageMediaUpdate
from app.models.media_model import Media
from app.schemas.media_schema import IMediaCreate
from sqlmodel.ext.asyncio.session import AsyncSession
import datetime
import cloudinary.uploader
from app.utils.resize_image import modify_image
from sqlmodel import select


class CRUDImageMedia(CRUDBase[ImageMedia, IImageMediaCreate, IImageMediaUpdate]):
    async def upload_images(
        self,
        *,
        image_list,
        account_id: uuid.UUID,
        db_session: AsyncSession | None = None,
        to_db: bool = True,
    ) -> list[ImageMedia]:
        
  
      
        db_session = db_session or super().get_db().session
        result = []
        for image_file in image_list:
            try:
                image_modified = modify_image(BytesIO(image_file.file.read()))
                description = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                file_name = f"{account_id}:{str(uuid.uuid4())}"
                file_data = BytesIO(image_modified.file_data)

                upload_result = cloudinary.uploader.upload(
                    file_data, public_id=file_name, resource_type="image",
                    
                )

        
                image_url = upload_result.get("secure_url")
                optimized_url = image_url.replace("upload/", "upload/w_1920/q_auto/f_auto/")

                # print(upload_result)
                media = IMediaCreate(
                    title=image_file.filename, description=description, path=optimized_url
                )

                image_media = ImageMedia(
                    media=Media.from_orm(media),
                    height=image_modified.height,
                    width=image_modified.width,
                    file_format=image_modified.file_format,
                )

                if to_db is True:
                    db_session.add(image_media)

                result.append(image_media)
            except Exception as e:
                print(e)

        await db_session.commit()
        return result

    async def get_image_media_by_id(
        self, *, id: uuid.UUID, db_session: AsyncSession | None = None
    ) -> ImageMedia | None:
        db_session = db_session or super().get_db().session

        image_media = await db_session.execute(
            select(ImageMedia).where(ImageMedia.id == id)
        )

        return image_media.scalar_one_or_none()


image = CRUDImageMedia(ImageMedia)
