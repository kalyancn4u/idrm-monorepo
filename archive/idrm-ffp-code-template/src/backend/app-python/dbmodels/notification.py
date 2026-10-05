"""
dbmodels/notification.py — the `notifications` table.
Mirrors 02-schema.sql §notifications.
"""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from dbmodels.base import Base


class Notification(Base):
    """One message to a user about an event (e.g. their request was accepted),
    delivered over a channel (in-app, email, SMS, push)."""

    __tablename__ = "notifications"

    notification_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    type: Mapped[str] = mapped_column(String(50), nullable=False)      # enums.NotificationType
    channel: Mapped[str] = mapped_column(String(20), nullable=False)   # enums.NotificationChannel

    subject: Mapped[str | None] = mapped_column(String(255))           # required for EMAIL (DB CHECK)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    related_service_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("service_requests.service_id", ondelete="CASCADE")
    )
    related_org_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("organizations.org_id", ondelete="SET NULL")
    )

    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="PENDING")
    sent_at: Mapped[datetime | None] = mapped_column(DateTime)
    read_at: Mapped[datetime | None] = mapped_column(DateTime)
    error_message: Mapped[str | None] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))

    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Notification {self.type}/{self.channel} [{self.status}]>"
