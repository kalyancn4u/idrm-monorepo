# IDRM MVP — Documents

**MVP = Minimum Viable Product** (the lean first build — a Python/FastAPI modular monolith).

This folder holds the **MVP specifications & project detail**. Flat files, named
`<prefix>-<category>-<name>.md` (shared legend: `00` overview · `10` requirements · `20` architecture ·
`30` design · `40` api · `50` data · `60` uidesign · `70` quality · `80` ops · `90` project).

## Start here
- **[`27-implementation-roadmap.md`](27-implementation-roadmap.md)** — 🧭 **the builder's "start here"**: the Complete Implementation Roadmap (Concept → working code), written for a **complete novice → mastery**. Read this first — it orients every doc below and threads them into reading order.
- **[`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md)** — the plan: the **minimal set of documents** the MVP needs, in what order, with a generation brief for each.

## Suggested reading order (the logical flow)
New to IDRM? Read in this order — each layer builds on the one before (the *why* is in italics):
1. **Orient** → [`27-implementation-roadmap.md`](27-implementation-roadmap.md) — *the whole journey in plain language; sets the "building a house" metaphor and the five build habits.*
2. **What must it do?** → [`10`](10-requirements-prd.md) → [`11`](11-requirements-scope-and-acceptance.md) → [`12`](12-domain-capability-and-operating-model.md) — *requirements before design: you can't build what isn't specified.*
3. **What shape is it?** → [`20`](20-architecture-system.md) → [`21`](21-architecture-decisions.md) → [`25`](25-module-elucidation.md) — *the big picture and the reasons behind it, then each of the 10 modules in plain words.*
4. **The foundation** → [`50`](50-data-model.md) → [`40`](40-api-specification.md) → [`30`](30-design-data-flow-and-modules.md) — *data model first (everything rests on it), then the API over it, then the request path through the modules.*
5. **Cross-cutting** → [`22`](22-architecture-security-and-iam.md) → [`60`](60-uidesign-web-interaction.md) → [`70`](70-quality-test-strategy.md) → [`80`](80-ops-deployment-and-operations.md) → [`90`](90-governance-and-raci.md) — *security, the web UI, testing, running it, and who owns what.*
6. **Prove it's done** → [`13`](13-requirements-traceability-matrix.md) + [`26-conformance-pics.md`](26-conformance-pics.md) — *the audit spine and the signed-off conformance gate: the objective "is it finished?"*

> Brand-new to the concepts themselves? Each doc links to the matching **101 guide** in [`../../guides/mvp/learn/`](../../guides/mvp/learn/README.md) — start there when a topic is unfamiliar, then return here for how IDRM applies it.

## Specification set (every file below is clickable)
*Priority: 🔴 core · 🟠 supporting · 🟢 elucidation/conformance. "Answers" tells a newcomer **why** the doc exists.*

| File | Document — what it is & why it exists | Priority |
|---|---|---|
| [`10-requirements-prd.md`](10-requirements-prd.md) | **Product Requirements (PRD)** — the tech-free "what the MVP must do and why" | 🔴 |
| [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) | **Scope & Acceptance** — feature→requirement→acceptance→test; the incident lifecycle | 🔴 |
| [`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md) | **Domain, Capability & Operating Model** — the 10 capabilities + how disaster response actually runs | 🟠 *(T1)* |
| [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) | **Traceability & Compliance** — the audit spine (need→…→evidence) + standards mapping | 🟠 *(T1)* |
| [`20-architecture-system.md`](20-architecture-system.md) | **System Architecture** — the modular monolith, and *why* it's shaped that way | 🔴 |
| [`21-architecture-decisions.md`](21-architecture-decisions.md) | **Architecture Decisions (ADRs)** — each choice + the rationale (why NOT React/Redis/Docker yet) | 🟠 |
| [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) | **Security & IAM** — authn/authz, the role→operation matrix, audit, secrets | 🔴 |
| [`25-module-elucidation.md`](25-module-elucidation.md) | **Module Elucidation** — the *what / why / how* of each of the 10 modules, for a complete novice → mastery | 🟢 *(2026-08-16)* |
| [`26-conformance-pics.md`](26-conformance-pics.md) | **Conformance Checklist (PICS)** — the signed-off **build gate**: every obligation, its M/O/C rationale + evidence | 🟢 *(signed off 2026-08-16)* |
| [`27-implementation-roadmap.md`](27-implementation-roadmap.md) | **Complete Implementation Roadmap** — the novice→mastery **builder's guide** (Concept → working code): data foundation, API, code structure, concurrency, logging, design system, testing, CI, module-by-module plan | 🟢 *(2026-08-17, in progress)* |
| [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md) | **Data Flow & Module Specs** — the request path + the skeleton every module repeats | 🟠 *(T1)* |
| [`31-concurrency-and-thread-model.md`](31-concurrency-and-thread-model.md) | **Concurrency & Thread Model (LLD)** — worker/thread sizing vs CPU cores kept ≤ 70 %, as a formula anchored to 4 vCPU/16 GB; the deep-dive behind roadmap §6 | 🟢 *(2026-08-17)* |
| [`32-logging-and-diagnostics.md`](32-logging-and-diagnostics.md) | **Logging & Diagnostics (LLD)** — structured-JSON logs, the `request_id` thread, levels, DPDP redaction, retention; the deep-dive behind roadmap §7 | 🟢 *(2026-08-17)* |
| [`33-design-system.md`](33-design-system.md) | **Web Design System** — Tailwind v4 tokens, visual hierarchy, components + states, templates, the page-transition map, WCAG 2.2 AA; the deep-dive behind roadmap §9 | 🟢 *(2026-08-17)* |
| [`34-seed-data-and-fixtures.md`](34-seed-data-and-fixtures.md) | **Seed Data & Fixtures** — the row-by-row starter dataset (4 personas + extras, orgs/resources, incidents in all 8 states incl. a guest, + alerts/notifications/files/audit); companion to `code/scripts/seed.py`; the deep-dive behind roadmap §3.4 | 🟢 *(2026-08-17)* |
| [`40-api-specification.md`](40-api-specification.md) (+ [`40-api-openapi.yaml`](40-api-openapi.yaml)) | **API & OpenAPI** — the frozen `/api/v1` contract | 🔴 |
| [`50-data-model.md`](50-data-model.md) | **Data & Database Design** — PostgreSQL + PostGIS tables, enums, migrations | 🔴 |
| [`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md) | **UI / Web Interaction** — screens, forms, maps; WCAG 2.2 AA | 🟠 |
| [`70-quality-test-strategy.md`](70-quality-test-strategy.md) | **Test Strategy** — unit/API/integration via pytest; ≥80% | 🔴 |
| [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md) | **Deployment & Operations** — native Ubuntu/systemd install, backup, DR | 🟠 |
| [`90-governance-and-raci.md`](90-governance-and-raci.md) | **Governance & RACI** — one Accountable owner per capability + decision governance | 🟠 *(T1)* |

> The **Developer / Contributor Guide** is a novice guide, so it lives in the sibling guides library:
> [`30-contribute-developer-guide.md`](../../guides/mvp/30-contribute-developer-guide.md).

Generation prompts (CO-STAR) live in [`prompts/`](prompts/); the current authoritative MVP docs are in the top-level [`../../docs/`](../../docs/). See [`../INDEX.md`](../../archive/INDEX.md) for the full archive map.
