# Chapter 1 — The Big Picture

*How the whole system fits together, and the ideas everything else depends on.*

**By the end of this chapter you will be able to:** explain what IDRM does, name the
four ideas the codebase is built on, read the architecture diagram, and state the
three "design laws" that keep the system correct.

Files: the whole app under [`services/monolith/app/`](../../services/monolith/app/); the entry point is
[`app/main.py`](../../services/monolith/app/main.py). No need to open them yet — this chapter is the map.

---

## What are we building?

**IDRM — Integrated Disaster Response Management** — an India-focused, **map-driven**
web platform that connects disaster-affected people with the organizations and
responders who can help them.[1] The shorthand is *"Uber for disaster relief."*

Someone in trouble raises a **help request** at a location; nearby verified providers
see it, claim it, and work it to completion; coordinators oversee; everyone is kept
informed. The whole product is organized around that one record and its journey.[2]

> **Footnotes**
>
> - **[1]** "Web platform" is precise: the MVP is server-rendered **HTML + Tailwind CSS + a little JavaScript + Leaflet** (the map library) — **no React, no mobile app** yet. Those belong to the later *FFP* (Full-Fledged Product) phase, introduced at the end of this chapter.
> - **[2]** In the UI we say ***help request***; in the API and database the same thing is the resource ***incident***. One concept, two names — you will see both. Chapter 7 is entirely about its lifecycle.

---

## The four ideas (the whole app in four phrases)

1. ***Modular monolith*** — **one** deployable application, internally split into **ten
   clean modules**.[1]
2. ***Incident lifecycle*** — the help request moves through a small, strict set of
   states (created → … → verified); the rules of that journey *are* the domain.[2]
3. ***Spatial source of truth*** — **PostgreSQL 16 + PostGIS 3.4** stores everything,
   including geography, so "what's near me?" is a first-class question.[3]
4. ***Contract-first + roles*** — a **frozen `/api/v1` contract** and four roles
   (citizen · provider · coordinator · admin) **+ a guest path** decide who can do what.

Almost every file you will read is an implementation detail of one of these four ideas.

> **Footnotes**
>
> - **[1]** The ten modules: **users, incidents, resources (organizations), locations, alerts, notifications, reports, files, audit, administration**. A ***modular monolith*** keeps the simplicity of one app to deploy while enforcing clean internal seams — so it can later split into microservices *without a rewrite* (the ***Strangler Fig*** path, defined in the Glossary).
> - **[2]** A ***lifecycle*** is the set of allowed states a record can be in, plus the legal moves between them — a *state machine*. Modeling it explicitly (Chapter 7) is what stops illegal jumps like "complete before accept."
> - **[3]** ***PostGIS*** is the spatial extension for PostgreSQL: it adds geographic types and functions (distance, "within radius", "point-in-polygon") so the *database* answers location questions, instead of pulling every row into Python. Chapter 8.

---

## The architecture, as a request flows

![Architecture of the IDRM MVP modular monolith: an HTTP request from the web client flows through the FastAPI app (request-id and JSON logging middleware), into a module router, through the shared guards (JWT auth, RBAC, rate limit, DB session), into a service that enforces business rules such as the incident lifecycle, then a repository, then PostgreSQL with PostGIS as the single source of truth; the response is one data-and-pagination or error envelope. MinIO stores file objects; audit and notifications are composed at the router edge. Three design laws: PostGIS is the source of truth, the api/v1 contract is frozen, modules compose only at the router edge.](assets/architecture.svg)

Read it top to bottom: that arrow is *exactly* the journey each chapter zooms into.[1]
A plain-text version is on the next slide (screen-reader and terminal friendly).[2]

