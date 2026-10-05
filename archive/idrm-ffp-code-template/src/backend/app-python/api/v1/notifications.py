"""
api/v1/notifications.py — notification routes (Module M5).

GET /notifications — the signed-in user's list + unread count.
POST /notifications/{id}/read — mark one notification read.
Both require authentication. Thin handlers delegate to
`services.notification_service`. Mounted under `/api/v1`.
"""
import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from dbmodels.user import User
from schemas.notification import NotificationListResponse, NotificationOut
from services import notification_service

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=NotificationListResponse)
async def list_notifications(
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationListResponse:
    """The signed-in user's notifications (newest first) plus an unread count."""
    return await notification_service.list_for_user(db, current)


@router.post("/{notification_id}/read", response_model=NotificationOut)
async def mark_notification_read(
    notification_id: uuid.UUID,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> NotificationOut:
    """Mark one of the signed-in user's notifications as read."""
    return await notification_service.mark_read(db, current, notification_id)
