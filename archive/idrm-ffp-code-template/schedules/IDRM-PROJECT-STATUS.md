# IDRM Project Status, Decisions Log & Pending Work

**Last updated**: 2026-05-31
**Purpose**: The single place to see **where the project stands, every decision we've locked in, and what still needs doing**. New contributors should read this first, then the doc that matches their task (see the map below).

> This is a living status/tracker doc. The **build mechanics** live in `IDRM-BUILD-WORKFLOW.md`; the **timeline** lives in `IDRM-IMPLEMENTATION-GUIDE.md`; the **gap analysis** lives in `IDRM-MVP-ANALYSIS-ROADMAP.md`. This file ties them together.

---

## 1. At a glance

| Area | State |
|------|-------|
| **Documentation** | ✅ Reconciled & internally consistent (FS/PRD/HLD/LLD/CLAUDE/DB+API guides + all 44 markdown files swept) |
| **UI design system** | ✅ Canonical: Slate + Emerald (`instructions/instructions_ui_v3.md`) |
| **Setup scripts / infra** | ✅ Complete (prereqs, dev, staging, prod, Docker Compose, Makefile, `.env`, requirements) |
| **Database schema** | ✅ Written (`database/init/01–03.sql`); migrations (Alembic) pending |
| **Backend code** | 🏗️ **M0–M6 written — feature-complete** (boot/health, models/schemas, auth, service lifecycle, geo, notifications + Redis pub/sub, analytics). Not yet run here; Alembic migrations + tests pending. |
| **API Gateway** | 🏗️ **G1–G4 built** (proxy, CORS, security, rate-limit, JWT auth, WebSocket) — bundles cleanly; G1 + G3-crypto ran locally; live flow **verify on Ubuntu**. |
| **Frontend (web-html)** | 🏗️ **F0–F6 built** — full web-html track (setup, public, auth, citizen core, map, notifications/profile, provider). Verify on Ubuntu. |
| **React SPA (web-react)** | 🏗️ **Part D foundation built** — Login + analytics Dashboard (Recharts) + approval queue (DM_AUTHORITY approve/reject). Verify on Ubuntu; user/provider mgmt + LiveMap deferred. |
| **Mobile (Expo)** | 🔒 Post-MVP |
| **Git** | ⚠️ **Nothing committed yet** this session |

---

## 2. Schedules directory map (what each doc is for)

| Doc | Use it for |
|-----|-----------|
| **IDRM-PROJECT-STATUS.md** (this file) | Current status, decisions log, pending backlog |
| `IDRM-BUILD-WORKFLOW.md` | **How** to build each module, step-by-step (rookie playbook, M0→F6) |
| `IDRM-IMPLEMENTATION-GUIDE.md` | **When** — the 16-week timeline |
| `IDRM-MVP-ANALYSIS-ROADMAP.md` | Gap analysis, what's built vs missing, beginner orientation |
| `idrm-task-execution-matrix.xlsx` | _(empty placeholder — superseded by the trackers in this file & the build workflow)_ |

---

## 3. Decisions log (locked — build to these)

These were reconciled across all docs this session. **Source of truth for roles/permissions = `docs/development/IDRM-FS.md` §3.3.**

