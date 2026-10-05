# Changelog — IDRM MVP Application Code

All notable changes to the IDRM MVP code (`code/`) are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); driven by the build plan in
[`../docs/mvp/27-implementation-roadmap.md`](../docs/mvp/27-implementation-roadmap.md) §13.

## [Unreleased]

### Changed — 2026-08-22 (F3 — DRY the pagination envelope into one core helper)
- **New `app/core/pagination.py`** — `paginate(data, page, limit, total)` builds the standard
  `{data, pagination}` envelope, and `total_pages(total, limit)` holds the single ceiling-division (with a
  divide-by-zero guard). The `{page, limit, total, total_pages}` shape + arithmetic had been **hand-copied
  at 8 sites across 6 modules** (audit, incidents ×3, notifications, resources ×2, users); now there is one
  source of truth, so a future contract tweak is a one-line change and the ceiling-division can't drift.
- **All 8 list endpoints** now return `paginate(...)`; 0 residual hand-built pagination dicts remain.
- **Tests:** `tests/unit/core/test_pagination.py` — a **pure, dependency-free** unit test (exact fit, ceiling
  remainder, empty, and the zero-limit guard). It was **executed on this box and passes** (no DB needed);
  the existing per-endpoint API tests already assert the envelope shape.
- **Quality:** **`ruff check app tests` clean**, `compileall` clean. Pure refactor — no behavior change, same
  wire output. `code/` only (the archive snapshot is frozen).

### Added — 2026-08-22 (F5-B — GET /incidents filters the contract already promised)
- **`incidents` list now honors `priority`, `q` (free-text), and `sort`** — filters the OpenAPI advertised
  but the code had never wired (it did only `status` + `service_type`). The schema was already built for all
  three (migration 0002: `ix_incidents_priority`, a GIN `to_tsvector('english', description)` index, and
  `ix_incidents_created_at`), so this **activates indexes that were dead weight** and makes code = contract =
  schema agree.
  - `priority` — exact-match filter (repository + service + router).
  - `q` — PostgreSQL full-text over the description via
    `to_tsvector('english', description) @@ plainto_tsquery('english', :q)`, so it **uses the GIN index**
    (deliberately not `ILIKE`, which would scan). Capped at 100 chars.
  - `sort` — **strictly whitelisted** to `created_at` / `priority` (with a leading `-` for descending);
    anything else → `422 invalid_sort`. No arbitrary-column sorting (KISS + avoids injection). Default stays
    newest-first. (`SORTABLE_FIELDS` + `resolve_order` in `incidents/repository.py`, validated in the service.)
- **Tests (Task N):** `tests/api/incidents/test_list_filters.py` — priority filter, full-text hit/miss,
  ascending/descending priority sort, and invalid-sort 422.
- **Quality:** **`ruff check app tests` clean**, `compileall` clean. Not executed here (needs PostgreSQL);
  `PICS-INC-*` stays `Planned` until the green run. `code/` only (the archive snapshot is frozen).

### Changed — 2026-08-22 (Task K — public-surface docstring pass; honest coverage)
- **Docstrings added across all ten modules** (Session-6 coherence work). An AST scan found **193 of 387**
  defs undocumented despite earlier "Task K honored" notes; a *public-surface* pass added **~96** docstrings
  to endpoint functions, service methods, and repository methods (plus two `core/logging` overrides). The
  remaining ~95 undocumented defs are Pydantic **schema classes** (self-describing fields), `__init__`, and
  trivial private helpers — intentionally out of scope for this pass.
- **Corrected the record:** the Increment-4 "Task K … honored" line is amended to *in progress* — the audit
  trail should not claim completion the code did not have.
- **Quality:** **`ruff check app` clean** (fixed 3 over-length docstrings the pass introduced) and full
  `py_compile`/`compileall` clean. Comments only — no behavior change. Not executed here (no DB); unchanged
  runtime. *Applied in `code/` only; it will land in the `archive/idrm-mvp-code` mirror when that is created
  (T3), per the "mirror last" decision.*

### Added — 2026-08-17 (Increment 1 — repository scaffold)
- **Project skeleton** for the FastAPI modular monolith (roadmap §5): `pyproject.toml` (deps + Black/isort/Ruff/
  mypy/pytest/coverage config), `Makefile` (the §11 task menu), `environment.yml`, `.gitignore`, `.env.example`,
  and the minimal **CI** workflow `.github/workflows/ci.yml` (§12).
