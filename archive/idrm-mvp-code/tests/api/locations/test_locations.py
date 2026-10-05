"""API tests for the Locations endpoints — distance, reverse-geocode, nearby RBAC, map layers."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
DEL = {"latitude": 28.6139, "longitude": 77.2090}


async def test_distance_between_two_points(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    resp = await client.post(
        "/api/v1/locations/distance",
        json={"origin": HYD, "destination": DEL},
        headers=bearer(token),
    )
    assert resp.status_code == 200
    assert 1200 < resp.json()["distance_km"] < 1300


async def test_distance_requires_auth(client: AsyncClient) -> None:
    resp = await client.post(
        "/api/v1/locations/distance", json={"origin": HYD, "destination": DEL}
    )
    assert resp.status_code == 401


async def test_reverse_geocode_returns_region(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit2@ex.com", "citizen")
    resp = await client.get(
        "/api/v1/locations/reverse-geocode", params=HYD, headers=bearer(token)
    )
    assert resp.status_code == 200
    assert resp.json()["region"] == "Telangana, India"


async def test_reverse_geocode_rejects_bad_coordinates(
    client: AsyncClient, db: AsyncSession
) -> None:
    token, _ = await auth_user(client, db, "cit3@ex.com", "citizen")
    resp = await client.get(
        "/api/v1/locations/reverse-geocode",
        params={"latitude": 200, "longitude": 0},
        headers=bearer(token),
    )
    assert resp.status_code == 422


async def test_citizen_cannot_use_generic_nearby(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit4@ex.com", "citizen")
    resp = await client.get("/api/v1/locations/nearby", params={**HYD, "radius_km": 5}, headers=bearer(token))
    assert resp.status_code == 403


async def test_unknown_map_layer_is_404(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    resp = await client.get("/api/v1/locations/map/rivers", headers=bearer(token))
    assert resp.status_code == 404