| # | Decision | Notes / why |
|---|----------|-------------|
| D1 | **10 account roles + a Public tier** | `CITIZEN, VOLUNTEER, ORGANIZER, PROVIDER, MANAGER, EVENT_MANAGER, EXECUTIVE, DM_AUTHORITY, AUDITOR, ADMIN` + "Public" (not logged in). Expanded from the old 6. |
| D2 | **"Event Admin" = `DM_AUTHORITY`**, can be a **GO or NGO** | The approving authority; `EVENT_MANAGER` (L5) runs a disaster-event instance below it. |
| D3 | **`EXECUTIVE` = Post-MVP**, **`AUDITOR` = MVP read-only** | Auditor's credibility/expense scoring is Post-MVP. |
| D4 | **Statuses (10)**: `SUBMITTED→APPROVED→ACCEPTED→IN_PROGRESS→COMPLETED→VERIFIED` + `REJECTED, CANCELLED, EXPIRED, DISPUTED` | Use `ACCEPTED` (not `ASSIGNED`); dropped `DRAFT`/`CLOSED`. |
| D5 | **Emergencies auto-approved** | `CRITICAL`/`HIGH` go `SUBMITTED→APPROVED` by the system, reviewed for credibility after. |
| D6 | **Service types (6)**: `RESCUE, MEDICAL, FOOD, SHELTER, WATER, OTHER` | "Clothing" → `OTHER` + description. |
| D7 | **Privacy (3)**: `PUBLIC, PROTECTED, PRIVATE`, **default `PROTECTED`**, raise-only | `PROTECTED` hides name/phone from public; responders get contact via the system. |
| D8 | **Auth**: 15-min access + 7-day refresh, `Authorization: Bearer` (httpOnly cookie optional, gateway also reads it) | |
| D9 | **Guest access** = **phone + OTP quick-start** → lightweight verified `CITIZEN` | No anonymous submits; no long form. |
| D10 | **MVP scope** = 2-district pilot (**Hyderabad + Vijayawada**) | pan-India / 100k MAU / 25k-peak = **growth targets**, not MVP. |
| D11 | **Targets**: API p95 <500ms (per-category), page <3s, DB <100ms; satisfaction 1–5 (4.0 MVP / 4.5 scale); uptime 99.5% MVP → 99.9% growth | |
| D12 | **Languages**: `en`, `hi`, `te` (English, Hindi, Telugu) | 12+ = growth target. Pilot region is Telugu-speaking. |
| D13 | **Out of MVP**: Finance/Donations, AI Chatbot, native mobile app, MAD module | Finance: recorded **eventually**, implicit & event-driven allocation. |
| D14 | **Backend data layer** = SQLAlchemy 2.0 **async** + **GeoAlchemy2** | Alembic migrations. |
| D15 | **API** = GET/POST only, under `/api/v1`, **action sub-endpoints** (`/{id}/approve|accept|…`) | No PUT/DELETE; not `/services/requests`; route folder is `api/v1/`. |
| D16 | **UI** = Slate + Emerald, canonical rulebook `instructions_ui_v3.md` | Priority colors = FS map convention: Critical=red, High=orange, Medium=amber, Low=green. |
| D17 | **Version** stays **3.0** + "reconciled 2026-05-30" | No fictional 3.1 release. |

---

## 4. Completed this session

