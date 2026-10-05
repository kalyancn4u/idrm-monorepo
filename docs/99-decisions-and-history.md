# Decisions & History (Owner Reference)

> **Part of:** IDRM Documentation · `99-decisions-and-history.md`
> **Answers:** What did we decide, why, and what changed along the way?
> **Source posters:** all (as the authoritative baseline)
> **Audience:** Owner / maintainers (reference only) · **Depth:** Reference
> **Status:** Living record

---

## About this file

This is a **private-to-the-project reference**, kept deliberately **separate** from the reader-facing
documentation. The main documents (`00`–`08`) describe the MVP and its future vision **as they are now** —
they never discuss earlier approaches. This file is the one place that records **decisions and change
history**, so nothing is lost and no one has to rediscover *why* a choice was made.

It is not part of any reading path. Consult it only when you need the rationale or the lineage.

---

## Part 1 — Architecture Decision Records (ADRs)

Each record is short: the decision, the context, and its consequences. All are **Accepted** and reflected in
the posters and the current documentation.

### ADR-001 — Modular monolith (not microservices)
- **Decision:** Build IDRM as a single application organised into clean internal modules.
- **Context:** A disaster-response MVP needs reliability, low operational burden, and fast delivery by a
  small team. Microservices add distributed-systems complexity, more failure points, and higher cost.
- **Consequences:** Simple to run and debug; deploy as one unit. Module boundaries are kept clean so
  individual modules can be split out later *if* scale ever demands it. Scaling is vertical first.

### ADR-002 — One language: Python 3.12 (Flask + FastAPI)  *(view layer superseded by ADR-012 — FastAPI only, no Flask)*
- **Decision:** Use Python 3.12 end to end — Flask for the web UI, FastAPI for the APIs — in one process.
  No separate JavaScript/other-language gateway service.
- **Context:** A single language and runtime minimises skills needed, moving parts, and integration bugs.
- **Consequences:** One dependency set, one deployment, one debugging model. NGINX (optional) is the only
  reverse proxy in front.

### ADR-003 — Server-rendered UI (Jinja2 + Bootstrap 5)  *(superseded by ADR-012 — Tailwind CSS + vanilla JS, no Bootstrap)*
- **Decision:** Render pages on the server with Flask + Jinja2, styled with Bootstrap 5. No client-side SPA
  framework for the MVP.
- **Context:** The MVP needs accessible, fast, low-complexity pages that work on modest devices and networks.
- **Consequences:** Simpler build, better first-load performance, easy accessibility. Richer client apps
  (e.g. a mobile/PWA experience) remain a future option, not an MVP dependency.

### ADR-004 — In-process background jobs (threading / ThreadPoolExecutor / APScheduler)
- **Decision:** Run background and scheduled work inside the application using Python's threading tools and
  APScheduler. No external message broker or separate worker fleet for the MVP.
- **Context:** MVP background needs (alerts, emails, imports, scheduled reports) fit comfortably in-process.
- **Consequences:** Fewer services to run and monitor. If job volume grows, an external queue/worker can be
  introduced later behind the same module interfaces.

### ADR-005 — Geospatial via Python + GDAL (Conda), not a separate map server
- **Decision:** Handle GIS with Python geospatial libraries and GDAL, managed in a Conda environment, with
  PostGIS in the database.
- **Context:** A standalone map server is heavy operational overhead for MVP needs; Python + GDAL + PostGIS
  covers required spatial queries and layers.
- **Consequences:** One fewer server to operate. Conda is used *only* for the GIS/GDAL toolchain.

### ADR-006 — PostgreSQL + PostGIS primary; Redis optional  *(superseded by ADR-012 — no Redis in MVP; MinIO added)*
- **Decision:** PostgreSQL (with PostGIS) is the single source of truth. Redis is used for caching/sessions
  where it helps, and is optional.
- **Consequences:** Strong, well-understood data foundation; spatial support built in; caching can be added
  or removed without architectural change.

