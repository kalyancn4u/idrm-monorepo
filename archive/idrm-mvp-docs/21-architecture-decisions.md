# IDRM MVP — Architecture Decision Records (ADRs)

> *Type: Document (decision log) · Audience: developers, architects, reviewers · Status: MVP — current*
> *A lightweight ADR set recording **why** the MVP is deliberately built the way it is — especially why it is *not* (yet) using React, Redis, Docker, microservices, or biometric ML. Each record: **Decision · Context · Options · Consequences.** Most formalise choices already made and logged in [`CHANGELOG.md`](CHANGELOG.md); the "→ FFP" ones are chartered in the [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md).*

> **How ADRs work here:** an ADR is short and immutable once **Accepted**. A later reversal is a **new**
> ADR that supersedes an old one (never an edit). The FFP introduces each deferred technology via its own
> ADR naming the concrete trigger.

**Status legend:** Accepted (MVP) · every "deferred" item is *chartered*, not rejected.

---

## ADR-001 — Modular monolith (not microservices)
- **Decision:** Build IDRM as **one deployable FastAPI application** with clean internal modules
  (`users, incidents, organizations, resources, locations, alerts, notifications, reports, files, audit,
  administration`), each shaped `router → service → repository`.
- **Context:** MVP scale (2 states, 10k users) doesn't justify distributed-system complexity; a novice team
  ships faster with one codebase.
- **Options:** (a) microservices from day one; (b) **modular monolith** ✅; (c) unstructured monolith.
- **Consequences:** Simple to build/run/deploy; module boundaries + the API contract are preserved so the
  FFP can extract one service at a time **without a rewrite**. → FFP: selective microservices.

## ADR-002 — PostgreSQL + PostGIS is the single source of truth
- **Decision:** One **PostgreSQL 16 + PostGIS 3.4** database is the authoritative store for all records and
  geospatial data.
- **Context:** IDRM is map-driven (proximity, areas); one reliable store keeps data consistent.
- **Options:** (a) separate GIS server (GeoServer); (b) **PostGIS in the DB** ✅; (c) NoSQL + geo add-on.
- **Consequences:** Spatial queries live next to the data (`ST_DWithin`); no sync problems. Caches/brokers
  (Redis, Kafka) may be added later but **never** become the source of truth. → FFP: dedicated tile/GIS
  server only if map load demands it.

## ADR-003 — API-first; canonical `/api/v1` contract, stable across the SDLC
- **Decision:** The **OpenAPI contract is the product**. URIs are **incident-centric** under **`/api/v1`**,
  `snake_case`, UUIDs, with a machine-readable [`40-api-openapi.yaml`](40-api-openapi.yaml).
- **Context:** The same contract must serve the MVP HTML/JS UI **and** future React/mobile clients.
- **Options:** (a) service-request-centric `/services/requests…` (the old xlsx); (b) **incident-centric
  `/api/v1/incidents…`** ✅ (matches the authoritative `docs/` + module list).
- **Consequences:** **A URI defined in the MVP never changes in the FFP** — the FFP *adds* endpoints, never
  renames. The `idrm-api-resource-mapping.xlsx` asset is reconciled to this (queued).

## ADR-004 — HTML + Tailwind CSS v4 + JavaScript for the web UI (React deferred)
- **Decision:** The MVP web UI is **server-friendly HTML, Tailwind CSS v4, and vanilla JS** — no SPA framework.
- **Context:** Emergencies need fast, light pages on basic phones/low bandwidth; a novice team; progressive
  enhancement.
- **Options:** (a) React/Vue SPA now; (b) **HTML + Tailwind + JS** ✅.
- **Consequences:** Small, fast, accessible; consumes the same API a React client will later. → FFP: React
  SPA + React Native/Expo, same contract.

## ADR-005 — No Redis in the MVP (DB-backed sessions; caching deferred)
- **Decision:** No Redis. Refresh-token **sessions live in PostgreSQL** (`user_sessions`); rely on
  Postgres/PostGIS indexing for speed.
- **Context:** MVP load doesn't need a cache or a second datastore to operate.
- **Options:** (a) Redis for sessions/cache now; (b) **PostgreSQL only** ✅.
- **Consequences:** One less moving part. → FFP: Redis/Redis Streams for caching, sessions, and event flows
  when measured need appears.

## ADR-006 — Native systemd on Ubuntu (no Docker/Swarm/Kubernetes)
- **Decision:** Run natively under **systemd** on a standalone **Ubuntu 22.04 LTS** server (uvicorn,
  PostgreSQL, MinIO).
- **Context:** One app on one server; containers/orchestration add ops overhead the MVP doesn't need.
- **Options:** (a) Docker Compose; (b) Kubernetes; (c) **native systemd** ✅.
- **Consequences:** Simple, reproducible via [`../scripts/setup-idrm-ubuntu.sh`](../scripts/setup-idrm-ubuntu.sh).
  → FFP: Docker → Swarm/Kubernetes, CI/CD, distributed observability.

## ADR-007 — MinIO (S3-compatible) for object storage — in the MVP
- **Decision:** Uploaded photos/documents are stored in **MinIO**; PostgreSQL keeps only keys/URLs.
- **Context:** File upload is an MVP capability (incident evidence, completion proof); the DB shouldn't hold
  blobs.
