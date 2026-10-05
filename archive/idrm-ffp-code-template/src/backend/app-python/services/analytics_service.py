"""
services/analytics_service.py — dashboard analytics (Module M6).

Computes the aggregate operational metrics for GET /analytics/dashboard (mirrors
CLAUDE.md §Analytics). The result is cached in Redis for 5 minutes — these counts
are read often and change slowly, so we avoid re-aggregating on every request.
The cache is best-effort: a miss or a Redis outage simply recomputes from Postgres.
"""
from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import cache_get_json, cache_set_json
from dbmodels.enums import ServiceStatus, ServiceType
from dbmodels.service_request import ServiceRequest
from schemas.analytics import DashboardData, DashboardResponse

_CACHE_KEY = "analytics:dashboard"
_CACHE_TTL_SECONDS = 300  # 5 minutes, per the M6 spec

# Which statuses count as "live" vs "successfully finished".
_ACTIVE_STATUSES = {"SUBMITTED", "APPROVED", "ACCEPTED", "IN_PROGRESS"}
_COMPLETED_STATUSES = {"COMPLETED", "VERIFIED"}


async def get_dashboard(db: AsyncSession) -> DashboardResponse:
    """Return the dashboard metrics, served from the 5-minute Redis cache when warm
    and recomputed (then re-cached) on a miss."""
    cached = await cache_get_json(_CACHE_KEY)
    if cached is not None:
        return DashboardResponse(data=DashboardData(**cached))

    data = await _compute_dashboard(db)
    await cache_set_json(_CACHE_KEY, data.model_dump(), _CACHE_TTL_SECONDS)
    return DashboardResponse(data=data)


async def _compute_dashboard(db: AsyncSession) -> DashboardData:
    """Run the aggregate queries that build the dashboard numbers."""
    # One grouped count per dimension (status, service_type).
    status_rows = await db.execute(
        select(ServiceRequest.status, func.count()).group_by(ServiceRequest.status)
    )
    status_counts = {row[0]: row[1] for row in status_rows.all()}

    type_rows = await db.execute(
        select(ServiceRequest.service_type, func.count()).group_by(ServiceRequest.service_type)
    )
    type_counts = {row[0]: row[1] for row in type_rows.all()}

    # Seed every enum key at 0 so the response shape is stable and complete
    # (all 10 statuses, all 6 service types) regardless of what's in the table.
    by_status = {s.value: status_counts.get(s.value, 0) for s in ServiceStatus}
    by_service_type = {t.value: type_counts.get(t.value, 0) for t in ServiceType}

    total_requests = sum(by_status.values())
    active_requests = sum(by_status[s] for s in _ACTIVE_STATUSES)
    completed = sum(by_status[s] for s in _COMPLETED_STATUSES)
    completion_rate = round(completed / total_requests, 2) if total_requests else 0.0

    # Average response time = minutes from created_at to accepted_at (how long until
    # a provider picked the request up), over requests that were actually accepted.
    avg_seconds = await db.scalar(
        select(
            func.avg(extract("epoch", ServiceRequest.accepted_at - ServiceRequest.created_at))
        ).where(ServiceRequest.accepted_at.is_not(None))
    )
    avg_response_time_min = round(float(avg_seconds) / 60.0, 1) if avg_seconds is not None else 0.0

    return DashboardData(
        total_requests=total_requests,
        active_requests=active_requests,
        avg_response_time_min=avg_response_time_min,
        completion_rate=completion_rate,
        by_service_type=by_service_type,
        by_status=by_status,
    )
