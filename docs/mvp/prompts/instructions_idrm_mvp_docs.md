# IDRM MVP — Minimal Documentation Set

*Type: Document (overview / plan) · Audience: everyone · Status: MVP planning*

> **Principle:** The goal is **not** to write 30 documents before writing code. It is to create the
> **minimum set that gives stakeholders, developers, testers, security reviewers, and future
> contributors one shared source of truth** — and no more. The documentation should mirror the
> architecture: clear boundaries, minimal duplication, one source of truth per decision, and enough
> explanation that a newcomer knows *what to change, where, and why*.

This plan aligns with the IDRM MVP architecture (a **Python/FastAPI modular monolith**, HTML/Tailwind CSS/JS
web UI, PostgreSQL/PostGIS as the source of truth, API-first, with Redis/Docker/React/microservices
**deferred**). See the generation prompt at [`../prompts/IDRM MVP Architecture - CO-STAR Prompt.md`](../prompts/IDRM%20MVP%20Architecture%20-%20CO-STAR%20Prompt.md).

---

## The set at a glance

**Ten core documents.** Nine are specifications → they live in **`idrm-mvp-docs/`**. One is a
novice guide → it lives in **`idrm-mvp-guides/`**. Filenames follow the shared archive convention
`<prefix>-<category>-<name>.md` (tens-digit = category: `10` requirements · `20` architecture ·
`40` api · `50` data · `60` uidesign · `70` quality · `80` ops; guides: `30` contribute).

| # | Document | Answers | Priority | Target file | Folder |
|---|---|---|---|---|---|
| 01 | **Product Requirements (PRD)** | *Why* IDRM, for whom, what problem | 🔴 Essential | `10-requirements-prd.md` | docs |
| 02 | **MVP Scope & Acceptance Criteria** | What is in/out of MVP; when it's "done" | 🔴 Essential | `11-requirements-scope-and-acceptance.md` | docs |
| 03 | **System Architecture (SAD)** | Overall design & technology decisions | 🔴 Essential | `20-architecture-system.md` | docs |
| 04 | **API & OpenAPI Specification** | Exact client↔backend contract | 🔴 Essential | `40-api-specification.md` (+ `40-api-openapi.yaml`) | docs |
| 05 | **Data Architecture & Database Design** | What is stored and how it relates | 🔴 Essential | `50-data-model.md` | docs |
| 06 | **Security & IAM Design** | Who can do what; how the system is protected | 🔴 Essential | `22-architecture-security-and-iam.md` | docs |
| 07 | **UI / Web Interaction Specification** | Screens, workflows, API interactions | 🟠 Important | `60-uidesign-web-interaction.md` | docs |
| 08 | **Test Strategy & Test Plan** | How we know IDRM works | 🔴 Essential | `70-quality-test-strategy.md` | docs |
| 09 | **Deployment & Operations Guide** | How to run, configure, back up, operate | 🟠 Important | `80-ops-deployment-and-operations.md` | docs |
| 10 | **Developer / Contributor Guide** | How a rookie makes their first contribution | 🔴 Essential | `30-contribute-developer-guide.md` | **guides** |

> **Note on categories:** Security & IAM (06) sits in the `20` architecture band (`22-…`) because
> it is an architectural concern, keeping the shared legend intact without inventing a new category.
> ADRs (below) live alongside it as `21-architecture-decisions.md`.

---

## Per-document briefs

Each brief is a compact generation spec (a "CO-STAR-lite"). Any one can be expanded into a full
CO-STAR prompt — like the existing Architecture prompt — and placed in [`../prompts/`](../prompts/).

