# IDRM MVP — Code Walk-Through

**A guided, presentation-style tour of the MVP application code, written for complete
beginners who want to reach real mastery — not just "run it," but understand *why*
every piece is shaped the way it is.**

You do not need prior experience with FastAPI, PostGIS, JWT auth, or async Python.
Each concept is introduced from zero, shown in the actual code, and reinforced with
footnotes, pitfalls, and small exercises.

> **What this covers:** the code under [`services/monolith/`](../../services/monolith/) — a pure-Python
> **FastAPI modular monolith** (HTML + Tailwind + JS + Leaflet UI, PostgreSQL 16 +
> PostGIS 3.4, MinIO for files). It pairs with the product specs in
> [`docs/mvp/`](../mvp/) and the builder's [Implementation Roadmap](../mvp/27-implementation-roadmap.md).

---

## How this walk-through is organized

The tour follows the **path a request travels** through the system — client → app →
router → guards → service → repository → PostgreSQL — because understanding the flow
is the fastest route to understanding the parts.

Each chapter is a **mini-presentation**: it is split into "slides" separated by a
horizontal rule (`───`). Every slide ends with a **Footnotes** block that defines
jargon, explains the reasoning, flags pitfalls, and points to further reading. Read
them — the footnotes are where the nuance lives.

> **📺 Live slides:** the decks publish to GitHub Pages on every push once Pages is
> enabled — **[view them online](https://kalyancn4u.github.io/idrm-monorepo/)**
> (combined deck + one per chapter). See [`.github/workflows/pages.yml`](../../.github/workflows/pages.yml).

> **Two ways to read it**
> 1. **As a document** (recommended first pass): just scroll — it reads top to bottom
>    like a book with slide breaks.
> 2. **As slides** (for teaching/presenting): build every chapter — plus one combined
>    deck — into self-contained HTML with the included script:
>    ```bash
>    ./scripts/build_slides.ps1     # Windows (PowerShell);  add -Pdf for PDFs
>    ./scripts/build_slides.sh      # macOS/Linux;           add --pdf for PDFs
>    ```
>    Decks land in `docs/walkthrough/slides/` — right beside these chapters (open
>    `walkthrough-full.html`). The script injects Marp front-matter into temporary
>    copies, so the source files stay clean for GitHub. **Requires [Node.js](https://nodejs.org)**
>    (Marp CLI is fetched automatically via `npx`).

---

## The learning path (read in order)

| # | Chapter | What you'll master |
|---|---------|--------------------|
| 1 | [The Big Picture](01-big-picture.md) | The modular-monolith architecture, the 10 modules, the request journey, and the three design laws that hold everything together |
| 2 | [Anatomy of a Module](02-anatomy-of-a-module.md) | The five-layer shape — `models · schemas · repository · service · router` — and why that separation makes the code testable and swappable |
| 3 | [Configuration & App Assembly](03-configuration-and-app-assembly.md) | Where every setting lives (`core/config.py`), how `main.py` assembles the app, middleware, the health probe, and request-id correlation |
| 4 | [Observability & Errors](04-observability-and-errors.md) | Structured JSON logging with PII redaction, and the single error envelope every failure returns |
| 5 | [The Data Layer](05-the-data-layer.md) | Async SQLAlchemy, the shared Base + UUID/timestamps/soft-delete mixins, the repository pattern, and Alembic migrations |
| 6 | [Security, Auth & RBAC](06-security-auth-and-rbac.md) | RS256 JWT, bcrypt, the dependency guards + guest path, per-endpoint rate limiting, and the full auth lifecycle |
| 7 | [The Incident Lifecycle](07-the-incident-lifecycle.md) | The 8-state machine at the heart of the domain, and the service rules (single-claim, critical-approval, ownership) that enforce it |
| 8 | [Geospatial with PostGIS](08-geospatial-with-postgis.md) | Proximity search (`ST_DWithin`), the `locations` module, GeoJSON for the map, and the offline reverse-geocoder |
| 9 | [Cross-Cutting: Audit · Notifications · Files](09-cross-cutting-audit-notifications-files.md) | Router-edge composition, the append-only audit trail, and the object-storage + image pipeline for uploads |
| 10 | [The API Contract & Responses](10-the-api-contract-and-responses.md) | The frozen `/api/v1` conventions, the `{data, pagination}` helper, list filters, OpenAPI, and the error catalog |
| 11 | [Testing & Quality](11-testing-and-quality.md) | The per-module `unit/api/integration` layout, the test fixtures, the quality gate, and the "written-but-unrun-here" reality |
| 12 | [Mastery: End-to-End & Exercises](12-mastery-end-to-end.md) | A full trace of one request through every layer, extension projects, and a self-assessment |

**Reference:** [Glossary of terms](GLOSSARY.md) — every piece of jargon, defined
plainly, cross-linked from the footnotes.

---

## Conventions used throughout

- **Code excerpts are illustrative**, often trimmed for focus. Each links to the real
  file so you can read it in full — e.g. [`app/main.py`](../../services/monolith/app/main.py).
- Inline markers like `[1]` point to the bulleted **Footnotes** block at the bottom of
  that same slide (one bullet per reference).
- 🧠 **Nuance** callouts highlight a subtle "why." ⚠️ **Pitfall** callouts warn of a
  common mistake. 🛠️ **Try it** callouts are hands-on exercises.
- Terms in **bold italic** like ***idempotent*** are defined in the [Glossary](GLOSSARY.md).
- An **honest scope note** appears wherever the MVP defers something to the FFP —
  saying what would change the decision.

---

## Before you start (optional but helpful)

This app is not a single-file script — it needs **PostgreSQL + PostGIS + MinIO** to run.
The fastest way to see it live is the Ubuntu bring-up checklist in
[`PENDING.md` §1](../../PENDING.md); the day-to-day commands are in
[`services/monolith/README.md`](../../services/monolith/README.md):

```bash
cd code
make install    # dependencies
make migrate    # build the schema (Alembic)
make seed       # load realistic sample data
make run        # http://127.0.0.1:8000  (API docs at /docs)
```

If any of that is unfamiliar, don't worry — **Chapter 1** explains the shape of the
system before we open a single file, and each later chapter names exactly which files
it covers.

---

*This walk-through documents the code as of the MVP build (2026). It reads on GitHub as
a book and renders as slides with the included [build kit](../../scripts/build_slides.sh).
For the authoritative product vision, see the [posters and specs](../mvp/); for what's
left to do, see [`PENDING.md`](../../PENDING.md).*