- **Options:** (a) blobs in PostgreSQL; (b) local filesystem; (c) **MinIO / S3 API** ✅.
- **Consequences:** The **S3 API** carries unchanged into the FFP (distributed MinIO / cloud S3) — no
  rewrite. Private bucket + pre-signed URLs. *(Contrast: local disk would force a rewrite later.)*

## ADR-008 — RS256 JWT + RBAC (OIDC / MFA / ABAC deferred)
- **Decision:** Email+password auth; **RS256-signed JWT** access tokens + rotating refresh tokens; **RBAC**
  over 4 roles with ownership checks.
- **Context:** Need a solid, standard auth baseline that survives the move to services.
- **Options:** (a) HS256 shared-secret; (b) **RS256 asymmetric** ✅; (c) OIDC/SSO now.
- **Consequences:** FFP services verify the same tokens with the **public key**, no shared secret. → FFP:
  OIDC/SSO, MFA/OTP, ABAC policy rules.

## ADR-009 — Lean 7-state incident lifecycle (Disputed / auto-close deferred)
- **Decision:** `created → (approved if critical) → accepted → in_progress → completed → verified`, plus
  `cancelled`/`rejected` exits.
- **Context:** The v3 model had 10 states; the MVP needs the minimum that is human-verifiable.
- **Options:** (a) full 10-state incl. Disputed + auto-Close; (b) **lean 7-state** ✅.
- **Consequences:** Simpler state machine and tests; enum can grow. → FFP: `disputed`, automatic close.

## ADR-010 — Four roles (full 10-role hierarchy + Auditor deferred)
- **Decision:** `citizen · provider · coordinator · admin` (+ a narrow `guest` path).
- **Context:** The v3 spec had 8–10 tiers; the MVP's flows need only these.
- **Options:** (a) full hierarchy (Volunteer/Organizer/Manager/Executive/Event-Admin/Auditor/…); (b) **4
  roles** ✅.
- **Consequences:** Simple RBAC matrix. → FFP: the richer hierarchy + read-only Auditor role.

## ADR-011 — Face **detection** only in the MVP; **FaceNet recognition** deferred
- **Decision:** MVP uses **lightweight client-side face detection** as a photo-quality gate (nothing
  biometric stored). Identity **recognition/matching (FaceNet)** is out.
- **Context:** Biometric data of vulnerable disaster victims carries **DPDP Act 2023** consent/retention
  obligations; it's also heavier ML.
- **Options:** (a) FaceNet recognition in MVP; (b) **detection-only gate** ✅.
- **Consequences:** Useful photo quality without biometric risk. → FFP: FaceNet recognition with consent +
  safeguards (missing-person matching).

## ADR-012 — No message broker/queue in the MVP (near-real-time notifications)
- **Decision:** Notifications (SMS/email) are dispatched **inline** on state changes with a **retry** on
  failure; no broker/worker.
- **Context:** Near-real-time is acceptable for the MVP (PRD §13); a broker is infra the MVP doesn't need.
- **Options:** (a) RabbitMQ/Kafka + workers; (b) **inline dispatch + retry** ✅.
- **Consequences:** A channel outage never blocks a state change (recorded for retry). → FFP: brokers,
  background workers, deep push.

## ADR-013 — Native PostgreSQL `ENUM` types matching API wire values
- **Decision:** Domain enums (`incident_status`, `service_type`, `priority`, `user_role`, …) are native
  PostgreSQL `ENUM`s whose values **equal the API wire values**.
- **Context:** One vocabulary from DB to API to UI; the DB rejects invalid values.
- **Options:** (a) free-text + CHECK; (b) lookup tables; (c) **native ENUM** ✅.
- **Consequences:** Type-safe and consistent; FFP **adds** values via `ALTER TYPE … ADD VALUE` (never
  renames) — mirroring the API's "only grows" rule.

## ADR-014 — MVP setup script is now a pure-MVP installer (Bun stripped) — RESOLVED (2026-08-16)
- **Decision:** [`../scripts/setup-idrm-ubuntu.sh`](../scripts/setup-idrm-ubuntu.sh) **no longer installs Bun**.
  Chose **option (a)**: strip Bun so the installer provisions only the MVP stack.
- **Context:** The script previously installed **Bun** (an FFP technology) inside an MVP installer, and its
  generated README/dev scripts described a separate `bun run dev` frontend — an inconsistency with the locked
  MVP frontend (HTML + Tailwind CSS v4 + vanilla JS + Leaflet, served by FastAPI; ADR-003).
- **What changed:** removed the Bun install/verify step and PATH edits; retitled the frontend as static assets
  served by FastAPI (`frontend/templates` + `frontend/static/{css,js,img}`); fixed the generated README and
  `dev-start.sh` (one FastAPI server on :8000, no `:3000` frontend); dropped the `oven.bun-vscode` editor
  recommendation and the `Bun/Node` `.gitignore` block; renumbered the install steps (now 1–13).
- **Consequences:** The installer is internally consistent with the MVP stack. **MinIO in the same script
  remains legitimate MVP** (ADR-007). Bun/Node/Deno return only in the FFP phase (edge/BFF behind APISIX).

---

*Related:* [`20-architecture-system.md`](20-architecture-system.md) · [`40-api-specification.md`](40-api-specification.md) ·
[`50-data-model.md`](50-data-model.md) · [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) ·
[`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) ·
[FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md). Plan: [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).