- **`app/core/`** — `config.py` (env-driven Pydantic settings), `logging.py` (structured-JSON + `request_id`
  contextvar + secret/PII redaction, §7), `exceptions.py` (the single error envelope + handlers, §4.6),
  `security.py` (bcrypt-12 hashing + RS256 JWT sign/verify), `dependencies.py` (`get_db`, `get_current_claims`,
  `require_role`).
- **`app/infrastructure/database/`** — async SQLAlchemy `engine.py` + `base.py` (declarative Base + UUID/
  timestamps/soft-delete mixins, §3.2).
- **`app/main.py`** — assembles the app: JSON logging, the `X-Request-Id` middleware (start/end logs + echoed
  header), CORS, the error envelope, `/api/v1/health`, and mounts all **ten** module routers (empty stubs until
  each module's build increment).
- **`alembic/`** (async env, no versions yet — baseline migration lands with the users models), **`tests/`**
  (`conftest.py` + a health smoke test), **`frontend/`** (design **tokens** `app.css` from doc 33 + a base
  template), **`scripts/seed.py`** stub.
- **Verified:** all 41 Python files pass `py_compile` (syntax). Full `make qa` (lint/types/tests) runs once the
  dependencies are installed on a target with PostgreSQL/PostGIS + MinIO (roadmap §11).

### Added — 2026-08-17 (Increment 2 — Users/Auth (USR) module)
- **Models** (`app/modules/users/models.py`) — `users`, `user_sessions`, `email_verification_tokens`,
  `password_reset_tokens` + the `user_role` / `user_status` enums (doc 50 §5.1–5.2), on the shared UUID/
  timestamps/soft-delete mixins.
- **Baseline migration** `alembic/versions/0001_users_baseline.py` — `CREATE EXTENSION postgis`, the two enums,
  and the four USR tables + indexes (email/refresh_token/token uniques, role/user_id).
- **Schemas** — the `/auth` + `/users` request/response contract (register/login/verify/refresh/reset/change,
  profile, admin update; `TokenResponse`, `UserResponse`, paginated list).
- **Repository** — async data access (users, sessions, tokens) + an explicit `commit()` for the lockout path.
- **Service** — the auth rules: RS256 access + **rotating** refresh tokens, bcrypt-12, **5-fail / 15-min
  lockout**, email-verification + password-reset token flows (single-use, expiring), profile + admin ops.
  Email delivery is logged as a notification-module seam.
- **Router** — all `/auth/*` and `/users/*` endpoints with two-layer guards (role via `require_role`, the current
  user via `get_current_user`); real **HTTPBearer** token extraction wired into `core/dependencies.py`
  (`get_db` now commits-on-success / rolls-back-on-error).
- **Tests** — unit tests for password hashing (salt, verify, reject) and the lockout policy constants.
- **Fix (self-review):** the failed-login increment is now committed explicitly, so the `401` rollback can't wipe
  the lockout counter.
- **Verified:** all 52 files pass `py_compile`. **Not yet executed here** (no deps / no PostgreSQL+PostGIS on this
  box): the DB-backed API/IT tests + `make qa` run on a target box or in CI. **`PICS-USR-*` rows stay `Planned`**
  until that test run is green (roadmap §14 — a row flips to ✅ only with code **and** a passing test).

### Added — 2026-08-17 (Increment 2b — finish USR: tests + rate-limiting)
- **Per-endpoint rate-limiting** (`app/core/rate_limit.py`) — a simple in-process limiter (login 5/min,
  register 10/min, forgot/resend 3/min, reset 5/min) returning `429` + `Retry-After`; `AppError` extended to carry
  response headers. *(Distributed rate-limiting + WAF = → FFP, APISIX.)*
- **Test infrastructure** (`tests/conftest.py`) — sets a test DB URL + generates an **ephemeral RS256 keypair**
  before importing the app; per-test schema create/drop; async HTTP client; direct DB session; rate-limit reset
  between tests. Unit tests need no database.
- **DB-backed tests:** API (`tests/api/users/test_auth.py`, `test_rate_limit.py`) — register/verify/login,
  duplicate-email 409, privileged-role 403, login-before-verify 403, wrong-password 401, `/users/me` 401/200,
  citizen-forbidden 403, rate-limit 429. Integration (`tests/integration/users/test_flows.py`) — refresh
  **rotation** invalidates the old token, **logout** revokes the session, **5 failures lock** the account, and the
  **password reset is single-use**. Health smoke test moved to async.
- **Quality:** **`ruff check` passes clean** and all 56 files `py_compile`; ruff configured for the FastAPI
  `Depends()` idiom + `str, Enum` compatibility.
- **Honest status:** written + lint/syntax-verified, **not yet executed here** (no deps / no PostgreSQL+PostGIS on
  this box). The suite runs in CI (its Postgres+MinIO services) or on the Ubuntu box; **`PICS-USR-*` flips to ✅
  only after that run is green** (roadmap §14).

### Added — 2026-08-17 (Increment 3 — Incidents (INC) module)
- **Lifecycle state machine** (`app/modules/incidents/lifecycle.py`) — pure, unit-testable: the enums
  (service_type, priority, 8-state incident_status) + the allowed transitions and per-action roles.
- **Models** (`models.py`) — `incidents` (PostGIS `POINT` location, requester nullable=guest, tracking_token,
  `assigned_organization_id` as a plain UUID until ORG lands, rating CHECK 1–5) + `incident_updates` timeline;
  enum types defined once and reused across columns.
- **Migration** `0002_incidents.py` — the three enums, both tables, the **GiST** spatial index, B-tree filters,
  a **GIN full-text** index on description, and the rating check.
- **Schemas / repository / service / router** — create (citizen + **guest** with tracking token; providers 403),
  role-scoped list + `/mine`, **PostGIS `/nearby`** proximity, detail + timeline, pre-accept `PATCH`, and the
  **eight lifecycle transitions** with **single-claim** (first accept wins → 409 `already_accepted`),
  **critical-needs-approval**, illegal-jump → 409 `invalid_transition`, and citizen ownership on verify/cancel.
  Added `get_optional_claims` (guest-allowed auth) to `core/dependencies.py`.
- **Tests** — unit (the state machine); API (guest/citizen/provider-403 create, read-scope, RBAC, invalid
  transition, bad coordinates 422); integration (the full **created→verified** walk incl. critical-approval gate,
  **single-claim**, and **`/nearby`**). Shared `tests/factories.py` builds users of any role.
- **Quality:** **`ruff check` clean**; all 69 files `py_compile`.
- **Deferred (documented TODOs, land with the Organizations module):** the FK on `assigned_organization_id`;
  resolving a provider's org server-side in `accept` (currently supplied in the body); org-membership on
  `start`/`complete`; `/incidents/assigned`; per-endpoint stricter guest rate-limit.
- **Honest status:** written + lint/syntax-verified, **not executed here** (no deps / no PostgreSQL+PostGIS).
  **`PICS-INC-*` stay `Planned`** until a green `make qa` on CI / the Ubuntu box (roadmap §14).

### Added — 2026-08-17 (Increment 4 — Organizations & Resources (ORG/RES) module)
- **Module placement decision:** organizations + resources share one code module
  (`app/modules/resources/`) — doc 50 §2 groups them as the "Providers" data and the locked 10-module
  layout has no separate `organizations` module. Two routers: `/resources` and `/organizations`
  (mounted in `app/main.py`).
- **Models** (`resources/models.py`) — `organizations` (owner_user_id, `org_type` enum, `service_type[]`
  categories, PostGIS service-area point + radius, capacity/availability, verification fields, rating) +
  `resources` (org-owned assets, kind, quantity, optional PostGIS point). The shared `service_type` enum
  instance is **reused** from the incidents module so PostgreSQL creates the type once.
- **MVP relationship model:** one organization per provider (`owner_user_id`); "the provider's org" = the
  org they own. Multi-member orgs (a membership join table) are **→ FFP**.
- **Migration** `0003_organizations_resources.py` — the `org_type` enum, both tables (GiST spatial + GIN
  categories indexes), and finally the **FK** `incidents.assigned_organization_id → organizations.id`
  that migration 0002 deferred.
- **Schemas / repository / service / routers** — `POST/GET/PATCH /organizations`, `/mine`,
  `/{id}/verify` (coordinator/admin), `/{id}/capacity`, `/{id}/availability`; `GET/POST/PATCH /resources`.
  RBAC per doc 40 §5.3; spatial/type/verified filters + proximity ordering (PICS-RES-003 seam);
  one-org-per-provider (409 `already_exists`); verification gate (`org_not_verified`).
- **Wired the deferred INC ↔ ORG links** (all five from Increment 3):
  1. **FK** on `incidents.assigned_organization_id` (model + migration);
  2. **`accept` resolves the provider's own verified org server-side** — `AcceptRequest` no longer carries
     `organization_id`; unverified/no-org → 403 (`org_not_verified` / `org_required`);
  3. **org-membership check** on `start`/`complete` — only the *assigned* provider may progress
     (else 403 `not_assigned`);
  4. **`GET /incidents/assigned`** — the provider's work queue (their org's incidents);
  5. **stricter guest rate-limit** on incident create (5/min for unauthenticated, vs 20/min signed-in).
  `assign` (coordinator) still takes an org id in the body and now validates it is verified.
