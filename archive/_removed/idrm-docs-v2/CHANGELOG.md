# Changelog — idrm-docs-v2

> Historical record for this archived generation. Distilled from status/completion/audit docs
> that were removed on 2026-08-11 so no factual history is lost.
> This generation is **superseded** — see [`../INDEX.md`](../INDEX.md) and the current
> [`../../docs/`](../../docs/) set. The stack named here (microservices/Bun) is history, not current guidance.

## v2 — 2026-05-10 (complete rewrite)
- Declared **100% complete**: 14 new `*-v2` files on top of the earlier set.
- **Technology-stack decisions finalized in this generation** (the defining v2 change):
  | Layer | v2 decision | Replaced |
  |---|---|---|
  | Reverse proxy | **NGINX** | — |
  | API gateway | **Bun** | Node.js |
  | Services runtime | **Python (Miniconda)** microservices | `venv` |
  | Geospatial | **Python geospatial service** | Java **GeoServer** |
  | Cache | **Redis** | — |
  | Database | **PostgreSQL + PostGIS** | — |
  | Frontend | **HTML/CSS/JS + Tailwind** (primary) | — |
- **Core specs (kept in this folder):** `IDRM-MVP-PRD-v2.md`, `IDRM-HLD-v2.md`, `IDRM-LLD-v2.md`,
  `IDRM-FS-v2.md`, `architecture-decisions.md`, `monolith-architecture.md`, setup guides,
  `MASTER-BEGINNERS-GUIDE.md`, `gap-analysis-and-roadmap.md`, `executive-summary.md`.

## Audit finding — 2026-05-10
- A documentation audit against PRD v2.0 found **9 older uploaded documents contained outdated
  stack references** conflicting with v2 → they were to be archived, not merged. (This is the
  origin of the v0/v1 → v2 supersession recorded across the archive.)

## Housekeeping — 2026-08-11
- Removed 5 status/completion/audit fluff docs (facts above preserved):
  `DOCUMENTATION-STATUS.md`, `FRONTEND-DOCS-STATUS.md`, `FINAL-COMPLETION-SUMMARY.md`,
  `FINAL-VALIDATION-REPORT.md`, `UPLOADED-DOCS-AUDIT-REPORT.md`.
- Note: the older `setup-prerequisites.md` and `idrm-instructions_setup_staging.md` were
  earlier superseded by their `_v2` versions and were removed as well.
