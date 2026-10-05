"""API tests for the Users/Auth module (roadmap §10, §13.3). Require the test DB + keys."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import EmailVerificationToken, User

EMAIL = "rajesh@example.com"
PASSWORD = "disaster-relief-2026"


async def _register(client: AsyncClient, email: str = EMAIL, role: str = "citizen"):
    return await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": PASSWORD, "name": "Rajesh Kumar", "role": role},
    )


async def _verify(client: AsyncClient, db: AsyncSession, email: str = EMAIL):
    user = (await db.execute(select(User).where(User.email == email))).scalar_one()
    token = (
        await db.execute(select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id))
    ).scalar_one()
    return await client.post("/api/v1/auth/verify-email", json={"token": token.token})


async def _login(client: AsyncClient, email: str = EMAIL, password: str = PASSWORD):
    return await client.post("/api/v1/auth/login", json={"email": email, "password": password})


async def test_register_returns_pending_account(client: AsyncClient) -> None:
    resp = await _register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["email"] == EMAIL
    assert body["status"] == "pending"
    assert body["email_verified"] is False


async def test_duplicate_email_conflicts(client: AsyncClient) -> None:
    await _register(client)
    resp = await _register(client)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "email_exists"


async def test_cannot_self_register_privileged_role(client: AsyncClient) -> None:
    resp = await _register(client, role="admin")
    assert resp.status_code == 403


async def test_login_blocked_before_verification(client: AsyncClient) -> None:
    await _register(client)
    resp = await _login(client)
    assert resp.status_code == 403  # account still 'pending'


async def test_register_verify_login_flow(client: AsyncClient, db: AsyncSession) -> None:
    await _register(client)
    assert (await _verify(client, db)).status_code == 200
    resp = await _login(client)
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] and body["refresh_token"]
    assert body["user"]["role"] == "citizen"


async def test_wrong_password_is_401(client: AsyncClient, db: AsyncSession) -> None:
    await _register(client)
    await _verify(client, db)
    resp = await _login(client, password="wrong")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "invalid_credentials"


async def test_me_requires_authentication(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code == 401


async def test_me_returns_profile_when_authenticated(client: AsyncClient, db: AsyncSession) -> None:
    await _register(client)
    await _verify(client, db)
    access = (await _login(client)).json()["access_token"]
    resp = await client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == EMAIL


async def test_citizen_cannot_list_users(client: AsyncClient, db: AsyncSession) -> None:
    await _register(client)
    await _verify(client, db)
    access = (await _login(client)).json()["access_token"]
    resp = await client.get("/api/v1/users", headers={"Authorization": f"Bearer {access}"})
    assert resp.status_code == 403
