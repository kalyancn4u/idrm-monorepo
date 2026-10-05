"""Notifications module repository — per-user messages and channel preferences."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.notifications.models import Notification, NotificationPreference


class NotificationRepository:
    """Async data access for notifications and preferences."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, notification: Notification) -> Notification:
        """Persist one notification (flush) and return it."""
        self.session.add(notification)
        await self.session.flush()
        return notification

    async def get(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification | None:
        """Fetch one of the user's own (not-deleted) notifications."""
        result = await self.session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: uuid.UUID, limit: int, offset: int, unread_only: bool = False
    ) -> tuple[list[Notification], int]:
        """A user's notifications (newest first), optionally unread-only; page + total count."""
        stmt = select(Notification).where(
            Notification.user_id == user_id, Notification.deleted_at.is_(None)
        )
        if unread_only:
            stmt = stmt.where(Notification.is_read.is_(False))
        total = len((await self.session.execute(stmt)).scalars().all())
        paged = stmt.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(paged)).scalars().all()
        return list(rows), total

    async def unread_count(self, user_id: uuid.UUID) -> int:
        """Number of the user's unread, not-deleted notifications (for the badge)."""
        stmt = select(func.count()).select_from(Notification).where(
            Notification.user_id == user_id,
            Notification.deleted_at.is_(None),
            Notification.is_read.is_(False),
        )
        return int((await self.session.execute(stmt)).scalar_one())

    async def mark_all_read(self, user_id: uuid.UUID) -> int:
        """Mark every unread notification for the user as read; return how many changed."""
        result = await self.session.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None),
                Notification.is_read.is_(False),
            )
            .values(is_read=True)
        )
        return int(result.rowcount or 0)

    # --- preferences ---
    async def get_preferences(self, user_id: uuid.UUID) -> NotificationPreference | None:
        """Fetch the user's channel preferences row, or ``None`` if not yet created."""
        result = await self.session.execute(
            select(NotificationPreference).where(NotificationPreference.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def add_preferences(self, prefs: NotificationPreference) -> NotificationPreference:
        """Persist a new channel-preferences row (flush) and return it."""
        self.session.add(prefs)
        await self.session.flush()
        return prefs