- **Tests** — unit (`resources` enums/schema defaults); API (`resources/test_organizations.py`,
  `resources/test_resources.py` — registration, one-org rule, verify, capacity/availability, RBAC,
  role-scoped listing); integration (`resources/test_incident_org_wiring.py` — unverified/no-org cannot
  accept, non-assigned provider cannot start, assigned queue). Updated `tests/factories.py`
  (`make_org` / `auth_provider_with_org`) and the incident walk tests to the server-side-org flow.
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`. Task K (docstrings) *in progress*
  and Task N (per-module `tests/{unit,api,integration}/resources/`) honored. *(2026-08-22 note: the Task-K
  claim was optimistic — a public-surface docstring pass completed that date; see the entry above.)*
- **Honest status:** written + lint/syntax-verified, **not executed here** (no `asyncpg`/`geoalchemy2`, no
  PostgreSQL+PostGIS on this Windows box). **`PICS-ORG-*`/`PICS-RES-*` stay `Planned`** until a green
  `make qa` on CI / the Ubuntu box (roadmap §14).

### Added — 2026-08-17 (Increment 5 — Locations/geo (LOC) module)
- **No table of its own** — LOC reads the geometry already on `incidents` and `organizations`
  (doc 50), so there is **no migration**. It enriches INC + ORG (roadmap §13.5).
- **Pure DB-free core** (`locations/geo.py`, mirroring the incidents `lifecycle` pattern):
  `haversine_km` (great-circle distance), an **offline reverse-geocode** (a tiny built-in
  bounding-box gazetteer — Telangana / Andhra Pradesh / India — **no third-party call**, honouring
  DPDP and MVP simplicity; the seam where a real geocoder plugs in), and GeoJSON `point_feature` /
  `feature_collection` builders ([lng, lat] order).
- **Repository** — PostGIS `ST_DWithin` proximity (geography cast → true metres) over open incidents
  and verified providers; plus full-layer reads for the map.
- **Service / router** — the four endpoints (doc 40 §5.4): `GET /locations/nearby` (provider/
  coordinator; GeoJSON of incidents and/or providers), `POST /locations/distance` (any role; km),
  `GET /locations/reverse-geocode` (any role; offline label), `GET /locations/map/{layer}` (GeoJSON
  `incidents`|`providers`, **role-scoped** — citizens see only their own incidents; unknown layer →
  404). All outputs are GeoJSON FeatureCollections for Leaflet.
- **Tests** — unit (`locations/test_geo.py` — distance, gazetteer, GeoJSON shape; **executed here**,
  since the core is dependency-free — all pass); API (distance/reverse-geocode/RBAC/404); integration
  (`ST_DWithin` proximity + role-scoped map layers over real data).
- **Design note (flagged for the user):** reverse-geocode is an **offline stub** by deliberate MVP
  choice; a real geocoder is a later enhancement.
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`; the geo unit assertions were
  **actually run and pass** on this box (the rest need PostgreSQL/PostGIS).
