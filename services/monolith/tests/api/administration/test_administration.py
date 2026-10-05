"""API tests for the Administration endpoints — reference data (staff) + overview (admin)."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer


async def test_reference_data_available_to_staff(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    body = (await client.get("/api/v1/administration/reference-data", headers=bearer(coord))).json()
    assert set(body["roles"]) == {"citizen", "provider", "coordinator", "admin"}
    assert "medical" in body["service_types"]
    assert body["incident_transitions"]["accept"]["to"] == "accepted"
    assert "provider" in body["incident_transitions"]["accept"]["roles"]


async def test_reference_data_denied_to_citizen(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    resp = await client.get("/api/v1/administration/reference-data", headers=bearer(cit))
    assert resp.status_code == 403


async def test_overview_is_admin_only(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord2@ex.com", "coordinator")
    assert (await client.get("/api/v1/administration/overview", headers=bearer(coord))).status_code == 403


async def test_overview_counts(client: AsyncClient, db: AsyncSession) -> None:
    admin, _ = await auth_user(client, db, "admin@ex.com", "admin")
    await auth_user(client, db, "c1@ex.com", "citizen")
    await auth_user(client, db, "c2@ex.com", "citizen")
    body = (await client.get("/api/v1/administration/overview", headers=bearer(admin))).json()
    assert body["users_by_role"]["citizen"] == 2
    assert body["users_by_role"]["admin"] == 1
    assert body["organizations_pending_verification"] == 0
