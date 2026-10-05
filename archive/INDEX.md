# IDRM Archive — Index & Reading Guide

**Last tidied:** 2026-08-11 · **Status:** Historical reference only

> This `archive/` folder holds the **earlier generations** of IDRM documentation and code.
> It is kept for **history and reference** — it is *not* the current source of truth.
>
> - **Current authoritative documents** live in the top-level [`../docs/`](../docs/) folder.
> - **The design source of truth** is the poster set in [`../posters/`](../posters/) (the "modular monolith" MVP).
> - Everything here predates those and may describe **older, superseded architectures** (microservices, Bun gateway, React/Native, GeoServer). Read it as history, not as instructions to build from.

---

## 1. What was cleaned up (2026-08-11)

The archive was a large pile of overlapping copies, old zip snapshots, and process/status "fluff". It was cleaned up and reorganised in stages. Every removal went through a **quarantine-for-review** step first and was then **permanently deleted** — the `_removed/` holding area has since been cleared and no longer holds anything. Nothing unique was lost: wherever files overlapped, the content was preserved in a retained or merged file and only the redundant copies were removed.

- **Duplicates & superseded versions removed:** ~75 byte-identical duplicates (`- Copy`, `(1)`/`(2)`, and `placeholder/`+`todo/` mirror copies), older `_v2` bases superseded in the same folder, and near-duplicate tracker files (verified by content, not just filename).
- **Old zip snapshots resolved (none remain):** the v3 documentation zips were extracted and consolidated into [`idrm-docs-v3/`](idrm-docs-v3/); the redundant `idrm-docs-v3-2.zip` and the stale `idrm-mvp-3-3.zip` were removed (its one unique file, `schedules/implementation-guide.md`, was first recovered into `schedules/` of the code skeleton — now [`idrm-ffp-code-template/schedules/`](idrm-ffp-code-template/schedules/) after that folder was renamed). The emptied `idrm-v3-artifacts/` folder was removed.
- **Fluff/process docs removed:** ~74 celebration/status/progress/analysis docs across the generations — their genuinely useful history was distilled into each generation's **`CHANGELOG.md`** first, so the facts survive even though the docs are gone.
- **Each generation was then refactored** into a consistent `docs/` + `guides/` (+ `assets/`) structure — see §2 and §3 below and each folder's own `README.md`.

---

## 2. What's in this archive

> **Acronyms:** **MVP** = *Minimum Viable Product* — the lean first build (a modular monolith).
> **FFP** = *Full-Fledged Product* — the later, full-scale enterprise system the MVP evolves into.

The archive holds three kinds of material:

### (a) Product tracks — MVP and FFP
Each track is split into `code` / `docs` / `guides`. The **MVP** (a pure-Python modular monolith) is being written fresh; the archived code skeleton — which is Bun/microservices/React, i.e. **FFP-style** — was moved into the FFP track.

| Folder | Track | Intended for | Status |
|---|---|---|---|
| `idrm-mvp-docs/` → [open](idrm-mvp-docs/) | MVP | MVP specifications | **in progress** (architecture doc + plan) |
| [`idrm-mvp-guides/`](idrm-mvp-guides/) | MVP | MVP novice guides | empty (scaffolding) |
| *(MVP code)* | MVP | the modular-monolith code — **to be built fresh** per the MVP docs (target: top-level `../code/`) | not in archive |
| [`idrm-ffp-code-template/`](idrm-ffp-code-template/) | FFP | Full-Fledged-Product code — the archived Python/**Bun**/React/microservices skeleton (**reference template**; relocated from `idrm-mvp-code`, renamed from `idrm-ffp-code` 2026-08-18) | **populated** (289 files) |
| [`idrm-ffp-docs/`](idrm-ffp-docs/) | FFP | FFP specifications | **in progress** (charter added) |
| [`idrm-ffp-guides/`](idrm-ffp-guides/) | FFP | FFP novice guides | empty (scaffolding) |