- **Honest status:** **`PICS-LOC-*` stay `Planned`** until a green `make qa` on CI / the Ubuntu box.

### Added — 2026-08-17 (Increment 6 — Alerts + Notifications (ALR/NTF) modules)
- **Alerts** (`app/modules/alerts/`) — `Alert` model + `alert_severity` enum; area is a PostGIS
  **MultiPolygon** (NULL = platform-wide). `POST /alerts` (coordinator/admin) accepts a polygon ring
  (3+ points) or none; `GET /alerts` returns active, non-expired alerts, **area-filtered by an
  optional lat/lng** via `ST_Contains` + platform-wide (PICS-ALR-001/002). Pull-model delivery — no
  broker in the MVP (ADR-012).
- **Notifications** (`app/modules/notifications/`) — `Notification` + `NotificationPreference` models
  + `notification_type` enum. Endpoints (doc 40 §5.4): list (paginated, `unread_only`),
  `unread-count`, `{id}/read`, `read-all`, `GET/PATCH preferences` (defaults created on first read),
  `DELETE {id}` (soft-delete). All strictly scoped to the calling user.
- **PICS-NTF-001 wired** — the incidents router now raises an `incident_update` notification to the
  requester on **every** lifecycle transition (skipped for guests and for self-actions), with a
  `link` back to `/incidents/{id}` (PICS-NTF-003). Composition happens at the router edge, keeping the
  incident service pure.
