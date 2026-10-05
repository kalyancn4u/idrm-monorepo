# Organization — Who Owns It, Where It's Going

> **Part of:** IDRM Documentation · `08-organization.md`
> **Answers:** Who does what, who owns what, how do people grow into their role, and where is IDRM headed?
> **Source posters:** Posters 31–35 (Phase 8 Organizational Knowledge)
> **Audience:** Leaders & teams (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

1. [Roles & responsibilities](#1-roles--responsibilities) — who does what, across the lifecycle.
2. [Ownership matrix](#2-ownership-matrix) — who owns each part of the system.
3. [Decision guide](#3-decision-guide) — when to use which building block.
4. [Training & mastery paths](#4-training--mastery-paths) — how each role grows from novice to master.
5. [Evolution roadmap](#5-evolution-roadmap) — where IDRM goes next.
6. [The big picture](#6-the-big-picture) — the whole ecosystem in one view.

---

## 1. Roles & responsibilities

IDRM is delivered by roles mapped to the **eight SDLC phases**. On a small team, one person may wear several
hats.

| SDLC phase | Primary roles | Key responsibilities & success outcomes |
|---|---|---|
| **1 · Inception & Planning** | Product Owner / BA, Project Manager, Solution Architect | Vision, scope, feasibility & risk, roadmap → approved PRD, project plan. |
| **2 · Requirements & Analysis** | Business Analyst, Domain Expert, System Analyst | Detailed FR/NFR, use cases, business rules, traceability → SRS sign-off, backlog. |
| **3 · Design** | Solution & System Architect, UI/UX Designer, Security Architect | Architecture, data model, API & UI/UX design, threat analysis → design doc, DB schema & API specs. |
| **4 · Development** | Software / Frontend / Backend Developers | Code to standards, unit tests, reviews, version control → working code, coverage, code quality. |
| **5 · Security** | Security Engineer, DevSecOps, Compliance Analyst | Threat modeling, secure coding, vuln scanning, access control → security report, remediation, compliance. |
| **6 · Quality Assurance** | QA / Test Manager, Test Engineer, Performance Engineer | Test strategy, unit→E2E, performance & security testing → coverage, defect closure, quality sign-off. |
| **7 · Operations** | DevOps, SRE, System Administrator | Server provisioning & hardening, CI/CD, monitoring, backup/DR → stable deployment, HA, readiness. |
| **8 · Maintenance & Evolution** | App Support Engineer, Change Manager, Data Steward | Fixes & patches, change & data mgmt, tuning, roadmap → SLA compliance, evolving product. |

**Cross-cutting roles** (active across phases): Project Manager · Configuration Manager · Documentation
Specialist / Technical Writer · Data Steward / DBA · Change Manager · Training & Adoption Lead · Compliance &
Audit Lead · Vendor / Support Manager.

**Collaboration principles:** clear communication · defined ownership (one accountable owner) · document
everything · measure & improve · security by design · quality first.

---

## 2. Ownership matrix

Every domain has one **accountable owner**, so nothing falls through the cracks — using a light **RACI**
(**R**esponsible does the work · **A**ccountable owns the outcome · **C**onsulted gives input · **I**nformed
kept up to date). One accountable owner per domain; ownership doesn't restrict collaboration.

| Domain | Accountable owner | Consulted / supporting | Key responsibilities |
|---|---|---|---|
| **APIs** | API Owner / Tech Lead | Backend Dev, Architect, Security, QA | Standards, design & review, versioning, performance, docs. |
| **Database** | Data Owner / DBA | Backend, Data Steward, Sys Admin, Security | Modeling, tuning, backup/retention, access & integrity. |
| **Security** | Security Engineer | DevSecOps, Sys Admin, Compliance, all devs | Threat modeling, IAM, secure coding, monitoring & response. |
| **Testing** | QA / Test Manager | Developers, Automation Eng., Product Owner | Test strategy, manual & automated, defects, sign-off. |
| **Documentation** | Technical Writer | Architect, Developers, API Owner, PO | Technical & user docs, runbooks, versioning, accessibility. |
| **CI/CD** | DevOps / Release Manager | Developers, QA, Sys Admin, Security | Pipelines, build/scan/package, deploy, IaC, rollback. |

Escalate conflicts to the Project Manager; update this matrix when roles or scope change.

---

## 3. Decision guide

A quick reference for *when to use which building block* — so choices stay consistent with the design.

| Need | Use | When |
|---|---|---|
| A web page for people | **FastAPI + Jinja2 + Tailwind CSS** | Anything a human views or fills in (HTML served by FastAPI; no Flask). |
| A machine-to-machine endpoint | **FastAPI + Pydantic** | Data exchange, integrations, mobile/API clients. |
| Store core / relational data | **PostgreSQL** | The default home for records. |
| Store or query locations | **PostGIS** | Anything involving maps, distance, or areas. |
| Speed up repeated reads / sessions | **PostgreSQL** (MVP) · **Redis** (FFP) | MVP keeps sessions/cache in Postgres; Redis is deferred to the FFP scale-out. |
| Store files, images, documents | **Object / file storage** | Uploads and attachments. |
| Do work without blocking the user | **threading / ThreadPoolExecutor** | Send an alert, generate a report, import data. |
| Run something on a schedule | **APScheduler** | Nightly cleanups, periodic reports. |
| Front the app on a server | **NGINX** | TLS, static files, routing (optional but recommended). |

**Technology fit at a glance** (★ 1 low – 5 high):

| Technology | Best when | Trade-offs | Perf / Simplicity / Scale |
|---|---|---|---|
| **Flask** | Simple/medium APIs, UI, flexibility | Manual setup; not for very high concurrency. *(IDRM uses FastAPI, below — Flask is not in the stack.)* | ★★★ / ★★★★ / ★★★ |
| **FastAPI** | Modern high-performance APIs, async, auto-docs | Slight learning curve; fewer extensions than Flask | ★★★★★ / ★★★★ / ★★★★ |
| **PostgreSQL** | Reliable relational + spatial (PostGIS) | Needs tuning for very high write loads | ★★★★ / ★★★ / ★★★★ |
| **Redis** | Caching, sessions, queues, rate limiting | In-memory (RAM-bound); not a primary DB. **FFP scale-out — not in the MVP.** | ★★★★★ / ★★★★ / ★★★★ |
| **Object storage** (MinIO/S3) | Files, media, backups, exports | Not for transactional data; eventual consistency | ★★★★ / ★★★★ / ★★★★★ |
| **ThreadPoolExecutor** | I/O-bound background work | Not ideal for CPU-bound (GIL) | ★★★ / ★★★★ / ★★★ |
| **APScheduler** | Scheduled / periodic jobs | Single-node; not distributed | ★★★ / ★★★★ / ★★★ |
| **APISIX** (optional) | Edge gateway: routing, auth, rate-limit, WAF | More complex; needs etcd for HA | ★★★★ / ★★★ / ★★★★ |

For richer edge features (routing, auth, and rate-limiting at the gateway), **APISIX** is an optional choice;
the MVP monolith uses **NGINX** by default. The reasoning behind these defaults is recorded for maintainers in
[`99-decisions-and-history.md`](99-decisions-and-history.md).

---

## 4. Training & mastery paths

Each role can grow along a **four-rung ladder** — from novice to master — using this documentation plus a few
external fundamentals. Read the IDRM documents listed at each rung; practise by contributing at that level.

**The four rungs (all roles):**
1. **Novice** — understand *why* and *what*: read [`00`](00-orientation.md), [`01`](01-foundation.md),
   [`02`](02-architecture.md).
2. **Practitioner** — do the core work of your role with guidance.
3. **Proficient** — work independently; make sound trade-offs.
4. **Master** — set direction, mentor others, own decisions.

### Backend Engineer
| Rung | Focus | Read / do |
|---|---|---|
| Novice | Python, HTTP, the codebase layout | `02`, `03` |
| Practitioner | Build endpoints & services; validate with Pydantic | `03`, `04`, `06` |
| Proficient | Design across modules; performance & security aware | `04`, `05`, `06` |
| Master | Own API design & standards; mentor | `99` (decisions), all |

### Frontend Engineer
| Rung | Focus | Read / do |
|---|---|---|
| Novice | HTML/CSS, Tailwind CSS, Jinja2 templates | `02` §4, `03` |
| Practitioner | Build accessible pages, wire to APIs | `03`, `01` §5 (who screens serve) |
| Proficient | Consistent UX, WCAG accessibility | `05` (safe handling), `06` |
| Master | Own the design system & accessibility bar | all |

### Database / GIS Engineer
| Rung | Focus | Read / do |
|---|---|---|
| Novice | SQL, PostgreSQL, (PostGIS for GIS) | `04` |
| Practitioner | Models, migrations, spatial queries | `04`, `03` (Repository pattern) |
| Proficient | Performance, integrity, backups | `04`, `07` |
| Master | Own the data model & geospatial strategy | `99`, all |

### Security Engineer
| Rung | Focus | Read / do |
|---|---|---|
| Novice | Web security basics (OWASP) | `05` |
| Practitioner | Apply authN/authZ, validate inputs | `05`, `03` |
| Proficient | Threat modelling, audit, monitoring | `05`, `07` |
| Master | Own the security posture & compliance | `99`, all |

### QA / Test Engineer
| Rung | Focus | Read / do |
|---|---|---|
| Novice | Testing basics, pytest | `06` |
| Practitioner | Write unit/integration/API tests | `06`, `02` (flows) |
| Proficient | E2E, performance, security testing | `06`, `05` |
| Master | Own the test strategy & quality gates | all |

### DevOps / SRE
| Rung | Focus | Read / do |
|---|---|---|
| Novice | Linux/Ubuntu, services, NGINX | `07` |
| Practitioner | Deploy, configure, run backups | `07`, `06` (CI/CD) |
| Proficient | Observability, recovery, tuning | `07`, `04` |
| Master | Own operations, DR, and scaling | `99`, all |

### Leadership / Stakeholder
| Rung | Focus | Read / do |
|---|---|---|
| Novice | The problem & the vision | `01` |
| Practitioner | Scope, outcomes, success measures | `01`, this doc |
| Proficient | Roadmap & trade-offs | §5 below, `02` |
| Master | Steer strategy & partnerships | the big picture (§6) |

Deeper, hands-on training material (tutorials, exercises) is part of the optional later pass; this ladder is
the map that organises it.

---

## 5. Evolution roadmap

IDRM is designed to **start simple and grow with confidence** — a 10-year, six-phase journey where each phase
adds capability without discarding what came before.

| Phase | Horizon | Focus |
|---|---|---|
| **1 · Foundation** | Year 0–1 | Establish the core: modules, RBAC/IAM/audit, maps & basic analytics, standard workflows, stable on-prem, docs & training. |
| **2 · Stabilization** | Year 1–2 | Strengthen & standardize: performance tuning & hardening, high availability, data quality & governance, agency integrations, mobile-responsive, monitoring/backup/DR. |
| **3 · Integration** | Year 2–3 | Connect & interoperate: API ecosystem, GIS/remote sensing, IoT & early-warning feeds, inter-agency data sharing, advanced reporting. |
| **4 · Intelligence** | Year 3–5 | Intelligent & predictive: AI/ML risk prediction, NLP, predictive alerts, decision-support dashboards. |
| **5 · Autonomy** | Year 5–7 | Automate & optimize: workflow automation & rules engine, auto-dispatch, chatbot/voice, computer vision, digital twin. |
| **6 · Resilience 2.0** | Year 7–10 | Adaptive & future-ready: self-healing, cross-border interoperability, trust technologies, community-resilience platforms. |

The through-line: the clean module boundaries in today's MVP are exactly what make each future phase low-risk —
every phase is additive.

---

## 6. The big picture

Pulling it all together — IDRM is **one integrated ecosystem** serving many stakeholders through a single,
coherent platform:

- **People:** citizens, volunteers, responders, officials, agencies, partners — each with the access they need.
- **Capabilities:** incident, resource, volunteer, GIS, communication, analytics — one shared picture.
- **Foundation:** one Python application, one reliable database with maps built in, secure and observable,
  running dependably on a single server today and ready to grow.
- **Purpose:** faster response, better decisions, stronger communities — lives and livelihoods protected.

> *An integrated ecosystem. A shared mission. A safer tomorrow.*

---

## Where this leads

- Back to the start → [`00-orientation.md`](00-orientation.md)
- Why it all matters → [`01-foundation.md`](01-foundation.md)
- The decisions behind the design (owner reference) → [`99-decisions-and-history.md`](99-decisions-and-history.md)

---

*"Prepared today. Protected tomorrow. Technology in service of humanity."*
