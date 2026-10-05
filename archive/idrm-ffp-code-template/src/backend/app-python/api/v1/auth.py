"""
api/v1/auth.py — authentication routes (Module M2): register, login, refresh, logout.

Thin handlers: each validates its body via a Pydantic schema, then delegates to
`services.auth_service`. Mounted by main.py under `/api/v1`, so the full paths are
`/api/v1/auth/register`, `/api/v1/auth/login`, etc.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db
from core.security import get_current_user
from dbmodels.user import User
from schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    TokenResponse,
)
from schemas.user import UserOut
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserOut)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)) -> User:
    """Create a new account. Self-service signup is limited to CITIZEN / PROVIDER /
    VOLUNTEER; elevated roles are granted later by an ADMIN."""
    return await auth_service.register(db, body)


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    """Verify credentials and return an access + refresh token pair plus the profile."""
    return await auth_service.login(db, body)


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(body: RefreshRequest, db: AsyncSession = Depends(get_db)) -> RefreshResponse:
    """Exchange a valid refresh token for a fresh 15-minute access token."""
    return await auth_service.refresh(db, body)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current: User = Depends(get_current_user)) -> None:
    """Log out. JWTs are stateless, so the client simply discards its tokens; this
    endpoint just confirms a valid session. (Server-side token revocation via a
    Redis denylist is a future addition.)"""
    return None
