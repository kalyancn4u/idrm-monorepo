# Glossary

Plain-language definitions of every term used in the walk-through. Skim it once, then use
it as a lookup. Each entry notes the chapter(s) where the idea is used.

---

### ADR (Architecture Decision Record)
A short document capturing one decision and *why*, so a future reader can revisit it when
circumstances change. IDRM's ADRs live in `docs/mvp/21`. *(Ch 1, 6, 12)*

### Account enumeration
Leaking which emails are registered via different error messages or timings. Login returns
a generic `invalid_credentials` for both "no such user" and "wrong password" to prevent it. *(Ch 6)*

### Append-only
A store that only ever gains rows — never updates or deletes. The audit trail is append-only
and has no write endpoint, so it cannot be rewritten over the API. *(Ch 9)*

### ASGITransport
An httpx transport that runs the FastAPI app **in-process** (real routing/middleware, no
socket), so API tests are fast and hermetic yet exercise the true request path. *(Ch 11)*

### Async I/O
Non-blocking waiting: `await` yields the worker while the database (or network) responds,
so one worker serves many concurrent requests. The `asyncpg` driver enables it for PostgreSQL. *(Ch 5)*

### Asymmetric signing
Signing with a private key that anyone can verify with the matching public key. RS256 tokens
use it, so a verifier needs only the public key — smaller blast radius than a shared secret. *(Ch 6)*

### bcrypt
A deliberately slow, salted password hash. Slowness is a feature — it makes mass guessing
expensive. IDRM uses cost (work factor) 12. *(Ch 6)*

### Ceiling division
Rounding a division up: `(total + limit - 1) // limit`. 21 items at 20/page = 2 pages. Lives
once in `total_pages`. *(Ch 10)*

### Claims
The readable, tamper-evident fields inside a JWT — here `sub` (user id), `role`, and expiry.
The server trusts a valid signature rather than a DB lookup per call. *(Ch 6)*

### Composition over inheritance
Assembling capabilities from small mixins (UUID id, timestamps, soft-delete) rather than a
deep class tree. *(Ch 2)*

### Composition root
The single place (here `main.py`) where the app's pieces are assembled — middleware, error
handlers, routers — and which contains no business logic itself. *(Ch 3)*

### Connection pool
A small set of reused database connections (`pool_size=5`) instead of opening one per query. *(Ch 5)*

### Contextvar
Per-task, async-safe storage (`contextvars.ContextVar`) — the async cousin of thread-local.
The request id and client IP are set in middleware and read anywhere downstream. *(Ch 3, 4)*

### Contract-first
Designing the API as a product with a stability guarantee: additive change is safe, renames
break every client. IDRM corrects docs to match shipped behaviour, not the reverse. *(Ch 1, 10)*

### Correlation id
One identifier (`X-Request-Id`) shared by every log line of a single request, so a whole
request can be replayed by filtering logs. Echoed back in the response header. *(Ch 3, 4)*

### Coupling
How much one part must know about another. IDRM keeps it **low and one-directional** (a
feature depends on audit/notifications, never the reverse). *(Ch 1, 9, 11)*

### Cross-cutting concern
Something many features need (logging, audit, notifications) that isn't the feature itself.
Composed at the router edge to keep services pure. *(Ch 9)*

### Dependency (FastAPI)
A reusable, declarative "give me X" annotation resolved per request — e.g. `get_db`,
`get_current_claims`, `require_role`. Keeps routers thin. *(Ch 3, 6)*

### Dependency inversion
High-level code depends on an abstraction it defines; low-level code conforms. The files
service owns the `ObjectStorage` protocol; `S3Storage` (and a test fake) implement it. *(Ch 9)*

### Design law
A house rule holding across the whole codebase. IDRM has three: PostGIS is the source of
truth; the `/api/v1` contract is frozen; modules compose only at the router edge. *(Ch 1)*

### DPDP (Act 2023)
India's Digital Personal Data Protection Act. Drives choices like redacting PII in logs,
stripping photo GPS, and not shipping coordinates to a third-party geocoder. *(Ch 4, 8, 9)*

### DRY (Don't Repeat Yourself)
Each piece of knowledge lives in one place. The pagination envelope + ceiling division and
the lat/lng conversion are each centralized once. *(Ch 8, 10)*

### DTO (Data Transfer Object)
An API shape (Pydantic schema) kept separate from the database model, so the wire format and
storage format can differ and internal fields never leak. *(Ch 2)*

### Envelope (response envelope)
The consistent JSON shapes: a bare object for one item, `{data, pagination}` for a list,
`{error: {code, message, details}}` for a failure. *(Ch 1, 4, 10)*

### EXIF
Metadata cameras embed in photos (orientation, timestamp, often GPS). The image pipeline
rebuilds from raw pixels to strip all of it — a privacy control. *(Ch 9)*

