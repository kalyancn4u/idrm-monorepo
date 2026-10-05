# IDRM FFP — Documentation Charter & Instructions

*Type: Document (charter / instructions) · Audience: everyone · Status: FFP (next-phase) planning*

> **FFP = Full-Fledged Product** — the later, full-scale enterprise system that the **MVP**
> (a Python/FastAPI **modular monolith**) evolves into **once concrete requirements justify it**.
> This file charters what belongs to the FFP phase and how its documents should be produced.

---

## 1. Relationship to the MVP

The MVP and FFP are **two phases of one product**, not two products:

```
MVP  (now)                         FFP  (next phase)
Modular monolith            ──►    Selective microservices (polyglot: Python + Java/Go/JS)
Python / FastAPI                   + APISIX API gateway + JS edge (Bun/Node/Deno)
HTML / Tailwind CSS / JS web UI             + React web SPA + React Native / Expo mobile
PostgreSQL + PostGIS               + Redis / Streams, brokers, workers
Single deployable                  + Docker / Swarm / Kubernetes, CI/CD, observability
```

**Golden rule:** the FFP is introduced **incrementally and only when a real requirement
justifies it** — scale, team ownership, independent deployment, performance, or reliability.
The MVP's **API contracts and module boundaries are preserved**, so each FFP capability is an
*evolution* of the monolith, never a rewrite. Every FFP addition is recorded as an ADR that
states the concrete trigger.

See the MVP side at [`../../idrm-mvp-docs/prompts/instructions_idrm_mvp_docs.md`](../../idrm-mvp-docs/prompts/instructions_idrm_mvp_docs.md).

---

## 2. What is chartered to the FFP (deferred from the MVP)

These are **explicitly out of the MVP** and belong here. They are *not rejected* — they are the
next phase.

| Area | FFP technologies | Why it's FFP, not MVP |
|---|---|---|
| **Web frontend** | **React** (SPA) | The MVP ships server-friendly HTML/Tailwind CSS/JS; React is added when rich client-side interactivity is needed — consuming the *same* APIs. |
| **Mobile** | **React Native / Expo** | Native mobile apps come once field/offline use is required; they consume the same APIs. |
| **API gateway** | **APISIX** (with apt plugins/extensions) | The dedicated API gateway — **reverse proxy, caching, authentication, rate limiting, TLS termination, request routing, load balancing, observability** — covering all NGINX reverse-proxy capabilities via plugins. Introduced when the platform fronts multiple services/clients; the MVP has FastAPI serve APIs directly. |
| **Edge / runtime** | **Bun / Node / Deno** | JavaScript **edge / BFF / websocket / SSR** services that run **behind APISIX** for real-time and client-facing concerns — not the gateway itself. |
| **Architecture** | **Selective microservices** | Individual monolith modules are extracted into services only when scale/ownership/deploy pressure justifies it. |
| **Service runtimes (polyglot)** | **Java / Go / JavaScript** alongside **Python** | Performance-, security-, and resilience-critical services may be (re)written in **Java, Go, or a JS runtime** for better scaling, fault isolation, and runtime diversity (a resilience & backup strategy — not all services on one runtime). **Python is retained for rapid prototyping and DS/ML tasks & modeling** — its core strengths. Adopted **per-service, if and as time permits**, each justified by an ADR; all services keep the same public API contract. |
| **Async / messaging** | **Redis / Redis Streams**, **RabbitMQ / Kafka**, background **workers & queues** | Added for caching, background processing, and event-driven flows once measured need exists — PostgreSQL is optimised first. |
| **Infra / ops** | **Docker**, **Docker Swarm / Kubernetes**, CI/CD, distributed **observability**, HA/scaling | Containerisation and orchestration arrive with production/scale requirements. |
| **Object storage (scale-out)** | **distributed MinIO** cluster or **cloud S3** | The MVP already runs **MinIO** (single-node, S3-compatible) for file uploads. Because the code speaks the **S3 API**, the FFP scales it to a distributed/erasure-coded MinIO cluster or swaps in cloud S3 **without a code change** — same bucket/object contract. |
| **Geospatial (optional)** | dedicated tile/GIS server if needed | The MVP uses PostGIS + Python; a heavier GIS server is only added if map workloads demand it. |

> **PostgreSQL/PostGIS remains the system of record** across both phases. Redis, brokers, and
> caches never become the source of truth.

---

### Product-scope items deferred from the MVP PRD