- **Migration** `0004_alerts_notifications.py` — the two enums, `alerts` (GiST on area), `notifications`
  (user/is_read indexes), `notification_preferences` (unique per user).
- **Tests** (Task N) — alerts API (RBAC, platform-wide vs area, **point-in-polygon filtering** —
  inside Hyderabad sees both, Delhi sees only platform-wide); notifications API (empty state,
  preference defaults + update, ownership 404s); integration (`NTF-001` requester-notified on accept,
  no self-notify on own cancel, read/read-all/soft-delete end-to-end).
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`.
- **Honest status:** written + lint/syntax-verified, **not executed here** (no PostgreSQL+PostGIS).
  **`PICS-ALR-*`/`PICS-NTF-*` stay `Planned`** until a green `make qa` on CI / the Ubuntu box.

### Added — 2026-08-17 (Increment 7 — Audit (AUD) module, cross-cutting)
- **Append-only audit trail** (`app/modules/audit/`) — `AuditLog` model (actor, `action`,
  resource_type/id, ip_address, old/new JSONB snapshots, created_at; **no** updated_at/deleted_at,
  PICS-AUD-002) + migration `0005_audit_logs.py` (actor / action / resource / created_at-desc
  indexes).
- **`AuditService.record`** — the cross-cutting write other modules call; the router exposes only a
  **read** (`GET /audit-logs`, coordinator/admin, filterable by actor/resource_type/resource_id/
  action, PICS-AUD-003). No write endpoint exists → the trail cannot be mutated over the API.
- **Wired PICS-AUD-001 into three modules** (composition at the router edge, one-directional coupling
  feature→audit): every **incident transition** (`incident.<action>`), **organization verification**
  (`organization.verified`), and **alert broadcast** (`alert.created`).
- **Client-IP capture** — added a `client_ip_ctx` contextvar (alongside the existing `request_id_ctx`)
  set in the request middleware, so audit entries carry the caller's IP without threading `Request`
  through every endpoint.
- **Tests** (Task N) — API (read RBAC: coordinator/admin 200, citizen/provider 403, anon 401; empty
  state); integration (incident transition audited with `new_values`; filter by resource; org-verify
  and alert-create audited).
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`.
- **Honest status:** written + lint/syntax-verified, **not executed here** (no PostgreSQL+PostGIS).
  **`PICS-AUD-*` stay `Planned`** until a green `make qa` on CI / the Ubuntu box.

### Added — 2026-08-17 (Increment 8 — Files (FIL) module, cross-cutting: MinIO uploads)
- **Metadata-only `files` table** (`app/modules/files/models.py` + migration `0006_files.py`) with the
  `file_purpose` enum and a `size_bytes ≤ 10 MB` CHECK — the DB stores the object **key/URL, never the
  blob** (ADR-007, PICS-FIL-001).
- **Storage abstraction** (`storage.py`) — the service depends on an `ObjectStorage` **protocol**;
  `S3Storage` (boto3, lazy import) talks to MinIO/S3 in production, and tests inject an in-memory fake.
  Synchronous `put` is run in a threadpool from the async service.
- **Server-side media pipeline** (`imaging.py`, **Pillow**) — never trust the client: apply EXIF
  orientation, **strip all metadata incl. GPS** (rebuild from raw pixels, PICS-FIL-003), downscale to
  ≤ 1920 px, enforce ≥ 640×480 (`image_too_small`), and a **blur check** via edge-variance
  (`image_too_blurry`) — PICS-FIL-002.
- **Face-detection-only gate is a documented seam** (`passes_face_quality_gate`, user-approved scope):
  nothing biometric is computed or stored (ADR-011); a real detector is a follow-up, so **PICS-FIL-005
  stays `Planned`**.
