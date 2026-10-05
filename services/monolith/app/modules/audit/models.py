"""Audit module ORM model — the append-only accountability record (doc 50 §5.10).

**Append-only:** rows are only ever inserted and read, never updated or deleted (PICS-AUD-002). The
service exposes a ``record`` write and the router exposes only a read, so there is no code path that
mutates a past entry. ``actor_id`` is NULL for system-originated actions; ``old_values`` /
``new_values`` hold optional before/after JSON snapshots.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, UUIDPrimaryKey


class AuditLog(UUIDPrimaryKey, Base):
    """One recorded action (doc 50 §5.10). No ``updated_at`` / ``deleted_at`` — append-only."""

    __tablename__ = "audit_logs"

    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), index=True
    )  # NULL = system action
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    resource_type: Mapped[str | None] = mapped_column(String(50), index=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(PgUUID(as_uuid=True), index=True)
    ip_address: Mapped[str | None] = mapped_column(INET)
    old_values: Mapped[dict | None] = mapped_column(JSONB)
    new_values: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
