from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .controllers.rest.exceptions import register_exception_handlers
from .controllers.rest.grocery_routes import router as groceries_router
from .controllers.rest.middlewares import add_middleware
from .controllers.rest.recipe_routes import router as recipes_router
from .infra.db import close_db
from .settings import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await close_db()


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    add_middleware(app)
    register_exception_handlers(app)
    app.include_router(recipes_router, prefix="/api/v1", tags=["recipes"])
    app.include_router(groceries_router, prefix="/api/v1", tags=["groceries"])

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
