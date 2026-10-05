"""Notifications module ORM models — per-user messages and channel preferences (doc 50 §5.8).

A notification is a row the client pulls (``GET /notifications``); there is no broker in the MVP
(ADR-012). ``link`` points back at the source (e.g. ``/incidents/{id}``) so a notification is
traceable (PICS-NTF-003). Preferences record which channels a user wants (email / sms / in-app).
"""

from __future__ import annotations

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base, SoftDelete, UUIDPrimaryKey


class NotificationType(str, enum.Enum):
    incident_update = "incident_update"
    assignment = "assignment"
    alert = "alert"
    verification = "verification"
    system = "system"


notification_type_enum = SAEnum(NotificationType, name="notification_type")


class Notification(UUIDPrimaryKey, SoftDelete, Base):
    """One message for one user (doc 50 §5.8)."""

    __tablename__ = "notifications"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[NotificationType] = mapped_column(notification_type_enum, nullable=False)
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false", index=True
    )
    link: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class NotificationPreference(UUIDPrimaryKey, Base):
    """A user's channel choices; one row per user (doc 50 §5.8)."""

    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True
    )
    email: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    sms: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    in_app: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
