"""Integration tests for operational reports over real, walked-through incident data."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_provider_with_org, auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
REQ = {"service_type": "medical", "priority": "high", "description": "Injured", "location": HYD}


async def _walk_to_verified(client: AsyncClient, cit: str, prov: str) -> str:
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]
    for action, body in [("accept", {}), ("start", None), ("complete", {"notes": "x"})]:
        await client.post(f"/api/v1/incidents/{iid}/{action}", json=body, headers=bearer(prov))
    await client.post(f"/api/v1/incidents/{iid}/verify", json={"rating": 5}, headers=bearer(cit))
    return iid


async def test_dashboard_counts_reflect_data(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    prov, _, _ = await auth_provider_with_org(client, db, "prov@ex.com")
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    await _walk_to_verified(client, cit, prov)
    await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))  # a second, still open

    board = (await client.get("/api/v1/reports/dashboard", headers=bearer(coord))).json()
    assert board["total_incidents"] == 2
    assert board["by_status"]["verified"] == 1
    assert board["by_status"]["created"] == 1
    assert board["by_service_type"]["medical"] == 2
    assert board["by_region"]["Telangana, India"] == 2
    assert board["organizations"] == {"total": 1, "verified": 1}


async def test_response_times_and_fulfillment(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit2@ex.com", "citizen")
    prov, _, _ = await auth_provider_with_org(client, db, "prov2@ex.com")
    coord, _ = await auth_user(client, db, "coord2@ex.com", "coordinator")
    await _walk_to_verified(client, cit, prov)

    rt = (await client.get("/api/v1/reports/response-times", headers=bearer(coord))).json()
    assert rt["time_to_accept"]["count"] == 1
    assert rt["time_to_accept"]["avg_seconds"] is not None
    assert rt["time_to_resolve"]["count"] == 1

    ful = (await client.get("/api/v1/reports/fulfillment", headers=bearer(coord))).json()
    assert ful["total_incidents"] == 1
    assert ful["resolved"] == 1
    assert ful["fulfillment_rate"] == 1.0
    assert ful["verification_rate"] == 1.0
    assert ful["verified_from_audit"] == 1  # cross-checked against the audit trail


async def test_csv_export_has_flattened_metrics(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit3@ex.com", "citizen")
    prov, _, _ = await auth_provider_with_org(client, db, "prov3@ex.com")
    coord, _ = await auth_user(client, db, "coord3@ex.com", "coordinator")
    await _walk_to_verified(client, cit, prov)

    resp = await client.get("/api/v1/reports/dashboard/export", headers=bearer(coord))
    assert resp.status_code == 200
    text = resp.text
    assert "by_status.verified,1" in text
    assert 'filename="dashboard.csv"' in resp.headers["content-disposition"]