- **Phase 1 — FS ↔ PRD reconciliation**: 8 core docs aligned (FS, PRD, HLD, LLD, `CLAUDE.md`, DB guide, API guide, `02-schema.sql`).
- **Phase 2 — repo-wide audit**: all 44 markdown files swept; ~21 fixed; verified clean of stale enums/paths/tokens.
- **UI**: authored `instructions/instructions_ui_v3.md`; re-skinned `COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md` to Slate + Emerald.
- **Setup scripts & infra (12 files)**: `scripts/_lib.sh`, `setup-{prerequisites,development-monolith,development-modular,staging,production}.sh`, `infra/docker/full-stack.yml`, `src/backend/requirements.txt`, `.env`, `.gitignore`, `.gitattributes`, `Makefile`.
- **Schedules**: fixed the stale folder tree in the roadmap; created `IDRM-BUILD-WORKFLOW.md`.
- **Backend M0**: `src/backend/app-python/{main.py, core/config.py, core/database.py, core/__init__.py}` — app boots, CORS, `/api/v1/health` + `/health/ready`, async DB session.
- **Backend M1**: `dbmodels/*.py` (Base, enums, User, Organization, ServiceRequest, Notification, AuditLog) + `schemas/*.py` (common, auth, user, service, geo, notification, analytics) — SQLAlchemy 2.0 async ORM (GeoAlchemy2 `POINT`/4326) mirroring `02-schema.sql`, plus Pydantic v2 request/response models.
- **Docs pass (M0 + M1)**: added class-level docstrings to all 5 ORM models, all 11 enums, and every Pydantic schema class; fixed a stale `core/__init__.py` comment. Docstrings/comments only — no behaviour change.
- **Backend M2 (Auth)**: `core/security.py` (bcrypt cost 12 + JWT access/refresh + `get_current_user`), `services/auth_service.py`, `api/v1/{auth,users}.py` (+ package inits), wired into `main.py` — `POST /auth/{register,login,refresh,logout}` and `GET|POST /users/me`. Also: `UserOut` now exposes the PK as `id`, `UserUpdate` takes `preferences`. (phone+OTP quick-start deferred — needs an SMS provider.)
- **Backend M3 (Service requests)**: `services/service_service.py` + `api/v1/services.py` — create (auto-approve CRITICAL/HIGH), list (filters+pagination, `{status,data}` envelope), get (privacy-aware), and the lifecycle actions approve/reject/accept/**start**/complete/verify/cancel/dispute per FS §6.1, wired into `main.py`. PostGIS via `ST_MakePoint`/`to_shape`; race-safe accept (`SELECT … FOR UPDATE`); added `get_current_user_optional` + `ServiceListResponse`; `AcceptBody` gained `org_id`.
- **Backend M4 (Geo)**: `services/geo_service.py` + `api/v1/geo.py` — `GET /geo/nearby` (ST_DWithin on `::geography`, nearest-first, optional service_type) and `GET /geo/cluster` (ST_ClusterKMeans, zoom-derived k, optional bounds), wired into `main.py`. Public/read-only, live requests only; raw parameterised PostGIS SQL via `text()`.
- **Backend M5 (Notifications)**: `core/redis.py` (async client + best-effort `publish_json`), `services/notification_service.py`, `api/v1/notifications.py`, reshaped `schemas/notification.py` (`{id,type,title,message,read,created_at}` + `{status,data}`), wired into `main.py`. Emissions added to the M3 lifecycle: requestor notified on accept (SERVICE_ACCEPTED) + complete (VERIFICATION_REQUEST); `request_created`/`request_updated` published to Redis for the gateway/WebSocket (G4).
- **Backend M6 (Analytics)**: `services/analytics_service.py` + `api/v1/analytics.py` — `GET /analytics/dashboard` (totals, active count, completion rate, avg response time, by-type/by-status breakdowns), Redis-cached 5 min (added `cache_get_json`/`cache_set_json` to `core/redis.py`), wired into `main.py`. **All backend feature routers (M2–M6) are now mounted.**
- **Gateway G1 (Proxy skeleton)**: `src/backend/api-gateway/` — Bun.serve on :3000 proxies `/api/*` to FastAPI, answers the CORS preflight, and adds CORS + security headers to every response (`src/{index,config}.ts`, `src/middleware/{cors,security}.ts`, `src/routes/api.ts` + `package.json`/`tsconfig.json`/`.env.example`). **Runtime-verified** with Bun 1.3.9 (proxy/preflight/404/502 + headers all confirmed). Later hardened the proxy with a 30s timeout (→ 504).
- **Gateway G2 (Rate limiting)**: `src/middleware/rateLimit.ts` (+ `config.redisUrl`, wired into `index.ts`) — per-IP/endpoint fixed-window limits (login 5/15min, API 60/min, …) → 429 + `Retry-After`, with auth-endpoint blocking and `X-RateLimit-*` headers. Pluggable store: in-memory (single-instance MVP default) or Redis (Bun-native, fail-open, for multi-replica). **Verify on Ubuntu** (Windows authoring box gave an inconclusive run — see §4b).
- **Gateway G3 (JWT auth)**: `src/utils/jwt.ts` (dependency-free HS256 verify via Web Crypto) + `src/middleware/auth.ts` (public/optional/required modes; injects `X-User-ID`/`X-User-Role`), wired into `index.ts`; `routes/api.ts` now **strips client-supplied `X-User-*`** (anti-spoof); `config.jwtSecret` added. JWT verify **runtime-checked locally** (5/5: valid / wrong-secret / tampered / expired / garbage); full token→backend flow verify on Ubuntu.
- **Gateway G4 (WebSocket)**: `src/routes/websocket.ts` (+ `config.wsPort`, second `Bun.serve` + `startRedisBridge()` in `index.ts`) — a dedicated `:3001` WebSocket server; clients `{type:"subscribe",channel}` join per-channel sets; a Bun-native Redis subscriber relays the backend's `service_requests`/`notifications` events to them. No deps; best-effort (works without Redis, just no events). **Gateway G1–G4 now complete** (bundles cleanly; live relay verify on Ubuntu).
- **Frontend F0 (web-html build setup)**: `package.json` (Vite + Tailwind), `vite.config.js` (:5173 + `/api`→:3000, `/ws`→:3001 proxy), `postcss.config.js`, `tailwind.config.js` (Slate+Emerald + Inter), `src/js/api/client.js` (dependency-free fetch wrapper — Bearer + proactive/reactive refresh), `src/js/auth-guard.js`, and a Slate+Emerald landing `index.html` that self-checks `/api/v1/health`. **Run on Ubuntu** (`bun install && bun run dev`).
- **Frontend F1 (public pages)**: rewrote `index.html` as the public landing (hero, Request-help/Provider CTAs, emergency hotlines, "how it works") + new `src/pages/about.html`; `main.js` is now just redirect-if-authed; **no API calls** on public pages. **Deleted the e-commerce stubs** (`product-*`/`cart`/`checkout`/`payment` + their components) and two empty `index.html` duplicates.
- **Frontend F2 (auth pages)**: `src/pages/{login,register,forgot-password}.html` + `src/js/{auth-login,auth-register}.js`; added `register()` to the API client and the page entries to `vite.config.js`. Login → store session → `?next`/dashboard; register (self-roles, optional phone, language) → auto-login → dashboard; client-side validation; redirect-if-authed. Phone+OTP and password-reset shown as "coming soon" (no backend endpoints yet).
- **Frontend F3 (citizen core)**: `src/pages/{dashboard,create-service,service-detail,my-services}.html` + matching `src/js/*`; shared `src/js/api/services.js` + `src/js/ui.js` (badges/app-header/escapeHtml); `getMe()` on the client; Vite inputs. create-service uses a Leaflet pin (jsdelivr + no-subdomain OSM, CSP-safe) → POST `/services`; service-detail shows badges/timeline/mini-map + owner actions (cancel/verify/dispute); my-services + dashboard list via `?mine=true`. Built to the **canonical** API (doc paths stale). **Backend:** added `?mine=true` to `GET /services` (M3 requestor filter).
- **Frontend F4 (live map)**: `src/pages/map-view.html` + `src/js/map-view.js` + `src/js/api/geo.js` (Vite input added). Leaflet/OSM; priority-coloured `circleMarker`s via `/geo/nearby` when zoomed in, cluster circles via `/geo/cluster` when zoomed out; type filter; legend; marker popups link to detail. **WebSocket** (`/ws` → gateway G4) subscribes to `service_requests` and debounce-refreshes on `request_*` → near-real-time.
- **Frontend F5 (notifications + profile)**: `src/pages/{notifications,profile}.html` + `src/js/{notifications,profile}.js` + `src/js/api/notifications.js`; `updateMe()` on the client; Notifications/Profile links in the app header; Vite inputs. notifications: list + unread highlight + mark-read + deep-link; profile: edit name/phone/language via `POST /users/me`. **Backend:** added `related_service_id` to `NotificationOut` (M5) for deep-linking.
- **Frontend F6 (provider pages)**: `src/pages/provider.html` + `src/js/provider.js` (uses the accept/start/complete helpers in `services.js`); conditional Provider nav link (PROVIDER/ADMIN); Vite input. Available (`?status=APPROVED`) → Accept; My active (`?provider_id=<org>`) → Start/Complete; org UUID pasted (localStorage) until user↔org linking exists. **Backend:** added `?provider_id` to `GET /services` (M3 filter). **🏁 web-html F0–F6 complete.**
- **React SPA Part D (admin foundation)**: scaffolded `src/frontend/web-react/` from empty — Vite + TS + Tailwind (Slate+Emerald+Inter) on **:5174**, proxying `/api`→:3000 & `/ws`→:3001. `lib/api.ts` (typed fetch client: sessionStorage tokens + one silent `/auth/refresh` retry; `login/logout/getMe/getDashboard/listServices/approveService/rejectService` + full enum/`User`/`ServiceRequest`/`Paginated`/`DashboardData` types), `store/auth.ts` (Zustand), `components/{Layout,ProtectedRoute}.tsx`, `pages/{Login,Dashboard,Requests}.tsx`, `main.tsx`/`App.tsx` (React Query + Router). Core admin views: **Login**, **Dashboard** (Recharts bars from `GET /analytics/dashboard`), **Approval queue** (`GET /services?status=SUBMITTED` → `POST /{id}/approve|reject` — the DM_AUTHORITY capability). **Deferred** (README + workflow): user mgmt + `POST /users/{id}/role`, provider/org views, admin LiveMap (react-leaflet) + `/geo/cluster`, request detail drawer, live WS updates. Comments are **TS JSDoc/block — not Python docstrings**. **Verify on Ubuntu.**

