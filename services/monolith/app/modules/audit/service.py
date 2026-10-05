"""Audit module service — record significant actions and read the trail (roadmap §13.5).

:meth:`AuditService.record` is the cross-cutting entry point other modules call after a significant
action (incident transitions, org verification, alert broadcasts, …). It only ever inserts, so the
trail is append-only (PICS-AUD-001/002). Reads are coordinator/admin-only (enforced at the router).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.modules.audit.models import AuditLog
from app.modules.audit.repository import AuditRepository

logger = logging.getLogger("idrm.audit")


class AuditService:
    """Write and query the audit trail."""

    def __init__(self, repo: AuditRepository) -> None:
        self.repo = repo

    async def record(
        self,
        action: str,
        *,
        actor_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        ip_address: str | None = None,
        old_values: dict[str, Any] | None = None,
        new_values: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Append one entry to the audit trail (never updates an existing row)."""
        entry = AuditLog(
            action=action,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            old_values=old_values,
            new_values=new_values,
        )
        await self.repo.add(entry)
        logger.info(
            "audit.record",
            extra={"extra_fields": {"action": action, "resource_type": resource_type}},
        )
        return entry

    async def list(
        self,
        page: int,
        limit: int,
        actor_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        action: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        """Read the trail, filterable by actor/resource/action, paginated (coordinator/admin)."""
        return await self.repo.list(
            limit=limit,
            offset=(page - 1) * limit,
            actor_id=actor_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
        )
