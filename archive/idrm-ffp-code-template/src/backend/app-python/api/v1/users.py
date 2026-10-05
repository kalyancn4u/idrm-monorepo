"""
api/v1/users.py — current-user profile routes (Module M2): GET/POST /users/me.

Both require a logged-in user (the `get_current_user` dependency). Mounted under
`/api/v1`, so the paths are `/api/v1/users/me`.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from dbmodels.user import User
from schemas.user import UserOut, UserUpdate
from services import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def read_me(current: User = Depends(get_current_user)) -> User:
    """Return the signed-in user's own profile."""
    return current


@router.post("/me", response_model=UserOut)
async def update_me(
    body: UserUpdate,
    current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Update the signed-in user's own profile (full_name, phone, preferences).
    Email and role can't be changed here — role changes go through an ADMIN."""
    return await auth_service.update_profile(db, current, body)
