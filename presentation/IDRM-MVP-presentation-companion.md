# IDRM MVP — Presentation Companion & Master Narrative

**Integrated Disaster Response Management — Minimum Viable Product**
*The complete story behind the IDRM‑MVP presentations, elaborated from summary to substance.*

> **Purpose.** The slide decks (`IDRM-MVP.pptx`, `IDRM-MVP-v2.pptx`) give the headlines. This document is the
> **full narrative** behind them — enough detail to brief any audience, and enough structure to generate
> further presentations (and, one level deeper, the code) from a single source. It stops at **high‑level
> functions and abstracted API functionality**; implementation code is intentionally left to derived material.
>
> **How it was built.** Content is **collated from all MVP‑relevant posters** (Phases 0–8 vision posters and
> the MVP execution posters) and the IDRM documentation set, then **merged, de‑duplicated, validated, and
> sorted** into a coherent order. Where posters disagreed, the conflict was resolved against the confirmed MVP
> design (see [§0.3](#03-conformance--how-discrepancies-were-resolved)).

---

## 0. Front matter

### 0.1 Audience map — how to read this

| You are… | Read | Depth |
|---|---|---|
| Leader, sponsor, agency official, citizen advocate, new joiner | **Part I — General Audience** | Plain language, no code |
| Architect, engineer, data/GIS, security, QA, DevOps | **Part I** then **Part II — Technical Deep‑Dive** | Design‑level to abstracted API |
| Presentation author | Any section — each maps 1:1 to a slide/theme | As needed |

### 0.2 One‑paragraph summary

**IDRM is a people‑centric platform that helps communities and agencies prepare for, respond to, and recover
from disasters** — by unifying incidents, resources, volunteers, maps, communication, and analytics into one
shared, real‑time picture. The **MVP** is deliberately simple: a **standalone modular monolith** written in
**Python 3.12** (a Flask/Jinja2 web UI and a FastAPI API in one process, with in‑process background jobs),
backed by **PostgreSQL + PostGIS** and optional **Redis**, deployed on a single **Ubuntu** server. It is built
to **start simple and grow** — the same clean module boundaries that keep the MVP tidy make each future step
(more capability, then a larger enterprise deployment) low‑risk.

### 0.3 Conformance — how discrepancies were resolved

The posters describe two horizons. To keep this document truthful and non‑contradictory:

- **The MVP is authoritative here** — a **modular monolith**: Python 3.12, Flask + FastAPI, in‑process
  threading/APScheduler, Jinja2 + Bootstrap UI, Python + GDAL for GIS (no separate map server), on Ubuntu.
- **The broader/enterprise ("FFP") vision** shown on some Phase‑3 posters (microservices, Node/NestJS, React,
  GeoServer, Kubernetes, Kafka) is treated **only as the future direction**, surfaced in the roadmap — never as
  the MVP build.
- The **data model** (Posters 21–22) and the disaster‑domain content are architecture‑neutral and hold across
  both horizons.
- Minor reconciliations: object storage is named **MinIO** (S3‑compatible) with local/S3 alternatives; test
  **coverage ≥ 80%** with a **≥ 70% minimum gate**; **shelters** are modelled as a resource type for the MVP;
  the optional **APISIX** gateway is noted but the MVP uses **NGINX**.

### 0.4 Standards we hold ourselves to (throughout)

**WCAG 2.1 / 2.2 AA** (accessibility) · **ISO/IEC 27001** (information security) · **ISO 22301** (business
continuity) · **DPDP Act, 2023 — India** (data protection) · **OpenAPI 3.1**, **ISO/IEC/IEEE 29148/42010**,
**NIST CSF**, **OWASP Top 10 / ASVS** (engineering & security references).

---

# PART I — GENERAL AUDIENCE
### *Understanding IDRM: why it exists, whom it serves, and what it does*

---

## 1. The problem we solve

When disasters strike, failures are rarely a lack of goodwill — they are failures of **coordination and shared
information**. Today, across most response systems:

- **Siloed systems and fragmented data** delay a common understanding of the situation.
- **Slow information flow and weak coordination** hurt timely decisions.
- **Manual processes and duplicate reporting** waste effort and reduce accuracy.
- **Limited visibility of resources** makes allocation and tracking hard.
- **Weak last‑mile communication** leaves citizens under‑informed at the worst moment.
- **Little standardisation or interoperability** across tools and agencies.

**IDRM exists to close these gaps** — one shared, real‑time operating picture that every stakeholder can act on.

## 2. Vision, mission, principles & goals

**Vision.** *A disaster‑resilient world where communities, institutions, and responders act early, respond
faster, and recover stronger — saving lives and livelihoods.*

**Mission.** *To integrate people, processes, data, and technology on a unified platform that enables
collaboration, situational awareness, and informed action across the disaster‑management lifecycle.*

**Six guiding principles** (the tie‑breakers when decisions are hard):

| Principle | In practice |
|---|---|
| People‑Centric | Safety, dignity, inclusion — especially for the vulnerable. |
| Integrity & Trust | Transparency, accountability, privacy. |
| Interoperability | Connect systems and stakeholders via open standards. |
| Timeliness | Early warnings, rapid response, continuous updates. |
| Innovation | Evidence‑based decisions from data. |
| Sustainability | Strengthen long‑term resilience, not quick fixes. |

**Six strategic goals:** an **Integrated Platform**, **Situational Awareness**, **Effective Communication**,
**Community Empowerment**, **Data‑Driven Decisions**, and a **Resilient Ecosystem**.

## 3. Scope — what the MVP does (and doesn't)

A deliberate boundary keeps the MVP useful yet trustworthy.

| In scope (MVP) | Out of scope (future) |
|---|---|
| Situational awareness & dashboard | Advanced AI/ML predictions |
| Incident reporting & alerts | Complex financial management |
| Resource management | Long‑term recovery planning |
| Tasking & coordination | Custom hardware solutions |
| Communication & notifications | Deep third‑party integrations |
| Reports & analytics (basic) | |
| User & role management | |
| Mobile & web access | |
| Data security & audit | |

## 4. Stakeholder ecosystem

IDRM brings **all stakeholders** onto one platform, each with a clear role.

| Stakeholder | Role in IDRM |
|---|---|
| **Citizens & communities** | Receive alerts/guidance; report incidents; request help; access shelters/relief; give feedback. |
| **Volunteers & community groups (NGOs/CBOs)** | Support awareness/preparedness; assist in search, rescue, relief, logistics — force multipliers. |
| **Emergency services** | Police, Fire, Medical, SDRF, NDRF, Coast Guard, Home Guards — respond, provide care/evacuation, maintain readiness. |
| **District administration & EOCs** | Incident command; resource allocation & coordination; damage assessment; law & order; public communication. |
| **State agencies** | Policy, guidance, resources; state EOCs & line departments; monitor and support districts. |
| **National agencies** | NDMA, MHA, NDRF, IMD, ISRO, MoHFW, BRO, Railways — policy, strategic direction, specialised resources, oversight. |
| **External systems & partners** | Weather/early‑warning (IMD), GIS/remote‑sensing/satellite, health systems, UN agencies & private sector, media, crowd sources. |

**Cross‑cutting enablers for all:** Trusted Access · Communication · **Common Operating Picture** (a shared,
real‑time situational view) · Data & Interoperability · Mobility · Analytics & Insights · Security & Privacy.

## 5. User personas & responsibilities

Design targets real people with real jobs:

- **Citizen (web/mobile)** — reports needs, tracks status, receives alerts. *Needs: simplicity, language support.*
- **Volunteer** — registers availability & skills, responds to tasks/missions, shares updates. *Force multiplier.*
- **Emergency responder** — acts on alerts, executes response (search/rescue/medical), shares real‑time status.
- **Coordinator / District administrator** — monitors incidents & resources, allocates, issues directives,
  communicates with the public.
- **Administrator** — manages users, roles, configuration, and audit oversight.
- **Government official** — views dashboards and reports for decisions and accountability.

*(Oversight roles — state/national agencies, NGOs, media, partners — chiefly consume dashboards and reports.)*

## 6. Business domains

IDRM's work divides into six domains (which become the platform's modules):

| Domain | What it covers |
|---|---|
| Incident Management | Reporting, classification, status tracking, escalation, timeline. |
| Resource Management | Inventory, fleet, equipment, shelters, availability. |
| Volunteer Management | Registration, skills, assignments, attendance. |
| GIS & Mapping | Live map, layers, geofencing, search, routing. |
| Communication | Alerts & notifications across email, SMS, in‑app. |
| Analytics | Operational reports, KPIs, dashboards, insights. |

## 7. The disaster lifecycle

IDRM supports the **whole** lifecycle — not just the emergency — which is what separates it from a simple
ticketing tool.

**Preparedness → Mitigation → Response → Recovery → Resilience**

| Phase | IDRM helps with |
|---|---|
| Preparedness | Planning, training, SOPs, awareness. |
| Mitigation | Reducing risk before events; hazard awareness. |
| Response | Incident handling, field ops, resource mobilisation, communication. |
| Recovery | Restoring services, tracking relief, reporting. |
| Resilience | Learning from each event to prepare better for the next. |

## 8. End‑to‑end business workflow

Information, people, and resources flow through nine steps — from early warning to continuous improvement:

**Monitor & Early Warning → Assess & Activate → Incident Management → Resource Management → Communication &
Collaboration → Operational Response → Recovery & Restoration → Evaluation & Learnings → Continuous Improvement**

Each step has a clear **output** (e.g., *Activation → Incident Plan → Deployed Resources → Informed
Stakeholders → Response Updates → Restored Communities → Lessons Learned → Improved Preparedness*). A parallel
**information flow** — sensors/feeds → ingestion → validation → situational awareness (dashboard & GIS) →
decision support → actionable alerts → field teams → feedback — keeps everyone working from the same picture.

## 9. How we deliver it — the SDLC roadmap

IDRM is delivered responsibly, value first, through seven stages:

| Stage | What happens | Output |
|---|---|---|
| 1 · Idea | Problem discovery, stakeholder inputs, feasibility, value proposition | Problem statement & concept note |
| 2 · PRD & Architecture | Requirements & use cases, FR/NFR, system architecture, data/integration design | PRD, architecture & design specs |
| 3 · Development | Iterative development, code standards, security by design, version control | Working software (builds) |
| 4 · Testing | Test planning, functional, performance, security, UAT | Test reports & quality sign‑off |
| 5 · Deployment | Deployment planning, CI/CD automation, data migration, go‑live & rollback | Live system (production) |
| 6 · Operations | Monitoring & alerts, incident management, backup & recovery, support, SLA | Stable, available, supported system |
| 7 · Continuous Improvement | Feedback & analytics, post‑incident review, tuning, roadmap evolution | Improved outcomes & innovation |

**Cross‑cutting principles at every stage:** Security & Privacy · User‑Centricity · Interoperability · Data
Quality · Compliance · Accessibility · Sustainability.

## 10. Success metrics & KPIs

Success is measured by better **response**, not merely working software:

| Area | Example measures |
|---|---|
| Adoption & Reach | Active users; registered organisations; geographic coverage. |
| Response Effectiveness | Alert delivery time; response‑time reduction; incident resolution rate. |
| Operational Performance | System uptime; data accuracy; workflow completion rate. |
| Stakeholder Satisfaction | Satisfaction score; training completion. |
| Impact | Lives saved; people assisted; resource‑utilisation efficiency. |
| Compliance & Trust | Policy compliance; data‑privacy adherence; audit readiness. |

## 11. The big picture

IDRM is **one integrated ecosystem**: the right **people** (citizens, volunteers, responders, officials,
agencies, partners) using shared **capabilities** (incident, resource, volunteer, GIS, communication,
analytics) on a common **foundation** (one Python application, one reliable database with maps built in,
secure and observable) — for one **purpose**: faster response, better decisions, stronger communities.

## 12. Evolution roadmap — the next ten years

Start simple; grow with confidence. Each phase is **additive**.

| Phase | Horizon | Focus |
|---|---|---|
| 1 · Foundation | Yr 0–1 | Core modules, RBAC/IAM/audit, maps & basic analytics, standard workflows, stable on‑prem, docs & training. |
| 2 · Stabilization | Yr 1–2 | Performance & hardening, high availability, data governance, agency integrations, mobile‑responsive, monitoring/backup/DR. |
| 3 · Integration | Yr 2–3 | API ecosystem, GIS/remote sensing, IoT & early‑warning feeds, inter‑agency data sharing, advanced reporting. |
| 4 · Intelligence | Yr 3–5 | AI/ML risk prediction, NLP, predictive alerts, decision‑support dashboards. |
| 5 · Autonomy | Yr 5–7 | Workflow automation & rules engine, auto‑dispatch, chatbot/voice, computer vision, digital twin. |
| 6 · Resilience 2.0 | Yr 7–10 | Self‑healing, cross‑border interoperability, trust technologies, community‑resilience platforms. |

---

# PART II — TECHNICAL DEEP‑DIVE
### *Building & running IDRM: architecture through abstracted API*

---

## 13. Architecture overview — a modular monolith

IDRM is **one Python 3.12 application** containing all features as clean internal **modules**, running as a
**single process**, deployed as a **single unit**.

- **Flask + Jinja2 + Bootstrap 5** serve the **web interface** (server‑rendered pages).
- **FastAPI + Pydantic** serve the **REST API** (validated, with OpenAPI/Swagger docs).
- **In‑process background work** (alerts, emails, imports, scheduled reports) runs via Python **threading /
  ThreadPoolExecutor** and **APScheduler** — no external broker or worker fleet.

Three bands describe the system end‑to‑end:

```
ENTRY POINTS   Web browser (Flask UI) · REST APIs (FastAPI) · Admin/Ops · Mobile/PWA (future) · Third‑party
      │        systems (weather/IMD, ISRO, maps)
      ▼
APPLICATION    One Python 3.12 process: Web UI (Flask/Jinja2) · APIs (FastAPI) · Background jobs
CORE           (threading · APScheduler) · Business modules · Cross‑cutting (security · logging · config)
      │
      ▼
DATA &         PostgreSQL + PostGIS (primary) · Redis (cache/sessions, optional) · Object/file storage
STORAGE
```

**Why this shape?** For a disaster platform, *reliability and simplicity beat distributed complexity*: one
codebase, one deployment, one debugging model; module boundaries kept clean so features can be split out later
only if scale demands it.

## 14. Architecture evolution

The architecture matures through four stages, each answering one question:

| Stage | Question | Focus |
|---|---|---|
| Prototype | *Can it work?* | Learning, validation, feedback. |
| **MVP (today)** | *Does it solve the problem?* | Core features, usability, early adoption — a modular monolith. |
| Production Monolith | *Can it run reliably at scale?* | Stability, performance, ops excellence (optimised DB, caching, HA, backup/DR). |
| Enterprise FFP | *Can it evolve endlessly?* | Scalability, flexibility, interoperability (distributed, cloud‑native) — future only. |

## 15. Layered architecture (eight layers)

Responsibilities are stacked; each layer has one job and talks mainly to its neighbours, wrapped by security
at every level.

| # | Layer | Responsibility |
|---|---|---|
| 1 | User & Interaction | Multi‑channel access (web/mobile/API), self‑service, role‑based views, notifications, public info. |
| 2 | Core Functional | The disaster capabilities: preparedness, early warning, response, monitoring. |
| 3 | Business Services | Domain services: identity, incident, resource, volunteer, GIS, workflow, communication, reporting. |
| 4 | Platform Services | Shared enablers: routing, auth, config, notifications, workflow engine, storage, search, caching, audit. |
| 5 | Data & Integration | Data stores (PostgreSQL, PostGIS, Redis, object storage) and external‑system integration. |
| 6 | Intelligence & Decision Support | Trends & KPIs, risk/impact, resource optimisation, basic insights, dashboards. |
| 7 | Infrastructure & Operations | Scheduling, background jobs, logging, metrics, health checks, alerts. |
| 8 | Security, Governance & Compliance | Security by design, identity & data governance, audit, privacy, compliance. |

## 16. Functional overview

Mapped to the lifecycle, the core capabilities are: **Preparedness** (risk assessment, planning, SOPs) ·
**Early Warning** (threat detection, alerts) · **Response** (incident management, field ops, mobilisation) ·
**Resource Management** (assets, allocation, tracking) · **Volunteer Management** (onboarding, deployment) ·
**Situational Monitoring** (dashboards, maps, KPIs).

## 17. Modules & component overview

The business modules are vertical feature areas that cooperate through **direct internal calls**, a **shared
database**, and **in‑app events/jobs** — no network hops.

| Module | Responsibility |
|---|---|
| Authentication & Authorization | Login, sessions/JWT, roles & permissions (RBAC). |
| Incident Management | Create, classify, track, escalate incidents; timeline. |
| Resource Management | Inventory, fleet, equipment, shelters, deployments. |
| Volunteer / Responder | Registration, skills, assignments, availability. |
| GIS & Mapping | Maps, layers, geocoding, geofencing, routing. |
| Notification / Alerts | Email, SMS, in‑app alerts, templates. |
| Reports & Analytics | Operational reports, KPIs, dashboards, exports. |
| Document / Media | Uploads, attachments, documents, metadata. |
| Audit & Activity | Immutable logs of who did what, when. |

Two **platform‑level services** support every module: an **Administration Service** (system settings, master
data, monitoring) and **Integration Services** (adapters/connectors to external systems). Interactions follow
four **flow types**: **synchronous** request/response, **asynchronous** events, **data** flow, and **control**
flow.

**Worked example — a new incident:** *Incident* creates the record → *GIS* places it on the map →
*Notifications* alerts nearby responders → *Resource* and *Volunteer* supply people/assets → *Audit* records
each step → *Analytics* rolls it into dashboards. All within one application.

## 18. How a request flows (data · packet · pipeline)

**Request → response pipeline** (every request passes the same disciplined path):

```
Request received → Routing & method check → Middleware (CORS, GZip, auth context, logging)
→ Authentication (session/JWT) → Authorization (RBAC) → Validation (Pydantic)
→ Controller/endpoint → Business module → Data access (SQLAlchemy) → PostgreSQL/PostGIS/Redis
→ Response (serialize, headers, compress, status) → client
```

**Background‑job flow:** task submitted → task queue → worker thread (ThreadPoolExecutor) → execute business
logic → update status / notify → complete (or retry). Recurring work is triggered by **APScheduler**.

**Packet path:** client → network/edge (DNS, TLS, firewall, rate limit) → NGINX (optional) → IDRM app (Flask
UI · FastAPI) → data stores → response.

**Value flow (end‑to‑end):** Detect/Sense → Assess/Alert → Decide/Plan → Act/Execute → Monitor/Track →
Evaluate/Learn → Improve/Prepare.

## 19. Repository structure

One repository, one clear layout; each business module has a slice across `models`/`schemas`/`services`/`apis`/`routes`.

```
idrm_mvp/
├── app/
│   ├── __init__.py        # application factory
│   ├── config/            # settings per environment
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # business logic per module
│   ├── apis/              # FastAPI routers (REST endpoints)
│   ├── routes/            # Flask views (server‑rendered pages)
│   ├── templates/         # Jinja2 + Bootstrap 5
│   ├── static/            # CSS, JS, images
│   ├── tasks/             # background jobs (threading / APScheduler)
│   └── utils/             # shared helpers (security, email, …)
├── migrations/            # Alembic migrations
├── tests/                 # unit / integration
├── scripts/               # setup & utilities
├── run.py                 # entry point
├── requirements.txt       # dependencies
├── environment.yml        # Miniconda env (incl. GIS/GDAL)
└── .env.example
```

## 20. Coding standards — principles across the full stack

Principles exist so any developer can read, trust, and safely change the code.

| Principle | Meaning |
|---|---|
| SOLID | Five guidelines that keep modules focused, loosely coupled, extensible. |
| DRY | Say a thing once; reuse it. |
| KISS | Prefer the simplest solution that works. |
| YAGNI | Build what's needed now, not imagined futures. |
| Clean Code | Clear names, small functions, readable structure. |

**Applied per layer** (the "elucidate for each layer" view):

| Layer | SOLID | DRY | KISS | YAGNI | Clean Code |
|---|---|---|---|---|---|
| Frontend | Component, single responsibility | Reusable UI components | Simple interfaces | Only what's needed | Readable components |
| API/Services | Separation of concerns, clear contracts | Shared services | Simple endpoints | Only required APIs | Consistent naming |
| Data | Repository pattern | Reuse queries/models | Simple queries | Avoid premature complexity | Readable models |
| Core/Domain | Encapsulate domain logic | Reuse domain services | Keep rules clear | Only needed features | Well‑named classes |
| Infrastructure | Dependency inversion | Reusable adapters | Simple integrations | Only required services | Clean configuration |
| Testing | Isolated units | Reusable test utilities | Focused tests | Critical paths first | Readable tests |
| DevOps | Separation in pipelines | Reusable configs | Simple deploys | Automate what's needed | Clear scripts/docs |
| Documentation | Accurate, modular | Single source of truth | Clear, concise | Document what matters | Easy to navigate |

## 21. Design patterns

| Pattern | When to use | What it gives IDRM |
|---|---|---|
| Repository | Multiple data sources / complex queries | Clean boundary between logic and the database. |
| Factory | Object creation varies | Consistent object creation (e.g. app factory). |
| Strategy | Multiple algorithms/behaviours | Swappable behaviours (email vs SMS) without `if/else` sprawl. |
| Adapter | Third‑party / legacy integration | Uniform interface to weather/map services. |
| Observer | Events notify many components | "Incident created" → notifications, loosely coupled. |
| Dependency Injection | Loose coupling & testability | Pass in dependencies; testable, flexible. |
| Facade | Complex subsystem, simple caller | A simple front door over complexity. |

**By layer:** Presentation → Strategy/Observer/Facade · API/App → DI/Facade/Strategy/Factory · Domain →
Repository/Strategy/Observer · Data → Repository/Factory/Adapter · Infrastructure → Adapter/Factory/DI ·
Integration → Adapter/Facade/Observer.

## 22. Technology stack — and why each exists

| Job | Technology | Why |
|---|---|---|
| Language & runtime | **Python 3.12** | One language for logic, web, APIs, jobs. |
| Environment/deps | **Miniconda** (mamba/micromamba/uv acceptable) | Reproducible env incl. native GIS/GDAL, lighter than full Anaconda; Docker for specialised setups later. |
| Web UI | **Flask + Jinja2 + Bootstrap 5** | Server‑rendered, accessible, fast. |
| APIs | **FastAPI + Pydantic** (+ OpenAPI/Swagger) | Validated, well‑documented REST. |
| Background work | **threading / ThreadPoolExecutor + APScheduler** | In‑process jobs & scheduling — no extra servers. |
| ORM & migrations | **SQLAlchemy + Alembic** | Objects over SQL; versioned schema. |
| Database | **PostgreSQL + PostGIS** | Reliable data with maps built in. |
| Cache/sessions | **Redis** (optional) | Speed for repeated reads and sessions. |
| Geospatial | **GDAL (via Python)** | Read/write/transform geodata without a map server. |
| Serving | **Gunicorn (Flask) · Uvicorn (FastAPI) · NGINX (optional)** | Production serving, TLS, static files. |
| Quality | **pytest, pytest‑cov, Ruff, Black, isort, mypy** | Tests, coverage, lint, format, types. |

### 22.1 Decision guide — technology fit (★ 1 low – 5 high)

| Technology | Best when | Trade‑offs | Perf / Simplicity / Scale |
|---|---|---|---|
| Flask | Simple/medium APIs, UI, flexibility | Manual setup; not very high concurrency | ★★★ / ★★★★ / ★★★ |
| FastAPI | Modern high‑performance APIs, async, auto‑docs | Slight learning curve | ★★★★★ / ★★★★ / ★★★★ |
| PostgreSQL | Reliable relational + spatial | Tuning for very high write | ★★★★ / ★★★ / ★★★★ |
| Redis | Caching, sessions, queues | In‑memory; not a primary DB | ★★★★★ / ★★★★ / ★★★★ |
| Object storage (MinIO/S3) | Files, media, backups | Not transactional | ★★★★ / ★★★★ / ★★★★★ |
| ThreadPoolExecutor | I/O‑bound background work | Not for CPU‑bound (GIL) | ★★★ / ★★★★ / ★★★ |
| APScheduler | Scheduled jobs | Single‑node | ★★★ / ★★★★ / ★★★ |
| APISIX (optional) | Edge gateway: routing, auth, rate‑limit | More complex; needs etcd for HA | ★★★★ / ★★★ / ★★★★ |

## 23. Database architecture

A pragmatic, **polyglot‑but‑simple** data layer:

| Store | Role |
|---|---|
| **PostgreSQL** | System of record — all core records. |
| **PostGIS** | Spatial types, indexing (GiST), proximity & location queries. |
| **Redis** | High‑speed cache, sessions, rate‑limit counters (optional). |
| **Object storage (MinIO/S3)** | Documents, media, maps/layers, backups/exports. |

**Data‑flow guarantees:** write/ingest → process/store (PostgreSQL consistency; PostGIS spatial; Redis fast
reads) → read/access → analyze/act, with a feedback loop that improves data quality.

## 24. Entity‑relationship model (the 18 MVP tables)

Authoritative for the MVP database. **Conventions:** UUID primary keys (`<entity>_id`); `created_at` /
`updated_at`; enums via `CHECK`; PostGIS geometry for spatial columns; files in object storage; audit rows
immutable.

| Group | Tables |
|---|---|
| **Access & Administration** | `users`, `roles`, `organizations`, `locations` |
| **Incident Management** | `incidents`, `incident_types`, `incident_updates`, `alerts` |
| **Response Management** | `responders`, `resources`, `resource_types`, `deployments`, `tasks` |
| **Data & Content** | `documents`, `media`, `geospatial_data` |
| **Communication & Audit** | `communication_logs`, `audit_logs` |

**Key relationships:** Organizations 1—N Users · Locations 1—N Organizations · Incidents N—1 Locations ·
Incidents 1—N Updates/Alerts/Tasks/Deployments/Documents/Media/CommLogs/AuditLogs · Resources N—N Incidents
(via **Deployments**) · Users 1—N AuditLogs. *(Shelters are modelled as `resource_type = SHELTER` for the MVP.)*

**Selected fields** (illustrative):
- `incidents`: incident_id, incident_number, title, incident_type_id, severity_level, status, location_id,
  reported_by, occurred_at, description, created_at. *Status lifecycle:* Reported → Verified → In‑Progress →
  Resolved → Closed (forward‑only; plus Rejected/Cancelled/Expired).
- `resources`: resource_id, name, resource_type_id, quantity, unit, owner_org_id, status, location_id.
- `audit_logs`: audit_log_id, user_id, action, entity_name, entity_id, old_values (JSONB), new_values (JSONB),
  created_at.

## 25. GIS architecture

Location is first‑class — handled with **Python + GDAL + PostGIS**, no separate map server for the MVP.

- **CRS:** WGS‑84 / **EPSG:4326** (UTM/projected as needed).
- **Spatial data types:** points, lines, polygons; layers such as Locations, Boundaries, Hazard Zones, Assets
  (points), Routes (lines), Areas (polygons).
- **Indexing:** GiST for fast "within X km", bounding‑box, and viewport queries; cast to `geography` for
  metre‑based distance (`ST_DWithin`, `ST_Distance`).
- **Presentation:** **Leaflet** interactive maps; dashboards; reporting/map‑sharing.
- **Typical features:** live incident mapping, nearest available resources/volunteers, geofencing alerts,
  heatmaps, routing.

## 26. Security architecture

**Built in, not bolted on**, across four layers and by clear principles.

| Layer | Covers |
|---|---|
| Application security | RBAC, authorization, input validation, OWASP Top 10. |
| Data security | Encryption, data masking, secure storage. |
| Infrastructure security | Network protection, TLS, hardening. |
| Operational security | Monitoring, logging, audit, incident response. |

**Principles:** Zero Trust · Defense in Depth · Least Privilege · Secure by Default · Visibility &
Accountability. **The security workflow (every request):** authenticate (OIDC/MFA) → issue token (JWT) →
authorize (RBAC) → secure resource access → encrypted data handling → audit & monitoring. **Controls:**
HTTPS/TLS, JWT/session security, RBAC (extensible to ABAC), input validation, CSRF/XSS/SQL‑injection
protection, rate limiting, file‑upload validation, security headers, immutable audit trails. **Compliance:**
ISO/IEC 27001, NIST CSF, OWASP Top 10 & ASVS, DPDP Act 2023.

## 27. Threat model

Structured with **OWASP + STRIDE**, clear assets, trust boundaries, threat actors, and a risk rating.

- **Assets:** user identities & credentials · incident/operational data · geospatial data & maps · systems &
  applications · APIs & integrations · infrastructure & networks · audit logs & backups.
- **Trust boundaries:** Untrusted (internet/public) → DMZ (web app/gateway) → Trusted (internal services &
  data); external systems (OIDC, SMS/email, maps/weather) sit outside. Each boundary authenticates, validates,
  rate‑limits; all traffic TLS 1.2+.
- **STRIDE:** Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege.
- **Threat actors:** opportunistic · malicious insiders · organised criminals · nation‑state/APTs ·
  third‑party compromise · insider mistakes.

**OWASP Top 10 (2021) → IDRM relevance → mitigations:**

| Risk | Relevance | Mitigation |
|---|---|---|
| A01 Broken Access Control | Unauthorized access to incidents/resources/admin | RBAC, least privilege, policy enforcement |
| A02 Cryptographic Failures | Weak encryption, hard‑coded secrets | TLS 1.2+, encryption at rest, secrets mgmt |
| A03 Injection | SQL/command injection via APIs/inputs | Input validation, parameterized queries, ORM |
| A04 Insecure Design | Missing threat modeling | Secure SDLC, threat modeling, reviews |
| A05 Security Misconfiguration | Open ports, default creds | Hardening, config mgmt, patching |
| A06 Vulnerable Components | Outdated libraries | Dependency scanning, timely updates |
| A07 Identification & Auth Failures | Weak auth, credential stuffing | OIDC, MFA, rate limiting, lockout |
| A08 Software & Data Integrity | Unsigned updates, tampered data | Code signing, checksums, integrity controls |
| A09 Security Logging Failures | Insufficient logging | Central logs, alerts, retention |
| A10 SSRF | SSRF via internal URLs/metadata | Egress filtering, URL validation |

**Risk rating:** each risk scored by **likelihood × impact** (Low/Medium/High/Critical); mitigations
prioritised Critical/High first. **Practice:** identify assets & flows → boundaries → threats → assess →
mitigate → validate by testing → review after changes.

## 28. Testing strategy

The **testing pyramid** balances coverage and feedback speed — many fast tests at the base, few broad at the top,
on a reliable **test‑data foundation**.

| Level | Share | Checks |
|---|---|---|
| End‑to‑End | ~5% | Whole user workflows. |
| API | ~20% | Endpoint behaviour, contracts, error handling. |
| Integration | ~15% | Modules + database together. |
| Unit | ~60% | Functions, models, utilities. |

Plus **Database, Performance, Security, Contract, and UAT** testing. **Approach:** understand requirements →
plan → design → execute → report; **shift left** and run in CI/CD. **Tools:** pytest/pytest‑cov, Ruff/Black/
isort/mypy, Postman/Newman & HTTP clients, Playwright/Cypress, k6/Locust, OWASP ZAP/Snyk. **Gates:** lint/type
pass, tests green, **coverage ≥ 80% (≥ 70% minimum)**, no high/critical vulnerabilities.

## 29. CI/CD pipeline

Every change flows through one automated pipeline:

**Commit → Lint & Format → Type Check → Test (unit/API/integration) → Coverage → Package → Deploy**
(staging → production), on **GitHub Actions**. Fail‑fast: any stage failure stops the change.

**Release readiness (all must pass):** linting/format · tests · coverage threshold · no high/critical vulns ·
build & package · smoke/health checks · approval. **Health metrics (DORA):** deployment frequency, lead time
for changes, change‑failure rate, MTTR, coverage, vulnerability count.

## 30. Deployment — standalone Ubuntu server

The MVP runs on **one Ubuntu server** (enterprise/academic campus, on‑prem), native under systemd.

- **Server:** Ubuntu 22.04 LTS (64‑bit), ~4 vCPU / 16 GB RAM / 500 GB SSD, static private IP, hostname e.g.
  `idrm-server.campus.local`.
- **Edge & app:** NGINX (reverse proxy, TLS, static) → Gunicorn (Flask UI) + Uvicorn (FastAPI) + in‑process
  jobs; PostgreSQL/PostGIS, Redis, object storage; systemd auto‑restart.
- **Ports (UFW):** 22 (SSH, admin only), 80 (→ HTTPS), 443 (HTTPS); all others blocked.
- **Data paths:** `/var/lib/postgresql`, `/data` (object storage), `/var/log/idrm`, `/etc/idrm`, `/backups/idrm`.
- **Hardening:** SSH key‑based, Fail2Ban, UFW, Let's Encrypt (auto‑renew), secrets in `.env`, regular patching.
- *(Docker Compose is an equally valid packaging option and the expected path as the deployment grows.)*

## 31. Observability

End‑to‑end visibility across four signals:

| Signal | Tells you | Tooling |
|---|---|---|
| Logs | What happened (structured JSON + correlation IDs) | Filebeat → Loki/Elasticsearch; Kibana/Grafana |
| Metrics | How it performs | Prometheus (+ exporters); Grafana |
| Traces | Where it's slow | OpenTelemetry → Tempo; Grafana |
| Alerts | What needs attention | Alertmanager → email/SMS/webhook |

**SLO/SLA targets:** availability ≥ 99.5% · API p95 < 800 ms · error rate < 1% · incident ack < 5 min · P1
resolution < 1 hr. **Retention:** logs 7–14 d (hot) / 30–90 d (warm); metrics 15–30 d raw / 1–2 y downsampled;
traces 7–14 d; alerts 90 d. **Alerting playbook** (e.g., High CPU > 85%/5m → investigate; Disk < 15% →
critical; Service down → restart/failover) with **on‑call escalation** (engineer → secondary → manager) and
**health checks** (app `/health`, DB, disk/inodes, SSL expiry, dependencies).

## 32. Disaster recovery

Resilience is non‑negotiable for a disaster platform.

- **Backup plan:** database (full + WAL, daily + continuous, 30 d, local + off‑site); app code/configs (daily,
  30 d); user uploads (daily, 30 d); system/OS (weekly, 12 wk); logs (daily, 30 d).
- **RPO/RTO targets:** web app & database RPO 1 hr / RTO 2 hr (High); file storage 4 hr / 4 hr (Medium); logs
  24 hr / 24 hr (Low).
- **DR runbook:** Detect → Assess → Decide failover → Recover → Validate → Communicate → Review.
- **Practices/tools:** 3‑2‑1 rule (3 copies, 2 media, 1 off‑site); encrypt & test restores; quarterly restore,
  semi‑annual failover drills; `pg_dump`/`pg_basebackup`, `borgbackup`/`restic`, `rsync`, `cron`.

## 33. High‑level / abstracted API functionality

The MVP exposes a single **REST API** (FastAPI) under **`/api/v1`**, JWT bearer auth, RBAC, JSON, Pydantic
validation, OpenAPI 3.1 contract (live at `/docs`/`/redoc`). Conventions: pagination (`page`/`size`),
filtering, sorting (`sort`/`-sort`), spatial params (`bbox`, `near`+`radius_km`), a consistent error envelope
with `request_id`, GZip, rate limiting, standard status codes.

**Abstracted function catalog** (what each resource group *does* — implementation left to derived material):

| Resource group | Abstracted functions |
|---|---|
| **Auth** | Authenticate & obtain token; refresh token; sign out. |
| **Users & Roles** | Manage accounts (create/list/read/update, activate/deactivate); self‑profile; read roles (RBAC). |
| **Organizations** | Register/verify organisations; hierarchy (parent org); list/read/update. |
| **Locations** | Manage locations & boundaries (geometry); hierarchy (parent location). |
| **Incidents** | Report an incident; list/filter (status, severity, type, area/bbox); read; update status through its lifecycle; close/cancel. |
| **Incident updates** | Add & list timeline updates for an incident. |
| **Alerts** | Raise an alert for an incident; list; deliver across channels (email/SMS/push/in‑app). |
| **Responders** | Register responder profiles (skills, availability); list/update. |
| **Resources & types** | Register resources (type, quantity, owner, location); list/filter by status; read reference types. |
| **Deployments** | Deploy a resource to an incident; mark returned; list per incident. |
| **Tasks** | Create tasks for an incident; assign; update status/priority; list/filter. |
| **Documents & media** | Register uploaded documents/media (object‑storage reference); list; read; delete. |
| **Map / geospatial** | Retrieve map layers/features, filtered by layer type and bounding box; nearby/radius queries. |
| **Communication logs** | Record and list communications (channel, direction, status). |
| **Audit logs** | List/filter the immutable action trail (admin, read‑only). |
| **Reports & analytics** | Read operational dashboards/reports (counts, status, response times). |

**Design rules (all endpoints):** validate input (Pydantic) → enforce RBAC → do the work in the module's
service → persist via the Repository/ORM → audit state changes → return the standard response/error envelope;
hand slow/asynchronous work to the background‑jobs component.

## 34. Roles & responsibilities (by SDLC)

| Phase | Primary roles | Success outcomes |
|---|---|---|
| 1 Inception & Planning | Product Owner/BA, PM, Solution Architect | Approved PRD, project plan. |
| 2 Requirements & Analysis | BA, Domain Expert, System Analyst | SRS sign‑off, backlog, traceability. |
| 3 Design | Solution/System Architect, UI/UX, Security Architect | Architecture doc, DB schema & API specs. |
| 4 Development | Software/Frontend/Backend Developers | Working code, coverage, code quality. |
| 5 Security | Security Engineer, DevSecOps, Compliance | Security report, remediation, compliance. |
| 6 Quality Assurance | QA/Test Manager, Test/Performance Engineer | Coverage, defect closure, quality sign‑off. |
| 7 Operations | DevOps, SRE, System Admin | Stable deployment, HA, readiness. |
| 8 Maintenance & Evolution | App Support, Change Manager, Data Steward | SLA compliance, evolving product. |

**Cross‑cutting roles:** PM · Configuration Manager · Technical Writer · Data Steward/DBA · Change Manager ·
Training & Adoption Lead · Compliance & Audit Lead · Vendor/Support Manager.

## 35. Ownership matrix (RACI)

One **accountable owner** per domain (**R**esponsible does the work · **A**ccountable owns the outcome ·
**C**onsulted · **I**nformed):

| Domain | Accountable owner | Consulted / supporting | Key responsibilities |
|---|---|---|---|
| APIs | API Lead | Backend, Architect, Security, QA | Standards, design/review, versioning, performance, docs. |
| Database | DBA | Backend, Data Steward, Sys Admin, Security | Modeling, tuning, backup/retention, access & integrity. |
| Security | Security Engineer | DevSecOps, Sys Admin, Compliance, devs | Threat modeling, IAM, secure coding, monitoring/response. |
| Testing | QA/Test Manager | Developers, Automation, Product | Strategy, manual & automated, defects, sign‑off. |
| Documentation | Technical Writer | Architect, Developers, API Owner, PO | Technical & user docs, runbooks, versioning, accessibility. |
| CI/CD | DevOps/Release Manager | Developers, QA, Sys Admin, Security | Pipelines, build/scan/package, deploy, IaC, rollback. |

---

# APPENDICES

## A. Poster → section map (MVP‑relevant, in order)

| Poster(s) | Topic | This document |
|---|---|---|
| 1 | Vision, Mission & Objectives | §2 |
| 2 | Problem & PRD | §1, §3 |
| 3 | Stakeholder Ecosystem | §4 |
| 4 | SDLC Roadmap | §9 |
| 5 | Business Domains | §6 |
| 6 | Disaster Lifecycle | §7 |
| 7, 16 | Business Workflow | §8 |
| 8 | Personas & Responsibilities | §5 |
| 9 | Architecture Evolution | §14 |
| 10, MVP‑04 | Layered Architecture | §15 |
| 11, MVP‑02 | Functional Overview | §16 |
| 12, 13 | Component / Module Interaction | §17 |
| 14, 15, MVP‑05 | Data / Packet / Request Flow | §18 |
| MVP‑01/03 | System Architecture | §13 |
| 17 | Repository Structure | §19 |
| 18 | Coding Standards | §20 |
| 19 | Design Patterns | §21 |
| 20 | Technology Stack | §22 |
| 21 | Database Architecture | §23 |
| 22 | Entity Relationship | §24 |
| 23 | GIS Architecture | §25 |
| 24 | Security Architecture | §26 |
| 25 | Threat Model | §27 |
| 26 | Testing Pyramid | §28 |
| 27 | CI/CD Pipeline | §29 |
| 28 | Deployment (Ubuntu) | §30 |
| 29 | Observability | §31 |
| 30 | Disaster Recovery | §32 |
| 31 | Roles & Responsibilities | §34 |
| 32 | Ownership Matrix | §35 |
| 33 | Decision Matrix | §22.1 |
| 34 | Evolution Roadmap | §12 |
| 35 | Big Picture | §11 |

## B. How to derive other presentations from this document

- **Executive deck** → Part I (§1–§12), 12–15 slides.
- **Technical deck** → Part II (§13–§35), one slide per section.
- **Deep‑dive/code walkthrough** → expand §19–§25 and §33 with the developer deep‑dive docs
  (`docs/deep-dive/`: SRS, architecture & design, `openapi.yaml`, data model, traceability, ops runbook).
- **Role‑specific brief** → pick the sections in that role's reading path (see `docs/00-orientation.md`).

## C. Related artifacts

- **Reader docs:** `docs/00`–`08`, glossary `docs/90-glossary.md`.
- **Developer deep‑dive:** `docs/deep-dive/` (SRS `10`, architecture & design `11`, API spec `12` +
  `openapi.yaml`, data model `13`, traceability `14`, ops runbook `15`).
- **User guides:** `docs/user-guides/`.
- **Decisions & conformance:** `docs/99-decisions-and-history.md`; review backlog `docs/98-review-and-improvements.md`.
- **Slides:** `presentation/IDRM-MVP.pptx` (navy+green) and `presentation/IDRM-MVP-v2.pptx` (Indian‑flag theme).

---

*Prepared as the single, complete narrative source for the IDRM‑MVP presentations — general audience and
technical deep‑dive — reconciled to the MVP posters, forward‑looking, and ready to generate further material.*
