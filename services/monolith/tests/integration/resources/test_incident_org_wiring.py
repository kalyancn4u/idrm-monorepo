"""Integration tests for the wired INC↔ORG links (server-side org resolution + membership).

Covers: an unverified provider cannot claim; ``accept`` resolves the provider's own org;
``start``/``complete`` are restricted to the assigned provider; ``GET /incidents/assigned``.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_provider_with_org, auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
REQ = {"service_type": "rescue", "priority": "high", "description": "Trapped", "location": HYD}


async def test_unverified_provider_cannot_accept(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "c@ex.com", "citizen")
    prov, _, _ = await auth_provider_with_org(client, db, "p@ex.com", verified=False)
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]

    resp = await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(prov))
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "org_not_verified"


async def test_provider_without_org_cannot_accept(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "c2@ex.com", "citizen")
    prov, _ = await auth_user(client, db, "p2@ex.com", "provider")
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]
    resp = await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(prov))
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "org_required"


async def test_non_assigned_provider_cannot_start(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "c3@ex.com", "citizen")
    assignee, _, _ = await auth_provider_with_org(client, db, "assignee@ex.com")
    intruder, _, _ = await auth_provider_with_org(client, db, "intruder@ex.com")
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]

    assert (await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(assignee))).status_code == 200
    denied = await client.post(f"/api/v1/incidents/{iid}/start", headers=bearer(intruder))
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "not_assigned"
    assert (await client.post(f"/api/v1/incidents/{iid}/start", headers=bearer(assignee))).status_code == 200


async def test_assigned_queue_lists_claimed_incidents(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "c4@ex.com", "citizen")
    prov, _, _ = await auth_provider_with_org(client, db, "q@ex.com")
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]

    empty = await client.get("/api/v1/incidents/assigned", headers=bearer(prov))
    assert empty.json()["pagination"]["total"] == 0

    await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(prov))
    queued = await client.get("/api/v1/incidents/assigned", headers=bearer(prov))
    assert queued.json()["pagination"]["total"] == 1
    assert queued.json()["data"][0]["id"] == iid
