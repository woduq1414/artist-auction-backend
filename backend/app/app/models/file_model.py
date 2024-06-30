from uuid import UUID
from app.models.base_uuid_model import BaseUUIDModel
from app.models.account_model import Account
from sqlmodel import SQLModel, Field, Relationship
from app.utils.minio_client import MinioClient
from app.core.config import settings
from app import api


class FileBase(SQLModel):
    title: str | None
    description: str | None
    path: str | None
    format : str | None


class File(BaseUUIDModel, FileBase, table=True):
    
    account_id: UUID | None = Field(default=None, foreign_key="Account.id")
    account : Account = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "File.account_id==Account.id",
        }
    )
    
    @property
    def link(self) -> str | None:
        if self.path is None:
            return ""
        # minio: MinioClient = api.deps.minio_auth()
        # url = minio.presigned_get_object(
        #     bucket_name=settings.MINIO_BUCKET, object_name=self.path
        # )
        return self.path
    
    
