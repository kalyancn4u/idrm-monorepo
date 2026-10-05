"""Alerts module service — issue and pull coordinator area broadcasts (roadmap §13.5)."""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.modules.alerts.models import Alert
from app.modules.alerts.repository import AlertRepository, to_multipolygon
from app.modules.alerts.schemas import AlertCreate, AlertResponse

logger = logging.getLogger("idrm.alerts")


def to_response(alert: Alert) -> AlertResponse:
    """Map an ORM alert to its API shape (``platform_wide`` = it has no bounded area)."""
    return AlertResponse(
        id=alert.id,
        title=alert.title,
        message=alert.message,
        severity=alert.severity,
        active=alert.active,
        platform_wide=alert.area is None,
        created_by=alert.created_by,
        expires_at=alert.expires_at,
        created_at=alert.created_at,
    )


class AlertService:
    """Create alerts and list the ones active for a user's location."""

    def __init__(self, repo: AlertRepository) -> None:
        self.repo = repo

    async def create(self, data: AlertCreate, coordinator_id: uuid.UUID) -> Alert:
        """Broadcast an alert; a polygon ring bounds its area, or none = platform-wide."""
        alert = Alert(
            title=data.title,
            message=data.message,
            severity=data.severity,
            area=to_multipolygon(data.area) if data.area else None,
            created_by=coordinator_id,
            expires_at=data.expires_at,
        )
        await self.repo.add(alert)
        logger.info(
            "alert.create",
            extra={"extra_fields": {"alert_id": str(alert.id), "severity": data.severity.value}},
        )
        return alert

    async def list_active(self, point: tuple[float, float] | None) -> list[Alert]:
        """Active, non-expired alerts (area-filtered to ``point`` when given)."""
        return await self.repo.list_active(datetime.now(UTC), point)
