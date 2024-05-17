from app.models.base_uuid_model import BaseUUIDModel
from app.models.links_model import LinkGroupUser
from app.models.links_model import LinkProjectUser
from app.models.image_media_model import ImageMedia
from app.schemas.common_schema import IGenderEnum
from datetime import datetime
from sqlmodel import BigInteger, Field, SQLModel, Relationship, Column, DateTime, String
from typing import Optional
from sqlalchemy_utils import ChoiceType
from pydantic import EmailStr
from uuid import UUID


class UserBase(SQLModel):
    name: str = Field(nullable=False)
    email: EmailStr = Field(
        nullable=True, index=True, sa_column_kwargs={"unique": True}
    )
    is_active: bool = Field(default=False)
    is_superuser: bool = Field(default=False)
    birthdate: datetime | None = Field(
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )  # birthday with timezone
    role_id: UUID | None = Field(default=None, foreign_key="Role.id")
    phone: str | None
    gender: IGenderEnum | None = Field(default=None)
    state: str | None
    country: str | None
    address: str | None

    login_type: str | None = Field(default=None, nullable=True)
    kakao_id: str | None = Field(default=None, nullable=True)
    is_email_verified: bool | None = Field(nullable=True)



class User(BaseUUIDModel, UserBase, table=True):

    

    hashed_password: str | None = Field(nullable=False, index=True)
    role: Optional["Role"] = Relationship(  # noqa: F821
        back_populates="users", sa_relationship_kwargs={"lazy": "joined"}
    )
    groups: list["Group"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=LinkGroupUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )
    projects: list["Project"] = Relationship(  # noqa: F821
        back_populates="users",
        link_model=LinkProjectUser,
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    image_id: UUID | None = Field(default=None, foreign_key="ImageMedia.id")
    image: ImageMedia = Relationship(
        sa_relationship_kwargs={
            "lazy": "joined",
            "primaryjoin": "User.image_id==ImageMedia.id",
        }
    )
    follower_count: int | None = Field(
        sa_column=Column(BigInteger(), server_default="0")
    )
    following_count: int | None = Field(
        sa_column=Column(BigInteger(), server_default="0")
    )