Beyond the technologies above, the MVP **PRD** deferred these **product-scope** ambitions to the FFP
(see [`../../idrm-mvp-docs/10-requirements-prd.md`](../../idrm-mvp-docs/10-requirements-prd.md) §13):

- AI-powered automated matching / routing (MVP uses rule-based matching)
- National-scale rollout (all states/UTs); market/competitive positioning & monetization
- Advanced / predictive analytics & insights (MVP = basic reports)
- Full localization in 12+ Indian languages (MVP = core languages, multi-language-ready)
- Multi-channel intake (WhatsApp / voice / IVR)
- Deep real-time push infrastructure (MVP = near-real-time is acceptable)

---

### Product-scope items deferred from the MVP Scope & Acceptance work

While writing [`../../idrm-mvp-docs/11-requirements-scope-and-acceptance.md`](../../idrm-mvp-docs/11-requirements-scope-and-acceptance.md),
the richer **v3 Functional Specification** (`v3/11-requirements-functional-spec.md`, now in `../../_removed/idrm-docs-v3/`)
described a larger system than the MVP. These five capabilities were **routed here** (user-confirmed 2026-08-12)
so the MVP scope stays lean; the v3 functional spec is their primary source material:

- **Full role hierarchy (8–10 levels).** The MVP uses **3 roles** (citizen, provider, coordinator/admin).
  The v3 tiers — Individual, Volunteer, Organizer, Manager, Executive, Event Admin, Auditor, System Admin,
  with a per-cell permission matrix and area/org/jurisdiction scoping — are an FFP IAM concern.
- **Financial / donation subsystem.** Donation recording, fund pooling & allocation, financial-transparency
  reports, and the **Auditor** role (v3 `FR-FIN-*`, `BR-FIN-*`). The MVP coordinates *help*, not *funds*.
- **Extended request lifecycle states.** The MVP lifecycle is lean (created → *approved-if-critical* →
  accepted → in-progress → completed → verified, plus cancelled/rejected exits). The v3 **Disputed** state
  and **automatic Close** (auto-close N days after Verified) are deferred.
- **Per-request privacy levels (Public / Protected / Private).** The MVP protects citizen personal and
  location data through **role-based access** (not exposing contact details publicly) rather than a
  three-tier, per-request privacy model with system-mediated contact (v3 `FR-SEC-001`).
- **"Disaster Event" as a first-class entity.** Authorities declaring events, **drawing affected zones**
  on the map, auto-linking requests to an event, and computing affected area (v3 `FR-GEO-004`, event
  lifecycle). The MVP stays **request-centric**: each request carries a location + service type, and the
  coordinator sees them all on one map.

---

### Media & biometric capabilities deferred from the MVP media rules

The MVP enforces file/photo **compression, resolution, and clarity** rules and uses **lightweight,
client-side face *detection*** as a photo-quality gate (a clear, sharp face is present — **nothing
biometric is created or stored**). See [`../../idrm-mvp-docs/40-api-specification.md`](../../idrm-mvp-docs/40-api-specification.md) §5.7
("Media handling & quality rules"). Routed to the FFP (user-confirmed 2026-08-12):

- **FaceNet face *recognition* / matching** — biometric face **embeddings** to identify or re-identify
  people across photos (missing-person search, reuniting families). This is heavier **DS/ML** *and*
  processes **biometric data of vulnerable people**, so it must ship with **explicit consent, purpose
  limitation, retention limits, and India DPDP Act 2023 safeguards**. Uses the FFP's retained **Python
  DS/ML** stack. Never a silent MVP addition.
- **Scaled server-side media pipeline** — background **workers/queues** for transcoding, thumbnailing,
  virus scanning, and heavier re-compression (the MVP does light client-side compression + inline server
  validation). Ties to the deferred Redis/broker/worker infra above.
- **Video & large media** — beyond the MVP's image/PDF **≤ 10 MB** rule.

---

## 3. Primary source material

The **archived documentation generations already describe this FFP-style design** (Bun gateways,
microservices, React/React Native, Redis, Docker) — they were ahead of the MVP simplification.
So the FFP docs should be **consolidated primarily from the archive**:

- `idrm-docs-v2` — the microservices "corrected-final" architecture, Bun gateway, React. *(RETIRED to `../../_removed/idrm-docs-v2/` on 2026-08-12 after its detail was deep-merged into FFP-02/03/04/06/08; recoverable from quarantine.)*
- `idrm-docs-v3` — multi-frontend design, API contracts, the recorded decisions. *(RETIRED to `../../_removed/idrm-docs-v3/` on 2026-08-12 after its detail was deep-merged into the FFP docs; its beginner tutorials — Redis-101, FastAPI-from-scratch, Bun-gateway — are **guide-source for the pending T2 guides**, recoverable from quarantine.)*
- `idrm-docs-v0` — earliest / mixed microservices + DevOps material (API/data extracted to `assets/*.xlsx`). *(RETIRED to `../../_removed/idrm-docs-v0/` on 2026-08-12.)*

