from datetime import timedelta
import time
from typing import Any, List, Optional
from app.schemas.notify_schema import INotifyCreate, INotifyRead
from app.models.account_model import Account
from app.schemas.payment_schema import IPaymentCreate, IPaymentRead
from fastapi import APIRouter, Body, Depends, HTTPException
from redis.asyncio import Redis
from app.utils.login import create_login_token
from app.utils.token import get_valid_tokens
from app.utils.token import delete_tokens
from app.utils.token import add_token_to_redis
from app.core.security import get_password_hash
from app.core.security import verify_password
from app.models.user_model import User
from app.api.deps import get_redis_client
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from pydantic import EmailStr
from pydantic import ValidationError
from app import crud
from app.api import deps
from app.core import security
from app.core.config import settings
from app.schemas.common_schema import ILoginTypeEnum, TokenType, IMetaGeneral
from app.schemas.token_schema import TokenRead, Token, RefreshToken
from app.schemas.response_schema import (
    IGetResponseBase,
    IPostResponseBase,
    create_response,
)
from app.utils.notify import delete_notify, delete_notify_all, get_notify, make_notify
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
import requests
import base64
import json


router = APIRouter()

@router.post("/new")
async def new_payment(
    new_payment: IPaymentCreate,
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[dict[str, Any]]:
    order_id, amount = new_payment.order_id, new_payment.amount
    await redis_client.set("payment:" + order_id, amount)
    return create_response({"order_id": order_id, "amount": amount})
    


@router.post("/confirm")
async def confirm_payment(
    new_payment: IPaymentCreate,
    current_account: Account = Depends(deps.get_current_account()),
    db_session=Depends(deps.get_db),
    redis_client: Redis = Depends(deps.get_redis_client),
) -> IPostResponseBase[IPaymentRead]:
    """
    get notify
    """

    artist_goods_deal_id = new_payment.order_id.split("_")[0]
    artist_goods_deal = await crud.artist_goods_deal.get(db_session = db_session, id = artist_goods_deal_id)
    if artist_goods_deal is None:
        raise HTTPException(status_code=400, detail="상품 거래가 존재하지 않습니다.")
    if artist_goods_deal.status != "accept":
        raise HTTPException(status_code=400, detail="상품 거래가 수락되지 않았습니다.")
    if artist_goods_deal.company_id != current_account.company_id:
        raise HTTPException(status_code=400, detail="상품 거래의 회사가 일치하지 않습니다.")    
    
    old_payment = await crud.payment.get_by_artist_goods_deal_id(db_session = db_session, artist_goods_deal_id = artist_goods_deal_id)
    if old_payment is not None:
        raise HTTPException(status_code=400, detail="이미 결제가 완료되었습니다.")
    
    print(await redis_client.get("payment:" + new_payment.order_id), new_payment.order_id, new_payment.amount)
    if int(await redis_client.get("payment:" + new_payment.order_id)) != new_payment.amount:
        raise HTTPException(status_code=400, detail="결제 금액이 일치하지 않습니다.")
    
    new_payment.artist_id = artist_goods_deal.artist_id
    new_payment.company_id = artist_goods_deal.company_id

    # return
    res = requests.post(
        "https://api.tosspayments.com/v1/payments/confirm", headers={
            "Authorization" : "Basic " + base64.b64encode((settings.TOSS_API_KEY + ":").encode("utf8")).decode("utf8"),
                'Content-Type': 'application/json',
            }, json={
                "paymentKey" : new_payment.payment_key,
                "amount" : new_payment.amount,
                "orderId" : new_payment.order_id,
            }
    )
    print(res.text)
    print(res.status_code)
    
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="결제 확인에 실패하였습니다.")
    
    detail = json.loads(res.text)
    # detail = 
    
    new_payment.detail = detail
    
    payment = await crud.payment.create(db_session = db_session, obj_in=new_payment, artist_goods_deal_id=artist_goods_deal_id)
    

    artist_goods_deal.status = "paid"
    
    artist_goods = artist_goods_deal.artist_goods
    
    artist_goods.max_price = max(artist_goods.max_price, artist_goods_deal.price * 10000)
    
    await db_session.commit()

    await make_notify(
                    redis=redis_client,
                    message=INotifyCreate(
                        receiver_id=[artist_goods_deal.artist_id],
                        title=f"[{current_account.company.nickname}] 님이 [{artist_goods_deal.artist_goods.title}] 상품에 대한 거래에 대해 결제를 완료하였습니다.",
                        description=f"결제 완료",
                        type="artist_goods",
                        action=f"artist_goods_deal/{artist_goods_deal.id}",
                        created_at=int(time.time() * 1000),
                    ),
                )

    return create_response(payment)
