# Changelog — IDRM MVP Documents

All notable changes to the IDRM MVP documentation set (`idrm-mvp-docs/`) are recorded here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) with date-based releases.

## [Unreleased]

### Fixed — 2026-08-22 (incidents `q` wording — matches the implemented full-text search)
- **`40-api-openapi.yaml`** — `GET /incidents` `q` description "over title/description" → "over the
  description (PostgreSQL full-text)" (+ `maxLength: 100`); incidents have no title column. Accompanies the
  F5-B code change implementing `priority`/`q`/`sort` on the incidents list. Synced from base (C3; YAML
  byte-identical).

### Fixed — 2026-08-22 (Query-parameter drift, part 2 — audit-logs & locations/nearby)
- **`40-api-openapi.yaml`** — continued *contract-catches-up-to-code* (F5 Kind A; additive/rename, no runtime
  change): `GET /audit-logs` now documents the code's **`resource_type`**/**`resource_id`**/**`action`**
  filters; `GET /locations/nearby` replaced the stale **`type`** param with the code's real **`layer`**
  (`all|incidents|providers`). Synced from base (C3; YAML byte-identical). *F5 Kind B (`/incidents`
  priority/q/sort) remains deferred (board §17).*

### Fixed — 2026-08-22 (Query-parameter drift — OpenAPI catches up to the code's real filters)
- **`40-api-openapi.yaml`** — reconciled list-endpoint query parameters with what the code actually accepts
  (decision: *contract catches up to code*; additive, no runtime change): `GET /notifications` filter
  `read` → **`unread_only`**; `GET /organizations` gained **`verified_only`** + optional proximity
  (**`latitude`**/**`longitude`**/**`radius_km`**). Synced from base (C3; YAML byte-identical). *Residual
  drift (`/incidents` priority/q/sort; `/audit-logs` resource filters; `/locations/nearby` layer) is logged
  as F5 in `instructions.txt` §17, pending a decision.*

### Fixed — 2026-08-22 (API contract catches up to the shipped chat endpoint — code↔docs coherence)
- **`40-api-specification.md` + `40-api-openapi.yaml`** — documented **`POST /notifications/chat`**, the Task-L
  FAQ-chatbot stub. It shipped in the code (Increment 10) and had a PICS row (`PICS-NTF-004`), but was **missing
  from the API contract** — a real code↔docs gap surfaced by the Session-6 coherence audit. Added: the §5.5 table
  row + a note (request `{message}` 1–2000 chars; the fixed acknowledgement reply; auth-required; `422` on empty),
  and the `/notifications/chat` path in the OpenAPI. Synced from base (C3 parity; YAML byte-identical, Markdown
  prose-identical). Every code route now matches the OpenAPI contract.

### Added — 2026-08-17 (Doc 34 — Seed Data & Fixtures — synced from base)
- **`34-seed-data-and-fixtures.md`** — the row-by-row starter dataset deep-dive (roadmap §3.4): 8 users + guest,
  3 orgs + 4 resources, incidents in all 8 lifecycle states + timelines, alerts/notifications/files/audit; the
  companion to `code/scripts/seed.py`; idempotent `make seed`; fixtures-vs-seed (Task N). Byte-identical to
  `docs/mvp/34` (layout-independent links). Registered in the README; roadmap §3.4 link updated.

### Added — 2026-08-17 (PICS row for the Task-L FAQ chatbot stub — synced from base)
- **`26-conformance-pics.md`** — added **`PICS-NTF-004`** (FAQ chatbot stub: fixed acknowledgement; Optional;
  real NLP → FFP), status `Planned`, as the Task-L chatbot endpoint landed in the code build (Increment 10).
  Kept in parity with `docs/mvp/26` (C3).

### Decided — 2026-08-17 (Data-foundation §3.6 SIGN-OFF — the coding gate is cleared — synced from base)
- **User signed off all five data-foundation items** (roadmap §3.6): data model & 13-table schema + enums;
  indexes + logic-in-service/minimal-DB-views; the rich seed dataset spec; and the five user journeys. **`27` §3.6
  stamped "SIGNED OFF 2026-08-17".** Task G (build the MVP code) is now fully unblocked — next is the concrete
  module-by-module build order (USR/auth first) for user confirmation.

### Added — 2026-08-17 (Roadmap §15 + COMPLETE DRAFT — What's deferred to FFP — synced from base)
- **`27-implementation-roadmap.md` §15 "What's deferred to FFP (and why)"** — one categorised table of every → FFP
  deferral with the why + the MVP seam; the chatbot line (Task-L stub / Task-M papers); and the closing gate
  reminder. ***COMPLETE IMPLEMENTATION ROADMAP — FULL DRAFT DONE (§0–§15)*** with sub-docs 31/32/33. Mirror of
  base; parity OK; full link pass = 5 known-accepted legacy only.

### Added — 2026-08-17 (Roadmap §14 — Definition of Done + conformance — synced from base)
- **`27-implementation-roadmap.md` §14 "Definition of Done + conformance"** — "done" as an explicit checklist at
  three levels (feature/module/MVP), the per-change code DoD checklist, docs held to the Definition-of-Documentation-
  Done, and the auditable finish line. Ties doc 26/11/90 + instructions/definition-of-done. Mirror of base; 96
  links, 0 broken.

### Added — 2026-08-17 (Roadmap §13 — Module-by-module build plan — synced from base)
- **`27-implementation-roadmap.md` §13 "Module-by-module build plan"** — the data-foundation gate restated, the
  universal 10-step module recipe, the dependency-justified build order (USR → INC → ORG/RES → LOC → ALR/NTF →
  RPT → ADM; AUD/FIL cross-cutting), two worked modules (USR, INC), a compact table for the rest (+ Task L chatbot
  stub, Task K docstrings), and the per-module finish line. Grounds in docs 25/40/50/22/26. Mirror of base; 91
  links, 0 broken.

### Added — 2026-08-17 (Roadmap §12 — CI pipeline — synced from base)
- **`27-implementation-roadmap.md` §12 "CI pipeline"** — what CI is, the minimal MVP GitHub Actions pipeline
  (Postgres+PostGIS + MinIO services → make install/migrate/lint/typecheck/coverage + pip-audit) with a full worked
  `ci.yml`, branch protection enforcing the DoD, and the FFP seam (CD/containers/K8s/DAST/DORA). Reuses §11 make
  targets. Mirror of base; 81 links, 0 broken.

### Added — 2026-08-17 (Roadmap §11 — Build & run automation — synced from base)
- **`27-implementation-roadmap.md` §11 "Build & run automation"** — orients to doc 80: the native-Ubuntu platform
  recap, the full generic **Makefile** (setup/install/migrate/seed/run/format/lint/typecheck/test*/coverage/qa/
  clean/help) with real commands, and the everyday flows (bring-up, `make qa` pre-PR gate, server deploy) shared
  with CI. Mirror of base; 80 links, 0 broken.

### Added — 2026-08-17 (Roadmap §10 — Quality & test automation — synced from base)
- **`27-implementation-roadmap.md` §10 "Quality & test automation"** — orients to doc 70: the testing pyramid
  (UT/API/IT/system) with a novice translation, per-module independent tests (Task N) + fixtures, the hard-part
  suites (fallback/negative, RBAC/lockout/rate-limit, no-PII, a11y), and the quality gates (Black/Ruff/mypy/
  docstrings/tests/coverage ≥ 80 %/security) as make+CI checks; FFP = perf/DAST/DORA/contract. Mirror of base;
  77 links, 0 broken.

