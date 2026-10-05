"""
schemas/service.py — service-request request/response shapes
(mirrors CLAUDE.md §Service Request APIs + instructions_json_formats_v3.md).

Notes:
  • The ORM stores `location` as a PostGIS WKBElement. The service layer converts
    it to a GeoPoint when building `ServiceOut` — it is not auto-mapped.
  • GET /services returns a `{status, data}` envelope (`ServiceListResponse`).
  • `AcceptBody.org_id` exists because `users` has no organisation link yet; the
    provider states which verified org is accepting (see service_service docstring).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from dbmodels.enums import Priority, PrivacyLevel, ServiceStatus, ServiceType
from schemas.common import GeoPoint, Page

PHONE_PATTERN = r"^\+[1-9]\d{1,14}$"


# ---- Create -----------------------------------------------------------------
class ServiceCreate(BaseModel):
    """Body for POST /services — a citizen filing a new request for help."""

    service_type: ServiceType
    priority: Priority
    description: str = Field(min_length=10, max_length=500)
    location: GeoPoint
    address: str | None = None
    num_people_affected: int = Field(default=1, ge=1, le=1000)
    privacy_level: PrivacyLevel = PrivacyLevel.PROTECTED
    contact_phone: str | None = Field(default=None, pattern=PHONE_PATTERN)


# ---- Nested briefs ----------------------------------------------------------
class RequestorBrief(BaseModel):
    """Minimal requestor info embedded in a ServiceOut (omitted entirely by the
    service layer when the viewer may not see a PROTECTED/PRIVATE requestor)."""

    model_config = ConfigDict(from_attributes=True)
    user_id: uuid.UUID
    full_name: str
    phone: str | None = None


class ProviderBrief(BaseModel):
    """Minimal provider-organization info embedded in a ServiceOut."""

    model_config = ConfigDict(from_attributes=True)
    org_id: uuid.UUID
    name: str
    contact_phone: str | None = None


# ---- Read -------------------------------------------------------------------
class ServiceOut(BaseModel):
    """Full view of one service request (GET /services/{id})."""

    model_config = ConfigDict(from_attributes=True)
    service_id: uuid.UUID
    service_type: ServiceType
    priority: Priority
    status: ServiceStatus
    location: GeoPoint | None = None   # populated by the service layer (see module docstring)
    address: str | None = None
    description: str
    num_people_affected: int
    privacy_level: PrivacyLevel
    contact_phone: str | None = None
    created_at: datetime
    accepted_at: datetime | None = None
    completed_at: datetime | None = None
    verified_at: datetime | None = None
    rating: int | None = None
    feedback: str | None = None
    requestor: RequestorBrief | None = None
    provider: ProviderBrief | None = None


class ServiceListItem(BaseModel):
    """Compact row for the paginated list (GET /services)."""

    model_config = ConfigDict(from_attributes=True)
    service_id: uuid.UUID
    service_type: ServiceType
    priority: Priority
    status: ServiceStatus
    address: str | None = None
    created_at: datetime


class ServiceListResponse(BaseModel):
    """Envelope for GET /services: `{ "status": "success", "data": <paginated list> }`."""

    status: str = "success"
    data: Page[ServiceListItem]


# ---- Action bodies (POST /services/{id}/<action>) ---------------------------
class ApproveBody(BaseModel):
    """Body for POST /services/{id}/approve (DM Authority approves a SUBMITTED request).
    `notes` has no DB column yet — the approval is captured in the audit trail."""

    notes: str | None = None


class AcceptBody(BaseModel):
    """Body for POST /services/{id}/accept (Provider takes on an APPROVED request).

    `org_id` is the verified organisation accepting the request. It lives in the
    body because `users` has no organisation link yet — when a membership model
    lands, derive the org from the acting user and drop this field. `estimated_arrival`
    has no DB column yet, so it is accepted but not persisted.
    """

    org_id: uuid.UUID
    estimated_arrival: datetime | None = None
    notes: str | None = None


class CompleteBody(BaseModel):
    """Body for POST /services/{id}/complete (Provider marks the service done)."""

    notes: str | None = None


class VerifyBody(BaseModel):
    """Body for POST /services/{id}/verify (Requestor confirms completion). Rating 1–5
    is required; feedback is optional."""

    rating: int = Field(ge=1, le=5)
    feedback: str | None = None


class CancelBody(BaseModel):
    """Body for POST /services/{id}/cancel (Requestor; allowed only while SUBMITTED/APPROVED).
    `reason` has no DB column yet — it is captured in the audit trail."""

    reason: str | None = None


class RejectBody(BaseModel):
    """Body for POST /services/{id}/reject (DM Authority rejects a SUBMITTED/DISPUTED request)."""

    reason: str = Field(min_length=3)


class DisputeBody(BaseModel):
    """Body for POST /services/{id}/dispute (raised from IN_PROGRESS/COMPLETED).
    `reason` has no DB column yet — it is captured in the audit trail."""

    reason: str = Field(min_length=3)
