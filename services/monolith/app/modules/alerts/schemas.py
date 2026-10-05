"""Alerts module Pydantic schemas — the ``/alerts`` request/response contract (doc 40)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.alerts.models import AlertSeverity


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class AlertCreate(BaseModel):
    """Broadcast an area alert. ``area`` is a polygon ring (3+ points); omit for platform-wide."""

    title: str = Field(min_length=1, max_length=255)
    message: str = Field(min_length=1)
    severity: AlertSeverity
    area: list[GeoPoint] | None = Field(default=None, min_length=3)
    expires_at: datetime | None = None


class AlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message: str
    severity: AlertSeverity
    active: bool
    platform_wide: bool
    created_by: uuid.UUID
    expires_at: datetime | None
    created_at: datetime