### Added — 2026-08-17 (Roadmap §9 + new sub-doc 33 — Web layer & design system — synced from base)
- **`33-design-system.md`** (NEW deep-dive) — the full MVP web design system: `@theme` design tokens
  (accessibility-checked palette; locked priority colours), visual-hierarchy rules, a component catalogue with
  states + WCAG 2.2 AA a11y, app-shell templates, a page-transition map, low-bandwidth/motion posture, a11y
  checklist, implementation + verification, and the FFP seam. **`27` §9** = concise hub orientation linking to `33`.
  Listed in the README spec table. Mirror of base (link prefixes per §13, incl. `../ffp/ → ../idrm-ffp-docs/`);
  71 + 13 links, 0 broken; parity OK.

### Added — 2026-08-17 (Roadmap §8 — Security in practice — synced from base)
- **`27-implementation-roadmap.md` §8 "Security in practice"** — orients to doc 22: auth (RS256 JWT, bcrypt-12,
  NIST passwords), sessions-in-Postgres + safe cookies (HttpOnly/Secure/SameSite/CSP/HSTS/CORS), lockout +
  rate-limits, the MVP's static allow/deny-lists table + the FFP line (AD-driven lists = Task M), two-layer RBAC
  enforcement + guest path, data protection/secrets/audit, testing + FFP seam. Mirror of base; 69 links, 0 broken.

### Added — 2026-08-17 (Roadmap §7 + new sub-doc 32 — Logging & diagnostics — synced from base)
- **`32-logging-and-diagnostics.md`** (NEW deep-dive) — logs-vs-audit distinction, structured-JSON lines + the
  elements-of-circumstance fields, levels, the `request_id` correlation thread, per-layer logging + never-log list,
  DPDP redaction (secrets/PII/EXIF), MVP destinations/retention (journald + logrotate; no aggregation), the
  diagnosis workflow, verification tests, and the FFP seam. **`27` §7** = concise hub orientation linking to `32`.
  Listed in the README spec table. Mirror of base; 60 + 19 links, 0 broken; parity OK.

### Added — 2026-08-17 (Roadmap §6 + new sub-doc 31 — Concurrency & thread LLD — synced from base)
- **`31-concurrency-and-thread-model.md`** (NEW deep-dive) — FastAPI's three tiers, the full workload
  classification, the single-box co-tenancy reality, and a **parameterized formula anchored to 4 vCPU/16 GB**
  (≤ 70 % CPU): workers, CPU-bound limit, background + DB pools; worked examples at 4/8 vCPU; load-test plan; the
  FFP seam. Chatbot/ML reserve zero threads. **`27` §6** = concise hub orientation linking to `31`. Listed in the
  README spec table. Mirror of base; 56 + 18 links, 0 broken; parity OK.

### Added — 2026-08-17 (Roadmap §5 — Code structure — synced from base)
- **`27-implementation-roadmap.md` §5 "Code structure"** — the FFP-extensible repo layout, the per-module 5-file
  inward-only skeleton + request path, cross-cutting `core/` (DRY), docstrings & naming (Task K) with a worked
  example, and independent testability (Task N) + the Strangler-Fig module→microservice seam. Grounds in docs
  20/30/25/21. Mirror of base; 54 links, 0 broken.

### Added — 2026-08-17 (Roadmap §4 — The API layer — synced from base)
- **`27-implementation-roadmap.md` §4 "The API layer"** — REST in novice terms, the frozen `/api/v1` conventions,
  the 12-resource URI map, the lifecycle-as-dedicated-endpoints pattern (single-claim/assigned-only), a worked
  example, and a synthesised **fallback-behaviour** table (validation, refresh, 429, 409, notification retry,
  emergency-lite, 500/503) tied to the life-safety principle + API tests. Orients to doc 40. Mirror of base;
  46 links, 0 broken.

### Added — 2026-08-17 (Roadmap §3 — The Data Foundation — synced from base)
- **`27-implementation-roadmap.md` §3 "The Data Foundation"** — the gate before coding: data modeling (3 levels
  + terms), the 13-table schema + enums (orient + link `50`), indexes & the logic-in-service/DB-views-minimal
  stance, the rich seed-data spec (4 personas, all 8 lifecycle states, TG/AP coords, idempotent load), the five
  user journeys with checklists, and the data-foundation sign-off checklist. Mirror of base (link prefixes per
  §13); 37 links, 0 broken.

### Added — 2026-08-17 (Complete Implementation Roadmap — front matter; reading-flow wiring — synced from base)
- **`27-implementation-roadmap.md`** (NEW, in progress) — the novice→mastery **builder's roadmap** (Concept →
  working code): the HUB that orchestrates the whole MVP build. Front matter drafted (§0 how-to-read + house
  metaphor · §1 big picture · §2 the five build habits); §§3–15 + deep-dive sub-docs to follow, section-by-section.
  Mirror of the base doc (link prefixes per §13); links verified (0 broken).
- **Reading-flow wiring** — added a **"Suggested reading order (the logical flow)"** section to `README.md` with
  the *why* per step; listed doc 27 in the spec table + "Start here"; 25/26 footers point back to 27.
- Provenance: new pending tasks recorded in `../instructions.txt` §15 — **Task J** (this roadmap), **Task K**
  (code docstrings from day one), **Task L** (FAQ-chatbot stub template), **Task M** (technical white papers:
  chatbot, two anomaly-detection engines, two recommendation systems, churn detection — engines → FFP).

### Added — 2026-08-16 (module elucidation + conformance PICS + sign-off — synced from base)
- **`25-module-elucidation.md`** — the *what/why/how* of each of the 10 monolith modules (module companion to the
  component map `../idrm-mvp-guides/learn/tech-stack-101.md`). Novice → mastery, rationale-forward.
- **`26-conformance-pics.md`** — a **PICS-style conformance checklist** (65 rows: 10 modules + stack; item · M/O/C ·
  phase · supported · evidence · src). Reviewed, gap-closed (added WCAG 2.2 AA, TLS, secrets, guest, role-scoped
  read, health) and **USER-SIGNED-OFF** as the build gate before the MVP code. Twin of doc 25.
