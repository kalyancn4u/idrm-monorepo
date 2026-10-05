"""API test for per-endpoint rate limiting (roadmap §8.3; doc 22 §6)."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.users.models import EmailVerificationToken, User

EMAIL = "priya@example.com"
PASSWORD = "coordinated-response-2026"


async def test_login_is_rate_limited(client: AsyncClient, db: AsyncSession) -> None:
    await client.post(
        "/api/v1/auth/register",
        json={"email": EMAIL, "password": PASSWORD, "name": "Dr. Priya Sharma", "role": "provider"},
    )
    user = (await db.execute(select(User).where(User.email == EMAIL))).scalar_one()
    token = (
        await db.execute(select(EmailVerificationToken).where(EmailVerificationToken.user_id == user.id))
    ).scalar_one()
    await client.post("/api/v1/auth/verify-email", json={"token": token.token})

    # login budget is 5/min; the 6th attempt is rejected with 429 + Retry-After
    for _ in range(5):
        await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "wrong"})
    resp = await client.post("/api/v1/auth/login", json={"email": EMAIL, "password": "wrong"})
    assert resp.status_code == 429
    assert resp.json()["error"]["code"] == "rate_limit_exceeded"
    assert resp.headers.get("Retry-After")
