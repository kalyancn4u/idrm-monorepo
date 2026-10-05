"""Integration tests for the locations module against the real database (PostGIS).

Exercises ``ST_DWithin`` proximity and the GeoJSON map layers over real incidents and organizations.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
INCIDENT = {"service_type": "medical", "priority": "high", "description": "Need help", "location": HYD}
ORG = {
    "name": "Hyderabad Relief",
    "type": "ngo",
    "service_categories": ["medical"],
    "service_area_center": HYD,
    "service_radius_km": 20,
    "capacity": 5,
}


async def _verified_provider_org(client: AsyncClient, db: AsyncSession, email: str) -> str:
    prov, _ = await auth_user(client, db, email, "provider")
    coord, _ = await auth_user(client, db, f"coord-{email}", "coordinator")
    org_id = (await client.post("/api/v1/organizations", json=ORG, headers=bearer(prov))).json()["id"]
    await client.post(f"/api/v1/organizations/{org_id}/verify", headers=bearer(coord))
    return org_id


async def test_nearby_returns_incidents_and_providers(
    client: AsyncClient, db: AsyncSession
) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    await client.post("/api/v1/incidents", json=INCIDENT, headers=bearer(cit))
    await _verified_provider_org(client, db, "prov@ex.com")
    coord, _ = await auth_user(client, db, "viewer@ex.com", "coordinator")

    resp = await client.get(
        "/api/v1/locations/nearby",
        params={**HYD, "radius_km": 10, "layer": "all"},
        headers=bearer(coord),
    )
    assert resp.status_code == 200
    kinds = {f["properties"]["kind"] for f in resp.json()["features"]}
    assert kinds == {"incident", "provider"}
    # every feature is GeoJSON [lng, lat]
    for f in resp.json()["features"]:
        assert f["geometry"]["coordinates"] == [78.486, 17.385]


async def test_map_incidents_layer_is_role_scoped(client: AsyncClient, db: AsyncSession) -> None:
    owner, _ = await auth_user(client, db, "owner@ex.com", "citizen")
    other, _ = await auth_user(client, db, "other@ex.com", "citizen")
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    await client.post("/api/v1/incidents", json=INCIDENT, headers=bearer(owner))

    # the other citizen sees none of the owner's incidents
    assert (await client.get("/api/v1/locations/map/incidents", headers=bearer(other))).json()["features"] == []
    # the owner sees their own
    assert len((await client.get("/api/v1/locations/map/incidents", headers=bearer(owner))).json()["features"]) == 1
    # a coordinator sees all open incidents
    assert len((await client.get("/api/v1/locations/map/incidents", headers=bearer(coord))).json()["features"]) == 1


async def test_map_providers_layer_lists_verified_orgs(
    client: AsyncClient, db: AsyncSession
) -> None:
    await _verified_provider_org(client, db, "p@ex.com")
    viewer, _ = await auth_user(client, db, "v@ex.com", "citizen")
    resp = await client.get("/api/v1/locations/map/providers", headers=bearer(viewer))
    assert resp.status_code == 200
    features = resp.json()["features"]
    assert len(features) == 1 and features[0]["properties"]["kind"] == "provider"
