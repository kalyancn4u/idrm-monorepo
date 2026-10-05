"""
services/service_service.py — service-request business logic (Module M3).

Owns the whole request lifecycle: create, list, read, and the status-changing
actions (approve / reject / accept / start / complete / verify / cancel / dispute),
following the FS §6.1 state machine. Route handlers in `api/v1/services.py` stay
thin and call these functions.

What the DATABASE already does for us (so this layer must NOT duplicate it):
  • `updated_at` is bumped by a trigger on every UPDATE.
  • Organisation capacity & stats (available_capacity, totals, average_rating) are
    maintained by the `update_organization_stats` trigger on status changes.
  • An immutable audit row is written by `audit_service_request_changes` on every
    insert and status change — so we never write audit logs by hand.

Geometry: `location` is a PostGIS Point in SRID 4326, ordered [lon, lat]. We write
it with ST_SetSRID(ST_MakePoint(lon, lat), 4326) and read it back via GeoAlchemy2's
`to_shape` (a Shapely point whose `.x` is longitude and `.y` is latitude).

Real-time + notifications (M5): on create and on every status change we publish a
best-effort map event to Redis (the `service_requests` channel) for the gateway
(G4) to fan out over WebSocket; on `accept`/`complete` we also create a notification
for the requestor. None of this can break the action — the notification shares the
action's transaction, and Redis publishing is best-effort (never raises).

Known gap (documented): `users` has no organisation link, but a request needs a
`provider_id` once accepted. So `accept` takes the org_id in its body and we
validate it is a verified organisation. When a user↔org membership model lands,
derive the org from the acting user and drop org_id from the body.
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from geoalchemy2.shape import to_shape
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import CHANNEL_SERVICE_REQUESTS, publish_json
from dbmodels.enums import EMERGENCY_PRIORITIES
from dbmodels.organization import Organization
from dbmodels.service_request import ServiceRequest
from dbmodels.user import User
from schemas.common import GeoPoint, Page
from schemas.service import (
    AcceptBody,
    ApproveBody,
    CancelBody,
    CompleteBody,
    DisputeBody,
    ProviderBrief,
    RejectBody,
    RequestorBrief,
    ServiceCreate,
    ServiceListItem,
    ServiceOut,
    VerifyBody,
)
from services import notification_service

# Roles allowed to perform each class of action (ADMIN can do anything).
_DM_ROLES = {"DM_AUTHORITY", "ADMIN"}
_PROVIDER_ROLES = {"PROVIDER", "ADMIN"}
# Roles that may always see a requestor's identity/contact, regardless of privacy.
_PRIVILEGED_VIEWERS = {"ADMIN", "DM_AUTHORITY", "MANAGER", "EVENT_MANAGER", "AUDITOR"}


# ---- small helpers ----------------------------------------------------------
def _naive_utcnow() -> datetime:
    """Current UTC time as a naive datetime (the timestamp columns are tz-naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _point_to_geopoint(location) -> GeoPoint:
    """Convert a PostGIS WKB point (as fetched by GeoAlchemy2) to a GeoJSON point.
    Shapely's `.x` is longitude and `.y` is latitude — GeoJSON order is [lon, lat]."""
    point = to_shape(location)
    return GeoPoint(coordinates=(point.x, point.y))


async def _publish_request_event(req: ServiceRequest, event_type: str) -> None:
    """Best-effort: publish a map event ('request_created' / 'request_updated') to
    the Redis `service_requests` channel so the gateway (G4) can push it over
    WebSocket. Identity-free (map-safe) and never raises — `publish_json` swallows
    Redis errors. Call AFTER the transaction has committed."""
    point = _point_to_geopoint(req.location)
    await publish_json(
        CHANNEL_SERVICE_REQUESTS,
        {
            "type": event_type,
            "request": {
                "service_id": str(req.service_id),
                "service_type": req.service_type,
                "priority": req.priority,
                "status": req.status,
                "address": req.address,
                "location": {"type": "Point", "coordinates": list(point.coordinates)},
                "created_at": req.created_at,
            },
        },
    )


def _require_role(user: User, allowed: set[str], action: str) -> None:
    """403 unless `user.role` is in `allowed`."""
    if user.role not in allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Your role ({user.role}) may not {action} this request",
        )


