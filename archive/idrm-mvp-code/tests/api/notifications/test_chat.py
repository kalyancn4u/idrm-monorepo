"""API test for the Task-L FAQ chatbot stub — always the fixed acknowledgement (no ML in MVP)."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

EXPECTED = "Your input is noted, we'll try to get back to you shortly, if possible."


async def test_chat_returns_fixed_reply(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "u@ex.com", "citizen")
    for message in ["How do I report an incident?", "anything at all"]:
        resp = await client.post(
            "/api/v1/notifications/chat", json={"message": message}, headers=bearer(token)
        )
        assert resp.status_code == 200
        assert resp.json()["reply"] == EXPECTED


async def test_chat_requires_auth(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/notifications/chat", json={"message": "hi"})
    assert resp.status_code == 401


async def test_chat_rejects_empty_message(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "u2@ex.com", "citizen")
    resp = await client.post(
        "/api/v1/notifications/chat", json={"message": ""}, headers=bearer(token)
    )
    assert resp.status_code == 422
