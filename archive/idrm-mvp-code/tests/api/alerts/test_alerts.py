"""API tests for the Alerts endpoints — RBAC, platform-wide vs area-scoped, point filtering."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

# A square roughly around Hyderabad (17.2–17.6 lat, 78.3–78.7 lng).
HYD_BOX = [
    {"latitude": 17.2, "longitude": 78.3},
    {"latitude": 17.2, "longitude": 78.7},
    {"latitude": 17.6, "longitude": 78.7},
    {"latitude": 17.6, "longitude": 78.3},
]
PLATFORM_ALERT = {"title": "Nationwide advisory", "message": "Stay safe", "severity": "info"}
AREA_ALERT = {"title": "Hyderabad flood", "message": "Evacuate low areas", "severity": "critical",
              "area": HYD_BOX}


async def test_coordinator_creates_platform_alert(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    resp = await client.post("/api/v1/alerts", json=PLATFORM_ALERT, headers=bearer(coord))
    assert resp.status_code == 201
    assert resp.json()["platform_wide"] is True


async def test_citizen_cannot_create_alert(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    resp = await client.post("/api/v1/alerts", json=PLATFORM_ALERT, headers=bearer(cit))
    assert resp.status_code == 403


async def test_area_alert_is_marked_not_platform_wide(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord2@ex.com", "coordinator")
    resp = await client.post("/api/v1/alerts", json=AREA_ALERT, headers=bearer(coord))
    assert resp.status_code == 201
    assert resp.json()["platform_wide"] is False


async def test_area_filtering_by_point(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord3@ex.com", "coordinator")
    cit, _ = await auth_user(client, db, "cit2@ex.com", "citizen")
    await client.post("/api/v1/alerts", json=PLATFORM_ALERT, headers=bearer(coord))
    await client.post("/api/v1/alerts", json=AREA_ALERT, headers=bearer(coord))

    # inside Hyderabad → both the platform-wide and the area alert
    inside = await client.get(
        "/api/v1/alerts", params={"latitude": 17.385, "longitude": 78.486}, headers=bearer(cit)
    )
    assert {a["title"] for a in inside.json()["data"]} == {"Nationwide advisory", "Hyderabad flood"}

    # far away (Delhi) → only the platform-wide alert
    far = await client.get(
        "/api/v1/alerts", params={"latitude": 28.6139, "longitude": 77.2090}, headers=bearer(cit)
    )
    assert {a["title"] for a in far.json()["data"]} == {"Nationwide advisory"}


async def test_list_without_point_returns_all_active(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord4@ex.com", "coordinator")
    cit, _ = await auth_user(client, db, "cit3@ex.com", "citizen")
    await client.post("/api/v1/alerts", json=PLATFORM_ALERT, headers=bearer(coord))
    await client.post("/api/v1/alerts", json=AREA_ALERT, headers=bearer(coord))
    resp = await client.get("/api/v1/alerts", headers=bearer(cit))
    assert len(resp.json()["data"]) == 2
