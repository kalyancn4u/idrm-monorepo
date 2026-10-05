"""Incidents module service — create help requests and drive the lifecycle (roadmap §5.2, §13.4).

Enforces the 8-state machine (illegal jump -> 409), single-claim (first accept wins -> 409
already_accepted), assigned-provider-only progress, and citizen ownership on verify/cancel.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import UTC, datetime

from app.core.exceptions import AppError
from app.modules.incidents.lifecycle import (
    IncidentStatus,
    Priority,
    ServiceType,
    can_transition,
    next_status,
    role_allowed,
)
from app.modules.incidents.models import Incident, IncidentUpdate
from app.modules.incidents.repository import IncidentRepository, from_point, to_point
from app.modules.incidents.schemas import IncidentCreate, IncidentResponse, Location

logger = logging.getLogger("idrm.incidents")


def _now() -> datetime:
    return datetime.now(UTC)


def to_response(incident: Incident) -> IncidentResponse:
    """Map an ORM incident to its API shape (converting the PostGIS point to lat/lng)."""
    latitude, longitude = from_point(incident.location)
    return IncidentResponse(
        id=incident.id,
        service_type=incident.service_type,
        priority=incident.priority,
        status=incident.status,
        description=incident.description,
        location=Location(latitude=latitude, longitude=longitude),
        requester_id=incident.requester_id,
        assigned_organization_id=incident.assigned_organization_id,
        rating=incident.rating,
        tracking_token=incident.tracking_token,
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        verified_at=incident.verified_at,
    )


class IncidentService:
    """Capture and progress help requests through their lifecycle."""

    def __init__(self, repo: IncidentRepository) -> None:
        self.repo = repo

    async def create(self, data: IncidentCreate, requester_id: uuid.UUID | None) -> Incident:
        """Create a help request. A guest (``requester_id`` None) gets a tracking token (AC-1.4)."""
        incident = Incident(
            service_type=data.service_type,
            priority=data.priority,
            description=data.description,
            location=to_point(data.location.latitude, data.location.longitude),
            requester_id=requester_id,
            guest_contact=data.guest_contact,
            tracking_token=None if requester_id else secrets.token_urlsafe(24),
            status=IncidentStatus.created,
        )
        await self.repo.add(incident)
        await self.repo.add_update(
            IncidentUpdate(
                incident_id=incident.id,
                from_status=None,
                to_status=IncidentStatus.created,
                actor_id=requester_id,
                note="created",
            )
        )
        logger.info(
            "incident.create",
            extra={
                "extra_fields": {"incident_id": str(incident.id), "priority": data.priority.value}
            },
        )
        return incident

    async def get(self, incident_id: uuid.UUID) -> Incident:
        """Return the incident by id, or raise 404 ``not_found`` if it does not exist."""
        incident = await self.repo.get(incident_id)
        if incident is None:
            raise AppError(404, "not_found", "Incident not found.")
        return incident

    async def list_incidents(
        self,
        role: str,
        user_id: uuid.UUID | None,
        page: int,
        limit: int,
        status: IncidentStatus | None = None,
        service_type: ServiceType | None = None,
    ) -> tuple[list[Incident], int]:
        """Role-scoped list: citizen -> own; coordinator/admin -> all (AC-3, doc 22 §3.2)."""
        requester = user_id if role == "citizen" else None
        return await self.repo.list(
            limit=limit,
            offset=(page - 1) * limit,
            status=status,
            service_type=service_type,
            requester_id=requester,
        )

    async def list_mine(
        self, user_id: uuid.UUID, page: int, limit: int
    ) -> tuple[list[Incident], int]:
        """A citizen's own help requests, paginated (AC-7.1)."""
        return await self.repo.list(limit=limit, offset=(page - 1) * limit, requester_id=user_id)

    async def list_assigned(
        self, organization_id: uuid.UUID, page: int, limit: int
    ) -> tuple[list[Incident], int]:
        """Requests currently assigned to a provider's organization (their work queue)."""
        return await self.repo.list(
            limit=limit, offset=(page - 1) * limit, assigned_organization_id=organization_id
        )

    async def nearby(
        self, latitude: float, longitude: float, radius_km: float, service_type: ServiceType | None
    ) -> list[Incident]:
        """Open, unassigned requests within ``radius_km`` of a point, nearest first (AC-4.1)."""
        return await self.repo.nearby(latitude, longitude, radius_km, service_type)

    async def updates(self, incident_id: uuid.UUID) -> list[IncidentUpdate]:
        """Return an incident's status timeline (404 first if the incident is missing)."""
        await self.get(incident_id)  # 404 if missing
        return await self.repo.updates_for(incident_id)

    async def patch(
        self,
        incident: Incident,
        actor_id: uuid.UUID,
        role: str,
        description: str | None,
        priority: Priority | None,
    ) -> Incident:
        """Edit description/priority — only before the request is accepted (AC-5.3)."""
        if incident.status not in {IncidentStatus.created, IncidentStatus.approved}:
            raise AppError(403, "cannot_modify", "This request can no longer be edited.")
        if role == "citizen" and incident.requester_id != actor_id:
            raise AppError(403, "forbidden", "You can only edit your own request.")
        if description is not None:
            incident.description = description
        if priority is not None:
            incident.priority = priority
        return incident

    async def perform_transition(
        self,
        incident: Incident,
        action: str,
        actor_id: uuid.UUID,
        actor_role: str,
        *,
        organization_id: uuid.UUID | None = None,
        actor_organization_id: uuid.UUID | None = None,
        reason: str | None = None,
        note: str | None = None,
        rating: int | None = None,
        review: str | None = None,
    ) -> Incident:
        """Validate + apply one lifecycle transition, writing a timeline entry.

        ``organization_id`` is the org being assigned (accept = the provider's own, resolved by the
        router; assign = a coordinator's choice). ``actor_organization_id`` is the provider's own
        org, used to enforce that only the *assigned* provider may ``start``/``complete``.
        """
        if not role_allowed(action, actor_role):
            raise AppError(403, "forbidden", "Your role cannot perform this action.")
        # single-claim: a second accept/assign on an already-claimed request
        if action in {"accept", "assign"} and incident.status == IncidentStatus.accepted:
            raise AppError(
                409, "already_accepted", "This request was already accepted by another provider."
            )
        if not can_transition(action, incident.status):
            raise AppError(
                409, "invalid_transition", f"Cannot '{action}' from '{incident.status.value}'."
            )
        # critical requests must be coordinator-approved before a provider may claim them (doc 11)
        if (
            action in {"accept", "assign"}
            and incident.priority == Priority.critical
            and incident.status == IncidentStatus.created
        ):
            raise AppError(
                409, "invalid_transition", "Critical requests require coordinator approval first."
            )
        # citizen ownership on the actions they own
        if (
            actor_role == "citizen"
            and action in {"verify", "cancel"}
            and incident.requester_id != actor_id
        ):
            raise AppError(403, "forbidden", "You can only act on your own request.")
        # org membership: only the ASSIGNED provider may progress the work
        if (
            actor_role == "provider"
            and action in {"start", "complete"}
            and incident.assigned_organization_id != actor_organization_id
        ):
            raise AppError(403, "not_assigned", "This request is assigned to another provider.")

        from_status = incident.status
        incident.status = next_status(action)
        if action == "approve":
            incident.approved_by = actor_id
        elif action == "reject":
            incident.rejection_reason = reason
        elif action in {"accept", "assign"}:
            incident.assigned_organization_id = organization_id
        elif action == "cancel":
            incident.cancellation_reason = reason
        elif action == "verify":
            incident.rating = rating
            incident.review = review
            incident.verified_at = _now()

        await self.repo.add_update(
            IncidentUpdate(
                incident_id=incident.id,
                from_status=from_status,
                to_status=incident.status,
                actor_id=actor_id,
                note=note or reason,
            )
        )
        logger.info(
            "incident.transition",
            extra={
                "extra_fields": {
                    "incident_id": str(incident.id),
                    "action": action,
                    "to": incident.status.value,
                }
            },
        )
        return incident
