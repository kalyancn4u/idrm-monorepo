"""
main.py — IDRM backend entry point (FastAPI modular monolith).

RUN IT (from this folder, with the conda env active):
    conda activate idrm-mvp
    uvicorn main:app --reload --port 8000

THEN OPEN:
    http://localhost:8000/docs            → interactive API docs (Swagger UI)
    http://localhost:8000/api/v1/health   → should return {"status": "ok", ...}

Built in **Module M0** (boot + CORS + health checks) and extended through **M2–M6**:
auth (`/auth`, `/users`), services (`/services` + action sub-endpoints), geo
(`/geo`), notifications (`/notifications`) and analytics (`/analytics`). All backend
feature routers are now mounted — see the block at the bottom.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from api.v1 import analytics, auth, geo, notifications, services, users
from core.config import settings
from core.database import engine

# Create the application. Title/version show up in the Swagger UI at /docs.
app = FastAPI(
    title=settings.APP_NAME,
    version="3.0",
    description="Integrated Disaster Response Management — backend API (modular monolith).",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- CORS --------------------------------------------------------------------
# Browsers block cross-origin calls unless the server opts in. Our frontends run
# on different ports (5173 HTML, 5174 React) so we must allow them explicitly.
# IDRM uses only GET and POST, so we don't allow PUT/PATCH/DELETE.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# --- Health checks -----------------------------------------------------------
@app.get(f"{settings.API_V1_PREFIX}/health", tags=["health"])
async def health() -> dict:
    """Liveness: is the API process running? (Used by load balancers & uptime checks.)"""
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get(f"{settings.API_V1_PREFIX}/health/ready", tags=["health"])
async def readiness() -> dict:
    """Readiness: can we actually reach the database right now?"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        database_up = True
    except Exception:
        database_up = False
    return {
        "status": "ok" if database_up else "degraded",
        "database": "up" if database_up else "down",
    }


# --- Feature routers (mounted as each module is built) -----------------------
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)      # M2
app.include_router(users.router, prefix=settings.API_V1_PREFIX)     # M2
app.include_router(services.router, prefix=settings.API_V1_PREFIX)  # M3
app.include_router(geo.router, prefix=settings.API_V1_PREFIX)       # M4
app.include_router(notifications.router, prefix=settings.API_V1_PREFIX)  # M5
app.include_router(analytics.router, prefix=settings.API_V1_PREFIX)      # M6

# All backend feature modules (M2–M6) are mounted. Next: the API Gateway (G1–G4)
# proxies these at :3000, and the frontends (F0–F6) consume them.
