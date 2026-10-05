"""Incidents module router — ``/incidents`` + the lifecycle transition endpoints (doc 40 §5.2).

Mounted at ``/api/v1/incidents`` by ``app.main``. Static sub-paths (``/mine``, ``/nearby``) are
declared before ``/{incident_id}`` so they match correctly.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import (
    get_current_claims,
    get_db,
    get_optional_claims,
    require_role,
)
from app.core.exceptions import AppError
from app.core.logging import client_ip_ctx
from app.core.pagination import paginate
from app.core.rate_limit import rate_limit
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.modules.incidents.lifecycle import IncidentStatus, Priority, ServiceType
from app.modules.incidents.repository import IncidentRepository
from app.modules.incidents.schemas import (
    AcceptRequest,
    ApproveRequest,
    AssignRequest,
    CancelRequest,
    CompleteRequest,
    IncidentCreate,
    IncidentResponse,
    IncidentUpdateResponse,
    PatchIncidentRequest,
    RejectRequest,
    VerifyRequest,
)
from app.modules.incidents.service import IncidentService, to_response
from app.modules.notifications.models import NotificationType
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.service import NotificationService
from app.modules.resources.repository import OrganizationRepository
from app.modules.resources.service import OrganizationService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]

# A guest (no token) may create only a few requests per minute — stricter than the signed-in cap.
_guest_create_limiter = rate_limit("incident_create_guest", limit=5)


def guest_create_rate_limit(request: Request) -> None:
    """Apply the tighter guest budget only to unauthenticated (no ``Authorization``) creates."""
    if request.headers.get("Authorization") is None:
        _guest_create_limiter(request)


def _service(db: DbSession) -> IncidentService:
    return IncidentService(IncidentRepository(db))


def _org_service(db: DbSession) -> OrganizationService:
    return OrganizationService(OrganizationRepository(db))


def _actor(claims: dict) -> tuple[uuid.UUID, str]:
    return uuid.UUID(claims["sub"]), claims["role"]


# --------------------------------------------------------------------------- create & read
@router.post(
    "",
    response_model=IncidentResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[
        Depends(rate_limit("incident_create", limit=20)),
        Depends(guest_create_rate_limit),
    ],
)
async def create_incident(
    data: IncidentCreate,
    db: DbSession,
    claims: dict | None = Depends(get_optional_claims),
) -> IncidentResponse:
    """Create a help request. Unauthenticated = guest (gets a tracking token); providers may not."""
    requester_id: uuid.UUID | None = None
    if claims is not None:
        if claims.get("role") == "provider":
            raise AppError(403, "forbidden", "Providers cannot raise help requests.")
        requester_id = uuid.UUID(claims["sub"])
    incident = await _service(db).create(data, requester_id)
    return to_response(incident)


@router.get("")
async def list_incidents(
    db: DbSession,
    claims: Claims,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status_filter: IncidentStatus | None = Query(None, alias="status"),
    service_type: ServiceType | None = None,
    priority: Priority | None = None,
    q: str | None = Query(None, min_length=1, max_length=100),
    sort: str | None = Query(None, description="field or -field; one of created_at, priority"),
) -> dict:
    """List incidents, role-scoped and filterable, wrapped with pagination.

    Filters: ``status``, ``service_type``, ``priority``, ``q`` (free-text over the description);
    ``sort`` = ``created_at``/``priority`` with an optional leading ``-`` for descending.
    """
    _, role = _actor(claims)
    user_id = uuid.UUID(claims["sub"])
    incidents, total = await _service(db).list_incidents(
        role=role,
        user_id=user_id,
        page=page,
        limit=limit,
        status=status_filter,
        service_type=service_type,
        priority=priority,
        q=q,
        sort=sort,
    )
    return paginate(
        [to_response(i).model_dump(mode="json") for i in incidents], page, limit, total
    )


@router.get("/mine")
async def list_mine(
    db: DbSession,
    claims: Claims,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """The current citizen's own requests (AC-7.1)."""
    user_id = uuid.UUID(claims["sub"])
    incidents, total = await _service(db).list_mine(user_id, page, limit)
    return paginate(
        [to_response(i).model_dump(mode="json") for i in incidents], page, limit, total
    )


@router.get("/assigned")
async def list_assigned(
    db: DbSession,
    claims: Annotated[dict, Depends(require_role("provider"))],
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """The provider's work queue — requests assigned to their organization (AC-8.2)."""
    org = await _org_service(db).get_mine(uuid.UUID(claims["sub"]))
    incidents, total = await _service(db).list_assigned(org.id, page, limit)
    return paginate(
        [to_response(i).model_dump(mode="json") for i in incidents], page, limit, total
    )


@router.get("/nearby")
async def nearby(
    db: DbSession,
    _: Annotated[dict, Depends(get_current_claims)],
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    radius_km: float = Query(5.0, gt=0, le=100),
    service_type: ServiceType | None = None,
) -> dict:
    """Open, unassigned requests near a point, nearest first (PostGIS proximity, AC-4.1)."""
    incidents = await _service(db).nearby(latitude, longitude, radius_km, service_type)
    return {"data": [to_response(i).model_dump(mode="json") for i in incidents]}


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: uuid.UUID, db: DbSession, claims: Claims) -> IncidentResponse:
    """Fetch one help request; a citizen may read only their own (else 403)."""
    incident = await _service(db).get(incident_id)
    _, role = _actor(claims)
    if role == "citizen" and incident.requester_id != uuid.UUID(claims["sub"]):
        raise AppError(403, "forbidden", "You can only view your own request.")
    return to_response(incident)


