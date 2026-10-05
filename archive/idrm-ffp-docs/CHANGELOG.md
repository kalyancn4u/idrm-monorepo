# Changelog — IDRM FFP Documents

All notable changes to the IDRM FFP documentation set (`idrm-ffp-docs/`) are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with date-based releases.

The FFP set **mirrors the MVP set 1:1** (+ one Messaging & Async doc). Each FFP doc is written as a
**delta on its MVP counterpart** — it states what the FFP *adds* and cross-links the MVP doc for the shared
foundation, rather than duplicating it. Direction is fixed by the
[charter](prompts/instructions_idrm_ffp_docs.md); per-doc sources by the
[consolidation checklist](prompts/ffp-consolidation-checklist.md).

## [Unreleased]

### Added — 2026-08-16 (module elucidation + conformance PICS — FFP deltas, synced from base)
- **`25-module-elucidation.md`** — FFP delta on `../idrm-mvp-docs/25`: per module, what changes and on what
  **trigger** (contract-preserving), rationale-forward.
- **`26-conformance-pics.md`** — FFP delta PICS: the *added*, trigger-gated conformance rows (32 rows), **user-signed-off**
  alongside the MVP sheet. Twin of doc 25.
- Built in the base (`../../docs/ffp/`) during the PICS program and now **replicated here (links rewritten to the
  archive layout)** to keep base ↔ archive in sync. Full detail in `../../docs/ffp/CHANGELOG.md`.

### Added — 2026-08-14 (T1 doc-gaps — FFP deltas; T1 complete)
- Added the FFP-side T1 deltas as **thin deltas** on the new MVP T1 docs (not copies):
  - **`12-domain-capability-and-operating-model.md`** — capability **depth** MVP→FFP (AI matching, live national
    COP, multi-channel comms, OIDC/MFA/ABAC/Auditor, financial capability) + operating-model deepening
    (Prepare/Recover).
  - **`13-requirements-traceability-matrix.md`** — the FFP audit spine: **added columns** (release, service,
    operational evidence, trigger, compliance control) + **added rows** for the deferred capabilities + the T3
    standards mapping (ISO 22320, NIST CSF 2.0, 800-63-4, WCAG 2.2, DPDP).
  - **`90-governance-and-raci.md`** — **per-service ownership** (one Accountable owner per extracted service),
    the **Auditor** role, on-call/SRE rotations, and contract-governance.
- **Event-model delta deliberately NOT duplicated** — it already lives in `81-ops-messaging-and-async.md` §3
  (outbox, idempotent consumers, versioned events, DLQ, projections). Per the *cross-link, don't duplicate*
  guardrail, no FFP `30` was created; the MVP `30`'s FFP branch points to `81`. **This completes blueprint T1.**

### Added — 2026-08-14 (FFP guides — learning hub; T2 complete)
- **`idrm-ffp-guides/00-start-ffp-learning-paths.md`** — the FFP learning hub, written as a **DELTA** (not a copy)
  on the MVP guides. Rationale: the 39 topic-101s + 12 role-mastery guides live once in `idrm-mvp-guides/` and are
  already phase-tagged, so duplicating them into the FFP folder would create a second source of truth (violating
  the *cross-link, don't duplicate* guardrail). The hub instead provides: the "what FFP adds" delta table (same
  `/api/v1` contract, evolved on triggers), the FFP reading path through the shared 101s, per-role FFP deltas, and
  links to the FFP spec docs. FFP guides README updated. **This completes blueprint T2 (guides).**

### Changed — 2026-08-14 (domain quick-ref → elucidated spoke)
- Moved the hub's Domain Quick-Reference (§8) into a new spoke `archive/instructions/domain.md`, rewritten as an
  **elucidated ground-truth card** — each element (modules, module shape, roles, the incident + 8-state
  lifecycle, enums, personas, Q4-2026 success targets) now carries the **rationale / "why"** so a complete
  novice can use IDRM's real vocabulary correctly. The hub keeps a **3-line digest** + pointer (option 1).
  (11 spokes total now.)

