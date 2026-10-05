"""
dbmodels/organization.py — the `organizations` table (NGOs, hospitals, agencies).
Mirrors 02-schema.sql §organizations.
"""
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from dbmodels.base import Base


class Organization(Base):
    """A provider org (NGO, hospital, agency, volunteer group) that fulfils requests.
    Only `is_verified` orgs appear in provider search and may accept work."""

    __tablename__ = "organizations"

    org_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    # Identity
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    org_type: Mapped[str] = mapped_column(String(50), nullable=False)  # see enums.OrgType
    registration_number: Mapped[str | None] = mapped_column(String(100), unique=True)

    # Which service types this org can deliver, e.g. ['MEDICAL', 'FOOD']
    service_types: Mapped[list[str]] = mapped_column(ARRAY(String(50)), nullable=False)

    # Capacity (available decreases on ACCEPT, increases on COMPLETE — via DB trigger)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    available_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))

    # Geographic coverage: {"type":"circle","center":[lon,lat],"radius_km":25}
    coverage_area: Mapped[dict] = mapped_column(JSONB, nullable=False)

    # Contact
    contact_person: Mapped[str | None] = mapped_column(String(255))
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=False)
    contact_email: Mapped[str | None] = mapped_column(String(255))

    # Verification (only verified orgs appear in provider search)
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL")
    )

    documents: Mapped[dict] = mapped_column(JSONB, server_default=text("'{}'::jsonb"))

    # Denormalised stats (kept fresh by DB triggers)
    total_services_completed: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    average_rating: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), server_default=text("0.00"))
    average_response_time_minutes: Mapped[int | None] = mapped_column(Integer, server_default=text("0"))

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Organization {self.name} ({self.org_type})>"
