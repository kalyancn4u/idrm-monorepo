"""Load rich, realistic sample data — **idempotent** (safe to run many times).

Implements the signed-off seed spec (roadmap §3.4; documented row-by-row in
``docs/mvp/34-seed-data-and-fixtures.md``): the four PRD personas (Rajesh / Priya / Arjun /
Lakshmi) plus extras, three provider organizations with resources, incidents in **all eight
lifecycle states** (including one **guest** submission) with real Telangana / Andhra Pradesh
coordinates, plus the supporting timeline, alerts, notifications, files and audit rows.

**Idempotency:** every row uses a deterministic UUID (``uuid5`` of a stable key), and each insert is
guarded by a primary-key lookup — running ``make seed`` twice never creates duplicates
(``50-data-model.md`` §9). Run via ``make seed`` (after ``make migrate``).
"""

from __future__ import annotations

import asyncio
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from geoalchemy2.elements import WKTElement
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.infrastructure.database.engine import async_session
from app.modules.alerts.models import Alert, AlertSeverity
from app.modules.audit.models import AuditLog
from app.modules.files.models import File, FilePurpose
from app.modules.incidents.lifecycle import IncidentStatus, Priority, ServiceType, next_status
from app.modules.incidents.models import Incident, IncidentUpdate
from app.modules.notifications.models import Notification, NotificationType
from app.modules.resources.models import Organization, OrgType, Resource
from app.modules.users.models import User, UserRole, UserStatus

# A fixed namespace so seed UUIDs are stable across runs (the key to idempotency).
_NS = uuid.UUID("1d3e0a5c-000d-4b12-a000-1de70a5eed00")
SEED_PASSWORD = "IDRMseed#2026"  # dev-only; the Ubuntu bring-up rotates real creds (PENDING.md §1)
NOW = datetime.now(UTC)


def sid(*parts: str) -> uuid.UUID:
    """A deterministic seed id from stable parts (idempotency key)."""
    return uuid.uuid5(_NS, ":".join(parts))


def point(latitude: float, longitude: float) -> WKTElement:
    """A PostGIS POINT (SRID 4326). Note WKT uses ``longitude latitude`` order."""
    return WKTElement(f"POINT({longitude} {latitude})", srid=4326)


def box_multipolygon(min_lat: float, min_lng: float, max_lat: float, max_lng: float) -> WKTElement:
    """A rectangular MULTIPOLYGON (SRID 4326) for an alert's affected area."""
    ring = [
        (min_lng, min_lat), (max_lng, min_lat), (max_lng, max_lat),
        (min_lng, max_lat), (min_lng, min_lat),
    ]
    coords = ", ".join(f"{lng} {lat}" for lng, lat in ring)
    return WKTElement(f"MULTIPOLYGON((({coords})))", srid=4326)


async def _get_or_create(session: AsyncSession, model: type, pk: uuid.UUID, **fields: Any) -> Any:
    """Insert a row with a fixed id only if it does not already exist (idempotent)."""
    existing = await session.get(model, pk)
    if existing is not None:
        return existing
    obj = model(id=pk, **fields)
    session.add(obj)
    return obj


# --------------------------------------------------------------------------- users
# (email, role, name, home lat/lng) — password is shared (dev only).
_USERS = [
    ("rajesh@idrm.example", UserRole.citizen, "Rajesh Kumar", 17.385, 78.486),
    ("priya@idrm.example", UserRole.provider, "Dr. Priya Sharma", 17.441, 78.391),
    ("arjun@idrm.example", UserRole.coordinator, "Arjun Reddy", 17.978, 79.594),
    ("lakshmi@idrm.example", UserRole.admin, "Lakshmi Iyer (IAS)", 16.506, 80.648),
    ("sita@idrm.example", UserRole.citizen, "Sita Devi", 17.400, 78.500),
    ("mohan@idrm.example", UserRole.citizen, "Mohan Rao", 17.960, 79.560),
    ("kiran@idrm.example", UserRole.provider, "Kiran Varma", 17.978, 79.594),
    ("ananya@idrm.example", UserRole.provider, "Ananya Nair", 17.385, 78.486),
]


