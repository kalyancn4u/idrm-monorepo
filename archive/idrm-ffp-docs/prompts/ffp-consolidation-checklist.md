# IDRM FFP — Consolidation Checklist (what's needed vs what can be discarded)

*Type: Document (plan / triage checklist) · Audience: everyone · Status: FFP planning*

> **Why this exists:** before any archived generation (`idrm-docs-v0..v3`) can be retired to `_removed/`,
> **every file** in it must be either **(a) consolidated** into the MVP docs, **(b) planned into an FFP
> doc** here, or **(c) explicitly marked discard/park**. This checklist is that accounting. It also keeps
> the **FFP set on the same lines as the MVP set** — FFP is functionally an *extension* of the MVP, so its
> docs mirror the MVP's 1:1 (see the [charter §4](instructions_idrm_ffp_docs.md)).

> **Retirement gate:** a generation folder moves to `_removed/` **only** when its row in Part D is 100%
> green (every file ✅ consolidated / →FFP-planned-captured / 🗑 discard-approved) **and** the FFP docs that
> depend on it have been written (so no live doc references point into `_removed/`).

**Legend:** ✅MVP = already in the MVP docs · →FFP-NN = feeds FFP doc #NN (to be written) · 📦 = already
extracted to a live asset (`assets/*.xlsx`) · 🗑 = discard/park candidate (see Part C) · 🕮 = historical
overview, superseded.

---

## Part A — FFP documents to write (mirror the MVP set + 1) — **FROZEN (12)**

