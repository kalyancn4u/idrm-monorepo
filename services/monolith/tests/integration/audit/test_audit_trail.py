"""Integration tests for the audit trail (PICS-AUD-001/003).

Significant actions across modules (incident transitions, org verification, alert broadcast) each
append an entry that a coordinator can then query and filter.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
INCIDENT = {"service_type": "medical", "priority": "critical", "description": "Injured", "location": HYD}
ORG = {"name": "Relief NGO", "type": "ngo", "service_categories": ["medical"], "capacity": 5}
ALERT = {"title": "Advisory", "message": "Stay safe", "severity": "warning"}


async def test_incident_transition_is_audited(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    iid = (await client.post("/api/v1/incidents", json=INCIDENT, headers=bearer(cit))).json()["id"]
    await client.post(f"/api/v1/incidents/{iid}/approve", json={}, headers=bearer(coord))

    logs = (await client.get("/api/v1/audit-logs", headers=bearer(coord))).json()["data"]
    entry = next(e for e in logs if e["action"] == "incident.approve")
    assert entry["resource_type"] == "incident"
    assert entry["resource_id"] == iid
    assert entry["new_values"] == {"status": "approved"}


async def test_filter_by_resource(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "c2@ex.com", "citizen")
    coord, _ = await auth_user(client, db, "coord2@ex.com", "coordinator")
    iid = (await client.post("/api/v1/incidents", json=INCIDENT, headers=bearer(cit))).json()["id"]
    await client.post(f"/api/v1/incidents/{iid}/approve", json={}, headers=bearer(coord))
    await client.post(f"/api/v1/incidents/{iid}/cancel", json={"reason": "x"}, headers=bearer(coord))

    filtered = await client.get(
        "/api/v1/audit-logs",
        params={"resource_type": "incident", "resource_id": iid},
        headers=bearer(coord),
    )
    actions = {e["action"] for e in filtered.json()["data"]}
    assert actions == {"incident.approve", "incident.cancel"}


async def test_org_verification_and_alert_are_audited(client: AsyncClient, db: AsyncSession) -> None:
    prov, _ = await auth_user(client, db, "prov@ex.com", "provider")
    coord, _ = await auth_user(client, db, "coord3@ex.com", "coordinator")
    org_id = (await client.post("/api/v1/organizations", json=ORG, headers=bearer(prov))).json()["id"]
    await client.post(f"/api/v1/organizations/{org_id}/verify", headers=bearer(coord))
    await client.post("/api/v1/alerts", json=ALERT, headers=bearer(coord))

    logs = (await client.get("/api/v1/audit-logs", headers=bearer(coord))).json()["data"]
    actions = {e["action"] for e in logs}
    assert "organization.verified" in actions
    assert "alert.created" in actions
