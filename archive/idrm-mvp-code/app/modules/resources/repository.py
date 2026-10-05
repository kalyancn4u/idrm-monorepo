"""Resources module repository — data access for organizations and resources (roadmap §5.2).

Includes PostGIS proximity for "nearest capable, available provider" matching (PICS-RES-003).
"""

from __future__ import annotations

import uuid

from geoalchemy2 import Geography
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.incidents.lifecycle import ServiceType
from app.modules.resources.models import Organization, Resource


def to_point(latitude: float, longitude: float) -> WKTElement:
    """Build a PostGIS POINT (SRID 4326) from latitude/longitude."""
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


def from_point(geom: object | None) -> tuple[float, float] | None:
    """Return (latitude, longitude) from a stored PostGIS point, or None if unset."""
    if geom is None:
        return None
    shape = to_shape(geom)
    return shape.y, shape.x


class OrganizationRepository:
    """Async data access for provider organizations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, org: Organization) -> Organization:
        """Persist a new organization (flush) and return it."""
        self.session.add(org)
        await self.session.flush()
        return org

    async def get(self, org_id: uuid.UUID) -> Organization | None:
        """Fetch a non-deleted organization by id, or ``None`` if absent."""
        result = await self.session.execute(
            select(Organization).where(
                Organization.id == org_id, Organization.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def get_by_owner(self, owner_user_id: uuid.UUID) -> Organization | None:
        """The single organization owned by a provider (MVP: one org per provider)."""
        result = await self.session.execute(
            select(Organization).where(
                Organization.owner_user_id == owner_user_id, Organization.deleted_at.is_(None)
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        limit: int,
        offset: int,
        service_type: ServiceType | None = None,
        verified_only: bool = False,
        near: tuple[float, float] | None = None,
        radius_km: float | None = None,
    ) -> tuple[list[Organization], int]:
        """List organizations with optional type/verified filters and proximity ordering."""
        stmt = select(Organization).where(Organization.deleted_at.is_(None))
        if service_type is not None:
            stmt = stmt.where(Organization.service_categories.any(service_type))
        if verified_only:
            stmt = stmt.where(Organization.is_verified.is_(True))
        if near is not None:
            latitude, longitude = near
            point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
            distance = func.ST_Distance(
                func.cast(Organization.service_area_center, Geography), func.cast(point, Geography)
            )
            if radius_km is not None:
                stmt = stmt.where(
                    Organization.service_area_center.isnot(None),
                    func.ST_DWithin(
                        func.cast(Organization.service_area_center, Geography),
                        func.cast(point, Geography),
                        radius_km * 1000,
                    ),
                )
            order = distance.asc()
        else:
            order = Organization.created_at.desc()
        total = len((await self.session.execute(stmt)).scalars().all())
        paged = stmt.order_by(order).limit(limit).offset(offset)
        rows = (await self.session.execute(paged)).scalars().all()
        return list(rows), total


class ResourceRepository:
    """Async data access for provider resources (assets)."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, resource: Resource) -> Resource:
        """Persist a new resource/asset (flush) and return it."""
        self.session.add(resource)
        await self.session.flush()
        return resource

    async def get(self, resource_id: uuid.UUID) -> Resource | None:
        """Fetch a non-deleted resource by id, or ``None`` if absent."""
        result = await self.session.execute(
            select(Resource).where(Resource.id == resource_id, Resource.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        limit: int,
        offset: int,
        organization_id: uuid.UUID | None = None,
        available_only: bool = False,
    ) -> tuple[list[Resource], int]:
        """List resources (optionally by org / available-only), paginated + total count."""
        stmt = select(Resource).where(Resource.deleted_at.is_(None))
        if organization_id is not None:
            stmt = stmt.where(Resource.organization_id == organization_id)
        if available_only:
            stmt = stmt.where(Resource.is_available.is_(True))
        total = len((await self.session.execute(stmt)).scalars().all())
        paged = stmt.order_by(Resource.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(paged)).scalars().all()
        return list(rows), total
