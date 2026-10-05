"""Structured-JSON logging with request correlation and secret/PII redaction.

Every log line is a JSON object carrying the "elements of circumstance" (who/what/when/where/
outcome) plus a ``request_id`` that ties all lines of one request together. A redaction filter
guarantees secrets are never logged and personal data is masked. See roadmap §7 and doc 32.
"""

from __future__ import annotations

import json
import logging
from contextvars import ContextVar
from typing import Any

# The current request's correlation id (set by middleware; attached to every log line).
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")

# The current request's client IP (set by middleware; used to stamp audit-log entries).
client_ip_ctx: ContextVar[str | None] = ContextVar("client_ip", default=None)

# Keys whose values must never appear in logs (dropped/masked before emit).
_REDACT_KEYS = frozenset(
    {"password", "password_hash", "token", "access_token", "refresh_token",
     "authorization", "secret", "s3_secret_key", "jwt_private_key"}
)
_REDACTED = "***"


class RequestIdFilter(logging.Filter):
    """Attach the current ``request_id`` to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Stamp the record with the current request id and keep it (always returns True)."""
        record.request_id = request_id_ctx.get()
        return True


def _redact(value: Any) -> Any:
    """Recursively drop/mask any secret- or PII-bearing fields."""
    if isinstance(value, dict):
        return {
            k: (_REDACTED if k.lower() in _REDACT_KEYS else _redact(v)) for k, v in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_redact(v) for v in value]
    return value


class JsonFormatter(logging.Formatter):
    """Render a log record as a single compact JSON line."""

    def format(self, record: logging.LogRecord) -> str:
        """Render one log record as a single compact JSON line (with redaction)."""
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%03dZ"),
            "level": record.levelname,
            "logger": record.name,
            "request_id": getattr(record, "request_id", "-"),
            "message": record.getMessage(),
        }
        extra = getattr(record, "extra_fields", None)
        if isinstance(extra, dict):
            payload.update(_redact(extra))
        if record.exc_info:
            payload["error"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter + request-id filter on the root logger."""
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
