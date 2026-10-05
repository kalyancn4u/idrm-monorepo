"""
dbmodels/service_request.py — the `service_requests` table (the core entity).
Mirrors 02-schema.sql §service_requests.

`location` is a PostGIS Point (lon, lat) in WGS-84 (SRID 4326). GeoAlchemy2
returns it as a WKBElement; in queries we convert with ST_AsGeoJSON / ST_X / ST_Y.
"""
import uuid
from datetime import datetime

from geoalchemy2 import Geometry, WKBElement
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from dbmodels.base import Base


class ServiceRequest(Base):
    """The core entity: one citizen's request for help, tracked through its lifecycle
    (see enums.ServiceStatus) from SUBMITTED to VERIFIED. Carries a PostGIS location."""

    __tablename__ = "service_requests"

    service_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Relationships
    requestor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    provider_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.org_id", ondelete="SET NULL", onupdate="CASCADE"),
    )

    # Classification (see enums.ServiceType / Priority / ServiceStatus)
    service_type: Mapped[str] = mapped_column(String(50), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, server_default="SUBMITTED")

    # Where + what
    location: Mapped[WKBElement] = mapped_column(
        Geometry(geometry_type="POINT", srid=4326), nullable=False
    )
    address: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text, nullable=False)  # 10–500 chars (DB CHECK)
    num_people_affected: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))

    # Privacy (default PROTECTED; can only be raised)
    privacy_level: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PROTECTED")
    contact_phone: Mapped[str | None] = mapped_column(String(20))

    # Timeline
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    # Feedback + stage notes
    rating: Mapped[int | None] = mapped_column(Integer)  # 1–5, only once VERIFIED
    feedback: Mapped[str | None] = mapped_column(Text)
    acceptance_notes: Mapped[str | None] = mapped_column(Text)
    completion_notes: Mapped[str | None] = mapped_column(Text)
    rejection_reason: Mapped[str | None] = mapped_column(Text)

    def __repr__(self) -> str:
        return f"<ServiceRequest {self.service_id} {self.service_type}/{self.priority} [{self.status}]>"
