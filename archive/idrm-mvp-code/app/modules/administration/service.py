"""Administration module service — reference data + an admin oversight overview (roadmap §13.5).

User/role administration itself lives in the USR module (``PATCH /users/{id}`` etc., PICS-ADM-002) —
this module does not duplicate it (DRY). It adds the admin-only reference data (PICS-ADM-001) and a
small account/provider oversight summary.
"""

from __future__ import annotations

from typing import Any

from app.modules.administration.reference import build_reference_data
from app.modules.administration.repository import AdministrationRepository


class AdministrationService:
    """Reference data and platform oversight for administrators."""

    def __init__(self, repo: AdministrationRepository) -> None:
        self.repo = repo

    @staticmethod
    def reference_data() -> dict[str, Any]:
        """The platform's controlled vocabularies + the incident state machine (PICS-ADM-001)."""
        return build_reference_data()

    async def overview(self) -> dict[str, Any]:
        """Admin oversight snapshot: users by role, users by status, orgs pending verification."""
        return {
            "users_by_role": await self.repo.users_by_role(),
            "users_by_status": await self.repo.users_by_status(),
            "organizations_pending_verification": await self.repo.pending_organization_count(),
        }
