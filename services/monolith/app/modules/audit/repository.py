"""Audit module repository — insert (append-only) and filtered read of the trail."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


class AuditRepository:
    """Async data access for the audit trail — insert and query only."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, entry: AuditLog) -> AuditLog:
        """Append one audit row (flush) and return it — there is no update/delete path."""
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def list(
        self,
        limit: int,
        offset: int,
        actor_id: uuid.UUID | None = None,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        action: str | None = None,
    ) -> tuple[list[AuditLog], int]:
        """Return a filtered, paginated page of audit entries (newest first) + total count."""
        stmt = select(AuditLog)
        if actor_id is not None:
            stmt = stmt.where(AuditLog.actor_id == actor_id)
        if resource_type is not None:
            stmt = stmt.where(AuditLog.resource_type == resource_type)
        if resource_id is not None:
            stmt = stmt.where(AuditLog.resource_id == resource_id)
        if action is not None:
            stmt = stmt.where(AuditLog.action == action)
        total = len((await self.session.execute(stmt)).scalars().all())
        paged = stmt.order_by(AuditLog.created_at.desc()).limit(limit).offset(offset)
        rows = (await self.session.execute(paged)).scalars().all()
        return list(rows), total
