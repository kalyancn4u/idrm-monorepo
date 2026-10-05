"""Smoke test: the app boots and the health probe answers with a correlation id."""

from __future__ import annotations

from httpx import AsyncClient


async def test_health_ok(client: AsyncClient) -> None:
    resp = await client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    # every response echoes a correlation id (roadmap §7)
    assert resp.headers.get("X-Request-Id")
