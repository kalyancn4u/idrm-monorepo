# Deep-Dive (Phase G) — Plan & Standards

> **Part of:** IDRM Documentation · `deep-dive/00-plan.md`
> **Answers:** How will the developer-grade "deep pass" (G1) be produced, to what standards, and in what order?
> **Source posters:** all (as the authoritative baseline) · validated against external standards (see §6)
> **Audience:** Owner / maintainers (planning reference) · **Depth:** Reference
> **Status:** Approved plan — not yet executed

---

## 0. About this file

This is the **approved plan** for the deep-dive pass. It is a planning/reference document, not part of any
reader path. The reader-facing lean set (`docs/00`–`08`, `90`, `99`) stays unchanged; the deep-dive content
**deepens** it and cross-links back to it. All deep-dive documents will be **forward-only** (no legacy detail;
history stays in [`../99-decisions-and-history.md`](../99-decisions-and-history.md)).

**Scope selected:** **G1 — Developer-grade technical documentation.**
**Deferred (not in this pass):** G2 end-user guides (Diátaxis + ISO/IEC/IEEE 26514) and G3 the `.pptx`
presentation — recorded here so they aren't lost, to be planned later.

---

## 1. What G1 produces

Five documents plus one machine-readable API file, in `docs/deep-dive/`:

