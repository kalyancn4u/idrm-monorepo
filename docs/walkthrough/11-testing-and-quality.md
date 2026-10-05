# Chapter 11 — Testing & Quality

*How we prove the system works — and test a database-backed app without brittleness.*

**By the end of this chapter you will be able to:** describe the test layout, explain the
fixtures, know which tests run without a database, and use the one-command quality gate.

Files: [`tests/`](../../code/tests/), [`tests/conftest.py`](../../code/tests/conftest.py),
[`code/Makefile`](../../code/Makefile).

---

## Three kinds of test, one folder per module

Tests mirror the code: each module has its own subfolder under three levels, the classic
**test pyramid**.[1]

```text
tests/
├── unit/         # pure logic, no DB (geo, lifecycle, pagination, hashing…)  — many, fast
├── api/          # one endpoint via an in-process HTTP client                — medium
└── integration/  # a whole flow across modules (e.g. created → verified)     — fewer, broad
    └── <module>/…
```

🧠 **Nuance:** per-module test folders are **Task N** — each module is independently
testable, which is the same seam that lets it later become its own service.[2]

> **Footnotes**
>
> - **[1]** The ***test pyramid***: lots of fast unit tests at the base, fewer API tests, a thin layer of broad integration tests on top. Fast tests catch most bugs cheaply; the few slow ones prove the pieces connect. Inverting it (mostly slow end-to-end tests) makes a suite that's slow and flaky.
> - **[2]** Independent testability = low coupling made verifiable. If a module's tests need half the app spun up, the module is too entangled. IDRM's do not — which is the practical proof of Design Law #3.

---

## The fixtures: a real database, isolated per test

`conftest.py` does the un-obvious but essential setup. First, it configures the
environment **before importing the app** — because settings are cached at import
(Ch 3):[1]

```python
# tests/conftest.py (trimmed) — this runs at import time, ABOVE `from app.main import app`
_generate_rs256_keypair()                       # ephemeral keys, so RS256 signing works in tests
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://idrm_user:test@localhost:5432/idrm_test")
os.environ["JWT_PRIVATE_KEY_PATH"] = str(_TMP / "jwt_private.pem")
```

Then a per-test schema is created and dropped, giving each test a clean database:[2]

```python
# tests/conftest.py (trimmed)
@pytest_asyncio.fixture
async def _schema():
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
```

> **Footnotes**
>
> - **[1]** Generating an ***ephemeral*** RS256 keypair (thrown away after the run) means auth is exercised for real — tokens are genuinely signed and verified — without shipping test keys. Setting env *before* import is the flip side of the cached-settings gotcha from Chapter 3.
> - **[2]** ***Test isolation***: create-then-drop the whole schema per test so no test can see another's rows. It's a little slower than sharing a DB, but it removes the single biggest source of flaky, order-dependent test failures. A `reset_rate_limits` autouse fixture likewise clears the in-process counters between tests.

---

## Two fixtures the tests actually ask for

Tests declare `client` (an in-process HTTP client bound to the ASGI app) and/or `db` (a
direct session for setup and assertions). Ask for neither and your test needs **no
database** at all.[1]

```python
# tests/conftest.py (trimmed)
@pytest_asyncio.fixture
async def client(_schema):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as http:
        yield http                     # calls the real app, no network/server
```

> **Footnotes**
>
> - **[1]** ***ASGITransport*** runs the FastAPI app **in-process** — real routing, real dependencies, real middleware — but no socket, no running server. Tests are fast and hermetic yet exercise the true request path. `db` is for arranging state ("insert a verified org") and checking results directly.

---

## Unit tests run anywhere — even here

The pure cores (`geo.py`, `lifecycle.py`, `core/pagination.py`, password hashing) need no
database, so their tests run on any machine — including the Windows docs box this
walk-through was written on.[1]

```python
# tests/unit/core/test_pagination.py (trimmed)
@pytest.mark.parametrize(("total","limit","expected"),
    [(0,20,0),(1,20,1),(20,20,1),(21,20,2),(137,20,7),(5,0,0)])
def test_total_pages(total, limit, expected):
    assert total_pages(total, limit) == expected
```

