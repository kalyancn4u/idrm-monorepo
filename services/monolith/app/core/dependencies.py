"""Shared FastAPI dependencies: a database session and token/role guards.

Loading the full user record from a token lives in the users module (``app.modules.users.deps``)
to keep ``core`` free of module imports. These are the shared primitives every router builds on.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AppError
from app.core.security import decode_token
from app.infrastructure.database.engine import async_session

_bearer = HTTPBearer(auto_error=False)


async def get_db() -> AsyncIterator[AsyncSession]:
    """Yield a session, committing on success and rolling back on error."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_current_claims(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, str]:
    """Validate the ``Authorization: Bearer`` token and return its claims (``sub``, ``role``)."""
    if creds is None:
        raise AppError(401, "unauthorized", "Authentication required.")
    try:
        return decode_token(creds.credentials)
    except Exception as exc:  # noqa: BLE001 - any decode failure is an auth failure
        raise AppError(401, "unauthorized", "Invalid or expired token.") from exc


async def get_optional_claims(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> dict[str, str] | None:
    """Return token claims if a valid token is present, else None (for guest-allowed routes).

    A token that is present but invalid still fails with 401 — only *absence* means guest.
    """
    if creds is None:
        return None
    try:
        return decode_token(creds.credentials)
    except Exception as exc:  # noqa: BLE001
        raise AppError(401, "unauthorized", "Invalid or expired token.") from exc


def require_role(*roles: str) -> Callable[..., dict[str, str]]:
    """Return a dependency that allows only the given roles (else 403)."""

    def _guard(claims: dict[str, str] = Depends(get_current_claims)) -> dict[str, str]:
        if roles and claims.get("role") not in roles:
            raise AppError(403, "forbidden", "You do not have permission to do this.")
        return claims

    return _guard
