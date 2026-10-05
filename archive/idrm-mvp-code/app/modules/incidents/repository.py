"""Incidents module repository — data access, including PostGIS proximity (roadmap §5.2, §3.3)."""

from __future__ import annotations

import uuid

from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.lifecycle import IncidentStatus, ServiceType
from app.modules.incidents.models import Incident, IncidentUpdate


def to_point(latitude: float, longitude: float) -> WKTElement:
    """Build a PostGIS POINT (SRID 4326) from latitude/longitude."""
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


def from_point(geom: object) -> tuple[float, float]:
    """Return (latitude, longitude) from a stored PostGIS point."""
    shape = to_shape(geom)
    return shape.y, shape.x


class IncidentRepository:
    """Async data access for incidents and their status timeline."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, incident: Incident) -> Incident:
        """Persist a new incident and flush so its generated id is available; return it."""
        self.session.add(incident)
        await self.session.flush()
        return incident

    async def add_update(self, update_row: IncidentUpdate) -> IncidentUpdate:
        """Persist one status-timeline row (flush) and return it."""
        self.session.add(update_row)
        await self.session.flush()
        return update_row

    async def get(self, incident_id: uuid.UUID) -> Incident | None:
        """Fetch a non-soft-deleted incident by id, or ``None`` if absent."""
        result = await self.session.execute(
            select(Incident).where(Incident.id == incident_id, Incident.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def updates_for(self, incident_id: uuid.UUID) -> list[IncidentUpdate]:
        """Return an incident's status-timeline rows, oldest first."""
        result = await self.session.execute(
            select(IncidentUpdate)
            .where(IncidentUpdate.incident_id == incident_id)
            .order_by(IncidentUpdate.created_at.asc())
        )
        return list(result.scalars().all())

    async def list(
        self,
        limit: int,
        offset: int,
        status: IncidentStatus | None = None,
        service_type: ServiceType | None = None,
        requester_id: uuid.UUID | None = None,
        assigned_organization_id: uuid.UUID | None = None,
    ) -> tuple[list[Incident], int]:
        """Return a filtered, paginated page of incidents plus the total match count.

        Filters (all optional) combine with AND; role scoping is applied by the caller
        (the service) via ``requester_id`` / ``assigned_organization_id``.
        """
        stmt = select(Incident).where(Incident.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(Incident.status == status)
        if service_type is not None:
            stmt = stmt.where(Incident.service_type == service_type)
        if requester_id is not None:
            stmt = stmt.where(Incident.requester_id == requester_id)
        if assigned_organization_id is not None:
            stmt = stmt.where(Incident.assigned_organization_id == assigned_organization_id)
        total = len((await self.session.execute(stmt)).scalars().all())
        paged = stmt.order_by(Incident.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(paged)).scalars().all()
        return list(rows), total

    async def nearby(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        service_type: ServiceType | None = None,
    ) -> list[Incident]:
        """Open, unassigned incidents within ``radius_km``, nearest first (PostGIS ST_DWithin)."""
        point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
        distance = func.ST_Distance(
            func.cast(Incident.location, Geography), func.cast(point, Geography)
        )
        stmt = (
            select(Incident)
            .where(
                Incident.deleted_at.is_(None),
                Incident.status.in_([IncidentStatus.created, IncidentStatus.approved]),
                func.ST_DWithin(
                    func.cast(Incident.location, Geography),
                    func.cast(point, Geography),
                    radius_km * 1000,
                ),
            )
            .order_by(distance.asc())
        )
        if service_type is not None:
            stmt = stmt.where(Incident.service_type == service_type)
        rows = (await self.session.execute(stmt)).scalars().all()
        return list(rows)
