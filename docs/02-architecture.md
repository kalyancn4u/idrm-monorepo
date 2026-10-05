# Architecture — What IDRM Is

> **Part of:** IDRM Documentation · `02-architecture.md`
> **Answers:** What is IDRM, technically — how does the whole thing fit together?
> **Source posters:** Posters 9–16 (Phase 2 Architecture) and execution posters MVP-01…07
> **Audience:** Architects & developers (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

This explains *what* IDRM is, from the big idea down to how a single request travels through it:

1. [The big idea](#1-the-big-idea-a-modular-monolith) — one application, many tidy modules.
2. [High-level architecture](#2-high-level-architecture) — entry points → core → data.
3. [The eight layers](#3-the-eight-layers) — how responsibilities are stacked.
4. [What it does](#4-what-it-does--functional-overview) — the functional view.
5. [Modules & how they interact](#5-modules--how-they-interact).
6. [How a request flows](#6-how-a-request-flows) — request/response, background jobs, packet path.
7. [Cross-cutting qualities](#7-cross-cutting-qualities) — the "-ilities".
8. [Evolution path](#8-evolution-path) — how IDRM grows over time.

---

## 1. The big idea: a modular monolith

IDRM is **one Python application** that contains all its features, organised into clean internal **modules**
with clear boundaries. It runs as a **single process** and is deployed as a **single unit**.

- The **web interface** is **HTML + Tailwind CSS + vanilla JavaScript** (with **Leaflet** maps), served by the
  same FastAPI app — no separate web framework.
- **FastAPI** serves the **APIs** (REST, validated with Pydantic, documented via OpenAPI/Swagger).
- **Background work** (alerts, emails, imports, scheduled reports) runs **in-process** using Python
  threading / `ThreadPoolExecutor` and **APScheduler**.

Everything shares one codebase, one database connection, and one deployment — which makes IDRM simple to run,
easy to debug, and inexpensive to operate. The modules are kept cleanly separated so the platform stays tidy
as it grows.

> **Why this shape?** The rationale is recorded for maintainers in
> [`99-decisions-and-history.md`](99-decisions-and-history.md).

---

## 2. High-level architecture

At the highest level, IDRM has three bands: who/what talks to it, the application core, and where data lives.

```
        ┌──────────────────────────────────────────────────────────────┐
        │  ENTRY POINTS                                                 │
        │  Web browser (HTML/JS UI) · REST APIs (FastAPI) · Admin/Ops   │
        │  Mobile / PWA (future) · Third-party systems (IMD, ISRO, …)   │
        └───────────────────────────────┬──────────────────────────────┘
                                        │
        ┌───────────────────────────────▼──────────────────────────────┐
        │  APPLICATION CORE  (one Python 3.12 process)                  │
        │                                                               │
        │  Web UI (HTML/Tailwind/JS)   ·   APIs (FastAPI/Pydantic)      │
        │  Background jobs (threading · ThreadPoolExecutor · APScheduler)│
        │                                                               │
        │  Business modules:  Auth · Incident · Resource · Volunteer ·  │
        │     GIS & Mapping · Notifications · Reports & Analytics ·      │
        │     File Management · Audit & Activity                        │
        │                                                               │
        │  Cross-cutting:  logging · error handling · configuration ·   │
        │     security · audit                                          │
        └───────────────────────────────┬──────────────────────────────┘
                                        │
        ┌───────────────────────────────▼──────────────────────────────┐
        │  DATA & STORAGE                                               │
        │  PostgreSQL + PostGIS (primary)  ·  MinIO (object storage)    │
        │  File / object storage (local or S3-compatible)              │
        └──────────────────────────────────────────────────────────────┘
```

- **Entry points** are the ways people and systems reach IDRM.
- The **application core** holds all the logic, organised into modules.
- **Data & storage** is where everything is kept — with PostGIS giving the database native map/location power.

---

## 3. The eight layers

Inside the core, responsibilities are organised into eight layers. Each layer has one job and talks mainly to
the layers next to it — which keeps the system easy to reason about.

| # | Layer | What it does |
|---|---|---|
| 1 | **User & Interaction** | Multi-channel access (web, mobile, APIs), self-service, role-based views, notifications, public info. |
| 2 | **Core Functional** | The disaster-response capabilities themselves — preparedness, early warning, response, monitoring. |
| 3 | **Business Services** | Domain services: identity, incident, resource, volunteer, GIS, workflow, communication, reporting. |
| 4 | **Platform Services** | Shared enablers: API gateway/routing, authentication, authorization, configuration, notifications, workflow engine, storage, search, caching, audit. |
| 5 | **Data & Integration** | Data stores (PostgreSQL, PostGIS, MinIO object storage) and integration with external systems. |
| 6 | **Intelligence & Decision Support** | Trends & KPIs, risk assessment, resource optimisation, basic insights, dashboards. |
| 7 | **Infrastructure & Operations** | Scheduling, background jobs, logging, metrics, health checks, alerts. |
| 8 | **Security, Governance & Compliance** | Security by design, identity governance, data governance, audit trails, privacy, compliance. |

Read top-to-bottom, it's the path from *a person using IDRM* down to *the data and the server it runs on*,
wrapped by *security* at every level.

---

## 4. What it does — functional overview

Mapped to the disaster lifecycle (see [`01-foundation.md`](01-foundation.md)), the core capabilities are:

| Capability | In practice |
|---|---|
| **Preparedness** | Risk assessment, planning, training, SOPs, awareness. |
| **Early Warning** | Threat detection, alerts, dissemination, notifications. |
| **Response** | Incident management, field operations, resource mobilisation, communication. |
| **Resource Management** | Assets, inventory, supplies, allocation, tracking. |
| **Volunteer Management** | Onboarding, skills, deployment, scheduling, tracking. |
| **Situational Monitoring** | Dashboards, maps, live feeds, KPIs. |

---

## 5. Modules & how they interact

The business modules are the vertical feature areas. They live in one process and cooperate through **direct
internal calls**, a **shared database**, and **in-app events/background jobs** — no network hops between them.

| Module | Responsibility |
|---|---|
| **Authentication & Authorization** | Login, sessions/JWT, roles & permissions (RBAC). |
| **Incident Management** | Create, classify, track, escalate incidents. |
| **Resource Management** | Inventory, fleet, equipment, shelters, availability. |
| **Volunteer Management** | Registration, skills, assignments, attendance. |
| **GIS & Mapping** | Maps, layers, geocoding, geofencing, routing. |
| **Notifications** | Email, SMS, in-app alerts, templates. |
| **Reports & Analytics** | Operational reports, KPIs, dashboards, exports. |
| **File Management** | Uploads, attachments, documents, metadata. |
| **Audit & Activity** | Immutable logs of who did what, when. |

**Example interaction —** a new incident: *Incident* creates the record → *GIS* places it on the map →
*Notifications* alerts nearby responders → *Resource* and *Volunteer* supply people and assets → *Audit*
records every step → *Analytics* rolls it into dashboards. All within one application.

Two **platform-level services** support every module: an **Administration Service** (system settings, master
data, monitoring) and **Integration Services** (adapters/connectors to external systems). Interactions follow
four **flow types** — **synchronous** request/response, **asynchronous** events, **data** flow, and
**control** flow.

---

## 6. How a request flows

### 6.1 Request → response (a page or an API call)

```
Request received
   → Routing & method check
   → Middleware (CORS, GZip, auth context, logging)
   → Authentication (session / JWT)
   → Authorization (RBAC)
   → Validation (Pydantic / schemas)
   → Controller / endpoint handler
   → Business module (the actual work)
   → Data access (SQLAlchemy) → PostgreSQL / PostGIS  (+ MinIO for files)
   → Response (serialize, headers, compress, status code) → sent to client
```

Every request passes the same disciplined pipeline, so security and validation are never skipped.

### 6.2 Background job flow (work that shouldn't block the user)

```
Task submitted (from an API/UI action or a schedule)
   → Task queue
   → Worker thread (ThreadPoolExecutor)
   → Execute business logic
   → Update status / send notification
   → Complete  (or retry on failure)
```

Recurring work (e.g. nightly reports, cleanups) is triggered by **APScheduler** on a schedule.

### 6.3 Packet path (how traffic reaches the app)

```
Client (browser / mobile / API client)
   → Network & edge (DNS, TLS/SSL, firewall, rate limiting)
   → NGINX (optional reverse proxy)
   → IDRM application  (FastAPI: HTML/Tailwind/JS web UI + REST APIs)
   → Data stores
   → Response back to the client
```

---

## 7. Cross-cutting qualities

These qualities apply across every layer — they're designed in, not bolted on:

**High availability · Reliability · Performance · Security · Maintainability · Modularity · Extensibility ·
Testability.**

They connect directly to the non-functional goals in [`01-foundation.md`](01-foundation.md) and are verified
in [`06-quality.md`](06-quality.md).

---

## 8. Evolution path

IDRM is built to **start simple and grow with confidence**. The same clean module boundaries that keep the
MVP tidy are what make each future step low-risk:

```
Prototype  →  MVP  →  Production Monolith  →  Enterprise FFP
```

Each stage answers a question and has its own focus:

| Stage | The question | Focus |
|---|---|---|
| **Prototype** | *Can it work?* | Learning, validation, user feedback. |
| **MVP** (today) | *Does it solve the problem?* | Core features, usability, early adoption — a modular monolith. |
| **Production Monolith** | *Can it run reliably at scale?* | Stability, performance, operational excellence (optimised DB, caching, HA, backup/DR). |
| **Enterprise FFP** | *Can it evolve endlessly?* | Scalability, flexibility, interoperability (distributed, cloud-native — when needed). |

Each step is **additive**: new capability and scale are introduced without rewriting what came before. The
long-term vision — the enterprise-grade "full-fledged" deployment — is covered in
[`08-organization.md`](08-organization.md).

---

## Where this leads

- How it's built and where the code lives → [`03-engineering.md`](03-engineering.md)
- The data and maps behind it → [`04-data.md`](04-data.md)
- How it's kept safe → [`05-security.md`](05-security.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"One platform. One view. One mission: saving lives."*