### (b) Historical documentation generations (v0 → v3) — ✅ ALL RETIRED (2026-08-12)
Earlier documentation attempts. **All four are now retired to [`_removed/`](_removed/)** (reversible) — their
needful content was consolidated into the **MVP docs**, the **FFP docs**, the **`assets/*.xlsx`**, and
**[`analyses/`](analyses/)** (overviews, LLDs, research, roadmaps). Recover from `_removed/` if a detail is
ever needed (e.g. v3's beginner tutorials → the T2 guide phase).

| Folder | Era | Now contains | Architecture it described |
|---|---|---|---|
| ~~`idrm-docs-v0/`~~ → [`_removed/idrm-docs-v0/`](_removed/idrm-docs-v0/) | earliest | **RETIRED 2026-08-12** — PRDs → MVP; API/data → `assets/*.xlsx`; overviews/LLDs/meta → [`analyses/`](analyses/) | Early / mixed (microservices-leaning) |
| ~~`idrm-docs-v1/`~~ → [`_removed/idrm-docs-v1/`](_removed/idrm-docs-v1/) | early | **RETIRED 2026-08-12** — content verified as consolidated into MVP + FFP docs | Transitional (most-duplicated) |
| ~~`idrm-docs-v2/`~~ → [`_removed/idrm-docs-v2/`](_removed/idrm-docs-v2/) | mid | **RETIRED 2026-08-12** — deep-merged into FFP docs; overview/LLD/roadmap → [`analyses/`](analyses/) | **Microservices** (primary FFP source, consolidated) |
| ~~`idrm-docs-v3/`~~ → [`_removed/idrm-docs-v3/`](_removed/idrm-docs-v3/) | later | **RETIRED 2026-08-12** — deep-merged into FFP docs; overview/LLD/roadmap → [`analyses/`](analyses/); tutorials = T2 guide-source | "Modular monolith" w/ Bun gateway + multi-frontend (primary FFP source, consolidated) |

> **Why these are still "archive":** even `v3` kept a separate gateway, multiple frontends, and Python 3.11. The **posters** removed all of that, so every generation here is superseded by `../posters/` + `../docs/`.

### (c) Shared
- [`assets/`](assets/) — data artifacts shared across generations (the skills tracker, data-model / API-mapping / triggers-views spreadsheets). *(The Ubuntu setup script moved to `scripts/` on 2026-08-12.)*
- [`scripts/`](scripts/) — **shell scripts (added 2026-08-12):** `setup-idrm-ubuntu.sh` (the MVP Ubuntu installer, moved from `assets/`) plus **copies** of the FFP devops scripts from [`idrm-ffp-code-template/backup/`](idrm-ffp-code-template/backup/) (check / install / setup / update `*-devops*`, `_lib.sh`, etc.).
- [`analyses/`](analyses/) — **auxiliary & research material (added 2026-08-12):** docs from the generations that are research/meta/exploratory (not product spec, not merged into MVP/FFP), kept with a generation prefix (e.g. `v0-90-project-odoo-analysis.md`). Distinct from `_removed/` — this content is retained deliberately. See its README + the [FFP consolidation checklist](idrm-ffp-docs/prompts/ffp-consolidation-checklist.md) Part C.
- [`_removed/`](_removed/) — quarantine holding area for review before permanent deletion (currently empty).
- Loose items: two `.pptx` presentations and `idrm-mvp-documentation-blueprint.md`.

---

## 3. How each generation is organised (shared structure)

Every `idrm-docs-vN/` folder now follows the **same** layout, so they read consistently and can be compared/consolidated easily:

- **`README.md`** — router with reading tracks by audience.
- **`docs/`** — specifications & project detail (for practitioners/architects).
- **`guides/`** — elaborate, novice-friendly tutorials & how-tos.
- **`assets/`** (where present) — non-document files (trackers, diagrams, scripts).

Files are named **`<prefix>-<category>-<name>.md`** — the 2-digit prefix orders files; its tens-digit is the category, using this **shared legend**:

- **docs/** — `00` overview · `10` requirements · `20` architecture · `30` design · `40` api · `50` data · `60` uidesign · `70` quality · `80` ops · `90` project
- **guides/** — `00` start · `10` setup · `20` build · `30` contribute · `40` reference

Grounded in **Diátaxis** (guides = tutorials/how-to; docs = reference/explanation) and the spec standards in [`../docs/99-decisions-and-history.md`](../docs/99-decisions-and-history.md) (ISO/IEC/IEEE 29148, arc42/C4, IEEE 1016). The refactor was **lossless** — overlapping files were merged (content preserved, sectioned); replaced sources and duplicates were reviewed via a quarantine step and then removed.

---

## 4. Where to go instead (current, authoritative)

- **Read the finished docs:** [`../docs/`](../docs/) — the numbered `00`–`08`, `90`, `99` reader set, plus `deep-dive/` (SRS, architecture, API, data model, traceability) and `user-guides/`.
- **Design intent / ground truth:** [`../posters/`](../posters/).
- **Presentation:** [`../presentation/`](../presentation/).

*This archive is retained only so the project's history and rationale are recoverable.*
