"""Notifications module Pydantic schemas — the ``/notifications`` contract (doc 40)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.notifications.models import NotificationType


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    message: str
    type: NotificationType
    is_read: bool
    link: str | None
    created_at: datetime


class UnreadCountResponse(BaseModel):
    count: int


class PreferenceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: bool
    sms: bool
    in_app: bool


class PreferenceUpdate(BaseModel):
    email: bool | None = None
    sms: bool | None = None
    in_app: bool | None = None


class ChatRequest(BaseModel):
    """A message to the FAQ chatbot stub (Task L)."""

    message: str = Field(min_length=1, max_length=2000)


class ChatResponse(BaseModel):
    reply: str
