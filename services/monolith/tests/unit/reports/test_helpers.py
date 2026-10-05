"""Unit tests for the pure report helpers (no database) — summary stats and CSV flattening."""

from __future__ import annotations

from app.modules.reports.service import _flatten, _summary


def test_summary_empty() -> None:
    assert _summary([]) == {"count": 0, "avg_seconds": None, "median_seconds": None}


def test_summary_computes_avg_and_median() -> None:
    result = _summary([10.0, 20.0, 60.0])
    assert result["count"] == 3
    assert result["avg_seconds"] == 30.0
    assert result["median_seconds"] == 20.0


def test_flatten_nested_dict() -> None:
    rows = dict(_flatten({"total": 2, "by_status": {"created": 1, "verified": 1}}))
    assert rows["total"] == 2
    assert rows["by_status.created"] == 1
    assert rows["by_status.verified"] == 1