- **Endpoints** (doc 40 §5.4) — `POST /files` (multipart; any authenticated user; content-type
  allow-list → `400 invalid_file_type`, 10 MB / ~500 KB "lite" limit → `413 file_too_large`,
  PICS-FIL-004) and `GET /files/{id}` (role-scoped metadata: uploader or coordinator/admin).
- **Deps/config** — added `pillow>=10.3` to `pyproject.toml`; added media-limit settings to
  `core/config.py` (`file_max_bytes`, `lite_photo_max_bytes`, `image_*` dimension/blur knobs). `boto3`
  and `python-multipart` were already declared.
- **Tests** (Task N) — unit (`imaging`: downscale + metadata strip, too-small reject, corrupt reject,
  face-gate seam — **Pillow-based, runnable on CI**); API (upload stores to the fake bucket + returns
  metadata, invalid type 400, lite 413, role-scoped read) via a `FakeStorage` dependency override.
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`.
- **Honest status:** written + lint/syntax-verified, **not executed here** (no Pillow/boto3/MinIO/
  PostgreSQL on this box). **`PICS-FIL-*` stay `Planned`** until a green `make qa` on CI / the Ubuntu box.

### Added — 2026-08-17 (Increment 9 — Reports (RPT) module)
- **No table of its own** — RPT aggregates live data (`incidents` + timeline, `organizations`,
  `audit_logs`); no migration. Read-only, coordinator/admin (F8/F10).
- **Repository** (`reports/repository.py`) — SQL group-by counts (status / service_type / priority),
  totals + open count, org counts, response-time samples (created → first-reach of a status via the
  `incident_updates` timeline), incident points (for coarse area grouping), and audit-action counts.
- **Service** (`reports/service.py`) — three reports: **dashboard** (incidents by status/type/priority
  + **by region** via the LOC gazetteer + org counts, PICS-RPT-001); **response-times** (time-to-accept
  and time-to-resolve, avg + median computed in Python); **fulfillment** (resolution + verification
  rates, **cross-checked against the audit trail** `incident.verify` count, PICS-RPT-002). Any report
  exports to **CSV** (flattened `metric,value`, PICS-RPT-003).
- **Endpoints** (doc 40 §5.4) — `GET /reports/{dashboard,response-times,fulfillment}` and
  `GET /reports/{name}/export?format=csv` (non-csv → `422 unsupported_format`; unknown name → `404`).
- **Tests** (Task N) — unit (`_summary`/`_flatten` pure helpers); API (staff-only RBAC, empty shape,
  export format + unknown-report errors, CSV content-type); integration (dashboard counts + by-region
  over a walked incident, response-times/fulfillment rates, audit cross-check, flattened CSV export).
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`.
- **Honest status:** written + lint/syntax-verified, **not executed here** (no PostgreSQL+PostGIS).
  **`PICS-RPT-*` stay `Planned`** until a green `make qa` on CI / the Ubuntu box.

### Added — 2026-08-17 (Increment 10 — Administration (ADM) module + Task-L chatbot stub)
- **The 10th and final module** (`app/modules/administration/`). No table of its own — user/role
  administration already lives in USR (`PATCH /users/{id}` etc., PICS-ADM-002), so ADM does **not**
  duplicate it (DRY); it adds the two missing pieces:
  - `GET /administration/reference-data` (staff) — the platform's controlled vocabularies (roles,
    statuses, service types, priorities, org/alert/notification/file enums) **+ the incident state
    machine** (transitions with allowed from-states and roles), assembled purely from code
    (PICS-ADM-001). Mutable disaster-type configuration is → FFP.
  - `GET /administration/overview` (admin) — users by role/status + organizations awaiting verification.
- **Admin user-change is now audited** — `PATCH /users/{id}` records a `user.admin_update` audit entry
  (actor, target, new role/status, IP), satisfying doc 40's "(audited)" note and PICS-ADM-002/AUD-001.
- **Task L — FAQ chatbot stub** — `POST /notifications/chat` (authenticated) always returns the fixed
  acknowledgement *"Your input is noted, we'll try to get back to you shortly, if possible."* No ML in
  the MVP (real NLP is a Task-M white-paper item → FFP). Added `PICS-NTF-004` to `docs/mvp/26`
  (+ archive copy, C3 parity), status Planned.