async def _seed_users(session: AsyncSession, password_hash: str) -> dict[str, uuid.UUID]:
    ids: dict[str, uuid.UUID] = {}
    for email, role, name, _lat, _lng in _USERS:
        uid = sid("user", email)
        ids[email] = uid
        await _get_or_create(
            session, User, uid,
            email=email, password_hash=password_hash, name=name, role=role,
            status=UserStatus.active, email_verified=True,
        )
    return ids


# --------------------------------------------------------------------------- organizations
# (key, name, type, owner email, categories, centre lat/lng, radius, verified, capacity)
_ORGS = [
    ("priya-care", "Priya Care Hospital", OrgType.hospital, "priya@idrm.example",
     [ServiceType.medical], 17.441, 78.391, 15.0, True, 20),
    ("deccan-relief", "Deccan Relief NGO", OrgType.ngo, "ananya@idrm.example",
     [ServiceType.food, ServiceType.shelter], 17.385, 78.486, 25.0, True, 50),
    ("warangal-corps", "Warangal Volunteer Corps", OrgType.volunteer_group, "kiran@idrm.example",
     [ServiceType.rescue], 17.978, 79.594, 30.0, False, 15),
]


async def _seed_orgs(
    session: AsyncSession, users: dict[str, uuid.UUID]
) -> dict[str, uuid.UUID]:
    ids: dict[str, uuid.UUID] = {}
    lakshmi = users["lakshmi@idrm.example"]
    for key, name, otype, owner, cats, lat, lng, radius, verified, cap in _ORGS:
        oid = sid("org", key)
        ids[key] = oid
        await _get_or_create(
            session, Organization, oid,
            name=name, type=otype, owner_user_id=users[owner], service_categories=cats,
            service_area_center=point(lat, lng), service_radius_km=radius,
            capacity=cap, available_capacity=cap, is_verified=verified,
            verified_by=lakshmi if verified else None,
            verified_at=NOW - timedelta(days=3) if verified else None,
        )
    return ids


# (key, org key, name, kind, qty, lat/lng, available)
_RESOURCES = [
    ("ambulance-01", "priya-care", "Ambulance-01", "ambulance", 2, 17.441, 78.391, True),
    ("beds-01", "priya-care", "Hospital Beds", "beds", 40, 17.441, 78.391, True),
    ("boat-01", "warangal-corps", "Rescue Boat", "boat", 1, 17.978, 79.594, True),
    ("tanker-01", "deccan-relief", "Water Tanker", "water_tanker", 3, 17.385, 78.486, True),
]


async def _seed_resources(session: AsyncSession, orgs: dict[str, uuid.UUID]) -> None:
    for key, org_key, name, kind, qty, lat, lng, available in _RESOURCES:
        await _get_or_create(
            session, Resource, sid("resource", key),
            organization_id=orgs[org_key], name=name, kind=kind, quantity=qty,
            location=point(lat, lng), is_available=available,
        )


# --------------------------------------------------------------------------- incidents + timeline
# Each spec: key, service_type, priority, final status, requester email (or None=guest),
# assigned org key (or None), lat/lng, description, and the ordered actions that produced the state.
_INCIDENTS = [
    ("created", ServiceType.water, Priority.high, IncidentStatus.created,
     "sita@idrm.example", None, 17.40, 78.50, "Borewell dry — need drinking water.", []),
    ("approved", ServiceType.rescue, Priority.critical, IncidentStatus.approved,
     "mohan@idrm.example", None, 17.98, 79.60, "Building collapse, people trapped.", ["approve"]),
    ("accepted", ServiceType.medical, Priority.critical, IncidentStatus.accepted,
     "rajesh@idrm.example", "priya-care", 17.39, 78.47, "Injured, need medical help.",
     ["approve", "accept"]),
    ("in_progress", ServiceType.medical, Priority.high, IncidentStatus.in_progress,
     "rajesh@idrm.example", "priya-care", 17.44, 78.40, "Elderly patient needs evacuation.",
     ["accept", "start"]),
    ("completed", ServiceType.food, Priority.medium, IncidentStatus.completed,
     "sita@idrm.example", "deccan-relief", 17.38, 78.49, "Food supplies needed at shelter.",
     ["accept", "start", "complete"]),
    ("verified", ServiceType.medical, Priority.high, IncidentStatus.verified,
     "rajesh@idrm.example", "priya-care", 17.42, 78.42, "Medical evacuation completed.",
     ["accept", "start", "complete", "verify"]),
    ("cancelled", ServiceType.shelter, Priority.low, IncidentStatus.cancelled,
     "mohan@idrm.example", None, 17.95, 79.55, "Requested shelter — family found on their own.",
     ["cancel"]),
    ("rejected", ServiceType.other, Priority.low, IncidentStatus.rejected,
     "sita@idrm.example", None, 17.41, 78.51, "Report could not be substantiated.", ["reject"]),
    ("guest", ServiceType.other, Priority.medium, IncidentStatus.created,
     None, None, 16.506, 80.648, "Roadblock near market — need assistance.", []),
]

