"""Resources module router — ``/resources`` (provider assets on the map; doc 40 §5.3).

Mounted at ``/api/v1/resources`` by ``app.main``. The sibling ``/organizations`` endpoints live in
``org_router`` (same module, mounted at ``/api/v1/organizations``).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db, require_role
from app.core.pagination import paginate
from app.core.rate_limit import rate_limit
from app.modules.resources.repository import OrganizationRepository, ResourceRepository
from app.modules.resources.schemas import ResourceCreate, ResourceResponse, ResourceUpdate
from app.modules.resources.service import ResourceService, resource_to_response

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]
ProviderClaims = Annotated[dict, Depends(require_role("provider"))]


def _service(db: DbSession) -> ResourceService:
    return ResourceService(ResourceRepository(db), OrganizationRepository(db))


@router.get("")
async def list_resources(
    db: DbSession,
    claims: Claims,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """List resources, role-scoped (providers see their own; coordinators/admins see all)."""
    resources, total = await _service(db).list(
        role=claims["role"], owner_user_id=uuid.UUID(claims["sub"]), page=page, limit=limit
    )
    return paginate(
        [resource_to_response(r).model_dump(mode="json") for r in resources], page, limit, total
    )


@router.post(
    "",
    response_model=ResourceResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("resource_write", limit=20))],
)
async def create_resource(
    data: ResourceCreate, db: DbSession, claims: ProviderClaims
) -> ResourceResponse:
    """Declare an asset for the authenticated provider's organization."""
    resource = await _service(db).create(data, uuid.UUID(claims["sub"]))
    return resource_to_response(resource)


@router.patch(
    "/{resource_id}",
    response_model=ResourceResponse,
    dependencies=[Depends(rate_limit("resource_write", limit=20))],
)
async def update_resource(
    resource_id: uuid.UUID, data: ResourceUpdate, db: DbSession, claims: ProviderClaims
) -> ResourceResponse:
    """Edit one of the provider's own assets (only the owning provider may; else 403)."""
    resource = await _service(db).update(resource_id, uuid.UUID(claims["sub"]), data)
    return resource_to_response(resource)