- **Tests** (Task N) — API (reference-data staff-gated + contents incl. lifecycle; overview admin-only
  + counts; chatbot fixed reply, auth-required, empty-message 422); integration (admin role change
  writes the audit entry; non-admin 403).
- **Quality:** **`ruff check app tests` clean**; all files `py_compile`.
- **Honest status:** written + lint/syntax-verified, **not executed here** (no PostgreSQL+PostGIS).
  **`PICS-ADM-*` / `PICS-NTF-004` stay `Planned`** until a green `make qa` on CI / the Ubuntu box.

### Milestone — all 10 modules built
USR · INC · ORG/RES · LOC · ALR · NTF · AUD · FIL · RPT · ADM are all written, `ruff`-clean, and
`py_compile`-clean. Nothing has been executed on this Windows box (no deps / no PostgreSQL+PostGIS);
every `PICS-*` row stays `Planned` until a green `make qa` on CI / the Ubuntu box flips it (roadmap §14).

### Changed — 2026-08-17 (`.gitignore` hardened)
- Expanded `code/.gitignore`: added `.env.*` (with a `!.env.example` negation so the template stays tracked),
  `*.key`, build/dist (`build/ dist/ .eggs/ *.egg`), coverage variants (`.coverage.* coverage.xml`), mypy daemon
  (`.dmypy.json`/`dmypy.json`), Windows OS files (`Thumbs.db`, `Desktop.ini`), more editors (`.idea/ *.swp *~`),
  `*.log`, and `/minio-data/`. **Fixed a latent bug** — removed inline `# comments` from pattern lines (git treats
  them as literal text, which had silently broken `*.pem` key-ignoring and the `.env.example` negation). Verified
  every rule with `git check-ignore` in a throwaway repo (secrets ignored; `.env.example`/sources tracked).

### Added — 2026-08-17 (FIL face-detection quality gate — client-side, ADR-011)
- **`frontend/static/js/face-quality.js`** — a dependency-free, on-device photo-quality gate: checks size,
  dimensions, brightness, and a sharpness/blur proxy, plus a best-effort **face *count*** via the browser's
  `FaceDetector` API. **Advisory** (never blocks the upload) and **graceful** (skips the face check if the API is
  absent). **Nothing biometric leaves the device or is stored** — the count is used then discarded (ADR-011,
  detection-only, not recognition). `node --check` clean.
- **`app/modules/files/imaging.py`** — `passes_face_quality_gate` docstring updated: it is an intentional
  server-side **no-op** (the server computes no face data by design); the authoritative quality re-checks
  (size/dims/EXIF-strip/blur) stay in `process_image`.
- **Design note:** `docs/whitepapers/face-quality-gate.md` (companion to the six Task-M papers) — options, DPDP,
  MVP-detection vs FFP-recognition, metrics.
- **Status:** browser code, so **not** exercised by `make qa`; `PICS-FIL-005` stays `Planned` pending a manual
  browser check (roadmap §14).

### Added — 2026-08-17 (Seed data — `scripts/seed.py` filled in + doc 34)
- **`scripts/seed.py`** implemented (was a stub) — the rich, **idempotent** starter dataset from roadmap §3.4:
  8 users (the 4 PRD personas + extras) + a guest incident, 3 provider organizations + 4 resources, **incidents
  in all 8 lifecycle states** (incl. a guest submission) with generated, time-staggered `incident_updates`
  timelines, plus 2 alerts (one platform-wide, one Hyderabad MultiPolygon), 2 notifications, 2 files, and 2 audit
  entries. Every row uses a deterministic `uuid5` id guarded by a PK lookup → `make seed` never duplicates.
  Passwords hashed once (dev-only `IDRMseed#2026`). Loaded by `make seed` after `make migrate`.
- **Doc:** the row-by-row companion `docs/mvp/34-seed-data-and-fixtures.md` (+ archive copy) documents the exact
  dataset and the fixtures-vs-seed split.
- **Quality:** `ruff check` clean (incl. `scripts/`); `py_compile` clean. Not executed here (no deps / DB).

### Next
- **Run the full suite green** on CI / the Ubuntu box (`make install && make migrate && make seed && make qa`),
  then flip the passing `PICS-*` rows to ✅ in `docs/mvp/26` (+ archive copy; keep parity). See
  `PENDING.md` §1 for the Ubuntu bring-up checklist.
- **Optional follow-ups:** the FIL face-detection detector (PICS-FIL-005 seam), and the Task-M white papers.
