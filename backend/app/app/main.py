import gc
import sys
from typing import Any
from app.api import deps
from app.models.account_model import Account
from fastapi import FastAPI, Request
from app.api.deps import get_current_account, get_redis_client
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router as api_router_v1
from app.core.config import settings
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_async_sqlalchemy import SQLAlchemyMiddleware
from contextlib import asynccontextmanager
from app.utils.fastapi_globals import g, GlobalsMiddleware
from transformers import pipeline

from fastapi.staticfiles import StaticFiles

from fastapi.templating import Jinja2Templates

import cloudinary

import datetime
from sse_starlette.sse import EventSourceResponse

from fastapi import Depends, HTTPException, status


from typing import Callable
from redis.asyncio import Redis
import json

import signal

import asyncio
import time


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup

    # redis
    redis_client = await get_redis_client()
    FastAPICache.init(RedisBackend(redis_client), prefix="fastapi-cache")

    # Load a pre-trained sentiment analysis model as a dictionary to an easy cleanup
    # models: dict[str, Any] = {
    #     "sentiment_model": pipeline(
    #         "sentiment-analysis",
    #         model="distilbert-base-uncased-finetuned-sst-2-english",
    #     ),
    #     "text_generator_model": pipeline("text-generation", model="gpt2"),
    # }
    # g.set_default("sentiment_model", models["sentiment_model"])
    # g.set_default("text_generator_model", models["text_generator_model"])
    print("startup fastapi")
    yield
    # shutdown
    await FastAPICache.clear()
    print("shutdown fastapi")
    

    
    # models.clear()
    # g.cleanup()
    gc.collect()


# Core Application Instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SQLAlchemyMiddleware,
    db_url=settings.ASYNC_DATABASE_URI,
    engine_args={
        "echo": False,
        "pool_pre_ping": True,
        "pool_size": settings.POOL_SIZE,
        "max_overflow": 64,
    },
)
app.add_middleware(GlobalsMiddleware)

# Set all CORS origins enabled
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class CustomException(Exception):
    http_code: int
    code: str
    message: str

    def __init__(self, http_code: int = None, code: str = None, message: str = None):
        self.http_code = http_code if http_code else 500
        self.code = code if code else str(self.http_code)
        self.message = message


@app.get("/")
async def root():
    """
    An example "Hello world" FastAPI route.
    """
    # if oso.is_allowed(user, "read", message):
    return {
        "message": "Hello World~!!!! "
        + str(datetime.datetime.now())
        + " "
        + settings.FRONTEND_URL
    }


async def listen_to_channel(user_id: str, redis: Redis):
    # Create message listener and subscr    be on the event source channel



    try:
        async with redis.pubsub() as listener:
            await listener.subscribe("event_source_channel")

            async def before_exit(*args):
                print("Closing" )
                await listener.close()
                print("Closed112")
                await redis.close()
                print("Closed12313213")
                sys.exit(0)
            
            
            signal.signal(signal.SIGTERM, lambda *args: asyncio.create_task(before_exit(*args)))

            # Create a generator that will 'yield' our data into opened TLS connection
            while True:
                message = await listener.get_message()
                if message is None:
                    continue
                if message.get("type") == "message":
                    print(message)
                    message = json.loads(message["data"])
                    # Checking, if the user that opened this SSE conection
                    # is recipient of the message or not.
                    # The message obj has field recipient_id to compare.
                    
                    if message.get("recipient_id") == user_id or message.get("recipient_id") == "all":
                        yield {"data": json.dumps(message)}
    except Exception as e:
        print(e)

# This is where the error is thrown
        print("Cancelled")
    finally:
        await listener.unsubscribe("event_source_channel")
        await listener.close()


# SSE implementation
@app.get("/sse/notify")
async def notification(request: Request, redis: Redis = Depends(get_redis_client),
                       current_account: Account = Depends(deps.get_current_account()),
                       ):
    if current_account is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    return EventSourceResponse(listen_to_channel(current_account.id, redis))


@app.get("/sse/make-notify")
async def make_notification(redis: Redis = Depends(get_redis_client)):
    await redis.publish("event_source_channel", json.dumps({"message": "즐거우세요?", "recipient_id": "all"}))
    return {"message": "Notification sent!"}


# Add Routers
app.include_router(api_router_v1, prefix=settings.API_V1_STR)
add_pagination(app)
