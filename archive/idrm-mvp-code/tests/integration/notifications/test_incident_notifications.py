"""Integration test for PICS-NTF-001 — a notification on each incident state change.

The requester (a citizen) is notified when someone else moves their request through the lifecycle,
and read/read-all/soft-delete behave end-to-end against the real database.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_provider_with_org, auth_user, bearer

HYD = {"latitude": 17.385, "longitude": 78.486}
REQ = {"service_type": "medical", "priority": "high", "description": "Injured", "location": HYD}


async def test_requester_is_notified_on_state_change(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    prov, _, _ = await auth_provider_with_org(client, db, "prov@ex.com")
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]

    # provider accepts → the citizen requester should get one incident_update notification
    assert (await client.post(f"/api/v1/incidents/{iid}/accept", json={}, headers=bearer(prov))).status_code == 200

    inbox = await client.get("/api/v1/notifications", headers=bearer(cit))
    data = inbox.json()["data"]
    assert len(data) == 1
    assert data[0]["type"] == "incident_update"
    assert data[0]["link"] == f"/incidents/{iid}"
    assert "accepted" in data[0]["message"]

    count = await client.get("/api/v1/notifications/unread-count", headers=bearer(cit))
    assert count.json()["count"] == 1


async def test_self_actions_do_not_notify(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "self@ex.com", "citizen")
    iid = (await client.post("/api/v1/incidents", json=REQ, headers=bearer(cit))).json()["id"]
    # the citizen cancels their own request → no self-notification
    await client.post(f"/api/v1/incidents/{iid}/cancel", json={"reason": "resolved"}, headers=bearer(cit))
    inbox = await client.get("/api/v1/notifications", headers=bearer(cit))
    assert inbox.json()["pagination"]["total"] == 0


async def test_read_all_and_delete(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "r@ex.com", "citizen")
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    # a critical request generates an approval notification from the coordinator
    critical = {**REQ, "priority": "critical"}
    iid = (await client.post("/api/v1/incidents", json=critical, headers=bearer(cit))).json()["id"]
    await client.post(f"/api/v1/incidents/{iid}/approve", json={}, headers=bearer(coord))

    nid = (await client.get("/api/v1/notifications", headers=bearer(cit))).json()["data"][0]["id"]
    assert (await client.post(f"/api/v1/notifications/{nid}/read", headers=bearer(cit))).json()["is_read"] is True
    assert (await client.get("/api/v1/notifications/unread-count", headers=bearer(cit))).json()["count"] == 0
    assert (await client.delete(f"/api/v1/notifications/{nid}", headers=bearer(cit))).status_code == 204
    assert (await client.get("/api/v1/notifications", headers=bearer(cit))).json()["pagination"]["total"] == 0
