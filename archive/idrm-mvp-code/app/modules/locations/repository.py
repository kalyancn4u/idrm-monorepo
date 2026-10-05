"""Locations module repository — PostGIS spatial reads across incidents and organizations.

The locations module owns **no table of its own** (doc 50); it reads the geometry already stored on
``incidents`` and ``organizations`` (roadmap §13.5). Proximity uses ``ST_DWithin`` on a geography
cast so the radius is true metres regardless of latitude.
"""

from __future__ import annotations

import uuid

from geoalchemy2 import Geography
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.lifecycle import IncidentStatus
from app.modules.incidents.models import Incident
from app.modules.resources.models import Organization

# Incident states that are still "on the map" as open work.
_OPEN_STATES = [IncidentStatus.created, IncidentStatus.approved, IncidentStatus.accepted,
                IncidentStatus.in_progress]


def _within(column: object, latitude: float, longitude: float, radius_km: float):
    """A ``ST_DWithin`` predicate (metres) against a stored geometry column."""
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    return func.ST_DWithin(
        func.cast(column, Geography), func.cast(point, Geography), radius_km * 1000
    )


class LocationRepository:
    """Async spatial reads used by the locations service."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def incidents_within(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[Incident]:
        """Open incidents within ``radius_km`` of a point (ST_DWithin, true metres)."""
        stmt = select(Incident).where(
            Incident.deleted_at.is_(None),
            Incident.status.in_(_OPEN_STATES),
            _within(Incident.location, latitude, longitude, radius_km),
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def organizations_within(
        self, latitude: float, longitude: float, radius_km: float
    ) -> list[Organization]:
        """Verified providers with a mapped service area within ``radius_km`` of a point."""
        stmt = select(Organization).where(
            Organization.deleted_at.is_(None),
            Organization.is_verified.is_(True),
            Organization.service_area_center.isnot(None),
            _within(Organization.service_area_center, latitude, longitude, radius_km),
        )
        return list((await self.session.execute(stmt)).scalars().all())

    async def open_incidents(self, requester_id: uuid.UUID | None = None) -> list[Incident]:
        """Open incidents for the map layer; scoped to one requester when given (citizen view)."""
        stmt = select(Incident).where(
            Incident.deleted_at.is_(None), Incident.status.in_(_OPEN_STATES)
        )
        if requester_id is not None:
            stmt = stmt.where(Incident.requester_id == requester_id)
        return list((await self.session.execute(stmt)).scalars().all())

    async def verified_organizations(self) -> list[Organization]:
        """Verified providers with a mapped service area, for the providers map layer."""
        stmt = select(Organization).where(
            Organization.deleted_at.is_(None),
            Organization.is_verified.is_(True),
            Organization.service_area_center.isnot(None),
        )
        return list((await self.session.execute(stmt)).scalars().all())
