"""Pagination envelope helper — the one place that builds the API's ``{data, pagination}`` shape.

Every list endpoint returns the same contract shape (doc 40 §2): a ``data`` array plus a
``pagination`` object. Centralising it here keeps that shape — and the ceiling-division for
``total_pages`` — correct in exactly one place (DRY), so a future contract tweak is a single edit.
"""

from __future__ import annotations

from typing import Any


def total_pages(total: int, limit: int) -> int:
    """Number of pages needed for ``total`` items at ``limit`` per page (ceiling division).

    Returns 0 when ``limit`` is non-positive, guarding against division by zero (endpoints already
    constrain ``limit >= 1``, but the helper stays safe on its own).
    """
    if limit <= 0:
        return 0
    return (total + limit - 1) // limit


def paginate(data: list[Any], page: int, limit: int, total: int) -> dict[str, Any]:
    """Wrap an already-serialised ``data`` list in the standard ``{data, pagination}`` envelope."""
    return {
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages(total, limit),
        },
    }
