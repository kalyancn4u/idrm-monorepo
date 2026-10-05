"""
schemas/auth.py — authentication request/response shapes
(mirrors CLAUDE.md §Authentication APIs).
"""
from pydantic import BaseModel, EmailStr, Field

from dbmodels.enums import Language, UserRole
from schemas.user import UserOut

PHONE_PATTERN = r"^\+[1-9]\d{1,14}$"


class RegisterRequest(BaseModel):
    """Body for POST /auth/register (self-service signup)."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=2, max_length=255)
    phone: str | None = Field(default=None, pattern=PHONE_PATTERN)
    # Only CITIZEN / PROVIDER / VOLUNTEER are self-registrable — enforced in the
    # auth service against enums.SELF_REGISTRABLE_ROLES (others are admin-granted).
    role: UserRole = UserRole.CITIZEN
    language_preference: Language = Language.EN


class LoginRequest(BaseModel):
    """Body for POST /auth/login (email + password)."""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Response for register/login: the token pair plus the signed-in user's profile."""

    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int = 900  # 15 minutes, in seconds
    user: UserOut


class RefreshRequest(BaseModel):
    """Body for POST /auth/refresh (exchange a valid refresh token)."""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response for POST /auth/refresh: a fresh short-lived access token."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int = 900
