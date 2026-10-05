# IDRM — Pending Items & Ubuntu Bring-Up Handoff

> **What this file is:** a single, self-contained checklist of everything still to do, written so a **fresh session
> on another system (a Ubuntu server)** can pick the work up without re-reading the whole history. Read this first,
> then the live status board [`archive/instructions.txt`](archive/instructions.txt) §15 (the authoritative source)
> and the builder's guide [`docs/mvp/27-implementation-roadmap.md`](docs/mvp/27-implementation-roadmap.md).
>
> *Last refreshed: 2026-08-22. This file is a convenience mirror — if it ever disagrees with `instructions.txt`
> §15, trust §15.*

---

## 0. Status in one glance

- ✅ **Documentation** — complete: MVP + FFP specs, the 40 "101" guides + 12 role guides, module elucidation (25),
  the signed-off conformance PICS (26), and the full **Implementation Roadmap (27)** §0–§15 + deep-dives
  (31 concurrency, 32 logging, 33 design system).
- ✅ **Data-foundation gate (§3.6)** — signed off 2026-08-17 (data model, schema+enums, indexes/views, seed spec,
  five user journeys).
- 🟢 **MVP code (Task G)** — **all 10 modules written** (USR · INC · ORG/RES · LOC · ALR/NTF · AUD · FIL · RPT ·
  ADM), 6 migrations, `ruff` + `py_compile` clean, but **unrun** on this Windows/docs-only box. The one blocking
  item is **the run** on Ubuntu/CI (`make migrate && seed && qa`), which flips the `PICS-*` rows to ✅. See §2.
- ✅ **Follow-ups** — seed data + doc 34, the six Task-M white papers, and the FIL face-detection gate: all done (§3).
- ⏳ **Still open** — the run (§2) + the external poster update (§3). *(The 2026-08-22 coherence audit's
  follow-ups — F5-B `/incidents` filters and F3 pagination helper — were both implemented that day.)*
- 🗄️ **`archive/idrm-mvp-code/`** — a **frozen one-time snapshot** of `services/monolith/` (not a living mirror; `services/monolith/`
  stays the sole source). Committed 2026-08-22; `local == origin/main`.
- 📖 **Code walk-through (2026-08-23)** — `docs/walkthrough/` (README + 12 chapters + GLOSSARY + Marp/Pages
  tooling) is **done, committed, and LIVE** at https://kalyancn4u.github.io/idrm-artifacts/ (Pages enabled).

---

## 1. ⭐ Ubuntu bring-up checklist (do this first on the new server)

The MVP runs **natively on Ubuntu** (no Docker). To stand up and run the code:

1. **Install the stack** — run the idempotent installer
   [`archive/scripts/setup-idrm-ubuntu.sh`](archive/scripts/setup-idrm-ubuntu.sh). It installs **PostgreSQL 16 +
   PostGIS 3.4**, **MinIO** (S3-compatible object storage), and a **Miniconda** env `idrm-mvp` (Python 3.11).
2. **Change the placeholder credentials** the script ships (DB + MinIO) — *mandatory before any non-local use.*
3. **Create the RS256 JWT keypair** (auth signing keys) at the paths in `.env`, e.g.:
   ```bash
   sudo mkdir -p /etc/idrm
   sudo openssl genpkey -algorithm RSA -out /etc/idrm/jwt_private.pem -pkeyopt rsa_keygen_bits:2048
   sudo openssl rsa -pubout -in /etc/idrm/jwt_private.pem -out /etc/idrm/jwt_public.pem
   ```
4. **Configure the app** — `cp services/monolith/.env.example services/monolith/.env` and fill in real values (DB URL, S3 keys, key paths).
5. **Build & run** (from `services/monolith/`):
   ```bash
   make setup      # conda env + dependencies
   make install    # (or: pip install -e ".[dev]")
   make migrate    # apply the schema (Alembic)
   make seed       # load sample data (implemented as modules land)
   make run        # http://127.0.0.1:8000  (API docs at /docs)
   ```
6. **Prove quality** — `make qa` (format, lint, mypy, tests, coverage ≥ 80 %). *(Not yet run end-to-end — it needs
   the dependencies + a live PostgreSQL/PostGIS + MinIO, which is exactly this Ubuntu box.)*
