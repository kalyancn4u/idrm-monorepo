"""Reports module service — operational metrics + CSV export (roadmap §13.5; PICS-RPT-001/002/003).

Reads live data via the repository and shapes three reports: a **dashboard** (incidents by status /
type / priority / coarse area, + organization counts), **response-times** (created→accepted and
created→verified, avg + median), and **fulfillment** (resolution + verification rates, cross-checked
against the audit trail). Any report can be exported as CSV.
"""

from __future__ import annotations

import csv
import io
from statistics import mean, median
from typing import Any

from app.core.exceptions import AppError
from app.modules.incidents.lifecycle import IncidentStatus
from app.modules.locations.geo import reverse_geocode
from app.modules.reports.repository import ReportRepository

_REPORTS = {"dashboard", "response-times", "fulfillment"}


def _summary(samples: list[float]) -> dict[str, Any]:
    """Count + average + median (seconds) for a set of durations."""
    if not samples:
        return {"count": 0, "avg_seconds": None, "median_seconds": None}
    return {
        "count": len(samples),
        "avg_seconds": round(mean(samples), 1),
        "median_seconds": round(median(samples), 1),
    }


class ReportService:
    """Compute operational reports from live incident / organization / audit data."""

    def __init__(self, repo: ReportRepository) -> None:
        self.repo = repo

    async def dashboard(self) -> dict[str, Any]:
        """Live overview: incident totals + counts by status/type/priority/region + org counts."""
        total, verified = await self.repo.organization_counts()
        points = await self.repo.incident_points()
        by_region: dict[str, int] = {}
        for latitude, longitude in points:
            region = reverse_geocode(latitude, longitude)["region"]
            by_region[region] = by_region.get(region, 0) + 1
        return {
            "total_incidents": await self.repo.total_incidents(),
            "open_incidents": await self.repo.open_incidents(),
            "by_status": await self.repo.counts_by_status(),
            "by_service_type": await self.repo.counts_by_service_type(),
            "by_priority": await self.repo.counts_by_priority(),
            "by_region": by_region,
            "organizations": {"total": total, "verified": verified},
        }

    async def response_times(self) -> dict[str, Any]:
        """Time-to-accept and time-to-resolve summaries (count/avg/median seconds)."""
        accepted = await self.repo.response_time_samples(IncidentStatus.accepted)
        verified = await self.repo.response_time_samples(IncidentStatus.verified)
        return {
            "time_to_accept": _summary(accepted),
            "time_to_resolve": _summary(verified),
        }

    async def fulfillment(self) -> dict[str, Any]:
        """Resolution + verification rates, cross-checked against the audit trail (PICS-RPT-002)."""
        by_status = await self.repo.counts_by_status()
        total = await self.repo.total_incidents()
        resolved = by_status.get("completed", 0) + by_status.get("verified", 0)
        verified = by_status.get("verified", 0)
        return {
            "total_incidents": total,
            "resolved": resolved,
            "verified": verified,
            "cancelled": by_status.get("cancelled", 0),
            "rejected": by_status.get("rejected", 0),
            "fulfillment_rate": round(resolved / total, 3) if total else 0.0,
            "verification_rate": round(verified / resolved, 3) if resolved else 0.0,
            # PICS-RPT-002: cross-check the live count against the append-only audit trail.
            "verified_from_audit": await self.repo.audit_action_count("incident.verify"),
        }

    async def build(self, name: str) -> dict[str, Any]:
        """Return the named report as a dict, or raise 404 for an unknown name."""
        if name == "dashboard":
            return await self.dashboard()
        if name == "response-times":
            return await self.response_times()
        if name == "fulfillment":
            return await self.fulfillment()
        raise AppError(404, "not_found", f"Unknown report '{name}'.")

    async def export_csv(self, name: str) -> str:
        """Render the named report as CSV (a flat ``metric,value`` sheet)."""
        report = await self.build(name)
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(["metric", "value"])
        for key, value in _flatten(report):
            writer.writerow([key, value])
        return buffer.getvalue()


def _flatten(data: dict[str, Any], prefix: str = "") -> list[tuple[str, Any]]:
    """Flatten nested report dicts into dotted ``key, value`` rows for CSV."""
    rows: list[tuple[str, Any]] = []
    for key, value in data.items():
        full = f"{prefix}{key}"
        if isinstance(value, dict):
            rows.extend(_flatten(value, prefix=f"{full}."))
        else:
            rows.append((full, value))
    return rows