- Both were built in the base (`../../docs/mvp/`) during the `_removed` cleanup + PICS program and are now
  **replicated here (links rewritten to the archive layout)** to keep base ↔ archive in sync. Full detail in
  `../../docs/mvp/CHANGELOG.md`. Also synced: `../idrm-mvp-guides/learn/tech-stack-101.md` (#40 component map).

### Changed — 2026-08-16 (9-F — Bun stripped from the setup script; ADR-014 RESOLVED)
- Made [`../scripts/setup-idrm-ubuntu.sh`](../scripts/setup-idrm-ubuntu.sh) a **pure-MVP installer** by
  removing all **Bun** (an FFP technology). Chose **option (a)** from ADR-014. Removed: the Bun install/verify
  step + PATH edits; the generated README's `Frontend: Bun` line and `bun run dev` commands; `dev-start.sh`'s
  separate `:3000` frontend terminal; the `oven.bun-vscode` editor recommendation; the `Bun/Node` `.gitignore`
  block. **Retitled the frontend** as static assets served by FastAPI (`frontend/templates` +
  `frontend/static/{css,js,img}`, no JS build step); renumbered the install steps to **1–13**; `bash -n` clean.
- **MinIO in the same script stays** (legitimate MVP, ADR-007). Marked **ADR-014 RESOLVED** in
  `21-architecture-decisions.md` and updated the deployment note in `80-ops-deployment-and-operations.md`.
  With this, hand-off **§9-F is done** — only §9-G (build the MVP code) remains.

### Changed — 2026-08-16 (T5 — base replication + stack reconciliation, COMPLETE)
- **Replicated** the finalized archive sets to the base ("sit beside", user decision): `docs/mvp/` (15 MVP specs),
  `docs/ffp/` (15 FFP specs), `guides/mvp/` + `guides/ffp/` (the 39 101s + 12 role guides + hubs). **986
  cross-links rewritten and verified — 0 broken** (intra-replica links stay in base; links to archive-only working
  files point back to `archive/`). `docs/README` routed to the new layers.
- **Conflict surfaced + resolved:** the base overview was poster-faithful (**Flask+Jinja+Bootstrap, Redis-optional**)
  but the archive MVP is **HTML+Tailwind+JS+Leaflet, no Redis, +MinIO**. User decided **"archive wins — update
  base."** Recorded as **ADR-012** in `docs/99-decisions-and-history.md` (supersedes ADR-002/003/006). Posters
  are empty in this workspace → the authoritative posters must be updated elsewhere (flagged in ADR-012 + README).
- **Reconciled:** `docs/README`, `02-architecture`, `03-engineering`, `04-data`, `06-quality`, `07-operations`,
  `08-organization`, `90-glossary`, `99` (ADR-012 + superseded markers on ADR-002/003/006). `98-review` needed
  no change (its MinIO notes already align).
- **Completed 2026-08-16:** added the ADR-012 **supersession banner** (right after the H1) to the five
  `docs/deep-dive/` files that still mention Flask/Jinja/Bootstrap/Redis — `10-srs.md`,
  `11-architecture-and-design.md`, `13-data-model.md`, `14-traceability-matrix.md`, `15-ops-runbook.md` —
  pointing readers to `../mvp/` and `../99-decisions-and-history.md`. **This completes T5, and with it the
  whole blueprint T1–T5.** (Posters remain empty in this workspace → the authoritative posters must still be
  updated elsewhere, as flagged in ADR-012.)

### Changed — 2026-08-14 (T3 — standards alignment)
- Folded the named standards into the docs "where relevant," centred on one **compliance-mapping table** in
  **`13-requirements-traceability-matrix.md` §4** (Standard → what it requires → where addressed → owner → phase):
  **ISO 22320** + **ICS** (with a note that IDRM runs on India's **NDMA / DM Act 2005**; **NIMS** cited only as
  the US analog for structure), **NIST CSF 2.0**, **NIST SP 800-63-4 / 63B-4**, **WCAG 2.2 AA**, **DPDP Act 2023**.
- **Decided (WCAG):** raised the MVP accessibility target **2.1 AA → 2.2 AA**, so both phases share 2.2 AA. Updated
  `60-uidesign-web-interaction.md`, `22-…security` (§ standards), `90-governance`, the `ui` spoke, and the
  accessibility-testing + frontend-engineer guides. `12-…operating-model.md` gained an ISO 22320 / ICS alignment
  section; `22` now names NIST CSF 2.0 + 800-63-4. (Historical `_removed/`, `analyses/`, `idrm-ffp-code/` left
  untouched.) **Completes blueprint T3.**

### Added — 2026-08-14 (T4 — Definition of Done adopted)
- Adopted the blueprint's "Definition of Documentation Done" (§32) as
  **`../instructions/definition-of-done.md`** — the 14 criteria (purpose/scope/owner/inputs/outputs/deps/
  terminology/diagrams/traceability/security/accessibility/ops/tests/version/review) **plus IDRM conventions**
  (the header line, phase-honest MVP-vs-FFP, cross-link-don't-duplicate, dated CHANGELOG, and the guides
  quality bar) **plus a copy-paste checklist**. Wired into the workflow (`../instructions.txt` §7 step 6), the
  spokes index, and both governance docs (MVP + FFP `90` §3). Existing sets broadly already satisfy it; it is
  now the go-forward finalization gate. **Completes blueprint T4.**

### Added — 2026-08-14 (T1 doc-gaps — 4 new MVP technical docs)
- Closed the genuine blueprint-T1 gaps (per §5/§8/§10-11/§21/§22), after a gap analysis confirmed each was NOT
  already covered (existing docs had only *per-doc* traceability, no cross-doc spine; no domain/capability,
  data-flow, module-spec, or governance doc):
  - **`12-domain-capability-and-operating-model.md`** — the 10 business capabilities + the disaster operating
    model (Prepare→…→Learn; MVP focus Detect→Assess→Respond→Coordinate→Stabilize), each mapped to modules/lifecycle.
  - **`13-requirements-traceability-matrix.md`** — the **audit spine**: consolidates the scattered per-doc
    traceability into one Feature→Capability→Design/ADR→API→Data→Test matrix + security-control + compliance rows.
  - **`30-design-data-flow-and-modules.md`** — the design layer: canonical data path (MVP **synchronous**; event
    bus shown as a dashed **FFP** seam), packet/API sequence, cross-cutting mechanisms, and the standard **module
    spec template** (incidents + IAM filled as worked examples).
  - **`90-governance-and-raci.md`** — ownership: "every capability has exactly one Accountable owner" + the RACI
    matrix + decision governance.
- MVP doc set is now **15** (11 core + these 4). Observability was **correctly excluded** (FFP-deferred). FFP T1
  deltas (event model, per-service ownership, expanded governance) are the agreed **next** step. README updated.

### Added — 2026-08-14 (T2 guides — started: framework + first 101)
- **`idrm-mvp-guides/00-start-learning-paths.md`** — the guides learning hub from blueprint §24–30: the universal
  role-mastery ladder, the one shared operational flow, the new-joinee reading path + reading pyramid, a table of
  the 12 role mastery-tests, and the full **39-guide catalogue** (bold = MVP-relevant now).
- **`idrm-mvp-guides/learn/disaster-management-101.md`** — the **first 101 guide**, written as the exemplar/template
  for the novice→mastery quality bar (hazard vs disaster, the lifecycle, ICS/EOC/COP, India's NDMA/SDMA/DDMA/NDRF,
  and how each maps to IDRM). Plus `learn/README.md` (library index).
- MVP guides README updated (was "empty scaffolding"). Remaining 38 guides + 12 role guides + FFP mirror pending
  (`instructions.txt` §9-A); file scheme `learn/<name>-101.md` proposed, awaiting user confirmation.

### Added — 2026-08-14 (T2 guides — role-mastery guides COMPLETE 12/12)
- Wrote the final role guides: **`roles/data-engineer.md`** (clean constrained operational + spatial model in the
  MVP; ETL/events/lineage/analytics phase-tagged FFP; PostGIS stays source of truth), **`roles/incident-ops-
  manager.md`** (the non-technical coordinator/admin journey: assess → command → task → allocate → close →
  after-action, mapped to the domain guides), **`roles/technical-support.md`** (system-literacy triage: logs/
  dashboards → runbooks → escalation → RCA; incident-vs-problem, the help-request/incident naming bridges).
- **MILESTONE: all 12 role-mastery guides COMPLETE** in `idrm-mvp-guides/roles/`. Combined with the 39/39 101
  library, **T2's guide-building is essentially done** — only an optional FFP-guides mirror remains. Four blueprint
  §25 corrections were applied and flagged in-guide (frontend React→FFP, GIS GeoServer→PostGIS, DevOps containers→
  FFP, data-eng ETL/analytics→FFP).

### Added — 2026-08-14 (T2 guides — role-mastery guides, batch 3: QA/Security/DevOps)
- Wrote **`roles/qa-sdet.md`** (requirements → unit/API/E2E → security/perf/resilience/disaster-drills; the
  IDRM-specific things QA proves — lifecycle, RBAC, contract, a11y, surge), **`roles/security-engineer.md`**
  (networking → IAM → OIDC/OAuth/MFA → threat modeling → response; DPDP privacy, API-as-boundary; MVP RBAC vs
  FFP OIDC/ABAC), **`roles/devops-sre.md`** (**MVP native systemd — containers/CI-CD/K8s phase-tagged FFP**,
  corrected the blueprint's container-first map; observability → SLOs → incident response → backup/DR).
  Role guides now **9/12**. Remaining 3: Data Engineer, Incident/Ops Manager, Technical Support.

### Added — 2026-08-14 (T2 guides — role-mastery guides, batch 2: engineers)
- Wrote the engineer role guides (6/12 now): **`roles/backend-engineer.md`** (module end-to-end: contract →
  domain → data/transactions → auth → tests → observability; the layering/lifecycle/Alembic rules),
  **`roles/frontend-engineer.md`** (**MVP = HTML/Tailwind/JS + Leaflet, React/TS phase-tagged FFP** — corrected
  the blueprint's React-first map), **`roles/gis-engineer.md`** (PostGIS + Python spatial; **corrected the
  blueprint's "GeoServer" rung → NO GeoServer**, EPSG:4326 discipline, COP). Remaining 6/12.

### Added — 2026-08-14 (T2 guides — role-mastery guides, batch 1)
- Started the **12 role-mastery guides** (blueprint §25) in **`idrm-mvp-guides/roles/`** (+ `roles/README.md`
  index). Unlike the topic-based 101s, each role guide is a **learning journey**: the role's mission, its mastery
  map (mermaid, IDRM-corrected + phase-tagged), an ordered reading path mapping each rung to the exact 101 guide/
  doc, MVP-vs-FFP notes, and the capability-based mastery test. Batch 1 (3/12): **`product-manager.md`**,
  **`business-analyst.md`**, **`solution-architect.md`**. Learning-paths hub §4 now routes to `roles/`.
  Remaining 9/12 pending.

### Added — 2026-08-14 (T2 guides — Operations 8/8; 101 LIBRARY COMPLETE 39/39)
- Completed the **Operations** track: **`learn/networking-101.md`** (IP/DNS/ports, the request journey, TLS/certs,
  private networks/firewalls), **`learn/cloud-101.md`** (IaaS/PaaS/SaaS, elasticity, data sovereignty; MVP on-prem
  vs FFP cloud), **`learn/monitoring-101.md`** (monitoring vs observability, golden signals, alert fatigue),
  **`learn/incident-response-101.md`** (operational incidents — distinct from disaster help-requests — lifecycle,
  severity, blameless post-mortems, runbooks), **`learn/disaster-recovery-101.md`** (backup vs DR, RPO/RTO, DR
  strategies), **`learn/sre-101.md`** (SLI/SLO/SLA/error budgets tying the whole Ops track together).
- **MILESTONE: the 101 guide library is COMPLETE — 39/39** across all five tracks (Domain 8, Software-Eng 9,
  Security 7, Quality 7, Operations 8), each balanced for stakeholders + developer-mastery, phase-honest (MVP vs
  FFP), and cross-linked into one learning web anchored by `00-start-learning-paths.md`. Remaining T2: the 12
  role-mastery guides (blueprint §25) + the FFP-guides mirror.

### Added — 2026-08-14 (T2 guides — FFP-oriented 101s, batch 3: Quality 7/7)
- Completed the **Quality** track: **`learn/e2e-testing-101.md`** (whole-journey tests, IDRM's critical journeys,
  Playwright, accessible selectors), **`learn/performance-testing-101.md`** (load/stress/spike/soak, p95/p99,
  the disaster-surge rationale, k6/Locust), **`learn/security-testing-101.md`** (SAST/DAST/SCA/secrets/pen,
  mapped to IDRM's RBAC/injection/privacy checks), **`learn/disaster-drill-scenario-testing-101.md`** (the
  IDRM-unique one: rehearsing people+process+system, chaos engineering, graceful degradation, After-Action).
  Library now **33/39** — only the Operations FFP six remain. Then role-mastery guides + FFP mirror.

### Added — 2026-08-14 (T2 guides — FFP-oriented 101s, batch 2: Security 7/7)
- Completed the **Security** track: **`learn/oidc-101.md`** (federated identity/SSO, IdP, ID token),
  **`learn/oauth-2.1-pkce-101.md`** (delegated authorization, Authorization Code flow, why PKCE is mandatory in
  2.1), **`learn/mfa-101.md`** (the three factor categories, TOTP/push/SMS/hardware keys, protecting admin roles),
  **`learn/threat-modeling-101.md`** (the four questions, STRIDE mapped to IDRM defences, trust boundaries). All
  phase-tagged FFP (MVP = RS256 JWT password login + RBAC), cross-linked to IAM/RBAC/Secure-Coding. Library now
  **29/39**. Remaining: Quality (4) + Operations (6) FFP 101s, then role-mastery guides + FFP mirror.

### Added — 2026-08-14 (T2 guides — FFP-oriented 101s, batch 1: Domain + SW-Eng)
- Completed the **Domain** track (now 8/8): **`learn/emergency-operations-centre-101.md`**,
  **`learn/common-operational-picture-101.md`**, **`learn/emergency-communications-101.md`**,
  **`learn/incident-command-101.md`** (EOC/COP/ICS concepts + how IDRM's coordinator role, map, and alerts/
  notifications realise them). Completed the **Software-Engineering** track (now 9/9) with the FFP-tech guides
  (clearly phase-tagged FFP): **`learn/event-driven-architecture-101.md`** (MVP is synchronous; events are FFP),
  **`learn/docker-101.md`** (MVP is native systemd, no Docker), **`learn/ci-cd-101.md`** (MVP native/scripted;
  full pipeline FFP). Guide library now **25/39**. Remaining: Security (4) + Quality (4) + Operations (6) FFP
  101s, then role-mastery guides + FFP mirror.

### Added — 2026-08-14 (T2 guides — Operations track; all 18 MVP-relevant 101s done)
- Wrote the Operations track's MVP-relevant 101 guides: **`learn/linux-101.md`** (filesystem, everyday commands,
  pipes, permissions/sudo, apt, and **systemd/journalctl** — exactly how IDRM's native Ubuntu services are run
  and debugged) and **`learn/backup-restore-101.md`** (why backups are mission-critical, RPO/RTO/PITR, pg_dump +
  WAL, MinIO DB↔object consistency, off-host+encrypted, restore drills; backup vs DR). **Milestone: 18/39 —
  all MVP-relevant 101s complete** (Domain 4 + Software-Eng 6 + Security 3 + Quality 3 + Operations 2). Remaining:
  21 FFP-oriented 101s + 12 role-mastery guides + the FFP-guides mirror (decision point with user).

### Added — 2026-08-14 (T2 guides — Quality track MVP guides)
- Wrote the Quality track's MVP-relevant 101 guides: **`learn/testing-101.md`** (why test, the testing pyramid,
  Arrange–Act–Assert, pytest, coverage as a floor), **`learn/api-testing-101.md`** (status/shape/rules/validation
  checks, positive+negative examples against `/api/v1`, OpenAPI contract testing, per-role testing),
  **`learn/accessibility-testing-101.md`** (situational a11y, WCAG 2.1→2.2 AA, POUR, keyboard/screen-reader/
  contrast, the mandatory map→list alternative, axe + manual). Guide library now **16/39**. Next: Operations
  track (Linux, Backup & Restore) completes the 18 MVP-relevant 101s.

### Added — 2026-08-14 (T2 guides — Security track MVP guides)
- Wrote the Security track's MVP-relevant 101 guides: **`learn/iam-101.md`** (authN vs authZ, sessions vs tokens,
  RS256 JWT access+refresh, bcrypt-12 + lockout, defense-in-depth), **`learn/rbac-abac-101.md`** (RBAC over the 4
  roles + guest with a can/cannot table; ABAC + Auditor deferred to FFP), **`learn/secure-coding-101.md`** (OWASP
  Top 10 habits, Pydantic validation + parameterised queries, DPDP Act privacy: EXIF strip, no PII in logs/URLs,
  secrets handling). Guide library now **13/39** (Domain 4 + Software-Eng 6 + Security 3). Next: Quality track.

