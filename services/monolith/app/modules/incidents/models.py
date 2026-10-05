"""Incidents module ORM models — the core "help request" and its status timeline.

Backs the ``/incidents`` API (roadmap §13.4; doc 50 §5.5–5.6). Location is a PostGIS point
(SRID 4326). ``assigned_organization_id`` carries an FK to ``organizations`` (added with the
resources module in migration 0003).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, SmallInteger, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, SoftDelete, Timestamps, UUIDPrimaryKey
from app.modules.incidents.lifecycle import IncidentStatus, Priority, ServiceType

# Defined once and reused across columns/tables so the type is created only once.
service_type_enum = SAEnum(ServiceType, name="service_type")
priority_enum = SAEnum(Priority, name="priority")
incident_status_enum = SAEnum(IncidentStatus, name="incident_status")


class Incident(UUIDPrimaryKey, Timestamps, SoftDelete, Base):
    """A citizen's help request — the heart of IDRM (doc 50 §5.5)."""

    __tablename__ = "incidents"
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="ck_incidents_rating_range"),)

    service_type: Mapped[ServiceType] = mapped_column(service_type_enum, nullable=False, index=True)
    priority: Mapped[Priority] = mapped_column(priority_enum, nullable=False, index=True)
    status: Mapped[IncidentStatus] = mapped_column(
        incident_status_enum, default=IncidentStatus.created, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    location: Mapped[object] = mapped_column(Geometry("POINT", srid=4326), nullable=False)

    requester_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), index=True
    )  # NULL = guest / anonymous
    guest_contact: Mapped[str | None] = mapped_column(String(20))
    tracking_token: Mapped[str | None] = mapped_column(String(64), unique=True, index=True)

    assigned_organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("organizations.id"), index=True
    )  # the single-claim owner (resources module)
    approved_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id")
    )

    rating: Mapped[int | None] = mapped_column(SmallInteger)
    review: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)
    cancellation_reason: Mapped[str | None] = mapped_column(Text)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class IncidentUpdate(UUIDPrimaryKey, Base):
    """One status transition — the timeline feeding ``GET /incidents/{id}/updates``."""

    __tablename__ = "incident_updates"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True
    )
    from_status: Mapped[IncidentStatus | None] = mapped_column(incident_status_enum)
    to_status: Mapped[IncidentStatus] = mapped_column(incident_status_enum, nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), ForeignKey("users.id"))
    note: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
