# IDRM — Integrated Disaster Response Management

**IDRM** is an India-focused, web-based, **map-driven platform that connects disaster-affected people with the
organizations and responders who can help them** — incidents (help requests), resources, volunteers, alerts,
coordination, and reporting. Think *"Uber for disaster relief."*

This repository is the **complete artifact set** for IDRM: the product vision, the full documentation, the built
MVP application code, the learning library, the forward-looking design white papers, and the reference material.
It is written so a **complete newcomer can orient in minutes and reach mastery** — every folder has its own README.

---

## 0. Status at a glance (2026-08-18)

| Area | State |
|---|---|
| **Product vision** (`posters/`) | ✅ 35 posters across 9 phases — the authoritative source |
| **Documentation** (`docs/`, `guides/`) | ✅ Complete — MVP + FFP specs, 40 "101" guides + 12 role guides, roadmap, glossary |
| **MVP application code** (`code/`) | 🟢 **All 10 modules written** (FastAPI modular monolith, 6 migrations, tests, seed) — `ruff` + `py_compile` clean, **not yet executed** (needs a Linux box with PostgreSQL/PostGIS/MinIO) |
| **Design white papers** (`docs/whitepapers/`) | ✅ 6 "intelligence-engine" papers (design-now / build-FFP) + a face-quality-gate note |
| **The one open step** | ▶️ **The run** — `make install && migrate && seed && qa` on Ubuntu/CI, which turns "written" into "verified" (see [`PENDING.md`](PENDING.md)) |

> **The two phases.** IDRM ships as an **MVP** (Minimum Viable Product — a deliberately simple, single-server app
> that works today) that evolves *without a rewrite* into the **FFP** (Full-Fledged Product — the enterprise
> version: selective microservices, an API gateway, mobile apps, brokers). Every document is labelled with the
> phase it belongs to.

---

## 1. Start here — pick your path

| You are… | Open this first |
|---|---|
| **New to IDRM** (any role) | [`docs/README.md`](docs/README.md) → then [`docs/00-orientation.md`](docs/00-orientation.md) — the shortest path in |
| **Building the MVP code** | [`docs/mvp/27-implementation-roadmap.md`](docs/mvp/27-implementation-roadmap.md) (the builder's guide) → then [`code/README.md`](code/README.md) |
| **Running / deploying it** | [`PENDING.md`](PENDING.md) §1 — the Ubuntu bring-up checklist |
| **A stakeholder / sponsor** | [`docs/09-roadmap.md`](docs/09-roadmap.md) (the whole journey) + [`presentation/`](presentation/) (the decks) |
| **Learning a topic (novice→mastery)** | [`guides/mvp/learn/`](guides/mvp/learn/) — 40 "101" guides |
| **Understanding the CODE (novice→mastery)** | [`docs/walkthrough/`](docs/walkthrough/README.md) — a 12-chapter code walk-through (reads as a book on GitHub; also renders as slides) |
| **Curious about the "smart" features** | [`docs/whitepapers/`](docs/whitepapers/) — the FFP intelligence engines |

---

## 2. Repository map

```
idrm-artifacts/
├── README.md            ← you are here (the repository front door)
├── PENDING.md           ← what's left to do + the Ubuntu bring-up checklist (read for hand-off)
├── posters/             ← 🎯 the AUTHORITATIVE product vision — 35 phase posters (start of truth)
├── docs/                ← all documentation (overview + full MVP & FFP specs + white papers)
│   ├── mvp/             ←   the MVP specifications + the Implementation Roadmap (27)
│   ├── ffp/             ←   the FFP (enterprise) specifications (deltas on the MVP)
│   ├── walkthrough/     ←   the 12-chapter CODE walk-through (novice→mastery; GitHub docs + Marp slides)
│   ├── whitepapers/     ←   6 design-now/build-FFP "intelligence engine" papers
│   ├── deep-dive/       ←   condensed developer deep-dive docs (SRS, arch, API, data, ops)
│   └── user-guides/     ←   task-oriented end-user guides (citizen, responder, coordinator, admin)
├── guides/              ← the novice→mastery LEARNING library (40 "101s" + 12 role journeys)
│   ├── mvp/             ←   MVP learning hub + learn/ (101s) + roles/ (role journeys)
│   └── ffp/             ←   FFP learning hub (delta)
├── code/                ← 🟢 the MVP APPLICATION CODE (FastAPI modular monolith) — the deliverable
├── presentation/        ← stakeholder decks (pptx/pdf) + companion notes
└── archive/             ← working history: doc-set masters, analyses, the FFP code TEMPLATE, retired drafts
```

Every folder above has a **README** (or INDEX) explaining its contents — open the folder to get oriented.

---

## 3. What the MVP is (the locked shape)

A pure-Python **FastAPI modular monolith** — one deployable app, ten clean modules:

- **UI:** FastAPI-served **HTML + Tailwind CSS v4 + vanilla JS + Leaflet** (no React/Node in the MVP)
- **Data:** **PostgreSQL 16 + PostGIS 3.4** (the single source of truth) + **MinIO** (S3-compatible file storage)
- **Auth:** RS256 JWT, RBAC over 4 roles (citizen · provider · coordinator · admin) + a guest path
- **The 10 modules:** users · incidents · resources · locations · alerts · notifications · reports · files ·
  audit · administration
- **Deployment:** native **systemd on Ubuntu** (no Docker in the MVP)

The **FFP** grows this — on concrete triggers, one module at a time (Strangler-Fig) — into selective
microservices behind an **APISIX** gateway, React web + React Native mobile, brokers, and Kubernetes, **keeping the
same `/api/v1` contract**. See [`docs/ffp/`](docs/ffp/).

---

## 4. Running the MVP (quick pointer)

The code is complete but has only been static-checked here (this was a Windows/docs box). To actually run it, use a
Linux box with the stack installed (full steps in [`PENDING.md`](PENDING.md) §1):

```bash
cd code
make install    # dependencies
make migrate    # build the schema (Alembic)
make seed       # load rich, realistic sample data
make run        # http://127.0.0.1:8000  (API docs at /docs)
make qa         # format · lint · types · tests · coverage ≥ 80%
```

---

## 5. The single source of truth

The **`posters/`** are the authoritative product vision, refined by the finalized specifications in
[`docs/mvp/`](docs/mvp/) + [`docs/ffp/`](docs/ffp/). Where a finalized spec refines a poster (the view-layer stack
and the no-Redis/+MinIO decisions — ADR-012), the spec wins and the posters are flagged to be updated to match.
Decisions and their rationale are recorded in [`docs/99-decisions-and-history.md`](docs/99-decisions-and-history.md).

---

## 6. For the hand-off / knowledge transfer

- **The authoritative status board** is [`archive/instructions.txt`](archive/instructions.txt) §15 — the live
  record of what's done, what's pending, and the one constraint that shapes everything (this box can't run the code).
- **The pending checklist** (self-contained, for a fresh session on the Ubuntu server) is [`PENDING.md`](PENDING.md).
- **Nothing is "done/conformant" until it runs green** — every `PICS-<module>-*` conformance row stays `Planned`
  until a green `make qa` on Ubuntu/CI (roadmap §14). That run is the next milestone.