### Added — 2026-08-14 (T2 guides — Software-Engineering track MVP guides)
- Wrote the Software-Engineering track's MVP-relevant 101 guides: **`learn/sdlc-101.md`** (SDLC stages mapped to
  IDRM's own doc set; MVP→FFP triggers; traceability; ADRs/CHANGELOGs), **`learn/git-github-101.md`** (version
  control, branch/PR flow, the IDRM way), **`learn/rest-api-101.md`** (HTTP/REST from scratch, then the frozen
  `/api/v1` contract rules), **`learn/database-101.md`** (relational model, keys, SQL CRUD, transactions/ACID,
  indexes), **`learn/postgresql-postgis-101.md`** (the actual engine + PostGIS spatial + SQLAlchemy/GeoAlchemy2/
  Alembic), **`learn/observability-101.md`** (logs/metrics/traces, health endpoints, MVP-pragmatic vs FFP-full).
  Guide library now **10/39** (Domain 4 + Software-Eng 6). Next: Security MVP track.

### Added — 2026-08-14 (T2 guides — Domain track MVP guides)
- Wrote the Domain track's MVP-relevant 101 guides (balanced depth: stakeholder-friendly + developer-mastery):
  **`learn/incident-management-101.md`** (the incident vs task vs resource distinction, triage, and the LOCKED
  8-state lifecycle as a state machine), **`learn/gis-for-emergency-response.md`** (coordinates/CRS/EPSG:4326,
  GeoJSON, PostGIS `ST_*` queries, Leaflet, accessibility), **`learn/resource-management-101.md`** (needs↔means
  matching, capacity/availability, allocation). Domain track MVP guides now 4/4 (1,2,5,6). Confirmed decisions:
  one library in `mvp-guides/learn`, balanced depth. Next: Software-Engineering MVP track.