*This set is **frozen (2026-08-12)** and **ALL 12 ARE NOW WRITTEN (2026-08-12)** — see
[`../CHANGELOG.md`](../CHANGELOG.md). Every archived-generation doc merges into one of these 12, or goes to
`../../analyses/` if auxiliary — no new FFP doc categories are invented. Dependency order, like the MVP.
Each doc was written as a **delta on its MVP counterpart** (extend, don't duplicate); the source detail
below can still be deep-merged before retiring the generations.*

- [x] **FFP-01 · `10-requirements-prd.md`** — enterprise-scale PRD & SLAs.
  *Sources:* MVP PRD §13 deferrals · `v3/10-prd` (enterprise parts) · `v2/10-prd` · `v0/10,11-prd` · charter §2 product-scope list.
- [x] **FFP-02 · `11-requirements-scope-and-roadmap.md`** — phased evolution + per-capability triggers.
  *Sources:* `v3/91-roadmap`, `v3/92-migration-to-microservices`, `v2/90-roadmap` · MVP scope §3 deferrals.
- [x] **FFP-03 · `20-architecture-system.md`** — microservices, **APISIX** gateway, Bun/Node edge, boundaries.
  *Sources:* `v2/21-corrected-final` (primary), `v2/22-lightweight`, `v2/23-hld`, `v3/21-hld`, `v3/82-api-gateway` (reframe Bun→APISIX), `v1/20-web-platform`, `v3/92-migration`.
- [x] **FFP-04 · `21-architecture-decisions.md`** — ADRs, each with a concrete trigger.
  *Sources:* `v3/22-decisions` (46 ADRs, primary), `v2/24-decisions` · the "→ FFP" side of the MVP ADRs.
- [x] **FFP-05 · `22-architecture-security-and-iam.md`** — OIDC/SSO, MFA, ABAC, zero-trust, secrets vault.
  *Sources:* MVP security §9 deferrals · `../../docs/05-security.md` (OIDC/MFA/ABAC "future-ready") · v3 security detail.
- [x] **FFP-06 · `40-api-specification.md` (+ `40-api-openapi.yaml`)** — gateway + inter-service contracts, **same public API**.
  *Sources:* `v3/40-api` (5.4k L, primary), `v2/40-api`, `v2/41-json-formats`, `v1/40-api`, `assets/idrm-api-resource-mapping.xlsx` (FFP rows), `v3/82-api-gateway`.
- [x] **FFP-07 · `50-data-model.md`** — per-service data ownership + the **deferred tables** (disasters, financial, clusters, websocket, chat), replication.
  *Sources:* `v3/50-data`, `v3/51-query-ref`, `v0/50,51`, `assets/idrm-data-model.xlsx` (FFP tables), MVP data-model §10 deferrals.
- [x] **FFP-08 · `60-uidesign-frontend.md`** — React web SPA + React Native/Expo.
  *Sources:* `v3/32-frontend` (React, primary), `v3/60-design-system`, `v2/60,61,62-uidesign`, `v1/60-ui`.
- [x] **FFP-09 · `70-quality-test-strategy.md`** — contract testing, heavy E2E, performance/load, DAST, DORA.
  *Sources:* `v3/70-testing` (primary), `v3/71-code-standards` · MVP test §6 deferrals.
- [x] **FFP-10 · `80-ops-platform-and-deployment.md`** — Docker → Swarm/K8s, CI/CD, observability, HA, AWS variant.
  *Sources:* `v3/80-ci-cd`, `v2/80-ci-cd`, `v1/80-ci-cd`, `v0/21-hld-devops`, `v0/35-devops-components`, `../../docs/07-operations.md` (§5 AWS).
- [x] **FFP-11 · `81-ops-messaging-and-async.md`** *(FFP-only)* — Redis Streams / RabbitMQ / Kafka, workers, queues, deep push.
  *Sources:* `v3/81-redis` (primary), charter §2 async row · MVP ADR-012 (deferred broker).
- [x] **FFP-12 · `idrm-ffp-guides/30-contribute-developer-guide.md`** — contributing across services.
  *Sources:* `v2/30-contribute`, `v3/30-contribute`, `v3/90-structure`, `v3` guides.

*(Then, as with the MVP: write a CO-STAR prompt per doc in `prompts/` if desired; keep an FFP CHANGELOG.)*

---

## Part B — Coverage map (every generation file has a destination)

### `idrm-docs-v0` — ✅ **RETIRED → `../../_removed/idrm-docs-v0/` (2026-08-12)**
Verified: PRDs (10/11/12) → ✅MVP; architecture/devops HLD (20/21/35) → MVP arch + FFP-03/10 (superseded by the
richer v2/v3 detail already merged); **API/data (40/50/51) are already the live `assets/*.xlsx`**
(api-resource-mapping, data-model, triggers-views). Overviews + LLDs (00, 30–34) and meta/research (70/71/90/
guide-41) had already gone to `analyses/`; training-tracker → 📦 `assets/idrm_skills_tracker.xlsx`. Rest moved
to `_removed/`. **No unique needful content lost.**

### `idrm-docs-v1` — ✅ **RETIRED → `../../_removed/idrm-docs-v1/` (2026-08-12)**
Verified (2026-08-12): all 6 docs superseded by MVP + FFP docs; the 4 setup guides' spec-level content is in
MVP ops §7 + FFP-10 (their step-by-step how-to is recoverable source for the pending T2 guides). Moved intact
to `_removed/` (reversible quarantine). *(Was: 10-prd →MVP/FFP-01 · 20/30 →FFP-03/06 · 40-api →FFP-06 ·
60-pages →FFP-08 · 80-ci-cd →FFP-10 · setup guides →FFP-10/T2.)*

### `idrm-docs-v2` — ✅ **RETIRED → `../../_removed/idrm-docs-v2/` (2026-08-12)**
Verified: PRD/functional-spec/monolith/web → ✅MVP; 41-json-formats → canonical MVP API/OpenAPI; UI (60/61/62)
superseded by v3 → FFP-08; decisions (24) → MVP/FFP ADRs. **Deep-merged into FFP** before retiring:
`21-corrected-final` → **FFP-03 §6.1/6.2** (concrete service decomposition + Python geospatial service);
`24-decisions` playbook → **FFP-02 §4.1** (migration checklists). Overview + LLD had already gone to
`analyses/` (v2-00, v2-30); **`90-roadmap` → `analyses/v2-90-…`**. Rest moved intact to `_removed/`.

### `idrm-docs-v3` — ✅ **RETIRED → `../../_removed/idrm-docs-v3/` (2026-08-12)**
The primary FFP source. Verified: specs (10/11/20/40/50/51/72) → MVP + FFP docs; decisions (22) → FFP-04/ADRs;
design (23/60/32) → FFP-08; ops (80/81/82) → FFP-10/11/03. **Deep-merged into FFP** before retiring:
`92-migration` → **FFP-02 §4.1** (Strangler Fig pattern + success metrics + service-mesh note). Overview + LLD
already in `analyses/` (v3-00, v3-30); **`91-roadmap` → `analyses/v3-91-…`**. Its **beginner tutorials**
(`81-redis` Redis-101, `31-backend` FastAPI-from-scratch, `82-api-gateway` Bun guide, `70-testing`,
`71-code-standards`) are **guide-source for the pending T2 guides**, recoverable from `_removed/`.

---

## Part C — Auxiliary → `../../analyses/` (kept, not discarded)

*Policy (user, 2026-08-12): auxiliary/research/meta docs are **preserved in `../../analyses/`** with a
generation prefix — **not** deleted. `_removed/` stays reserved for genuine duplicates/stubs only.*

**Already moved (2026-08-12):**
- [x] `v0/70-quality-multilingual-validation` → `analyses/v0-70-…` — doc-*validation tooling* (meta).
- [x] `v0/71-quality-periodic-validation` → `analyses/v0-71-…` — doc-*validation tooling* (meta).
- [x] `v0/90-project-odoo-analysis` → `analyses/v0-90-…` — Odoo/ERP governance research.
- [x] `v0/guides/41-reference-prompts` → `analyses/v0-41-…` — CO-STAR prompt library.

**Moved 2026-08-12:**
- [x] **Generation overviews** — `v0/00-overview-presentation`, `v2/00-overview…`, `v3/00-overview…` →
  `analyses/v0-00…`, `v2-00…`, `v3-00…` (historical; superseded by posters + MVP/FFP overviews, kept).
- [x] **Exhaustive monolith LLDs** — `v0/30` (24.6k L) + `v0/31,32,33,34`, `v2/30`, `v3/30` →
  `analyses/v0-30…34`, `v2-30`, `v3-30` (**kept as design reference** — code is built fresh from the specs;
  their decisions are already in the MVP/FFP specs).

**Still deferred (active sources — not moved):**
- [ ] **Gap-analyses** — `v2/90-roadmap`, `v3/91-roadmap` stay in place; they are still sources for **FFP-02**
  and the pending **v2/v3 deep-merge**. Move to `analyses/` (analysis remainder) when v2/v3 are retired.

*Everything else in v0–v3 is ✅MVP, →FFP-planned, or 📦 an asset — i.e. accounted for.*

---

## Part D — Per-generation retirement readiness (the gate)

| Generation | MVP content | FFP content | Discard items | **Retire to `_removed/` when…** |
|---|---|---|---|---|
| ~~**v0**~~ | ✅ done | ✅ covered (assets + FFP-03/10) | ✅ LLD/overview/meta → analyses | ✅ **RETIRED → `_removed/idrm-docs-v0/` (2026-08-12)** |
| ~~**v1**~~ | ✅ done | ✅ captured | (none unique) | ✅ **RETIRED → `_removed/idrm-docs-v1/` (2026-08-12)** |
| ~~**v2**~~ | ✅ done | ✅ deep-merged (FFP-02 §4.1, FFP-03 §6.1/6.2) | ✅ overview/LLD/roadmap → analyses | ✅ **RETIRED → `_removed/idrm-docs-v2/` (2026-08-12)** |
| ~~**v3**~~ | ✅ done | ✅ deep-merged (FFP-02 §4.1 Strangler Fig) | ✅ overview/LLD/roadmap → analyses; tutorials = T2 source | ✅ **RETIRED → `_removed/idrm-docs-v3/` (2026-08-12)** |

**Bottom line (updated 2026-08-12):** MVP side ✅ complete; **FFP side ✅ drafted (12/12)**. The FFP docs
were written as **deltas** on the MVP — so the generations' *decisions/direction* are captured, but their
**detailed content has not yet been line-by-line deep-merged**. **Recommended before retiring any
generation:** a **verification pass** per generation (confirm each file's needful detail is either in an
FFP/MVP doc, an asset, or `analyses/`), then move it to `_removed/` and fix any source-links. **ALL FOUR
generations (v0, v1, v2, v3) RETIRED (2026-08-12)** to `_removed/` — generation consolidation is **COMPLETE**.
Their content lives in the MVP + FFP docs, `assets/*.xlsx`, and `analyses/`; `_removed/` is reversible. Nothing is lost —
all mapped, and `_removed/` is reversible.

---

## Part E — Sequence & next action

1. **Approve Part C** (the discard/park list) — the only content we'd *not* carry forward.
2. **Write the FFP docs** in Part A order (10 → 11 → 20 → 21 → 22 → 40 → 50 → 60 → 70 → 80 → 81 → guide),
   same workflow as the MVP (read sources, flag conflicts + recommendation, write, update an FFP CHANGELOG).
3. **Retire generations** per Part D as their content lands in FFP docs — moving each to `_removed/` and
   fixing the charter §3 source-links as we go (so no live doc points into quarantine).

*Related:* [FFP charter](instructions_idrm_ffp_docs.md) · MVP set [`../../idrm-mvp-docs/`](../../idrm-mvp-docs/) ·
archive map [`../../INDEX.md`](../../INDEX.md) · hand-off [`../../instructions.txt`](../../instructions.txt).