# Which seeded actor performs each action.
_ACTION_ACTOR = {
    "approve": "coordinator", "reject": "coordinator",
    "cancel": "requester", "verify": "requester",
    "accept": "owner", "start": "owner", "complete": "owner",
}


def _actor_for(
    action: str,
    requester: uuid.UUID | None,
    owner: uuid.UUID | None,
    coordinator: uuid.UUID,
) -> uuid.UUID | None:
    who = _ACTION_ACTOR[action]
    if who == "requester":
        return requester
    if who == "owner":
        return owner
    return coordinator


async def _seed_incidents(
    session: AsyncSession, users: dict[str, uuid.UUID], orgs: dict[str, uuid.UUID]
) -> dict[str, uuid.UUID]:
    coordinator = users["arjun@idrm.example"]
    ids: dict[str, uuid.UUID] = {}
    for key, stype, prio, final, requester_email, org_key, lat, lng, desc, actions in _INCIDENTS:
        iid = sid("incident", key)
        ids[key] = iid
        if await session.get(Incident, iid) is not None:
            continue  # already seeded — keep idempotent
        requester = users[requester_email] if requester_email else None
        owner = users[_owner_email(org_key)] if org_key else None
        created_at = NOW - timedelta(hours=len(actions) + 2)
        incident = Incident(
            id=iid, service_type=stype, priority=prio, status=final, description=desc,
            location=point(lat, lng), requester_id=requester,
            guest_contact="+919000000000" if requester is None else None,
            tracking_token=f"seed-{key}-token" if requester is None else None,
            assigned_organization_id=orgs[org_key] if org_key else None,
            created_at=created_at,
        )
        if final is IncidentStatus.verified:
            incident.rating = 5
            incident.review = "Fast, professional response."
            incident.verified_at = NOW - timedelta(minutes=30)
        if final is IncidentStatus.rejected:
            incident.rejection_reason = "Unverifiable / duplicate report."
        if final is IncidentStatus.cancelled:
            incident.cancellation_reason = "No longer needed."
        session.add(incident)

        # timeline: the initial 'created' row, then one row per action
        session.add(IncidentUpdate(
            id=sid("update", key, "created"), incident_id=iid, from_status=None,
            to_status=IncidentStatus.created, actor_id=requester, note="created",
            created_at=created_at,
        ))
        current = IncidentStatus.created
        for step, action in enumerate(actions, start=1):
            nxt = next_status(action)
            session.add(IncidentUpdate(
                id=sid("update", key, action), incident_id=iid, from_status=current,
                to_status=nxt, actor_id=_actor_for(action, requester, owner, coordinator),
                note=action, created_at=created_at + timedelta(minutes=30 * step),
            ))
            current = nxt
    return ids


def _owner_email(org_key: str) -> str:
    return {o[0]: o[3] for o in _ORGS}[org_key]


