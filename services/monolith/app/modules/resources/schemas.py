"""Resources module Pydantic schemas — the ``/organizations`` + ``/resources`` contract (doc 40).

A local :class:`GeoPoint` mirrors the incidents module's ``Location`` so the schema layer stays
independent of other modules (the two are intentionally identical lat/lng pairs).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.incidents.lifecycle import ServiceType
from app.modules.resources.models import OrgType


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


# --------------------------------------------------------------------------- organizations
class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    type: OrgType
    service_categories: list[ServiceType] = Field(default_factory=list)
    service_area_center: GeoPoint | None = None
    service_radius_km: float = Field(default=10.0, gt=0, le=500)
    capacity: int = Field(default=0, ge=0)
    contact_phone: str | None = Field(default=None, max_length=20)


class OrganizationUpdate(BaseModel):
    """Partial edit of an org's own details (owner) or moderation fields (coordinator)."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: OrgType | None = None
    service_categories: list[ServiceType] | None = None
    service_area_center: GeoPoint | None = None
    service_radius_km: float | None = Field(default=None, gt=0, le=500)
    contact_phone: str | None = Field(default=None, max_length=20)


class CapacityRequest(BaseModel):
    """Set how many concurrent requests the provider can take on (F4/AC-4.5)."""

    capacity: int = Field(ge=0)
    available_capacity: int | None = Field(default=None, ge=0)


class AvailabilityRequest(BaseModel):
    is_available: bool


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    type: OrgType
    owner_user_id: uuid.UUID
    service_categories: list[ServiceType]
    service_area_center: GeoPoint | None
    service_radius_km: float
    capacity: int
    available_capacity: int
    is_available: bool
    is_verified: bool
    rating: float | None
    total_requests_completed: int
    contact_phone: str | None
    created_at: datetime
    updated_at: datetime


# --------------------------------------------------------------------------- resources
class ResourceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    kind: str = Field(min_length=1, max_length=50)
    quantity: int = Field(default=1, ge=0)
    location: GeoPoint | None = None
    is_available: bool = True


class ResourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    kind: str | None = Field(default=None, min_length=1, max_length=50)
    quantity: int | None = Field(default=None, ge=0)
    location: GeoPoint | None = None
    is_available: bool | None = None


class ResourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    kind: str
    quantity: int
    location: GeoPoint | None
    is_available: bool
    created_at: datetime
    updated_at: datetime
