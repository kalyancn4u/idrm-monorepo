# Glossary

> **Part of:** IDRM Documentation · `90-glossary.md`
> **Answers:** What do all these terms and acronyms mean?
> **Source posters:** all
> **Audience:** Everyone · **Depth:** Overview
> **Status:** Draft

---

Plain-language definitions of the terms used across IDRM documentation. Grouped for easy scanning.

## The project

| Term | Meaning |
|---|---|
| **IDRM** | Integrated Disaster Response Management — this platform. |
| **MVP** | Minimum Viable Product — the first complete, useful version we build now. |
| **FFP** | Full-Fledged / Production deployment — the larger enterprise version IDRM can grow into later. |
| **SDLC** | Software Development Life Cycle — the stages from idea → requirements → design → build → test → deploy → operate → improve. |
| **Stakeholder** | Anyone with an interest in IDRM: citizens, responders, officials, agencies, partners. |
| **Persona** | A representative type of user (e.g. "Field Officer") used to design for real needs. |

## Architecture shape

| Term | Meaning |
|---|---|
| **Monolith** | One application that contains all the features, deployed as a single unit. |
| **Modular monolith** | A monolith organised into clean internal **modules** with clear boundaries — simple to run, but tidy inside and ready to split up later. IDRM's chosen shape. |
| **Microservices** | The opposite approach: many small separate services. IDRM does **not** use this for the MVP (it's a possible future step). |
| **Layer** | A horizontal slice of the system with one responsibility (e.g. the data layer, the security layer). |
| **Module** | A vertical feature area (e.g. Incident Management, Volunteer Management). |
| **Cross-cutting** | Concerns that apply everywhere — logging, error handling, security, configuration. |

## Core technologies (per posters)

| Term | Meaning |
|---|---|
| **Python 3.12** | The single programming language IDRM is written in. |
| **FastAPI** | The single Python web framework — serves both the **web pages** (HTML UI) and the **REST APIs**. (Replaces Flask, which the MVP does not use.) |
| **Jinja2** | Templating engine (used via FastAPI) — fills HTML pages with live data on the server. |
| **Tailwind CSS** | Utility-first styling toolkit for the HTML pages — consistent, responsive, mobile-friendly. (Replaces Bootstrap.) |
| **Vanilla JS** | Plain browser JavaScript for light interactivity (no React in the MVP). |
| **FastAPI** | Python framework that serves the **APIs** (machine-to-machine endpoints). |
| **Pydantic** | Validates incoming/outgoing API data so it's always the right shape. |
| **OpenAPI / Swagger** | An automatically generated, interactive catalogue of the APIs. |
| **Threading / ThreadPoolExecutor** | Python's built-in way to run background work (e.g. sending alerts) without extra servers. |
| **APScheduler** | Runs scheduled/recurring jobs (like a built-in cron) inside the app. |
| **SQLAlchemy** | The **ORM** — lets Python talk to the database using objects instead of raw SQL. |
| **ORM** | Object-Relational Mapper — the translator between program code and database tables. |
| **Alembic** | Applies versioned changes to the database structure (migrations). |
| **Gunicorn / Uvicorn** | The servers that run the FastAPI app in production — Gunicorn manages Uvicorn (ASGI) workers. |

## Data & maps

| Term | Meaning |
|---|---|
| **PostgreSQL** | The main database that stores IDRM's data. |
| **PostGIS** | An add-on to PostgreSQL for **geospatial** data — locations, shapes, distances. |
| **Redis** | A fast in-memory store for caching/sessions. **Not used in the MVP** (sessions live in PostgreSQL); deferred to the FFP scale-out. |
| **MinIO** | S3-compatible object storage for uploaded files/images (on-prem); the database keeps only keys/URLs. |
| **Object / File storage** | Where uploaded files, documents, and images are kept (local disk or S3-compatible). |
| **GIS** | Geographic Information System — the mapping and location features. |
| **GDAL** | A geospatial data library IDRM uses (via Python/Conda) instead of a separate map server. |
| **Conda** | An environment manager used specifically for the GIS/GDAL toolchain. |
| **Leaflet** | The JavaScript library that draws interactive maps in the browser. |
| **ERD** | Entity-Relationship Diagram — a picture of the data tables and how they connect. |

## Security

| Term | Meaning |
|---|---|
| **Authentication (AuthN)** | Proving *who you are* (login). |
| **Authorization (AuthZ)** | Deciding *what you're allowed to do*. |
| **JWT** | JSON Web Token — a signed digital pass that proves a logged-in session. |
| **OIDC** | OpenID Connect — a standard way to sign in, often via an identity provider. |
| **RBAC** | Role-Based Access Control — permissions based on your role (citizen, admin, …). |
| **ABAC** | Attribute-Based Access Control — finer permissions based on attributes/context. |
| **Encryption** | Scrambling data so only authorised parties can read it (in transit and at rest). |
| **Audit trail** | A tamper-evident log of who did what, when. |
| **OWASP** | A well-known catalogue of the most common web security risks. |
| **STRIDE** | A method for finding threats (Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, Elevation of privilege). |
| **Trust boundary** | A line in the system where data crosses between more- and less-trusted zones. |

## Quality & operations

| Term | Meaning |
|---|---|
| **Unit / Integration / API / E2E test** | Tests at increasing scope: one function → parts together → the API → the whole user flow. |
| **UAT** | User Acceptance Testing — real users confirm it meets their needs. |
| **Coverage** | How much of the code the tests exercise (a quality signal). |
| **CI/CD** | Continuous Integration / Continuous Delivery — automation that lints, tests, and ships code. |
| **Observability** | Being able to see what the running system is doing, via **logs, metrics, traces, alerts**. |
| **DR** | Disaster Recovery — plans to restore service after a failure. |
| **RPO** | Recovery Point Objective — how much recent data you can afford to lose (backup freshness). |
| **RTO** | Recovery Time Objective — how quickly you must be back up. |
| **Ubuntu** | The Linux server operating system IDRM's MVP is deployed on. |

## Standards & compliance

| Term | Meaning |
|---|---|
| **WCAG 2.1 / 2.2 AA** | Web accessibility guidelines IDRM aims to meet, so the platform works for everyone. |
| **ISO 27001** | International standard for information security management. |
| **ISO 22301** | International standard for business continuity. |
| **DPDP Act, 2023** | India's Digital Personal Data Protection Act — the privacy law IDRM complies with. |
| **ADR** | Architecture Decision Record — a short note capturing one decision and why it was made. |
| **PWA** | Progressive Web App — a website that can behave like an installable app (a future option). |

## Indian agencies & data sources (context)

| Term | Meaning |
|---|---|
| **NDMA / SDMA / DDMA** | National / State / District Disaster Management Authorities. |
| **NDRF / SDRF** | National / State Disaster Response Forces. |
| **IMD** | India Meteorological Department — weather and warnings. |
| **ISRO / NRSC** | India's space agency and remote-sensing centre — satellite data. |
| **EOC** | Emergency Operations Centre — a coordination hub during incidents. |

---

*If a term you need isn't here, add it in a pull request — this glossary is meant to grow.*
