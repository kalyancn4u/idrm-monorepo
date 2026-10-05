# IDRM MVP — Logging & Diagnostics (Low-Level Design)

> *Type: Document (LLD / deep-dive) · Audience: complete novices → backend & ops engineers · Status: MVP — current*
> *The deep-dive behind [`27-implementation-roadmap.md`](27-implementation-roadmap.md) §7. It specifies **exactly
> what IDRM writes to its logs, in what shape, where they go, and what must never appear in them** — so that when
> something goes wrong at 2 a.m. during a flood, an engineer can find the one request that failed in seconds, and
> so that no citizen's private data ever leaks into a log file. Format decision (yours): **structured JSON**.
> Heavy central observability (Prometheus/Grafana/Loki/Tempo, distributed tracing) is deliberately **→ FFP**;
> the MVP keeps logging simple, native, and correct.*

---

## 1. Why logs — and how they differ from the audit trail

A **log** is the application's **diary**: a timestamped stream of "here's what just happened" entries the app writes
as it runs. We keep them for three reasons: **debugging** (why did this fail?), **tracing** (what was the sequence
of events for this one request?), and **operations** (is the system healthy, fast, and coping with load?).

There is a second kind of record in IDRM, and confusing the two is a classic beginner mistake, so let's separate
them cleanly:

| | **Application logs** (this document) | **Audit trail** (`audit_logs` table) |
|---|---|---|
| **What** | the operational diary — requests, timings, errors | a tamper-evident business record: *who* did *what* to *which* resource |
| **Where** | text/JSON to the OS log stream (journald/files) | a database table ([`50-data-model.md`](50-data-model.md)), read via `GET /audit-logs` |
| **Audience** | engineers & operators, short-lived | coordinators/admins & compliance, long-lived |
| **Example** | `{"level":"INFO","event":"incident.create","status":201,"latency_ms":42}` | "user *X* changed incident *Y* from `accepted`→`in_progress` at *T*" |

> **Rule of thumb:** if it helps an *engineer* fix or run the system, it's a **log**; if it holds someone
> *accountable* for a business action, it's an **audit entry**. IDRM keeps both. This doc is about the first;
> audit is specified in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).

New to the broader topic? [`observability-101.md`](../../guides/mvp/learn/observability-101.md) and
[`monitoring-101.md`](../../guides/mvp/learn/monitoring-101.md) are the primers (much of what they describe is the
FFP target; the MVP does the essentials).

## 2. Structured JSON — what one log line looks like

