
from fastapi import APIRouter
from app.api.v1.endpoints import (
    natural_language,
    project,
    user,
    hero,
    team,
    login,
    role,
    group,
    cache,
    weather,
    report,
    periodic_tasks,
    purchase,
    image,
    auth,
    artist,
    artist_goods,
    notify,
    chatting,
    payment,
    file
)

api_router = APIRouter()

api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(group.router, prefix="/group", tags=["group"])
api_router.include_router(project.router, prefix="/project", tags=["project"])
api_router.include_router(purchase.router, prefix="/purchase", tags=["purchase"])
api_router.include_router(image.router, prefix="/image", tags=["image"])

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(artist.router, prefix="/artist", tags=["artist"])

api_router.include_router(artist_goods.router, prefix="/artist/goods", tags=["artist_goods"])

api_router.include_router(notify.router, prefix="/notify", tags=["notify"])

api_router.include_router(chatting.router, prefix="/chatting", tags=["chatting"])

api_router.include_router(payment.router, prefix="/payment", tags=["payment"])
api_router.include_router(file.router, prefix="/file", tags=["file"])

# api_router.include_router(team.router, prefix="/team", tags=["team"])
# api_router.include_router(hero.router, prefix="/hero", tags=["hero"])
# api_router.include_router(cache.router, prefix="/cache", tags=["cache"])
# api_router.include_router(weather.router, prefix="/weather", tags=["weather"])
# api_router.include_router(report.router, prefix="/report", tags=["report"])
# api_router.include_router(
    # natural_language.router, prefix="/natural_language", tags=["natural_language"]
# )
# api_router.include_router(
    # periodic_tasks.router, prefix="/periodic_tasks", tags=["periodic_tasks"]
# )
