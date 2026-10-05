"""The declarative base and shared column mixins (roadmap §3.2, §5).

Every table gets a UUID primary key and timezone-aware ``created_at`` / ``updated_at``; most
user-facing tables also get ``deleted_at`` (soft delete — never truly erase history).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


class UUIDPrimaryKey:
    """A random, non-guessable UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class Timestamps:
    """``created_at`` / ``updated_at`` maintained in UTC."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDelete:
    """A nullable ``deleted_at`` stamp; NULL means the row is active."""

    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
