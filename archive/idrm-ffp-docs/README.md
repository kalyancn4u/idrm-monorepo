# IDRM FFP — Documents

**FFP = Full-Fledged Product** (the later, full-scale enterprise system the MVP evolves into).

This folder holds the **FFP specifications & project detail** — the *next phase* after the MVP:
selective microservices, an **APISIX** API gateway (with JavaScript edge services — Bun / Node / Deno), a React web SPA + React
Native / Expo mobile, plus Redis, brokers, Docker/Kubernetes and observability. Flat files named
`<prefix>-<category>-<name>.md` (shared legend: `00` overview · `10` requirements · `20` architecture ·
`30` design · `40` api · `50` data · `60` uidesign · `70` quality · `80` ops · `90` project).

## Status: the FFP doc set is WRITTEN (12/12, 2026-08-12)
Each FFP doc is a **delta on its MVP counterpart** — it states what the FFP *adds* and cross-links the MVP
doc for the shared foundation. See [`CHANGELOG.md`](CHANGELOG.md).

| # | Doc | | # | Doc |
|---|---|---|---|---|
| 01 | [`10-requirements-prd.md`](10-requirements-prd.md) | | 07 | [`50-data-model.md`](50-data-model.md) |
| 02 | [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md) | | 08 | [`60-uidesign-frontend.md`](60-uidesign-frontend.md) |
| 03 | [`20-architecture-system.md`](20-architecture-system.md) | | 09 | [`70-quality-test-strategy.md`](70-quality-test-strategy.md) |
| 04 | [`21-architecture-decisions.md`](21-architecture-decisions.md) | | 10 | [`80-ops-platform-and-deployment.md`](80-ops-platform-and-deployment.md) |
| 05 | [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) | | 11 | [`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md) |
| 06 | [`40-api-specification.md`](40-api-specification.md) | | 12 | [`../idrm-ffp-guides/30-contribute-developer-guide.md`](../idrm-ffp-guides/30-contribute-developer-guide.md) *(guide)* |

**Companion + T1 deltas (added 2026-08-14):**
[`61-frontend-engineering-standards.md`](61-frontend-engineering-standards.md) (companion) ·
[`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md) ·
[`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) ·
[`90-governance-and-raci.md`](90-governance-and-raci.md) — each a **delta** on its MVP counterpart.

**Elucidation + conformance (added 2026-08-16):**
[`25-module-elucidation.md`](25-module-elucidation.md) — the *what/why/how* of how each module **evolves** in the
FFP (trigger-gated deltas) · [`26-conformance-pics.md`](26-conformance-pics.md) — the **signed-off** PICS
conformance checklist (added, trigger-gated obligations + rationale + evidence). Twins of the MVP
[`../idrm-mvp-docs/25-module-elucidation.md`](../idrm-mvp-docs/25-module-elucidation.md) / [`../idrm-mvp-docs/26-conformance-pics.md`](../idrm-mvp-docs/26-conformance-pics.md).

## Start here
- **[`prompts/instructions_idrm_ffp_docs.md`](prompts/instructions_idrm_ffp_docs.md)** — the FFP **charter**: what belongs to the next phase, how it relates to the MVP, its source material (the archived generations), and the planned FFP document set.
- **[`prompts/IDRM FFP Architecture - CO-STAR Prompt.md`](prompts/IDRM%20FFP%20Architecture%20-%20CO-STAR%20Prompt.md)** — *(first draft, to refine later)* generation prompt for the FFP architecture document, mirroring the MVP one.

Most FFP content will be **consolidated from the archived generations** (`../idrm-docs-v2/`, `../idrm-docs-v3/`, …), which already describe this microservices/multi-frontend design. The MVP side lives in [`../idrm-mvp-docs/`](../idrm-mvp-docs/). See [`../INDEX.md`](../INDEX.md) for the full archive map.
