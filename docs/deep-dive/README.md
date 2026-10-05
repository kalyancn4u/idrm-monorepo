# IDRM Docs — Developer Deep-Dive

Condensed, developer-grade reference documents that sit *beneath* the overview set in
[`../`](../). They give engineering depth (SRS, architecture, API, data model, ops) in industry-standard formats.

> **Authority note (ADR-012).** These deep-dive docs predate the finalized specifications in
> [`../mvp/`](../mvp/) and [`../ffp/`](../ffp/). Where they still mention **Flask / Jinja / Bootstrap / Redis**,
> defer to the `mvp/` set: the MVP view layer is FastAPI-served **HTML + Tailwind + JS + Leaflet**, with **no
> Redis** (sessions in PostgreSQL) and **MinIO** for files. Each affected file carries an ADR-012 banner right after
> its title. Rationale: [`../99-decisions-and-history.md`](../99-decisions-and-history.md).

## Contents

| File | What it is | Standard / basis |
|---|---|---|
| [`00-plan.md`](00-plan.md) | The deep-dive plan and index | — |
| [`10-srs.md`](10-srs.md) | Software Requirements Specification | ISO/IEC/IEEE 29148 |
| [`11-architecture-and-design.md`](11-architecture-and-design.md) | Architecture & design | arc42 + C4 + IEEE 1016 |
| [`12-api-spec.md`](12-api-spec.md) + [`openapi.yaml`](openapi.yaml) | API specification | OpenAPI 3.1 |
| [`13-data-model.md`](13-data-model.md) | Data model (entities, schema) | Poster 22 |
| [`14-traceability-matrix.md`](14-traceability-matrix.md) | Requirements → design → test traceability | — |
| [`15-ops-runbook.md`](15-ops-runbook.md) | Operations runbook | — |

## When to use this vs. `mvp/`

- For the **authoritative, current** specifications (and the build), use [`../mvp/`](../mvp/) — especially the
  **[Implementation Roadmap](../mvp/27-implementation-roadmap.md)**, the **[data model](../mvp/50-data-model.md)**,
  and the **[API spec](../mvp/40-api-specification.md)**.
- Use these deep-dive docs for the **condensed, standards-framed** view and for historical traceability. Where the
  two differ, `mvp/` wins (ADR-012).
