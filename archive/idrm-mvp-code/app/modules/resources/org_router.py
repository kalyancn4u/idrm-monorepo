"""Organizations router — ``/organizations`` (provider registration + verification; doc 40 §5.3).

Mounted at ``/api/v1/organizations`` by ``app.main``. Static sub-paths (``/mine``) are declared
before ``/{organization_id}`` so they match correctly. Lives in the resources module because doc 50
groups organizations and resources together as the "Providers" data.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db, require_role
from app.core.logging import client_ip_ctx
from app.core.rate_limit import rate_limit
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.modules.incidents.lifecycle import ServiceType
from app.modules.resources.repository import OrganizationRepository
from app.modules.resources.schemas import (
    AvailabilityRequest,
    CapacityRequest,
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.modules.resources.service import OrganizationService, org_to_response

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]
ProviderClaims = Annotated[dict, Depends(require_role("provider"))]


def _service(db: DbSession) -> OrganizationService:
    return OrganizationService(OrganizationRepository(db))


def _actor(claims: dict) -> tuple[uuid.UUID, str]:
    return uuid.UUID(claims["sub"]), claims["role"]


@router.post(
    "",
    response_model=OrganizationResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(require_role("provider")),
        Depends(rate_limit("org_create", limit=5)),
    ],
)
async def create_organization(
    data: OrganizationCreate, db: DbSession, claims: Claims
) -> OrganizationResponse:
    """Register a provider organization (pending verification)."""
    org = await _service(db).create(data, uuid.UUID(claims["sub"]))
    return org_to_response(org)


@router.get("", dependencies=[Depends(require_role("coordinator", "provider", "admin"))])
async def list_organizations(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    service_type: ServiceType | None = None,
    verified_only: bool = False,
    latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180),
    radius_km: float | None = Query(None, gt=0, le=500),
) -> dict:
    """List providers with optional service-type / verified / proximity filters (F3)."""
    near = (latitude, longitude) if latitude is not None and longitude is not None else None
    orgs, total = await _service(db).list(
        page=page,
        limit=limit,
        service_type=service_type,
        verified_only=verified_only,
        near=near,
        radius_km=radius_km,
    )
    return {
        "data": [org_to_response(o).model_dump(mode="json") for o in orgs],
        "pagination": {"page": page, "limit": limit, "total": total,
                       "total_pages": (total + limit - 1) // limit},
    }


@router.get("/mine", response_model=OrganizationResponse)
async def my_organization(db: DbSession, claims: ProviderClaims):
    """The authenticated provider's own organization."""
    org = await _service(db).get_mine(uuid.UUID(claims["sub"]))
    return org_to_response(org)


@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(organization_id: uuid.UUID, db: DbSession, _: Claims):
    """An organization's public profile (any authenticated role)."""
    org = await _service(db).get(organization_id)
    return org_to_response(org)


@router.patch(
    "/{organization_id}",
    response_model=OrganizationResponse,
    dependencies=[Depends(rate_limit("org_write", limit=20))],
)
async def update_organization(
    organization_id: uuid.UUID, data: OrganizationUpdate, db: DbSession, claims: Claims
):
    """Owner (provider) or a coordinator updates an org's details."""
    actor_id, role = _actor(claims)
    svc = _service(db)
    org = await svc.get(organization_id)
    updated = await svc.update(org, actor_id, role, data)
    return org_to_response(updated)


@router.post(
    "/{organization_id}/verify",
    response_model=OrganizationResponse,
    dependencies=[
        Depends(require_role("coordinator", "admin")),
        Depends(rate_limit("org_write", limit=20)),
    ],
)
async def verify_organization(organization_id: uuid.UUID, db: DbSession, claims: Claims):
    """Coordinator/admin approves an org — enables it to claim requests (AC-8.4)."""
    svc = _service(db)
    org = await svc.get(organization_id)
    updated = await svc.verify(org, uuid.UUID(claims["sub"]))
    await AuditService(AuditRepository(db)).record(
        "organization.verified",
        actor_id=uuid.UUID(claims["sub"]),
        resource_type="organization",
        resource_id=updated.id,
        ip_address=client_ip_ctx.get(),
    )
    return org_to_response(updated)


@router.patch(
    "/{organization_id}/capacity",
    response_model=OrganizationResponse,
    dependencies=[
        Depends(require_role("provider")),
        Depends(rate_limit("org_write", limit=50)),
    ],
)
async def set_capacity(
    organization_id: uuid.UUID, data: CapacityRequest, db: DbSession, claims: Claims
):
    """Provider sets its concurrent-request capacity (F4/AC-4.5)."""
    svc = _service(db)
    org = await svc.get(organization_id)
    updated = await svc.set_capacity(org, uuid.UUID(claims["sub"]), data)
    return org_to_response(updated)


@router.patch(
    "/{organization_id}/availability",
    response_model=OrganizationResponse,
    dependencies=[
        Depends(require_role("provider")),
        Depends(rate_limit("org_write", limit=30)),
    ],
)
async def set_availability(
    organization_id: uuid.UUID, data: AvailabilityRequest, db: DbSession, claims: Claims
):
    """Provider toggles itself in/out of matching."""
    svc = _service(db)
    org = await svc.get(organization_id)
    updated = await svc.set_availability(org, uuid.UUID(claims["sub"]), data.is_available)
    return org_to_response(updated)