def _require_owner(user: User, req: ServiceRequest, action: str) -> None:
    """403 unless `user` is the request's requestor (ADMIN is always allowed)."""
    if user.role != "ADMIN" and user.user_id != req.requestor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only the requestor may {action} this request",
        )


def _require_status(req: ServiceRequest, allowed: set[str], action: str) -> None:
    """409 unless the request's current status is one of `allowed`."""
    if req.status not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot {action} a request while it is {req.status}",
        )


def _can_see_contact(viewer: User | None, req: ServiceRequest) -> bool:
    """Privacy gate: may `viewer` see the requestor's identity + contact phone?

    PUBLIC → everyone. Otherwise only the requestor themselves or a privileged
    role. (Assigned providers should also get contact "via the system", but that
    needs the user↔org membership model — see the module docstring's known gap.)
    """
    if req.privacy_level == "PUBLIC":
        return True
    if viewer is None:
        return False
    if viewer.user_id == req.requestor_id:
        return True
    return viewer.role in _PRIVILEGED_VIEWERS


def _to_service_out(
    req: ServiceRequest,
    requestor: User | None,
    provider: Organization | None,
    viewer: User | None,
) -> ServiceOut:
    """Assemble a ServiceOut, converting the geometry and applying privacy."""
    show_contact = _can_see_contact(viewer, req)
    return ServiceOut(
        service_id=req.service_id,
        service_type=req.service_type,
        priority=req.priority,
        status=req.status,
        location=_point_to_geopoint(req.location),
        address=req.address,
        description=req.description,
        num_people_affected=req.num_people_affected,
        privacy_level=req.privacy_level,
        contact_phone=req.contact_phone if show_contact else None,
        created_at=req.created_at,
        accepted_at=req.accepted_at,
        completed_at=req.completed_at,
        verified_at=req.verified_at,
        rating=req.rating,
        feedback=req.feedback,
        requestor=RequestorBrief.model_validate(requestor) if (show_contact and requestor) else None,
        provider=ProviderBrief.model_validate(provider) if provider else None,
    )


async def _get_or_404(db: AsyncSession, service_id: uuid.UUID) -> ServiceRequest:
    """Fetch a request by id, or raise 404."""
    req = await db.scalar(select(ServiceRequest).where(ServiceRequest.service_id == service_id))
    if req is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")
    return req


async def _serialize(db: AsyncSession, req: ServiceRequest, viewer: User | None) -> ServiceOut:
    """Load the request's requestor + provider and build a privacy-aware ServiceOut."""
    requestor = await db.scalar(select(User).where(User.user_id == req.requestor_id))
    provider = None
    if req.provider_id is not None:
        provider = await db.scalar(select(Organization).where(Organization.org_id == req.provider_id))
    return _to_service_out(req, requestor, provider, viewer)


# ---- create / read ----------------------------------------------------------
async def create_request(db: AsyncSession, requestor: User, data: ServiceCreate) -> ServiceOut:
    """Create a request. Emergencies (CRITICAL/HIGH) are auto-approved by the system
    (SUBMITTED → APPROVED, per decision D5); everything else starts SUBMITTED awaiting
    DM review. Publishes a `request_created` map event."""
    longitude, latitude = data.location.coordinates
    new_status = "APPROVED" if data.priority in EMERGENCY_PRIORITIES else "SUBMITTED"
    req = ServiceRequest(
        requestor_id=requestor.user_id,
        service_type=data.service_type.value,
        priority=data.priority.value,
        status=new_status,
        location=func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326),
        address=data.address,
        description=data.description,
        num_people_affected=data.num_people_affected,
        privacy_level=data.privacy_level.value,
        contact_phone=data.contact_phone,
    )
    db.add(req)
    await db.commit()
    await db.refresh(req)  # load DB-generated columns + the stored geometry
    await _publish_request_event(req, "request_created")
    return await _serialize(db, req, requestor)


async def get_request(db: AsyncSession, service_id: uuid.UUID, viewer: User | None) -> ServiceOut:
    """Read one request (privacy applied for the given viewer, who may be None)."""
    req = await _get_or_404(db, service_id)
    return await _serialize(db, req, viewer)


