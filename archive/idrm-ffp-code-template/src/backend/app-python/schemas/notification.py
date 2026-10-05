"""
schemas/notification.py — notification response shapes (mirrors CLAUDE.md
§Notification APIs).

The API exposes a compact, client-friendly shape — {id, type, title, message,
read, created_at} — which the service layer maps from the DB columns
(`subject`→title, `body`→message, `status`→read). The list is wrapped in a
`{status, data}` envelope.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel

from dbmodels.enums import NotificationType


class NotificationOut(BaseModel):
    """One notification as returned by GET /notifications.

    Built by the service layer (not straight from the ORM): `title` comes from the
    row's `subject`, `message` from `body`, and `read` is `status == 'READ'`.
    """

    id: uuid.UUID
    type: NotificationType
    title: str | None = None
    message: str
    read: bool
    created_at: datetime
    related_service_id: uuid.UUID | None = None  # deep-link target for the UI (if the notification is about a request)


class NotificationData(BaseModel):
    """The list payload: the user's notifications + how many are unread."""

    items: list[NotificationOut]
    unread_count: int


class NotificationListResponse(BaseModel):
    """Envelope for GET /notifications: `{ "status": "success", "data": {...} }`."""

    status: str = "success"
    data: NotificationData
