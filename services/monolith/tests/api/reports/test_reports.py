"""API tests for the Reports endpoints — RBAC, empty shape, export format + unknown-report errors."""

from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.factories import auth_user, bearer


async def test_dashboard_requires_staff(client: AsyncClient, db: AsyncSession) -> None:
    cit, _ = await auth_user(client, db, "cit@ex.com", "citizen")
    prov, _ = await auth_user(client, db, "prov@ex.com", "provider")
    assert (await client.get("/api/v1/reports/dashboard", headers=bearer(cit))).status_code == 403
    assert (await client.get("/api/v1/reports/dashboard", headers=bearer(prov))).status_code == 403


async def test_empty_dashboard_shape(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord@ex.com", "coordinator")
    body = (await client.get("/api/v1/reports/dashboard", headers=bearer(coord))).json()
    assert body["total_incidents"] == 0
    assert body["by_status"] == {}
    assert body["organizations"] == {"total": 0, "verified": 0}


async def test_export_rejects_non_csv_format(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord2@ex.com", "coordinator")
    resp = await client.get(
        "/api/v1/reports/dashboard/export", params={"format": "pdf"}, headers=bearer(coord)
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "unsupported_format"


async def test_export_unknown_report_is_404(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord3@ex.com", "coordinator")
    resp = await client.get("/api/v1/reports/nonsense/export", headers=bearer(coord))
    assert resp.status_code == 404


async def test_export_csv_content_type(client: AsyncClient, db: AsyncSession) -> None:
    coord, _ = await auth_user(client, db, "coord4@ex.com", "coordinator")
    resp = await client.get("/api/v1/reports/fulfillment/export", headers=bearer(coord))
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "metric,value" in resp.text