### Ephemeral (keys)
Generated for one run and thrown away. Tests mint an ephemeral RS256 keypair so auth is
exercised for real without shipping keys. *(Ch 11)*

### FFP (Full-Fledged Product)
The enterprise phase the MVP grows into *without a rewrite*: microservices, an API gateway,
React web + mobile, brokers, Kubernetes — each added on a concrete trigger. *(Ch 1, 12)*

### flush vs commit
`flush` sends pending SQL within the transaction (so ids/constraints apply now); `commit`
makes it permanent and ends the transaction. Repositories flush; `get_db` commits. *(Ch 5)*

### Full-text search
Searching text by tokenized words, not substrings. `q` uses `to_tsvector('english',
description) @@ plainto_tsquery(...)`, backed by a GIN index. *(Ch 5, 10)*

### Geography vs geometry (PostGIS)
`geometry` is fast and planar (units = degrees); `geography` is spherical (units = metres,
accurate globally). Proximity casts to geography so the radius is true metres. *(Ch 8)*

### GeoJSON
The JSON standard for geographic features (points, polygons) that Leaflet consumes directly.
Note `[longitude, latitude]` order. *(Ch 1, 8)*

### GIN index
A PostgreSQL index for "contains" lookups — here over `to_tsvector(description)` for
full-text search, and over array columns. *(Ch 5, 10)*

### GiST index
The PostGIS index type for spatial columns; makes "within radius" / "contains point" fast. *(Ch 1, 8)*

### Guest path
The narrow set of actions an unauthenticated user may take — chiefly raising an emergency
request, which returns a tracking token. `get_optional_claims` powers it. *(Ch 1, 6, 7, 12)*

### Haversine
Great-circle distance between two lat/lng points on a sphere — enough for a one-off
calculation without querying PostGIS. *(Ch 8)*

### Health endpoint
A trivial, dependency-free URL a load balancer or `systemd` pings to ask "are you alive?".
Kept DB-free so it answers even when downstream is degraded. *(Ch 3)*

### IDOR (Insecure Direct Object Reference)
Guessing/altering an id to reach data you shouldn't. Random UUID ids (not sequential ints)
remove that whole class of probing. *(Ch 5)*

### Idempotent
An operation that can be repeated without changing the result beyond the first time. The
seed script is idempotent — `make seed` never duplicates rows. *(Ch 5, 11)*

### Incident
The core record: one help request at a location (service type, priority, status, requester).
Called a "help request" in the UI. *(Ch 1, 7)*

### JWT (JSON Web Token)
A signed, self-describing token whose claims are readable and tamper-evident. IDRM's access
tokens are short-lived RS256 JWTs. *(Ch 6)*

### KISS (Keep It Simple)
Prefer the simplest thing that's correct. Why `sort` is a whitelist not a general engine,
and why the MVP defers Redis/React/Docker. *(Ch 1, 10)*

### Layered architecture
Each layer talks only to its neighbour: router → service → repository → DB, data flowing
back up. No layer skips another. *(Ch 2)*

### Lifecycle / state machine
The fixed set of states a record may be in plus the legal moves between them. IDRM's incident
lifecycle has eight states, modeled as pure data. *(Ch 1, 7)*

### lru_cache
Memoizes a function's result. `get_settings()` uses it to read the environment once and reuse
one `Settings` instance (a lightweight singleton). *(Ch 3)*

### Migration
A versioned, replayable schema change (Alembic). Ordered files build/evolve the schema so
every environment reaches the same shape. `make migrate` = `alembic upgrade head`. *(Ch 5)*

### Mixin
A small class you inherit *alongside* your base to add a bundle of behaviour (id, timestamps,
soft-delete). *(Ch 2)*

### MinIO
An S3-compatible object store for uploaded files. IDRM stores the **bytes** here and only the
object **key/URL** in the database — never the blob. *(Ch 1, 9)*

### Modular monolith
One deployable application divided into clean modules with enforced seams — simple to deploy,
splittable later into microservices. *(Ch 1, 2)*

### MVP (Minimum Viable Product)
The deliberately simple first phase: a FastAPI modular monolith, server-rendered UI,
PostgreSQL + PostGIS + MinIO, native `systemd`. *(Ch 1)*

### One-directional coupling
Dependencies point one way only (feature → audit/notifications). The acyclic shape is what
lets a module become its own service later. *(Ch 9)*

### OpenAPI
A standard schema describing a REST API. FastAPI serves a live `/docs`; the committed
`40-api-openapi.yaml` is the authoritative, reviewable contract. *(Ch 10)*

### ORM (Object-Relational Mapper)
A library (SQLAlchemy) mapping Python objects to database rows, so you write `incident.status`
instead of raw SQL. *(Ch 2)*

### Parametrize (pytest)
Running one test body across many input/output pairs — used to cover pagination edge cases
compactly. *(Ch 11)*