> **All versioned generations (v0–v3) are now retired to `../../_removed/`** (reversible quarantine). Their
> needful content lives in the MVP + FFP docs, the `assets/*.xlsx`, and `../../analyses/`. Recover from
> `_removed/` if a detail is ever needed (e.g. v3's beginner tutorials for the T2 guide phase).

When the MVP consolidation routes a conflicting/advanced topic here (e.g. "Bun gateway",
"React SPA", "microservice decomposition"), capture it in the matching FFP document below.

---

## 4. FFP documentation set (mirrors the MVP set)

Same shared naming `<prefix>-<category>-<name>.md` and legend as everywhere else. FFP specs live
in `idrm-ffp-docs/`; FFP novice guides in `idrm-ffp-guides/`; FFP code in `idrm-ffp-code-template/`.

The FFP set **mirrors the MVP set 1:1** (FFP is functionally an *extension* of the MVP), plus **one**
FFP-specific doc (Messaging & Async). Each MVP doc has an FFP counterpart at the **same** `<prefix>` so the
two sets read in parallel. **12 docs — this set is FROZEN (2026-08-12):** all archived-generation content
merges into one of these 12 (or goes to `../../analyses/` if auxiliary); no new FFP doc categories are
invented from the generations.

| # | Document | MVP counterpart | Focus at FFP scale | Target file |
|---|---|---|---|---|
| 01 | Product Requirements (PRD) | `10-requirements-prd` | enterprise-scale requirements & SLAs | `10-requirements-prd.md` |
| 02 | Scope & Roadmap | `11-…-scope-and-acceptance` | phased evolution from MVP; triggers per capability | `11-requirements-scope-and-roadmap.md` |
| 03 | System Architecture | `20-architecture-system` | **microservices** decomposition, **APISIX** gateway, Bun/Node edge, service boundaries | `20-architecture-system.md` |
| 04 | Architecture Decisions | `21-architecture-decisions` | ADRs recording each FFP addition & its trigger | `21-architecture-decisions.md` |
| 05 | Security & IAM | `22-…-security-and-iam` | OIDC/SSO, MFA, ABAC, gateway auth, zero-trust, secrets vault | `22-architecture-security-and-iam.md` |
| 06 | API & Contracts | `40-api-specification` | gateway + inter-service contracts (**same public API**) | `40-api-specification.md` (+ `40-api-openapi.yaml`) |
| 07 | Data Architecture | `50-data-model` | per-service data ownership, the deferred tables, replication, migrations | `50-data-model.md` |
| 08 | Frontend | `60-uidesign-web-interaction` | React web SPA + React Native/Expo mobile (same API) | `60-uidesign-frontend.md` |
| 09 | Quality & Test | `70-quality-test-strategy` | contract testing, heavy E2E, performance/load, DAST, DORA | `70-quality-test-strategy.md` |
| 10 | Operations & Platform | `80-ops-deployment-and-operations` | Docker, Swarm/Kubernetes, CI/CD, observability, HA, AWS variant | `80-ops-platform-and-deployment.md` |
| 11 | Messaging & Async *(FFP-only)* | — | Redis Streams / RabbitMQ / Kafka, workers, queues, deep push | `81-ops-messaging-and-async.md` |
| 12 | Contributor Guide *(→ guides)* | `guides/30-contribute` | contributing across services | `idrm-ffp-guides/30-contribute-developer-guide.md` |

Each can be expanded into a full CO-STAR prompt (like the MVP Architecture prompt) and saved in
this `prompts/` folder. **The per-doc source map + keep/discard triage lives in the consolidation
checklist:** [`ffp-consolidation-checklist.md`](ffp-consolidation-checklist.md).

---

## 5. Guardrails

- **Do not build the FFP before the MVP is proven.** The FFP is the *destination*, not the start.
- **Preserve the public API contract** so MVP clients keep working as services are introduced.
- **One trigger per addition** — every FFP technology enters via an ADR naming the concrete need.
- **Incremental extraction** — pull one module into a service at a time; never big-bang rewrite.
- Keep the same **domain model and module boundaries** the MVP established.