🧠 **Nuance:** this is a payoff of pulling pure logic out of services (Ch 7, 8, 10) — the
trickiest arithmetic and rules are the *easiest* things to test.[2]

> **Footnotes**
>
> - **[1]** ***Parametrize*** runs one test body across many input/output pairs — here every pagination edge case (exact fit, ceiling remainder, empty, zero-limit guard) in one compact, readable test.
> - **[2]** Testability follows design. Because `total_pages`, `can_transition`, and `haversine_km` are pure functions, no fixtures or mocks are needed — just call and assert. Hard-to-test code is usually a design smell pointing at hidden coupling.

---

## API and integration tests, by example

An **API** test drives one endpoint and asserts the contract; an **integration** test
walks a whole flow across modules. Shared `factories.py` builds authenticated users of any
role so tests read clearly:[1]

```python
# tests/api/incidents/test_list_filters.py (trimmed)
cit, _  = await auth_user(client, db, "c@example.com", "citizen")
coord,_ = await auth_user(client, db, "co@example.com", "coordinator")
await _create(client, cit, service_type="medical", priority="critical", description="Severe bleeding")
resp = await client.get("/api/v1/incidents?priority=critical", headers=bearer(coord))
assert resp.status_code == 200 and all(i["priority"] == "critical" for i in resp.json()["data"])
```

Integration tests do the full **created → approved → accepted → … → verified** walk,
proving the lifecycle, notifications, and audit all fire together.[2]

> **Footnotes**
>
> - **[1]** ***Test factories*** hide setup noise (create a user, verify email, log in, return a token) behind one call, so the test body shows only what it's actually testing. Readable tests are maintainable tests.
> - **[2]** For semantic/data-heavy assertions the habit is *robustness*: assert the shape and the invariant ("only critical rows come back", "the audit trail gained an `incident.verify`"), not brittle exact strings or counts that legitimate changes would break.

---

## The quality gate — one command

Before any change is considered done, `make qa` runs the whole machine-checkable bar in
order:[1]

```make
# code/Makefile
qa: ## the pre-PR gate: everything a machine can check, in order
	$(MAKE) format lint typecheck coverage      # black+isort · ruff · mypy · pytest ≥80% coverage
```

⚠️ **Honest scope note:** this walk-through was written on a **Windows, docs-only** box
with **no PostgreSQL/PostGIS/MinIO** — so the DB-backed suite **cannot run here**. The
ceiling here is `ruff` (clean) + `py_compile`; the full green run happens on an Ubuntu
box or in CI (which spins up PostGIS + MinIO service containers).[2]

> **Footnotes**
>
> - **[1]** ***Type checking*** (mypy) catches whole classes of bugs before runtime; ***coverage ≥ 80%*** guards against untested code creeping in. Chaining them in one target means "did I break the bar?" is a single command, locally and in CI.
> - **[2]** This is a governance rule of the project: a conformance row flips to "done" **only after a green test run** on a real database — never on the strength of "it compiles." Code that has never executed is "written," not "verified." The pure unit tests above are the exception that *does* run everywhere.

---

## Recap & what's next

- Tests mirror the code: **unit · api · integration**, one folder per module (**Task N**),
  a proper **pyramid**.
- `conftest.py` sets env **before import**, mints **ephemeral RS256 keys**, and gives each
  test an **isolated schema**; `client` runs the app **in-process**.
- Pure-core unit tests run **anywhere**; the DB-backed suite runs on Ubuntu/CI; `make qa`
  is the one-command gate, and "done" means **green on a real database**.

🛠️ **Try it:** if you have Python, run `pytest tests/unit/core/test_pagination.py` — it
passes with no database, because the code under test is pure.

**Next:** [Chapter 12 — Mastery: End-to-End & Exercises](12-mastery-end-to-end.md), where
we trace one request through every layer and you test yourself.