---

## 4b. Verification log (how completed work was checked)

| Item | Verified by | Result |
|------|-------------|--------|
| Docs reconciliation + repo-wide audit | `grep` sweep across all 44 `.md` for stale enums / paths / tokens | ✅ Clean — only intentional residuals (changelog text, migration-doc `8002`, archived crosswalk) |
| Setup shell scripts (`scripts/*.sh`) | `bash -n` syntax check on all 6 | ✅ All pass |
| `Makefile` | recipe-indentation check | ✅ 23 tab-indented recipes, 0 space-indented |
| `.env` ↔ production guard | `setup-production.sh` greps for the dev password / `change-in-production` secret | ✅ Guard blocks dev defaults reaching production |
| **Backend M0** | `py_compile` → `uvicorn` → `curl /api/v1/health` (full commands in `IDRM-BUILD-WORKFLOW.md` → M0 **✅ Verify**) | ⏳ Code written & reviewed; **run on a machine with Python/conda to confirm** (no Python in the authoring environment) |
| **Backend M1** | enum/column cross-check vs `02-schema.sql`; `from dbmodels import *` & `import schemas` import test; `py_compile dbmodels/*.py schemas/*.py` (commands in `IDRM-BUILD-WORKFLOW.md` → M1 **✅ Verify**) | ⏳ Reviewed & cross-checked by eye (the `audit_logs.user_id` FK bug found in review was fixed); **run the imports/compile to confirm** (no Python here) |
| **Docs pass (M0 + M1)** | `grep -rn -A1 '^class '` over `dbmodels/` + `schemas/` (every class → a docstring); re-read `geo.py`/`auth.py` to confirm doc URLs intact | ✅ All classes carry a docstring; docstrings/comments only — no behaviour change. `py_compile` deferred (no Python here) |
| **Backend M2 (Auth)** | docstring-coverage grep over `security.py`/`auth_service.py`/routes; checked no stale `UserOut.user_id` / `UserUpdate.language_preference`; round-trip + guard plan (register→login→/users/me→refresh; 403/409/401) in `IDRM-BUILD-WORKFLOW.md` → M2 **✅ Verify** | ⏳ Code written, reviewed & wired into `main.py`; **run the round-trip on a machine with Python/conda + Postgres to confirm** (no Python here) |
| **Backend M3 (Services)** | docstring-coverage grep (21 service fns + 11 routes); role/status guards mapped to the FS §6.1 state machine; full-lifecycle + reject/dispute + guard plan in `IDRM-BUILD-WORKFLOW.md` → M3 **✅ Verify** | ⏳ Code written, reviewed & wired into `main.py`; **run the lifecycle walk on a machine with Python/conda + Postgres (seed a DM + provider + verified org) to confirm** (no Python here) |
| **Backend M4 (Geo)** | docstring-coverage grep (geo_service + routes); SQL mirrored against Query Reference §Spatial; nearby/cluster + edge-case plan (empty, radius clamp, bad bounds → 400, range → 422) in `IDRM-BUILD-WORKFLOW.md` → M4 **✅ Verify** | ⏳ Code written, reviewed & wired into `main.py`; **run on a machine with Python/conda + PostGIS to confirm** (no Python here) |
| **Backend M5 (Notifications)** | docstring-coverage grep (notification_service + redis + routes); confirmed 14 emission hooks in `service_service.py`; list/mark-read + accept/complete-notify plan in `IDRM-BUILD-WORKFLOW.md` → M5 **✅ Verify** | ⏳ Code written, reviewed & wired into `main.py`; **run on a machine with Python/conda + Postgres (+ Redis for realtime) to confirm** (no Python here) |
| **Backend M6 (Analytics)** | docstring-coverage grep (analytics_service + cache helpers + route); response shape checked against CLAUDE.md §Analytics; fetch/cache/auth plan in `IDRM-BUILD-WORKFLOW.md` → M6 **✅ Verify** | ⏳ Code written, reviewed & wired into `main.py`; **run on a machine with Python/conda + Postgres (+ Redis for cache) to confirm** (no Python here) |
| **Gateway G1 (Proxy)** | **Actually run** (Bun 1.3.9): launched the gateway + a stub upstream on :8000 and drove it with curl — proxy round-trip, OPTIONS preflight, non-API path, upstream-down | ✅ **PASS** — proxy→200 (upstream JSON), preflight→204, `/nope`→404, upstream-down→502; security + CORS headers on every response. (Full FastAPI round-trip still pending a Python env.) |
| **Gateway G2 (Rate limiting)** | logic review (module-level in-memory store ⇒ accumulates per process); limits/headers checked vs the Gateway Guide. Local run inconclusive (Windows authoring box: stray Bun processes + localhost quirks) | ⏳ **Verify on the Ubuntu dev laptop** — 6th login → 429, `X-RateLimit-*` headers, per-IP buckets (commands in `IDRM-BUILD-WORKFLOW.md` → G2 **✅ Verify**) |
| **Gateway G3 (JWT auth)** | **JWT crypto run locally** (Bun one-shot, no server): mint+verify with the dev secret; accept-valid + reject wrong-secret/tampered/expired/garbage; auth-mode + anti-spoof logic reviewed | ✅ crypto **5/5 PASS**; ⏳ end-to-end (token → `X-User-*` → FastAPI) **verify on Ubuntu** (commands in `IDRM-BUILD-WORKFLOW.md` → G3 **✅ Verify**) |
| **Gateway G4 (WebSocket)** | `bun build` bundle-check of the whole gateway (no server, no ports); WS subscribe-registry + `broadcast` + Bun pub/sub API reviewed | ✅ **bundles cleanly**; ⏳ live handshake + Redis→WS relay **verify on Ubuntu** (commands in `IDRM-BUILD-WORKFLOW.md` → G4 **✅ Verify**) |
| **Frontend F0 (web-html)** | code review (JS/JSDoc + HTML; not Python); config cross-checked vs `instructions_ui_v3.md` (Slate+Emerald+Inter) + the web conventions | ⏳ **Verify on Ubuntu** — `bun install && bun run dev` → styled page on :5173 + header badge “API: ok” (commands in `IDRM-BUILD-WORKFLOW.md` → F0 **✅ Verify**) |
| **Frontend F1 (public pages)** | code review (HTML + 3-line JS; not Python); confirmed no `/api` calls on public pages; `ls` confirms the e-commerce stubs are gone | ⏳ **Render-verify on Ubuntu** — landing + About on :5173, CTAs, authed-redirect, zero network calls (commands in `IDRM-BUILD-WORKFLOW.md` → F1 **✅ Verify**) |
| **Frontend F2 (auth pages)** | code review (HTML + JSDoc JS; not Python); request shapes checked vs CLAUDE.md §Auth / M2 (bare tokens, self-roles, 401/409/422 handling) | ⏳ **Verify on Ubuntu** (backend+gateway up) — register→auto-login→dashboard, login 401/200, tokens in sessionStorage (commands in `IDRM-BUILD-WORKFLOW.md` → F2 **✅ Verify**) |
| **Frontend F3 (citizen core)** | code review (HTML + JSDoc JS; not Python); built to canonical `/services` + actions; GeoJSON [lon,lat] + escapeHtml checked; M3 `?mine=true` filter added | ⏳ **Verify on Ubuntu** (full stack) — create→detail→(approve/accept/start/complete)→verify→VERIFIED; my-services `?mine=true` + filters (commands in `IDRM-BUILD-WORKFLOW.md` → F3 **✅ Verify**) |
| **Frontend F4 (live map)** | code review (HTML + JSDoc JS; not Python); geo calls + WS subscribe/relay checked vs M4/G4; GeoJSON [lon,lat]↔Leaflet [lat,lng] | ⏳ **Verify on Ubuntu** (full stack + Redis) — markers/clusters by zoom, type filter, marker→detail, and a new request appearing live (commands in `IDRM-BUILD-WORKFLOW.md` → F4 **✅ Verify**) |
| **Frontend F5 (notifications + profile)** | code review (HTML + JSDoc JS; not Python); checked vs M5/M2 (notification shape + mark-read, UserUpdate preferences merge); added `related_service_id` to `NotificationOut` | ⏳ **Verify on Ubuntu** (backend+gateway) — notification unread→mark-read→count drops + deep-link; profile edit persists (commands in `IDRM-BUILD-WORKFLOW.md` → F5 **✅ Verify**) |
| **Frontend F6 (provider pages)** | code review (HTML + JSDoc JS; not Python); accept/start/complete vs the M3 state machine; added `?provider_id` filter | ⏳ **Verify on Ubuntu** (seed a verified org) — Available→Accept→My active→Start→Complete; role-gate + nav link (commands in `IDRM-BUILD-WORKFLOW.md` → F6 **✅ Verify**) |
| **React SPA Part D (admin)** | code review (**TS → JSDoc/block comments, not Python**); built to canonical `/api/v1` (bare auth tokens, `{status,data}` lists, `POST /{id}/approve\|reject`); enum/types cross-checked vs CLAUDE.md; React Query v5 + Zustand + Recharts wiring reviewed | ⏳ **Verify on Ubuntu** — `bun install` → `bun run build` (tsc+vite) → `bun run dev` :5174; guard→login, Recharts dashboard, approve/reject clears the queue, silent refresh past 15 min (commands in `IDRM-BUILD-WORKFLOW.md` → Part D **✅ Verify**) |

