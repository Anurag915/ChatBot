from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import get_settings
from app.db.mongodb import close_mongo_connection, connect_to_mongo
from app.routes.health import router as health_router
from app.routes.upload import router as upload_router
from app.routes.chat import router as chat_router
from app.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application-level resources such as database connections."""

    await connect_to_mongo()
    yield
    await close_mongo_connection()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(upload_router, prefix=settings.api_prefix)
    app.include_router(chat_router, prefix=settings.api_prefix)

    return app


app = create_app()