async def list_requests(
    db: AsyncSession,
    *,
    status: str | None = None,
    service_type: str | None = None,
    priority: str | None = None,
    requestor_id: uuid.UUID | None = None,
    provider_id: uuid.UUID | None = None,
    page: int = 1,
    per_page: int = 20,
) -> Page[ServiceListItem]:
    """Paginated, filterable list of requests (newest first). Compact rows only —
    no requestor identity — so this is safe for public/map views. `requestor_id`
    (the `?mine=true` path) restricts to a user's own requests; `provider_id`
    restricts to a provider org's assigned requests (the provider pages)."""
    per_page = min(max(per_page, 1), 100)
    page = max(page, 1)

    conditions = []
    if status:
        conditions.append(ServiceRequest.status == status)
    if service_type:
        conditions.append(ServiceRequest.service_type == service_type)
    if priority:
        conditions.append(ServiceRequest.priority == priority)
    if requestor_id:
        conditions.append(ServiceRequest.requestor_id == requestor_id)
    if provider_id:
        conditions.append(ServiceRequest.provider_id == provider_id)

    count_stmt = select(func.count()).select_from(ServiceRequest)
    list_stmt = select(ServiceRequest).order_by(ServiceRequest.created_at.desc())
    if conditions:
        count_stmt = count_stmt.where(*conditions)
        list_stmt = list_stmt.where(*conditions)
    list_stmt = list_stmt.limit(per_page).offset((page - 1) * per_page)

    total = await db.scalar(count_stmt) or 0
    rows = (await db.scalars(list_stmt)).all()
    items = [ServiceListItem.model_validate(row) for row in rows]
    pages = (total + per_page - 1) // per_page  # ceil division
    return Page[ServiceListItem](items=items, total=total, page=page, per_page=per_page, pages=pages)


# ---- lifecycle actions ------------------------------------------------------
# Each action enforces the right ROLE and the right current STATUS per the FS §6.1
# state machine, then sets the new status (+ any timeline timestamp). The DB
# triggers take care of updated_at, organisation stats, and audit logging; we then
# publish a best-effort `request_updated` map event (and, on accept/complete, a
# notification for the requestor).

