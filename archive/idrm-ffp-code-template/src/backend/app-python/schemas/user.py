"""
schemas/user.py — user request/response shapes.
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from dbmodels.enums import UserRole

# E.164 phone, e.g. +919876543210
PHONE_PATTERN = r"^\+[1-9]\d{1,14}$"


class UserOut(BaseModel):
    """Safe public view of a user — never includes password_hash.

    The API exposes the primary key as `id` (per CLAUDE.md), but the ORM/DB column
    is `user_id`. The `validation_alias` makes Pydantic read `user_id` off the ORM
    object while the JSON field stays `id`.
    """

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: uuid.UUID = Field(validation_alias="user_id")
    email: EmailStr
    full_name: str
    phone: str | None = None
    role: UserRole
    is_verified: bool
    preferences: dict = {}
    created_at: datetime


class UserUpdate(BaseModel):
    """Fields a user may change on their own profile via POST /users/me.

    `preferences` is merged into the stored JSON (e.g. {"language": "hi"}); email
    and role cannot be changed here.
    """

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    preferences: dict | None = None
