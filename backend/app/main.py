"""
FastAPI application entry point.
Registers routers, middleware, lifespan events.
"""

from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db

from app.auth.router import router as auth_router
from app.accounts.router import router as accounts_router
from app.inbox.router import router as inbox_router
from app.meetings.router import router as meetings_router
from app.drafts.router import router as drafts_router
from app.scheduling.router import router as scheduling_router
from app.approvals.router import router as approvals_router
from app.execution.router import router as execution_router
from app.audit.router import router as audit_router
from app.notifications.router import router as notifications_router
from app.ai.router import router as ai_router
from app.common.middleware import RequestTracingMiddleware

logger = structlog.get_logger()
settings = get_settings()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Startup / shutdown lifecycle."""
    logger.info("app.starting", version=settings.app_version)
    if settings.debug:
        await init_db()
    yield
    logger.info("app.shutdown")


def create_app() -> FastAPI:
    """Application factory."""
    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # ── CORS ─────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Custom middleware ────────────────────────────
    application.add_middleware(RequestTracingMiddleware)

    # ── Routers ──────────────────────────────────────
    prefix = settings.api_prefix
    application.include_router(auth_router, prefix=f"{prefix}/auth", tags=["auth"])
    application.include_router(accounts_router, prefix=f"{prefix}/accounts", tags=["accounts"])
    application.include_router(inbox_router, prefix=f"{prefix}/inbox", tags=["inbox"])
    application.include_router(meetings_router, prefix=f"{prefix}/meetings", tags=["meetings"])
    application.include_router(drafts_router, prefix=f"{prefix}/drafts", tags=["drafts"])
    application.include_router(scheduling_router, prefix=f"{prefix}/scheduling", tags=["scheduling"])
    application.include_router(approvals_router, prefix=f"{prefix}/approvals", tags=["approvals"])
    application.include_router(execution_router, prefix=f"{prefix}/execution", tags=["execution"])
    application.include_router(audit_router, prefix=f"{prefix}/audit", tags=["audit"])
    application.include_router(notifications_router, prefix=f"{prefix}/notifications", tags=["notifications"])
    application.include_router(ai_router, prefix=f"{prefix}/ai", tags=["ai"])

    @application.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app_version}

    return application


app = create_app()