> **Footnotes**
>
> - **[1]** Notice the **layering**: the *router* handles HTTP, the *guards* handle who-are-you/may-you, the *service* holds business rules, the *repository* handles data access, and only PostgreSQL touches disk. Each layer has one job — that is what makes each one testable and replaceable (Chapters 2 and 11).
> - **[2]** Same information, two forms — the diagram for a quick visual grasp, the text for accessibility and copy-paste. Keeping them on separate slides keeps each legible.

---

## The architecture — text version

<!-- _class: diagram-text -->

*The same flow as the diagram, in plain text:*

```text
   Web client  (HTML + Tailwind + JS + Leaflet)
            │  HTTP request  (Authorization: Bearer <jwt>)
            ▼
  ┌────────────────────────┐
  │ FastAPI app  main.py   │  X-Request-Id + JSON logging      Ch 3–4
  └────────────────────────┘
            │
            ▼
  ┌────────────────────────┐
  │ Module router  /api/v1  │  one of 10 modules               Ch 2
  └────────────────────────┘
            │
            ▼
  ┌────────────────────────┐
  │ Shared guards          │  Bearer→claims (RS256) · RBAC
  │ core/dependencies      │  · rate_limit · get_db            Ch 6
  └────────────────────────┘
            │                         ┌───────────────────────┐
            ▼                 (edge)  │ Audit + Notifications  │  Ch 9
  ┌────────────────────────┐ ───────▶│ composed at the router │
  │ Service — business rules│         └───────────────────────┘
  │ e.g. incident lifecycle │                                   Ch 7
  └────────────────────────┘
            │                         ┌───────────────────────┐
            ▼                 (files) │ MinIO (S3) object store│  Ch 9
  ┌────────────────────────┐ ───────▶│ bytes; DB stores keys  │
  │ Repository (async)     │         └───────────────────────┘
  └────────────────────────┘                                   Ch 5
            │
            ▼
  ┌────────────────────────┐
  │ PostgreSQL 16 + PostGIS │  single source of truth          Ch 5, 8
  └────────────────────────┘
            │  rows → Pydantic → JSON
            ▼
   Response: one {data, pagination} | item | error{code}       Ch 10
```

> **Footnotes**
>
> - **[1]** Each box names the responsible layer and its chapter, so you can trace the flow straight into the code: `main.py` (Ch 3) → a module's `router.py` (Ch 2) → `core/dependencies.py` (Ch 6) → `service.py` (Ch 7) → `repository.py` (Ch 5) → PostgreSQL/PostGIS (Ch 8).

---

## Design Law #1 — PostGIS is the source of truth

The relational + spatial database is **the** authoritative store.[1] One consequence
shapes the whole file layer: uploaded photos and documents live in **MinIO** (an
object store), but the database records **only the object's key/URL — never the bytes**.

- Lose the app server? Redeploy; the data is safe in PostgreSQL.
- Every "where is X?" question is answered *in the database* with PostGIS, not by
  scanning rows in Python.[2]

🧠 **Nuance:** this is why there is no `blob` column anywhere. The database is the
system of record for *facts*; MinIO is a content-addressed *bucket of files* the facts
point at.

> **Footnotes**
>
> - **[1]** A ***source of truth*** is the one store that wins if any two ever disagree. Keeping it single is what makes the system easy to reason about and back up. See [`docs/mvp/50-data-model.md`](../mvp/50-data-model.md).
> - **[2]** Doing distance/containment math in the database uses **spatial indexes** (GiST) and returns only the rows you need. Pulling everything into Python to filter would be slower and would not scale. Chapter 8 shows the exact `ST_DWithin` query.

---

## Design Law #2 — the `/api/v1` contract is frozen

Every endpoint lives under **`/api/v1`**, and those paths are a **stable promise**.[1]
The rules (Chapter 10): plural resource URLs, `snake_case` fields, UUID ids, ISO-8601
UTC timestamps, lowercase enum values, and one response shape — a bare object for a
single item, `{data, pagination}` for a list, and one error envelope for every failure.

