"""
services/notification_service.py — notifications (Module M5).

Two responsibilities:
  • Serve the signed-in user's notifications (`list_for_user`, `mark_read`) for
    GET /notifications and POST /notifications/{id}/read.
  • Provide a reusable `create_notification` that other modules (e.g. the service
    lifecycle in M3) call to notify a user, plus `publish_notification` to push it
    to Redis for real-time delivery (the gateway/G4 fans it out over WebSocket).

Shape mapping: the API uses {id, type, title, message, read, created_at}; we map
the DB columns `subject`→title, `body`→message and `status`→read in `_to_out`.

Persistence vs. realtime: a notification row is the source of truth (the user sees
it via GET /notifications even if they were offline). The Redis publish is an
extra, best-effort live push — see core.redis.
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.redis import CHANNEL_NOTIFICATIONS, publish_json
from dbmodels.notification import Notification
from dbmodels.user import User
from schemas.notification import NotificationData, NotificationListResponse, NotificationOut


def _naive_utcnow() -> datetime:
    """Current UTC time as a naive datetime (the timestamp columns are tz-naive)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _to_out(notification: Notification) -> NotificationOut:
    """Map a Notification row to the documented API shape."""
    return NotificationOut(
        id=notification.notification_id,
        type=notification.type,
        title=notification.subject,
        message=notification.body,
        read=(notification.status == "READ"),
        created_at=notification.created_at,
        related_service_id=notification.related_service_id,
    )


async def create_notification(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    type: str,
    body: str,
    subject: str | None = None,
    channel: str = "IN_APP",
    related_service_id: uuid.UUID | None = None,
    related_org_id: uuid.UUID | None = None,
) -> Notification:
    """Insert a notification for a user and return it.

    Flushes (to assign the id) but does NOT commit — the notification therefore
    shares the caller's transaction, so it's saved atomically with whatever event
    triggered it (e.g. a service status change). The caller commits, then may call
    `publish_notification` for the live push.

    In-app notifications are created already `SENT` (with `sent_at`/`created_at` set)
    so they appear immediately as unread and can later be marked `READ` — the DB
    requires `sent_at` to precede `read_at`.
    """
    now = _naive_utcnow()
    notification = Notification(
        user_id=user_id,
        type=type,
        channel=channel,
        subject=subject,
        body=body,
        related_service_id=related_service_id,
        related_org_id=related_org_id,
        status="SENT",
        sent_at=now,
        created_at=now,
    )
    db.add(notification)
    await db.flush()  # assign notification_id without committing
    return notification


async def publish_notification(notification: Notification) -> None:
    """Best-effort live push of a freshly-created notification to Redis (for the
    gateway to fan out over WebSocket). Call AFTER the transaction has committed."""
    await publish_json(
        CHANNEL_NOTIFICATIONS,
        {
            "user_id": str(notification.user_id),
            "notification": _to_out(notification).model_dump(mode="json"),
        },
    )


async def list_for_user(db: AsyncSession, user: User) -> NotificationListResponse:
    """All of `user`'s notifications (newest first) plus a count of unread ones."""
    rows = (
        await db.scalars(
            select(Notification)
            .where(Notification.user_id == user.user_id)
            .order_by(Notification.created_at.desc())
        )
    ).all()
    unread_count = await db.scalar(
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == user.user_id, Notification.status != "READ")
    ) or 0
    return NotificationListResponse(
        data=NotificationData(items=[_to_out(n) for n in rows], unread_count=unread_count)
    )


async def mark_read(db: AsyncSession, user: User, notification_id: uuid.UUID) -> NotificationOut:
    """Mark one of `user`'s notifications READ. 404 if it isn't theirs."""
    notification = await db.scalar(
        select(Notification).where(
            Notification.notification_id == notification_id,
            Notification.user_id == user.user_id,
        )
    )
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notification.status != "READ":
        now = _naive_utcnow()
        if notification.sent_at is None:  # satisfy the DB's sent_before_read CHECK
            notification.sent_at = now
        notification.read_at = now
        notification.status = "READ"
        await db.commit()
    return _to_out(notification)