### ADR-007 — Deploy on a standalone Ubuntu server first; AWS later
- **Decision:** Target a standalone Ubuntu server (enterprise / academic campus, on-premises) as the primary
  deployment. AWS is documented as a later variant.
- **Context:** Initial users are campus/enterprise settings with on-prem preference and budget limits.
- **Consequences:** Predictable, low-cost operation; a single-server footprint. Cloud deployment is an
  additive path, not a rewrite.

### ADR-008 — Single-server MVP, scale when triggered
- **Decision:** Run the MVP on one appropriately-sized server; scale up (vertical) or out (later) only when
  measured load requires it.
- **Consequences:** Lowest complexity and cost for launch; clear, metric-based triggers govern any scaling.

### ADR-009 — URL-based API versioning (`/api/v1/...`)
- **Decision:** Version the API in the URL path; add `/api/v2` only for genuinely breaking changes, with a
  deprecation window.
- **Consequences:** Clear, cacheable, easy to test; stable contracts for clients.

### ADR-010 — Environment & dependency management: Miniconda for MVP
- **Decision:** Manage the Python 3.12 environment and dependencies with **Miniconda** for the MVP (presumed
  default). Lighter, context-appropriate managers — **mamba, micromamba, or uv** — may be used instead where
  they fit better (e.g. faster solves, slimmer CI images). Miniconda is chosen over full Anaconda to avoid
  bulk while still providing the geospatial/GDAL packages the project needs.
- **Context:** IDRM needs reliable native/geospatial dependencies (GDAL and friends) without the heaviness of
  a full Anaconda install. The team may prefer faster or slimmer tools depending on the machine or pipeline.
- **Consequences:** One consistent way to reproduce environments for the MVP, with room to swap in
  mamba/micromamba/uv without changing the architecture. **Specialised or isolated setups going forward are
  expected to move to Docker** (per-service or per-tool images), especially as needs diverge from the single
  MVP environment. This aligns with ADR-005 (GIS via Python + GDAL) — Miniconda is simply how that toolchain
  is provisioned.

### ADR-011 — Documentation standards for the deep-dive (Phase G1)
- **Decision:** Produce the developer-grade documentation to recognised, current standards: **ISO/IEC/IEEE
  29148:2018** (requirements/SRS), **ISO/IEC/IEEE 42010:2022** with the **arc42** template and **C4 model**
  diagrams (architecture), **IEEE 1016** viewpoints (detailed design), **OpenAPI 3.1** (API spec; 3.2 exists
  but 3.1 maximises tooling support, and 4.0 is unreleased), ERD + data dictionary aligned to **ISO/IEC
  11179** metadata principles (data model), and a **29148** bidirectional traceability matrix. Decisions use
  **MADR**-style ADRs, changes follow **Keep a Changelog 1.0.0** + **SemVer 2.0.0**, and all output targets
  **WCAG 2.2 AA**. (For the deferred end-user guides: **Diátaxis** structure + **ISO/IEC/IEEE 26514:2022**
  process + **Google/Microsoft** style guides.)
- **Context:** The owner asked that Phase G follow standard professional approaches, validated against top
  trusted sources before any artifact is produced.
- **Consequences:** Deep-dive docs live in `docs/deep-dive/` and deepen the lean set without altering it. Each
  artifact passes a validation-first workflow and conformance checklist before emission (see
  `docs/deep-dive/00-plan.md`). Scope for now is **G1 (developer docs)**; G2/G3 are planned but deferred.

### ADR-012 — MVP stack refinement: FastAPI-served HTML/Tailwind/JS UI; no Redis; MinIO for files
- **Decision:** For the MVP, refine three stack specifics from the original posters:
  1. **View layer** — the web UI is **FastAPI-served HTML + Tailwind CSS + vanilla JS (+ Leaflet)**, *not*
     Flask + Jinja2 + **Bootstrap**. One framework (FastAPI) serves both the HTML pages and the REST APIs.
     (Jinja2 templating is retained, used via FastAPI; **Flask** and **Bootstrap** are dropped.)
  2. **Redis** — **not used in the MVP**; sessions/caching live in **PostgreSQL**. Redis is deferred to the FFP
     scale-out.
  3. **Object storage** — **MinIO** (S3-compatible) is **in** the MVP for uploaded files (incident photos,
     completion proof); the DB stores only keys/URLs.