### PII (Personally Identifiable Information)
Data identifying a person. Masked in logs and handled carefully under DPDP. *(Ch 4)*

### Principle of least astonishment
Design so behaviour matches expectations. Uniform API conventions mean knowing one resource
lets you guess the next. *(Ch 10)*

### Protocol (structural typing)
A Python interface defined by shape ("has `bucket` and `put(...)`") without inheritance. Lets
tests swap a fake storage for the real one. *(Ch 9)*

### Pull-model (notifications)
The client fetches unread notifications; there is no server push. Real-time push is FFP. *(Ch 9)*

### Pydantic
A library that validates and coerces data against typed models. Rejects bad input before your
code runs; invalid input becomes a `422`. *(Ch 2, 4)*

### RBAC (Role-Based Access Control)
Granting permissions by role — citizen, provider, coordinator, admin — plus a guest path.
Enforced by `require_role`. *(Ch 1, 6)*

### Redaction
Masking secret/PII keys before a log line is emitted — defense-in-depth, not a licence to log
sensitive data. *(Ch 4)*

### Repository pattern
Putting all of a module's database access behind a narrow class, so services depend on a small
data API rather than SQL. *(Ch 1, 2, 5)*

### RS256
RSA signing with SHA-256 — the asymmetric algorithm for IDRM's JWTs (sign with private, verify
with public). *(Ch 6)*

### run_in_threadpool
Offloads blocking (synchronous) work — Pillow image processing, boto3 uploads — to a thread so
the async event loop isn't frozen. *(Ch 9)*

### Salt
Random data mixed into a password before hashing so identical passwords hash differently,
defeating rainbow tables. bcrypt salts automatically. *(Ch 6)*

### Seam
A clean interface a simple thing hides behind, so a more powerful thing can replace it later
(rate limit → APISIX, geocode stub → real geocoder). *(Ch 12)*

### Separation of concerns
Each file/layer has exactly one reason to change: URL → router, rule → service, column →
model + migration. *(Ch 2)*

### Service layer
The layer holding business rules (validation, transitions, authorization), between router
(HTTP) and repository (data). Kept pure of I/O side effects. *(Ch 1, 2, 7)*

### Single-claim
The first provider to accept an incident wins; a second gets `409 already_accepted`. Stops two
responders both "owning" one emergency. *(Ch 7)*

### Soft delete
Setting `deleted_at` instead of erasing a row; reads filter `deleted_at IS NULL`. Preserves
history for audit and recovery. *(Ch 5)*

### Source of truth
The one authoritative store that wins if any two disagree — here PostgreSQL + PostGIS. *(Ch 1, 5)*

### SQL injection
Smuggling malicious SQL through unsanitized input (including a column name). Avoided by
parameterized queries and a `sort` allow-list. *(Ch 10)*

### SRID 4326
The WGS-84 coordinate system (GPS latitude/longitude in degrees) used for all IDRM geometry. *(Ch 8)*

### Strangler Fig
An evolution strategy: grow the new system around the old, one piece at a time, until the old
can be retired — never a big-bang rewrite. *(Ch 1, 12)*

### Structured logging
Logging as key/value data (JSON) rather than prose, so logs are queryable and aggregatable. *(Ch 4)*

### Test isolation
Each test gets a fresh schema (create-then-drop) so tests can't see each other's rows —
removing order-dependent flakiness. *(Ch 11)*

### Test pyramid
Many fast unit tests, fewer API tests, a thin layer of broad integration tests. Fast feedback
plus confidence the pieces connect. *(Ch 11)*

### Tracking token
A random, unguessable string standing in for an account, letting a guest follow their request
without signing up. *(Ch 7, 12)*

### tsvector / tsquery
PostgreSQL full-text types: `to_tsvector` turns text into searchable tokens; `plainto_tsquery`
turns a query into a matchable form; `@@` tests a match. *(Ch 10)*

### Unit of Work
Grouping all of one operation's changes into a single transaction that commits together or not
at all. `get_db` implements it per request. *(Ch 5, 6)*

### UUID
A random, non-guessable identifier used as every table's primary key — no enumerable ids. *(Ch 5)*

### WAF (Web Application Firewall)
A filter that blocks malicious HTTP traffic. Deferred to the FFP (with the APISIX gateway);
the MVP's rate limiter is the in-process abuse guard. *(Ch 6)*

### WKT (Well-Known Text)
PostGIS's text form for geometry, e.g. `POINT(78.47 17.39)` — note `longitude latitude` order. *(Ch 8)*

### Work factor
The tunable cost of a slow hash (bcrypt rounds = 12), raised over time as hardware speeds up. *(Ch 6)*

### 12-factor
A set of app-building principles IDRM follows: config in the environment, logs as an event
stream to stdout, one build across all environments. *(Ch 3, 4)*
