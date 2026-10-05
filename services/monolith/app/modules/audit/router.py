"""Audit module router — ``GET /audit-logs`` (read-only trail; doc 40 §5.4).

Mounted at ``/api/v1/audit-logs`` by ``app.main``. There is **no** write endpoint — entries are a
side-effect of significant actions (see ``AuditService.record``), which keeps the trail append-only
(PICS-AUD-002). Reads are restricted to coordinator/admin (PICS-AUD-003, F9/AC-9.1).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db, require_role
from app.core.pagination import paginate
from app.core.rate_limit import rate_limit
from app.modules.audit.repository import AuditRepository
from app.modules.audit.schemas import AuditLogResponse
from app.modules.audit.service import AuditService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("", dependencies=[
    Depends(require_role("coordinator", "admin")),
    Depends(rate_limit("audit_list", limit=50)),
])
async def list_audit_logs(
    db: DbSession,
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    actor_id: uuid.UUID | None = None,
    resource_type: str | None = None,
    resource_id: uuid.UUID | None = None,
    action: str | None = None,
) -> dict:
    """Read-only, filterable audit trail (coordinator/admin)."""
    service = AuditService(AuditRepository(db))
    entries, total = await service.list(
        page=page,
        limit=limit,
        actor_id=actor_id,
        resource_type=resource_type,
        resource_id=resource_id,
        action=action,
    )
    return paginate(
        [AuditLogResponse.model_validate(e).model_dump(mode="json") for e in entries],
        page, limit, total,
    )