You chose **structured logging**: every entry is a small **JSON** record, not a free-form sentence. It reads
slightly less prettily to the naked eye, but it is **searchable and filterable** ("show me every `ERROR` for
request `abc123`") and it flows into the FFP observability tools with zero rework.

A typical line:
```json
{ "ts": "2026-08-17T09:12:00.042Z", "level": "INFO", "logger": "incidents.service",
  "event": "incident.create", "request_id": "req_7f3a…", "user_id": "9f1c…", "role": "citizen",
  "method": "POST", "path": "/api/v1/incidents", "status": 201, "latency_ms": 42,
  "resource": "incident", "resource_id": "a2b4…", "outcome": "success" }
```

Those fields are the **"elements of circumstance"** you asked for — the *who / what / when / where / outcome* of
every noteworthy event, made uniform:

| Element | Field(s) | Example |
|---|---|---|
| **When** | `ts` (UTC, millisecond) | `2026-08-17T09:12:00.042Z` |
| **Who** | `user_id`, `role` (or `guest`) | `citizen` |
| **What** | `event`, `method`, `path`, `resource`, `resource_id` | `incident.create` |
| **Where** (in code) | `logger` (module.layer) | `incidents.service` |
| **Outcome** | `status`, `outcome`, `latency_ms`, `error.code` | `201 / success / 42 ms` |
| **Correlation** | `request_id` | ties every line of one request together (§4) |

## 3. Log levels — say the right amount

A **level** is how loud/important an entry is. Using them well means production stays quiet until something
actually needs attention:

| Level | Use it for | IDRM example |
|---|---|---|
| `DEBUG` | developer detail, **off in production** | "computed proximity radius = 5 km" |
| `INFO` | normal, noteworthy events | `incident.create`, `user.login`, a completed background job |
| `WARNING` | recoverable oddities worth noticing | a notification send failed and was queued for retry; a slow query |
| `ERROR` | a request/operation failed | unhandled exception (with stack trace + `request_id`) |
| `CRITICAL` | the system itself is in danger | cannot reach PostgreSQL; disk nearly full |

> **Novice guidance:** default production level is **INFO**. If logs are noisy, raise the bar; if an incident is
> being investigated, temporarily lower it to `DEBUG` for detail. Every `ERROR`/`CRITICAL` must carry a
> `request_id` so it can be traced (§4).

## 4. Correlation — the `request_id` thread

This is the single most useful idea in the whole document. Every incoming request is stamped with a unique
**`request_id`** (the `X-Request-Id` from [`40-api-specification.md`](40-api-specification.md) §2 — generated at the
edge, or accepted from the reverse proxy). That id is stored in a **context variable** and **automatically attached
to every log line** produced while handling that request — across all layers — and **echoed back to the client** in
the `X-Request-Id` response header.

So a single request weaves one traceable thread:
```
request_id=req_7f3a…  INFO  incidents.router   request.start   POST /api/v1/incidents
request_id=req_7f3a…  DEBUG incidents.service  validation.ok
request_id=req_7f3a…  INFO  incidents.service  incident.create resource_id=a2b4…
request_id=req_7f3a…  INFO  incidents.router   request.end     status=201 latency_ms=42
```

Filter the logs by that one id and you have the *complete story* of that request — which is exactly how §8's
2-a.m. diagnosis works.

## 5. What to log at each layer (and what never to)

Mapped to the §5 code layers:

- **Router (edge):** one `request.start` and one `request.end` line per call (method, path, status, latency).
- **Service (brain):** the meaningful **business events** — `incident.create`, `incident.accept`,
  `org.verify` — with the resource id and outcome. This is the layer that tells the story.
- **Repository (memory):** normally silent; a `WARNING` for a **slow query** (over a threshold) is valuable.
- **Background jobs:** start/finish/failure of each job, with its own `request_id`-style job id.
- **Errors:** every unhandled exception → one `ERROR` with the **stack trace**, the `request_id`, and the
  user-facing error `code` (§4.6) — never a second, duplicate log for the same failure.

**Never log** (this is a hard rule, not a preference): passwords, password hashes, JWT/refresh tokens, reset
tokens, API keys, full card/ID numbers, or raw request bodies that contain them. See §6.

## 6. Privacy & redaction (DPDP Act 2023)

IDRM serves disaster-affected, often vulnerable people; India's **DPDP — Digital Personal Data Protection Act,
2023** — and plain decency require that logs never become a personal-data leak. So a **redaction filter** sits in
the logging setup and enforces:

- **Secrets are never logged** — a deny-list of fields (`password`, `token`, `authorization`, `refresh_token`, …)
  is dropped/masked before any line is written.
- **Personal data is minimised & masked** — prefer opaque `user_id` (a UUID) over name/email/phone; where a
  contact must appear, **mask** it (`+9198••••3210`, `r••••@gmail.com`).
- **No location surveillance by accident** — an incident's location comes only from the user's chosen map pin;
  photo **EXIF/GPS is stripped on upload** ([`40-api-specification.md`](40-api-specification.md) §5.7) and never
  logged. File **bytes** are never logged (only the MinIO key).
- **Least data, shortest time** — log only what a diagnosis needs, and rotate/expire it (§7).

> **Why this is designed in, not bolted on:** redaction lives in `core/logging.py` (§5.3) as a filter every logger
> inherits, so an engineer *cannot* accidentally leak a secret by writing a naïve log line — the filter catches it.

## 7. Where logs go, and for how long (MVP)

Native and simple, matching the ops model ([`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md);
no Redis, no Docker in the MVP):

- The app writes JSON logs to **stdout**; **systemd** captures them into **journald** (and/or a rotating file under
  `/var/log/idrm/`).
- **Rotation & retention:** `logrotate` (or journald limits) caps size and keeps ~**14–30 days** (a tunable), so
  disks never fill (a `CRITICAL` cause). The **audit trail** — the accountability record — is kept **longer**, per
  the retention policy in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).
- **No central aggregation in the MVP.** Shipping logs to a cluster (Loki/ELK), metrics (Prometheus/Grafana), and
  distributed tracing (OpenTelemetry/Tempo) are the **FFP** upgrade (§9) — the JSON format is chosen so that
  upgrade is drop-in.

## 8. The diagnostics workflow (why all of this pays off)

A concrete 2-a.m. story, end to end:

1. A responder sees an error toast; the app shows a support code — the **`X-Request-Id`** (`req_7f3a…`) from the
   response header.
2. The on-call engineer runs one command on the box — e.g. `journalctl -u idrm | grep req_7f3a…` — and instantly
   sees **every** log line for that exact request: the inputs, the layer it failed in, the stack trace, the
   `error.code`.
3. Because levels and events are consistent, they know *what* failed and *where* without reproducing it. Fix,
   deploy, done — and a matching **audit** entry (if a business action was involved) remains for the record.

*That* is the return on structured logging + a correlation id: minutes to diagnosis instead of hours of guessing.

## 9. How we verify it — and the FFP seam

**Verification (§10 of the roadmap):** automated tests assert that (a) logs are valid JSON with the required
fields, (b) every request produces a `request_id` that also appears in the response header, and (c) a login/upload
test proves **no secret or PII** appears in the emitted logs (a redaction test). Per Task N, each module's logging
is covered by its own tests.

**FFP seam:** the same JSON logs flow into **Loki/ELK**; **OpenTelemetry** adds distributed **traces** (following a
request across future microservices) and **Prometheus/Grafana** add **metrics/dashboards/alerts**. Nothing about
the MVP's log *shape* changes — that's the whole point of choosing structured JSON now. (Decisions:
[`21-architecture-decisions.md`](21-architecture-decisions.md); FFP observability doc.)

---

*Related:* roadmap [`27-implementation-roadmap.md`](27-implementation-roadmap.md) §7 · security & audit [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) ·
data flow [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) (§3 request-id) · API [`40-api-specification.md`](40-api-specification.md) (X-Request-Id) ·
ops [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md) · concurrency [`31-concurrency-and-thread-model.md`](31-concurrency-and-thread-model.md) ·
primers [`observability-101.md`](../../guides/mvp/learn/observability-101.md) · [`monitoring-101.md`](../../guides/mvp/learn/monitoring-101.md) · [`secure-coding-101.md`](../../guides/mvp/learn/secure-coding-101.md).