> Every build module documents its own verification **inline** — see each module's **✅ Verify** block in `IDRM-BUILD-WORKFLOW.md`, plus the per-layer quick-reference in its §2 "Verifying your work".

---

## 5. The needful — pending backlog

### 5a. Build modules (see `IDRM-BUILD-WORKFLOW.md` for steps)
| Track | Modules | Status |
|-------|---------|--------|
| Backend | M0 boot ✅ · M1 models/schemas ✅ · M2 auth ✅ · M3 services+actions ✅ · M4 geo ✅ · M5 notifications ✅ · M6 analytics ✅ | **M0–M6 all built** (run + migrate + test pending) |
| Gateway | G1 proxy ✅ · G2 rate-limit ✅ · G3 JWT ✅ · G4 WebSocket ✅ | **G1–G4 all built** (live flow verify on Ubuntu) |
| web-html | F0 build setup ✅ · F1 public ✅ · F2 auth ✅ · F3 citizen core ✅ · F4 map ✅ · F5 notifications/profile ✅ · F6 provider ✅ | **F0–F6 all built** (verify on Ubuntu) |
| React SPA | Part D foundation ✅ — Login + Dashboard (Recharts) + approval queue | **built** (verify on Ubuntu); user/provider mgmt + LiveMap deferred |
| Mobile (Expo) | — | 🔒 Post-MVP |