7. **Production** — put the app behind a reverse proxy (TLS on 443) as a **systemd** service; see
   [`docs/mvp/80-ops-deployment-and-operations.md`](docs/mvp/80-ops-deployment-and-operations.md).

---

## 2. The MVP code build (Task G) — where it stands & what's next

Driven by the roadmap [`§13`](docs/mvp/27-implementation-roadmap.md) and the signed-off PICS
[`docs/mvp/26-conformance-pics.md`](docs/mvp/26-conformance-pics.md). Build **one module at a time**; flip a
`PICS-<MOD>-*` row to ✅ **only** when its code **and** a passing test exist.

- [x] **Increment 1 — repository scaffold** (`services/monolith/`): app/core, infrastructure/database, `main.py` (health +
  request-id middleware + 10 module routers), Makefile, CI, alembic (async), tests (health smoke), frontend
  design tokens, seed stub. `py_compile` OK.
- [~] **Increment 2 — Users/Auth (USR)** — **code + tests DONE** (models + migration 0001; schemas; repository;
  service with RS256/bcrypt-12/5-fail-15-min-lockout/token flows; `/auth/*` + `/users/*` router with HTTPBearer +
  RBAC; **per-endpoint rate-limiting**; unit + **DB-backed API + integration tests**; `conftest` test infra with an
  ephemeral RS256 keypair). **`ruff` clean; all files `py_compile`.** **ONLY REMAINING:** run `make qa` on a
  DB-enabled box (CI/Ubuntu) and, once green, flip `PICS-USR-*` to ✅. *(Cannot execute on this Windows box — no
  deps/PostgreSQL. This is the FIRST thing to do on the Ubuntu server per §1.)*
- [~] **Increment 3 — Incidents (INC)** — **code + tests DONE** (lifecycle state machine; models + migration 0002
  with PostGIS point + GiST/GIN indexes; create incl. **guest**; role-scoped list/mine; **`/nearby`** proximity;
  the 8 transitions with **single-claim**, critical-needs-approval, illegal-jump 409, citizen ownership; unit +
  DB-backed API + integration tests incl. the full created→verified walk). **`ruff` clean; all 69 files
  `py_compile`.** REMAINING: run `make qa` (CI/Ubuntu) then flip `PICS-INC-*` to ✅. **Deferred to ORG:** FK +
  server-side org resolution in `accept`, org-membership on start/complete, `/incidents/assigned` — **all now
  DONE in Increment 4 below.**
- [~] **Increment 4 — Organizations & Resources (ORG/RES)** — **code + tests DONE.** organizations + resources in
  one module (`app/modules/resources/`; two routers `/organizations` + `/resources`); models + migration 0003
  (`org_type` enum, both tables, GiST/GIN indexes, and the deferred `incidents→organizations` FK); org
  registration (one-per-provider), coordinator verification gate, capacity/availability, resource CRUD, RBAC,
  spatial/type filters. **Wired the 5 deferred INC↔ORG links:** FK; `accept` resolves the provider's own verified
  org server-side (no org id in the body); org-membership check on start/complete (403 `not_assigned`);
  `GET /incidents/assigned`; stricter 5/min guest create limit. Unit + API + integration tests added; incident
  walk tests updated. **`ruff check app tests` clean; all files `py_compile`.** REMAINING: run `make qa`
  (CI/Ubuntu) then flip `PICS-ORG-*`/`PICS-RES-*` to ✅.
- [~] **Increment 5 — Locations/geo (LOC)** — **code + tests DONE.** No table of its own (reads incidents +
  organizations geometry; no migration). Pure DB-free core (`locations/geo.py`: haversine distance, offline
  reverse-geocode gazetteer, GeoJSON builders) + PostGIS `ST_DWithin` repository. Four endpoints: `GET /nearby`
  (provider/coordinator), `POST /distance`, `GET /reverse-geocode`, `GET /map/{layer}` (role-scoped GeoJSON).
  Unit tests **executed here and pass** (core is dependency-free); API + integration tests added. **`ruff check
  app tests` clean; all files `py_compile`.** REMAINING: run `make qa` (CI/Ubuntu) then flip `PICS-LOC-*` to ✅.
  *Design note: reverse-geocode is an offline stub (no third-party call) by MVP choice — a real geocoder is a
  later enhancement.*
