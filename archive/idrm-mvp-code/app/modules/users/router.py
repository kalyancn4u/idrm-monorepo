"""Users module router — the ``/auth`` and ``/users`` endpoints (doc 40 §5.1; roadmap §13.3).

Role checks run here (via dependencies); ownership and business rules live in the service.
Mounted at ``/api/v1`` by ``app.main``.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_claims, get_db, require_role
from app.core.logging import client_ip_ctx
from app.core.rate_limit import rate_limit
from app.core.security import create_access_token
from app.modules.audit.repository import AuditRepository
from app.modules.audit.service import AuditService
from app.modules.users.deps import get_current_user
from app.modules.users.models import User
from app.modules.users.repository import UserRepository
from app.modules.users.schemas import (
    AdminUpdateUserRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    UpdateProfileRequest,
    UserResponse,
    VerifyEmailRequest,
)
from app.modules.users.service import UserService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]


def _service(db: DbSession) -> UserService:
    return UserService(UserRepository(db))


# --------------------------------------------------------------------------- auth
@router.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(rate_limit("register", limit=10))],
)
async def register(data: RegisterRequest, db: DbSession) -> User:
    """Create an account (starts ``pending`` until email is verified)."""
    return await _service(db).register(data)


@router.post("/auth/verify-email", response_model=MessageResponse)
async def verify_email(data: VerifyEmailRequest, db: DbSession) -> MessageResponse:
    """Activate an account from its emailed verification token (AC-1.2)."""
    await _service(db).verify_email(data.token)
    return MessageResponse(message="Email verified. You can now sign in.")


@router.post(
    "/auth/resend-verification",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit("resend", limit=3))],
)
async def resend_verification(data: ResendVerificationRequest, db: DbSession) -> MessageResponse:
    """Re-send the verification email (always replies the same, to avoid leaking who exists)."""
    await _service(db).resend_verification(data.email)
    return MessageResponse(
        message="If the account exists and is unverified, a new link has been sent."
    )


@router.post(
    "/auth/login",
    response_model=TokenResponse,
    dependencies=[Depends(rate_limit("login", limit=5))],
)
async def login(data: LoginRequest, request: Request, db: DbSession) -> TokenResponse:
    """Authenticate and return access + refresh tokens (5-fail / 15-min lockout applies)."""
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    refresh_token, user = await _service(db).login(data.email, data.password, ip, user_agent)
    access = create_access_token(str(user.id), user.role.value)
    return TokenResponse(
        access_token=access, refresh_token=refresh_token, user=UserResponse.model_validate(user)
    )


@router.post("/auth/refresh", response_model=RefreshResponse)
async def refresh(data: RefreshRequest, db: DbSession) -> RefreshResponse:
    """Rotate the refresh token and return a fresh access token."""
    access, new_refresh = await _service(db).refresh(data.refresh_token)
    return RefreshResponse(access_token=access, refresh_token=new_refresh)


@router.post("/auth/logout", response_model=MessageResponse)
async def logout(
    data: RefreshRequest, db: DbSession, _: dict = Depends(get_current_claims)
) -> MessageResponse:
    """Revoke the given refresh-token session (sign out)."""
    await _service(db).logout(data.refresh_token)
    return MessageResponse(message="Signed out.")


@router.post(
    "/auth/forgot-password",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit("forgot_password", limit=3))],
)
async def forgot_password(data: ForgotPasswordRequest, db: DbSession) -> MessageResponse:
    """Start a password reset (always replies the same, to avoid leaking who exists)."""
    await _service(db).forgot_password(data.email)
    return MessageResponse(message="If the account exists, a reset link has been sent.")


@router.post(
    "/auth/reset-password",
    response_model=MessageResponse,
    dependencies=[Depends(rate_limit("reset_password", limit=5))],
)
async def reset_password(data: ResetPasswordRequest, db: DbSession) -> MessageResponse:
    """Set a new password from a single-use reset token, then revoke existing sessions."""
    await _service(db).reset_password(data.token, data.new_password)
    return MessageResponse(message="Password reset. Please sign in.")


@router.post("/auth/change-password", response_model=MessageResponse)
async def change_password(
    data: ChangePasswordRequest,
    db: DbSession,
    user: User = Depends(get_current_user),
) -> MessageResponse:
    """Change the signed-in user's password (requires the current password)."""
    await _service(db).change_password(user, data.current_password, data.new_password)
    return MessageResponse(message="Password changed.")


# --------------------------------------------------------------------------- users
@router.get("/users/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> User:
    """The current user's profile."""
    return user


@router.patch("/users/me", response_model=UserResponse)
async def update_me(
    data: UpdateProfileRequest, db: DbSession, user: User = Depends(get_current_user)
) -> User:
    """Update the current user's own profile (name/phone/language)."""
    return await _service(db).update_profile(user, data)


@router.get("/users")
async def list_users(
    db: DbSession,
    _: dict = Depends(require_role("coordinator", "admin")),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
) -> dict:
    """List/manage users (coordinator/admin only), wrapped with pagination."""
    users, total = await _service(db).list_users(page=page, limit=limit)
    return {
        "data": [UserResponse.model_validate(u).model_dump(mode="json") for u in users],
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
        },
    }


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID, db: DbSession, _: dict = Depends(require_role("coordinator", "admin"))
) -> User:
    """Fetch a single user by id (coordinator/admin only)."""
    return await _service(db).get_user(user_id)


@router.patch("/users/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: uuid.UUID,
    data: AdminUpdateUserRequest,
    db: DbSession,
    claims: dict = Depends(require_role("admin")),
) -> User:
    """Admin-only change of a user's role/status (audited)."""
    user = await _service(db).admin_update_user(user_id, data.role, data.status)
    await AuditService(AuditRepository(db)).record(
        "user.admin_update",
        actor_id=uuid.UUID(claims["sub"]),
        resource_type="user",
        resource_id=user_id,
        ip_address=client_ip_ctx.get(),
        new_values={"role": user.role.value, "status": user.status.value},
    )
    return user