- **Context:** These were confirmed as **locked decisions** while building the finalized MVP specifications in
  the project archive (now replicated to [`mvp/`](mvp/) / [`ffp/`](ffp/)). They keep the MVP leaner (one web
  framework, no Redis) while adding the file-upload capability the product needs.
- **Consequences:** **Supersedes in part** ADR-002 (drops Flask), ADR-003 (Tailwind/JS instead of
  Jinja2+Bootstrap server-rendered), and ADR-006 (no Redis in MVP; MinIO added). The finalized `mvp/`+`ffp/`
  specs are authoritative where they differ from the older overview/posters. **The authoritative posters in
  `posters/` should be updated to match** (they are not present in this workspace to edit here). Decided
  2026-08-14.

*(Add new ADRs below as decisions are made — keep the same short shape.)*

---

## Part 2 — What changed along the way (lineage)

For context only. Earlier drafts explored heavier or more complex approaches before the design settled on the
simple modular monolith the posters describe. In brief:

| Stage | Direction explored | Then simplified toward… |
|---|---|---|
| Early drafts (v0–v1) | Multiple languages and a standalone map server | One language; DB-native GIS |
| v2 | Split into several separate services; a JavaScript API gateway; client-side app frameworks | Fewer moving parts |
| v3 | Named a "modular monolith" but still carried a separate gateway, multiple internal service ports, several frontends, and an older Python runtime | **Posters (current):** one Python 3.12 process, server-rendered UI, in-process jobs |
| **Posters (current, authoritative)** | Standalone modular monolith — the design all documentation now follows | — |

The takeaway: **each step removed complexity.** The current design is the simplest thing that fully serves
the MVP while leaving a clean path to grow.

Full historical material (the earlier drafts themselves) lives in `archive/` at the project root and is kept
for reference only.

---

## Part 3 — Guardrail: do NOT reintroduce

To keep the design clean, the following were intentionally left out of the MVP. Do not add them back without
a new ADR that supersedes the relevant decision above:

- Microservices with separate ports → internal modules in one process (ADR-001)
- A separate (e.g. JavaScript) API gateway → single Python process behind optional NGINX (ADR-002)
- Client-side SPA / native mobile frameworks → server-rendered Jinja2 + Bootstrap (ADR-003)
- External broker + worker fleet for background jobs → in-process threading/APScheduler (ADR-004)
- A standalone geospatial/map server → Python + GDAL + PostGIS (ADR-005)
- A non-current Python runtime → Python 3.12 (ADR-002)
- Full **Anaconda** for the MVP environment → **Miniconda** (lighter), or mamba/micromamba/uv per context;
  Docker for specialised setups later (ADR-010)

---

## Part 4 — Poster conformance record

This record pins the naming to the posters and prevents the MVP and the broader-vision posters from being
blended by accident.

### 4.1 Canonical MVP data entities (conforms to **Poster 22 — Entity Relationship Overview**)

18 tables in five groups. These names are authoritative for `docs/deep-dive/13-data-model.md` and the API.

| Group | Tables (PK = `<name>_id`) |
|---|---|
| **Access & Administration** | `users`, `roles`, `organizations`, `locations` |
| **Incident Management** | `incidents`, `incident_types`, `incident_updates`, `alerts` |
| **Response Management** | `responders`, `resources`, `resource_types`, `deployments`, `tasks` |
| **Data & Content Management** | `documents`, `media`, `geospatial_data` |
| **Communication & Audit** | `communication_logs`, `audit_logs` |

Naming conventions (Poster 22): PK/FK use `_id` suffix · timestamps `created_at`/`updated_at` · soft-state via
`status`/`is_active` · spatial columns use PostGIS Geometry · files/media in Object Storage. Key relationships:
Organizations 1—N Users · Locations 1—N Organizations · Incidents N—1 Locations · Incidents 1—N
Updates/Alerts/Tasks/Deployments/Documents/Media/CommLogs/AuditLogs · Resources N—N Incidents (via
Deployments) · Users 1—N AuditLogs.