# ----------------------------------------------------- alerts / notifications / files / audit
async def _seed_supporting(
    session: AsyncSession,
    users: dict[str, uuid.UUID],
    orgs: dict[str, uuid.UUID],
    incidents: dict[str, uuid.UUID],
) -> None:
    arjun, lakshmi = users["arjun@idrm.example"], users["lakshmi@idrm.example"]
    rajesh, priya = users["rajesh@idrm.example"], users["priya@idrm.example"]

    # alerts — one platform-wide, one area polygon over Hyderabad
    await _get_or_create(
        session, Alert, sid("alert", "monsoon"),
        title="Monsoon advisory", message="Heavy rain expected across Telangana. Stay alert.",
        severity=AlertSeverity.info, area=None, created_by=arjun,
        expires_at=NOW + timedelta(days=2),
    )
    await _get_or_create(
        session, Alert, sid("alert", "hyd-flood"),
        title="Flood warning — Hyderabad", message="Avoid low-lying areas near the Musi river.",
        severity=AlertSeverity.warning, area=box_multipolygon(17.2, 78.3, 17.6, 78.7),
        created_by=arjun, expires_at=NOW + timedelta(days=1),
    )

    # notifications for the citizen whose requests progressed
    await _get_or_create(
        session, Notification, sid("notif", "rajesh-accepted"),
        user_id=rajesh, type=NotificationType.incident_update,
        title="Update on your request", message="Your help request is now 'accepted'.",
        link=f"/incidents/{incidents['accepted']}", is_read=False,
    )
    await _get_or_create(
        session, Notification, sid("notif", "rajesh-verified"),
        user_id=rajesh, type=NotificationType.verification,
        title="Request verified", message="Your resolved request has been verified. Thank you.",
        link=f"/incidents/{incidents['verified']}", is_read=True,
    )

    # files — an incident photo and a completion proof (metadata only; bytes would be in MinIO)
    await _get_or_create(
        session, File, sid("file", "incident-photo"),
        uploaded_by=rajesh, bucket="idrm-uploads",
        object_key="incident_photo/seed-accepted.jpg",
        url="http://127.0.0.1:9000/idrm-uploads/incident_photo/seed-accepted.jpg",
        content_type="image/jpeg", size_bytes=845_000, purpose=FilePurpose.incident_photo,
        entity_type="incident", entity_id=incidents["accepted"],
    )
    await _get_or_create(
        session, File, sid("file", "completion-proof"),
        uploaded_by=priya, bucket="idrm-uploads",
        object_key="completion_proof/seed-completed.jpg",
        url="http://127.0.0.1:9000/idrm-uploads/completion_proof/seed-completed.jpg",
        content_type="image/jpeg", size_bytes=612_000, purpose=FilePurpose.completion_proof,
        entity_type="incident", entity_id=incidents["completed"],
    )

    # audit — a few significant actions (append-only)
    await _get_or_create(
        session, AuditLog, sid("audit", "org-verified"),
        actor_id=lakshmi, action="organization.verified", resource_type="organization",
        resource_id=orgs["priya-care"], new_values={"is_verified": True},
    )
    await _get_or_create(
        session, AuditLog, sid("audit", "incident-approved"),
        actor_id=arjun, action="incident.approve", resource_type="incident",
        resource_id=incidents["approved"], new_values={"status": "approved"},
    )


async def seed() -> None:
    """Load the full idempotent seed dataset in one transaction."""
    password_hash = hash_password(SEED_PASSWORD)  # hashed once; reused for all seed users
    async with async_session() as session:
        users = await _seed_users(session, password_hash)
        orgs = await _seed_orgs(session, users)
        await _seed_resources(session, orgs)
        incidents = await _seed_incidents(session, users, orgs)
        await _seed_supporting(session, users, orgs, incidents)
        await session.commit()
    print(
        f"seed: OK — {len(_USERS)} users, {len(_ORGS)} organizations, "
        f"{len(_RESOURCES)} resources, {len(_INCIDENTS)} incidents (+ timeline, alerts, "
        f"notifications, files, audit). Idempotent: safe to re-run."
    )


def main() -> None:
    """Entry point for ``make seed``."""
    asyncio.run(seed())


if __name__ == "__main__":
    main()
