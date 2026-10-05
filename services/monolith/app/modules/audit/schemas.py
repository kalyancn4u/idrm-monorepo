"""Audit module Pydantic schemas — the read-only ``/audit-logs`` response (doc 40 §5.4)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    resource_type: str | None
    resource_id: uuid.UUID | None
    ip_address: str | None
    old_values: dict[str, Any] | None
    new_values: dict[str, Any] | None
    created_at: datetime
