# Chapter 2 — Anatomy of a Module

*Open one module and meet the five files every module is made of.*

**By the end of this chapter you will be able to:** name the five layers of a module,
say what each one is responsible for (and what it must *not* do), and read a request as
it falls through them.

Files: a representative module — [`app/modules/incidents/`](../../services/monolith/app/modules/incidents/)
(`models · schemas · repository · service · router`).

---

## Why "modules", and why five files?

The app is **one deployable process**, but inside it is divided into ten **modules** —
users, incidents, resources, locations, alerts, notifications, reports, files, audit,
administration.[1] Each module owns one slice of the domain and (almost) always has the
**same five files**, in the same roles:

```text
app/modules/incidents/
├── models.py       # the database tables (ORM)          — "what is stored"
├── schemas.py      # the request/response shapes (API)  — "what crosses the wire"
├── repository.py   # data access (SQL)                  — "how we read/write it"
├── service.py      # business rules                     — "what is allowed"
└── router.py       # HTTP endpoints                     — "how it is called"
```

Learn these five once and you can read *any* module.[2]

> **Footnotes**
>
> - **[1]** Same idea as folders in a well-kept house: each room has a purpose. The seams are enforced by imports — a module reaches another module's *service* at the router edge, never its private internals (Design Law #3, Ch 1).
> - **[2]** This uniformity is a feature: a new contributor learns the shape once and is immediately productive in every module. It also makes each module a clean candidate for later extraction into its own service (the Strangler Fig plan).

---

## The five layers at a glance

Each layer depends only on the one below it — a classic **layered architecture**.[1]

| Layer | File | Job | Must NOT |
|---|---|---|---|
| API shapes | `schemas.py` | validate input, shape output (Pydantic) | contain business rules |
| HTTP | `router.py` | map URLs → calls; apply guards | contain business rules or SQL |
| Rules | `service.py` | enforce what's allowed; orchestrate | know about HTTP or raw SQL |
| Data | `repository.py` | read/write the database | make policy decisions |
| Storage | `models.py` | define tables/columns | know about HTTP |

🧠 **Nuance:** the **service** is the heart — it is where the domain rules live, and it
is deliberately kept free of HTTP and I/O so it is the easiest thing to unit-test.[2]

> **Footnotes**
>
> - **[1]** ***Layered architecture*** means each layer talks only to its neighbour. A request flows *down* (router → service → repository → DB); data flows *up*. No layer skips another — the router never runs SQL; the service never touches `Request`.
> - **[2]** ***Separation of concerns*** — each file has exactly one reason to change. Change the URL? Only `router.py`. Change a rule? Only `service.py`. Change a column? `models.py` + a migration. This is what "maintainable" means in practice.

---

## `models.py` — what is stored

Models are **ORM**[1] classes: one Python class per table. They inherit shared column
**mixins** so every table gets a UUID id, UTC timestamps, and (usually) soft-delete —
without repeating the boilerplate.

```python
# app/infrastructure/database/base.py — shared mixins (trimmed)
class UUIDPrimaryKey:
    id: Mapped[uuid.UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

class Timestamps:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), ...)
    updated_at: Mapped[datetime] = mapped_column(..., onupdate=func.now(), ...)

class SoftDelete:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

An `Incident(Base, UUIDPrimaryKey, Timestamps, SoftDelete)` therefore *has* all of these
for free. Chapter 5 covers the data layer in full.[2]

> **Footnotes**
>
> - **[1]** ***ORM*** (Object-Relational Mapper) = a library (here SQLAlchemy) that maps Python objects to database rows, so you write `incident.status` instead of hand-writing SQL for every read/write.
> - **[2]** ***Mixin*** = a small class you inherit *alongside* your main base to add a bundle of behaviour. Combining mixins is ***composition over inheritance*** — you assemble capabilities rather than build a deep class tree.

---

## `schemas.py` — what crosses the wire

Schemas are **Pydantic**[1] models: the *validated* shapes of request bodies and
responses. They are **not** the database models — they are the public API contract,
deliberately separate so the wire format can differ from the storage format.

```python
# app/modules/incidents/schemas.py (trimmed)
class IncidentCreate(BaseModel):
    service_type: ServiceType
    priority: Priority
    description: str = Field(min_length=1)
    location: Location            # {latitude, longitude}, each range-checked
