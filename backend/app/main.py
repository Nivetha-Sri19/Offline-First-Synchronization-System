from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.deps import initialize_dependencies
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import configure_logging
from app.database.redis import RedisManager
from app.database.session import DatabaseSessionManager
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging(settings.log_level)

    app.state.db = DatabaseSessionManager(
        settings.database_url,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
        echo=settings.debug,
    )

    app.state.redis = RedisManager(
        settings.redis_url,
        max_connections=settings.redis_max_connections,
    )

    initialize_dependencies(
        app.state.db,
        app.state.redis,
    )

    yield

    app.state.redis.close()
    app.state.db.dispose()


def create_application() -> FastAPI:
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Enterprise Offline-First Data Synchronization System "
            "with conflict resolution, idempotent synchronization, "
            "audit logging, and synchronization history."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    cors_origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(RequestLoggingMiddleware)

    register_exception_handlers(application)

    application.include_router(
        api_router,
        prefix=settings.api_v1_prefix,
    )

    return application


app = create_application()