"""A simple in-process, per-endpoint rate limiter (roadmap §8.3; doc 22 §6).

Keyed by (endpoint-name, client IP), fixed sliding window. Exceeding the budget raises
``429 rate_limit_exceeded`` with a ``Retry-After`` header. This is deliberately in-process and
single-box — **centralised/distributed rate limiting + a WAF arrive with APISIX (→ FFP)**. It is
an adequate abuse guard for the MVP.
"""

from __future__ import annotations

import time
from collections import defaultdict
from collections.abc import Callable

from fastapi import Request

from app.core.exceptions import AppError

# (endpoint-name, client-ip) -> list of hit timestamps (monotonic seconds)
_hits: dict[tuple[str, str], list[float]] = defaultdict(list)


def reset() -> None:
    """Clear all counters (used between tests)."""
    _hits.clear()


def rate_limit(name: str, limit: int, window_seconds: int = 60) -> Callable[[Request], None]:
    """Return a FastAPI dependency allowing ``limit`` requests per ``window`` per client IP."""

    def _dependency(request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = (name, client_ip)
        now = time.monotonic()
        window_start = now - window_seconds
        recent = [t for t in _hits[key] if t >= window_start]
        if len(recent) >= limit:
            retry_after = max(1, int(window_seconds - (now - recent[0])) + 1)
            raise AppError(
                429,
                "rate_limit_exceeded",
                "Too many requests. Please slow down and try again shortly.",
                headers={"Retry-After": str(retry_after)},
            )
        recent.append(now)
        _hits[key] = recent

    return _dependency