- [~] **Increment 6 — Alerts + Notifications (ALR/NTF)** — **code + tests DONE.** Alerts: `Alert` model +
  `alert_severity` enum, PostGIS MultiPolygon area (NULL = platform-wide); `POST /alerts` (coordinator/admin),
  `GET /alerts` with **area filtering by lat/lng** (`ST_Contains` + platform-wide). Notifications: models +
  `notification_type` enum; list/unread-count/read/read-all/preferences/delete, user-scoped. **PICS-NTF-001
  wired** — incidents router notifies the requester on every state change (skips guests + self-actions).
  Migration 0004. Unit-ish via API + integration tests. **`ruff check app tests` clean; all files
  `py_compile`.** REMAINING: run `make qa` (CI/Ubuntu) then flip `PICS-ALR-*`/`PICS-NTF-*` to ✅.
- [~] **Increment 7 — Audit (AUD, cross-cutting)** — **code + tests DONE.** Append-only `audit_logs`
  (migration 0005; no update/delete path — PICS-AUD-002); `GET /audit-logs` (coordinator/admin, filterable —
  PICS-AUD-003); `AuditService.record` wired into incident transitions, org verification, and alert creation
  (PICS-AUD-001); client-IP captured via a new `client_ip_ctx` contextvar in the request middleware. API +
  integration tests. **`ruff check app tests` clean; all files `py_compile`.** REMAINING: run `make qa`
  (CI/Ubuntu) then flip `PICS-AUD-*` to ✅.
- [~] **Increment 8 — Files (FIL, cross-cutting: MinIO uploads)** — **code + tests DONE.** Metadata-only `files`
  table (migration 0006; key/URL not blob — PICS-FIL-001); `ObjectStorage` protocol + boto3 `S3Storage` (fake
  injectable in tests); **Pillow** pipeline (EXIF/GPS strip, downscale ≤1920, min 640×480, blur check —
  PICS-FIL-002/003); **face-detection gate = client-side JS** (`frontend/static/js/face-quality.js`, ADR-011 —
  on-device, advisory, nothing biometric stored; server `passes_face_quality_gate` = intentional no-op; design note
  `docs/whitepapers/face-quality-gate.md`. PICS-FIL-005 stays Planned pending a manual browser check);
  `POST /files` (type/size gates, lite path PICS-FIL-004) + `GET /files/{id}` (role-scoped). Added `pillow` dep
  + media settings. Unit (Pillow, CI-runnable) + API tests. **`ruff check app tests` clean; all files
  `py_compile`.** REMAINING: run `make qa` (CI/Ubuntu) then flip `PICS-FIL-*` (except FIL-005 seam) to ✅.
- [~] **Increment 9 — Reports (RPT)** — **code + tests DONE.** No table (aggregates incidents + timeline, orgs,
  audit; no migration). Read-only coordinator/admin. `GET /reports/dashboard` (by status/type/priority/region +
  org counts — PICS-RPT-001), `/response-times` (time-to-accept + resolve, avg/median), `/fulfillment`
  (resolution + verification rates, audit-cross-checked — PICS-RPT-002), `/{name}/export?format=csv`
  (PICS-RPT-003; non-csv 422, unknown 404). Unit + API + integration tests. **`ruff check app tests` clean; all
  files `py_compile`.** REMAINING: run `make qa` (CI/Ubuntu) then flip `PICS-RPT-*` to ✅.
- [~] **Increment 10 — Administration (ADM)** — **code + tests DONE. All 10 modules now built.** `GET
  /administration/reference-data` (staff; enums + incident state machine — PICS-ADM-001) + `GET
  /administration/overview` (admin; users by role/status + pending orgs). User/role admin stays in USR (DRY) and
  its `PATCH /users/{id}` is now **audited** (`user.admin_update`). **Task-L FAQ chatbot stub** shipped as
  `POST /notifications/chat` (fixed reply; `PICS-NTF-004` added to doc 26 + archive). API + integration tests.
  **`ruff check app tests` clean; all files `py_compile`.** REMAINING: run `make qa` (CI/Ubuntu) then flip
  `PICS-ADM-*`/`PICS-NTF-004` to ✅.