### Changed — 2026-08-14 (instructions refactor: hub-and-spoke)
- Split the growing `instructions.txt` into a **lean hub + 10 topic spokes** under `archive/instructions/`
  (`ui`, `api-gateway`, `apis`, `data-stores`, `data-modeling`, `security`, `observability`,
  `caching-messaging`, `backend-services`, `backup-and-dr`, + `00-README` index). The verbose §4A FFP map was
  collapsed into a **routing table**; its detail moved into the relevant spokes. Spokes are **thin routers**
  (phase-scoped decisions + pointers into the canonical docs + vetted external refs), so there is **no content
  duplication / drift** — when a fact changes, update hub digest + spoke + canonical doc + this CHANGELOG.

### Decided — 2026-08-14 (API gateway: APISIX vs Kong evaluation)
- **Evaluated Kong Gateway as the alternative to Apache APISIX** at the user's request, focusing on the
  **free/open-source** editions (IDRM is on-prem, cost-sensitive). **APISIX retained.** Rationale: in their OSS
  editions APISIX ships **OIDC (`openid-connect`), OAuth2.1/PKCE via an IdP, WAF/OWASP-CRS (`coraza-waf`),
  advanced rate-limiting, request validation, and admin RBAC as free plugins**, whereas Kong OSS gates several
  of these (notably OIDC and the WAF) behind **Kong Enterprise (paid)**. IDRM needs OIDC + OAuth2.1+PKCE +
  OWASP mitigation on a free self-hosted stack → APISIX wins on cost-to-capability. Kong remains valid **iff**
  Kong Enterprise is purchased or the team prefers its ecosystem — that would be a new decision, not a silent swap.
- Captured a **FFP high-level architecture reference map** (clients, gateway responsibilities, API types &
  integrations, health checks, data/caching/messaging, observability) in `instructions.txt` **Section 4A**.

### Added — 2026-08-14 (FFP frontend engineering specification)
- **`61-frontend-engineering-standards.md`** — new companion to `60-uidesign-frontend.md`. Expands a user-
  provided "React Application Engineering Specification" (only Core Principles + Tech Stack were captured) into
  a full, **IDRM-grounded** 20-section standard for the FFP React web + React Native clients: engineering
  principles, tech stack, feature-first folder structure, state classification, `/api/v1` contract mapping,
  TypeScript `strict`, forms (RHF+Zod), auth/RBAC (RS256 JWT, roles+guest), frontend security + DPDP/EXIF media
  rules, WCAG 2.2 AA, i18n, real-time/offline-first, React-Leaflet maps, error handling, testing gates,
  performance/Core Web Vitals, observability, tooling, and a Definition of Done.
- **Decided:** the React spec is **FFP-scoped**. The MVP web UI stays **HTML + Tailwind + JS + Leaflet**
  (no React/Bun) per the locked decision; forcing React on the MVP was explicitly rejected. Cross-linked from
  `60-uidesign-frontend.md`.

### Added — 2026-08-12 (FFP documentation set — 12/12 written)
- **`10-requirements-prd.md`** — enterprise PRD extending the MVP PRD (national scale, multi-agency,
  SLAs, the deferred capabilities as FFP requirements).
- **`11-requirements-scope-and-roadmap.md`** — phased evolution (MVP → Scale → Multi-Agency → Federation →
  Decision-Support → Enterprise) with a **concrete trigger per capability**.
- **`20-architecture-system.md`** — selective-microservices architecture (from the CO-STAR prompt):
  extraction pattern, **APISIX** gateway + plugins, Bun/Node/Deno edge behind it, polyglot runtimes,
  React/RN clients on the same contract, per-service data, messaging, Docker→K8s, migration roadmap.
- **`21-architecture-decisions.md`** — FFP ADRs, each naming a **concrete trigger** (extract-auth-first,
  APISIX, edge runtimes, polyglot, Redis/Streams, brokers, containers/orchestration, React/RN, per-service
  data, observability, secrets vault, OIDC/MFA/ABAC, disaster/financial modules, biometric).
- **`22-architecture-security-and-iam.md`** — enterprise IAM: OIDC/SSO, OAuth 2.1+PKCE, MFA, ABAC,
  zero-trust, gateway auth, secrets vault/KMS, at-rest AES-256, full role hierarchy + Auditor, biometric consent.
- **`40-api-specification.md`** — **same public `/api/v1` contract**; gateway routing + inter-service
  (sync + event) contracts; the FFP-added resources (`/disasters`, `/financial`, realtime) at stable paths.
- **`50-data-model.md`** — per-service data ownership; the deferred MVP tables realised; replication,
  projections, eventual consistency.
