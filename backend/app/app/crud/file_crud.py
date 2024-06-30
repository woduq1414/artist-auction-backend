from io import BytesIO
import uuid

from app.crud.base_crud import CRUDBase
from app.models.file_model import File
from app.schemas.file_schema import IFileCreate, IFileUpdate
from app.models.media_model import Media
from app.schemas.media_schema import IMediaCreate

from sqlmodel.ext.asyncio.session import AsyncSession
import datetime
import cloudinary.uploader
from app.utils.resize_image import modify_image
from sqlmodel import select
from app.core.config import settings

class CRUDFile(CRUDBase[File, IFileCreate, IFileUpdate]):
    async def upload_files(
        self,
        *,
        file_list,
        account_id: uuid.UUID,
        db_session: AsyncSession | None = None,
        to_db: bool = True,
        type : str = "default"
    ) -> list[File]:
        
  
        if to_db is True:
            db_session = db_session or super().get_db().session
        print(db_session)
        result = []
        for file in file_list:
         
            description = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file_name = file.filename
            file_data = file.file.read()
            
            # 100MB 용량 제한
            
            if len(file_data) > 100000000:
                raise Exception("파일 용량이 100MB를 초과했습니다.")
            
            
            upload_result = cloudinary.uploader.upload(
                file_data, public_id=file_name,
                resource_type = "auto",
                folder = settings.ENVIRONMENT
                
            )

    
            file_url = upload_result.get("secure_url")

            
            file = File(
                title = file.filename,
                description = description,
                path = file_url,
                
                format= file.content_type,
                account_id = account_id
            )

            if to_db is True:
                db_session.add(file)

            result.append(file)
           

        if to_db is True:
            await db_session.commit()

        return result

    async def get_file_by_id(
        self, *, id: uuid.UUID, db_session: AsyncSession | None = None
    ) -> File | None:
        db_session = db_session or super().get_db().session

        file = await db_session.execute(
            select(File).where(File.id == id)
        )

        return file.scalar_one_or_none()


file = CRUDFile(File)
