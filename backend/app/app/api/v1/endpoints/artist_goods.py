import datetime
import json
import time
import uuid
from app.schemas.artist_goods_schema import (
    IArtistGoodsCreate,
    IArtistGoodsListRead,
    IArtistGoodsRead,
    IArtistGoodsUpdate,
)
from app.models.account_model import Account
from app.schemas.artist_schema import IArtistRead
from app.models.artist_goods_model import ArtistGoods
from app.models.image_media_model import ImageMedia
from app.schemas.artist_goods_deal_schema import (
    IArtistGoodsDealCreate,
    IArtistGoodsDealRead,
    IArtistGoodsDealUpdate,
)
from app.models.artist_goods_deal_model import ArtistGoodsDeal
from app.utils.notify import make_notify
from app.schemas.notify_schema import INotifyCreate
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
from app.models import User, UserFollow, Media
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
from app.deps import user_deps, role_deps, auth_deps
import cloudinary.uploader
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def get_artist_goods_list(
    params: Params = Depends(),
    category: Optional[str] = Query(None),
    sort: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
) -> IGetResponsePaginated[IArtistGoodsListRead]:
    """
    Gets a paginated list of projects
    """
    # time.sleep(1)
    query = None

    query = select(crud.artist_goods.model).where(
        crud.artist_goods.model.status == "start"
    )

    if category:
        query = query.where(crud.artist_goods.model.category == category)
    else:
        pass

    if search:
        # query by title and description
        query = query.where(
            or_(
                crud.artist_goods.model.title.ilike(f"%{search}%"),
                crud.artist_goods.model.description.ilike(f"%{search}%"),
            )
        )

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

    artist_goods_list = await crud.artist_goods.get_multi_paginated(
        params=params, query=query
    )

    for artist_goods in artist_goods_list.data.items:
        artist_goods.example_image_url_list = json.loads(
            artist_goods.example_image_url_list
        )

    # time.sleep(5)

    print(artist_goods_list)
    # artist_goods_list.example_image_url_list = json.loads(artist_goods_list.example_image_url_list)
    # print("!@#!@#", json.loads(artist_goods_list.example_image_url_list))

    return create_response(data=artist_goods_list)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_artist_goods(
    new_artist_goods: IArtistGoodsCreate,
    current_account: Account = Depends(deps.get_current_account()),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    print(new_artist_goods)

    artist_goods = await crud.artist_goods.create(
        obj_in=new_artist_goods, artist_id=current_account.artist.id
    )

    return create_response(data=artist_goods)


@router.put(
    "/",
)
async def update_artist_goods(
    # artist_goods_id: UUID,
    new_artist_goods: IArtistGoodsUpdate,
    current_account: Account = Depends(deps.get_current_account()),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    print(new_artist_goods)

    artist_goods = await crud.artist_goods.update(
        obj_in=new_artist_goods, artist_id=current_account.artist.id
    )

    return create_response(data=artist_goods)


@router.get("/my")
async def get_my_artist_goods_list(
    params: Params = Depends(),
    current_account: Account = Depends(deps.get_current_account()),
) -> IGetResponsePaginated[IArtistGoodsListRead]:
    """
    Gets a paginated list of projects
    """

    query = (
        select(crud.artist_goods.model)
        .where(crud.artist_goods.model.artist_id == current_account.artist.id)
        .order_by(crud.artist_goods.model.status.desc())
        .order_by(crud.artist_goods.model.created_at.desc())
    )

    artist_goods_list = await crud.artist_goods.get_multi_paginated(
        params=params, query=query
    )

    for artist_goods in artist_goods_list.data.items:
        artist_goods.example_image_url_list = json.loads(
            artist_goods.example_image_url_list
        )

    return create_response(data=artist_goods_list)


@router.post("/deal")
async def create_artist_goods_deal(
    new_artist_goods_deal: IArtistGoodsDealCreate,
    current_account: Account = Depends(deps.get_current_account()),
    db_session=Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[IArtistGoodsDealRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    if current_account.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="company_id is required"
        )
    query = (
        select(crud.artist_goods_deal.model)
        .where(crud.artist_goods_deal.model.company_id == current_account.company_id)
        .where(crud.artist_goods_deal.model.status != "complete")
        .where(
            crud.artist_goods_deal.model.artist_goods_id
            == new_artist_goods_deal.artist_goods_id
        )
    )

    old_artist_goods_deal_row = (await db_session.execute(query)).scalars().first()

    if old_artist_goods_deal_row is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="already exist"
        )

    artist_goods_deal = await crud.artist_goods_deal.create(
        obj_in=new_artist_goods_deal, company_id=current_account.company.id
    )

    await make_notify(
        redis=redis_client,
        message=INotifyCreate(
            receiver_id=[artist_goods_deal.artist_id],
            title=f"[{current_account.company.nickname}] 님이 [{artist_goods_deal.artist_goods.title}] 상품에 대해 거래를 요청하였습니다.",
            description=f"거래 등록",
            type="artist_goods",
            action=f"artist_goods_deal/{artist_goods_deal.id}",
            created_at=int(time.time() * 1000),
        ),
    )

    return create_response(data=artist_goods_deal)


@router.put("/deal", status_code=status.HTTP_201_CREATED)
async def update_artist_goods_deal(
    new_artist_goods_deal: IArtistGoodsDealUpdate,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
    db_session=Depends(deps.get_db),
) -> IPostResponseBase[IArtistGoodsDealRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    if current_account.company_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="company_id is required"
        )
    old_artist_goods_deal = await crud.artist_goods_deal.get(
        id=new_artist_goods_deal.id, db_session=db_session
    )
    if old_artist_goods_deal is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="not exist")
    if (
        old_artist_goods_deal.company_id != current_account.company_id
        or old_artist_goods_deal.status != "pending"
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="not allowed"
        )

    artist_goods_deal = await crud.artist_goods_deal.update(
        obj_in=new_artist_goods_deal, company_id=current_account.company.id
    )

    await make_notify(
        redis=redis_client,
        message=INotifyCreate(
            receiver_id=[artist_goods_deal.artist_id],
            title=f"[{current_account.company.nickname}] 님이 [{artist_goods_deal.artist_goods.title}] 상품에 대한 거래 내용을 수정하였습니다.",
            description=f"거래 수정",
            type="artist_goods",
            action=f"artist_goods_deal/{artist_goods_deal.id}",
            created_at=int(time.time() * 1000),
        ),
    )

    return create_response(data=artist_goods_deal)


@router.get("/deal/my")
async def get_my_artist_goods_deal(
    artist_goods_id: UUID = Query(None),
    params: Params = Depends(),
    current_account: Account = Depends(deps.get_current_account()),
) -> IGetResponsePaginated[IArtistGoodsDealRead]:
    """
    Gets a paginated list of projects
    """
    if current_account.company_id is None:
        query = select(crud.artist_goods_deal.model).where(
            crud.artist_goods_deal.model.artist_id == current_account.artist_id
        )
    else:
        query = select(crud.artist_goods_deal.model).where(
            crud.artist_goods_deal.model.company_id == current_account.company_id
        )
    if artist_goods_id:
        query = query.where(
            crud.artist_goods_deal.model.artist_goods_id == artist_goods_id
        )

    artist_goods_deal_list = await crud.artist_goods_deal.get_multi_paginated(
        params=params, query=query
    )

    return create_response(data=artist_goods_deal_list)


@router.delete("/deal/{artist_goods_deal_id}")
async def delete_artist_goods_deal(
    artist_goods_deal_id: UUID,
    current_account: Account = Depends(deps.get_current_account()),
) -> IPostResponseBase[IArtistGoodsDealRead]:
    """
    Creates a new user

    Required roles:
    - admin
    """

    artist_goods_deal = await crud.artist_goods_deal.get(id=artist_goods_deal_id)

    if artist_goods_deal:
        if (
            current_account.company_id is None
            or artist_goods_deal.company_id != current_account.company_id
        ):
            raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)

        if artist_goods_deal.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="not allowed"
            )

        await crud.artist_goods_deal.remove(id=artist_goods_deal_id)
        return create_response(data=artist_goods_deal)


