# Technology Stack 101 — the component map

> *Type: Guide (101 / synthesis-index) · Audience: everyone (developers go deepest) · Status: MVP — current (+ FFP forward-refs) · Track: Software Engineering (#40)*
> *This is a **map, not a manual**: one line of plain-language *what* + IDRM *why* for **every** tool in the
> stack, each with a deep-link to the doc/guide that explains it in full. Use it to answer "what is X, why do we
> use it, and where do I read more?" — then follow the link. Nothing here is duplicated from the deep homes.*

---

## How to read this guide

Every component is tagged by **phase**:

- 🟢 **MVP** — ships in the Minimum Viable Product **now** (the pure-Python modular monolith).
- 🔵 **FFP** — relocated to the Full-Fledged Product, added **only on a concrete trigger** (scale, ownership,
  performance, reliability). Not in the MVP, not lost.
- ⚪ **Dropped / replaced** — named in an early draft (the retired `idrm-docs-v0`) but **not** in the current
  stack; the *role* it played is filled by something else. Listed so the map is honest about what we do **not** use.

A **framework** is pre-written code that calls *your* code (you fill in the blanks); a **library** is code *you*
call; an **extension** adds capability to an existing tool; a **runtime** is the program that executes your code.

---

## 1. 🟢 MVP stack — what ships now

The MVP is **one deployable FastAPI application** (a "modular monolith"), with PostgreSQL/PostGIS as the single
source of truth, MinIO for uploaded files, and a plain HTML/Tailwind/JS/Leaflet web UI served by that same app.

### 1.1 Backend runtime & API

| Component | What it is (plain language) | Why IDRM uses it | Read in full |
|---|---|---|---|
| **Python 3.11+** | A readable, batteries-included programming language. | One language for the whole MVP → simpler to build, learn, and hire for; superb geospatial + data libraries. | [docs/mvp/20](../../idrm-mvp-docs/20-architecture-system.md) |
| **FastAPI** | A modern Python **web framework** for building HTTP APIs, with automatic validation and OpenAPI docs. | It *is* the MVP app server: fast, async, type-driven, and it generates the `/api/v1` contract docs for free. | [docs/mvp/20](../../idrm-mvp-docs/20-architecture-system.md) · [REST API 101](rest-api-101.md) |
| **Uvicorn** | The **ASGI server** — the process that actually runs a FastAPI app and speaks HTTP. | FastAPI defines the app; Uvicorn serves it (under systemd in production). | [docs/mvp/80](../../idrm-mvp-docs/80-ops-deployment-and-operations.md) |
| **Pydantic** | A library that **validates data** against typed Python models. | Every request/response body is a Pydantic schema → bad data is rejected at the door; types double as docs. | [docs/mvp/30](../../idrm-mvp-docs/30-design-data-flow-and-modules.md) |

### 1.2 Data & storage

| Component | What it is | Why IDRM uses it | Read in full |
|---|---|---|---|
| **PostgreSQL 16** | A rock-solid, open-source **relational database** (ACID-safe). | The single source of truth for every record; also holds **sessions** (so no Redis is needed in the MVP). | [PostgreSQL/PostGIS 101](postgresql-postgis-101.md) · [docs/mvp/50](../../idrm-mvp-docs/50-data-model.md) |
| **PostGIS 3.4** | An **extension** that gives Postgres geographic types + spatial queries ("what's within 5 km?"). | IDRM is map-driven; PostGIS makes proximity/geofence queries fast **inside** the database — no separate GIS server. | [PostgreSQL/PostGIS 101](postgresql-postgis-101.md) · [docs/mvp/50](../../idrm-mvp-docs/50-data-model.md) |
| **SQLAlchemy 2.0** | An **ORM** (object-relational mapper) — lets Python objects stand in for database rows. | Write queries in Python, keep the DB swappable in theory, and centralise data access in the repository layer. | [docs/mvp/20](../../idrm-mvp-docs/20-architecture-system.md) · [PostgreSQL/PostGIS 101](postgresql-postgis-101.md) |
| **GeoAlchemy2** | A SQLAlchemy add-on that teaches the ORM about PostGIS **geometry columns**. | Lets IDRM read/write map points through the same ORM, no raw SQL for the common cases. | [PostgreSQL/PostGIS 101](postgresql-postgis-101.md) · [docs/mvp/50](../../idrm-mvp-docs/50-data-model.md) |
| **Alembic** | A **database migration** tool — versioned, repeatable schema changes. | The schema evolves safely across environments; every change is a reviewable migration file. | [PostgreSQL/PostGIS 101](postgresql-postgis-101.md) · [docs/mvp/80](../../idrm-mvp-docs/80-ops-deployment-and-operations.md) |
| **MinIO** | A self-hosted, **S3-compatible object store** for files (photos, PDFs). | Uploaded evidence lives in MinIO; the DB stores only the key/URL. Same S3 API carries into the FFP unchanged. | ADR-007 in [docs/mvp/21](../../idrm-mvp-docs/21-architecture-decisions.md) · [docs/mvp/80](../../idrm-mvp-docs/80-ops-deployment-and-operations.md) |

### 1.3 Web UI (served by FastAPI — no JS build step)

| Component | What it is | Why IDRM uses it | Read in full |
|---|---|---|---|
| **HTML + vanilla JavaScript** | The page structure + browser scripting, hand-written (no React/build). | Keeps the MVP simple and dependency-light; the app server returns the pages directly. | [docs/mvp/60](../../idrm-mvp-docs/60-uidesign-web-interaction.md) |
| **Tailwind CSS v4** | A **utility-first CSS** framework (style with small class names). | Fast, consistent styling without a custom design system or a heavy build. | ADR-004 in [docs/mvp/21](../../idrm-mvp-docs/21-architecture-decisions.md) · [docs/mvp/60](../../idrm-mvp-docs/60-uidesign-web-interaction.md) |
| **Leaflet 1.9** | A lightweight **JavaScript map** library. | Renders the incident/resource map in the browser — mobile-friendly, no map-server dependency. | [GIS for Emergency Response](gis-for-emergency-response.md) · [docs/mvp/60](../../idrm-mvp-docs/60-uidesign-web-interaction.md) |

### 1.4 Security, quality & operations

| Component | What it is | Why IDRM uses it | Read in full |
|---|---|---|---|
| **python-jose (RS256 JWT)** | A library to sign/verify **JSON Web Tokens** with RSA keys. | Stateless auth: a signed access token proves who you are; refresh tokens rotate/revoke. | [docs/mvp/22](../../idrm-mvp-docs/22-architecture-security-and-iam.md) · [IAM 101](iam-101.md) |
| **passlib + bcrypt** | Password **hashing** (bcrypt, cost 12). | Passwords are never stored in plain text; bcrypt is deliberately slow to resist cracking. | [docs/mvp/22](../../idrm-mvp-docs/22-architecture-security-and-iam.md) · [Secure Coding 101](secure-coding-101.md) |
| **pytest** | Python's **testing** framework. | Unit + API + integration tests (target ≥80% coverage) prove features F1–F11 behave. | [docs/mvp/70](../../idrm-mvp-docs/70-quality-test-strategy.md) · [Testing 101](testing-101.md) · [API Testing 101](api-testing-101.md) |
| **Git** | Distributed **version control**. | Tracks every change; the basis for review and collaboration. | [Git/GitHub 101](git-github-101.md) |
| **Ubuntu + systemd** | The Linux OS + its **service manager** (starts/keeps processes running). | The MVP deploys **natively** (no Docker): systemd runs the app, Postgres, and MinIO. | [docs/mvp/80](../../idrm-mvp-docs/80-ops-deployment-and-operations.md) · [Linux 101](linux-101.md) |

---

## 2. 🔵 FFP stack — added later, only on a trigger

None of this is in the MVP. Each arrives when a concrete trigger justifies it, **without breaking the `/api/v1`
contract** (the FFP only *adds* endpoints, never renames).

| Component | What it is | Trigger / role in the FFP | Read in full |
|---|---|---|---|
| **APISIX** | An **API gateway** (front door: routing, auth, rate-limit, TLS, WAF, observability). | Chosen over NGINX/Kong for the free/OSS build; fronts the services once there is more than one. | [api-gateway spoke](../../instructions/api-gateway.md) · [docs/ffp/20](../../idrm-ffp-docs/20-architecture-system.md) |
| **Selective microservices** | Splitting one module out of the monolith into its own service. | Extract the least-coupled module first (Strangler Fig) when scale/ownership demands. | [docs/ffp/20](../../idrm-ffp-docs/20-architecture-system.md) |
| **Node / Bun / Deno** | JavaScript **runtimes** for edge/BFF/SSR/websocket services **behind** APISIX. | Real-time and edge concerns, on a per-service basis — never the gateway itself. | [backend-services spoke](../../instructions/backend-services.md) |
| **React + React Native (Expo)** | A component **web SPA** + native **mobile** apps, sharing the same APIs. | Richer web app + real mobile clients when the HTML UI is outgrown. | [docs/ffp/60](../../idrm-ffp-docs/60-uidesign-frontend.md) · [docs/ffp/61](../../idrm-ffp-docs/61-frontend-engineering-standards.md) |
| **Redis / Redis Streams** | In-memory **cache** + lightweight event stream. | Caching, rate-limit counters, and first-step async events (sessions stay in Postgres until then). | [docs/ffp/81](../../idrm-ffp-docs/81-ops-messaging-and-async.md) · [caching-messaging spoke](../../instructions/caching-messaging.md) |
| **RabbitMQ / Kafka** | Message **brokers** for durable async work + high-volume event streams. | Background jobs, fan-out, and deep real-time push at scale. | [docs/ffp/81](../../idrm-ffp-docs/81-ops-messaging-and-async.md) · [Event-Driven Architecture 101](event-driven-architecture-101.md) |
| **Docker → Kubernetes** | **Containers** (bundle app + deps) → an **orchestrator** that runs them at scale. | Reproducible deploys and horizontal scale/HA when native systemd is no longer enough. | [Docker 101](docker-101.md) · [docs/ffp/80](../../idrm-ffp-docs/80-ops-platform-and-deployment.md) |
| **Python GeoPandas / Shapely service** | A dedicated **Python geospatial** service over PostGIS. | Heavy geoprocessing as its own service — the FFP's answer to "a GIS server" (see §3: not GeoServer). | [docs/ffp/20 §6.2](../../idrm-ffp-docs/20-architecture-system.md) |
| **OIDC · MFA · ABAC** | Federated login · multi-factor auth · attribute-based access. | Enterprise identity beyond the MVP's RS256-JWT + 4-role RBAC. | [docs/ffp/22](../../idrm-ffp-docs/22-architecture-security-and-iam.md) · [OIDC 101](oidc-101.md) · [MFA 101](mfa-101.md) |
| **Prometheus · OpenTelemetry** | Metrics + **distributed tracing** across services. | Full observability once there are multiple services to correlate. | [Observability 101](observability-101.md) · [docs/ffp/80](../../idrm-ffp-docs/80-ops-platform-and-deployment.md) |

---

## 3. ⚪ Dropped / replaced — named in v0, NOT in the current stack

The retired first-draft (`archive/_removed/idrm-docs-v0`) named these. They are **not** used; their role is filled
by something else. Listed so the map has no blind spots.

| v0 component | Status | What fills its role instead |
|---|---|---|
| **GeoServer** (Java map server) | ❌ Rejected (not even FFP) | A **Python GeoPandas/Shapely** service over PostGIS — lighter to run and matches IDRM's Python skills. [docs/ffp/20 §6.2](../../idrm-ffp-docs/20-architecture-system.md) |
| **NGINX** (as gateway/WAF/LB) | ⤴ Replaced in FFP | **APISIX** is the FFP gateway. The MVP keeps at most a *simple TLS reverse proxy*. [api-gateway spoke](../../instructions/api-gateway.md) |
| **Node.js + Express** (as the API gateway) | ⤴ Re-scoped | Node/Bun/Deno become **edge/BFF services behind** APISIX — never the gateway. [backend-services spoke](../../instructions/backend-services.md) |
| **Socket.io** | 🔁 Concept only | "Real-time push" is a **capability**, delivered later via brokers, not this specific library. [docs/ffp/81](../../idrm-ffp-docs/81-ops-messaging-and-async.md) |
| **Celery** | 🔁 Concept only | "Async workers/queues" is delivered by **RabbitMQ/Kafka + workers** in the FFP. [docs/ffp/81](../../idrm-ffp-docs/81-ops-messaging-and-async.md) |
| **Passport · Helmet · Joi · Winston · Morgan** (Node libs) | ❌ Not used | Their roles map to the **Python stack**: python-jose (auth), Pydantic (validation), secure-headers middleware, structured logging. [docs/mvp/22](../../idrm-mvp-docs/22-architecture-security-and-iam.md) |
| **Pandas** (as live analytics) | 🔵 FFP / dev-only | Advanced analytics is FFP; in the MVP, Pandas is only a **local data/asset tool**, not part of the running app. |
| **MongoDB** (candidate DB) | ❌ Rejected | **PostgreSQL + PostGIS** is the single source of truth (ACID + spatial). ADR-002 in [docs/mvp/21](../../idrm-mvp-docs/21-architecture-decisions.md) |

---

## 4. The stack in one sentence

> **MVP:** a single **FastAPI/Python** app (**Pydantic** in, **SQLAlchemy/GeoAlchemy2** to **PostgreSQL 16 +
> PostGIS 3.4**, **Alembic** for schema, **MinIO** for files, **RS256 JWT** auth, **pytest** tests) serving an
> **HTML + Tailwind + Leaflet** UI, run **natively on Ubuntu with systemd**.
> **FFP** grows that — on triggers, same API contract — into **APISIX**-fronted selective **microservices**
> (polyglot, incl. **React/Expo** clients, **Redis→brokers**, **Docker→Kubernetes**, a **Python geospatial**
> service, and full **OIDC/observability**).

---

## Mastery check

You've mastered this guide when you can, for **any** tool someone names, instantly say **(a)** what it is in one
sentence, **(b)** whether it's MVP, FFP, or dropped, **(c)** the role it plays (or what replaced it), and **(d)**
which doc or guide to open for the full story — without guessing. Try it now with: *FastAPI, PostGIS, Redis,
GeoServer, APISIX.*

---

*Related:* [REST API 101](rest-api-101.md) · [PostgreSQL/PostGIS 101](postgresql-postgis-101.md) ·
[Docker 101](docker-101.md) · [Event-Driven Architecture 101](event-driven-architecture-101.md) ·
architecture [docs/mvp/20](../../idrm-mvp-docs/20-architecture-system.md) + decisions [docs/mvp/21](../../idrm-mvp-docs/21-architecture-decisions.md).