### 01 · PRD — `10-requirements-prd.md`
- **Answers:** Why are we building IDRM, for whom, and what problem does it solve?
- **Contains:** vision · objectives · stakeholders · personas · use cases · functional requirements · non-functional requirements · business rules · constraints · assumptions · dependencies · success criteria.
- **Audience:** everyone (product → developers). · **Depends on:** nothing (start here).
- **Guardrail:** state *what/why*, **not** the tech (no "Python/FastAPI/PostgreSQL" here — that's the SAD).
- **Done when:** every MVP capability traces to a stated need; no solutioning; success criteria are measurable.

### 02 · MVP Scope & Acceptance Criteria — `11-requirements-scope-and-acceptance.md`
- **Answers:** Exactly what does "MVP complete" mean? (Kept separate from the PRD to prevent scope creep.)
- **Contains:** in-scope / out-of-scope lists · per-capability chain **Feature → Requirement → Acceptance Criteria → Test** · Given/When/Then examples.
- **Audience:** product, developers, testers. · **Depends on:** 01.
- **Done when:** every in-scope feature has testable acceptance criteria; out-of-scope is explicit.

### 03 · System Architecture (SAD) — `20-architecture-system.md`
- **Answers:** How is IDRM designed, and why these technologies? *(Already fully specified — generate from* [`../prompts/IDRM MVP Architecture - CO-STAR Prompt.md`](../prompts/IDRM%20MVP%20Architecture%20-%20CO-STAR%20Prompt.md)*.)*
- **Contains:** architecture principles · component/module boundaries · technology decisions · request flow · deployment-evolution roadmap · security & scalability/reliability strategy · Mermaid diagrams.
- **Audience:** novice → architect. · **Depends on:** 01, 02.
- **Done when:** it's a genuine modular monolith (not disguised microservices); boundaries explicit; evolution path credible.

### 04 · API & OpenAPI Specification — `40-api-specification.md` (+ `40-api-openapi.yaml`)
- **Answers:** Exactly how do clients talk to IDRM? (API-first — the contract is a product, not an afterthought.)
- **Contains:** resource endpoints (`/api/v1/incidents`, `/resources`, `/locations`, `/alerts`, `/users`…) · per-endpoint method, auth, request, params, validation, response, errors, status codes · a machine-readable `openapi.yaml`.
- **Audience:** developers, testers, integrators. · **Depends on:** 03 (+ 05 for schemas).
- **URI stability (user-confirmed 2026-08-12):** an API URI is a **public contract that does not change across the SDLC** — a path defined for the MVP keeps the **same URI** in the FFP (only the implementation behind it moves). Design the URIs **once, canonically**; FFP may *add* endpoints, never *rename* MVP ones.
- **Reconcile the asset:** [`../assets/idrm-api-resource-mapping.xlsx`](../../../archive/assets/idrm-api-resource-mapping.xlsx) is the single endpoint↔resource↔role↔rate-limit↔error matrix, but it currently uses a divergent, FFP-flavoured scheme (`/services/requests`, `/disasters`, `/financial/*`, base `https://api.idrm.gov.in/v1`). After the canonical URIs are confirmed, **update that xlsx** to match (tag rows MVP vs FFP, keep URIs identical, move financial/disaster/websocket rows to the FFP portion). Likewise reconcile `idrm-data-model.xlsx` / `idrm-triggers-views-complete.xlsx` with doc 50. See the hand-off §12.
- **Done when:** OpenAPI validates; the HTML/Tailwind CSS/JS UI **and** future React/mobile clients could consume the same contract; the assets xlsx matches the canonical URIs.

### 05 · Data Architecture & Database Design — `50-data-model.md`
- **Answers:** What information does IDRM store, and how is it related?
- **Contains:** conceptual model · logical model (entities, relationships, cardinalities) · physical model (PostgreSQL tables, columns, PKs/FKs, indexes, unique/constraints, timestamps, audit fields, **PostGIS** spatial columns) · migration approach (Alembic).
- **Audience:** DBAs, backend developers. · **Depends on:** 01, 03.
- **Done when:** PostgreSQL is the sole system of record; spatial data uses PostGIS; every table justified by a requirement.

### 06 · Security & IAM Design — `22-architecture-security-and-iam.md`
- **Answers:** Who can do what, and how do we protect the system? (Exists **before** serious implementation.)
- **Contains:** authentication · authorization · roles · permissions · RBAC (**User → Role → Permissions → API Operation**) · session/token model · password policy · API security · data protection · audit logging · secrets · least privilege.
- **Audience:** security reviewers, developers. · **Depends on:** 03, 04.
- **Done when:** every API operation maps to a permission; no secrets in code; audit trail defined. (ABAC deferred.)

### 07 · UI / Web Interaction Specification — `60-uidesign-web-interaction.md`
- **Answers:** What are the screens and how do they use the API? (Practical, not a giant UX spec.)
- **Contains:** pages · navigation · forms · tables · dashboards · maps · validation · error messages · accessibility · API interactions (e.g. Login → Dashboard → Incidents{List/View/Create/Update}).
- **Audience:** frontend devs, designers. · **Depends on:** 04.
- **Done when:** each screen names the API calls it makes; can evolve unchanged when React is introduced later.

### 08 · Test Strategy & Test Plan — `70-quality-test-strategy.md`
- **Answers:** How do we know IDRM works?
- **Contains:** the MVP pyramid — **Unit · API · Integration** (with DB tests), plus security/regression; later performance/E2E · tools (pytest) · coverage expectations · test-data approach.
- **Audience:** QA, developers. · **Depends on:** 02, 04, 05.
- **Done when:** every acceptance criterion (doc 02) maps to at least one test type.

### 09 · Deployment & Operations Guide — `80-ops-deployment-and-operations.md`
- **Answers:** How do we run, configure, back up, and operate IDRM? (Small for MVP — Docker/Swarm deferred.)
- **Contains:** install · configuration · env vars · database setup · migrations · startup/shutdown · logging · backup/restore · health checks. *(Growth path: Docker → CI/CD → Swarm → HA → monitoring.)*
- **Audience:** DevOps, admins, developers. · **Depends on:** 03, 05.
- **Done when:** a developer can stand up and operate IDRM locally from this doc alone.

### 10 · Developer / Contributor Guide — `idrm-mvp-guides/30-contribute-developer-guide.md`
- **Answers:** "I just joined IDRM — how do I make my first contribution?" *(Most important for the rookie/student model.)*
- **Contains:** prerequisites · repo structure · setup · running locally · database setup · running tests · coding conventions · branching/commit conventions · pull requests · issue workflow · module ownership · testing & security expectations.
- **Audience:** complete novices → experienced devs. · **Depends on:** 03, 08, 09.
- **Done when:** a "*I know Python*" reader can run IDRM and submit a small PR **without** understanding the whole architecture.

---

## Architecture Decision Records (ADRs) — one lightweight collection

Do **not** write a large separate decisions document. Keep a small ADR set as
`21-architecture-decisions.md` (or a folder of one-page records). Each ADR: **Decision · Context ·
Options considered · Decision made · Consequences.** Seed it with the intentional MVP *exclusions*:

```
ADR-001  Modular monolith (not microservices)
ADR-002  PostgreSQL + PostGIS as source of truth
ADR-003  API-first (OpenAPI as contract)
ADR-004  HTML/Tailwind CSS/JS for the MVP web UI (React deferred)
ADR-005  Redis deferred
ADR-006  Docker / Swarm deferred
```

These record **why** IDRM is deliberately *not* using React, Docker, Redis, Kafka, or Kubernetes yet.

---

## Build them in dependency order — not all at once

```
01 PRD
 ↓
02 MVP Scope
 ↓
03 System Architecture ── + ADRs
 ├───────────────┐
 ▼               ▼
04 API         05 Data
 └───────┬───────┘
         ▼
06 Security & IAM
         │
 ┌───────┴───────┐
 ▼               ▼
07 UI          08 Testing
 └───────┬───────┘
         ▼
09 Operations
         ▼
10 Contributor Guide
```

## The truly minimal core (six non-negotiable)

> **01 PRD → 02 Scope → 03 Architecture → 04 API → 05 Data → 06 Security**

Everything else (UI, Test, Ops, Contributor) can start as **lightweight sections inside those six**
and be split out into their own files only once they grow large. Start minimal; split on pressure.

---

## How to generate each document

Each brief above can be expanded into a full CO-STAR prompt following the template of
[`../prompts/IDRM MVP Architecture - CO-STAR Prompt.md`](../prompts/IDRM%20MVP%20Architecture%20-%20CO-STAR%20Prompt.md)
(Context · Situation · Task · Architectural requirements · Response requirements · Acceptance criteria),
then saved in [`../prompts/`](../prompts/) as e.g. `IDRM MVP PRD - CO-STAR Prompt.md`. The generated
document lands at the **Target file** named in the table above.

**Cross-cutting guardrails for every document:**
- The **PRD** states needs, not technology; technology lives in the SAD/design docs.
- **PostgreSQL is the source of truth** — never Redis, a broker, or a cache.
- **Defer infrastructure** (Redis, workers, Docker, Swarm, React, brokers, microservices) until a concrete, measured requirement justifies it — and record that reasoning as an ADR.
- Keep **one source of truth per decision**; cross-link rather than duplicate.
- Write so a **complete novice** can follow, without weakening technical accuracy.
