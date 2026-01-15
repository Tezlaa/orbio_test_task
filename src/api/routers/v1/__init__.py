from .common import common_router
from .reviews import reviews_router

from fastapi import APIRouter


api_router = APIRouter(prefix="/v1")

api_router.include_router(common_router)
api_router.include_router(reviews_router)


__all__ = [
    "api_router",
]
