"""Incidents module Pydantic schemas — the ``/incidents`` request/response contract (doc 40)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.incidents.lifecycle import IncidentStatus, Priority, ServiceType


class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class IncidentCreate(BaseModel):
    service_type: ServiceType
    priority: Priority
    description: str = Field(min_length=1)
    location: Location
    guest_contact: str | None = Field(default=None, max_length=20)


class PatchIncidentRequest(BaseModel):
    """Edit allowed only before the request is accepted (AC-5.3)."""

    description: str | None = Field(default=None, min_length=1)
    priority: Priority | None = None


class ApproveRequest(BaseModel):
    note: str | None = None


class RejectRequest(BaseModel):
    reason: str = Field(min_length=1)


class AcceptRequest(BaseModel):
    # The claiming provider's organization is resolved SERVER-SIDE from the authenticated user
    # (their own verified org) — never trusted from the request body.
    eta: str | None = None


class AssignRequest(BaseModel):
    # A coordinator assigns the request to a specific (verified) organization.
    organization_id: uuid.UUID


class CompleteRequest(BaseModel):
    notes: str | None = None
    photos: list[str] | None = None


class VerifyRequest(BaseModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    review: str | None = None


class CancelRequest(BaseModel):
    reason: str = Field(min_length=1)


class IncidentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    service_type: ServiceType
    priority: Priority
    status: IncidentStatus
    description: str
    location: Location
    requester_id: uuid.UUID | None
    assigned_organization_id: uuid.UUID | None
    rating: int | None
    tracking_token: str | None
    created_at: datetime
    updated_at: datetime
    verified_at: datetime | None


class IncidentUpdateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    from_status: IncidentStatus | None
    to_status: IncidentStatus
    actor_id: uuid.UUID | None
    note: str | None
    created_at: datetime