| # | Artifact | Governing standard | Deepens |
|---|---|---|---|
| 10 | `10-srs.md` — Software Requirements Specification | **ISO/IEC/IEEE 29148:2018** | `01-foundation.md` |
| 11 | `11-architecture-and-design.md` — architecture + detailed design | **ISO/IEC/IEEE 42010:2022**, **arc42**, **C4 model**, **IEEE 1016** | `02-architecture.md` |
| 12 | `12-api-spec.md` + `openapi.yaml` — API reference | **OpenAPI 3.1** | `02`, `03` |
| 13 | `13-data-model.md` — logical + physical model & data dictionary | ERD (crow's-foot), **ISO/IEC 11179** metadata principles | `04-data.md` |
| 14 | `14-traceability-matrix.md` — requirement → design → API → test → doc | **ISO/IEC/IEEE 29148** bidirectional traceability | ties `01`,`02`,`06` together |

Kept intentionally lean: architecture and detailed design are one document (arc42 provides the structure;
IEEE 1016 viewpoints provide the per-module design depth); traceability is one matrix rather than scattered.

---

## 2. Per-artifact outline

### 10 — SRS (ISO/IEC/IEEE 29148)
Purpose & scope · stakeholders · functional requirements (uniquely IDs, e.g. `FR-INC-001`) · non-functional
requirements (measurable) · external interfaces · constraints & assumptions · verification method per
requirement. Each requirement traces to a source poster and forward to design/tests.

### 11 — Architecture & Detailed Design (42010 / arc42 / C4 / IEEE 1016)
arc42 spine: introduction & goals · constraints · context & scope · solution strategy · **building-block view**
(C4 Container/Component) · **runtime view** (key scenarios) · **deployment view** (Ubuntu) · cross-cutting
concepts · architecture decisions (link to ADRs) · quality requirements · risks · glossary link.
**C4 diagrams:** Context → Container → Component (Code level only where it adds value), authored as
diagrams-as-code (e.g. Mermaid/Structurizr). **IEEE 1016 detailed design:** per module — responsibilities,
interfaces, data, dependencies.

### 12 — API Specification (OpenAPI 3.1)
A single `openapi.yaml` (FastAPI auto-generates a base; we validate and enrich: descriptions, examples, error
schemas, auth, versioning `/api/v1`). `12-api-spec.md` explains conventions and how to view it (Swagger UI /
ReDoc). Validated with a linter (e.g. Spectral) and confirmed to render.

### 13 — Data Model (ERD + data dictionary)
Logical ERD (entities, attributes, relationships, keys) · physical notes (types, indexes, PostGIS geometry) ·
**data dictionary** (every table/column: name, type, meaning, constraints) · migration approach (Alembic).

### 14 — Traceability Matrix
One table linking each requirement (from 10) → design element (11) → API operation (12) → test (per `06`) →
user-facing doc. Gives bidirectional traceability and coverage visibility.

---

## 3. Folder structure

```
docs/
├── 00–08, 90, 99            ← approved lean set (unchanged)
└── deep-dive/
    ├── 00-plan.md           ← this file
    ├── 10-srs.md
    ├── 11-architecture-and-design.md
    ├── 12-api-spec.md
    ├── openapi.yaml
    ├── 13-data-model.md
    └── 14-traceability-matrix.md
```

---

## 4. Validation-first production workflow

Applied to **every** deep-dive artifact, in order:

1. **Reason & outline** — map to source poster(s) and the governing standard's template before writing.
2. **Draft** at developer depth.
3. **Review** against the conformance checklist (§5).
4. **Verify / validate** — trace every claim to posters/PRD; lint & render the OpenAPI file; check links;
   run the forward-only check; confirm accessibility of any diagrams (alt text / described).
5. **Emit** — write the artifact, update the README index, add/append ADRs, log in the changelog.

No artifact is emitted until steps 1–4 pass.

## 5. Conformance checklist (reusable quality gate)

- [ ] Traces to a specific poster / requirement (no invented scope).
- [ ] Conforms to the named standard's structure for that artifact.
- [ ] Consistent with the lean set (`00`–`08`) and its terminology (`90-glossary.md`).
- [ ] **Forward-only** — no legacy tech or "what changed" (history lives in `99`).
- [ ] Cross-links resolve; numbering correct.
- [ ] Accessibility: headings, tables, and diagram alt/descriptions (WCAG 2.2 AA mindset).
- [ ] For APIs: `openapi.yaml` passes lint and renders in Swagger UI/ReDoc.
- [ ] Any decision captured as an ADR; change logged.

---

## 6. Validated sources (top trusted)

- Requirements — [ISO/IEC/IEEE 29148:2018](https://www.iso.org/standard/72089.html)
- Architecture description — [ISO/IEC/IEEE 42010:2022](https://en.wikipedia.org/wiki/ISO/IEC_42010) ·
  [arc42](https://arc42.org/) · [C4 model](https://c4model.com/)
- Design descriptions — IEEE 1016 (Software Design Descriptions)
- API — [OpenAPI Specification](https://spec.openapis.org/oas/) (3.1 adopted; 3.2.0 exists, 4.0 not released)
- User-info process (deferred G2) — [ISO/IEC/IEEE 26514:2022](https://www.iso.org/standard/77451.html) ·
  [Diátaxis](https://diataxis.fr/)
- Style — [Google developer documentation style guide](https://developers.google.com/style) ·
  [Microsoft Writing Style Guide](https://learn.microsoft.com/style-guide/welcome/)
- Accessibility — [WCAG 2.2](https://www.w3.org/TR/WCAG22/) (ISO/IEC 40500:2025)
- Decisions & change — [MADR](https://adr.github.io/madr/) · [Keep a Changelog](https://keepachangelog.com/) ·
  [Semantic Versioning](https://semver.org/)

---

## 7. Status & next

**Status:** Plan approved (2026-08-09). Standards recorded as ADR-011 in
[`../99-decisions-and-history.md`](../99-decisions-and-history.md).

**Progress:**
- ☑ `13-data-model.md` — **conformed to Poster 22** (18 named tables, exact columns/relationships/naming).
- ☑ `12-api-spec.md` + `openapi.yaml` — OpenAPI 3.1, resources conform to Poster 22 + the MVP packet-flow
  endpoint examples. Validated: YAML OK, 13 paths, 23 schemas, all 65 `$ref`s resolve; forward-only OK.
- ☑ `10-srs.md` — SRS to ISO/IEC/IEEE 29148 (requirement IDs `FR-*`/`NFR-*`, verification methods).
- ☑ `11-architecture-and-design.md` — arc42 + C4 (context/container/component) + IEEE 1016 per-module design.
- ☑ `14-traceability-matrix.md` — requirements ⇄ design ⇄ API ⇄ entities ⇄ tests ⇄ posters.
- ☑ `15-ops-runbook.md` — Ubuntu setup, deploy, backup cron, restore checklist, routine ops (added in the P3 pass).

**G1 (developer docs) is COMPLETE.** All six artifacts conformed to the posters and passed forward-only checks.

**Conformance gate (standing rule):** before naming/engineering in any artifact, consult the relevant poster
and the Part 4 conformance record in [`../99-decisions-and-history.md`](../99-decisions-and-history.md).

**G2 (end-user guides) — COMPLETE.** `docs/user-guides/`: `00-overview.md` + persona guides for Citizen,
Responder (Volunteers & Emergency Services), Coordinator (District Admin), Administrator. Diátaxis-structured,
conformed to Poster 8 (personas) & Poster 7 (workflow); forward-only verified.

**Deferred:** G3 (`.pptx` presentation).
