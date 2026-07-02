import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(settings.LOG_LEVEL)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    yield
    
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


def create_app() -> FastAPI:
    settings = get_settings()
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        lifespan=lifespan
    )
    
    app.include_router(api_router, prefix=settings.API_PREFIX)
    
    return app