@router.get("/deal/{artist_goods_deal_id}")
async def get_artist_goods_deal_by_id(
    artist_goods_deal_id: UUID,
    is_edit: bool = Query(False),
    is_payment: bool = Query(False),
    current_account: Account = Depends(deps.get_current_account()),
) -> IPostResponseBase[IArtistGoodsDealRead]:
    """
    Gets a project by its id
    """

    artist_goods_deal = await crud.artist_goods_deal.get(id=artist_goods_deal_id)

    if artist_goods_deal:
        if is_edit:
            if (
                current_account.company_id is None
                or artist_goods_deal.company_id != current_account.company_id
            ):

                raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)
        else:
            if (
                current_account.artist_id
                and artist_goods_deal.artist_id != current_account.artist_id
            ):

                raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)

            if (
                current_account.company_id
                and artist_goods_deal.company_id != current_account.company_id
            ):

                raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)
        if is_payment:
            if (
                current_account.company_id is None
                or artist_goods_deal.company_id != current_account.company_id
            ):
                raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)
            if artist_goods_deal.status != "accept":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="not allowed"
                )

        artist_goods_deal.request_image_list = json.loads(
            artist_goods_deal.request_image_list
        )
        if artist_goods_deal.request_file_list:
            artist_goods_deal.request_file_list = json.loads(
                artist_goods_deal.request_file_list
            )
        else:
            artist_goods_deal.request_file_list = []

        return create_response(data=artist_goods_deal)
    else:
        raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)


