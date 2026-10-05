"""API tests for the Audit endpoint — RBAC (read is coordinator/admin only) and empty state."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer


async def test_coordinator_can_read_audit_trail(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    resp = await client.get("/api/v1/audit-logs", headers=bearer(token))
    assert resp.status_code == 200
    assert resp.json()["pagination"]["total"] == 0


async def test_admin_can_read_audit_trail(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "admin@ex.com", "admin")
    assert (await client.get("/api/v1/audit-logs", headers=bearer(token))).status_code == 200


async def test_citizen_cannot_read_audit_trail(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    assert (await client.get("/api/v1/audit-logs", headers=bearer(token))).status_code == 403


async def test_provider_cannot_read_audit_trail(client: AsyncClient, db: AsyncSession) -> None:
    token, _ = await auth_user(client, db, "prov@ex.com", "provider")
    assert (await client.get("/api/v1/audit-logs", headers=bearer(token))).status_code == 403


async def test_audit_read_requires_auth(client: AsyncClient) -> None:
    assert (await client.get("/api/v1/audit-logs")).status_code == 401
