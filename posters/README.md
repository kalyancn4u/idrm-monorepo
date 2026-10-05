# IDRM Posters — the authoritative product vision

> **These posters are the single source of truth for IDRM.** Everything in [`../docs/`](../docs/) and
> [`../guides/`](../guides/) is written to match them. When a finalized specification refines a poster (see the
> ADR-012 note below), the spec wins *and* the poster is flagged to be updated to match.

This folder holds **35 posters** (as PNG images) that tell IDRM's story from concept to execution, organised into
**9 phases (0–8)**. Some posters span **multiple pages** — those are the `_0`, `_1` suffixes on the same poster
number (e.g. `..._poster_01_0.png` + `..._poster_01_1.png`). Filenames follow
`idrm_phase_<NN>_poster_<NN>_<page>.png`, so they sort in reading order.

---

## How to read them

Open them in phase order (0 → 8). Each phase was distilled into a chapter of the overview documentation, so you can
read a poster phase and then its written counterpart for depth. The mapping:

| Phase | Posters | Theme | Written up in |
|---|---|---|---|
| **0 — Concept** | 01–04 | Vision, the problem, "why IDRM exists" | [`../docs/01-foundation.md`](../docs/01-foundation.md) |
| **1 — Foundation** | 05–08 | Scope, stakeholders, domains, the incident lifecycle & workflow | [`../docs/01-foundation.md`](../docs/01-foundation.md) |
| **2 — Architecture** | 09–16 | *What* IDRM is: system, layers, functional design, the modules, flows, evolution | [`../docs/02-architecture.md`](../docs/02-architecture.md) |
| **3 — Engineering** | 17–20 | *How* it's built: repository, standards, patterns, the technology stack | [`../docs/03-engineering.md`](../docs/03-engineering.md) |
| **4 — Data & maps** | 21–23 | The database, entities, and the GIS (geographic) layer | [`../docs/04-data.md`](../docs/04-data.md) |
| **5 — Security** | 24–25 | Security architecture and the threat model | [`../docs/05-security.md`](../docs/05-security.md) |
| **6 — Quality** | 26–27 | How we know it works: testing and CI/CD | [`../docs/06-quality.md`](../docs/06-quality.md) |
| **7 — Operations** | 28–30 | Running it: Ubuntu deployment, observability, disaster recovery | [`../docs/07-operations.md`](../docs/07-operations.md) |
| **8 — Organization & big picture** | 31–35 | Roles & ownership, the decision matrix, training paths, the roadmap, and the Big Picture (35) | [`../docs/08-organization.md`](../docs/08-organization.md) |

*(New here? Start with the [documentation front door](../docs/README.md), which threads these into a reading path
by role.)*

---

## The one refinement to be aware of (ADR-012)

The finalized MVP specifications refined **two** stack specifics from the original posters, and the specs are
authoritative on these points (the posters should be updated to match):

1. **View layer** = FastAPI-served **HTML + Tailwind CSS v4 + vanilla JS + Leaflet** (not Flask/Jinja/Bootstrap).
2. **No Redis** in the MVP (sessions live in PostgreSQL); **MinIO** is added for file storage.

Full rationale: [`../docs/99-decisions-and-history.md`](../docs/99-decisions-and-history.md) (ADR-012).

---

## Poster inventory (by phase)

- **Phase 0 — Concept:** `poster_01` (2 pages), `poster_02`, `poster_03`, `poster_04`
- **Phase 1 — Foundation:** `poster_05`, `poster_06`, `poster_07`, `poster_08`
- **Phase 2 — Architecture:** `poster_09` … `poster_16` (8 posters)
- **Phase 3 — Engineering:** `poster_17`, `poster_18` (2 pages), `poster_19`, `poster_20` (2 pages)
- **Phase 4 — Data & maps:** `poster_21`, `poster_22`, `poster_23` (2 pages)
- **Phase 5 — Security:** `poster_24` (2 pages), `poster_25`
- **Phase 6 — Quality:** `poster_26`, `poster_27`
- **Phase 7 — Operations:** `poster_28`, `poster_29`, `poster_30` (each 2 pages)
- **Phase 8 — Organization & big picture:** `poster_31` (2 pages), `poster_32`, `poster_33`, `poster_34`, `poster_35`

*44 image files · 35 posters · ~78 MB total. These are the visual master; the documentation is their written,
searchable derivation.*
