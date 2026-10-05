"""Integration tests for the incident lifecycle against the real database (roadmap §10.1).

The full happy-path walk, single-claim, and PostGIS proximity.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_provider_with_org, auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
CRITICAL = {"service_type": "medical", "priority": "critical", "description": "Critical case", "location": HYD}
HIGH = {"service_type": "rescue", "priority": "high", "description": "Trapped", "location": HYD}


async def test_full_lifecycle_walk(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "rajesh@ex.com", "citizen")
    coord, _ = await auth_user(client, db, "arjun@ex.com", "coordinator")
    prov, _, _ = await auth_provider_with_org(client, db, "priya@ex.com")

    iid = (await client.post("/api/v1/incidents", json=CRITICAL, headers=bearer(cit))).json()["id"]

    # a critical request cannot be claimed before approval
    early = await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(prov))
    assert early.status_code == 409

    steps = [
        (coord, "approve", {}, "approved"),
        (prov, "accept", {}, "accepted"),
        (prov, "start", None, "in_progress"),
        (prov, "complete", {"notes": "done"}, "completed"),
        (cit, "verify", {"rating": 5, "review": "fast"}, "verified"),
    ]
    for token, action, body, expected in steps:
        resp = await client.post(
            f"/api/v1/incidents/{iid}/{action}", json=body, headers=bearer(token)
        )
        assert resp.status_code == 200, (action, resp.json())
        assert resp.json()["status"] == expected

    final = (await client.get(f"/api/v1/incidents/{iid}", headers=bearer(cit))).json()
    assert final["rating"] == 5
    updates = (await client.get(f"/api/v1/incidents/{iid}/updates", headers=bearer(cit))).json()
    assert len(updates["data"]) == 6  # created + 5 transitions


async def test_single_claim_first_wins(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "c@ex.com", "citizen")
    p1, _, _ = await auth_provider_with_org(client, db, "p1@ex.com")
    p2, _, _ = await auth_provider_with_org(client, db, "p2@ex.com")
    iid = (await client.post("/api/v1/incidents", json=HIGH, headers=bearer(cit))).json()["id"]

    first = await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(p1))
    assert first.status_code == 200
    second = await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(p2))
    assert second.status_code == 409
    assert second.json()["error"]["code"] == "already_accepted"


async def test_nearby_returns_incidents_in_range(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cn@ex.com", "citizen")
    prov, _ = await auth_user(client, db, "pn@ex.com", "provider")
    for lat, lng in [(17.385, 78.486), (17.390, 78.470)]:
        await client.post(
            "/api/v1/incidents",
            json={**HIGH, "location": {"latitude": lat, "longitude": lng}},
            headers=bearer(cit),
        )
    resp = await client.get(
        "/api/v1/incidents/nearby",
        params={"latitude": 17.386, "longitude": 78.480, "radius_km": 10},
        headers=bearer(prov),
    )
    assert resp.status_code == 200
    assert len(resp.json()["data"]) == 2