**Recommended first milestone (vertical slice):** M1 → M4, G1/G3, F0/F2/F3/F4 → a citizen can register, create a request, and see it live on the map.

> _Auth follow-up:_ **phone + OTP quick-start** (D9) is deferred until an SMS provider is selected — register/login cover the MVP round-trip for now.
>
> _M3 follow-ups:_ (1) add the **`/start`** action (ACCEPTED→IN_PROGRESS) to **CLAUDE.md**'s service action list (it's built, but missing from the doc summary); (2) model a **user↔organisation** membership so `/accept` derives the org from the acting user instead of taking `org_id`; (3) consider DB columns for `estimated_arrival` / approve-notes / cancel & dispute reasons (currently audit-logged only).

### 5b. Still-empty placeholder files (deferred earlier)
- **CI**: `.github/workflows/{unit,integration,component,e2e}.yml`
- **Tooling**: `.pre-commit-config.yaml`, `.vscode/{settings,extensions,launch,tasks}.json`
- **Docker app images** (needed for the compose `app` profile): `src/backend/app-python/Dockerfile`, `src/backend/api-gateway/Dockerfile`, `infra/docker/nginx.conf`
- **Frontend**: remove e-commerce stubs (`cart`, `checkout`, `payment`, `product-*`) and build the IDRM pages (F-track above); `mobile-expo` stubs (Post-MVP)

