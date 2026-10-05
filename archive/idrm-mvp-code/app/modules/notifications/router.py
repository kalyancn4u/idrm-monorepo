"""Notifications module router — ``/notifications`` (per-user messages + prefs; doc 40 §5.4).

Mounted at ``/api/v1/notifications`` by ``app.main``. Static sub-paths (``/unread-count``,
``/read-all``, ``/preferences``) are declared before ``/{notification_id}`` routes so they match.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db
from app.core.rate_limit import rate_limit
from app.modules.notifications.repository import NotificationRepository
from app.modules.notifications.schemas import (
    ChatRequest,
    ChatResponse,
    NotificationResponse,
    PreferenceResponse,
    PreferenceUpdate,
    UnreadCountResponse,
)
from app.modules.notifications.service import NotificationService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]
Claims = Annotated[dict, Depends(get_current_claims)]

# Task L — the MVP FAQ chatbot is a non-intelligent stub: it always returns this fixed
# acknowledgement. Real NLP (an actual assistant) is a Task-M white-paper item → FFP.
_CHATBOT_REPLY = "Your input is noted, we'll try to get back to you shortly, if possible."


def _service(db: DbSession) -> NotificationService:
    return NotificationService(NotificationRepository(db))


@router.get("")
async def list_notifications(
    db: DbSession,
    claims: Claims,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
) -> dict:
    """The current user's notifications (F6), newest first, wrapped with pagination."""
    user_id = uuid.UUID(claims["sub"])
    items, total = await _service(db).list(user_id, page, limit, unread_only)
    return {
        "data": [NotificationResponse.model_validate(n).model_dump(mode="json") for n in items],
        "pagination": {"page": page, "limit": limit, "total": total,
                       "total_pages": (total + limit - 1) // limit},
    }


@router.post("/chat", response_model=ChatResponse,
             dependencies=[Depends(rate_limit("notif_chat", limit=30))])
async def faq_chat(data: ChatRequest, _: Claims) -> ChatResponse:
    """FAQ chatbot **stub** (Task L) — always returns a fixed acknowledgement; no ML in the MVP."""
    return ChatResponse(reply=_CHATBOT_REPLY)


@router.get("/unread-count", response_model=UnreadCountResponse,
            dependencies=[Depends(rate_limit("notif_unread", limit=200))])
async def unread_count(db: DbSession, claims: Claims) -> UnreadCountResponse:
    """The badge count of unread notifications."""
    count = await _service(db).unread_count(uuid.UUID(claims["sub"]))
    return UnreadCountResponse(count=count)


@router.post("/read-all", dependencies=[Depends(rate_limit("notif_read_all", limit=20))])
async def read_all(db: DbSession, claims: Claims) -> dict:
    """Mark every unread notification read."""
    updated = await _service(db).mark_all_read(uuid.UUID(claims["sub"]))
    return {"updated": updated}


@router.get("/preferences", response_model=PreferenceResponse,
            dependencies=[Depends(rate_limit("notif_prefs", limit=50))])
async def get_preferences(db: DbSession, claims: Claims) -> PreferenceResponse:
    """View the user's channel preferences (defaults created on first read)."""
    prefs = await _service(db).get_preferences(uuid.UUID(claims["sub"]))
    return PreferenceResponse.model_validate(prefs)


@router.patch("/preferences", response_model=PreferenceResponse,
              dependencies=[Depends(rate_limit("notif_prefs", limit=50))])
async def set_preferences(
    data: PreferenceUpdate, db: DbSession, claims: Claims
) -> PreferenceResponse:
    """Set which channels (email / sms / in-app) the user wants."""
    prefs = await _service(db).set_preferences(uuid.UUID(claims["sub"]), data)
    return PreferenceResponse.model_validate(prefs)


@router.post("/{notification_id}/read", response_model=NotificationResponse,
             dependencies=[Depends(rate_limit("notif_read", limit=50))])
async def mark_read(
    notification_id: uuid.UUID, db: DbSession, claims: Claims
) -> NotificationResponse:
    """Mark one notification read."""
    notification = await _service(db).mark_read(notification_id, uuid.UUID(claims["sub"]))
    return NotificationResponse.model_validate(notification)


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(rate_limit("notif_delete", limit=30))])
async def delete_notification(
    notification_id: uuid.UUID, db: DbSession, claims: Claims
) -> None:
    """Soft-delete one of the user's notifications."""
    await _service(db).delete(notification_id, uuid.UUID(claims["sub"]))
