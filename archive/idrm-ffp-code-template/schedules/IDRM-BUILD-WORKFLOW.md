# IDRM Build Workflow — One Module at a Time

## A rookie-friendly playbook for building the backend, gateway, and frontends

**Version**: 1.0 · **Created**: 2026-05-30
**Audience**: Anyone building IDRM — assumes you can read code, but **not** that you know this codebase.
**Companion docs**: `IDRM-PROJECT-STATUS.md` (current status + the locked decisions log) · `IDRM-IMPLEMENTATION-GUIDE.md` (the *when* — 16-week timeline). **This file is the *how*** — the concrete files and steps for each module, in the order that lets you test as you go.

> **How to use this guide**: Build **top to bottom**. Each module is self-contained: do its steps, run its "Verify" check, tick its "Done when" box, then move to the next. Don't skip ahead — later modules assume earlier ones work.

---

## 0. Golden rules (read once, then keep handy)

**Single sources of truth** — when in doubt, these win (never invent values):

| For… | Look here |
|------|-----------|
| Who can do what (roles & permissions) | `docs/development/IDRM-FS.md` §3.3 (Permission Matrix) |
| Exact enums (roles, statuses, service types, privacy, priority) | `database/init/02-schema.sql` (the `CHECK` constraints) + `CLAUDE.md` |
| API endpoints, request/response shapes, security | `start-here/COMPLETE-API-SPECS-GUIDE.md` + `CLAUDE.md` API reference |
| SQL & PostGIS query patterns | `docs/IDRM-Database-Query-Reference.md` |
| JSON request/response examples | `instructions/instructions_json_formats_v3.md` |
| What each page shows/does | `instructions/instructions_pages_v3.md` |
| UI styling (Tailwind recipes, colors) | `instructions/instructions_ui_v3.md` (Slate + Emerald) |
| Gateway internals | `docs/IDRM-Bun-Gateway-Guide.md` |