### 4.2 Poster scope map — MVP (build now) vs broader vision (future/FFP)

The `posters/01-vision/` Phase-3 posters (17, 20, 23) depict the **enterprise/full-fledged (FFP)** stack; the
`posters/02-execution/` **MVP** posters (`idrm-mvp-*`) and the owner's `idrm-posters.txt` annotations govern
what we build now. When they differ, the **MVP source governs the current build**; the vision poster is the
recorded future target.

| Topic | MVP — build now (authoritative) | Broader vision / FFP — future only |
|---|---|---|
| Architecture | Modular monolith (execution `idrm-mvp-*`) | Microservices (Poster 17 repo; execution `idrm-ffp-*`) |
| Backend | Python 3.12 · Flask + FastAPI (execution MVP) | Node.js/NestJS + gRPC (Poster 20) |
| Frontend | Jinja2 + Bootstrap 5, server-rendered (execution MVP) | React/Next.js + React Native + Tailwind (Poster 20) |
| GIS | Python + GDAL + PostGIS, no map server (`idrm-posters.txt` note on Poster 23) | GeoServer + WMS/WFS + CesiumJS (Poster 23) |
| Background jobs | threading / ThreadPoolExecutor / APScheduler (execution MVP) | Kafka + Airflow (Poster 20) |
| Data stores | PostgreSQL+PostGIS · Redis · Object Storage (**Posters 21 & 22 — MVP**) | + OpenSearch · MinIO · ELK (Poster 20) |
| Deployment | Standalone Ubuntu server (Poster 28 Ubuntu) | Kubernetes / Terraform / cloud (Poster 20; Poster 28 AWS) |

**The data model (Posters 21 & 22) is MVP and architecture-neutral** — it holds whether IDRM is a monolith now
or is decomposed later, so no conflict there.

---

## Part 5 — Documentation change log

