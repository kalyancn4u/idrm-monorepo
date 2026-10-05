# IDRM MVP — Developer / Contributor Guide

> *Type: Guide (tutorial / how-to) · Audience: complete novices → experienced devs · Status: MVP — current*
> *"I just joined IDRM — how do I run it and make my first contribution?" You need only know a little Python. This guide gets you from zero to a running app and a merged pull request **without** having to understand the whole system first. Specs it draws on: [`20-architecture-system.md`](../idrm-mvp-docs/20-architecture-system.md), [`80-ops-deployment-and-operations.md`](../idrm-mvp-docs/80-ops-deployment-and-operations.md), [`70-quality-test-strategy.md`](../idrm-mvp-docs/70-quality-test-strategy.md).*

---

## 1. What IDRM is (30 seconds)

A map-driven web platform that connects disaster-affected people with responders. It's **one FastAPI app**
(a "modular monolith") over **PostgreSQL + PostGIS**, with a plain **HTML + Tailwind + JavaScript** web UI
and **MinIO** for uploaded files. That's the whole MVP — no microservices, no React, no Docker (those are
the future "FFP" phase).

---

## 2. Prerequisites

- **Ubuntu 22.04 LTS** (a VM is fine) — the supported dev + deploy target.
- Basic **Python** and comfort in a terminal. Git.
- You do **not** need to know FastAPI, PostGIS, or Tailwind up front — you'll pick them up per task.

---

## 3. One-command setup

The installer sets up everything (PostgreSQL+PostGIS, MinIO, Miniconda, the Python env):

```bash
chmod +x archive/scripts/setup-idrm-ubuntu.sh
./archive/scripts/setup-idrm-ubuntu.sh
```

It's **idempotent** (safe to re-run) and logs to `~/idrm-setup.log`. When it finishes you'll have the
`idrm_db` database, a running MinIO (S3 :9000 / console :9001), and the `idrm-mvp` conda environment.
*(The script's placeholder passwords are fine for local dev; change them for anything shared.)*

---

## 4. Repository structure (where things live)

The backend is organised by **module**, each a vertical slice with the **same shape**:

```
backend/app/
  main.py                  # FastAPI app entry
  core/                    # config, security, shared deps
  db/                      # session, base
  modules/
    incidents/             # ← a module (the pattern repeats)
      router.py            #   HTTP endpoints (the API surface)
      schemas.py           #   Pydantic request/response models
      models.py            #   SQLAlchemy tables
      service.py           #   business logic (calls the repository)
      repository.py        #   the ONLY place that touches the DB
      tests/               #   this module's tests
    users/  organizations/  resources/  alerts/  notifications/  reports/  files/  audit/
  migrations/              # Alembic revisions
frontend/                  # HTML + Tailwind CSS v4 + JS
```

**The golden rule of the layering:** `router → service → repository`. The **service never touches the DB
directly** — it goes through the repository. Keep new code inside the right module.

---

## 5. Run it locally

```bash
conda activate idrm-mvp
# 1) apply the database schema
alembic upgrade head
# 2) start the app (API + static UI)
uvicorn app.main:app --reload --port 8000
```

- App: `http://localhost:8000` · interactive API docs: `http://localhost:8000/docs` (FastAPI auto-generates
  these from the same OpenAPI contract as [`40-api-openapi.yaml`](../idrm-mvp-docs/40-api-openapi.yaml)).
- Health check: `http://localhost:8000/api/v1/health`.

---

## 6. Run the tests

```bash
conda activate idrm-mvp
pytest                     # whole suite
pytest app/modules/incidents/tests   # just one module
pytest --cov=app           # with coverage
```

Tests use a **disposable test database** and a **test MinIO bucket** — they never touch real data. See the
[test strategy](../idrm-mvp-docs/70-quality-test-strategy.md): write **Unit** tests for logic, **API** tests
for endpoints, **Integration** tests for flows through PostgreSQL/PostGIS.

---

## 7. Coding conventions

Enforced automatically — run them before you push:

```bash
black . && isort .         # formatting
ruff check .               # linting
mypy app                   # type checks
```

- **snake_case** everywhere; **UUID** ids; **ISO-8601 UTC** timestamps (matches the API/data model).
- Validate input with **Pydantic**; never build SQL by string concatenation (use SQLAlchemy).
- Keep the module boundaries; put DB access **only** in `repository.py`.

---

## 8. Make a change (branch → PR)

```bash
git switch -c feat/incidents-add-filter      # small, focused branch
# ...make your change + add tests...
black . && isort . && ruff check . && mypy app && pytest
git commit -m "incidents: add priority filter to list endpoint"
git push -u origin feat/incidents-add-filter
```

- **Branch names:** `feat/…`, `fix/…`, `docs/…`, `chore/…`.
- **Commits:** present-tense, module-prefixed, one logical change each.
- **Open a Pull Request** describing *what* and *why*; link the requirement/feature (F1–F11) it serves. CI
  runs format+lint+types+tests+coverage — all must be green.

---

## 9. Definition of Done (before you ask for review)

- Acceptance criteria for the feature each have a **passing test** (doc 11 §7).
- Edge cases handled (validation, illegal lifecycle transitions, permission denials).
- **RBAC** enforced on any new endpoint ([`22-architecture-security-and-iam.md`](../idrm-mvp-docs/22-architecture-security-and-iam.md)).
- Significant actions are **audited**; the relevant MVP doc/CHANGELOG updated.
- `black · isort · ruff · mypy · pytest (≥ 80% coverage)` all pass.

---

## 10. Module ownership & where to go next

- Each module has an owner; tag them on PRs touching their module.
- **New endpoint?** update [`40-api-specification.md`](../idrm-mvp-docs/40-api-specification.md) + the
  OpenAPI file. **New table/column?** add an **Alembic** migration and update
  [`50-data-model.md`](../idrm-mvp-docs/50-data-model.md).
- Anything advanced you're tempted to add (Redis, Docker, React, a broker, biometric ML) is **FFP** — raise
  it as an ADR, don't slip it into the MVP (see the [ADRs](../idrm-mvp-docs/21-architecture-decisions.md)).

Welcome aboard — start with a small module-local change, get it green, and open your first PR. 🚀
