"""
services/auth_service.py — authentication business logic (Module M2).

The route handlers in `api/v1/auth.py` / `api/v1/users.py` are thin: they call
these functions, which own the rules (role guards, uniqueness, token issuing,
profile updates). HTTP errors are raised as `HTTPException` so the routes don't
need any error-translation boilerplate.
"""
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import (
    REFRESH_TOKEN,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    unauthorized,
    verify_password,
)
from dbmodels.enums import SELF_REGISTRABLE_ROLES
from dbmodels.user import User
from schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenResponse,
)
from schemas.user import UserOut, UserUpdate


def _default_preferences(language: str) -> dict:
    """The DB's default `preferences` bag, with the chosen language filled in.

    Mirrors the `users.preferences` DEFAULT in `database/init/02-schema.sql`, so a
    freshly-registered user has the same shape as a row created with DB defaults.
    """
    return {
        "language": language,
        "notifications": {"email": True, "sms": True, "push": False},
        "theme": "light",
    }


def _issue_tokens(user: User) -> TokenResponse:
    """Build a TokenResponse (access + refresh + profile) for a verified user."""
    return TokenResponse(
        access_token=create_access_token(user.user_id, user.role),
        refresh_token=create_refresh_token(user.user_id),
        user=UserOut.model_validate(user),
    )


async def register(db: AsyncSession, data: RegisterRequest) -> User:
    """Create a new user account and return the saved row.

    Guards:
      • Role — only CITIZEN/PROVIDER/VOLUNTEER may self-register (403 otherwise);
        elevated roles are granted later by an ADMIN.
      • Uniqueness — email and phone must be free (409 otherwise).
    """
    if data.role not in SELF_REGISTRABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{data.role.value}' cannot be self-assigned; an ADMIN must grant it.",
        )

    # Friendly pre-checks (the DB UNIQUE constraints are the real guard — see below).
    if await db.scalar(select(User).where(User.email == str(data.email))):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if data.phone and await db.scalar(select(User).where(User.phone == data.phone)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already registered")

    user = User(
        email=str(data.email),
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=data.role.value,
        preferences=_default_preferences(data.language_preference.value),
    )
    db.add(user)
    try:
        await db.commit()
    except IntegrityError:
        # Race: another request inserted the same email/phone between our check
        # and this commit. The UNIQUE constraint caught it — report it cleanly.
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or phone already registered")
    await db.refresh(user)  # load DB-generated columns (user_id, created_at, …)
    return user


async def login(db: AsyncSession, data: LoginRequest) -> TokenResponse:
    """Verify email + password and issue an access/refresh token pair.

    Returns the same 401 for "no such email" and "wrong password" so an attacker
    can't probe which accounts exist.
    """
    user = await db.scalar(select(User).where(User.email == str(data.email)))
    if user is None or not verify_password(data.password, user.password_hash):
        raise unauthorized("Incorrect email or password")
    if not user.is_active:
        raise unauthorized("Account is inactive")

    # Best-effort: record the login time. The column is naive (TIMESTAMP without
    # time zone), so store naive UTC to match the schema.
    user.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
    await db.commit()

    return _issue_tokens(user)


async def refresh(db: AsyncSession, data: RefreshRequest) -> RefreshResponse:
    """Validate a refresh token and mint a new short-lived access token."""
    claims = decode_token(data.refresh_token, expected_type=REFRESH_TOKEN)
    try:
        user_id = uuid.UUID(claims.get("sub", ""))
    except ValueError:
        raise unauthorized("Invalid token subject")

    user = await db.scalar(select(User).where(User.user_id == user_id))
    if user is None or not user.is_active:
        raise unauthorized("User not found or inactive")

    return RefreshResponse(access_token=create_access_token(user.user_id, user.role))


async def update_profile(db: AsyncSession, user: User, data: UserUpdate) -> User:
    """Apply a self-service profile update (name, phone, preferences) and save.

    `preferences` is *merged* into the stored JSON so a partial update (e.g. just
    the language) doesn't wipe the user's other settings.
    """
    if data.full_name is not None:
        user.full_name = data.full_name

    if data.phone is not None and data.phone != user.phone:
        clash = await db.scalar(
            select(User).where(User.phone == data.phone, User.user_id != user.user_id)
        )
        if clash:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Phone already in use")
        user.phone = data.phone

    if data.preferences is not None:
        user.preferences = {**(user.preferences or {}), **data.preferences}

    await db.commit()
    await db.refresh(user)
    return user
