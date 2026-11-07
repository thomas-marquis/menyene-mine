from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.router import api_router
from .config import get_settings
from .db import close_db
from .exceptions import register_exception_handlers
from .middleware import add_middleware

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    add_middleware(app)
    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
