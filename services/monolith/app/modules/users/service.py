"""Users module service — the business rules for identity, sessions, and access.

No HTTP, no raw SQL (roadmap §5.2). Enforces the locked auth policy: RS256 access + rotating
refresh tokens, bcrypt-12 hashing, and a 5-fail / 15-minute lockout (roadmap §8; doc 22 §2).
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta

from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.modules.users.models import (
    EmailVerificationToken,
    PasswordResetToken,
    User,
    UserRole,
    UserSession,
    UserStatus,
)
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import RegisterRequest, UpdateProfileRequest

logger = logging.getLogger("idrm.users")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15
# Self-service registration may only create these roles; the rest are admin-assigned.
SELF_SERVICE_ROLES = {UserRole.citizen, UserRole.provider}


def _now() -> datetime:
    return datetime.now(UTC)


class UserService:
    """Identity & access operations, orchestrating the repository + security helpers."""

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    # --- registration & verification ---
    async def register(self, data: RegisterRequest) -> User:
        """Create a pending account and issue an email-verification token (AC-1.1)."""
        if data.role not in SELF_SERVICE_ROLES:
            raise AppError(403, "forbidden", "That role cannot be self-registered.")
        if await self.repo.get_by_email(data.email):
            raise AppError(409, "email_exists", "An account with this email already exists.")
        user = User(
            email=data.email,
            password_hash=hash_password(data.password),
            name=data.name,
            phone=data.phone,
            role=data.role,
            status=UserStatus.pending,
        )
        await self.repo.add(user)
        token = await self._issue_email_token(user.id)
        # Email delivery is a notification-module seam; for now, record the intent.
        logger.info(
            "user.register",
            extra={"extra_fields": {"user_id": str(user.id), "role": user.role.value}},
        )
        logger.info(
            "email.verification.send",
            extra={"extra_fields": {"user_id": str(user.id), "token": token.token}},
        )
        return user

    async def _issue_email_token(self, user_id: uuid.UUID) -> EmailVerificationToken:
        """Create and persist a fresh 24-hour email-verification token for a user."""
        token = EmailVerificationToken(
            user_id=user_id,
            token=secrets.token_urlsafe(32),
            expires_at=_now() + timedelta(hours=24),
        )
        return await self.repo.add_email_token(token)

    async def verify_email(self, token_value: str) -> None:
        """Activate an account from its emailed token (AC-1.2)."""
        token = await self.repo.get_email_token(token_value)
        if token is None or token.verified_at is not None:
            raise AppError(
                410, "token_expired", "This verification link is invalid or already used."
            )
        if token.expires_at < _now():
            raise AppError(410, "token_expired", "This verification link has expired.")
        user = await self.repo.get_by_id(token.user_id)
        if user is None:
            raise AppError(404, "not_found", "Account not found.")
        user.email_verified = True
        user.status = UserStatus.active
        token.verified_at = _now()

    async def resend_verification(self, email: str) -> None:
        """Re-issue a verification token for a still-pending account (quiet if none)."""
        user = await self.repo.get_by_email(email)
        if user is None or user.email_verified:
            return
        token = await self._issue_email_token(user.id)
        logger.info(
            "email.verification.resend",
            extra={"extra_fields": {"user_id": str(user.id), "token": token.token}},
        )

    # --- login / lockout / sessions ---
    async def login(
        self, email: str, password: str, ip: str | None, user_agent: str | None
    ) -> tuple[str, User]:
        """Authenticate and return (refresh_token, user); access token issued by the caller.

        Enforces the 5-fail / 15-minute lockout (AC-1.3). Returns a generic error on bad
        credentials so we never reveal whether an email exists.
        """
        user = await self.repo.get_by_email(email)
        if user is None:
            raise AppError(401, "invalid_credentials", "Incorrect email or password.")
        if user.locked_until and user.locked_until > _now():
            raise AppError(403, "account_locked", "Account temporarily locked. Try again later.")
        if user.status != UserStatus.active:
            raise AppError(403, "forbidden", "Account is not active.")
        if not verify_password(password, user.password_hash):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = _now() + timedelta(minutes=LOCKOUT_MINUTES)
                logger.warning("auth.lockout", extra={"extra_fields": {"user_id": str(user.id)}})
            # Persist the failed attempt NOW — otherwise the 401 below rolls it back and the
            # lockout counter would never accumulate.
            await self.repo.commit()
            raise AppError(401, "invalid_credentials", "Incorrect email or password.")
        # success — reset counters, stamp login, open a session
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = _now()
        refresh_token = await self._open_session(user.id, ip, user_agent)
        logger.info("user.login", extra={"extra_fields": {"user_id": str(user.id)}})
        return refresh_token, user

    async def _open_session(
        self, user_id: uuid.UUID, ip: str | None, user_agent: str | None
    ) -> str:
        """Create a persisted refresh-token session and return the new refresh token."""
        refresh_token = secrets.token_urlsafe(48)
        session = UserSession(
            user_id=user_id,
            refresh_token=refresh_token,
            expires_at=_now() + timedelta(days=get_settings().refresh_token_ttl_days),
            ip_address=ip,
            user_agent=user_agent,
        )
        await self.repo.add_session(session)
        return refresh_token

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        """Rotate a refresh token and mint a new access token (returns (access, new_refresh))."""
        session = await self.repo.get_session_by_token(refresh_token)
        if session is None or session.expires_at < _now():
            raise AppError(401, "unauthorized", "Invalid or expired refresh token.")
        user = await self.repo.get_by_id(session.user_id)
        if user is None:
            raise AppError(401, "unauthorized", "Account not found.")
        # rotate: retire the old session, open a new one
        await self.repo.delete_session(session)
        new_refresh = await self._open_session(user.id, session.ip_address, session.user_agent)
        access = create_access_token(str(user.id), user.role.value)
        return access, new_refresh

    async def logout(self, refresh_token: str) -> None:
        """Revoke a session (idempotent — logging out an unknown token is a no-op)."""
        session = await self.repo.get_session_by_token(refresh_token)
        if session is not None:
            await self.repo.delete_session(session)

    # --- passwords ---
    async def forgot_password(self, email: str) -> None:
        """Issue a reset token if the account exists (always returns quietly)."""
        user = await self.repo.get_by_email(email)
        if user is None:
            return
        token = PasswordResetToken(
            user_id=user.id, token=secrets.token_urlsafe(32), expires_at=_now() + timedelta(hours=1)
        )
        await self.repo.add_reset_token(token)
        logger.info(
            "password.reset.send",
            extra={"extra_fields": {"user_id": str(user.id), "token": token.token}},
        )

    async def reset_password(self, token_value: str, new_password: str) -> None:
        """Reset a password from its token and invalidate all existing sessions."""
        token = await self.repo.get_reset_token(token_value)
        if token is None or token.used_at is not None or token.expires_at < _now():
            raise AppError(410, "token_expired", "This reset link is invalid or expired.")
        user = await self.repo.get_by_id(token.user_id)
        if user is None:
            raise AppError(404, "not_found", "Account not found.")
        user.password_hash = hash_password(new_password)
        await self.repo.touch_used(token, _now())
        await self.repo.delete_sessions_for_user(user.id)

    async def change_password(self, user: User, current: str, new_password: str) -> None:
        """Change a password while logged in (verifies the current one first)."""
        if not verify_password(current, user.password_hash):
            raise AppError(401, "invalid_credentials", "Current password is incorrect.")
        user.password_hash = hash_password(new_password)

    # --- profile & admin ---
    async def update_profile(self, user: User, data: UpdateProfileRequest) -> User:
        """Update the caller's own name / phone / language (never email or role)."""
        if data.name is not None:
            user.name = data.name
        if data.phone is not None:
            user.phone = data.phone
        if data.language is not None:
            user.language = data.language
        return user

    async def list_users(self, page: int, limit: int) -> tuple[list[User], int]:
        """A page of users plus the total count (coordinator/admin use)."""
        return await self.repo.list_users(limit=limit, offset=(page - 1) * limit)

    async def get_user(self, user_id: uuid.UUID) -> User:
        """Return a user by id, or raise 404 ``not_found``."""
        user = await self.repo.get_by_id(user_id)
        if user is None:
            raise AppError(404, "not_found", "User not found.")
        return user

    async def admin_update_user(
        self, user_id: uuid.UUID, role: UserRole | None, status: UserStatus | None
    ) -> User:
        """Admin-only change of a user's role/status (audited by the audit module)."""
        user = await self.get_user(user_id)
        if role is not None:
            user.role = role
        if status is not None:
            user.status = status
        logger.info(
            "admin.user.update",
            extra={
                "extra_fields": {
                    "user_id": str(user_id),
                    "role": user.role.value,
                    "status": user.status.value,
                }
            },
        )
        return user
