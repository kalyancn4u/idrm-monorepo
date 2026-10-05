"""API tests for the Organizations endpoints — registration, RBAC, verification, capacity."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

ORG = {
    "name": "Hyderabad Relief NGO",
    "type": "ngo",
    "service_categories": ["medical", "food"],
    "service_area_center": {"latitude": 17.385, "longitude": 78.486},
    "service_radius_km": 15,
    "capacity": 10,
    "contact_phone": "+915551234567",
}


async def test_provider_registers_org_pending_verification(
    client: AsyncClient, db: AsyncSession
) -> None:
    token, _ = await auth_user(client, db, "prov@ex.com", "provider")
    resp = await client.post("/api/v1/organizations", json=ORG, headers=bearer(token))
    assert resp.status_code == 201
    body = resp.json()
    assert body["is_verified"] is False
    assert body["available_capacity"] == 10  # defaults to capacity
    assert set(body["service_categories"]) == {"medical", "food"}


async def test_citizen_cannot_register_org(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    resp = await client.post("/api/v1/organizations", json=ORG, headers=bearer(token))
    assert resp.status_code == 403


async def test_provider_cannot_register_two_orgs(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "prov2@ex.com", "provider")
    assert (await client.post("/api/v1/organizations", json=ORG, headers=bearer(token))).status_code == 201
    second = await client.post("/api/v1/organizations", json=ORG, headers=bearer(token))
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "already_exists"


async def test_coordinator_verifies_org(client: AsyncClient, db: AsyncSession) -> None:
    prov, _ = await auth_user(client, db, "prov3@ex.com", "provider")
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    org_id = (await client.post("/api/v1/organizations", json=ORG, headers=bearer(prov))).json()["id"]

    resp = await client.post(f"/api/v1/organizations/{org_id}/verify", headers=bearer(coord))
    assert resp.status_code == 200
    assert resp.json()["is_verified"] is True


async def test_provider_cannot_verify_own_org(client: AsyncClient, db: AsyncSession) -> None:
    prov, _ = await auth_user(client, db, "prov4@ex.com", "provider")
    org_id = (await client.post("/api/v1/organizations", json=ORG, headers=bearer(prov))).json()["id"]
    resp = await client.post(f"/api/v1/organizations/{org_id}/verify", headers=bearer(prov))
    assert resp.status_code == 403


async def test_only_owner_sets_capacity(client: AsyncClient, db: AsyncSession) -> None:
    owner, _ = await auth_user(client, db, "owner@ex.com", "provider")
    other, _ = await auth_user(client, db, "other@ex.com", "provider")
    org_id = (await client.post("/api/v1/organizations", json=ORG, headers=bearer(owner))).json()["id"]

    ok = await client.patch(
        f"/api/v1/organizations/{org_id}/capacity", json={"capacity": 3}, headers=bearer(owner)
    )
    assert ok.status_code == 200
    assert ok.json()["capacity"] == 3 and ok.json()["available_capacity"] == 3

    denied = await client.patch(
        f"/api/v1/organizations/{org_id}/capacity", json={"capacity": 99}, headers=bearer(other)
    )
    assert denied.status_code == 403


async def test_my_organization(client: AsyncClient, db: AsyncSession) -> None:
    prov, _ = await auth_user(client, db, "mine@ex.com", "provider")
    await client.post("/api/v1/organizations", json=ORG, headers=bearer(prov))
    resp = await client.get("/api/v1/organizations/mine", headers=bearer(prov))
    assert resp.status_code == 200
    assert resp.json()["name"] == ORG["name"]


async def test_list_filters_by_service_type(client: AsyncClient, db: AsyncSession) -> None:
    prov, _ = await auth_user(client, db, "l1@ex.com", "provider")
    coord, _ = await auth_user(client, db, "l2@ex.com", "coordinator")
    await client.post("/api/v1/organizations", json=ORG, headers=bearer(prov))

    hit = await client.get("/api/v1/organizations", params={"service_type": "medical"}, headers=bearer(coord))
    assert hit.status_code == 200 and hit.json()["pagination"]["total"] == 1
    miss = await client.get("/api/v1/organizations", params={"service_type": "shelter"}, headers=bearer(coord))
    assert miss.json()["pagination"]["total"] == 0
