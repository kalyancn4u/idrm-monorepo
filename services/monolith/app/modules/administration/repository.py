"""Administration module repository — account/provider oversight counts (admin view)."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.resources.models import Organization
from app.modules.users.models import User


class AdministrationRepository:
    """Async aggregate reads for the admin oversight overview."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def users_by_role(self) -> dict[str, int]:
        """Count non-deleted users grouped by role, as ``{role: count}``."""
        stmt = (
            select(User.role, func.count())
            .where(User.deleted_at.is_(None))
            .group_by(User.role)
        )
        return {role.value: count for role, count in (await self.session.execute(stmt)).all()}

    async def users_by_status(self) -> dict[str, int]:
        """Count non-deleted users grouped by account status, as ``{status: count}``."""
        stmt = (
            select(User.status, func.count())
            .where(User.deleted_at.is_(None))
            .group_by(User.status)
        )
        return {status.value: count for status, count in (await self.session.execute(stmt)).all()}

    async def pending_organization_count(self) -> int:
        """Number of organizations still awaiting coordinator verification."""
        stmt = select(func.count()).select_from(Organization).where(
            Organization.deleted_at.is_(None), Organization.is_verified.is_(False)
        )
        return int((await self.session.execute(stmt)).scalar_one())
