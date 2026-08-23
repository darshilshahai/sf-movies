import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    unhandled_exception_handler,
)
from app.core.logging import setup_logging
from app.middleware.request_logging import RequestLoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger = logging.getLogger("sf_movies")
    settings = get_settings()
    logger.info(f"starting_{settings.app_name} environment={settings.app_env}")
    yield
    logger.info(f"stopping_{settings.app_name}")


def create_application() -> FastAPI:
    settings = get_settings()

    docs_url = "/docs" if (settings.enable_docs or settings.is_development) else None
    redoc_url = "/redoc" if (settings.enable_docs or settings.is_development) else None
    openapi_url = (
        f"{settings.api_prefix}/openapi.json"
        if (settings.enable_docs or settings.is_development)
        else None
    )

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        docs_url=docs_url,
        redoc_url=redoc_url,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )


    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    app.add_middleware(RequestLoggingMiddleware)


    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)


    app.include_router(api_router, prefix=settings.api_prefix)

    return app


app = create_application()
