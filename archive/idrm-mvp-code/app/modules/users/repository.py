"""Users module repository — the only layer that touches the database (roadmap §5.2)."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import (
    EmailVerificationToken,
    PasswordResetToken,
    User,
    UserSession,
)


class UserRepository:
    """Async data access for accounts, sessions, and tokens."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def commit(self) -> None:
        """Persist pending changes immediately (used to record failed-login attempts)."""
        await self.session.commit()

    # --- users ---
    async def get_by_email(self, email: str) -> User | None:
        """Return the active (not soft-deleted) user with this email, or None."""
        result = await self.session.execute(
            select(User).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Return the active user with this id, or None."""
        result = await self.session.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def add(self, user: User) -> User:
        """Persist a new user (flushed so its id is available)."""
        self.session.add(user)
        await self.session.flush()
        return user

    async def list_users(self, limit: int, offset: int) -> tuple[list[User], int]:
        """Return a page of users plus the total count (admin/coordinator use)."""
        base = select(User).where(User.deleted_at.is_(None))
        total = len((await self.session.execute(base)).scalars().all())
        paged = base.order_by(User.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(paged)).scalars().all()
        return list(rows), total

    # --- sessions ---
    async def add_session(self, session_row: UserSession) -> UserSession:
        """Persist a new refresh-token session (flush) and return it."""
        self.session.add(session_row)
        await self.session.flush()
        return session_row

    async def get_session_by_token(self, refresh_token: str) -> UserSession | None:
        """Look up a session by its refresh token, or ``None`` if not found/revoked."""
        result = await self.session.execute(
            select(UserSession).where(UserSession.refresh_token == refresh_token)
        )
        return result.scalar_one_or_none()

    async def delete_session(self, session_row: UserSession) -> None:
        """Revoke one session (logout) by deleting its row."""
        await self.session.delete(session_row)

    async def delete_sessions_for_user(self, user_id: uuid.UUID) -> None:
        """Revoke every session for a user (e.g. after a password reset)."""
        rows = (
            await self.session.execute(select(UserSession).where(UserSession.user_id == user_id))
        ).scalars().all()
        for row in rows:
            await self.session.delete(row)

    # --- email-verification tokens ---
    async def add_email_token(self, token_row: EmailVerificationToken) -> EmailVerificationToken:
        """Persist a new email-verification token (flush) and return it."""
        self.session.add(token_row)
        await self.session.flush()
        return token_row

    async def get_email_token(self, token: str) -> EmailVerificationToken | None:
        """Look up an email-verification token, or ``None`` if unknown."""
        result = await self.session.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.token == token)
        )
        return result.scalar_one_or_none()

    # --- password-reset tokens ---
    async def add_reset_token(self, token_row: PasswordResetToken) -> PasswordResetToken:
        """Persist a new password-reset token (flush) and return it."""
        self.session.add(token_row)
        await self.session.flush()
        return token_row

    async def get_reset_token(self, token: str) -> PasswordResetToken | None:
        """Look up a password-reset token, or ``None`` if unknown."""
        result = await self.session.execute(
            select(PasswordResetToken).where(PasswordResetToken.token == token)
        )
        return result.scalar_one_or_none()

    async def touch_used(self, token_row: PasswordResetToken, when: datetime) -> None:
        """Stamp a reset token as used at ``when`` so it cannot be reused (single-use)."""
        token_row.used_at = when
