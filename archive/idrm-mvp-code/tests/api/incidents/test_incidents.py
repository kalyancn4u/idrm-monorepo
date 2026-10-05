"""API tests for the Incidents module — create, read scope, RBAC, illegal transition."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

CREATE = {
    "service_type": "medical",
    "priority": "high",
    "description": "Injured near the bus stand, need help",
    "location": {"latitude": 17.39, "longitude": 78.47},
}


async def test_guest_can_create_and_gets_tracking_token(client: AsyncClient) -> None:
    resp = await client.post("/api/v1/incidents", json=CREATE)
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "created"
    assert body["requester_id"] is None
    assert body["tracking_token"]
    assert body["location"] == {"latitude": 17.39, "longitude": 78.47}


async def test_citizen_create_has_no_tracking_token(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit@example.com", "citizen")
    resp = await client.post("/api/v1/incidents", json=CREATE, headers=bearer(token))
    assert resp.status_code == 201
    assert resp.json()["requester_id"] is not None
    assert resp.json()["tracking_token"] is None


async def test_provider_cannot_create(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "prov@example.com", "provider")
    resp = await client.post("/api/v1/incidents", json=CREATE, headers=bearer(token))
    assert resp.status_code == 403


async def test_citizen_read_scope(client: AsyncClient, db: AsyncSession) -> None:
    owner, _ = await auth_user(client, db, "owner@example.com", "citizen")
    created = (await client.post("/api/v1/incidents", json=CREATE, headers=bearer(owner))).json()
    assert (await client.get(f"/api/v1/incidents/{created['id']}", headers=bearer(owner))).status_code == 200
    other, _ = await auth_user(client, db, "other@example.com", "citizen")
    denied = await client.get(f"/api/v1/incidents/{created['id']}", headers=bearer(other))
    assert denied.status_code == 403


async def test_citizen_cannot_approve(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit2@example.com", "citizen")
    created = (await client.post("/api/v1/incidents", json=CREATE, headers=bearer(token))).json()
    resp = await client.post(f"/api/v1/incidents/{created['id']}/approve", json={}, headers=bearer(token))
    assert resp.status_code == 403


async def test_start_before_accept_is_invalid(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit3@example.com", "citizen")
    prov, _ = await auth_user(client, db, "prov2@example.com", "provider")
    created = (await client.post("/api/v1/incidents", json=CREATE, headers=bearer(cit))).json()
    resp = await client.post(f"/api/v1/incidents/{created['id']}/start", headers=bearer(prov))
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "invalid_transition"


async def test_create_requires_valid_coordinates(client: AsyncClient) -> None:
    bad = {**CREATE, "location": {"latitude": 200, "longitude": 78.47}}
    resp = await client.post("/api/v1/incidents", json=bad)
    assert resp.status_code == 422
