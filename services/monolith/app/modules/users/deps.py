"""Users-module dependencies that need the User record (kept out of ``core`` to avoid coupling)."""

from __future__ import annotations

import uuid

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db
from app.core.exceptions import AppError
from app.modules.users.models import User
from app.modules.users.repository import UserRepository


async def get_current_user(
    claims: dict[str, str] = Depends(get_current_claims),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Load the authenticated user from the token's ``sub`` claim, or raise 401."""
    try:
        user_id = uuid.UUID(claims["sub"])
    except (KeyError, ValueError) as exc:
        raise AppError(401, "unauthorized", "Invalid token subject.") from exc
    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise AppError(401, "unauthorized", "Account not found.")
    return user