@router.put("/deal/{artist_goods_deal_id}/accept", status_code=status.HTTP_201_CREATED)
async def accept_artist_goods_deal(
    artist_goods_deal_id: UUID,
    current_account: Account = Depends(deps.get_current_account()),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[IArtistGoodsDealRead]:
    """
    Gets a project by its id
    """

    artist_goods_deal = await crud.artist_goods_deal.get(id=artist_goods_deal_id)

    if artist_goods_deal:

        if (
            current_account.artist_id
            and artist_goods_deal.artist_id == current_account.artist_id
        ):

            await crud.artist_goods_deal.update_by_dict(
                obj_current=artist_goods_deal, obj_new={"status": "accept"}
            )
            await make_notify(
                redis=redis_client,
                message=INotifyCreate(
                    receiver_id=[artist_goods_deal.company_id],
                    title=f"[{current_account.artist.nickname}] 님이 [{artist_goods_deal.artist_goods.title}] 상품에 대한 거래를 수락하였습니다.",
                    description=f"거래 수락",
                    type="artist_goods",
                    action=f"artist_goods_deal/{artist_goods_deal.id}",
                    created_at=int(time.time() * 1000),
                ),
            )
            return create_response(data=artist_goods_deal)
        else:
            raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)

    else:
        raise IdNotFoundException(ArtistGoodsDeal, artist_goods_deal_id)


@router.get("/{artist_goods_id}")
async def get_artist_goods_by_id(
    artist_goods_id: UUID,
    is_edit: bool = Query(False),
    current_account: Account = Depends(
        deps.get_current_account(is_login_required=False)
    ),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Gets a project by its id
    """
    # time.sleep(1)

    artist_goods = await crud.artist_goods.get(id=artist_goods_id)

    if artist_goods:

        if is_edit:
            # print(current_account.artist.id, artist_goods.artist_id)
            if (
                current_account is None
                or artist_goods.artist_id != current_account.artist.id
            ):
                raise IdNotFoundException(ArtistGoods, artist_goods_id)
        else:
            if artist_goods.status == "draft" or artist_goods.status == "pending":
                if (
                    current_account is None
                    or artist_goods.artist_id != current_account.artist.id
                ):
                    raise IdNotFoundException(ArtistGoods, artist_goods_id)

        artist_goods.example_image_url_list = json.loads(
            artist_goods.example_image_url_list
        )

        return create_response(data=artist_goods)
    else:
        raise IdNotFoundException(ArtistGoods, artist_goods_id)


@router.delete("/{artist_goods_id}")
async def get_artist_goods_by_id(
    artist_goods_id: UUID,
    current_account: Account = Depends(
        deps.get_current_account(is_login_required=False)
    ),
) -> IPostResponseBase[IArtistGoodsRead]:
    """
    Gets a project by its id
    """
    # time.sleep(1)

    artist_goods = await crud.artist_goods.get(id=artist_goods_id)
    if artist_goods:
        if artist_goods.artist_id != current_account.artist.id:
            raise IdNotFoundException(ArtistGoods, artist_goods_id)
        await crud.artist_goods.remove(id=artist_goods_id)
        return create_response(data=artist_goods)
    else:
        raise IdNotFoundException(ArtistGoods, artist_goods_id)