**Decisions already made (build to these — don't re-litigate):**
- **Backend data layer**: SQLAlchemy 2.0 **async** ORM + **GeoAlchemy2** (PostGIS geometry). Alembic for migrations.
- **API style**: only **GET** and **POST**, all under **`/api/v1/...`**. Status changes use **action sub-endpoints** (`POST /services/{id}/approve|accept|complete|verify|cancel|reject`) — **never** `PUT`/`DELETE`, and **not** a `/services/requests` path (it's just `/services`).
- **Enums** (UPPERCASE, exact): roles `CITIZEN, VOLUNTEER, ORGANIZER, PROVIDER, MANAGER, EVENT_MANAGER, EXECUTIVE, DM_AUTHORITY, AUDITOR, ADMIN` (+ "Public" = not logged in); statuses `SUBMITTED→APPROVED→ACCEPTED→IN_PROGRESS→COMPLETED→VERIFIED` (+ `REJECTED, CANCELLED, EXPIRED, DISPUTED`); service types `RESCUE, MEDICAL, FOOD, SHELTER, WATER, OTHER`; privacy `PUBLIC, PROTECTED, PRIVATE` (default `PROTECTED`); priority `CRITICAL, HIGH, MEDIUM, LOW`.
- **Auth**: JWT **15-min access + 7-day refresh**, sent as `Authorization: Bearer`. Emergency citizens use **phone + OTP quick-start** (creates a lightweight `CITIZEN`). Emergencies (`CRITICAL`/`HIGH`) are **auto-approved** by the system.
- **Frontend**: build the **documented IDRM page inventory** (see Part C). The pre-existing e‑commerce stubs (`cart`, `checkout`, `payment`, `product-*`) are **wrong template leftovers — delete/ignore them**. Style everything with `instructions_ui_v3.md`.

**Each module section uses the same shape:**
> **🎯 Goal** · **🔗 Depends on** · **📁 Files** · **🪜 Steps** · **✅ Verify** · **🏁 Done when**

---

## 1. Build order (the dependency map)

Build in this order. Arrows mean "needs the thing before it."

```
BACKEND                         GATEWAY                 FRONTEND (web-html)
M0 Boot ──► M1 Models/Schemas    (after M2 works)        (after the API is reachable)
        │                        G1 Proxy ──► G2 Rate    F0 Build setup ──► F1 Public
        ├─► M2 Auth ─────────────┤            limit       ├─► F2 Auth (login/register)
        ├─► M3 Services          ├─► G3 JWT auth          ├─► F3 Citizen core
        ├─► M4 Geo               └─► G4 WebSocket         ├─► F4 Map
        ├─► M5 Notifications                              ├─► F5 Notifications/Profile
        └─► M6 Analytics                                  └─► F6 Provider pages

LATER:  React SPA (Part D)  ·  React Native (Post-MVP)
```

**Recommended first milestone (vertical slice):** M0 → M1 → M2 → M3 → M4 → G1 → G3 → F0 → F2 → F3 → F4. That gives a citizen who can register, log in, create a request, and see it on a live map — proving the whole stack end-to-end.

---

## 2. Verifying your work (confirm a module actually works)

Every module below ends with a **✅ Verify** block giving the exact commands + expected output. Here are the tools per layer (run from the repo root unless noted):

> **🐧 Where to verify**: the **dev/target platform is an Ubuntu laptop** — run all `✅ Verify` steps there (Python/conda, Postgres + PostGIS, Redis and Bun are all present). The Windows box used to author the code has none of those (and Bun-on-Windows showed sandbox quirks: stray processes, localhost-connect hangs), so for backend/gateway modules "verify" means **run it on Ubuntu**. 🚩 **Ports + running dev/staging/production on one Ubuntu host** (open/check/free ports, `ufw`, switching environments): see `docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`.

**Backend (Python / FastAPI)**

```bash
# Syntax only — no server, no DB needed:
conda run -n idrm-mvp python -m py_compile src/backend/app-python/main.py
# Run the API:
cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000
# Check an endpoint (each module lists the expected JSON):
curl -s http://localhost:8000/api/v1/health | python -m json.tool
# Try any endpoint by hand:  http://localhost:8000/docs   (Swagger UI)
# Tests (as they're added):
conda run -n idrm-mvp pytest -q          # or:  make test
```

**API Gateway (Bun / TypeScript)**

```bash
cd src/backend/api-gateway && bun run dev      # :3000 HTTP · :3001 WebSocket
curl -s http://localhost:3000/api/v1/health    # should mirror the backend health
bun test
```

**Frontend (web-html)**

```bash
cd src/frontend/web-html && bun run dev         # http://localhost:5173
# Manual: open the page; check the browser console for errors; confirm API calls hit :3000.
```

**Scripts & Makefile**

```bash
for f in scripts/*.sh; do bash -n "$f" && echo "OK $f"; done   # shell syntax check
make help                                                      # list all make targets
```

> **Rule**: a module is "done" only when its **✅ Verify** passes **and** it didn't break an earlier module's verify. All setup/DB steps are idempotent, so re-running to verify is always safe.

---

# PART A — Backend (`src/backend/app-python/`)

FastAPI modular monolith. Final shape:
```
src/backend/app-python/
├── main.py                 # FastAPI app, wires routers + middleware
├── core/
│   ├── config.py           # Settings from .env (pydantic-settings)
│   ├── database.py         # async SQLAlchemy engine + session
│   └── security.py         # JWT create/verify, bcrypt hashing
├── dbmodels/               # SQLAlchemy ORM models (mirror 02-schema.sql)
│   ├── base.py  user.py  service_request.py  organization.py  notification.py  audit_log.py
├── schemas/                # Pydantic request/response models
│   └── auth.py  user.py  service.py  geo.py  notification.py  analytics.py
├── services/               # Business logic (no HTTP here)
│   └── auth_service.py  service_service.py  geo_service.py  notification_service.py  analytics_service.py
└── api/v1/                 # Route handlers (thin — call services/)
    └── auth.py  services.py  geo.py  analytics.py  notifications.py  users.py
```

### Module M0 — Backend boots & says hello
> **🎯 Goal**: `uvicorn main:app` starts, `GET /api/v1/health` returns `{"status":"ok"}`, Swagger UI loads at `/docs`.
> **🔗 Depends on**: prerequisites + conda env (`./scripts/setup-development-monolith.sh`).
> **📁 Files**: `main.py`, `core/config.py`, `core/database.py`.
> **🪜 Steps**:
> 1. `core/config.py` — a `Settings(BaseSettings)` class that reads `.env` (DATABASE_URL, REDIS_URL, JWT_* , CORS_ORIGINS). Use `pydantic-settings`.
> 2. `core/database.py` — `create_async_engine(settings.DATABASE_URL)`, an `async_sessionmaker`, and a `get_db()` dependency that yields a session.
> 3. `main.py` — create `FastAPI(title="IDRM API")`, add CORS middleware from `CORS_ORIGINS`, include a `/api/v1/health` route, mount routers (empty for now).
> **✅ Verify** (M0 is **built** — run these to confirm on your machine):
> - Syntax check (no server/DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/main.py src/backend/app-python/core/config.py src/backend/app-python/core/database.py` → silent output = OK.
> - Start it: `cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000`
> - Health: `curl -s http://localhost:8000/api/v1/health` → `{"status":"ok","service":"IDRM API","environment":"development"}`
> - Readiness: `curl -s http://localhost:8000/api/v1/health/ready` → `{"status":"ok","database":"up"}` (needs Postgres running)
> - Docs: open `http://localhost:8000/docs` → Swagger lists both health routes.
> **🏁 Done when**: `uvicorn` starts with no import/syntax errors, `/api/v1/health` returns `{"status":"ok"}`, and `/docs` loads. (`database:"up"` appears only once Postgres is running — expected.)
> **🧪 Status**: code written & reviewed; **not yet executed in the authoring environment** (no Python/conda there) — run the steps above to confirm. Comments/docstrings polished & verified — see **"Docs pass (M0 + M1)"** below.

### Module M1 — Data models & schemas
> **🎯 Goal**: Python objects that mirror the database exactly, plus request/response shapes.
> **🔗 Depends on**: M0. **Read first**: `database/init/02-schema.sql` and `docs/development/IDRM-HLD.md` (it shows the ORM models).
> **📁 Files**: `dbmodels/*.py`, `schemas/*.py`.
> **🪜 Steps**:
> 1. `dbmodels/base.py` — `DeclarativeBase`. Define `Enum`s with the EXACT values from §0 (so Python and the DB agree).
> 2. One model per table (`users`, `service_requests`, `organizations`, `notifications`, `audit_logs`). Use **GeoAlchemy2** `Geometry('POINT', srid=4326)` for `service_requests.location`.
> 3. `schemas/` — Pydantic models for each request body and response (mirror `instructions_json_formats_v3.md`). Keep `ServiceCreate`, `ServiceOut`, `UserOut`, `Token`, etc.
> **✅ Verify** (M1 is **built** — run these to confirm on your machine):
> - Import models: `cd src/backend/app-python && conda run -n idrm-mvp python -c "from dbmodels import *; print('models OK')"` → no error.
> - Import schemas: `conda run -n idrm-mvp python -c "import schemas; print('schemas OK')"` → no error.
> - Syntax (no DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/dbmodels/*.py src/backend/app-python/schemas/*.py` → silent = OK.
> - Field/enum cross-check: every column & enum value matches `database/init/02-schema.sql` (the DB `CHECK` constraints are the source of truth).
> **🏁 Done when**: models + schemas import cleanly and every enum/column matches the schema.
> **🧪 Status**: code written & reviewed; enum/column values cross-checked against `02-schema.sql` by eye; the `audit_logs.user_id` foreign-key bug caught in review was fixed. **Not yet executed** here (no Python/conda) — run the imports above to confirm.

### Docs pass (M0 + M1) — comments & docstrings
> **🎯 Goal**: every module, class, and function in the M0 + M1 code carries an apt, rookie-readable docstring/comment. (Pydantic class docstrings also surface as model descriptions in Swagger `/docs`.)
> **🪜 What was added**: class-level docstrings on all 5 ORM models and all 11 `enums.py` enums; docstrings on every `schemas/*` request/response class; an accuracy fix in `core/__init__.py` (`core.security` arrives in M2, not today). M0's `main.py`/`config.py`/`database.py` were already fully documented.
> **✅ Verify** (done 2026-05-31):
> - Coverage: `grep -rn -A1 '^class ' src/backend/app-python/dbmodels src/backend/app-python/schemas` → every `class` line is followed by a `"""…"""` docstring.
> - Re-read `schemas/geo.py` + `schemas/auth.py` to confirm the URLs in docstrings are intact (`/geo/nearby`, `/auth/refresh`); the backslashes seen in grep output were a Windows display artifact, not file content.
> - Docstrings/comments **only** — no code behaviour, enum, or column changed.
> - Full `py_compile` still pending (no Python/conda in the authoring box) — covered by the M1 syntax check above.
> **🏁 Done when**: every class/function has an apt docstring and comments are accurate. ✅

### Module M2 — Auth (`api/v1/auth.py`, `services/auth_service.py`, `core/security.py`)
> **🎯 Goal**: register, login, refresh, logout, `GET /users/me`.
> **🔗 Depends on**: M1. **Read first**: API guide §Auth + `CLAUDE.md` auth endpoints.
> **📁 Files**: `core/security.py`, `services/auth_service.py`, `api/v1/auth.py`, `api/v1/users.py`.
> **🪜 Steps**:
> 1. `core/security.py` — bcrypt (cost 12) hash/verify; `create_access_token` (15 min) / `create_refresh_token` (7 days); `decode_token`; a `get_current_user` dependency that reads the `Authorization: Bearer` header **or** the gateway's `X-User-ID`.
> 2. `services/auth_service.py` — register (email unique, allowed self-roles = CITIZEN/PROVIDER/VOLUNTEER only), login, refresh, update-profile. _(phone+OTP quick-start is **deferred** — needs an SMS provider + a documented endpoint.)_
> 3. `api/v1/auth.py` — `POST /register`, `POST /login`, `POST /refresh`, `POST /logout`. `api/v1/users.py` — `GET /users/me`, `POST /users/me`.
> **✅ Verify** (M2 is **built** — run these once Postgres + the conda env are up):
> - Syntax (no server/DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/core/security.py src/backend/app-python/services/auth_service.py src/backend/app-python/api/v1/auth.py src/backend/app-python/api/v1/users.py src/backend/app-python/main.py` → silent = OK.
> - Boot: `cd src/backend/app-python && uvicorn main:app --reload --port 8000` → `/docs` now lists the **auth** + **users** routes.
> - Register: `curl -s -X POST :8000/api/v1/auth/register -H 'Content-Type: application/json' -d '{"email":"a@b.com","password":"SecurePass123!","full_name":"Test User"}'` → `201` with `{"id","email","full_name","role":"CITIZEN", …}`.
> - Login: POST the same email/password to `/api/v1/auth/login` → `200` with `access_token` + `refresh_token` (`expires_in: 900`).
> - Me: `curl :8000/api/v1/users/me -H "Authorization: Bearer <access_token>"` → `200` with the profile.
> - Refresh: `POST /api/v1/auth/refresh` with `{"refresh_token":"…"}` → `200` and a new access token.
> - Guards: register with `"role":"ADMIN"` → `403`; a second register with the same email → `409`; `/users/me` with no token → `401`.
> **🏁 Done when**: the register→login→me round-trip works, refresh issues a new token, and elevated roles can't self-register.
> **🧪 Status**: code written, reviewed & docstring-checked; routes wired into `main.py`. **Not yet executed** here (no Python/conda) — run the steps above to confirm. Notes: bcrypt cost 12 (passlib); JWT via python-jose, 15-min access (+`role` claim) / 7-day refresh, with a `type` claim so the two can't be swapped; `UserOut` exposes the PK as `id` (aliased from ORM `user_id`); `POST /users/me` merges the `preferences` JSON.

### Module M3 — Service requests (`api/v1/services.py`, `services/service_service.py`)
> **🎯 Goal**: the core lifecycle — create, list, get, and the action endpoints.
> **🔗 Depends on**: M1, M2. **Read first**: API guide §Services, FS §3.3 (who can do each action), FS §6.1 (state machine), `IDRM-Database-Query-Reference.md` (the race-safe `accept` query).
> **📁 Files**: `services/service_service.py`, `api/v1/services.py`.
> **🪜 Steps**:
> 1. `POST /services` (create; default status `SUBMITTED`; auto-approve if `CRITICAL`/`HIGH`), `GET /services` (filters + pagination), `GET /services/{id}`.
> 2. Action endpoints (each enforces the right role + current status per FS §3.3 & §6.1): `/approve` (DM_AUTHORITY), `/reject` (DM_AUTHORITY, also resolves DISPUTED), `/accept` (PROVIDER — `FOR UPDATE` race-safe, takes `org_id`), `/start` (PROVIDER, ACCEPTED→IN_PROGRESS), `/complete` (PROVIDER), `/verify` (requestor + rating), `/cancel` (requestor, only SUBMITTED/APPROVED), `/dispute` (requestor, from IN_PROGRESS/COMPLETED).
> 3. Enforce privacy levels on reads (PUBLIC/PROTECTED/PRIVATE) — `get_current_user_optional` lets the public see redacted requests.
> **✅ Verify** (M3 is **built** — run once Postgres has the schema + a few seed rows):
> - Syntax (no server/DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/services/service_service.py src/backend/app-python/api/v1/services.py src/backend/app-python/main.py` → silent = OK.
> - Boot: `uvicorn main:app --reload --port 8000` → `/docs` lists the **services** routes (create/list/get + approve/reject/accept/start/complete/verify/cancel/dispute).
> - Seed actors (no role-grant endpoint yet): in `psql`, set one user's role to `DM_AUTHORITY` and one to `PROVIDER`, and insert a **verified** `organizations` row. Citizens register via M2.
> - Create: `POST /api/v1/services` (Bearer = citizen) with a `MEDIUM` request → `201`, `status:"SUBMITTED"`; a `CRITICAL`/`HIGH` request → `status:"APPROVED"` (auto-approved, D5).
> - List/Get: `GET /api/v1/services?status=SUBMITTED` → `{status,data:{items,…}}`; `GET /api/v1/services/{id}` → full object (requestor redacted unless you're the requestor/privileged).
> - Happy path: approve (DM) → accept (provider, `{"org_id":"…"}`) → start (provider) → complete (provider) → verify (citizen, `{"rating":5}`) — each returns the updated object at the next status.
> - Guards: citizen calling `/approve` → `403`; `/accept` a non-APPROVED request → `409`; two providers `/accept` the same one → a `409`; `/cancel` after IN_PROGRESS → `409`.
> - Reject/dispute path: `/reject` a SUBMITTED (DM) → `REJECTED`; or `/dispute` (citizen) → `DISPUTED`, then `/reject` → `REJECTED`.
> **🏁 Done when**: the full happy path + a reject/dispute path work with correct role + status checks.
> **🧪 Status**: code written, reviewed & docstring-checked; routes wired into `main.py`. **Not yet executed** here (no Python/conda). Notes: a **`/start`** action (ACCEPTED→IN_PROGRESS) was added to honour the FS §6.1 machine — **CLAUDE.md's action list should be updated to add it**. DB triggers handle `updated_at` + org stats + audit logging (we don't). Geometry via `ST_MakePoint`/`to_shape`; accept uses `SELECT … FOR UPDATE`. **Known gap**: no user↔org link, so `/accept` takes `org_id` in the body (validated verified). `estimated_arrival` / approve-notes / cancel & dispute reasons have no columns yet (audit-logged only).

### Module M4 — Geo (`api/v1/geo.py`, `services/geo_service.py`)
> **🎯 Goal**: `GET /geo/nearby` and `GET /geo/cluster` using PostGIS.
> **🔗 Depends on**: M1, M3. **Read first**: `IDRM-Database-Query-Reference.md` §Spatial.
> **🪜 Steps**: nearby = `ST_DWithin` on `::geography` (metres) ordered by `ST_Distance`; cluster = `ST_ClusterKMeans` by zoom. Both consider only live requests (APPROVED/ACCEPTED/IN_PROGRESS) and expose no identity → public (no auth).
> **✅ Verify** (M4 is **built** — run once Postgres has PostGIS + a few seeded requests):
> - Syntax (no server/DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/services/geo_service.py src/backend/app-python/api/v1/geo.py src/backend/app-python/main.py` → silent = OK.
> - Boot: `uvicorn main:app --reload --port 8000` → `/docs` lists **geo** (`/geo/nearby`, `/geo/cluster`).
> - Nearby: `curl ":8000/api/v1/geo/nearby?latitude=13.0827&longitude=80.2707&radius=10"` → `{center, radius_km, total, results:[…]}` sorted by `distance_km` ascending; add `&service_type=MEDICAL` to filter.
> - Cluster: `curl ":8000/api/v1/geo/cluster?zoom=10"` → `{clusters:[{latitude, longitude, count, priority_breakdown}]}`; optional `&bounds=south,west,north,east`.
> - Edge cases: no live requests → `results: []` / `clusters: []`; `radius` > 50 is clamped; bad `bounds` → `400`; out-of-range/missing `latitude`/`longitude` → `422` (FastAPI Query validation).
> **🏁 Done when**: nearby returns distance-sorted live requests and cluster returns centroid + count + priority_breakdown.
> **🧪 Status**: code written, reviewed & docstring-checked; geo router wired into `main.py`. **Not yet executed** here (no Python/conda — PostGIS also required). Notes: distance computed on `::geography` (metres → km); raw parameterised SQL via `text()` (mirrors the Query Reference §Spatial); optional filters built as clauses (not `:p IS NULL OR …`) to avoid asyncpg untyped-NULL params; the cluster count `k` is derived from zoom (capped at 50 and the point count) and inlined as a validated int.

### Module M5 — Notifications
> **🎯 Goal**: `GET /notifications`, `POST /notifications/{id}/read`; emit events to Redis pub/sub (the gateway fans them out over WebSocket). **Read**: API guide §Notifications.
> **📁 Files**: `core/redis.py`, `services/notification_service.py`, `api/v1/notifications.py` (+ `schemas/notification.py` reshaped; emissions wired into `services/service_service.py`).
> **✅ Verify** (M5 is **built** — run once Postgres + Redis are up):
> - Syntax (no server/DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/core/redis.py src/backend/app-python/services/notification_service.py src/backend/app-python/api/v1/notifications.py src/backend/app-python/services/service_service.py src/backend/app-python/main.py` → silent = OK.
> - Boot: `uvicorn main:app --reload --port 8000` → `/docs` lists **notifications**. The app boots even if Redis is down (client is lazy; publishes are best-effort).
> - Generate: run the M3 happy path — **accept** (provider) gives the requestor a `SERVICE_ACCEPTED` notification; **complete** gives a `VERIFICATION_REQUEST`.
> - List: `GET /api/v1/notifications` (Bearer = requestor) → `{status:"success", data:{items:[{id,type,title,message,read,created_at}], unread_count}}`.
> - Mark read: `POST /api/v1/notifications/{id}/read` → `200`, item now `read:true`, `unread_count` drops next list; another user's id → `404`.
> - Realtime (optional): `redis-cli SUBSCRIBE service_requests notifications` while doing the above → see `request_*` + notification events.
> **🏁 Done when**: list + mark-read work, and accept/complete create the right notification types.
> **🧪 Status**: code written, reviewed & docstring-checked; notifications router wired into `main.py`; emissions wired into the M3 lifecycle (14 hooks). **Not yet executed** here (no Python/conda; realtime also needs Redis). Notes: response reshaped to the documented `{id,type,title,message,read,created_at}` + `{status,data}` envelope (subject→title, body→message, status→read); in-app notifications are created `SENT` (with `sent_at`) to satisfy the `sent_before_read` CHECK; the notification row shares the action's transaction, and Redis publishing is **best-effort** (a Redis outage never breaks the API call).

### Module M6 — Analytics
> **🎯 Goal**: `GET /analytics/dashboard` — the aggregate counts shown in `CLAUDE.md`. Cache in Redis (5-min TTL). **Read**: API guide §Analytics.
> **📁 Files**: `services/analytics_service.py`, `api/v1/analytics.py` (+ `cache_get_json`/`cache_set_json` added to `core/redis.py`).
> **✅ Verify** (M6 is **built** — run once Postgres has a few requests):
> - Syntax (no server/DB): `conda run -n idrm-mvp python -m py_compile src/backend/app-python/services/analytics_service.py src/backend/app-python/api/v1/analytics.py src/backend/app-python/core/redis.py src/backend/app-python/main.py` → silent = OK.
> - Boot: `uvicorn main:app --reload --port 8000` → `/docs` lists **analytics** (`/analytics/dashboard`).
> - Fetch: `curl :8000/api/v1/analytics/dashboard -H "Authorization: Bearer <token>"` → `{status:"success", data:{total_requests, active_requests, avg_response_time_min, completion_rate, by_service_type{…6 types}, by_status{…10 statuses}}}`.
> - Cache: a second call within 5 min is served from Redis (identical numbers); works without Redis too (just recomputes each call).
> - Auth: no token → `401`.
> **🏁 Done when**: the dashboard returns the documented JSON shape (cached 5 min).
> **🧪 Status**: code written, reviewed & docstring-checked; analytics router wired into `main.py` (**all backend routers M2–M6 now mounted**). **Not yet executed** here (no Python/conda; cache needs Redis). Notes: `by_service_type`/`by_status` are seeded with every enum key (all 6 types / 10 statuses) so the shape is stable; `completion_rate` = (COMPLETED+VERIFIED)/total; `avg_response_time_min` = avg(accepted_at − created_at) over accepted requests; the Redis cache is best-effort (miss/outage → recompute).

---

# PART B — API Gateway (`src/backend/api-gateway/`)

Bun + TypeScript. Final shape per `docs/IDRM-Bun-Gateway-Guide.md`:
```
src/backend/api-gateway/
├── src/index.ts            # Bun.serve() entry
├── src/middleware/         # rateLimit.ts  auth.ts  cors.ts  security.ts
├── src/routes/             # api.ts (proxy → :8000)  static.ts  websocket.ts
└── src/utils/              # jwt.ts  redis.ts
package.json · tsconfig.json
```

### G1 — Proxy skeleton
> **🎯 Goal**: `Bun.serve` on :3000 forwards `/api/v1/*` to FastAPI (:8000); adds CORS + security headers.
> **📁 Files**: `package.json`, `tsconfig.json`, `.env.example`, `src/config.ts`, `src/middleware/{cors,security}.ts`, `src/routes/api.ts`, `src/index.ts`. (Structured so G2 rate-limit / G3 JWT / G4 WebSocket slot into the chain.)
> **🪜 Steps**: `Bun.serve({port})` → answer OPTIONS preflight → proxy `/api/*` to `FASTAPI_URL` (buffer the body, strip `host`, 502 if upstream is down) → add CORS + security headers to every response. Env has in-code defaults, so it runs with no `.env`.
> **✅ Verify** (G1 — **runtime-verified here**; Bun 1.3.9 is installed):
> - Run it: `cd src/backend/api-gateway && bun run dev` (or `bun src/index.ts`) → logs `IDRM API Gateway → http://localhost:3000`.
> - Proxy: with FastAPI (or any stub) on :8000, `curl -i localhost:3000/api/v1/health` → **200** with the upstream's JSON plus the gateway's headers.
> - Upstream down → `curl -i localhost:3000/api/v1/health` → **502** `{"detail":"Upstream service unavailable","code":"BAD_GATEWAY"}` (clean, not a crash).
> - Preflight: `curl -i -X OPTIONS localhost:3000/api/v1/services -H 'Origin: http://localhost:5173'` → **204** + `Access-Control-Allow-*` (echoed origin; `GET, POST, OPTIONS`).
> - Non-API: `curl -i localhost:3000/nope` → **404** `{"detail":"Not found","code":"NOT_FOUND"}`.
> - Every response carries the security headers (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, CSP, HSTS, …).
> **🏁 Done when**: `curl localhost:3000/api/v1/health` returns the backend's health response.
> **🧪 Status**: ✅ **Built & runtime-verified** (2026-05-31). Exercised against a Bun stub upstream on :8000 (FastAPI itself needs Python, absent here): proxy round-trip → 200; upstream-down → 502; OPTIONS → 204; non-API → 404; security + CORS headers present on all. No runtime deps yet (G2 adds Redis, G3 adds `jsonwebtoken`).

### G2 — Rate limiting (Redis)
> **🎯 Goal**: per-IP/endpoint limits (login 5/15min, API 60/min, static 1000/min). **Copy the pattern** from the Bun Gateway Guide §Rate Limiting.
> **📁 Files**: `src/middleware/rateLimit.ts` (+ `redisUrl` in `src/config.ts`; wired into `src/index.ts`).
> **🪜 Steps**: fixed-window counters keyed by `ratelimit:{path}:{ip}`; `getRateLimitConfig(path)` sets the limits; over-limit → 429 (+ a block cooldown on the auth endpoints). The store is pluggable — **InMemoryStore** (default; correct for the single-instance MVP) or **RedisStore** (when `REDIS_URL` is set; shared across replicas; fails open). `X-RateLimit-*` + `Retry-After` headers added to responses.
> **✅ Verify** (run on the **Ubuntu** dev laptop — `bun run dev`; the in-memory store needs no Redis):
> - 6× `curl -s -o /dev/null -w "%{http_code}\n" -X POST localhost:3000/api/v1/auth/login -d '{}'` → first 5 pass through (200 if FastAPI is up, else 502); the **6th returns 429** with `Retry-After`; the 7th stays 429 (IP now blocked).
> - An allowed response carries `X-RateLimit-Limit` / `X-RateLimit-Remaining` (e.g. `GET /api/v1/services` → 60 / 59…).
> - A different `X-Forwarded-For` IP gets its own bucket (not 429).
> - (Multi-replica) set `REDIS_URL` and confirm the count is shared — not needed for the single-instance MVP.
> **🏁 Done when**: the 6th login in 15 min returns `429`.
> **🧪 Status**: code written, reviewed & doc-commented; wired into `index.ts`. **Verify on Ubuntu** (per §2) — the Windows authoring box couldn't give a clean run (stray Bun processes from earlier turns + localhost-connect quirks made the counter look like it reset). The in-memory store is a single module-level instance, so on one Ubuntu process the window accumulates correctly. The Redis path uses Bun's native client (API confirmed) and **fails open**; not exercised against a live Redis here.

### G3 — JWT auth middleware
> **🎯 Goal**: verify `Authorization: Bearer` (or httpOnly cookie); on success inject `X-User-ID`/`X-User-Role` and proxy; else `401`. Public paths (login/register/health) skip the check.
> **📁 Files**: `src/utils/jwt.ts` (HS256 verify), `src/middleware/auth.ts` (+ `jwtSecret` in `config.ts`, header-strip in `routes/api.ts`, wired into `index.ts`).
> **🪜 Steps**: dependency-free HS256 verify via Web Crypto (no `jsonwebtoken`); three modes — **public** (login/register/refresh/health → skip), **optional** (`GET /geo`, `GET /services` → inject if a valid token is present, else anonymous), **required** (everything else → 401). On success forward `X-User-ID`/`X-User-Role`. 🚩 The proxy **strips any client-supplied `X-User-*`** so identity can't be spoofed. 🚩 `JWT_SECRET` must equal the backend's `JWT_SECRET_KEY`.
> **✅ Verify**:
> - JWT math (**done locally**, Bun 1.3.9 — one-shot, no server): mint tokens with the dev secret → `verifyJwtHS256` **accepts** a valid one (extracts `sub`/`role`) and **rejects** wrong-secret, tampered, expired, and garbage. **5/5 passed.**
> - Full flow (**run on Ubuntu**, gateway + FastAPI up): `GET /api/v1/users/me` with **no** token → `401`; with a valid login token → `200` (backend sees the injected `X-User-ID`); `POST /api/v1/auth/login` (public) → no 401; `GET /api/v1/services` (optional) works with or without a token.
> - Spoof check: send `X-User-ID: someone-else` on a request → the backend must NOT receive it (the gateway strips it; only verified tokens inject identity).
> **🏁 Done when**: protected routes need a valid token; public ones don't; the injected identity reaches FastAPI.
> **🧪 Status**: code written, reviewed & doc-commented; wired into `index.ts`. The crypto (the one novel part) is **runtime-verified locally** (5/5); the end-to-end token→header→backend flow is **verify on Ubuntu** (needs the FastAPI backend, absent here). Notes: no new deps (Web Crypto); a Redis token-denylist (logout revocation) is deferred — the backend's logout is stateless for now.

### G4 — WebSocket (:3001)
> **🎯 Goal**: clients `subscribe` to `service_requests`; gateway relays Redis pub/sub events (`request_created|updated|deleted`).
> **📁 Files**: `src/routes/websocket.ts` (+ `wsPort` in `config.ts`; second `Bun.serve` + `startRedisBridge()` in `index.ts`).
> **🪜 Steps**: a **separate** `Bun.serve` on `:3001` (so the URL is `ws://localhost:3001`). A client sends `{type:"subscribe", channel:"service_requests"}`; the gateway tracks per-channel subscriber sets and `broadcast()`s to them. A dedicated Redis subscriber (Bun-native pub/sub) listens on the backend's `service_requests` + `notifications` channels (M5 publishes there) and relays each message. Best-effort: no `REDIS_URL` → clients still connect, just no events.
> **✅ Verify**:
> - Bundle (**done locally**, Bun 1.3.9, no server): `bun build src/backend/api-gateway/src/index.ts --target bun` → **bundles cleanly** (all G1–G4 modules' imports/syntax OK).
> - WS handshake + fan-out (**run on Ubuntu**): `bun run dev`; connect a client to `ws://localhost:3001`, send `{"type":"subscribe","channel":"service_requests"}` → get `{"type":"subscribed",…}`; then `redis-cli PUBLISH service_requests '{"type":"request_created",…}'` → the client receives the event.
> - End-to-end (**Ubuntu**, full stack): create a request via the API → a tab subscribed to `service_requests` shows it live.
> **🏁 Done when**: creating a request in one tab pushes an event to a subscribed tab.
> **🧪 Status**: code written, reviewed & doc-commented; second WS server on `:3001` + Redis bridge wired in `index.ts`. The whole gateway **bundles cleanly locally**; the live socket + Redis relay are **verify on Ubuntu** (needs Redis + the backend, absent here). Notes: Bun-native pub/sub (`RedisClient.subscribe`, API confirmed) — no deps; per-user notification routing/auth on the socket is a future enhancement (today it relays channel messages verbatim).

---

# PART C — Frontend: HTML/Tailwind (`src/frontend/web-html/`)

Vite + Tailwind + vanilla JS. **Build the documented inventory** (from `instructions_pages_v3.md`); **delete the e‑commerce stubs**. **Read first**: `instructions/instructions_web_v3.md` (build + API client) and `instructions/instructions_ui_v3.md` (every component's Tailwind classes).

Target structure:
```
src/frontend/web-html/src/
├── index.html  about.html
├── auth/        register.html  login.html  forgot-password.html
├── pages/app/   dashboard.html  create-service.html  service-detail.html
│                my-services.html  map.html  profile.html  notifications.html
├── pages/provider/  provider-dashboard.html  available-services.html  active-services.html
├── components/  navbar.html  sidebar.html  modal.html  map-container.html  loader.html  footer.html
├── layouts/     main-layout.html  auth-layout.html  dashboard-layout.html
├── js/api/      client.js (fetch wrapper) · auth.js · services.js · geo.js · notifications.js
├── js/          auth-guard.js · ws.js · ui helpers
└── styles/      tailwind input + theme
```

### F0 — Build setup
> **🎯 Goal**: `bun run dev` serves the site on :5173 with Tailwind working and a reusable API client.
> **📁 Files**: `package.json`, `vite.config.js`, `postcss.config.js`, `tailwind.config.js`, `src/js/api/client.js`, `src/js/auth-guard.js`, `src/js/main.js`, `index.html` (`src/styles/main.css` already has the `@tailwind` directives).
> **🪜 Steps**: `package.json` + Vite + `tailwind.config.js` (Inter; Tailwind's `slate`/`emerald` per `instructions_ui_v3.md`); `src/js/api/client.js` (dependency-free **fetch** wrapper — relative `/api/v1` via the Vite proxy, Bearer token, proactive refresh ~1 min before expiry + reactive 401 retry); `src/js/auth-guard.js` (redirect to login if no token). Vite proxies `/api`→:3000 and `/ws`→:3001 so the app uses relative URLs (no CORS in dev).
> **✅ Verify** (run on the **Ubuntu** dev laptop):
> - `cd src/frontend/web-html && bun install && bun run dev` → Vite serves on **http://localhost:5173** (hot-reload).
> - Open it: the landing page is **Slate+Emerald / Inter** styled (Tailwind works). With the gateway+backend up, the header badge reads **“API: ok”** (client.js → `/api/v1/health` via the proxy); with them down it shows “API unreachable”.
> - Build: `bun run build` completes; `bun run preview` serves the production bundle.
> **🏁 Done when**: a Tailwind-styled page loads on :5173 and `client.js` reaches `/api/v1/health`.
> **🧪 Status**: code written, reviewed & comment-checked (JS/JSDoc + HTML — **not Python**, so no doc-strings here). **Run on Ubuntu** (the authoring box is Windows-only). Notes: chose a **fetch** client (no Axios dep) per this workflow — `instructions_web_v3.md`'s Axios variant is an alternative; auth responses read **bare** (`res.data.access_token`), matching the M2 backend. The pre-existing **e-commerce stub files** (`product-*`, `cart`, `checkout`, `payment`, `product-card`, `cart-item`, `payment-form`) are still present — delete them during **F1** (not in the IDRM page inventory).

### F1 — Public pages (`index.html`, `about.html`)
> **🎯 Goal**: a public landing + About page. Hero + "Request Help"/"Register as provider" CTAs, emergency hotlines, "how it works"; if a token exists, redirect to `dashboard`. **No API calls** (must load even if the backend is down). Also: **delete the e-commerce stubs**.
> **📁 Files**: `index.html` (landing, rewritten), `src/pages/about.html` (new), `src/js/main.js` (now just redirect-if-authed). **Removed** the e-commerce stubs (`product-*`, `cart`, `checkout`, `payment` pages + `product-card`/`cart-item`/`payment-form` components) and two empty `index.html` duplicates.
> **✅ Verify** (run on the **Ubuntu** dev laptop):
> - `bun run dev` → open `http://localhost:5173`: a Slate+Emerald landing with hero, CTAs, hotlines, "how it works"; **no calls** to `/api` (DevTools → Network) — it renders with the backend down.
> - Click **About** → `/src/pages/about.html` loads (static). CTAs link to `register.html` / `login.html`.
> - Authed redirect: set `sessionStorage.access_token` to any value in DevTools, reload `/` → you're sent to the dashboard.
> - `ls src/pages src/components` shows **no** product/cart/checkout/payment files.
> **🏁 Done when**: the public landing + About render with no API calls, CTAs link correctly, an authed visitor is redirected, and the e-commerce stubs are gone.
> **🧪 Status**: built & comment-checked (HTML + a 3-line `main.js`; **not Python** → no doc-strings). E-commerce stubs **deleted** (confirmed via `ls`). **Render-verify on Ubuntu** (the authoring box is Windows-only).

### F2 — Auth pages (`login.html`, `register.html`, `forgot-password.html`)
> **🎯 Goal**: forms calling `POST /auth/login|register`; store tokens in `sessionStorage` (via the F0 client); client-side validation; redirect-if-authed.
> **📁 Files**: `src/pages/{login,register,forgot-password}.html`, `src/js/{auth-login,auth-register}.js`, `register()` added to `src/js/api/client.js`, page entries added to `vite.config.js`. (Pages live under `src/pages/` — the existing layout — not `auth/`.)
> **🪜 Notes**: login → `client.login()` → redirect to `?next=` or the dashboard. register (self-roles **CITIZEN/PROVIDER/VOLUNTEER**, optional E.164 phone, language en/hi/te) → `client.register()` → **auto-login** → dashboard; `?role=` preselects. **phone + OTP quick-start** is a **disabled "coming soon"** control (no backend OTP endpoint yet); **forgot-password** is a placeholder page (no reset endpoint yet).
> **✅ Verify** (run on the **Ubuntu** dev laptop, backend + gateway up):
> - `bun run dev`; open `/src/pages/register.html` → fill + submit → account created, auto-signed-in, redirected to the dashboard. Re-registering the same email → inline "already registered" (409).
> - `/src/pages/login.html` → wrong password → "Incorrect email or password" (401); correct → dashboard; `?next=…` honored.
> - Tokens land in `sessionStorage` (DevTools → Application). Visiting login/register while signed in redirects to the dashboard.
> - Validation: short password / bad phone show inline errors before any request fires.
> **🏁 Done when**: a new user can register and log in (tokens stored; protected pages reachable).
> **🧪 Status**: built & comment-checked (HTML + JSDoc'd JS — **not Python**). **Run on Ubuntu** (authoring box is Windows-only). Notes: auth reads the **bare** token shape (matches M2); OTP quick-start + password-reset are deferred (no backend endpoints) and shown as "coming soon".

### F3 — Citizen core (`dashboard`, `create-service`, `service-detail`, `my-services`)
> **🎯 Goal**: per `instructions_pages_v3.md` 1.5–1.8, built to the **canonical** API (`/services` + `POST /{id}/<action>`, not the doc's stale `/services/requests` + `PUT …/status`). `create-service` uses the enums + a Leaflet pin; `service-detail` shows the status badge + the requestor's action buttons.
> **📁 Files**: `src/pages/{dashboard,create-service,service-detail,my-services}.html` + `src/js/{dashboard,create-service,service-detail,my-services}.js`; shared `src/js/api/services.js` + `src/js/ui.js` (badges, app header, escapeHtml); `getMe()` added to the client; page entries added to `vite.config.js`. **Backend:** added `?mine=true` to `GET /services` (M3 `list_requests` requestor filter) so "My requests" can list the user's own.
> **🪜 Notes**: all four pages are auth-gated (`requireAuth`). create → GeoJSON `[lon,lat]` (Leaflet is `[lat,lng]`) → `/services` → detail. detail actions (owner-only client-side; backend enforces): Cancel (SUBMITTED/APPROVED), Confirm & rate (COMPLETED), Dispute (IN_PROGRESS/COMPLETED). Leaflet via jsdelivr + no-subdomain OSM tiles (CSP-safe); user text is `escapeHtml`-d before innerHTML.
> **✅ Verify** (run on the **Ubuntu** dev laptop, full stack up — register/login first):
> - `create-service`: drop a map pin (or "Use my location"), fill + submit → lands on `service-detail` at **SUBMITTED** (or **APPROVED** if CRITICAL/HIGH).
> - `service-detail`: badges, description, mini-map, timeline render; **Cancel** works while SUBMITTED/APPROVED.
> - Lifecycle walk (seed a DM + provider + verified org, per M3): approve → accept → start → complete → on the citizen detail page **Confirm & rate** → **VERIFIED**.
> - `my-services`: lists only your requests (`?mine=true`) with status filter + pagination + quick Cancel; `dashboard`: greeting + count + recent 5.
> **🏁 Done when**: a citizen can create a request and track it to VERIFIED.
> **🧪 Status**: built & comment-checked (HTML + JSDoc'd JS — **not Python**). **Run on Ubuntu** (authoring box is Windows-only). Notes: built to the canonical API (doc paths are stale); added the `?mine=true` backend filter; rating/dispute use simple `prompt()` for the MVP (a nicer inline star-form is a polish item).

### F4 — Map (`map-view.html`)
> **🎯 Goal**: Leaflet + OSM tiles; markers coloured by priority (CRITICAL=red, HIGH=orange, MEDIUM=amber, LOW=green); cluster circles when zoomed out; live updates via the WebSocket (G4).
> **📁 Files**: `src/pages/map-view.html` + `src/js/map-view.js`; shared `src/js/api/geo.js`; page entry added to `vite.config.js`.
> **🪜 Notes**: auth-gated. Zoom ≥ 12 → individual `circleMarker`s via `GET /geo/nearby` (radius derived from the viewport, ≤ 50 km); zoom < 12 → cluster circles via `GET /geo/cluster?zoom&bounds` (radius ∝ count, colour = highest priority inside). Pan/zoom + WebSocket events trigger a **debounced** refresh. WS connects to `/ws` (Vite proxies → gateway :3001), subscribes to `service_requests`, refreshes on `request_*`. Leaflet via jsdelivr + no-subdomain OSM tiles (CSP-safe); GeoJSON `[lon,lat]` ↔ Leaflet `[lat,lng]`.
> **✅ Verify** (run on the **Ubuntu** dev laptop, full stack + Redis up):
> - `bun run dev` → open `/src/pages/map-view.html` (signed in): the map renders on Hyderabad; create a request → a coloured marker appears.
> - Zoom out below ~12 → markers collapse into **cluster circles** with counts; zoom in → individual pins return. The **type filter** narrows results.
> - Click a marker → popup with type/priority/status + a "View request" link to the detail page.
> - **Real-time**: with Redis up, create a request in another tab → it shows on the map within a moment (WS `request_created` → refresh).
> **🏁 Done when**: new requests appear on the map in real time.
> **🧪 Status**: built & comment-checked (HTML + JSDoc'd JS — **not Python**). **Run on Ubuntu** (authoring box is Windows-only; live updates also need Redis + the backend publisher). Notes: "Request here" right-click + "find nearest provider" (spec 1.9) are deferred polish; the WS reconnects on close (5s).

### F5 — Notifications + Profile
> **🎯 Goal**: `notifications.html` (list + mark read) and `profile.html` (edit name/phone/language).
> **📁 Files**: `src/pages/{notifications,profile}.html` + `src/js/{notifications,profile}.js`; `src/js/api/notifications.js`; `updateMe()` added to the client; Notifications/Profile links added to the app header (`ui.js`); Vite inputs. **Backend:** `NotificationOut` now includes `related_service_id` (M5) so notifications can deep-link to their request.
> **🪜 Notes**: both auth-gated. notifications → `GET /notifications` (`{status,data:{items,unread_count}}`), highlight unread, **Mark read** → `POST /notifications/{id}/read`, deep-link via `related_service_id`. profile → `GET /users/me` prefill → edit → `POST /users/me` (`{full_name, phone?, preferences:{language}}`); email + role read-only.
> **✅ Verify** (run on the **Ubuntu** dev laptop, backend + gateway up):
> - Trigger a notification (e.g. a provider accepts the user's request) → `notifications.html` shows it **unread**; **Mark read** clears it + drops the unread count; the title links to the request.
> - `profile.html` loads your name/phone/language; change the language + name → Save → "Profile saved"; a reload of `/users/me` reflects it. Email/role are read-only.
> **🏁 Done when**: notifications list + mark-read work, and a profile edit persists.
> **🧪 Status**: built & comment-checked (HTML + JSDoc'd JS — **not Python**). **Run on Ubuntu** (authoring box is Windows-only). Note: a "mark all read" control is omitted (no backend endpoint).

### F6 — Provider pages
> **🎯 Goal**: provider workspace — available + active services with the **Accept → Start → Complete** flow.
> **📁 Files**: `src/pages/provider.html` + `src/js/provider.js` (uses the accept/start/complete helpers already in `src/js/api/services.js`); conditional "Provider" link in the app header (`ui.js`, PROVIDER/ADMIN only); Vite input. **Backend:** added `?provider_id=<org>` to `GET /services` (M3 list filter) for "my active assignments".
> **🪜 Notes**: auth-gated + role-gated (PROVIDER/ADMIN; soft client check, backend enforces). **Available** = `GET /services?status=APPROVED` → Accept. **My active** = `GET /services?provider_id=<org>` → Start (ACCEPTED→IN_PROGRESS) / Complete (IN_PROGRESS→COMPLETED). Org gap: the provider pastes their verified **org UUID** (localStorage) — sent as `org_id` on accept + used to filter active (until user↔org membership exists).
> **✅ Verify** (run on the **Ubuntu** dev laptop; seed a verified org, set its UUID in the Org box):
> - As a PROVIDER, open `/src/pages/provider.html`: **Available** lists APPROVED requests; **Accept** one → it moves to **My active** as ACCEPTED.
> - **Start** (→ IN_PROGRESS) then **Complete** (→ COMPLETED); the citizen can then Confirm & rate (F3) → VERIFIED.
> - A non-provider account sees the "for provider accounts" notice; the Provider nav link only shows for PROVIDER/ADMIN.
> **🏁 Done when**: a provider can accept and progress a request through to COMPLETED.
> **🧪 Status**: built & comment-checked (HTML + JSDoc'd JS — **not Python**). **Run on Ubuntu** (authoring box is Windows-only). Notes: single combined workspace page (dashboard/available/active in one) for the MVP; org UUID is pasted (no user↔org link yet); the provider's `service_types` filter on "available" (spec 1.13) is deferred.

---

# PART D — React SPA (`src/frontend/web-react/`) — after the HTML slice works

React 18 + TS + Vite + React Router + React Query + Zustand + Recharts + react-leaflet. Admin/coordinator pages from `instructions_pages_v3.md` Part 2 (`Dashboard`, `RequestList/Detail/Approval`, `UserList/Detail`, `ProviderList/Detail`, `analytics/*`, `LiveMap`). Reuse the same API client shape and the Slate+Emerald tokens (as a Tailwind config). **React Native (mobile) is Post-MVP** — skip for now.

**Built (foundation slice).** Scaffolded `src/frontend/web-react/` from empty: Vite + TS + Tailwind (Slate+Emerald+Inter) on **:5174**, proxying `/api`→:3000 & `/ws`→:3001. Files: `package.json` (React 18, react-router-dom v6, @tanstack/react-query v5, zustand v4, recharts), `tsconfig*.json`, `vite.config.ts`, `tailwind.config.js`, `postcss.config.js`, `index.html`, `.gitignore`, `README.md`; `src/` → `main.tsx` (QueryClient + Router providers), `App.tsx` (route table), `index.css`, `vite-env.d.ts`, `lib/api.ts` (typed fetch client — sessionStorage tokens + one silent `/auth/refresh` retry; `login/logout/getMe/getDashboard/listServices/approveService/rejectService` + full enum/`User`/`ServiceRequest`/`Paginated`/`DashboardData` types), `store/auth.ts` (Zustand, sessionStorage-seeded), `components/{Layout,ProtectedRoute}.tsx`, `pages/{Login,Dashboard,Requests}.tsx`. Core admin views: **Login**, **Dashboard** (Recharts bars from `GET /analytics/dashboard`), and the distinctly-admin **Approval queue** (`GET /services?status=SUBMITTED` → `POST /services/{id}/approve|reject`, the DM_AUTHORITY capability). **Deferred** (tracked in README): user management + `POST /users/{id}/role`, provider/org views, admin LiveMap (react-leaflet) + `/geo/cluster`, request detail drawer, live WebSocket updates.

> **✅ Verify** (on the **Ubuntu dev laptop** — Windows is authoring-only; needs FastAPI :8000 + gateway :3000/:3001 + Postgres/Redis up):
> ```bash
> cd src/frontend/web-react
> bun install                       # or: npm install
> bun run build                     # tsc -b && vite build → typechecks + bundles (no server/ports)
> bun run dev                       # Vite dev server → http://localhost:5174
> ```
> Then in the browser (all calls go through the gateway proxy → no CORS):
> - **Auth/guard**: hitting `/` while signed out redirects to `/login`; signing in as a `DM_AUTHORITY`/`ADMIN` lands on the Dashboard; **Sign out** clears the session and bounces back to `/login`.
> - **Dashboard**: 4 stat cards (total / active / avg-response-min / completion-rate %) + two Recharts bar charts (by service type, by status) render from `GET /analytics/dashboard`.
> - **Approval queue** (`/requests`): SUBMITTED rows list; **Approve** (`POST /{id}/approve`) and **Reject** (prompts for a reason → `POST /{id}/reject`) drop the row from the queue (React Query invalidation); a non-DM/ADMIN account surfaces the backend **403** inline.
> - **Token refresh**: leave the tab idle past the 15-min access-token expiry, then act — the silent `/auth/refresh` retry keeps the session alive (no forced re-login).
> - **Network**: confirm requests use the bare `/api/v1/...` paths (DevTools → Network) and carry `Authorization: Bearer …`.
> **🏁 Done when**: an admin can sign in, read the analytics dashboard, and clear the approval queue end-to-end against the live stack.
> **🧪 Status**: built & comment-checked (**TS → JSDoc/block comments, not Python docstrings**). ⏳ **Verify on Ubuntu** (authoring box is Windows-only; not run/built here). Notes: foundation slice only — the deferred views above are intentionally out of this pass; `react-leaflet`/`leaflet` deliberately **not** added to `package.json` yet (add when building the admin LiveMap).

---

## Progress tracker (tick as you go)

| # | Module | Done |
|---|--------|:----:|
| M0 | Backend boot + health | ✅ |
| M1 | Models & schemas | ✅ |
| M2 | Auth | ✅ |
| M3 | Service requests + actions | ✅ |
| M4 | Geo (PostGIS) | ✅ |
| M5 | Notifications | ✅ |
| M6 | Analytics | ✅ |
| G1 | Gateway proxy | ✅ |
| G2 | Rate limiting | ✅ |
| G3 | JWT middleware | ✅ |
| G4 | WebSocket | ✅ |
| F0 | web-html build setup | ✅ |
| F1 | Public pages | ✅ |
| F2 | Auth pages | ✅ |
| F3 | Citizen core | ✅ |
| F4 | Map | ✅ |
| F5 | Notifications + Profile | ✅ |
| F6 | Provider pages | ✅ |
| D | React SPA (admin) | ✅ |

---

## Reconciliation notes (cleanups to make as you build)
- **Delete** the e‑commerce stub files in `web-html` (`cart*.html`, `checkout.html`, `payment*.html`, `product-*.html`) — they're a wrong template and aren't in the IDRM inventory.
- Where `instructions_pages_v3.md` still shows `/api/v1/services/requests` or `PUT …/status`, use the **canonical** `/api/v1/services` + `POST /{id}/<action>` instead.
- Backend route folder is **`api/v1/`** (matches the `/api/v1` base URL), not a flat `api/`.

---

*Next: pick the top unchecked module and build it. Start with **M0**. When the vertical slice (through F4) works, you have a demoable MVP.*
