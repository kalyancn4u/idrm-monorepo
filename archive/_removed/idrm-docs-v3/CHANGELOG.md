# Changelog — idrm-docs-v3

> Historical record for this archived generation. Distilled from the ~30 batch/status/analysis/
> completion docs removed on 2026-08-11 so no factual history is
> lost. This generation is **superseded** — see [`../INDEX.md`](../INDEX.md) and the current
> [`../../docs/`](../../docs/) set. It called itself a "modular monolith" but still carried a Bun
> gateway, multiple frontends, and Miniconda/Python 3.11 — the **posters** later removed all of that.

## v3 — 2026-05-24
- Positioned as a **"modular monolith"** evolution of v2, but retained the **Bun API gateway**,
  **three frontend platforms**, and **Miniconda / Python 3.11**.
- **Three frontend platforms** introduced/documented: HTML + Tailwind, React SPA, React Native
  (with cross-platform design tokens, iOS HIG / Material notes, WCAG 2.1 AA).
- **6 new v3 guides created** (~25,000 lines), e.g. `design-system-v3.md`,
  `setup-prerequisites-v3.md`, `setup-staging-v3.md`, `setup-production-v3.md`,
  `production-ci-cd-readme-v3.md`, `gap-analysis-and-roadmap-v3.md`.

### Evolution findings recorded during v3
- **v2 core specs judged solid** (PRD, HLD, LLD, FS) — kept as baseline.
- **18 documents flagged as needing v3 updates** (unique content not yet in the v2 specs).
- **4 documents completely outdated** → to be archived (e.g. `setup-prerequisites.md`
  replaced by `setup-prerequisites_v2.md`).
- **5 PNG diagrams** to be re-expressed as **Mermaid** equivalents.

### Kept in this folder (real content)
- Numbered doc set `00-GETTING-STARTED` … `51-BUN-API-GATEWAY-GUIDE`; `IDRM-HLD/LLD/PRD-v3`;
  `API-CONTRACTS-v3`, `DATABASE-SCHEMAS-v3`, `MOCK-DATA-GUIDE-v3`, `TESTING-STRATEGY-v3`,
  `MERMAID-DIAGRAMS.md`, `PROJECT-STRUCTURE-v3`, and the **decisions log**
  `IDRM-V3-CLARIFICATIONS-AND-DECISIONS.md` (15 recorded decisions).

## Housekeeping — 2026-08-11
- This folder was **assembled** on 2026-08-11 by extracting + consolidating 6 old v3 zip
  snapshots (88 files, deduplicated; see `../INDEX.md`).
- Then removed ~30 process/status docs (facts above preserved): the `BATCH-*`,
  `PROGRESS-REPORT`, `SESSION-COMPLETION-SUMMARY`, `HANDOFF*`, `COMPLETION-REPORT`,
  `*-STATUS`, `*-ANALYSIS`, `*-VALIDATION`, `REDUNDANT-DOCS-LIST`, `OUTDATED-DOCUMENTS-LIST`,
  `LATEST-DOCUMENTS-TO-USE`, `DOCUMENT-VERSION-MAPPING`, `CONSOLIDATION-PLAN`,
  `v3-UPDATE-REQUIREMENTS`, `README-v3-OLD-BACKUP`, and similar bookkeeping files.
