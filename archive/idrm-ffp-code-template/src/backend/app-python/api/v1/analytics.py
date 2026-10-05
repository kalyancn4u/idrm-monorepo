"""
api/v1/analytics.py — analytics routes (Module M6): GET /analytics/dashboard.

Aggregate operational metrics for coordinator/admin dashboards. Requires
authentication (the numbers are operational, though aggregate and non-identifying).
Thin handler delegates to `services.analytics_service`. Mounted under `/api/v1`.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from dbmodels.user import User
from schemas.analytics import DashboardResponse
from services import analytics_service

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DashboardResponse:
    """Aggregate dashboard metrics — totals, active count, completion rate, average
    response time, and breakdowns by service type and status. Served from a
    5-minute Redis cache when warm."""
    return await analytics_service.get_dashboard(db)
