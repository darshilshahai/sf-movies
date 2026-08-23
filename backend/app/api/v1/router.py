from fastapi import APIRouter
from app.api.v1 import health, movies, search

api_router = APIRouter()

api_router.include_router(
    health.router,
    prefix="/health",
    tags=["Health"],
)

api_router.include_router(
    movies.router,
    prefix="/movies",
    tags=["Movies"],
)

api_router.include_router(
    search.router,
    prefix="/search",
    tags=["Search"],
)
