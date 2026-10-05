"""API tests for GET /incidents filtering & sorting (priority, full-text ``q``, whitelisted sort).

These exercise the F5-B filters wired 2026-08-22 so the code matches the OpenAPI contract and the
existing indexes (``ix_incidents_priority``, the GIN ``to_tsvector(description)``, ``ix_incidents_created_at``).
Coordinators list across all incidents, so a coordinator token is used to read what a citizen created.
"""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer

HYD = {"latitude": 17.39, "longitude": 78.47}


async def _create(
    client: AsyncClient, token: str, *, service_type: str, priority: str, description: str
) -> str:
    """Create one incident as the given user and return its id."""
    body = {
        "service_type": service_type,
        "priority": priority,
        "description": description,
        "location": HYD,
    }
    resp = await client.post("/api/v1/incidents", json=body, headers=bearer(token))
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def test_filter_by_priority(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "fp-cit@example.com", "citizen")
    coord, _ = await auth_user(client, db, "fp-coord@example.com", "coordinator")
    await _create(client, cit, service_type="medical", priority="critical",
                  description="Severe bleeding, urgent")
    await _create(client, cit, service_type="food", priority="low",
                  description="Needs rice and water")

    resp = await client.get("/api/v1/incidents?priority=critical", headers=bearer(coord))
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert data and all(i["priority"] == "critical" for i in data)


async def test_full_text_search_q(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "fq-cit@example.com", "citizen")
    coord, _ = await auth_user(client, db, "fq-coord@example.com", "coordinator")
    await _create(client, cit, service_type="shelter", priority="high",
                  description="Roof collapsed, need temporary shelter")
    await _create(client, cit, service_type="food", priority="low",
                  description="Family needs rice and water")

    hit = await client.get("/api/v1/incidents?q=shelter", headers=bearer(coord))
    assert hit.status_code == 200
    descriptions = [i["description"] for i in hit.json()["data"]]
    assert descriptions and all("shelter" in d.lower() for d in descriptions)

    miss = await client.get("/api/v1/incidents?q=earthquake", headers=bearer(coord))
    assert miss.status_code == 200
    assert miss.json()["data"] == []


async def test_sort_by_priority_ascending_and_descending(
    client: AsyncClient, db: AsyncSession
) -> None:
    cit, _ = await auth_user(client, db, "fs-cit@example.com", "citizen")
    coord, _ = await auth_user(client, db, "fs-coord@example.com", "coordinator")
    await _create(client, cit, service_type="food", priority="low", description="low one")
    await _create(client, cit, service_type="medical", priority="critical",
                  description="critical one")

    # enum order is low < medium < high < critical
    asc = await client.get("/api/v1/incidents?sort=priority", headers=bearer(coord))
    prios = [i["priority"] for i in asc.json()["data"]]
    assert prios.index("low") < prios.index("critical")

    desc = await client.get("/api/v1/incidents?sort=-priority", headers=bearer(coord))
    prios_desc = [i["priority"] for i in desc.json()["data"]]
    assert prios_desc.index("critical") < prios_desc.index("low")


async def test_invalid_sort_field_is_422(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "is-coord@example.com", "coordinator")
    resp = await client.get("/api/v1/incidents?sort=description", headers=bearer(coord))
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "invalid_sort"
