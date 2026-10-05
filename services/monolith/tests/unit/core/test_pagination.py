"""Unit tests for the pagination envelope helper (pure — no database, runs anywhere)."""

from __future__ import annotations

import pytest

from app.core.pagination import paginate, total_pages


@pytest.mark.parametrize(
    ("total", "limit", "expected"),
    [
        (0, 20, 0),      # no items -> no pages
        (1, 20, 1),      # a single item still needs one page
        (20, 20, 1),     # exact fit
        (21, 20, 2),     # one over -> rounds up (ceiling division)
        (137, 20, 7),    # 6 full pages + a remainder
        (100, 25, 4),    # exact multiple
        (5, 0, 0),       # non-positive limit is guarded (no ZeroDivisionError)
    ],
)
def test_total_pages(total: int, limit: int, expected: int) -> None:
    assert total_pages(total, limit) == expected


def test_paginate_wraps_data_and_meta() -> None:
    data = [{"id": 1}, {"id": 2}]
    result = paginate(data, page=2, limit=20, total=137)
    assert result == {
        "data": data,
        "pagination": {"page": 2, "limit": 20, "total": 137, "total_pages": 7},
    }


def test_paginate_empty() -> None:
    result = paginate([], page=1, limit=20, total=0)
    assert result["data"] == []
    assert result["pagination"]["total_pages"] == 0
