"""Resources module service — register/verify organizations and manage resources (roadmap §13.5).

Business rules enforced here:
- a provider owns **at most one** organization (MVP); a second ``POST /organizations`` → 409;
- only a **verified** organization may claim incidents (doc 40 §5.3, F8/AC-8.4) — used by the
  incidents module via :meth:`OrganizationService.resolve_active_for_owner`;
- only the owning provider (or a coordinator) may modify an organization or its resources (RBAC).
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.core.exceptions import AppError
from app.modules.incidents.lifecycle import ServiceType
from app.modules.resources.models import Organization, Resource
from app.modules.resources.repository import (
    OrganizationRepository,
    ResourceRepository,
    from_point,
    to_point,
)
from app.modules.resources.schemas import (
    CapacityRequest,
    GeoPoint,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
    ResourceCreate,
    ResourceResponse,
    ResourceUpdate,
)

logger = logging.getLogger("idrm.resources")


def _now() -> datetime:
    return datetime.now(UTC)


def org_to_response(org: Organization) -> OrganizationResponse:
    """Map an ORM organization to its API shape (PostGIS point → lat/lng)."""
    center = from_point(org.service_area_center)
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        type=org.type,
        owner_user_id=org.owner_user_id,
        service_categories=list(org.service_categories),
        service_area_center=GeoPoint(latitude=center[0], longitude=center[1]) if center else None,
        service_radius_km=float(org.service_radius_km),
        capacity=org.capacity,
        available_capacity=org.available_capacity,
        is_available=org.is_available,
        is_verified=org.is_verified,
        rating=float(org.rating) if org.rating is not None else None,
        total_requests_completed=org.total_requests_completed,
        contact_phone=org.contact_phone,
        created_at=org.created_at,
        updated_at=org.updated_at,
    )


def resource_to_response(resource: Resource) -> ResourceResponse:
    """Map an ORM resource to its API shape (PostGIS point → lat/lng if set)."""
    loc = from_point(resource.location)
    return ResourceResponse(
        id=resource.id,
        organization_id=resource.organization_id,
        name=resource.name,
        kind=resource.kind,
        quantity=resource.quantity,
        location=GeoPoint(latitude=loc[0], longitude=loc[1]) if loc else None,
        is_available=resource.is_available,
        created_at=resource.created_at,
        updated_at=resource.updated_at,
    )


class OrganizationService:
    """Register, verify, and update provider organizations."""

    def __init__(self, repo: OrganizationRepository) -> None:
        self.repo = repo

    async def create(self, data: OrganizationCreate, owner_user_id: uuid.UUID) -> Organization:
        """Register a provider's organization (pending verification). One org per provider."""
        if await self.repo.get_by_owner(owner_user_id) is not None:
            raise AppError(409, "already_exists", "You already have a registered organization.")
        org = Organization(
            name=data.name,
            type=data.type,
            owner_user_id=owner_user_id,
            service_categories=list(data.service_categories),
            service_area_center=(
                to_point(data.service_area_center.latitude, data.service_area_center.longitude)
                if data.service_area_center
                else None
            ),
            service_radius_km=data.service_radius_km,
            capacity=data.capacity,
            available_capacity=data.capacity,
            contact_phone=data.contact_phone,
        )
        await self.repo.add(org)
        logger.info("organization.create", extra={"extra_fields": {"organization_id": str(org.id)}})
        return org

    async def get(self, org_id: uuid.UUID) -> Organization:
        """Return the organization by id, or raise 404 ``not_found``."""
        org = await self.repo.get(org_id)
        if org is None:
            raise AppError(404, "not_found", "Organization not found.")
        return org

    async def get_mine(self, owner_user_id: uuid.UUID) -> Organization:
        """Return the caller's own organization, or 404 if they have not registered one."""
        org = await self.repo.get_by_owner(owner_user_id)
        if org is None:
            raise AppError(404, "not_found", "You have not registered an organization yet.")
        return org

    async def resolve_active_for_owner(self, owner_user_id: uuid.UUID) -> Organization:
        """Return the provider's org, requiring it to be verified (used before claiming).

        Raises 403 ``org_not_verified`` if the provider has no org or it is not yet verified —
        the gate that stops an unverified provider from accepting incidents (AC-8.4).
        """
        org = await self.repo.get_by_owner(owner_user_id)
        if org is None:
            raise AppError(
                403, "org_required", "Register an organization before claiming requests."
            )
        if not org.is_verified:
            raise AppError(
                403,
                "org_not_verified",
                "Your organization must be verified before claiming requests.",
            )
        return org

    async def list(
        self,
        page: int,
        limit: int,
        service_type: ServiceType | None = None,
        verified_only: bool = False,
        near: tuple[float, float] | None = None,
        radius_km: float | None = None,
    ) -> tuple[list[Organization], int]:
        """List providers with optional service-type / verified / proximity filters, paginated."""
        return await self.repo.list(
            limit=limit,
            offset=(page - 1) * limit,
            service_type=service_type,
            verified_only=verified_only,
            near=near,
            radius_km=radius_km,
        )

    async def update(
        self, org: Organization, actor_id: uuid.UUID, role: str, data: OrganizationUpdate
    ) -> Organization:
        """Owner or coordinator may edit an org's details (RBAC)."""
        self._require_owner_or_coordinator(org, actor_id, role)
        if data.name is not None:
            org.name = data.name
        if data.type is not None:
            org.type = data.type
        if data.service_categories is not None:
            org.service_categories = list(data.service_categories)
        if data.service_area_center is not None:
            org.service_area_center = to_point(
                data.service_area_center.latitude, data.service_area_center.longitude
            )
        if data.service_radius_km is not None:
            org.service_radius_km = data.service_radius_km
        if data.contact_phone is not None:
            org.contact_phone = data.contact_phone
        return org

    async def verify(self, org: Organization, coordinator_id: uuid.UUID) -> Organization:
        """Coordinator/admin approves an org — this is what enables it to claim (AC-8.4)."""
        org.is_verified = True
        org.verified_by = coordinator_id
        org.verified_at = _now()
        logger.info(
            "organization.verify", extra={"extra_fields": {"organization_id": str(org.id)}}
        )
        return org

    async def set_capacity(
        self, org: Organization, actor_id: uuid.UUID, data: CapacityRequest
    ) -> Organization:
        """Owner sets total capacity (and optional available capacity) for their org."""
        self._require_owner(org, actor_id)
        org.capacity = data.capacity
        org.available_capacity = (
            data.available_capacity if data.available_capacity is not None else data.capacity
        )
        return org

    async def set_availability(
        self, org: Organization, actor_id: uuid.UUID, is_available: bool
    ) -> Organization:
        """Owner toggles whether their org is currently accepting work."""
        self._require_owner(org, actor_id)
        org.is_available = is_available
        return org

    @staticmethod
    def _require_owner(org: Organization, actor_id: uuid.UUID) -> None:
        """Raise 403 unless ``actor_id`` owns the organization."""
        if org.owner_user_id != actor_id:
            raise AppError(403, "forbidden", "You can only manage your own organization.")

    @staticmethod
    def _require_owner_or_coordinator(org: Organization, actor_id: uuid.UUID, role: str) -> None:
        """Raise 403 unless the actor owns the org or is a coordinator/admin."""
        if role in {"coordinator", "admin"}:
            return
        if org.owner_user_id != actor_id:
            raise AppError(403, "forbidden", "You can only manage your own organization.")


