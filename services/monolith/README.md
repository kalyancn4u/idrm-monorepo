# IDRM MVP — Application Code

The **Integrated Disaster Response Management** MVP: a pure-Python **FastAPI modular monolith**
(HTML + Tailwind CSS v4 + vanilla JS + Leaflet UI, PostgreSQL + PostGIS, MinIO for files).

> Built from the specifications in [`../docs/mvp/`](../docs/mvp/), driven by the signed-off conformance
> checklist [`../docs/mvp/26-conformance-pics.md`](../docs/mvp/26-conformance-pics.md) and the builder's
> **[Implementation Roadmap](../docs/mvp/27-implementation-roadmap.md)**. This folder is the code that roadmap
> describes.

## Quick start (local dev)

```bash
make setup      # create the conda env + install dependencies (once)
make migrate    # build the database schema (Alembic)
make seed       # load rich, realistic sample data
make run        # http://127.0.0.1:8000  (API + docs at /docs)
```

Run `make help` for the full task menu. Before every pull request, run **`make qa`** (format, lint, types,
tests, coverage ≥ 80 %).

## Layout (see roadmap §5)

```
app/
  main.py            # assembles the FastAPI app; wires every module's router
  core/              # cross-cutting: config, logging, security, dependencies, exceptions
  infrastructure/    # database engine/session + base classes
  modules/           # the 10 rooms: users, incidents, resources, locations, alerts,
                     #   notifications, reports, files, audit, administration
tests/               # unit/ · integration/ · api/  (per-module)
alembic/             # migrations (the schema is created only here)
frontend/            # served HTML templates + static css/js/img
scripts/             # seed.py and helpers
```

## Status

**All 10 modules are written** (users · incidents · resources · locations · alerts · notifications · reports ·
files · audit · administration), across **6 Alembic migrations**, with unit/API/integration tests, an idempotent
[`scripts/seed.py`](scripts/seed.py), and a client-side [face-quality gate](frontend/static/js/face-quality.js).
The code is **`ruff`-clean and `py_compile`-clean**, but has **not been executed** — that needs a Linux box with
PostgreSQL/PostGIS + MinIO (this was built on a Windows/docs environment).

**Next step — "the run":** on Ubuntu or CI, `make install && make migrate && make seed && make qa`. Per roadmap
§14, a module's conformance rows flip to ✅ in the PICS ([`../docs/mvp/26-conformance-pics.md`](../docs/mvp/26-conformance-pics.md))
**only when its code and a passing test both exist** — so every `PICS-*` row stays `Planned` until that green run.
See [`../PENDING.md`](../PENDING.md) for the full bring-up checklist.
