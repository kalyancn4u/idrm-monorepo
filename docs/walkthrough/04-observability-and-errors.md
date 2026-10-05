# Chapter 4 — Observability & Errors

*How the system tells you what it's doing, and fails in one predictable shape.*

**By the end of this chapter you will be able to:** explain why logs are structured JSON,
read a log line, describe how secrets are kept out of logs, and trace how every error —
yours or the framework's — becomes one consistent envelope.

Files: [`app/core/logging.py`](../../code/app/core/logging.py),
[`app/core/exceptions.py`](../../code/app/core/exceptions.py).

---

## Why logs are JSON, not prose

Every log line is a **single JSON object**, not a human sentence.[1] Machines (log
aggregators, dashboards, alerts) can then filter and group by any field — `level`,
`logger`, `request_id`, `path` — instead of grepping free text.

```python
# app/core/logging.py — the emitted shape (trimmed)
payload = {
    "ts": ...,                      # ISO-8601 UTC, millisecond precision
    "level": record.levelname,
    "logger": record.name,
    "request_id": getattr(record, "request_id", "-"),   # the correlation id (Ch 3)
    "message": record.getMessage(),
}
```

🧠 **Nuance:** structured logs capture the **elements of circumstance** — who/what/
when/where/outcome — as fields, so an incident can be reconstructed after the fact.[2]

> **Footnotes**
>
> - **[1]** ***Structured logging*** = log records as key/value data rather than prose. "user 5 did X" becomes `{"user_id": 5, "action": "X"}` — queryable, aggregatable, and stable across code changes.
> - **[2]** Extra fields ride along under `extra_fields` and are merged into the JSON. A handler logs `logger.info("incident.create", extra={"extra_fields": {"incident_id": ..., "priority": ...}})` and those become first-class columns.

---

## The request id ties every line together

A logging **filter** stamps the current `request_id` (from the contextvar set in
middleware, Ch 3) onto *every* record automatically:

```python
# app/core/logging.py
class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()   # per-request, async-safe
        return True
```

So filtering the logs by one `request_id` replays a single request end-to-end — across
middleware, service, and repository — with zero manual plumbing.[1]

> **Footnotes**
>
> - **[1]** A ***logging filter*** is a hook that can enrich or drop records before they're formatted. Here it *enriches* every record with the contextvar value, which is why no code needs to pass the id around by hand.

---

## Secrets and PII never reach the logs

Before any `extra_fields` are emitted, a recursive **redactor** masks known-sensitive
keys — a safety net so a careless `extra={...}` can't leak a password or token.[1]

```python
# app/core/logging.py (trimmed)
_REDACT_KEYS = frozenset({"password", "password_hash", "token", "access_token",
                          "refresh_token", "authorization", "secret", ...})
def _redact(value):
    if isinstance(value, dict):
        return {k: ("***" if k.lower() in _REDACT_KEYS else _redact(v)) for k, v in value.items()}
    ...
```

⚠️ **Pitfall:** redaction is defense-in-depth, **not** a licence to log sensitive data
and rely on the mask. The first rule is still "don't put secrets in `extra_fields`."[2]

> **Footnotes**
>
> - **[1]** ***PII*** = Personally Identifiable Information. India's ***DPDP*** Act 2023 (Digital Personal Data Protection) requires care with personal data; masking secrets/PII in logs is one concrete control. The redactor recurses into nested dicts and lists so a buried `token` is still caught.
> - **[2]** A denylist can only mask keys it knows. New sensitive fields must be added to `_REDACT_KEYS` — and the safer habit is to log identifiers (a `user_id`) rather than the data itself.

---

## Installing it: one formatter, one handler

`configure_logging` (called first thing in `main.py`) replaces the root logger's handlers
with a single JSON handler carrying the redaction-aware formatter and the id filter:

```python
# app/core/logging.py (trimmed)
def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(RequestIdFilter())
    root = logging.getLogger(); root.handlers.clear()
    root.addHandler(handler); root.setLevel(level.upper())
```

Logs go to **stdout** — the right choice for a `systemd`/container world where the
platform captures and ships stdout.[1]

> **Footnotes**
>
> - **[1]** Logging to stdout (not to files the app manages) is another 12-factor principle: treat logs as an event *stream*. `systemd`'s journal (or a container runtime) captures it; rotation and shipping are the platform's job, not the app's.

---

## Errors: one envelope for everything

Now the other half of observability — failures. The API returns **one error shape**,
always:[1]

```json
{ "error": { "code": "not_found", "message": "Incident not found.", "details": [] } }
```

Your code raises a typed `AppError`; it carries the HTTP status, a **machine-readable
`code`**, a human message, optional field details, and even response headers:

```python
# app/core/exceptions.py (trimmed)
class AppError(Exception):
    def __init__(self, status_code, code, message, details=None, headers=None):
        self.status_code, self.code, self.message = status_code, code, message
        self.details, self.headers = details or [], headers or {}
```

> **Footnotes**
>
> - **[1]** A stable ***error envelope*** with a machine `code` lets clients branch on `error.code == "already_accepted"` reliably, while the `message` stays free to improve or be translated. Contrast an app that returns bare strings or inconsistent shapes — every client then parses differently and breaks often.

---

## Three handlers cover every failure

`register_exception_handlers` wires three handlers so **domain errors, validation errors,
and framework HTTP errors all leave as the same envelope**:[1]

```python
# app/core/exceptions.py (trimmed)
@app.exception_handler(AppError)            # your raised errors → their status + code (+ headers)
@app.exception_handler(RequestValidationError)   # Pydantic 422 → {code: "validation_error", details:[...]}
@app.exception_handler(StarletteHTTPException)    # 401/403/404/… → mapped code
```

So a bad body (Pydantic), a business rule (`AppError`), and a 404 from the framework are
indistinguishable in *shape* to a client — only the `code` differs.[2]

> **Footnotes**
>
> - **[1]** The validation handler flattens Pydantic's error list into `details: [{field, issue}]`, so a client can highlight the offending field. That's why endpoints don't need try/except around parsing — invalid input is turned into a clean `422` centrally.
> - **[2]** This is where `rate_limit`'s `AppError(429, ..., headers={"Retry-After": ...})` becomes a real response with a real header — the envelope carries headers through the handler (Ch 6).

---

## Recap & what's next

- Logs are **structured JSON** on stdout, each line carrying the **`request_id`**;
  secrets/PII are **redacted**.
- Every failure — yours, Pydantic's, or the framework's — becomes **one error envelope**
  with a machine `code`.
- Observability + a predictable error contract are what make the system *operable* and
  its clients *robust*.

🛠️ **Try it:** `POST /api/v1/incidents` with an out-of-range latitude. You'll get a
`422` whose `error.code` is `validation_error` and whose `details` name the bad field —
produced entirely by the central handler, not the endpoint.

**Next:** [Chapter 5 — The Data Layer](05-the-data-layer.md), where we meet the async
engine, the session lifecycle, and how the schema is built and evolved.