### Changed — 2026-08-12 (assets reconciled to canonical scheme)
- **Reconciled all three `../assets/*.xlsx`** to the canonical MVP/FFP docs (spreadsheets follow the docs):
  - **`idrm-api-resource-mapping.xlsx`** — all paths prefixed to **`/api/v1`**; `/services/requests` →
    `/incidents`; base URL → relative `/api/v1`; Overview updated; a **`Phase (MVP/FFP)`** column added to
    the mapping (MVP 73 / FFP 32); Error-Mapping patterns canonicalized. Disaster/financial/websocket/
    analytics rows tagged **FFP** (kept, not deleted).
  - **`idrm-data-model.xlsx`** — `service_requests`→**`incidents`**, `service_request_history`→
    `incident_updates`, `service_request_assignments`→`incident_assignments`, `service_ratings`→
    `incident_ratings`; enums → canonical (`incident_status_enum` = the 8-state lifecycle, `priority_enum`,
    `service_type_enum`) + fields (`urgency`→`priority`, `category`→`service_type`); **`Phase`** column on
    Tables Summary → **11 MVP / 14 FFP**.
  - **`idrm-triggers-views-complete.xlsx`** — same canonical renames across triggers/views/functions;
    summaries phase-tagged.
  - Verified **no stale names/paths/enums remain**; pre-edit backups kept in the scratchpad.

### Changed — 2026-08-12 (Part-C auxiliary triage → analyses/)
- Moved **10 auxiliary generation docs → `../analyses/`** (kept, not discarded; provenance-prefixed):
  the **3 generation overviews** (`v0/00`, `v2/00`, `v3/00` — historical, superseded) and the **7 LLD/design
  docs** (`v0/30-34` incl. the 24.6k-line 21-category LLD, `v2/30`, `v3/30` — kept as **design reference**
  since code is built fresh from the specs). Generation `docs/`+top-level READMEs repointed;
  `../analyses/README.md`, `../INDEX.md`, and the [checklist](../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md)
  Part B/C updated. **Deferred:** the gap-analysis roadmaps (`v2/90`, `v3/91`) stay put — still active
  sources for FFP-02 + the v2/v3 deep-merge.

### Removed — 2026-08-12 (generation retirement: v0–v3 — ALL generations retired ✅)
- **All four archived generations (`../idrm-docs-v0..v3`) retired → `../_removed/`** (reversible). v1 =
  transitional/duplicated. v2 + v3 = primary microservices/multi-frontend sources, **deep-merged into the FFP
  docs first** (FFP-03 §6.1/6.2 service decomposition + Python geospatial; FFP-02 §4.1 migration checklists +
  **Strangler Fig**). v0 = earliest; PRDs → MVP, **API/data → the live `assets/*.xlsx`**, devops → FFP-03/10.
  Overviews/LLDs/research/roadmaps preserved in `../analyses/` (16 docs); v3 tutorials = T2 guide-source in
  quarantine. **Generation consolidation is COMPLETE** — the archive now holds only the live MVP/FFP doc sets,
  guides, assets, scripts, `analyses/`, and `_removed/`. Details in the
  [FFP CHANGELOG](../idrm-ffp-docs/CHANGELOG.md) + [checklist](../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md).

### Added — 2026-08-12 (FFP documentation set written — cross-reference)
- The **FFP documentation set is now written (12/12)** in `../idrm-ffp-docs/` (+ `../idrm-ffp-guides/30-contribute`),
  each doc a **delta on its MVP counterpart**. Tracked in its own **`../idrm-ffp-docs/CHANGELOG.md`**; the
  [consolidation checklist](../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md) Part A/D updated. This
  **unblocks generation retirement** (pending a per-generation verification pass — v1 first, v3 last).

### Added — 2026-08-12 (documentation blueprint reviewed → tasks captured)
- Reviewed **`../assets/idrm-mvp-documentation-blueprint.md`** (a 25-doc technical set + a large
  guide/learning library). Finding: our 11 MVP technical docs cover the core; **most of the blueprint's
  remainder is GUIDE material** (role-mastery maps, 39 "101" guides, onboarding handbook, reading paths),
  not technical docs. Captured the follow-on work as **`../instructions.txt` §14** (pending, to run after
  the technical-docs phase):
  - **T1** — docs gap-check: add any missing *technical* content to docs (candidates: a dedicated
    Requirements-Traceability matrix, a Business-Domain/Capability + Disaster-Lifecycle operating model,
    data-flow/event model, deeper module spec, observability, RACI). *(CI/CD, event bus, deep
    observability stay FFP-deferred.)*
  - **T2** — build the **guides** (the bulk of the blueprint) into `idrm-mvp-guides/` + `idrm-ffp-guides/`.
  - **T3** — standards alignment (ISO 22320, NIMS, NIST CSF 2.0, NIST SP 800-63-4/63B-4, WCAG 2.2).
  - **T4** — adopt the blueprint's "Definition of Documentation Done" as the finalization checklist.
  - **T5** — once MVP+FFP **docs + guides are finalized, replicate the latest sets to the base directory**
    (`../docs/` + `../guides/`) as the **master reference for both MVP and FFP** — first resolving how they
    relate to the existing overview-depth base `docs/` (supersede / merge / sit-beside).

### Changed — 2026-08-12 (FFP set frozen · analyses folder)
- **FFP doc set FROZEN at 12** (mirrors the MVP set 1:1 + Messaging & Async). Every archived-generation doc
  now merges into one of these 12 frozen docs, or goes to `../../analyses/` if auxiliary — no new FFP doc
  categories invented. Recorded in the [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md) §4
  and the [checklist](../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md) Part A.