async def approve(db: AsyncSession, user: User, service_id: uuid.UUID, body: ApproveBody) -> ServiceOut:
    """DM Authority approves a SUBMITTED request → APPROVED (now visible to providers)."""
    req = await _get_or_404(db, service_id)
    _require_role(user, _DM_ROLES, "approve")
    _require_status(req, {"SUBMITTED"}, "approve")
    req.status = "APPROVED"
    await db.commit()
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def reject(db: AsyncSession, user: User, service_id: uuid.UUID, body: RejectBody) -> ServiceOut:
    """DM Authority rejects a SUBMITTED (or DISPUTED) request → REJECTED, with a reason."""
    req = await _get_or_404(db, service_id)
    _require_role(user, _DM_ROLES, "reject")
    _require_status(req, {"SUBMITTED", "DISPUTED"}, "reject")
    req.status = "REJECTED"
    req.rejection_reason = body.reason
    await db.commit()
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def accept(db: AsyncSession, user: User, service_id: uuid.UUID, body: AcceptBody) -> ServiceOut:
    """Provider accepts an APPROVED request on behalf of `body.org_id` → ACCEPTED.

    Race-safe: we SELECT ... FOR UPDATE the row only while it is still APPROVED and
    unassigned, so two providers can't grab the same request (the loser gets 409).
    Mirrors the pattern in IDRM-Database-Query-Reference.md. Notifies the requestor.
    """
    _require_role(user, _PROVIDER_ROLES, "accept")

    org = await db.scalar(select(Organization).where(Organization.org_id == body.org_id))
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    if not org.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Organization is not verified")

    # Lock the row; returns None if it is no longer APPROVED & unassigned.
    req = await db.scalar(
        select(ServiceRequest)
        .where(
            ServiceRequest.service_id == service_id,
            ServiceRequest.status == "APPROVED",
            ServiceRequest.provider_id.is_(None),
        )
        .with_for_update()
    )
    if req is None:
        # Distinguish "doesn't exist" from "already taken / not approved".
        exists = await db.scalar(
            select(ServiceRequest.service_id).where(ServiceRequest.service_id == service_id)
        )
        if exists is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service request not found")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Request is not available to accept (already taken or not APPROVED)",
        )

    req.provider_id = org.org_id
    req.status = "ACCEPTED"
    req.accepted_at = _naive_utcnow()
    if body.notes:
        req.acceptance_notes = body.notes

    # Tell the requestor help is on the way (saved in the same transaction).
    notification = await notification_service.create_notification(
        db,
        user_id=req.requestor_id,
        type="SERVICE_ACCEPTED",
        subject="Your request was accepted",
        body=f"{org.name} accepted your {req.service_type} request and is on the way.",
        related_service_id=req.service_id,
        related_org_id=org.org_id,
    )
    await db.commit()
    await notification_service.publish_notification(notification)
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def start(db: AsyncSession, user: User, service_id: uuid.UUID) -> ServiceOut:
    """Provider starts work: ACCEPTED → IN_PROGRESS. (Present to honour the FS §6.1
    state machine — `complete` requires IN_PROGRESS.)"""
    req = await _get_or_404(db, service_id)
    _require_role(user, _PROVIDER_ROLES, "start work on")
    _require_status(req, {"ACCEPTED"}, "start work on")
    req.status = "IN_PROGRESS"
    await db.commit()
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def complete(db: AsyncSession, user: User, service_id: uuid.UUID, body: CompleteBody) -> ServiceOut:
    """Provider marks delivery done: IN_PROGRESS → COMPLETED (sets completed_at) and
    asks the requestor to verify."""
    req = await _get_or_404(db, service_id)
    _require_role(user, _PROVIDER_ROLES, "complete")
    _require_status(req, {"IN_PROGRESS"}, "complete")
    req.status = "COMPLETED"
    req.completed_at = _naive_utcnow()
    if body.notes:
        req.completion_notes = body.notes

    notification = await notification_service.create_notification(
        db,
        user_id=req.requestor_id,
        type="VERIFICATION_REQUEST",
        subject="Please verify your request",
        body="The provider marked your request complete. Please confirm and rate the service.",
        related_service_id=req.service_id,
    )
    await db.commit()
    await notification_service.publish_notification(notification)
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def verify(db: AsyncSession, user: User, service_id: uuid.UUID, body: VerifyBody) -> ServiceOut:
    """Requestor confirms a COMPLETED service → VERIFIED, with a 1–5 rating + feedback.
    (The DB CHECK only allows a rating once status is VERIFIED, so we set them together.)"""
    req = await _get_or_404(db, service_id)
    _require_owner(user, req, "verify")
    _require_status(req, {"COMPLETED"}, "verify")
    req.status = "VERIFIED"
    req.verified_at = _naive_utcnow()
    req.rating = body.rating
    req.feedback = body.feedback
    await db.commit()
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def cancel(db: AsyncSession, user: User, service_id: uuid.UUID, body: CancelBody) -> ServiceOut:
    """Requestor cancels while still SUBMITTED or APPROVED → CANCELLED. (Per the API
    contract; FS BR-SR-005 also forbids cancelling once IN_PROGRESS or later.)"""
    req = await _get_or_404(db, service_id)
    _require_owner(user, req, "cancel")
    _require_status(req, {"SUBMITTED", "APPROVED"}, "cancel")
    req.status = "CANCELLED"
    await db.commit()
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)


async def dispute(db: AsyncSession, user: User, service_id: uuid.UUID, body: DisputeBody) -> ServiceOut:
    """Requestor raises a dispute from IN_PROGRESS or COMPLETED → DISPUTED. A DM
    Authority then resolves it (→ IN_PROGRESS reassignment, or → REJECTED via `reject`)."""
    req = await _get_or_404(db, service_id)
    _require_owner(user, req, "dispute")
    _require_status(req, {"IN_PROGRESS", "COMPLETED"}, "dispute")
    req.status = "DISPUTED"
    await db.commit()
    await _publish_request_event(req, "request_updated")
    return await _serialize(db, req, user)
