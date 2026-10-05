"""API tests for the Resources endpoints — declare/update assets, RBAC, role-scoped listing."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_provider_with_org, auth_user, bearer

RESOURCE = {
    "name": "Ambulance A1",
    "kind": "ambulance",
    "quantity": 2,
    "location": {"latitude": 17.385, "longitude": 78.486},
}


async def test_provider_declares_resource(client: AsyncClient, db: AsyncSession) -> None:
    token, _, org_id = await auth_provider_with_org(client, db, "prov@ex.com")
    resp = await client.post("/api/v1/resources", json=RESOURCE, headers=bearer(token))
    assert resp.status_code == 201
    body = resp.json()
    assert body["organization_id"] == str(org_id)
    assert body["location"] == {"latitude": 17.385, "longitude": 78.486}


async def test_provider_without_org_cannot_declare(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "noorg@ex.com", "provider")
    resp = await client.post("/api/v1/resources", json=RESOURCE, headers=bearer(token))
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "org_required"


async def test_citizen_cannot_declare_resource(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    resp = await client.post("/api/v1/resources", json=RESOURCE, headers=bearer(token))
    assert resp.status_code == 403


async def test_only_owner_updates_resource(client: AsyncClient, db: AsyncSession) -> None:
    owner, _, _ = await auth_provider_with_org(client, db, "owner@ex.com")
    other, _, _ = await auth_provider_with_org(client, db, "other@ex.com")
    rid = (await client.post("/api/v1/resources", json=RESOURCE, headers=bearer(owner))).json()["id"]

    denied = await client.patch(
        f"/api/v1/resources/{rid}", json={"is_available": False}, headers=bearer(other)
    )
    assert denied.status_code == 403
    ok = await client.patch(
        f"/api/v1/resources/{rid}", json={"is_available": False}, headers=bearer(owner)
    )
    assert ok.status_code == 200 and ok.json()["is_available"] is False


async def test_provider_list_is_scoped_to_own(client: AsyncClient, db: AsyncSession) -> None:
    p1, _, _ = await auth_provider_with_org(client, db, "p1@ex.com")
    p2, _, _ = await auth_provider_with_org(client, db, "p2@ex.com")
    await client.post("/api/v1/resources", json=RESOURCE, headers=bearer(p1))

    assert (await client.get("/api/v1/resources", headers=bearer(p1))).json()["pagination"]["total"] == 1
    assert (await client.get("/api/v1/resources", headers=bearer(p2))).json()["pagination"]["total"] == 0


async def test_coordinator_sees_all_resources(client: AsyncClient, db: AsyncSession) -> None:
    p1, _, _ = await auth_provider_with_org(client, db, "cp1@ex.com")
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    await client.post("/api/v1/resources", json=RESOURCE, headers=bearer(p1))
    resp = await client.get("/api/v1/resources", headers=bearer(coord))
    assert resp.json()["pagination"]["total"] == 1
