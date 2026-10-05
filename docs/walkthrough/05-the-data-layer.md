# Chapter 5 — The Data Layer

*The async engine, the session lifecycle, and how the schema is built and evolved.*

**By the end of this chapter you will be able to:** explain why database access is async,
describe the session-per-request pattern, read a repository, understand soft-delete, and
say how the schema is created and changed safely with migrations.

Files: [`infrastructure/database/engine.py`](../../services/monolith/app/infrastructure/database/engine.py),
[`base.py`](../../services/monolith/app/infrastructure/database/base.py),
[`core/dependencies.py`](../../services/monolith/app/core/dependencies.py),
[`alembic/versions/`](../../services/monolith/alembic/versions/).

---

## An async engine, so one worker serves many requests

The database is reached through an **async** SQLAlchemy engine and session factory:

```python
# app/infrastructure/database/engine.py
engine = create_async_engine(_settings.database_url, pool_size=5, max_overflow=0, future=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
```

🧠 **Nuance:** an API spends most of its time *waiting* on the database. **Async** lets
one worker start another request while the first waits — high concurrency without a thread
per request.[1]

> **Footnotes**
>
> - **[1]** ***Async I/O*** = non-blocking waiting. `await session.execute(...)` yields the worker while the DB thinks, so other requests progress. The `asyncpg` driver (in the URL, `postgresql+asyncpg://`) speaks PostgreSQL's protocol without blocking. A ***connection pool*** (`pool_size=5`) reuses a small set of connections instead of opening one per query.

---

## A session per request, committed or rolled back — automatically

`get_db` is the dependency every router uses. It yields one session for the request and
guarantees the right ending: **commit on success, roll back on any error**.

```python
# app/core/dependencies.py
async def get_db() -> AsyncIterator[AsyncSession]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()          # success → persist
        except Exception:
            await session.rollback()        # any error → undo
            raise
```

This is the **Unit of Work**[1]: everything a request does is one atomic transaction. A
service can raise `AppError` mid-way and be sure nothing half-written is committed.

> **Footnotes**
>
> - **[1]** ***Unit of Work*** = group all changes of one operation into a single transaction that commits together or not at all. Because the endpoint's whole body runs inside this `try`, a `404`/`403`/`409` raised anywhere leaves the database untouched. (One deliberate exception: the login path commits a failed-attempt counter explicitly, so a `401` can't erase the lockout count — Ch 6.)

---

## Every table, the same spine

Recall the mixins from Chapter 2: each model composes a UUID id, UTC timestamps, and
(usually) soft-delete.

```python
# a model, conceptually
class Incident(Base, UUIDPrimaryKey, Timestamps, SoftDelete): ...
```

- **UUID ids** are random and non-guessable — you can't enumerate `/incidents/1,2,3`.[1]
- **Soft-delete** sets `deleted_at` instead of erasing the row; every read filters
  `deleted_at IS NULL`.[2]

> **Footnotes**
>
> - **[1]** Sequential integer ids leak information (how many exist, order of creation) and invite ***IDOR*** (Insecure Direct Object Reference) probing. Random UUIDs remove that whole class of guessing.
> - **[2]** ***Soft delete*** keeps history for audit and recovery — critical in a disaster-response system where "who cancelled this and when" matters. The trade-off is that *every* query must exclude deleted rows; the repository does this consistently (`.where(Model.deleted_at.is_(None))`).

---

## The repository, concretely

A repository method reads/writes through the session and returns ORM objects — no policy,
just data. Note `flush` (not `commit`): it sends the INSERT so the generated id is
available, while the *request-level* `get_db` still owns the final commit.[1]

```python
# app/modules/incidents/repository.py (trimmed)
async def add(self, incident: Incident) -> Incident:
    self.session.add(incident)
    await self.session.flush()      # emit INSERT now (id becomes available)…
    return incident                 # …but commit happens in get_db at request end
```

⚠️ **Pitfall:** a repository must not `commit` — that would end the request's single
transaction early and break the all-or-nothing guarantee.[2]

> **Footnotes**
>
> - **[1]** ***flush vs commit***: `flush` pushes pending SQL to the DB *within* the transaction (so ids and constraints apply now); `commit` makes it permanent and ends the transaction. Keeping `commit` at the request edge is what makes the Unit of Work work.
> - **[2]** There is exactly one intentional `commit()` inside a repository — recording a failed login — and Chapter 6 explains precisely why that single exception is safe and necessary.

---

## The schema is built ONLY by migrations

Tables are **never** created ad-hoc. **Alembic** migrations are the one source of schema
truth: six ordered files (`0001…0006`) that build and evolve it. The very first enables
PostGIS and creates the spatial indexes.[1]

```python
# alembic/versions/0002_incidents.py (representative, trimmed)
op.create_index("ix_incidents_location", "incidents", ["location"], postgresql_using="gist")
op.create_index("ix_incidents_priority", "incidents", ["priority"])
op.execute("CREATE INDEX ix_incidents_desc_fts ON incidents USING gin (to_tsvector('english', description))")
```

`make migrate` runs `alembic upgrade head` to bring any database to the latest schema.[2]

> **Footnotes**
>
> - **[1]** A ***migration*** is a versioned, replayable schema change. Because they're ordered and idempotent-to-apply, any environment (a teammate's laptop, CI, prod) reaches the *same* schema by running them in order — no "works on my machine" drift. `CREATE EXTENSION postgis` lives in `0001` so spatial types exist before any table uses them.
> - **[2]** Those indexes aren't decoration: `gist` powers spatial "within radius" (Ch 8), the `priority` b-tree powers the filter (Ch 10), and the `gin(to_tsvector(...))` powers full-text search `q` (Ch 10). An index the code never queries is pure cost — so the code and schema are kept in lock-step.

---

## Reading a page of rows

List endpoints share a shape: filter, count the total, then fetch one page. The repository
returns `(rows, total)`; the router wraps it in the standard envelope (Ch 10).

```python
# app/modules/incidents/repository.py (trimmed)
total = len((await self.session.execute(stmt)).scalars().all())
paged = stmt.order_by(resolve_order(sort)).limit(limit).offset(offset)
rows  = (await self.session.execute(paged)).scalars().all()
return list(rows), total
```

🧠 **Nuance:** role scoping is applied *here* by passing (or not passing) a
`requester_id` — a citizen's list is silently narrowed to their own rows, decided by the
service (Ch 2, Ch 6).[1]

> **Footnotes**
>
> - **[1]** Counting then paging is the simplest correct pagination. At MVP scale it's fine; at FFP scale you'd switch heavy counts to estimates or keyset pagination — a change isolated entirely to this one repository method, which is the whole point of the layer.

---

## Recap & what's next

- Data access is **async** (high concurrency) via a pooled engine and a **session per
  request** with automatic commit/rollback (**Unit of Work**).
- Every table shares **UUID id + timestamps + soft-delete**; repositories return ORM
  objects and `flush` but don't `commit`.
- The schema is built and evolved **only by Alembic migrations**, including the PostGIS
  extension and the indexes the code relies on.

🛠️ **Try it:** open [`alembic/versions/0001_users_baseline.py`](../../services/monolith/alembic/versions/0001_users_baseline.py)
and find `CREATE EXTENSION`. That one line is why every later spatial column just works.

**Next:** [Chapter 6 — Security, Auth & RBAC](06-security-auth-and-rbac.md), where we learn
who the caller is and what they're allowed to do.