### 5c. Repo hygiene
- ⚠️ **Commit everything** (docs reconciliation, audit, UI, scripts, workflow, M0, M1 + docstrings, M2 auth, M3 services, M4 geo, M5 notifications, M6 analytics, G1 gateway, G2 rate-limit, G3 JWT auth, G4 WebSocket, F0 web-html setup, F1 public pages, F2 auth pages, F3 citizen core + M3 ?mine filter, F4 live map, F5 notifications/profile, F6 provider pages, **Part D React SPA admin foundation**) — nothing is in git yet. Suggested: grouped commits on a branch.

### 5d. Optional doc cleanups (low priority)
- `instructions/instructions_pages_v3.md` still has a few stale `/services/requests` / `PUT …/status` references in body text (build to canonical regardless).
- `dsml/projects/recommendation-system/**` — separate nested project; decide keep/remove.
- Deep line-by-line read of the ~handful of docs only grep-swept in the audit, if 100% certainty is required.

---

## 6. Open questions for the product owner
- Confirm the **frontend page set** (the documented IDRM inventory) once F0 starts — and approve **deleting the e-commerce stubs**.
- Confirm **MAD / Finance** stay Post-MVP (assumed per D13).
- Decide whether to keep or remove the stray `dsml/` sub-project.

---

*Update this file whenever a module is finished or a decision changes. The per-module checkboxes live in `IDRM-BUILD-WORKFLOW.md` §Progress tracker.*
