"""
core/redis.py — the shared async Redis client + a best-effort publish helper (M5).

Redis backs caching, sessions, rate-limiting and — relevant here — **pub/sub**:
the backend PUBLISHES events (new/updated requests, new notifications) to channels
that the Bun gateway (G4) SUBSCRIBES to and fans out over WebSocket.

`publish_json` is deliberately **best-effort**: real-time delivery is a
nice-to-have, so a Redis hiccup must never break the actual API request. Failures
are logged and swallowed; the HTTP call still succeeds.

Rookie note: the client is created lazily (on first use), so importing this module
— and therefore booting the app — does NOT require Redis to be running.
"""
import json
import logging
from typing import Any

import redis.asyncio as aioredis

from core.config import settings

logger = logging.getLogger(__name__)

# Channel names the gateway subscribes to — kept in one place so both sides agree.
CHANNEL_SERVICE_REQUESTS = "service_requests"
CHANNEL_NOTIFICATIONS = "notifications"

_redis: aioredis.Redis | None = None


def get_redis() -> aioredis.Redis:
    """Return the shared async Redis client, creating it on first use."""
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis


async def publish_json(channel: str, payload: dict[str, Any]) -> None:
    """Publish `payload` as JSON to `channel`. Best-effort — never raises.

    `default=str` lets non-JSON-native values (UUID, datetime) serialize cleanly.
    A Redis outage logs a warning and returns; it must not break the API call that
    triggered the event.
    """
    try:
        await get_redis().publish(channel, json.dumps(payload, default=str))
    except Exception as exc:  # noqa: BLE001 — best-effort delivery; log and continue
        logger.warning("Redis publish to channel %r failed: %s", channel, exc)


async def cache_get_json(key: str) -> Any | None:
    """Best-effort cache read: GET `key` and JSON-decode it. Returns None on a miss
    OR any Redis error (so callers transparently fall back to recomputing)."""
    try:
        raw = await get_redis().get(key)
    except Exception as exc:  # noqa: BLE001 — cache is optional; degrade gracefully
        logger.warning("Redis GET %r failed: %s", key, exc)
        return None
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except (TypeError, ValueError):
        return None


async def cache_set_json(key: str, value: Any, ttl_seconds: int) -> None:
    """Best-effort cache write: JSON-encode `value` and SET it with a TTL. Never
    raises — a cache write failure must not break the request."""
    try:
        await get_redis().set(key, json.dumps(value, default=str), ex=ttl_seconds)
    except Exception as exc:  # noqa: BLE001 — cache is optional; log and continue
        logger.warning("Redis SET %r failed: %s", key, exc)
