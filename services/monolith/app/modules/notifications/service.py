"""Notifications module service — generate, read, and manage per-user messages.

:meth:`NotificationService.notify` is the entry point other modules call to raise a notification —
notably the incidents module on every lifecycle change (PICS-NTF-001). Delivery is the in-app pull
model (no broker in the MVP, ADR-012); channel preferences are recorded for the FFP push layer.
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from app.core.exceptions import AppError
from app.modules.notifications.models import (
    Notification,
    NotificationPreference,
    NotificationType,
)
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import PreferenceUpdate

logger = logging.getLogger("idrm.notifications")


class NotificationService:
    """Create and manage notifications; read/update a user's channel preferences."""

    def __init__(self, repo: NotificationRepository) -> None:
        self.repo = repo

    async def notify(
        self,
        user_id: uuid.UUID,
        ntype: NotificationType,
        title: str,
        message: str,
        link: str | None = None,
    ) -> Notification:
        """Raise a notification for a user (called by other modules on domain events)."""
        notification = Notification(
            user_id=user_id, type=ntype, title=title, message=message, link=link
        )
        await self.repo.add(notification)
        logger.info(
            "notification.create",
            extra={"extra_fields": {"user_id": str(user_id), "type": ntype.value}},
        )
        return notification

    async def list(
        self, user_id: uuid.UUID, page: int, limit: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]:
        """A user's notifications, newest first, optionally unread-only, paginated."""
        return await self.repo.list_for_user(
            user_id, limit=limit, offset=(page - 1) * limit, unread_only=unread_only
        )

    async def unread_count(self, user_id: uuid.UUID) -> int:
        """The user's unread-notification count (badge)."""
        return await self.repo.unread_count(user_id)

    async def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        """Mark one of the user's own notifications read (404 if it is not theirs / missing)."""
        notification = await self.repo.get(notification_id, user_id)
        if notification is None:
            raise AppError(404, "not_found", "Notification not found.")
        notification.is_read = True
        return notification

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """Mark all of the user's unread notifications read; return how many changed."""
        return await self.repo.mark_all_read(user_id)

    async def delete(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> None:
        """Soft-delete one of the user's own notifications (404 if it is not theirs / missing)."""
        notification = await self.repo.get(notification_id, user_id)
        if notification is None:
            raise AppError(404, "not_found", "Notification not found.")
        notification.deleted_at = datetime.now(UTC)

    async def get_preferences(self, user_id: uuid.UUID) -> NotificationPreference:
        """Return the user's preferences, creating the default (all channels on) on first read."""
        prefs = await self.repo.get_preferences(user_id)
        if prefs is None:
            prefs = await self.repo.add_preferences(NotificationPreference(user_id=user_id))
        return prefs

    async def set_preferences(
        self, user_id: uuid.UUID, update: PreferenceUpdate
    ) -> NotificationPreference:
        """Update the user's channel preferences (only the provided fields change)."""
        prefs = await self.get_preferences(user_id)
        if update.email is not None:
            prefs.email = update.email
        if update.sms is not None:
            prefs.sms = update.sms
        if update.in_app is not None:
            prefs.in_app = update.in_app
        return prefs
