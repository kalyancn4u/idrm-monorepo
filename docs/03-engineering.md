# Engineering — How IDRM Is Built

> **Part of:** IDRM Documentation · `03-engineering.md`
> **Answers:** How is IDRM built — where does the code live, what standards guide it, and what is it made of?
> **Source posters:** Posters 17–20 (Phase 3 Engineering)
> **Audience:** Developers (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

1. [Repository structure](#1-repository-structure) — where everything lives.
2. [Coding standards](#2-coding-standards) — the principles we write by.
3. [Design patterns](#3-design-patterns) — the reusable shapes we build with.
4. [Technology stack](#4-technology-stack) — what IDRM is made of, and *why* each piece exists.
5. [Environment & tooling](#5-environment--tooling) — how a developer sets up and works.

---

## 1. Repository structure

IDRM lives in **one repository** with one clear layout. Everything for the application sits under `app/`,
organised by responsibility. A representative structure:

```
idrm_mvp/
├── app/
│   ├── __init__.py           # application factory (wires everything together)
│   ├── config/               # settings per environment (dev / test / prod)
│   ├── models/               # SQLAlchemy models (the data, as Python objects)
│   ├── schemas/              # Pydantic schemas (validate API in/out)
│   ├── services/             # business logic (the actual work), per module
│   ├── apis/                 # FastAPI routers (the REST API endpoints)
│   ├── routes/               # HTML page routes (served by FastAPI)
│   ├── templates/            # Jinja2 HTML templates, styled with Tailwind CSS
│   ├── static/               # Tailwind CSS build, JavaScript, Leaflet, images
│   ├── tasks/                # background jobs (threading / APScheduler)
│   └── utils/                # shared helpers (security, email, etc.)
│
├── migrations/               # Alembic database migrations
├── tests/
│   ├── unit/                 # test individual functions & models
│   ├── integration/          # test modules working together
│   └── conftest.py           # shared test fixtures
│
├── scripts/                  # setup and utility scripts
├── run.py                    # entry point to start the app
├── requirements.txt          # Python dependencies
├── environment.yml           # Miniconda environment (incl. GIS/GDAL)
├── .env.example              # template for configuration
└── README.md
```

**The pattern to notice:** each business module (incident, resource, volunteer, GIS, …) has a slice in
`models/`, `schemas/`, `services/`, and its endpoints in `apis/`/`routes/`. That consistency is what keeps a
single codebase tidy and easy to navigate.

---

## 2. Coding standards

IDRM follows a small set of well-known principles. They exist so any developer can read, trust, and safely
change the code.

| Principle | Plain meaning |
|---|---|
| **SOLID** | Five design guidelines that keep modules focused, loosely coupled, and easy to extend. |
| **DRY** — Don't Repeat Yourself | Say a thing once; reuse it, don't copy-paste. |
| **KISS** — Keep It Simple | Prefer the simplest solution that works. |
| **YAGNI** — You Aren't Gonna Need It | Don't build for imagined future needs; build what's needed now. |
| **Clean Code** | Clear names, small functions, readable structure, meaningful comments. |

**Applying the principles across the full stack** — how each principle shows up in each layer:

| Layer | SOLID | DRY | KISS | YAGNI | Clean Code |
|---|---|---|---|---|---|
| **Frontend** | Component-based, single responsibility | Reusable UI components | Simple, intuitive interfaces | Build only what's needed | Readable components |
| **API / Services** | Separation of concerns, clear contracts | Shared services & utilities | Simple endpoints & logic | Only required APIs | Consistent naming |
| **Data layer** | Repository pattern | Reuse queries & models | Simple queries & mappings | Avoid premature complexity | Readable models |
| **Core / Domain** | Encapsulate domain logic | Reuse domain services | Keep rules simple & clear | Only needed features | Well-named classes |
| **Infrastructure** | Dependency inversion | Reusable adapters & clients | Simple integrations & configs | Only required services | Clean configuration |
| **Testing** | Isolated units & components | Reusable test utilities | Simple, focused tests | Critical paths first | Readable tests |
| **DevOps / Deploy** | Separation of concerns in pipelines | Reusable pipeline configs | Simple automated deploys | Automate what's needed | Clear scripts & docs |
| **Documentation** | Accurate, modular docs | Single source of truth | Clear, concise content | Document what matters | Easy to navigate |

These are enforced in practice by automated checks (formatting, linting, type-checking) described in
[`06-quality.md`](06-quality.md).

---

## 3. Design patterns

A handful of proven patterns give the code predictable shapes, so new features slot in the same way each time.

| Pattern | When to use | What it gives IDRM |
|---|---|---|
| **Repository** | Multiple data sources or complex queries | A clean boundary between business logic and the database. |
| **Factory** | Object creation is complex or varies | A single, consistent way to create objects (e.g. the app factory). |
| **Strategy** | Multiple ways to perform a task | Swappable behaviours (e.g. email vs SMS) without `if/else` sprawl. |
| **Adapter** | Integrating third-party / legacy systems | A uniform way to talk to weather feeds, map services, etc. |
| **Observer** | Events must notify many components | React to "incident created" → notifications, without tight coupling. |
| **Dependency Injection** | Loose coupling & testability needed | Pass in what a component needs, making it testable and flexible. |
| **Facade** | A subsystem is complex, callers need simplicity | A simple front door over a complex subsystem. |

**Where each pattern applies:**

| Layer | Patterns |
|---|---|
| Presentation (Web) | Strategy, Observer, Facade |
| API / Application | Dependency Injection, Facade, Strategy, Factory |
| Domain | Repository, Strategy, Observer |
| Data | Repository, Factory, Adapter |
| Infrastructure | Adapter, Factory, Dependency Injection |
| Integration | Adapter, Facade, Observer |

---

## 4. Technology stack

Everything is chosen to serve the modular monolith: one language, few moving parts, each piece earning its
place. Grouped by the job it does:

### Language & runtime
| Technology | Why it exists |
|---|---|
| **Python 3.12** | One modern language for the whole application — logic, web, APIs, and jobs. |
| **Miniconda** | Manages the Python environment and dependencies (including native geospatial libraries) without the bulk of full Anaconda. |

### Web & API
| Technology | Why it exists |
|---|---|
| **Jinja2 (via FastAPI)** | Renders the HTML web pages server-side — no Flask; the same FastAPI app serves UI + APIs. |
| **Tailwind CSS v4** | Utility-first styling for the HTML pages (replaces Bootstrap). |
| **Vanilla JS + Leaflet** | Light client-side interactivity and the interactive map. |
| **FastAPI** | The one web framework — serves both the HTML web pages and the REST APIs, fast and well-structured. |
| **Pydantic** | Validates data coming in and going out of the APIs. |
| **OpenAPI / Swagger** | Auto-generated, interactive API documentation. |

### Background work
| Technology | Why it exists |
|---|---|
| **threading / ThreadPoolExecutor** | Runs background tasks in-process — no extra servers. |
| **APScheduler** | Runs scheduled/recurring jobs (a built-in scheduler). |

### Data
| Technology | Why it exists |
|---|---|
| **PostgreSQL** | The reliable primary database. |
| **PostGIS** | Adds map/location power to the database. |
| **MinIO** | S3-compatible object storage for uploaded files (no Redis in the MVP — sessions live in PostgreSQL). |
| **SQLAlchemy** | Lets Python work with the database as objects (the ORM). |
| **Alembic** | Applies versioned changes to the database structure. |
| **GDAL** | The geospatial data engine, used from Python (see [`04-data.md`](04-data.md)). |

### Serving & operations
| Technology | Why it exists |
|---|---|
| **Gunicorn** | Process manager running Uvicorn workers for the FastAPI app in production. |
| **Uvicorn** | ASGI server that runs the single FastAPI app (web UI + APIs). |
| **NGINX** (optional) | Reverse proxy for TLS, static files, and routing. |

### Supporting libraries
| Technology | Why it exists |
|---|---|
| **python-dotenv** | Loads configuration from environment files. |
| **Loguru / logging** | Structured application logging. |
| **Requests / httpx** | Talk to external HTTP services (weather, maps, agencies). |

### Quality tooling
| Technology | Why it exists |
|---|---|
| **pytest / pytest-cov** | Run tests and measure coverage. |
| **Ruff / Black / isort** | Lint and auto-format code consistently. |
| **mypy** | Check types to catch mistakes early. |

Full details on testing and CI are in [`06-quality.md`](06-quality.md).

---

## 5. Environment & tooling

- **One environment, reproducible.** Developers create the Python 3.12 environment with **Miniconda** from
  `environment.yml`, which includes the geospatial (GDAL) toolchain. Where a lighter or faster manager suits
  the machine or pipeline, **mamba, micromamba, or uv** may be used instead — the project doesn't depend on
  which one.
- **Configuration by environment.** Settings come from `.env` files (never hard-coded secrets), loaded via
  `python-dotenv`, with separate values for development, testing, and production.
- **Run it locally.** `run.py` starts the application; the web UI and APIs are served together as one app.
- **Specialised setups later.** As needs grow, specialised or isolated environments are expected to move to
  **Docker** images — an additive step that doesn't change the application's shape.

---

## Where this leads

- The data and maps this code works with → [`04-data.md`](04-data.md)
- How it's kept safe → [`05-security.md`](05-security.md)
- How quality is assured → [`06-quality.md`](06-quality.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"Clean, readable, and designed for evolution."*