- **New `../../analyses/` folder** (auxiliary/research material — **kept, not discarded**, distinct from
  `_removed/`). Policy: auxiliary docs preserved with a generation prefix. **Moved 4 v0 docs** there:
  `v0-90-project-odoo-analysis`, `v0-70-`/`v0-71-quality-validation` (doc-validation meta), `v0-41-reference-prompts`.
  v0 indexes + `../INDEX.md` updated; checklist Part C reframed from "discard" to "→ analyses" (remaining
  overviews/LLDs/gap-analyses flagged as confirm-first candidates).

### Added — 2026-08-12 (FFP consolidation checklist + doc-set parity)
- **`../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md`** — a triage checklist that (a) lists the
  **12 FFP docs to write** (mirroring the MVP set 1:1 + a Messaging & Async doc), each with its **primary
  sources** from v0..v3; (b) a **coverage map** assigning **every** v0..v3 file a destination
  (✅MVP-done / →FFP-doc / 📦asset / 🗑discard); (c) a **discard/park list** (doc-validation tooling,
  generation overviews, exhaustive monolith LLDs [verify-first], Odoo analysis, prompt dumps); (d) a
  **per-generation retirement gate**. Conclusion: **no generation is retirable yet** — MVP side done, FFP
  side not started; nothing is lost (all mapped).
- **FFP charter §4 aligned to the MVP set** — the FFP doc set now shows each doc's **MVP counterpart** and
  adds a **Quality & Test** doc (`70-…`) for parity; 12 docs total. Recorded in
  [`../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md`](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md).

### Added — 2026-08-12 (remaining docs — MVP doc set complete)
- **`21-architecture-decisions.md`** — **14 ADRs** (Decision/Context/Options/Consequences) formalising the
  locked choices: modular monolith · PostGIS source-of-truth · API-first `/api/v1` stable URIs ·
  HTML+Tailwind+JS · no Redis · native systemd/no Docker · MinIO-in · RS256+RBAC · lean 7-state lifecycle ·
  4 roles · face-detection-only/FaceNet-out · no broker · native ENUMs · setup-script "futuristic" (Bun) note.
- **`60-uidesign-web-interaction.md`** — the web UI spec: HTML+Tailwind v4+JS+Leaflet; role-based nav;
  global form/table/map/accessibility (WCAG 2.1 AA) patterns; **screen→API-call** tables for every role;
  the lifecycle flow diagram; low-bandwidth/emergency-lite posture. React/mobile/offline → FFP.
- **`70-quality-test-strategy.md`** — the MVP pyramid (Unit 60 / API 20 / Integration 15 / E2E 5); pytest +
  FastAPI TestClient + disposable PostGIS DB + test MinIO bucket; quality gates (Black/isort/Ruff/mypy,
  **≥80% coverage**); a **traceability table mapping every feature F1–F11's acceptance criteria to tests**.
- **`80-ops-deployment-and-operations.md`** — standalone **Ubuntu** deploy, **native systemd** (uvicorn +
  PostgreSQL/PostGIS + MinIO); install via `../scripts/setup-idrm-ubuntu.sh`; env/config; **Alembic**
  migrations; run/health/logging; **backup & DR** (3-2-1, pg_dump + `mc mirror`, RPO/RTO). Docker/APISIX/
  Redis/observability stack → FFP.
