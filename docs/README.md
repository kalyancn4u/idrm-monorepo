# IDRM Documentation — Master Plan & Index

**Project:** IDRM — Integrated Disaster Response Management (MVP)
**Document:** `docs/README.md` — the entry point and plan for all IDRM documentation
**Status:** Documentation complete · MVP code **written (all 10 modules)** · white papers done · pending the Ubuntu/CI run
**Last updated:** 2026-08-18

---

## 0. What this is

This is the **front door** to IDRM's documentation. It explains the approach, lists the (deliberately small)
set of documents, and points each type of reader to the right starting place.

Newcomers should open **[`00-orientation.md`](00-orientation.md)** first — it's the shortest path in.

> **Where the project stands (2026-08-18):** the documentation is complete, the **MVP application code is written —
> all 10 modules** (see [`../services/monolith/`](../services/monolith/)), the **novice→mastery guide library** is in [`../guides/`](../guides/),
> and the **six FFP "intelligence-engine" white papers** are in [`whitepapers/`](whitepapers/). The one remaining
> step is *running* the code green on a Linux box (see [`../PENDING.md`](../PENDING.md)). The repository front door
> is [`../README.md`](../README.md).

---

## 1. Single source of truth

> **The posters are the authority.** Everything here is written to match the posters in `posters/`.

The posters describe IDRM as a **standalone modular monolith**:

| Aspect | Decision (per posters) |
|---|---|
| **Shape** | One application, one process — a *modular monolith* |
| **Language** | Python 3.12 |
| **Web UI** | **FastAPI-served HTML + Tailwind CSS + vanilla JS + Leaflet** (no Flask/Bootstrap) ⟵ *refined; see note* |
| **APIs** | FastAPI (REST, Pydantic validation, OpenAPI/Swagger) |
| **Background jobs** | Python threading / ThreadPoolExecutor / APScheduler (in-process) |
| **Data** | PostgreSQL + PostGIS (primary) + **MinIO** object storage; **no Redis** in MVP (sessions in Postgres) ⟵ *refined* |
| **GIS** | Python + GDAL in a Conda environment |
| **Deployment** | Standalone **Ubuntu server**; AWS is a later variant |
| **Evolution** | Monolith today → modular monolith → (optionally) larger enterprise deployment later |

> **Refinement note (2026-08-14):** the finalized MVP specifications in **[`mvp/`](mvp/)** (and the FFP set in
> [`ffp/`](ffp/)) refine two stack specifics from the original posters — the **view layer** is
> FastAPI-served **HTML + Tailwind + JS + Leaflet** (not Flask/Jinja/Bootstrap), and the MVP carries **no Redis**
> (sessions in PostgreSQL) while adding **MinIO** for files. These finalized docs **supersede** the posters on
> these points; the authoritative posters should be updated to match. Full rationale in the new decision entry in
> [`99-decisions-and-history.md`](99-decisions-and-history.md).

The design rationale behind these choices is recorded, for maintainers, in
[`99-decisions-and-history.md`](99-decisions-and-history.md).

---

## 2. Principles

1. **Poster-faithful.** Every claim traces back to a poster. No invented technology, no scope creep.
2. **Lean set.** One substantial document per phase — few files, each read straight through. Too many
   documents is its own clutter.
3. **Reading-flow order.** Files are numbered `00 → 99`; the number *is* the reading order.
4. **Role-first.** Readers are routed by who they are (see `00-orientation.md`), not asked to read everything.
5. **Overview depth now, detail later.** The first pass is clear and mostly non-technical; deep technical
   detail is layered in a later pass and marked **Depth: Deep**.
6. **Self-anchoring.** Every file opens with a header naming its source poster(s), audience, and depth — so
   each document is always traceable to the authoritative posters.
7. **Accessible & non-duplicative.** Plain language, WCAG-minded formatting; shared facts live in one place.

---

## 3. The document set (lean, flat, ordered)

All documents live directly in `docs/`. Status: ☐ planned · ◐ in progress · ☑ done.

