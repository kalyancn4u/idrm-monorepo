"""Reports module router — ``/reports`` operational metrics + CSV export (doc 40 §5.4).

Mounted at ``/api/v1/reports`` by ``app.main``. All endpoints are coordinator/admin-only (F8/F10).
The ``{name}/export`` route is declared last so it does not shadow the named report routes.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_role
from app.core.exceptions import AppError
from app.core.rate_limit import rate_limit
from app.modules.reports.repository import ReportRepository
from app.modules.reports.service import ReportService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
StaffOnly = Depends(require_role("coordinator", "admin"))


def _service(db: DbSession) -> ReportService:
    return ReportService(ReportRepository(db))


@router.get("/dashboard", dependencies=[StaffOnly, Depends(rate_limit("report_read", limit=50))])
async def dashboard(db: DbSession) -> dict:
    """Live overview metrics — incidents by status/type/priority/area + org counts (AC-8.1)."""
    return await _service(db).dashboard()


@router.get("/response-times",
            dependencies=[StaffOnly, Depends(rate_limit("report_read", limit=50))])
async def response_times(db: DbSession) -> dict:
    """Average/median time-to-accept and time-to-resolve (AC-10.1)."""
    return await _service(db).response_times()


@router.get("/fulfillment",
            dependencies=[StaffOnly, Depends(rate_limit("report_read", limit=50))])
async def fulfillment(db: DbSession) -> dict:
    """Resolution + verification rates, cross-checked against the audit trail (AC-10.1)."""
    return await _service(db).fulfillment()


@router.get("/{name}/export",
            dependencies=[StaffOnly, Depends(rate_limit("report_export", limit=20))])
async def export(name: str, db: DbSession, format: str = Query("csv")) -> Response:
    """Export a report as a file. Only ``format=csv`` is supported in the MVP (AC-10.2)."""
    if format != "csv":
        raise AppError(422, "unsupported_format", "Only 'csv' export is supported.")
    body = await _service(db).export_csv(name)
    return Response(
        content=body,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{name}.csv"'},
    )
