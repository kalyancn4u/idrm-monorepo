"""Reports module repository — read-only aggregate queries over live data (roadmap §13.5).

The reports module owns **no table** (doc 50); it aggregates ``incidents`` (+ their timeline),
``organizations`` and the ``audit_logs`` trail. Grouped counts run in SQL; response-time samples are
returned raw for the service to summarise (avg/median) in Python — DB-agnostic and easy to test.
"""

from __future__ import annotations

from sqlalchemy import Column, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog
from app.modules.incidents.lifecycle import IncidentStatus
from app.modules.incidents.models import Incident, IncidentUpdate
from app.modules.incidents.repository import from_point
from app.modules.resources.models import Organization

_TERMINAL = [IncidentStatus.verified, IncidentStatus.cancelled, IncidentStatus.rejected]


class ReportRepository:
    """Async aggregate reads for operational reports."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _counts_by(self, column: Column) -> dict[str, int]:
        """``{value: count}`` for a grouped column over non-deleted incidents."""
        stmt = (
            select(column, func.count())
            .where(Incident.deleted_at.is_(None))
            .group_by(column)
        )
        rows = (await self.session.execute(stmt)).all()
        return {(value.value if hasattr(value, "value") else value): count
                for value, count in rows}

    async def counts_by_status(self) -> dict[str, int]:
        """Incident counts grouped by lifecycle status, as ``{status: count}``."""
        return await self._counts_by(Incident.status)

    async def counts_by_service_type(self) -> dict[str, int]:
        """Incident counts grouped by service type, as ``{service_type: count}``."""
        return await self._counts_by(Incident.service_type)

    async def counts_by_priority(self) -> dict[str, int]:
        """Incident counts grouped by priority, as ``{priority: count}``."""
        return await self._counts_by(Incident.priority)

    async def total_incidents(self) -> int:
        """Total number of non-deleted incidents."""
        stmt = select(func.count()).select_from(Incident).where(Incident.deleted_at.is_(None))
        return int((await self.session.execute(stmt)).scalar_one())

    async def open_incidents(self) -> int:
        """Number of incidents not yet in a terminal state (verified/cancelled/rejected)."""
        stmt = (
            select(func.count())
            .select_from(Incident)
            .where(Incident.deleted_at.is_(None), Incident.status.notin_(_TERMINAL))
        )
        return int((await self.session.execute(stmt)).scalar_one())

    async def organization_counts(self) -> tuple[int, int]:
        """(total, verified) organizations."""
        base = select(func.count()).select_from(Organization).where(
            Organization.deleted_at.is_(None)
        )
        total = int((await self.session.execute(base)).scalar_one())
        verified_stmt = base.where(Organization.is_verified.is_(True))
        verified = int((await self.session.execute(verified_stmt)).scalar_one())
        return total, verified

    async def response_time_samples(self, to_status: IncidentStatus) -> list[float]:
        """Seconds from each incident's creation to when it first reached ``to_status``."""
        first_reach = (
            select(
                IncidentUpdate.incident_id.label("incident_id"),
                func.min(IncidentUpdate.created_at).label("reached_at"),
            )
            .where(IncidentUpdate.to_status == to_status)
            .group_by(IncidentUpdate.incident_id)
            .subquery()
        )
        stmt = select(
            func.extract("epoch", first_reach.c.reached_at - Incident.created_at)
        ).join(first_reach, first_reach.c.incident_id == Incident.id)
        rows = (await self.session.execute(stmt)).scalars().all()
        return [float(r) for r in rows if r is not None]

    async def incident_points(self) -> list[tuple[float, float]]:
        """(latitude, longitude) of every active incident, for coarse area grouping."""
        stmt = select(Incident.location).where(Incident.deleted_at.is_(None))
        geoms = (await self.session.execute(stmt)).scalars().all()
        return [from_point(g) for g in geoms if g is not None]

    async def audit_action_count(self, action: str) -> int:
        """Number of audit entries for a given action (used to cross-check live counts)."""
        stmt = select(func.count()).select_from(AuditLog).where(AuditLog.action == action)
        return int((await self.session.execute(stmt)).scalar_one())
