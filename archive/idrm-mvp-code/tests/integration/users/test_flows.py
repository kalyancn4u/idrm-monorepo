"""Integration tests for the USR module against the real database (roadmap §10.1).

Cover the session lifecycle (refresh rotation, logout revocation), the lockout counter, and the
single-use password-reset flow.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import EmailVerificationToken, PasswordResetToken, User

EMAIL = "arjun@example.com"
PASSWORD = "volunteer-corps-2026"


async def _register_and_verify(client: AsyncClient, db: AsyncSession) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "name": "Arjun Reddy", "role": "provider"},
    )
    user = (await db.execute(select(User).where(User.email == EMAIL))).scalar_one()
    token = (
        await db.execute(select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id))
    ).scalar_one()
    await client.post("/api/v1/auth/verify-email", json={"token": token.token})


async def test_refresh_rotates_and_invalidates_old_token(client: AsyncClient, db: AsyncSession) -> None:
    await _register_and_verify(client, db)
    tokens = (await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})).json()
    rotated = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != tokens["refresh_token"]
    # the old refresh token no longer works after rotation
    reused = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401


async def test_logout_revokes_session(client: AsyncClient, db: AsyncSession) -> None:
    await _register_and_verify(client, db)
    tokens = (await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})).json()
    out = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert out.status_code == 200
    reused = await client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert reused.status_code == 401


async def test_five_failures_lock_the_account(client: AsyncClient, db: AsyncSession) -> None:
    await _register_and_verify(client, db)
    for _ in range(5):
        await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "wrong"})
    user = (await db.execute(select(User).where(User.email == EMAIL))).scalar_one()
    await db.refresh(user)
    assert user.failed_login_attempts == 5
    assert user.locked_until is not None


async def test_password_reset_is_single_use(client: AsyncClient, db: AsyncSession) -> None:
    await _register_and_verify(client, db)
    await client.post("/api/v1/auth/forgot-password", json={"email": EMAIL})
    user = (await db.execute(select(User).where(User.email == EMAIL))).scalar_one()
    reset = (
        await db.execute(select(PasswordResetToken).where(PasswordResetToken.user_id == user.id))
    ).scalar_one()

    new_password = "new-strong-passphrase"
    first = await client.post(
        "/api/v1/auth/reset-password", json={"token": reset.token, "new_password": new_password}
    )
    assert first.status_code == 200
    # new password works, old one does not
    assert (await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": new_password})).status_code == 200
    assert (await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": PASSWORD})).status_code == 401
    # the reset token cannot be reused
    reuse = await client.post(
        "/api/v1/auth/reset-password", json={"token": reset.token, "new_password": "another-one"}
    )
    assert reuse.status_code == 410
