import json
import time
from app.schemas.artist_goods_schema import IArtistGoodsCreate, IArtistGoodsListRead, IArtistGoodsRead
from app.models.account_model import Account
from app.schemas.artist_schema import IArtistRead
from app.models.artist_goods_model import ArtistGoods
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
    category: Optional[str] = Query(None),
    sort : Optional[str] = Query(None),
) -> IGetResponsePaginated[IArtistGoodsListRead]:
    """
    Gets a paginated list of projects
    """
    time.sleep(1)
    query = None
    
    if category:
        query = select(crud.artist_goods.model).where(crud.artist_goods.model.category == category)
    else:
        query = select(crud.artist_goods.model)
        
    available_sort = ["recent", "highPrice", "lowPrice", "end_date"]
    
    if sort:
        if sort in available_sort:
            if sort == "recent":
                query = query.order_by(crud.artist_goods.model.created_at.desc())
            elif sort == "highPrice":
                query = query.order_by(crud.artist_goods.model.price.desc())
            elif sort == "lowPrice":
                query = query.order_by(crud.artist_goods.model.price.asc())
            elif sort == "end_date":
                query = query.order_by(crud.artist_goods.model.end_date.asc())
        
    
    artist_goods_list = await crud.artist_goods.get_multi_paginated(params=params, query=query)
    
    for artist_goods in artist_goods_list.data.items:
        artist_goods.example_image_url_list = json.loads(artist_goods.example_image_url_list)
    
    # time.sleep(5)
    
    
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


@router.get("/goods/{artist_goods_id}")
async def get_artist_goods_by_id(
    artist_goods_id: UUID,

) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Gets a project by its id
    """
    time.sleep(1)
    artist_goods = await crud.artist_goods.get(id=artist_goods_id)
    
    if artist_goods:
        artist_goods.example_image_url_list = json.loads(artist_goods.example_image_url_list)
        return create_response(data=artist_goods)
    else:
        raise IdNotFoundException(ArtistGoods, artist_goods_id)
