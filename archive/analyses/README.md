# archive/analyses/ — auxiliary & research material (kept, not discarded)

*Type: folder index · Status: shared archive*

This folder holds documents from the generations (`idrm-docs-v0..v3`) that are **auxiliary** — research,
gap-analysis, meta/tooling, prompt libraries, exploratory studies, and superseded design references. They
are **not part of the frozen product doc sets** (MVP = [`../idrm-mvp-docs/`](../idrm-mvp-docs/), FFP =
[`../idrm-ffp-docs/`](../idrm-ffp-docs/)) and do **not** merge into a spec — but they are **worth keeping**,
so they live here rather than being deleted.

**Convention:**
- Files keep a **generation prefix** to preserve provenance, e.g. [`v0-90-project-odoo-analysis.md`](v0-90-project-odoo-analysis.md).
- This is **not** `_removed/` — content here is retained deliberately. `_removed/` remains the quarantine
  for genuine deletion.
- Live product docs should reference `analyses/` freely (unlike `_removed/`).

**What belongs here** (see the triage in
[`../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md`](../idrm-ffp-docs/prompts/ffp-consolidation-checklist.md) Part C):
research/analysis (e.g. Odoo governance study), documentation-*validation tooling*, prompt libraries,
gap-analyses not folded into a roadmap doc, and (optionally) exhaustive superseded LLDs kept as design
reference once their decisions are captured in the specs.

## Contents

**Research / meta (moved 2026-08-12):**
| File | Origin | What it is |
|---|---|---|
| [`v0-90-project-odoo-analysis.md`](v0-90-project-odoo-analysis.md) | idrm-docs-v0/docs | Odoo/ERP options for governance activities (exploratory research) |
| [`v0-70-quality-multilingual-validation.md`](v0-70-quality-multilingual-validation.md) | idrm-docs-v0/docs | Documentation multilingual-validation *system* (meta-tooling analysis) |
| [`v0-71-quality-periodic-validation.md`](v0-71-quality-periodic-validation.md) | idrm-docs-v0/docs | Documentation periodic-validation *system* (meta-tooling analysis) |
| [`v0-41-reference-prompts.md`](v0-41-reference-prompts.md) | idrm-docs-v0/guides | CO-STAR prompt library (authoring aid) |

**Historical overviews (superseded by posters + MVP/FFP overviews; moved 2026-08-12):**
| File | Origin | What it is |
|---|---|---|
| [`v0-00-overview-presentation.md`](v0-00-overview-presentation.md) | idrm-docs-v0/docs | Complete system presentation (2361 L) |
| [`v2-00-overview-vision-and-scope.md`](v2-00-overview-vision-and-scope.md) | idrm-docs-v2/docs | v2 documentation-package executive summary |
| [`v3-00-overview-vision-and-scope.md`](v3-00-overview-vision-and-scope.md) | idrm-docs-v3/docs | v3 documentation-package executive summary |

**Exhaustive low-level design — kept as design reference (code is built fresh from the specs; moved 2026-08-12):**
| File | Origin | What it is |
|---|---|---|
| [`v0-30-design-detailed-lld.md`](v0-30-design-detailed-lld.md) | idrm-docs-v0/docs | **Comprehensive LLD (24,589 L)** — 21 category LLDs (edge/auth/core/geo/realtime/data/infra/security/monitoring/analytics/db/financial) |
| [`v0-31-design-components-list.md`](v0-31-design-components-list.md) | idrm-docs-v0/docs | LLD components list |
| [`v0-32-design-master-checklist.md`](v0-32-design-master-checklist.md) | idrm-docs-v0/docs | LLD master checklist |
| [`v0-33-design-deepdive.md`](v0-33-design-deepdive.md) | idrm-docs-v0/docs | Technical deep-dive & best practices |
| [`v0-34-design-devops-lld.md`](v0-34-design-devops-lld.md) | idrm-docs-v0/docs | DevOps LLD (stub) |
| [`v2-30-design-detailed-lld.md`](v2-30-design-detailed-lld.md) | idrm-docs-v2/docs | v2 low-level design (2061 L) |
| [`v3-30-design-detailed-lld.md`](v3-30-design-detailed-lld.md) | idrm-docs-v3/docs | v3 detailed design / LLD (3859 L) |

**Gap-analysis roadmaps (moved as their generation retired):**
| File | Origin | What it is |
|---|---|---|
| [`v2-90-project-roadmap.md`](v2-90-project-roadmap.md) | idrm-docs-v2/docs | v2 gap-analysis & artifact roadmap (plan merged into FFP-02) |
| [`v3-91-project-roadmap.md`](v3-91-project-roadmap.md) | idrm-docs-v3/docs | v3 gap-analysis & roadmap (plan merged into FFP-02) |

> **Note:** all versioned generations (v1–v3) are now retired to `_removed/`; only `v0` remains (trimmed).
> v3's beginner **tutorials** (Redis-101, FastAPI-from-scratch, Bun-gateway) live in `_removed/idrm-docs-v3/`
> and are **guide-source for the pending T2 guides** — recover from there rather than re-deriving.