- **`60-uidesign-frontend.md`** — React web SPA + React Native/Expo mobile on the same API; offline-first; push.
- **`70-quality-test-strategy.md`** — contract testing, heavy E2E, performance/load, DAST, chaos/resilience, full DORA.
- **`80-ops-platform-and-deployment.md`** — Docker → Swarm/Kubernetes, CI/CD, full observability stack, HA, AWS variant.
- **`81-ops-messaging-and-async.md`** *(FFP-only)* — Redis Streams → RabbitMQ/Kafka, workers/queues, deep push, DLQ/idempotency.
- **`idrm-ffp-guides/30-contribute-developer-guide.md`** — contributing across services.

### Decided — 2026-08-12
- Every FFP technology enters via an **ADR naming a concrete trigger** (never "because enterprise"); the
  **public API contract and module boundaries are preserved** (evolution, not rewrite); **incremental
  extraction**, least-coupled module first (auth). PostgreSQL/PostGIS stays the system of record.

### Changed — 2026-08-12 (v2 deep-merge into the FFP docs)
- Before retiring v2, folded its concrete specifics into the FFP set: **FFP-03 §6.1/6.2** gained a
  **representative service decomposition** (auth · service-mgmt · geospatial · analytics · notifications)
  and a **Python geospatial service** (GeoPandas/Shapely, WMS/WFS-like endpoints — not Java GeoServer),
  reframed from v2's NGINX+Bun gateway to **APISIX**; **FFP-02 §4.1** gained v2's **migration checklists**
  (splitting a service / adding real-time / moving to cloud). v2's decisions (DR-001–006) and JSON formats
  were already covered by the MVP/FFP ADRs + canonical API.

### Changed — 2026-08-12 (v3 deep-merge into the FFP docs)
- Before retiring v3 (the primary FFP source), folded its additive spec into **FFP-02 §4.1**: the
  **Strangler Fig pattern** (the standard name for our incremental extraction), per-extraction **success
  metrics**, and the optional-service-mesh note (from `v3/92-migration`). v3's decisions (22), API (40),
  data (50/51), design (23/60/32), and ops (80/81/82) were already covered by the MVP/FFP docs. Its
  **beginner tutorials** (`81-redis`, `31-backend`, `82-api-gateway`, `70-testing`, `71-code-standards`) are
  **guide-source for the pending T2 guides** — not spec merges.

### Removed — 2026-08-12 (generation retirement: v3, then v0 — ALL generations retired ✅)
- **`idrm-docs-v3` retired → `../_removed/idrm-docs-v3/`** after the deep-merge above + verification. Overview
  + LLD already in `analyses/`; **`91-roadmap` → `analyses/v3-91-…`**.
- **`idrm-docs-v0` retired → `../_removed/idrm-docs-v0/`** — final generation. Verified: PRDs → MVP;
  architecture/devops (superseded by v2/v3 already merged) → FFP-03/10; **API/data (40/50/51) are already the
  live `assets/*.xlsx`**; overviews/LLDs/meta already in `analyses/`. No unique content lost.
- **Generation consolidation COMPLETE:** all four (v0–v3) retired to `_removed/` (reversible). Provenance
  paths in the FFP + MVP docs converted to plain labels; charter §3, checklist, INDEX all updated so nothing
  depends on `_removed/`.

### Removed — 2026-08-12 (generation retirement: v1, v2)
- **`idrm-docs-v1` retired → `../_removed/idrm-docs-v1/`** (transitional, most-duplicated; all content
  superseded by MVP + FFP docs).
- **`idrm-docs-v2` retired → `../_removed/idrm-docs-v2/`** after the deep-merge above + verification (PRD/
  functional-spec/monolith/web → MVP; UI superseded by v3; decisions/formats → ADRs/API). Its overview + LLD
  had already gone to `analyses/`; **`90-roadmap` → `analyses/v2-90-…`**. v2 provenance paths in the FFP docs
  converted to plain labels; charter §3, checklist, INDEX updated so nothing depends on `_removed/`. Reversible.

### Planned (follow-ups)
- **Verify + retire `idrm-docs-v3`** (last — primary source) per the
  [checklist](prompts/ffp-consolidation-checklist.md) Part D; deep-merge remaining v3 detail first, then
  move (with `v3/91-roadmap` → `analyses/`). Finish v0's split. Optional CO-STAR prompts per doc in `prompts/`.