| # | Document | Answers | Source posters | Status |
|---|---|---|---|---|
| 00 | [`00-orientation.md`](00-orientation.md) | Where do I start? How is this organised? | Big Picture (35) | ☑ |
| 01 | [`01-foundation.md`](01-foundation.md) | *Why* does IDRM exist? (vision, problem, scope, stakeholders, domains, lifecycle, workflow) | Posters 1–8 | ☑ |
| 02 | [`02-architecture.md`](02-architecture.md) | *What* is IDRM? (system, layers, functional, modules, flows, evolution) | Posters 9–16, MVP-01…07 | ☑ |
| 03 | [`03-engineering.md`](03-engineering.md) | *How* is it built? (repo, standards, patterns, tech stack) | Posters 17–20 | ☑ |
| 04 | [`04-data.md`](04-data.md) | The data & maps (database, entities, GIS) | Posters 21–23 | ☑ |
| 05 | [`05-security.md`](05-security.md) | How is it kept safe? (security architecture, threat model) | Posters 24–25 | ☑ |
| 06 | [`06-quality.md`](06-quality.md) | How do we know it works? (testing, CI/CD) | Posters 26–27 | ☑ |
| 07 | [`07-operations.md`](07-operations.md) | How do we run it? (Ubuntu deploy, observability, DR; AWS appendix) | Posters 28–30 | ☑ |
| 08 | [`08-organization.md`](08-organization.md) | Who owns it, where's it going? (roles, ownership, decision matrix, training paths, roadmap, big picture) | Posters 31–35 | ☑ |
| 09 | [`09-roadmap.md`](09-roadmap.md) | **The complete roadmap** — Concept → MVP → FFP, the build plan, the learning path; for novices, engineers & non-technical stakeholders | all | ☑ *(2026-08-16)* |
| 90 | [`90-glossary.md`](90-glossary.md) | What does this term mean? | all | ☑ |
| 98 | [`98-review-and-improvements.md`](98-review-and-improvements.md) | Conformance review & improvement backlog | all | ☑ |
| 99 | [`99-decisions-and-history.md`](99-decisions-and-history.md) | Decisions & rationale (owner reference — not a reading-path doc) | all | ☑ |

**Total: 12 documents** (incl. the new **[`09-roadmap.md`](09-roadmap.md)** — the complete Concept→MVP→FFP journey
for every audience). Each phase is a single, coherent chapter rather than a scatter of small files.

> **Later pass (optional, only if needed):** developer-grade depth (API specs, full data model, low-level
> design), task-oriented end-user guides, and the pptx presentation. These are added *after* the lean set is
> approved — not up front.

### Detailed reference layers (added 2026-08-14 — "sit beside" the overview)

Alongside this overview set, the **finalized, fuller specifications and the learning library** now live in the
base, replicated from the project archive (blueprint T5):

| Layer | Location | What it is |
|---|---|---|
| **MVP specs** | [`mvp/`](mvp/) | 18 detailed MVP specifications — PRD, architecture, ADRs, security, API+OpenAPI, data model, UI, quality, ops, + domain/capability, traceability, data-flow, governance, **module elucidation (25)**, the signed-off **conformance PICS (26)**, and the novice→mastery **Implementation Roadmap (27)** — the builder's "start here" that threads them all into reading order |
| **FFP specs** | [`ffp/`](ffp/) | 17 FFP specifications (deltas on the MVP) + the frontend-engineering companion + **module elucidation (25)** and **conformance PICS (26)** |
| **Guides** | [`../guides/`](../guides/) | The novice→mastery learning library — 40 topic **101s** (incl. the **Technology Stack 101** component map) + 12 **role-mastery** journeys (MVP) + the FFP learning hub |
| **White papers** | [`whitepapers/`](whitepapers/) | 6 "intelligence-engine" design papers (*design-now / build-FFP*): FAQ chatbot, anomaly detection ×2, two recommenders, churn detection — + a face-quality-gate note |
| **MVP code** | [`../services/monolith/`](../services/monolith/) | The **built application** — all 10 modules, 6 migrations, tests, idempotent seed (`ruff`+`py_compile` clean; pending the Ubuntu/CI run) |