- **`../idrm-mvp-guides/30-contribute-developer-guide.md`** — novice-friendly contributor guide (goes to
  **guides/**): what IDRM is, one-command setup, repo/module structure (`router→service→repository`), run
  locally, run tests, conventions, branch→PR flow, Definition of Done.
- **Ops MVP deviations recorded** (follow locked stack): **no Flask/Gunicorn** (uvicorn serves API+static
  UI), **no Redis** (DB-backed sessions), MinIO for files; a **lightweight reverse proxy** (Caddy/NGINX) is
  used for TLS/static only in the MVP — the full **APISIX** gateway is → FFP.

### Added — 2026-08-12 (security & IAM)
- **`22-architecture-security-and-iam.md`** — the MVP **Security & IAM Design** (sixth doc; **completes the
  "core six"**). Authentication (account lifecycle; **token model** — RS256 access ~60 min + rotating
  revocable refresh ~7 days + single-use email/reset tokens + scoped guest token); NIST-aligned **password
  policy** (length over composition, breached-password check, bcrypt cost 12); **5-attempt / 15-min
  lockout**; the **RBAC map** — a per-operation **role → API-operation matrix** covering every locked
  endpoint (citizen/provider/coordinator/admin + guest, with own/assigned ownership scoping); data
  protection (TLS 1.2+, Pydantic validation, private MinIO bucket + pre-signed URLs, env-var secrets);
  **append-only audit**; per-endpoint rate limits; OWASP/STRIDE threat model; **DPDP Act 2023** / WCAG
  compliance. Consolidated from the authoritative `../../docs/05-security.md` + the locked API/data model.
- **Security decisions of note** (chosen with rationale — adjust if desired): **RS256** JWT (FFP-service
  verify without shared secret); **NIST-style password policy** (gentler than v3's composition rule —
  better for stressed/low-literacy users); **15-min** lockout (not 30 — avoids shutting out emergency
  users). **Deferred → FFP** (recorded in the [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md)):
  OIDC/SSO, MFA, ABAC, full 10-role hierarchy + Auditor role, per-request privacy levels, FaceNet biometric,
  APISIX gateway/WAF, secrets vault/KMS + field-level AES-256 at rest.

### Added — 2026-08-12 (data model)
- **`50-data-model.md`** — the MVP **Data Model & Database Design** (fifth doc, PostgreSQL + PostGIS).
  Conceptual (ERD) → logical → physical. **13 MVP tables** backing the locked API resources: `users`,
  `user_sessions`, `password_reset_tokens`, `email_verification_tokens`, `organizations`, `resources`,
  **`incidents`** (+ `incident_updates`), `alerts`, `notifications`, `notification_preferences`, `files`
  (MinIO refs), `audit_logs`. Native `ENUM` types **matching the API wire values exactly**; UUID keys,
  snake_case, TIMESTAMPTZ `*_at`, PostGIS `GEOMETRY(...,4326)`; GiST/GIN/B-tree indexing incl. full-text
  `?q=`; soft-delete + append-only audit; **Alembic** migration approach. Consolidated from
  `../assets/idrm-data-model.xlsx` (25-table design), **trimmed to MVP and renamed to the canonical,
  incident-centric scheme**.
- **Reconciliation decisions recorded in the doc** (following already-locked choices — not re-litigated):
  `service_requests`→**`incidents`**; lifecycle enum = the locked 8 states (`created…verified` + cancel/
  reject); `service_type`/`priority` (not `category`/`urgency`); `org_type` aligned to the API set.
  **Folded** (kept lean): ratings + assignment onto `incidents`; org verification/capacity onto
  `organizations`; location geometry on each row (no shared `locations` table). **Deferred → FFP:**
  `disaster_events`, `affected_areas`, `financial_transactions`, `fund_allocations`, `donation_receipts`,
  `service_clusters`, `system_metrics`, `websocket_connections`, `chat_messages`, plus privacy-level
  column / `disputed` status / auto-close. Logged in the [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md).

### Changed — 2026-08-12 (archive scripts reorganized)
- **New `../scripts/` folder** consolidates shell scripts. **Moved** `setup-idrm-ubuntu.sh` from
  `../assets/` → `../scripts/` (the MVP Ubuntu installer). **Copied** the 15 FFP devops scripts from
  `../idrm-ffp-code/backup/` → `../scripts/` (originals kept in `backup/`). `assets/` now holds only data
  artifacts (the xlsx spreadsheets). Structure notes updated in [`../instructions.txt`](../instructions.txt) §4
  and [`../INDEX.md`](../INDEX.md); the setup-script link in the MinIO entry was repointed to `../scripts/`.
- **`check-devops-stack.sh` collision resolved.** The newer copy (2026-06-10, 60787 B) is now the canonical
  `check-devops-stack.sh` in **both** `../idrm-ffp-code/backup/` and `../scripts/`; the older copy
  (2026-06-08, 60587 B) is preserved alongside as `check-devops-stack-alt.sh` in both. This also emptied
  `../idrm-ffp-code/backup/`'s source folder `../idrm-ffp-code/scripts/`, completing the earlier
  scripts→backup move.

### Added — 2026-08-12 (API spec)
- **`40-api-specification.md`** — the MVP **API Specification** (fourth doc). API-first client↔backend
  contract: frozen **§2 conventions**, auth/roles model, the canonical **resource catalog**, and full
  **endpoint specs** grouped by resource, each tagged to a **Feature (F1–F11)** and the request-lifecycle
  transitions from doc 11 §4. Standard **error catalog** with machine-readable `code`s. Consolidated from
  the archived v3 API spec and the `../assets/idrm-api-resource-mapping.xlsx` matrix, restandardized to
  the canonical scheme.
- **`40-api-openapi.yaml`** — the machine-readable **OpenAPI 3.0.3** contract (48 paths, 56 operations,
  reusable schemas/params/responses). **Validated** with `openapi-spec-validator` (passes). Bearer-JWT
  security; anonymous `POST /incidents` allowed for guest emergencies.

### Added — 2026-08-12 (media handling & quality rules)
- Documented **file/photo handling rules** (novice-friendly, with rationale). **`40-api-specification.md`**
  §5.7 gains a **"Media handling & quality rules"** subsection; **`20-architecture-system.md`** §7 gains a
  compact "compress-first" note. Rules: compress-on-device + **server re-validation**; files **≤ 10 MB**
  (multi-page PDFs **≤ ~1.5 MB/page** for page-by-page upload on weak links); ≤ 5 photos/incident,
  ≤ 2 MB each; photos resized to **≤ 1920 px**, **≥ 640×480**, **blur-checked**, **EXIF/GPS stripped**;
  an **emergency "lite" mode** sends one **≤ ~500 KB** photo on slow connections.
- **Face handling decided (user-confirmed):** the **MVP uses lightweight client-side face _detection_**
  (photo-quality gate only — **no biometric data stored**). Full **FaceNet face _recognition_/matching**
  is **→ FFP** (heavier DS/ML + biometric data of vulnerable people → needs consent + **DPDP Act 2023**
  safeguards). Recorded in the [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md) §2
  (new "Media & biometric capabilities" subsection), alongside a deferred scaled server-side media
  pipeline and video/large-media support.

### Added — 2026-08-12 (MinIO object storage — MVP)
- **File/photo upload is confirmed MVP**, and **MinIO** (on-prem, **S3-compatible** object storage) is
  added as the MVP storage backend for uploaded photos/documents (incident evidence F2, completion proof
  F5). PostgreSQL stays the source of truth for *records*; MinIO holds the *bytes* (DB keeps only object
  keys/URLs). Chosen over local filesystem because the **S3 API contract carries unchanged into the FFP**
  (distributed MinIO / cloud S3) with no code rewrite.
  - **`20-architecture-system.md`** §7 — MinIO added to the required MVP stack table + a "file storage"
    principle note.
  - **`40-api-specification.md`** §5.7 — storage note on `POST /files` (MinIO, pre-signed URLs, S3).
  - **`../scripts/setup-idrm-ubuntu.sh`** (moved from `../assets/` on 2026-08-12) — new **Step 3B** installs MinIO **natively as a systemd service**
    (no Docker): server + `mc` client binaries, dedicated `minio-user`, `/var/lib/minio` data dir,
    `/etc/default/minio` config, `minio.service`, health-wait, and creates the **`idrm-uploads`** bucket.
    Added `boto3` to the conda env; MinIO added to header manifest, verification, and summary (S3 :9000,
    console :9001). Syntax-checked (`bash -n`).
  - **FFP charter** — new "Object storage (scale-out)" row (distributed MinIO / cloud S3, same S3 contract).

### Changed — 2026-08-12 (API contract completion pass)
- Closed the remaining gaps in the API contract (user-requested finalization). **`40-api-openapi.yaml`** now
  **52 paths / 61 operations**, re-validated (passes). Additions/fixes:
  - **File uploads (decision → included in MVP):** `POST /files` (+ `GET /files/{id}`) — `multipart/form-data`,
    image/jpeg·png·pdf, ≤ 10 MB; incidents' `photos` reference the returned URLs (F2 emergency evidence,
    F5 completion proof). Heavy media → FFP. *(Reversible if we later prefer external-URL-only.)*
  - **Pagination consistency:** added `page`/`limit`/`sort` to `/incidents/mine`, `/incidents/assigned`,
    `/incidents/nearby`, and `/alerts`; wrapped `/alerts` in the `{data, pagination}` envelope.
  - Added **`q` free-text search** to `GET /incidents`; **`GET /users/{id}`**; **`DELETE /notifications/{id}`**
    (soft-delete); **`GET /health`** liveness probe; `413 file_too_large` to the error catalog; `area`/
    `expires_at`/`active` on the `Alert` schema. `40-api-specification.md` updated to match.

### Decided — 2026-08-12 (API conventions frozen — v1)
- **Canonical URI scheme = Option 1** (user-confirmed): incident-centric, **version-in-path `/api/v1/…`**,
  matching the finished `docs/` set + MVP module list (the `xlsx` asset is the outlier and will be
  reconciled to this). The five convention choices were confirmed **all-as-recommended**:
  (1) singles = bare object, **collections wrapped** `{data,pagination}`;
  (2) lifecycle handled by **dedicated transition endpoints** (`/accept`, `/start`, `/complete`, `/verify`,
  `/cancel`, `/approve`, `/reject`) rather than a generic status PATCH;
  (3) **UUID** identifiers;
  (4) coordinates = explicit `{latitude, longitude}` on input, **GeoJSON** on map-layer output;
  (5) **lowercase snake_case** enum wire values (`service_type: medical`, `status: in_progress`).
  Also frozen: `snake_case` fields, ISO-8601 UTC `*_at` timestamps, `?page&limit` pagination, `-field`
  sort, `Bearer` JWT, `429`+`Retry-After`, `Accept-Language` for F11.

### Decided — 2026-08-12 (API URI stability)
- **API URIs are a stable contract across the whole SDLC** (user-confirmed). A path defined for the MVP
  keeps the **same URI** in the FFP — only the implementation behind it moves (FastAPI route → APISIX-
  fronted microservice). URIs are designed **once, canonically**, and shared by the MVP API spec and the
  FFP API doc; FFP may *add* endpoints but never *renames* MVP ones. Recorded in the hand-off
  [`../instructions.txt`](../instructions.txt) §12 and the API brief in
  [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).

### To do — 2026-08-12 (asset reconciliation, follow-up)
- **`../assets/idrm-api-resource-mapping.xlsx`** (the endpoint↔resource↔role↔rate-limit↔error matrix)
  currently uses a **divergent, FFP-flavoured** URI scheme (`/services/requests`, `/disasters`,
  `/financial/*`, base `https://api.idrm.gov.in/v1`) that does **not** match the finished `docs/` set or
  the MVP plan (`/api/v1/incidents`, `/resources`, `/locations`, `/alerts`, `/users`). **After** the
  canonical URIs are confirmed and `40-api-specification.md` is written, this xlsx (and
  `idrm-data-model.xlsx` / `idrm-triggers-views-complete.xlsx`) must be **updated to match** — tagging
  rows MVP vs FFP, keeping URIs identical, and moving financial/disaster/websocket rows to the FFP
  portion (not deleted).

### Added — 2026-08-12 (later)
- **`11-requirements-scope-and-acceptance.md`** — the MVP **Scope & Acceptance Criteria** document
  (third of the set). Explicit **in-scope / out-of-scope** lists; the authoritative lean **request
  lifecycle** (created → *approved-if-critical* → accepted → in-progress → completed → verified, plus
  cancelled/rejected exits, with a Mermaid state diagram); a **Feature → Requirement → Acceptance
  (Given/When/Then) → Test** chain for **11 features (F1–F11)** covering PRD **FR-1…12**;
  non-functional acceptance intent; and a two-level **Definition of Done** (feature + MVP).
  Consolidated from the PRD (source of truth) and the richer v3 Functional Specification
  (`../idrm-docs-v3/docs/11-requirements-functional-spec.md`), trimmed to MVP size. Tech-free
  (behaviour, not stack); security/perf specifics cross-linked to docs 22/70.

### Decided — 2026-08-12 (Scope & Acceptance)
- **Five v3 capabilities confirmed out of MVP scope → FFP** (user-approved, "go with all
  recommendations"): (1) the **full 8–10-level role hierarchy** — MVP keeps **3 roles** (citizen,
  provider, coordinator/admin); (2) the **financial/donation subsystem** and **Auditor** role — MVP
  coordinates help, not funds; (3) the extra lifecycle states **Disputed** and **automatic Close**;
  (4) **per-request privacy levels** (Public/Protected/Private) — MVP protects data via role-based
  access; (5) the **"Disaster Event"** first-class entity (declare event, draw zone, auto-link) — MVP
  stays request-centric. All five recorded in the
  [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md) §2 (new subsection), not dropped.
- **MVP request lifecycle fixed** at the lean 7-state model above; it is now the authoritative lifecycle
  referenced by the API, data, and test docs.

### Changed — 2026-08-12 (FFP charter)
- **`../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md`** — added a new subsection *"Product-scope
  items deferred from the MVP Scope & Acceptance work"* recording the five deferrals above, each with the
  v3 Functional Specification named as its primary source material.

### Added — 2026-08-12
- **`20-architecture-system.md`** — the MVP **System Architecture** document, generated from the
  CO-STAR prompt (all 35 sections, Mermaid diagrams, 5 GenAI poster prompts). Modular monolith ·
  HTML + **Tailwind CSS v4** + JS · FastAPI/Python · PostgreSQL/PostGIS. Domain detail (modules,
  request/module flows, security & testing overviews) consolidated from `../idrm-docs-v0..v3/`;
  every deferred technology (Bun/Node/Deno, React, Expo, Redis, Docker, Swarm/K8s, brokers,
  microservices) labeled **→ FFP** and cross-linked to the FFP charter. *First document of the set.*
- **`10-requirements-prd.md`** — the MVP **Product Requirements Document**. **Tech-free** (needs only;
  no stack), **MVP-scoped**, India-grounded. Consolidated primarily from the v3 PRD (vision, problem,
  objectives, stakeholders, personas, use cases, FR-1..12, NFR-1..7, business rules, constraints,
  success criteria). Enterprise-scale deviations (AI matching, national rollout, native mobile,
  full localization, multi-channel, advanced analytics) **recorded in §13 and in the FFP charter**
  rather than dropped.

### Decided — 2026-08-12
- **Architecture basis confirmed:** the MVP documentation set follows the CO-STAR prompt
  ([`prompts/IDRM MVP Architecture - CO-STAR Prompt.md`](prompts/IDRM%20MVP%20Architecture%20-%20CO-STAR%20Prompt.md)) —
  a **pure-Python FastAPI modular monolith**, HTML/Tailwind CSS/JS web UI, PostgreSQL/PostGIS as the source of truth.
- **Advanced tech chartered to the FFP (next phase):** Bun / Node / Deno, React (web),
  React Native / Expo (mobile), and microservices are **deferred to the Full-Fledged Product**.
  Recorded in [`../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md`](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md).
  Redis, Docker/Swarm/Kubernetes, Kafka/RabbitMQ and background workers are likewise deferred.
- **Consolidation strategy:** MVP docs are built by pulling **monolith-consistent domain detail**
  (modules, entities, layering, security, testing) from the archived generations
  `idrm-docs-v0..v3/`; conflicting/advanced tech is routed to the FFP charter, not discarded.
  This lets the versioned `idrm-docs-v*` folders be safely retired afterward.

### Changed — 2026-08-12
- **Web styling set to Tailwind CSS v4.** Replaced generic `CSS` / `CSS3` styling references with
  **Tailwind CSS v4** across `idrm-mvp-docs/` and the FFP charter (15 edits). The MVP web UI is now
  **HTML + Tailwind CSS v4 + JavaScript** (utility-first CSS, still no React; usable via CDN or a
  minimal build). No `.css` filenames or generic CSS-language references were altered. No Bootstrap
  was present. Scope confirmed by user: `idrm-mvp-docs/` + `idrm-ffp-docs/`.
- **Renamed** `prompts/idrm_mvp_docs_instructions.md` → `prompts/instructions_idrm_mvp_docs.md` (references updated).
- **FFP API gateway = APISIX** (with plugins/extensions covering reverse proxy, caching, authentication,
  rate limiting, TLS, routing, observability — i.e. all NGINX reverse-proxy capabilities). Bun/Node/Deno
  are re-scoped to **edge/runtime services behind APISIX**, not the gateway. Noted across the FFP docs
  (charter, FFP architecture prompt, README) and the MVP architecture doc's forward-references updated.
- **FFP is polyglot.** Recorded that scale-, security-, and resilience-critical FFP microservices may use
  **Java / Go / JS** runtimes (runtime diversity also as a resilience/backup strategy), while **Python is
  retained for rapid prototyping and DS/ML** — adopted per-service, as time permits, same API contract.
  Noted in the FFP charter + architecture prompt and the MVP architecture doc (§31).

### Planned (in dependency order — see `prompts/instructions_idrm_mvp_docs.md`)
- ~~`20-architecture-system.md`~~ — ✅ done · ~~`10-requirements-prd.md`~~ — ✅ done ·
  ~~`11-requirements-scope-and-acceptance.md`~~ — ✅ done ·
  ~~`40-api-specification.md` (+ `40-api-openapi.yaml`)~~ — ✅ done ·
  ~~`50-data-model.md`~~ — ✅ done · ~~`22-architecture-security-and-iam.md`~~ — ✅ done ·
  ~~`21-architecture-decisions.md`~~ · ~~`60-uidesign-web-interaction.md`~~ ·
  ~~`70-quality-test-strategy.md`~~ · ~~`80-ops-deployment-and-operations.md`~~ ·
  ~~`idrm-mvp-guides/30-contribute-developer-guide.md`~~ — ✅ **all done.**
- **THE MVP DOCUMENT SET IS COMPLETE (11/11).** Remaining follow-up (not a doc): reconcile the three
  `../assets/*.xlsx` to the canonical URIs/table names (see hand-off §13); optional Bun cleanup of the setup
  script (§13 / ADR-014).
- **Follow-up (queued):** reconcile all three `../assets/*.xlsx` (api-resource-mapping → `/api/v1/…` URIs;
  data-model + triggers-views → canonical table/column names) — now unblocked, since doc 50 fixed the names.
