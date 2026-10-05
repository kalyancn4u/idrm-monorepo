"""Resources module ORM models — provider **organizations** and their **resources**.

Backs the ``/organizations`` and ``/resources`` API (roadmap §13.5; doc 50 §5.3–5.4). Doc 50 §2
groups these two tables together under "Providers", so they share one code module (the locked
10-module layout has no separate ``organizations`` module).

MVP relationship model: an :class:`Organization` has a single ``owner_user_id`` — the provider who
owns it *is* its only member. Multi-member organizations (a membership join table) are **→ FFP**;
until then "the provider's organization" means the org they own. The ``service_type`` enum is the
shared domain vocabulary defined once in the incidents module (``service_type_enum``) and reused
here so PostgreSQL creates the type exactly once.
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from geoalchemy2 import Geometry
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, SoftDelete, Timestamps, UUIDPrimaryKey
from app.modules.incidents.lifecycle import ServiceType
from app.modules.incidents.models import service_type_enum


class OrgType(str, enum.Enum):
    """The kinds of provider an organization can be (doc 50 §6)."""

    ngo = "ngo"
    government = "government"
    private = "private"
    hospital = "hospital"
    volunteer_group = "volunteer_group"


org_type_enum = SAEnum(OrgType, name="org_type")


class Organization(UUIDPrimaryKey, Timestamps, SoftDelete, Base):
    """A provider (NGO / hospital / volunteer group) that can claim incidents (doc 50 §5.3)."""

    __tablename__ = "organizations"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[OrgType] = mapped_column(org_type_enum, nullable=False)
    owner_user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    # Which service categories this provider covers — matched against an incident's service_type.
    service_categories: Mapped[list[ServiceType]] = mapped_column(
        ARRAY(service_type_enum), nullable=False, server_default="{}"
    )
    service_area_center: Mapped[object | None] = mapped_column(Geometry("POINT", srid=4326))
    service_radius_km: Mapped[float] = mapped_column(
        Numeric(8, 2), nullable=False, server_default="10.0"
    )
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    available_capacity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    verified_by: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id")
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rating: Mapped[float | None] = mapped_column(Numeric(3, 2))
    total_requests_completed: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    contact_phone: Mapped[str | None] = mapped_column(String(20))


class Resource(UUIDPrimaryKey, Timestamps, SoftDelete, Base):
    """A provider asset — ambulance, boat, beds… — placed on the map (doc 50 §5.4)."""

    __tablename__ = "resources"

    organization_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    kind: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    location: Mapped[object | None] = mapped_column(Geometry("POINT", srid=4326))
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