| Date | Change |
|---|---|
| 2026-08-09 | Established the lean documentation set (`00`–`08`, `90`, `99`) aligned to the posters. Recorded ADRs 001–009. Reader-facing documents made forward-only; all history/decisions consolidated here. |
| 2026-08-09 | Added ADR-010 — Miniconda as the MVP environment/dependency manager (mamba/micromamba/uv as context-appropriate alternatives; Docker for specialised setups going forward). Reconciled the guardrail accordingly. |
| 2026-08-09 | Completed the lean reader set (`00`–`08`). Added ADR-011 — documentation standards for the deep-dive (Phase G1), validated against current external standards. Saved the Phase G plan at `docs/deep-dive/00-plan.md`. Scope = G1 (developer docs); G2/G3 deferred. |
| 2026-08-09 | Reviewed Posters 21, 22, 23, 17, 20. Rewrote `deep-dive/13-data-model.md` to **conform to Poster 22** (18 named tables). Added the Part 4 poster-conformance record, including the MVP-vs-broader-vision scope map (Phase-3 vision posters 17/20/23 = FFP/future; execution MVP posters govern the build). |
| 2026-08-09 | **Completed Phase G1 (developer docs)**: `12-api-spec.md` + `openapi.yaml` (OpenAPI 3.1, validated — 13 paths/23 schemas/65 refs resolve), `10-srs.md` (ISO/IEC/IEEE 29148), `11-architecture-and-design.md` (arc42 + C4 + IEEE 1016), `14-traceability-matrix.md`. All conformed to the posters and passed forward-only checks. G2/G3 deferred. |
| 2026-08-09 | **Completed Phase G2 (end-user guides)** in `docs/user-guides/`: overview + Citizen, Responder, Coordinator, Administrator. Diátaxis-structured (get-started/how-to/reference/understand); conformed to Poster 8 (personas) & Poster 7 (workflow); WCAG-minded, multilingual-ready. Only G3 (pptx) remains. |
| 2026-08-09 | **Completed Phase G3 (presentation)**: `presentation/IDRM-MVP.pptx` — 45 slides, hybrid audience, native poster-matched design (navy+green), MVP-only content in the posters' suggested order, speaker notes, appendix. Built with pptxgenjs; structural validation PASSED; visual QA via PowerPoint export (fixed dark-card contrast + chevron label clipping + roadmap overflow). PDF export alongside. Documentation effort complete. |
| 2026-08-09 | **Conformance review** against all MVP posters → `98-review-and-improvements.md`. Resolved tensions T1 (native systemd; Docker Compose optional), T2 (NGINX; APISIX optional), T3–T5. **Applied P1 batch**: `07-operations` (deploy spec/ports/paths/hardening + observability SLO/SLA/playbook + DR plan/RPO-RTO/runbook), `05-security` (layers, workflow, OWASP Top 10 mapping, assets, threat actors, risk matrix, NIST CSF/ASVS), `03-engineering` (per-layer SOLID & pattern matrices), `08-organization` (8-phase roles + RACI ownership), `02` (evolution stages + maturity questions), `06` (pyramid proportions + tools + DORA). P2/P3 remain. |
| 2026-08-09 | **Applied P2 batch**: `01-foundation` (SDLC delivery roadmap — Poster 4; specific agencies + Common Operating Picture — Poster 3), `08-organization` (technology fit-scores — Poster 33; 6-phase 10-year roadmap — Poster 34), `06-quality` (release-readiness gates — Poster 27). Only P3 items remain (02 flow-legend, deep-dive ops runbook, OWASP→SRS, refresh deck/user-guides). |
| 2026-08-09 | **Presentation v3** — `presentation/IDRM-MVP-v3.pptx` (+PDF): a from-scratch **editorial-minimalist makeover** in the style of the attached `DRMI_Presentation_01.pdf` — pure-white slides, "IDRM.**I**" wordmark, two-tone titles, inline accent highlights (orange/green/blue/red), **single font (Calibri)**, WCAG-AA. Blends the attachment's signature concepts (5W1H, disaster types, three-phase cycle, immediate/mid-term response, the **anatomy/analogy** = neural→information highway + circulatory→logistics highway, two highways, five C's, services & processes, web-portal, requirements, map annotator/summarizer, service-request fields, references) with the MVP substance. 40 slides. (Fix: removed negative-dimension connector lines that made PowerPoint reject the file though the XSD validator passed.) |
| 2026-08-09 | **Presentation companion** — `presentation/IDRM-MVP-presentation-companion.md`: the complete two‑part narrative (Part I general audience §1–12; Part II technical deep‑dive §13–35 incl. abstracted API function catalog), collated/merged/de‑duplicated/validated from all MVP posters + docs, sorted, with a poster→section map. Depth: up to high‑level/abstracted API (no code). Source for generating further presentations. |
| 2026-08-09 | **Presentation v2** — `presentation/IDRM-MVP-v2.pptx` (+PDF): 47 slides, **Indian-flag palette** (Ashoka-blue `0B2E63`, saffron `FF9933`/`C05600`, India-green `147A3D`, white — WCAG-AA tuned), **single font (Calibri)**. Adds an **SDLC roadmap** slide, an **OWASP Top 10 → mitigations** slide, deployment spec/ports; carries the SLO/RACI/6-phase updates. Validated + visual QA (flag-colored pyramid, saffron flow arrows, tricolor number chips). v1 retained. |
| 2026-08-09 | **Applied P3 batch (backlog complete)**: `02` (Admin/Integration services + flow-type legend), new `deep-dive/15-ops-runbook.md`, OWASP + perf targets folded into `10-srs`, and **presentation refreshed** (observability→SLO/SLA, ownership→RACI, roadmap→6-phase 10-year; re-validated + visual QA). User guides need no change. All 98-review findings resolved. |

---

*This file is the single home for decisions and history. The reader-facing documents stay focused on the
MVP and its future — clean, forward-looking, and free of legacy detail.*
