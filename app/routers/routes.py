from fastapi import APIRouter, FastAPI

from .auths import router as auths_router_v1
from .tweets import router as tweets_router_v1
from .users import router as users_router_v1
from .chats import router as chats_router_v1


def include_router(app: FastAPI):
    api_router_v1 = APIRouter()
    api_router_v1.include_router(auths_router_v1)
    api_router_v1.include_router(chats_router_v1)
    api_router_v1.include_router(tweets_router_v1)
    api_router_v1.include_router(users_router_v1)
    app.include_router(api_router_v1, prefix=f"/api/v1")