The existing `deep-dive/` (condensed developer docs) and `user-guides/` (end-user) remain; `mvp/` + `ffp/` are the
**fuller** canonical specifications. When they differ, the `mvp/`+`ffp/` sets are authoritative (see the refinement
note in §1).

---

## 4. Reading paths by role

Everyone starts with **00 → 01 → 02**. After that:

| Role | Then read |
|---|---|
| **Anyone wanting the whole journey** | **09 (the complete roadmap: Concept → MVP → FFP + build & learning path)** |
| **Anyone building the MVP (novice → mastery)** | **[`mvp/27-implementation-roadmap.md`](mvp/27-implementation-roadmap.md)** — the hands-on builder's roadmap (data foundation → API → code → tests → CI, module by module) |
| Leadership / sponsor | 09, then 08 (roadmap, big picture) |
| Business / domain expert | (01 is the core); 06 for UAT context |
| Architect | 03, 04, 05; 99 for decisions |
| Backend developer | 03, then 04, 06 |
| Frontend developer | 03 (repo/UI); 01 §5 for who the screens serve |
| Data / DB engineer | 04; 07 for backup/restore |
| GIS engineer | 04 (GIS section) |
| Security engineer | 05; 07 for audit/DR |
| QA / tester | 06; 02 for end-to-end flows |
| DevOps / SRE | 07; 06 for CI/CD |

Full role guidance lives in [`00-orientation.md`](00-orientation.md) and, in depth, in `08-organization.md`.

---

## 5. How we proceed

Documents are generated **in order (00 → 99)** so each builds on the last. Cadence: finish a phase, pause for
a quick review, then continue — locking tone and depth early to avoid rework.

- ☑ **Phase A — Orientation & Foundation** (`00`, `01`, `90`, `99`)
- ☑ **Phase B — Architecture** (`02`)
- ☑ **Phase C — Engineering & Data** (`03`, `04`)
- ☑ **Phase D — Security & Quality** (`05`, `06`)
- ☑ **Phase E — Operations** (`07`)
- ☑ **Phase F — Organization** (`08`)
- ☑ **Phase G1 — Developer docs:** complete — see [`deep-dive/00-plan.md`](deep-dive/00-plan.md). All in
  `docs/deep-dive/`, conformed to the posters and validated:
  [`13-data-model.md`](deep-dive/13-data-model.md) (Poster 22),
  [`12-api-spec.md`](deep-dive/12-api-spec.md) + [`openapi.yaml`](deep-dive/openapi.yaml) (OpenAPI 3.1),
  [`10-srs.md`](deep-dive/10-srs.md) (ISO/IEC/IEEE 29148),
  [`11-architecture-and-design.md`](deep-dive/11-architecture-and-design.md) (arc42 + C4 + IEEE 1016),
  [`14-traceability-matrix.md`](deep-dive/14-traceability-matrix.md).
- ☑ **Phase G2 — End-user guides:** complete — `docs/user-guides/` ([`00-overview.md`](user-guides/00-overview.md),
  citizen, responder, coordinator, administrator). Diátaxis-structured; conformed to Posters 8 & 7.
- ☑ **Phase G3 — Presentation:** complete — `presentation/IDRM-MVP.pptx` (45 slides, + PDF export). Hybrid
  audience, native poster-matched design, MVP-only content in the posters' suggested order; validated and
  visually QA'd.

**The entire documentation effort is complete** — the lean reader set (`00`–`08`, `90`, `99`), the G1
developer deep-dive, the G2 end-user guides, and the G3 presentation — all consistent with the posters.

---

## 6. Provenance

- **Authoritative source:** the **35 posters** (Phases 0–8) in [`../posters/`](../posters/) — see
  [`../posters/README.md`](../posters/README.md) for the phase-by-phase map and the ADR-012 refinement note.
- **Decisions & rationale:** recorded for maintainers in
  [`99-decisions-and-history.md`](99-decisions-and-history.md). The reader-facing documents (`00`–`08`) stay
  focused on the MVP and its future vision.