class ResourceService:
    """Manage provider resources (assets on the map)."""

    def __init__(self, repo: ResourceRepository, org_repo: OrganizationRepository) -> None:
        self.repo = repo
        self.org_repo = org_repo

    async def create(self, data: ResourceCreate, owner_user_id: uuid.UUID) -> Resource:
        """Declare an asset for the provider's own organization."""
        org = await self.org_repo.get_by_owner(owner_user_id)
        if org is None:
            raise AppError(403, "org_required", "Register an organization before adding resources.")
        resource = Resource(
            organization_id=org.id,
            name=data.name,
            kind=data.kind,
            quantity=data.quantity,
            location=(
                to_point(data.location.latitude, data.location.longitude) if data.location else None
            ),
            is_available=data.is_available,
        )
        await self.repo.add(resource)
        return resource

    async def get(self, resource_id: uuid.UUID) -> Resource:
        """Return the resource by id, or raise 404 ``not_found``."""
        resource = await self.repo.get(resource_id)
        if resource is None:
            raise AppError(404, "not_found", "Resource not found.")
        return resource

    async def update(
        self, resource_id: uuid.UUID, owner_user_id: uuid.UUID, data: ResourceUpdate
    ) -> Resource:
        """Edit an asset — only the owning provider may (RBAC)."""
        resource = await self.get(resource_id)
        org = await self.org_repo.get(resource.organization_id)
        if org is None or org.owner_user_id != owner_user_id:
            raise AppError(403, "forbidden", "You can only modify your own resources.")
        if data.name is not None:
            resource.name = data.name
        if data.kind is not None:
            resource.kind = data.kind
        if data.quantity is not None:
            resource.quantity = data.quantity
        if data.location is not None:
            resource.location = to_point(data.location.latitude, data.location.longitude)
        if data.is_available is not None:
            resource.is_available = data.is_available
        return resource

    async def list(
        self,
        role: str,
        owner_user_id: uuid.UUID,
        page: int,
        limit: int,
    ) -> tuple[list[Resource], int]:
        """Providers see their own assets; coordinators/admins see all (role-scoped)."""
        organization_id: uuid.UUID | None = None
        if role == "provider":
            org = await self.org_repo.get_by_owner(owner_user_id)
            if org is None:
                return [], 0
            organization_id = org.id
        return await self.repo.list(
            limit=limit, offset=(page - 1) * limit, organization_id=organization_id
        )