@router.get("/{incident_id}/updates")
async def incident_updates(incident_id: uuid.UUID, db: DbSession, _: Claims) -> dict:
    """The status timeline (AC-5, AC-7)."""
    updates = await _service(db).updates(incident_id)
    return {
        "data": [IncidentUpdateResponse.model_validate(u).model_dump(mode="json") for u in updates]
    }


@router.patch("/{incident_id}", response_model=IncidentResponse)
async def patch_incident(
    incident_id: uuid.UUID, data: PatchIncidentRequest, db: DbSession, claims: Claims
) -> IncidentResponse:
    """Edit a request's description/priority — allowed only before it is accepted (AC-5.3)."""
    actor_id, role = _actor(claims)
    svc = _service(db)
    incident = await svc.get(incident_id)
    updated = await svc.patch(incident, actor_id, role, data.description, data.priority)
    return to_response(updated)


# --------------------------------------------------------------------------- transitions
async def _transition(db: DbSession, incident_id: uuid.UUID, claims: dict, action: str, **kwargs):
    """Apply one lifecycle action, then notify the requester and write an audit entry.

    Composition happens here at the router edge (feature→notifications, feature→audit) so the
    incident service stays pure. Returns the updated incident's API shape.
    """
    actor_id, role = _actor(claims)
    svc = _service(db)
    incident = await svc.get(incident_id)
    updated = await svc.perform_transition(incident, action, actor_id, role, **kwargs)
    await _notify_requester(db, updated, actor_id)
    await AuditService(AuditRepository(db)).record(
        f"incident.{action}",
        actor_id=actor_id,
        resource_type="incident",
        resource_id=updated.id,
        ip_address=client_ip_ctx.get(),
        new_values={"status": updated.status.value},
    )
    return to_response(updated)


async def _notify_requester(db: DbSession, incident, actor_id: uuid.UUID) -> None:
    """PICS-NTF-001: on every incident state change, notify the requester (unless a guest, or the
    requester made the change themselves)."""
    if incident.requester_id is None or incident.requester_id == actor_id:
        return
    await NotificationService(NotificationRepository(db)).notify(
        user_id=incident.requester_id,
        ntype=NotificationType.incident_update,
        title="Update on your request",
        message=f"Your help request is now '{incident.status.value}'.",
        link=f"/incidents/{incident.id}",
    )


@router.post("/{incident_id}/approve", response_model=IncidentResponse)
async def approve(incident_id: uuid.UUID, data: ApproveRequest, db: DbSession, claims: Claims):
    """Coordinator approves a critical request so providers may claim it."""
    return await _transition(db, incident_id, claims, "approve", note=data.note)


@router.post("/{incident_id}/reject", response_model=IncidentResponse)
async def reject(incident_id: uuid.UUID, data: RejectRequest, db: DbSession, claims: Claims):
    """Coordinator rejects a request, recording the reason."""
    return await _transition(db, incident_id, claims, "reject", reason=data.reason)


@router.post("/{incident_id}/accept", response_model=IncidentResponse)
async def accept(incident_id: uuid.UUID, data: AcceptRequest, db: DbSession, claims: Claims):
    """A provider claims a request for their own verified organization (resolved server-side)."""
    org = await _org_service(db).resolve_active_for_owner(uuid.UUID(claims["sub"]))
    return await _transition(
        db, incident_id, claims, "accept", organization_id=org.id, note=data.eta
    )


@router.post("/{incident_id}/assign", response_model=IncidentResponse)
async def assign(incident_id: uuid.UUID, data: AssignRequest, db: DbSession, claims: Claims):
    """A coordinator assigns the request to a specific verified organization."""
    org = await _org_service(db).get(data.organization_id)
    if not org.is_verified:
        raise AppError(409, "org_not_verified", "That organization is not verified.")
    return await _transition(db, incident_id, claims, "assign", organization_id=org.id)


@router.post("/{incident_id}/start", response_model=IncidentResponse)
async def start(incident_id: uuid.UUID, db: DbSession, claims: Claims):
    """The assigned provider marks work started (only their org's requests, else 403)."""
    org = await _org_service(db).get_mine(uuid.UUID(claims["sub"]))
    return await _transition(db, incident_id, claims, "start", actor_organization_id=org.id)


@router.post("/{incident_id}/complete", response_model=IncidentResponse)
async def complete(incident_id: uuid.UUID, data: CompleteRequest, db: DbSession, claims: Claims):
    """The assigned provider marks the request completed (awaits requester verification)."""
    org = await _org_service(db).get_mine(uuid.UUID(claims["sub"]))
    return await _transition(
        db, incident_id, claims, "complete", actor_organization_id=org.id, note=data.notes
    )


@router.post("/{incident_id}/verify", response_model=IncidentResponse)
async def verify(incident_id: uuid.UUID, data: VerifyRequest, db: DbSession, claims: Claims):
    """The requester confirms resolution and rates the response (AC-7.2)."""
    return await _transition(
        db, incident_id, claims, "verify", rating=data.rating, review=data.review
    )


@router.post("/{incident_id}/cancel", response_model=IncidentResponse)
async def cancel(incident_id: uuid.UUID, data: CancelRequest, db: DbSession, claims: Claims):
    """Cancel a request, recording the reason (citizen may cancel only their own)."""
    return await _transition(db, incident_id, claims, "cancel", reason=data.reason)
