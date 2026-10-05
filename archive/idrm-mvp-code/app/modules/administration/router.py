"""Administration module router — ``/administration`` reference data + oversight (doc 40).

Mounted at ``/api/v1`` by ``app.main`` (so paths carry the ``/administration`` prefix themselves).
User/role administration lives in the users module; this router adds admin reference data and a
small oversight summary.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_role
from app.core.rate_limit import rate_limit
from app.modules.administration.repository import AdministrationRepository
from app.modules.administration.service import AdministrationService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/administration/reference-data", dependencies=[
    Depends(require_role("coordinator", "admin")),
    Depends(rate_limit("admin_reference", limit=100)),
])
async def reference_data() -> dict:
    """The platform's controlled vocabularies + incident lifecycle (staff-only, PICS-ADM-001)."""
    return AdministrationService.reference_data()


@router.get("/administration/overview", dependencies=[
    Depends(require_role("admin")),
    Depends(rate_limit("admin_overview", limit=50)),
])
async def overview(db: DbSession) -> dict:
    """Admin oversight: users by role/status + organizations awaiting verification."""
    return await AdministrationService(AdministrationRepository(db)).overview()
