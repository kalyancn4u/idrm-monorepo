"""IDRM MVP application entry point — assembles the FastAPI app and wires every module.

Sets up structured logging, the request-id correlation middleware, the single error envelope,
CORS, the health probe, and mounts each module's router under ``/api/v1`` (roadmap §5, §7).
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import client_ip_ctx, configure_logging, request_id_ctx
from app.modules.administration.router import router as administration_router
from app.modules.alerts.router import router as alerts_router
from app.modules.audit.router import router as audit_router
from app.modules.files.router import router as files_router
from app.modules.incidents.router import router as incidents_router
from app.modules.locations.router import router as locations_router
from app.modules.notifications.router import router as notifications_router
from app.modules.reports.router import router as reports_router
from app.modules.resources.org_router import router as organizations_router
from app.modules.resources.router import router as resources_router
from app.modules.users.router import router as users_router

settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger("idrm.app")

app = FastAPI(title="IDRM MVP API", version="0.1.0", docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)


@app.middleware("http")
async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
    """Stamp each request with an ``X-Request-Id``, log start/end, echo the id back."""
    rid = request.headers.get("X-Request-Id") or f"req_{uuid.uuid4().hex[:12]}"
    request_id_ctx.set(rid)
    client_ip_ctx.set(request.client.host if request.client else None)
    started = time.perf_counter()
    logger.info(
        "request.start",
        extra={"extra_fields": {"method": request.method, "path": request.url.path}},
    )
    response: Response = await call_next(request)
    latency_ms = round((time.perf_counter() - started) * 1000, 1)
    logger.info(
        "request.end",
        extra={"extra_fields": {"status": response.status_code, "latency_ms": latency_ms}},
    )
    response.headers["X-Request-Id"] = rid
    return response


@app.get("/api/v1/health", tags=["system"])
async def health() -> dict[str, str]:
    """Liveness/readiness probe (roadmap §4.3)."""
    return {"status": "ok"}


# Mount each module's router (scaffold: routers are empty until their build increment, roadmap §13).
app.include_router(users_router, prefix="/api/v1", tags=["users"])
app.include_router(incidents_router, prefix="/api/v1/incidents", tags=["incidents"])
app.include_router(organizations_router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(resources_router, prefix="/api/v1/resources", tags=["resources"])
app.include_router(locations_router, prefix="/api/v1/locations", tags=["locations"])
app.include_router(alerts_router, prefix="/api/v1/alerts", tags=["alerts"])
app.include_router(notifications_router, prefix="/api/v1/notifications", tags=["notifications"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["reports"])
app.include_router(files_router, prefix="/api/v1/files", tags=["files"])
app.include_router(audit_router, prefix="/api/v1/audit-logs", tags=["audit"])
app.include_router(administration_router, prefix="/api/v1", tags=["administration"])