- [ ] **Per module (Task N):** its own UT + functional + API tests with default fixtures/profiles.
- [ ] **Throughout (Task K):** a Python docstring on every apt function/method/module.

## 3. Other pending items

- [x] **Task L — FAQ chatbot stub** — **DONE (2026-08-17, Increment 10).** `POST /notifications/chat` returns the
  fixed *"Your input is noted, we'll try to get back to you shortly, if possible."* (no ML). `PICS-NTF-004` added to
  doc 26 (both copies). Real NLP = FFP — see Task M white paper (1).
- [x] **Task M — six technical white papers** — **DONE (2026-08-17).** All six written in `docs/whitepapers/`
  (standalone hub + shared 8-part template; classical-first with a DL upgrade path; full depth with diagram +
  worked example each): (1) FAQ chatbot, (2) AD engine #1 (adaptive rate-limiting/prioritization/smart lists),
  (3) AD engine #2 (credibility), (4) recommender #1 (financial/charity), (5) recommender #2 (incident-notification
  routing), (6) churn detection. Engines themselves remain → FFP. Grounded in the `archive/analyses/notebooks/`
  reference notebooks (FAQ chatbot + Zee recommenders). Links 0-broken.
- [x] **`docs/mvp/34-seed-data-and-fixtures.md` + `services/monolith/scripts/seed.py`** — **DONE (2026-08-17).** The full
  row-by-row seed dataset (roadmap §3.4) is written out, and the idempotent seed script is implemented (8 users +
  guest, 3 orgs + 4 resources, incidents in all 8 states + timelines, alerts/notifications/files/audit). Loaded by
  `make seed` after `make migrate`. `ruff` + `py_compile` clean; unrun here.
- [ ] **EXTERNAL — update the authoritative posters** for the ADR-012 stack change (HTML+Tailwind+JS+Leaflet, no
  Redis, +MinIO). `posters/` is empty in this repo, so this happens wherever the master posters live.
- [x] **F5-B — DONE 2026-08-22.** Implemented the `GET /incidents` `priority`, `q` (PostgreSQL full-text over
  the description, using the existing GIN index), and whitelisted `sort` filters + tests; fixed the contract's
  `q` wording. code = contract = schema now agree. `ruff`/`compile` clean; unrun here. See the CHANGELOGs.
- [x] **F3 — DONE 2026-08-22.** Extracted the `{data, pagination}` envelope into `app/core/pagination.py`
  (`paginate` + `total_pages`), routed all 8 list endpoints through it. Pure unit test executed here and
  passes; `ruff`/`compile` clean. See `services/monolith/CHANGELOG.md`.

## 4. Housekeeping when picking up on the new box

- Run the roadmap's **verification pass** ([`archive/instructions.txt`](archive/instructions.txt) §15): link
  integrity across live docs + base↔archive parity + the PICS sign-off stamps. Expected: ~5 known-accepted broken
  links inside `archive/analyses/v3-30-*` only; everything else 0-broken, parity OK.
- Keep the two copies in sync (base `docs/mvp` ↔ `archive/idrm-mvp-docs`) and both CHANGELOGs current (rule C3/C6).

---

## 5. Maintenance of *this* file (auto-save & cleanup) — DECIDED 2026-08-17

Confirmed with the user:

- **Refresh (implicit, no automation):** the assistant refreshes this file **routinely** — as each build increment
  is finished or paused — and notifies the user. No hook / no `settings.json` change; "implicit" by habit, with
  smart curation of which items are actually pending. *(Chosen over a mechanical hook, which cannot judge the
  item list.)*
- **Cleanup (archive, never silent):** when **all** pending items are resolved, the assistant will **propose**
  moving this file into [`archive/_removed/`](archive/_removed/) (preserving history), **notify the user with
  options, and wait for confirmation** before doing anything. Removal/relocation never happens silently.
