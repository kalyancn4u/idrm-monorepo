"""Alerts module ORM model — coordinator area broadcasts (roadmap §13.5; doc 50 §5.7).

An alert's ``area`` is a PostGIS ``MultiPolygon`` (SRID 4326); **NULL means platform-wide**. Users
"receive" an alert by pulling ``GET /alerts`` for their location — there is no message broker in the
MVP (ADR-012), so delivery is the in-app pull model (PICS-ALR-002).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, UUIDPrimaryKey


class AlertSeverity(str, enum.Enum):
    info = "info"
    warning = "warning"
    critical = "critical"


alert_severity_enum = SAEnum(AlertSeverity, name="alert_severity")


class Alert(UUIDPrimaryKey, Base):
    """A coordinator's area-scoped broadcast (doc 50 §5.7)."""

    __tablename__ = "alerts"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(alert_severity_enum, nullable=False)
    area: Mapped[object | None] = mapped_column(Geometry("MULTIPOLYGON", srid=4326))
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_by: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
