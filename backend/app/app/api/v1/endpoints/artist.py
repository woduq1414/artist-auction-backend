import json
from app.schemas.artist_goods_schema import IArtistGoodsCreate, IArtistGoodsRead
from app.models.account_model import Account
from app.schemas.artist_schema import IArtistRead
from fastapi import HTTPException
from io import BytesIO
from typing import Annotated, Optional
from uuid import UUID
from fastapi import Form
from redis.asyncio import Redis
from app.api.v1.endpoints.role import update_role
from app.models.group_model import Group
from app.models.links_model import LinkGroupUser
from app.utils.exceptions import (
    IdNotFoundException,
    SelfFollowedException,
    UserFollowedException,
    UserNotFollowedException,
    UserSelfDeleteException,
)
from app import crud
from app.api import deps
from app.deps import user_deps, role_deps
from app.models import User, UserFollow
from app.models.role_model import Role
from app.utils.login import verify_kakao_access_token
from app.utils.minio_client import MinioClient
from app.utils.resize_image import modify_image
from app.utils.email import send_security_code_mail, verify_security_code
from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Query,
    Response,
    UploadFile,
    status,
)
from app.schemas.media_schema import IMediaCreate
from app.schemas.response_schema import (
    IDeleteResponseBase,
    IGetResponseBase,
    IGetResponsePaginated,
    IPostResponseBase,
    IPutResponseBase,
    create_response,
)
from app.schemas.role_schema import IRoleEnum, IRoleRead, IRoleUpdate
from app.schemas.user_follow_schema import IUserFollowRead
from app.schemas.user_schema import (
    IUserCreate,
    IUserRead,
    IUserReadTrivial,
    IUserReadWithoutGroups,
    IUserStatus,
)
from app.schemas.user_follow_schema import (
    IUserFollowReadCommon,
)
from fastapi_pagination import Params
from sqlmodel import and_, select, col, or_, text
from pydantic import BaseModel, ValidationError


router = APIRouter()

class Base(BaseModel):
    name: str
    point: Optional[float] = None
    is_accepted: Optional[bool] = False
    
    

@router.get("/goods")
async def get_artist_goods_list(
    params: Params = Depends(),

) -> IGetResponsePaginated[IArtistGoodsRead]:
    """
    Gets a paginated list of projects
    """
    artist_goods_list = await crud.artist_goods.get_multi_paginated(params=params)
    
    for artist_goods in artist_goods_list.data.items:
        artist_goods.example_image_url_list = json.loads(artist_goods.example_image_url_list)
    
    
    
    print(artist_goods_list)
    # artist_goods_list.example_image_url_list = json.loads(artist_goods_list.example_image_url_list)
    # print("!@#!@#", json.loads(artist_goods_list.example_image_url_list))
    
    return create_response(data=artist_goods_list)
    
    
@router.post("/goods", status_code=status.HTTP_201_CREATED)
async def create_artist_goods(
    new_artist_goods: IArtistGoodsCreate,


    current_account: Account = Depends(
        deps.get_current_account()
    ),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """
    
    print(new_artist_goods)
    
    artist_goods = await crud.artist_goods.create(obj_in=new_artist_goods, artist_id=current_account.artist.id)
    
    
    return create_response(data=artist_goods)