```

⚠️ **Pitfall:** never accept or return a raw ORM model at the HTTP boundary. Going
through a schema is what validates untrusted input and stops internal fields leaking
out.[2]

> **Footnotes**
>
> - **[1]** ***Pydantic*** validates and coerces data against typed models. If `latitude` is out of range or `description` is empty, Pydantic rejects it *before* your code runs — and the error becomes a `422` (Ch 4).
> - **[2]** Keeping API schemas separate from DB models is the ***DTO*** (Data Transfer Object) pattern. It means a column rename doesn't silently change your API, and a sensitive column (say `password_hash`) can never be serialised to a client by accident.

---

## `repository.py` and `service.py` — how, and what's allowed

The **repository** is the *only* place that touches the database; the **service** holds
the rules and calls the repository. Notice the service raises a domain error, never an
HTTP one directly:

```python
# app/modules/incidents/service.py (trimmed)
async def get(self, incident_id: uuid.UUID) -> Incident:
    incident = await self.repo.get(incident_id)     # repository = data access
    if incident is None:
        raise AppError(404, "not_found", "Incident not found.")   # rule → typed error
    return incident
```

🧠 **Nuance:** the service depends on the repository's small method set (`get`, `list`,
`add`…), not on SQL. Swap the storage later and the rules don't change — that's the
point of the seam.[1]

> **Footnotes**
>
> - **[1]** ***Repository pattern*** = hide data access behind a narrow interface. It makes services readable ("get the incident") and testable (a fake repo in a unit test), and it concentrates all query tuning in one file. The `AppError` it raises is turned into a JSON response by one handler (Ch 4).

---

## `router.py` — how it is called

The router maps a URL to a service call, applies the **guards** (auth, RBAC, rate-limit,
DB session) as dependencies, and returns a **schema**. It also performs the cross-cutting
composition at the edge (Ch 9).

```python
# app/modules/incidents/router.py (trimmed)
@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(incident_id: uuid.UUID, db: DbSession, claims: Claims) -> IncidentResponse:
    incident = await _service(db).get(incident_id)
    if claims["role"] == "citizen" and incident.requester_id != uuid.UUID(claims["sub"]):
        raise AppError(403, "forbidden", "You can only view your own request.")
    return to_response(incident)
```

That is the whole vertical slice: **router → service → repository → DB**, with schemas at
the edge.[1]

> **Footnotes**
>
> - **[1]** `DbSession` and `Claims` are FastAPI ***dependencies*** — reusable, declarative "give me X" annotations resolved per request (Ch 3 & 6). The router stays thin: parse, guard, call, shape. Everything hard is one layer down.

---

## Not every module is identical (and that's fine)

The five-file shape is the *default*, not a straitjacket. Some modules legitimately
differ:[1]

- **No table of their own:** `locations`, `reports`, `administration` read data other
  modules own, so they have **no `models.py`** (and reports/administration need no
  `schemas.py` either).
- **Extra files where the domain warrants it:** `incidents/lifecycle.py` (the state
  machine, Ch 7), `locations/geo.py` (pure maths, Ch 8), `files/imaging.py` +
  `storage.py` (Ch 9), `resources/org_router.py` (a second router), `users/deps.py`.

The rule is **cohesion, not uniformity**: put code where it belongs.[2]

> **Footnotes**
>
> - **[1]** A module having no table is a sign the design is honest: `reports` *aggregates* incidents/orgs/audit — inventing a `reports` table would duplicate data and invite drift. It computes from the source of truth instead.
> - **[2]** ***High cohesion*** = things that change together live together. The `lifecycle` rules are pulled into their own file precisely because they are a self-contained, heavily-tested concept — not scattered through the service.

---

## Recap & what's next

- Every module is (mostly) five files: **models · schemas · repository · service ·
  router**, in a strict **layered** order.
- The **service** holds the rules and stays pure; the **repository** is the only code
  that touches the DB; **schemas** guard the wire.
- Deviations (no table; extra files) follow **cohesion**, not uniformity.

🛠️ **Try it:** open [`app/modules/audit/`](../../services/monolith/app/modules/audit/) — a small
module — and match each file to its row in the table above. Notice it has a `service`
and `repository` but its router only *reads* (Ch 9 explains why).

**Next:** [Chapter 3 — Configuration & App Assembly](03-configuration-and-app-assembly.md),
where we start the app up and watch a request enter it.