⚠️ **Pitfall:** "frozen" does **not** mean "finished." The future FFP phase may **add**
endpoints at the same paths — it must never **rename** or repurpose an existing one.[2]

> **Footnotes**
>
> - **[1]** The machine-readable contract is [`docs/mvp/40-api-openapi.yaml`](../mvp/40-api-openapi.yaml); the prose is [`40-api-specification.md`](../mvp/40-api-specification.md). A frozen contract lets the current HTML/JS UI **and** future React/mobile clients share one backend unchanged.
> - **[2]** ***Contract-first*** design treats the API as a product with a compatibility guarantee. Additive change is safe; renames break every client at once. This is why, in Chapter 10, the *docs* were corrected to match the *code* rather than the other way around.

---

## Design Law #3 — modules compose only at the router edge

Modules must not reach into each other's internals. When a feature needs a cross-cutting
effect — writing an **audit** entry, sending a **notification** — that wiring happens in
the **router**, *after* the service returns, not inside the service.[1]

The payoff: services stay **pure and independently testable**, and coupling is
**one-directional** (a feature depends on audit/notifications, never the reverse).[2]

```python
# services/monolith/app/modules/incidents/router.py — composition at the edge (trimmed)
updated = await svc.perform_transition(incident, action, actor_id, role, **kwargs)
await _notify_requester(db, updated, actor_id)          # notifications
await AuditService(AuditRepository(db)).record(...)     # audit
```

> **Footnotes**
>
> - **[1]** The incident *service* only knows how to move an incident through its lifecycle. It does **not** know notifications exist. The *router* orchestrates the extra effects. This keeps the hard-to-test bits (I/O, side effects) at the thin outer layer.
> - **[2]** ***Coupling*** is how much one part must know about another. Low, one-directional coupling is what lets a module later become its own microservice with minimal surgery (the Strangler Fig plan). Chapter 9 shows all three cross-cutting seams.

---

## The two phases — what is deliberately *not* here (and why)

The MVP stays small on purpose. It does **not** use:[1]

- React or a mobile app (server-rendered HTML + Leaflet instead),
- Redis, message brokers, or background workers (sessions live in PostgreSQL),
- Docker/Kubernetes (native `systemd` on Ubuntu),
- microservices or an API gateway (one modular monolith).

All of these are **planned for the FFP** (Full-Fledged Product) and the architecture is
*designed* so they can be added on a concrete trigger — one module at a time — **without
a rewrite**.[2]

🧠 **Nuance:** every "no" above is an application of the priority order
**Simple → Correct → Tested → Maintainable → Extensible.** The MVP earns the right to
grow by being correct first.

> **Footnotes**
>
> - **[1]** The full rationale for each deferral is recorded as ***ADRs*** (Architecture Decision Records) in [`docs/mvp/21-architecture-decisions.md`](../mvp/21-architecture-decisions.md). An ADR captures *why* a choice was made, so a future reader can revisit it when the trigger arrives.
> - **[2]** The evolution plan — which module extracts first, on what trigger — is the ***Strangler Fig*** pattern: grow the new system around the old until the old can be retired, never a big-bang rewrite. See [`docs/ffp/`](../ffp/).

---

## Recap & what's next

- IDRM connects people in a disaster with responders, organized around the **incident**
  (help request) and its lifecycle.
- **Four ideas:** modular monolith · incident lifecycle · spatial source of truth ·
  contract-first + roles.
- **Three laws:** PostGIS is truth · the `/api/v1` contract is frozen · modules compose
  only at the router edge.
- The MVP is deliberately minimal; the FFP grows it without a rewrite.

🛠️ **Try it:** open [`services/monolith/app/main.py`](../../services/monolith/app/main.py) and find the ten
`app.include_router(...)` lines near the bottom. That list *is* the ten modules — you
now know what each one is for.

**Next:** [Chapter 2 — Anatomy of a Module](02-anatomy-of-a-module.md), where we open one
module and meet the five files every module is made of.
