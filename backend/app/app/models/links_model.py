from sqlmodel import Field
from app.models.base_uuid_model import BaseUUIDModel
from uuid import UUID


class LinkGroupUser(BaseUUIDModel, table=True):
    group_id: UUID | None = Field(
        default=None, nullable=False, foreign_key="Group.id", primary_key=True
    )
    user_id: UUID | None = Field(
        default=None, nullable=False, foreign_key="User.id", primary_key=True
    )


class LinkProjectUser(BaseUUIDModel, table=True):
    project_id: UUID | None = Field(
        default=None, nullable=False, foreign_key="Project.id", primary_key=True
    )
    user_id: UUID | None = Field(
        default=None, nullable=False, foreign_key="User.id", primary_key=True
    )
