"""Integration test — an admin changing a user's role/status is audited (PICS-ADM-002 + AUD-001)."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer


async def test_admin_role_change_writes_audit_entry(client: AsyncClient, db: AsyncSession) -> None:
    admin, _ = await auth_user(client, db, "admin@ex.com", "admin")
    target, target_id = await auth_user(client, db, "target@ex.com", "citizen")

    resp = await client.patch(
        f"/api/v1/users/{target_id}",
        json={"role": "coordinator", "status": "active"},
        headers=bearer(admin),
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "coordinator"

    logs = (await client.get("/api/v1/audit-logs", headers=bearer(admin))).json()["data"]
    entry = next(e for e in logs if e["action"] == "user.admin_update")
    assert entry["resource_type"] == "user"
    assert entry["resource_id"] == str(target_id)
    assert entry["new_values"] == {"role": "coordinator", "status": "active"}


async def test_non_admin_cannot_change_user(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    _, target_id = await auth_user(client, db, "t2@ex.com", "citizen")
    resp = await client.patch(
        f"/api/v1/users/{target_id}", json={"role": "admin"}, headers=bearer(coord)
    )
    assert resp.status_code == 403
