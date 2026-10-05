"""Users module Pydantic schemas — the request/response shapes of the ``/auth`` & ``/users`` API.

Field names are snake_case; these are the wire contract (roadmap §4.2; doc 40 §5.1).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.modules.users.models import UserRole, UserStatus

# Self-registration is limited to these roles; coordinator/admin are created by an admin.
SelfRegisterRole = UserRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    name: str = Field(min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    role: UserRole = UserRole.citizen


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyEmailRequest(BaseModel):
    token: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)


class UpdateProfileRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, max_length=20)
    language: str | None = Field(default=None, max_length=5)


class AdminUpdateUserRequest(BaseModel):
    role: UserRole | None = None
    status: UserStatus | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    name: str
    phone: str | None
    role: UserRole
    status: UserStatus
    email_verified: bool
    language: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MessageResponse(BaseModel):
    message: str
