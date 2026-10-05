"""Alerts module router — ``/alerts`` (coordinator area broadcasts; doc 40 §5.4).

Mounted at ``/api/v1/alerts`` by ``app.main``. Delivery is the in-app pull model: a user lists the
alerts active for their location (no message broker in the MVP, ADR-012).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db, require_role
from app.core.logging import client_ip_ctx
from app.core.rate_limit import rate_limit
from app.modules.alerts.repository import AlertRepository
from app.modules.alerts.schemas import AlertCreate, AlertResponse
from app.modules.alerts.service import AlertService, to_response
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]


def _service(db: DbSession) -> AlertService:
    return AlertService(AlertRepository(db))


@router.post(
    "",
    response_model=AlertResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_role("coordinator", "admin")),
        Depends(rate_limit("alert_create", limit=20)),
    ],
)
async def create_alert(data: AlertCreate, db: DbSession, claims: Claims) -> AlertResponse:
    """Broadcast an area alert (F8). Omit ``area`` for a platform-wide alert."""
    alert = await _service(db).create(data, uuid.UUID(claims["sub"]))
    await AuditService(AuditRepository(db)).record(
        "alert.created",
        actor_id=uuid.UUID(claims["sub"]),
        resource_type="alert",
        resource_id=alert.id,
        ip_address=client_ip_ctx.get(),
        new_values={"severity": alert.severity.value},
    )
    return to_response(alert)


@router.get("", dependencies=[Depends(rate_limit("alert_list", limit=100))])
async def list_alerts(
    db: DbSession,
    _: Claims,
    latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180),
) -> dict:
    """Active alerts; pass lat/lng to get only those covering your location (+ platform-wide)."""
    point = (latitude, longitude) if latitude is not None and longitude is not None else None
    alerts = await _service(db).list_active(point)
    return {"data": [to_response(a).model_dump(mode="json") for a in alerts]}
