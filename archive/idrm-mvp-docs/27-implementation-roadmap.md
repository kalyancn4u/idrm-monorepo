# IDRM MVP — Complete Implementation Roadmap (Concept → Working Code, for a complete novice)

> *Type: Document (roadmap / build guide — the HUB) · Audience: complete novices → engineers reaching mastery · Status: MVP — current (in progress, written section-by-section)*
> *This is the **single "start here" guide** for building the IDRM MVP. It walks the entire journey — from the
> data foundation, through the API, code structure, concurrency, logging, security, the web design system,
> testing, automation and CI, to the module-by-module build plan — and **links out** to the deep specs rather
> than repeating them. Where a term is unavoidable, it is defined on first use and, for the basics, you are
> pointed to the matching **101 guide**. Its normative twin (the "is it done, and to what standard?" checklist)
> is the signed-off [`26-conformance-pics.md`](26-conformance-pics.md).*

---

## Contents

**Front matter (this installment)**
- [0. How to read this roadmap](#0-how-to-read-this-roadmap)
- [1. The big picture — Concept → MVP → FFP](#1-the-big-picture--concept--mvp--ffp)
- [2. The build philosophy (the five habits)](#2-the-build-philosophy-the-five-habits)

**The data foundation** *(must be finalized before any code — see §2)*
- 3. Data foundation — modeling · schema · indexes & views · **rich seed data** · **user workflows & journeys**

**The technical build**
- 4. API layer — URIs, JSON shapes, HTTP methods, error envelope, fallback behaviour
- 5. Code structure — the FFP-extensible folder scaffold
- 6. Concurrency & thread LLD — the *formula*, ≤ 70 % CPU, worked example (→ sub-doc)
- 7. Logging & diagnostics (MVP) — structured JSON, where/how/what (→ sub-doc)
- 8. Security in practice — sessions, cookies, rate-limiting, allow/deny lists, RBAC
- 9. Web layer & design system — Tailwind tokens, visual hierarchy, components, page map (→ sub-doc)
- 10. Quality & test automation — UT/IT/API/system, coverage, fixtures, the pytest harness
- 11. Build & run automation — Ubuntu recap + the Makefile menu
- 12. CI pipeline — minimal GitHub Actions (lint + tests + coverage)

**The build & the finish line**
- 13. Module-by-module build plan — the ten modules, in dependency order
- 14. Definition of Done + conformance (links the signed-off PICS)
- 15. What's deferred to FFP (and *why*)

> *All sections (§0–§15) are drafted. Deep-dive **sub-docs** — concurrency/thread LLD
> [`31`](31-concurrency-and-thread-model.md), logging [`32`](32-logging-and-diagnostics.md), design system
> [`33`](33-design-system.md) — are separate files this hub links into, so each stays focused. (A full row-by-row
> seed-data spec `34` may follow when the seed script is built.) **Next real-world step: sign off the data
> foundation (§3.6), then coding begins.***

---

## 0. How to read this roadmap

**If you have never built software before, start here.** This section teaches you how to *use* the guide; it
assumes nothing.

### 0.1 The one metaphor: building a house

We will return to this picture again and again, because it makes every technical choice intuitive:

| In a house… | …in IDRM (this roadmap) |
|---|---|
| The **foundation and plumbing** | The **data model** — the tables and the pipes between them (§3). Everything rests on it. |
| The **rooms** | The **modules** — users, incidents, resources… ten self-contained rooms in one house (§13). |
| The **taps and switches** | The **API** — the controls other things use to make the house *do* something (§4). |
| The **interior design** | The **web pages & design system** — how it looks and feels to live in (§9). |
| The **wiring diagram** | The **code structure** — where every wire runs, drawn so an electrician (future engineer) is never surprised (§5). |
| The **fuse box rating** | The **concurrency model** — how much load the wiring safely carries before it trips (§6, kept ≤ 70 %). |
| The **safety inspection** | **Testing & QA** — proof each room is safe before anyone moves in (§10). |
| The **security system** | **Auth, rate-limits, allow/deny lists** — who may enter and do what (§8). |

The golden rule of the whole roadmap follows from the picture: **you pour the foundation before you hang the
pictures.** That is why the *data foundation* (§3) is finalized *before* any code is written (§2).

### 0.2 Two phases you'll see everywhere: **MVP** and **FFP**

- **MVP** = *Minimum Viable Product* — the simplest version that genuinely works and is worth using. **This is
  what we build now.** It is deliberately modest: one FastAPI application (a "modular monolith"), a PostgreSQL
  database, plain HTML/CSS/JavaScript pages, and MinIO for file uploads.
- **FFP** = *Full-Fledged Product* — the enterprise version the MVP *grows into later*, only when a real trigger
  justifies the extra cost and complexity (many servers, mobile apps, message queues, machine learning, and so
  on).

Throughout, a **→ FFP** tag means *"deliberately deferred; not built now, but designed so it slots in later
without a rewrite."* Deferring is a *decision*, not an oversight — the reasoning is always given, because
understanding **why** something is *not* in the MVP is as important as understanding what *is*.

### 0.3 How terms, links, and symbols work

- **Every acronym is expanded on first use** (e.g. "API — *Application Programming Interface*"). If you ever hit
  one that isn't, it's a bug in this doc — tell me.
- **Basics live in the 101 guides.** Rather than re-teach, say, how databases work, this roadmap links to the
  matching **101 guide** (e.g. [`database-101.md`](../idrm-mvp-guides/learn/database-101.md)). "101" is a
  beginner's convention meaning *"the introductory course."* Read the linked 101 when a topic is new to you;
  come back here for how IDRM *applies* it.
- **Deep specs live in the numbered docs.** Where the authoritative detail already exists (e.g. the data model
  in [`50-data-model.md`](50-data-model.md)), this roadmap *summarises and orients*, then links — one source of
  truth, never duplicated.
- **Clicking links:** in the VS Code editor use **Ctrl+Click** (Windows) / **Cmd+Click** (Mac); in the Markdown
  **Preview** a single click works. (Full explanation: [`instructions.txt`](../instructions.txt) §13.)

### 0.4 What "done" means

A feature is **done** only when three things exist together: the **code**, a **passing automated test**, and the
matching **conformance row** flipped to ✅ in [`26-conformance-pics.md`](26-conformance-pics.md). "It runs on my
screen" is *not* done. This is the discipline that keeps a novice-built system trustworthy (§14).

---

## 1. The big picture — Concept → MVP → FFP

### 1.1 What IDRM is, in one breath

**IDRM — *Integrated Disaster Response Management*** — is an India-focused, map-driven web platform that connects
disaster-affected people with the organizations and responders who can help them. The shorthand is **"Uber for
disaster relief":** a citizen raises a **help request** (medical, food, rescue, water, shelter), and the system
routes it to the nearest able responder, tracks it to completion, and records everything for accountability.

The single most important object is the **incident** — the technical name for a citizen's *help request*. (Naming
bridge you'll see often: the **UI says "help request"; the API and database say `incident`.**) Everything else in
the system exists to serve incidents, in a three-beat core loop:

> **sense → route → record** — *sense* a need (someone raises an incident), *route* it to the right responder,
> *record* the outcome and the audit trail.

New to the disaster domain itself? Start with
[`disaster-management-101.md`](../idrm-mvp-guides/learn/disaster-management-101.md) and
[`incident-management-101.md`](../idrm-mvp-guides/learn/incident-management-101.md); this roadmap assumes only the
core loop above.

### 1.2 Where this roadmap sits

There is already a bird's-eye **Concept → MVP → FFP roadmap** for the whole product at
[`../../docs/09-roadmap.md`](../../docs/09-roadmap.md) — read that for the *strategic* view (what gets built when, and why).

**This document is different: it is the *builder's* roadmap** — the hands-on, step-by-step guide to turning the
finished MVP specifications into working, tested code. Think of [`../../docs/09-roadmap.md`](../../docs/09-roadmap.md) as the
*map of the whole journey*, and this file as the *turn-by-turn driving directions* for the MVP leg.

### 1.3 The MVP in one diagram

```text
        ┌──────────────────────── one Ubuntu server ────────────────────────┐
        │                                                                    │
  Browser ──HTTPS──▶  Reverse proxy ──▶  FastAPI app  ──────▶  PostgreSQL + PostGIS
 (HTML/CSS/JS,       (TLS, static      (ONE "modular         (the single source of truth:
  Leaflet map)        files)            monolith":            users, incidents, locations…)
                                        10 modules)   ──────▶  MinIO (uploaded photos/PDFs;
                                                                the DB stores only the file's
                                                                key, never the file itself)
        │                                                                    │
        └────────────────────────────────────────────────────────────────────┘

   Deliberately NOT in the MVP (all → FFP): React / mobile apps · Redis · message
   queues & background workers · Docker/Kubernetes · an API gateway · microservices · ML.
```

Every box above is explained in the component map
[`tech-stack-101.md`](../idrm-mvp-guides/learn/tech-stack-101.md); the *why NOT* for each deferred item is in the
Architecture Decisions [`21-architecture-decisions.md`](21-architecture-decisions.md).

### 1.4 The finish line for this roadmap

When this roadmap is complete you (or a small team) will be able to: stand up the server, initialise the code,
load rich realistic sample data, run the app locally and on Ubuntu, exercise every module through automated
tests, and see each conformance row in [`26-conformance-pics.md`](26-conformance-pics.md) turn ✅ — a working,
inspectable IDRM MVP, built the right way, with nothing left mysterious.

---

## 2. The build philosophy (the five habits)

Five habits govern *how* we build. Each is a rule you can apply without deep technical knowledge; together they
are what separate a system that lasts from a pile of code that collapses under its own weight.

### 2.1 Foundation-first — *finalize the data before writing code*

The API, the web pages, and the tests are **all shaped by the data model** — just as every tap and wall in a
house is shaped by where the pipes run. Changing the data model *after* code exists means smashing the floor to
move a pipe: slow, expensive, and error-prone.

**Therefore (your directive, recorded in [`instructions.txt`](../instructions.txt) §15):** before any
code is written, we finalize the **data foundation** — (1) data modeling, (2) schema, (3) indexes & DB views,
(4) rich seed data, (5) user workflows & journeys — each with a recommendation and your sign-off. That is
**§3**, and it is the gate in front of the code (task G).

### 2.2 Module-by-module — *one room at a time, in dependency order*

The monolith has **ten modules** (rooms). We build them one at a time, in the order where each depends only on
what's already built:

> **Users/Auth first** (every feature needs a logged-in user with a role) → **Incidents** (the heart) →
> resources → locations → alerts → notifications → reports → files → audit → administration.

Building a whole room before starting the next means you always have something *complete and testable*, never a
house full of half-finished walls. (The detailed per-module plan is §13.)

### 2.3 Test-as-you-go — *inspect each room before moving to the next*

We do not build everything and test at the end. Each module ships with its **automated tests** written alongside
the code, and a feature is not "done" until its test passes (§0.4). This catches mistakes while they are cheap to
fix — minutes, not months. The full approach is §10, grounded in
[`70-quality-test-strategy.md`](70-quality-test-strategy.md).

### 2.4 PICS-driven — *build against a signed-off checklist*

**PICS — *Protocol Implementation Conformance Statement*** — is a fancy name for a simple, powerful idea: a table
that lists **every** obligation the system must meet, and, for each, whether it is done and what proves it. Ours
is [`26-conformance-pics.md`](26-conformance-pics.md), already **signed off** as the build gate. We do not invent
work as we go; we *discharge the checklist*, flipping each row to ✅ only when code + a passing test exist. This
is how you know, objectively, that the MVP is finished.

### 2.5 Phase discipline — *keep the MVP simple; route advanced tech to FFP*

Whenever the build meets an advanced temptation — Redis, message queues, containers, an API gateway, machine
learning — we do **not** silently add it, and we do **not** drop it. We **route it to FFP with a written reason**
(an "ADR — *Architecture Decision Record*"), so the MVP stays lean and the future stays designed-for. Nothing is
lost; everything is placed. (See [`21-architecture-decisions.md`](21-architecture-decisions.md) and §15.)

> **The five habits in one line:** *pour the foundation first, build one room at a time, inspect as you go, work
> the signed-off checklist, and keep the MVP simple by designing the future in — not bolting it on.*

---

## 3. The Data Foundation *(finalize before any code)*

This is **the gate**. By habit #1 (§2.1), the data model is the foundation and plumbing of the whole house — the
API, the web pages, and the tests are all *shaped by it*. So before a single line of application code is written,
we finalize five things and you sign them off:

> **(1) data modeling → (2) the schema → (3) indexes & views → (4) rich seed data → (5) user workflows & journeys.**

"**Finalize**" does not mean "perfect forever" — the schema can still evolve later through disciplined
migrations (§3.2). It means *"stable enough that we can build on it without expecting a rethink."* Each sub-section
below **teaches the idea**, then **orients you** to the authoritative spec (mostly
[`50-data-model.md`](50-data-model.md)) rather than re-printing it — one source of truth. New to databases
entirely? Read [`database-101.md`](../idrm-mvp-guides/learn/database-101.md) and, for the map side,
[`postgresql-postgis-101.md`](../idrm-mvp-guides/learn/postgresql-postgis-101.md) first; come back here for how IDRM
*applies* them.

### 3.1 Data modeling — from real-world things to database tables

**Data modeling** is the craft of writing down *the things your system remembers and how they connect*, before
you build anything. It is done in **three levels**, from plainest to most precise — the same three doc 50 uses:

| Level | Question it answers | IDRM example |
|---|---|---|
| **Conceptual** | *What real-world things exist, and how do they relate?* | "A **citizen** raises a **help request** at a **location**; a **provider** is assigned to it; every change is **recorded**." |
| **Logical** | *What does each thing know about itself, and in what quantities does it relate?* | "An incident has a `priority` and a `status`; it is reported by **0-or-1** user and assigned **0-or-1** organization." |
| **Physical** | *How is it actually stored in PostgreSQL?* | "Table `incidents`, column `status` of type `incident_status`, a spatial `location` column, a foreign key to `users`." |

A few terms, defined once (you'll meet them everywhere):

- **Entity** — a *kind of thing* worth remembering (a user, an incident). Becomes a **table**.
- **Attribute** — a *fact about* an entity (an incident's `priority`). Becomes a **column**.
- **Relationship** — a *link between* entities ("a user *reports* incidents").
- **Cardinality** — *how many* on each side of a relationship. "**One-to-many**" (one user, many incidents) is
  the commonest; "**one-to-one**" and "**many-to-many**" also occur. IDRM writes these as `1`, `0..1`
  (zero-or-one, i.e. optional), `0..N` (zero-or-many).
- **Primary key (PK)** — the column that *uniquely names* each row (IDRM uses a **UUID** — a random,
  non-guessable id). **Foreign key (FK)** — a column that *points at* another table's primary key (this is how
  tables link).

**IDRM's conceptual model in one breath:** a **User** (citizen) reports an **Incident** (help request) at a
**location** — a *guest* can report one too, so the reporter is optional. A **provider Organization** owns
**Resources** (ambulances, boats, beds) and gets **assigned** to incidents. Each status change writes an
**IncidentUpdate** (the timeline); photos/proof become **Files** (stored in MinIO). Users receive
**Notifications**; coordinators broadcast **Alerts**; every significant action is written to the **AuditLog**.

> The authoritative entity-relationship diagram (the "map of all the tables") is
> [`50-data-model.md`](50-data-model.md) §3–§4 — read it once alongside this paragraph and the shapes will click.

### 3.2 The database schema — the thirteen tables

The **schema** is the physical design: the exact tables, columns, and rules. The MVP has **13 tables**, grouped by
the module (room) they belong to:

| Module group | Tables | Backs the API |
|---|---|---|
| Users & auth | `users` · `user_sessions` · `password_reset_tokens` · `email_verification_tokens` | `/auth`, `/users` |
| Providers | `organizations` · `resources` | `/organizations`, `/resources` |
| **Core** | **`incidents`** · `incident_updates` | `/incidents` (+ transitions, `/updates`) |
| Comms | `alerts` · `notifications` · `notification_preferences` | `/alerts`, `/notifications` |
| Files | `files` (metadata only; bytes live in MinIO) | `/files` |
| Audit | `audit_logs` (append-only) | `/audit-logs` |

Every table follows the same **frozen conventions** (so nothing is a surprise): **UUID** primary keys,
`snake_case` names, `TIMESTAMPTZ` (timezone-aware, stored in UTC) for every `*_at` timestamp, and **soft delete**
(a `deleted_at` stamp instead of truly erasing a row — because in a disaster system you must never lose history).

The columns that can only hold *a fixed set of values* use a database **ENUM** (enumerated type) — the database
itself rejects anything off-list, so bad data cannot get in. The ones you must know:

| Enum | Allowed values |
|---|---|
| `user_role` | `citizen` · `provider` · `coordinator` · `admin` |
| `service_type` | `medical` · `food` · `rescue` · `water` · `shelter` · `other` |
| `priority` | `low` · `medium` · `high` · `critical` |
| **`incident_status`** | `created → (approved) → accepted → in_progress → completed → verified`, plus `cancelled` · `rejected` |

> **The full physical spec — every column, type, key, constraint, and the complete enum list — is
> [`50-data-model.md`](50-data-model.md) §5–§6. This roadmap deliberately does not re-print it** (one source of
> truth). Your job here is to *understand and confirm* it, not to re-derive it.

**How the schema changes safely (why "finalize" isn't a cage):** the schema is only ever created or altered
through **Alembic migrations** — small, versioned, reversible change-scripts — never by hand-editing the live
database ([`50-data-model.md`](50-data-model.md) §9). Migration **0001** builds the whole baseline (the PostGIS
extension → the enums → the 13 tables → the indexes → one shared `set_updated_at()` trigger). Later changes are
new migrations. This is what lets us commit to the model now and still evolve it responsibly later.

### 3.3 Indexes & database views — making reads fast and simple

**An index** is like the index at the back of a book: instead of scanning every page (every row) to find
something, the database jumps straight to it. IDRM uses four kinds (full list in
[`50-data-model.md`](50-data-model.md) §7):

- **GiST (spatial)** on every map column (`incidents.location`, `organizations.service_area_center`, …) — this is
  what makes *"find the help requests / providers **near** me"* fast. It is the single most important index in a
  map-driven system. (Why maps matter here: [`gis-for-emergency-response.md`](../idrm-mvp-guides/learn/gis-for-emergency-response.md).)
- **B-tree (filter)** on the columns we filter/sort by a lot (`incidents.status`, `priority`, `created_at`, …).
- **GIN (array / full-text)** for "which providers offer *medical*?" and for the `?q=` text search over an
  incident's description.
- **Unique** on things that must not repeat (`users.email`, an incident's guest `tracking_token`).

**A database view** is a *saved query that behaves like a read-only virtual table* — handy for presenting data in
a fixed shape. Here a deliberate MVP decision matters, and it is worth understanding:

> **MVP stance — logic lives in the Python service layer, not in the database.** IDRM keeps business logic in
> readable, testable Python (the module's `service`), **not** in database views, stored procedures, or triggers.
> The *one* exception is the tiny `set_updated_at()` trigger (it just stamps the "last changed" time). So the MVP
> ships with **essentially no business views** — "read models" (e.g. *"open incidents near me"*, *"my
> assignments"*) are built as **plain queries in the service layer**, where they are easy for a novice to read,
> unit-test, and change. *Rationale:* logic hidden inside the database is hard to test and version; keeping it in
> Python honours our test-as-you-go and independent-testability rules (§2.3, Task N). *(Materialized views and
> heavier read-optimisation are a documented → FFP option.)*

This directly answers the "common operations / views" question: the **common operations** are a small, named set
of service-layer queries (create incident, find-nearby, accept, progress, complete, verify, list-my-work), which
§4 (API) and §13 (per-module plan) enumerate; **views** in the DB sense are intentionally minimal in the MVP.

### 3.4 Rich, realistic seed data — the fake-but-real starter dataset

**Seed data** is realistic starter data we load into a fresh database so that (a) you can open the app and see it
*alive* — real names, real map pins — instead of blank screens, and (b) automated tests have meaningful data to
check against. You chose the **rich, realistic** option, so the spec below covers **all four roles** and incidents
across **all eight lifecycle states**, using **real Telangana / Andhra Pradesh coordinates** so the map and the
"nearest responder" search behave believably.

**Grounded in the PRD personas** (so scenarios read like real stories —
[`10-requirements-prd.md`](10-requirements-prd.md) §personas):

| Seed user | Role | Stands for | Home area (lat, lng) |
|---|---|---|---|
| **Rajesh Kumar** | `citizen` | An affected citizen needing help | Hyderabad (17.385, 78.486) |
| **Dr. Priya Sharma** | `provider` | A medical/NGO responder | Hyderabad (17.441, 78.391) |
| **Arjun Reddy** | `coordinator` | A volunteer coordinator | Warangal (17.978, 79.594) |
| **Lakshmi Iyer (IAS)** | `admin` | A senior government officer (oversight) | Vijayawada (16.506, 80.648) |
| + 2–3 extra citizens, 2 extra providers, 1 guest (no account) | mixed | volume for realistic lists & tests | across TG/AP |

**The rest of the dataset (spec):**

- **Organizations** (owned by the provider users): e.g. *"Priya Care Hospital"* (`hospital`, medical), *"Deccan
  Relief NGO"* (`ngo`, food + shelter), *"Warangal Volunteer Corps"* (`volunteer_group`, rescue) — each with a
  service-area centre + radius, some `is_verified = true` (verified by Lakshmi), some pending.
- **Resources** per organization: ambulances, a boat, hospital `beds`, water tankers — with locations and
  availability.
- **Incidents — at least one in every lifecycle state**, varied `service_type` and `priority`, real coordinates,
  **including one guest-submitted** incident (reporter `NULL`, with a `tracking_token`). This is what lets you (and
  the tests) exercise *every* transition and RBAC rule.
- **Supporting rows:** each incident's `incident_updates` timeline; a couple of coordinator `alerts` (e.g. a flood
  warning polygon over a district); some `notifications`; `files` metadata (an incident photo, a completion
  proof); and `audit_logs` for the significant actions.

**How it's loaded (the mechanism):** as an **idempotent** seed step — *idempotent* means *"safe to run many times;
running it twice does not create duplicates"* — implemented as a data migration / script keyed on stable values
(fixed UUIDs or lookup-by-email), exactly as [`50-data-model.md`](50-data-model.md) §9 prescribes. It becomes the
`make seed` command (§11). Per Task N, each **module** also gets its own small **default fixtures/profiles** so it
can be tested in isolation without loading the whole world.

**A worked taste** (illustrative — the authoritative row-by-row dataset will live in a dedicated deep-dive
sub-doc, [`34-seed-data-and-fixtures.md`](34-seed-data-and-fixtures.md), plus the real seed script at
[`../../code/scripts/seed.py`](../../code/scripts/seed.py)):

```text
users:        Rajesh Kumar  · role=citizen  · status=active · lang=en
              Dr. Priya S.  · role=provider · status=active
organizations: "Priya Care Hospital" · type=hospital · owner=Priya
                 · service_categories={medical} · centre=(17.441,78.391) · radius=15km · verified=true
resources:     "Ambulance-01" · org=Priya Care · kind=ambulance · qty=2 · available=true
incidents:     #A "Injured, need medical help" · service_type=medical · priority=critical
                 · status=in_progress · location=(17.390,78.470) · requester=Rajesh · assigned=Priya Care
incident_updates (timeline for #A):
                 created → approved (by Arjun) → accepted (by Priya Care) → in_progress
```

### 3.5 User workflows & journeys — how each role actually uses IDRM

A **user journey** is a step-by-step story of *one person achieving one goal*; a **workflow** is *the system's
process* that supports it. Because IDRM's whole life revolves around the incident lifecycle
(`created → … → verified`), each role's journey is essentially *"which transitions may I drive, and how?"* These
map 1:1 to the acceptance criteria in [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md)
and the screen flows in [`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md). Each journey below ends
with a **checklist** — the plain-language "done when…".

**① Citizen — Rajesh raises and tracks a help request** *(the core `sense` beat)*
1. Registers / logs in (or continues as a **guest**, journey ⑤).
2. Creates a help request: picks a `service_type`, sets the location on the map, describes it, optionally attaches
   one photo.
3. The system creates the `incident` (`status = created`), notifies coordinators, and shows Rajesh a live status.
4. Rajesh watches it move `accepted → in_progress → completed`, then **rates** it at `verified`.
> ✅ *Done when:* an incident exists, is visible to Rajesh with a live status, and he can rate it once resolved.

**② Provider — Dr. Priya discovers, accepts and completes** *(the `route` beat)*
1. Logs in; sees a **map of open, nearby** requests matching her service categories (the GiST proximity query).
2. **Accepts** one (`accepted`) — single-claim: it's now hers alone.
3. Progresses it (`in_progress`), then marks **completed** with a completion-proof photo.
> ✅ *Done when:* Priya can find nearby matching requests, claim one, progress it, and complete it with proof.

**③ Coordinator — Arjun approves and oversees** *(the oversight of `route`)*
1. Logs in to a coordinator view of all activity.
2. **Approves** `critical` incidents that need it (`created → approved`) so responders can act.
3. Oversees progress; **verifies** completed work (`completed → verified`), closing the loop.
> ✅ *Done when:* Arjun can approve critical requests, watch the live picture, and verify completed ones.

**④ Admin — Lakshmi manages and reports** *(governance + the `record` beat)*
1. Manages users and organizations; **verifies providers** (marks an org trustworthy).
2. Reviews the **audit trail** and pulls essential operational **reports**.
> ✅ *Done when:* Lakshmi can verify providers, manage accounts, and read the audit-backed reports.

**⑤ Guest — anonymous life-safety report**
1. Without an account, submits a minimal "lite" incident (one small photo allowed) for life-safety.
2. Receives a **tracking token** to follow it up later.
> ✅ *Done when:* a guest can raise an incident (reporter `NULL`) and track it by token.

> These five journeys, together, exercise **every** lifecycle transition and **every** role's permissions — which
> is exactly why they double as the backbone of the seed data (§3.4) and the module tests (§10, §13).

### 3.6 The data-foundation sign-off checklist *(this is the gate in front of coding)*

Before Task G (writing code) begins, we confirm — together — that each item below is settled. This checklist *is*
the gate:

> ✅ **SIGNED OFF — 2026-08-17.** All five items approved by the user. The gate is cleared; the build (Task G) may
> begin, starting with **Users/Auth** (§13). Item 3 confirmed the **logic-in-service, minimal-DB-views** approach.

- [x] **Conceptual & logical model** understood and agreed (§3.1 + [`50`](50-data-model.md) §3–§4).
- [x] **Physical schema** — the 13 tables, columns, keys, and **enums** — confirmed frozen for the MVP ([`50`](50-data-model.md) §5–§6).
- [x] **Indexes** confirmed; **views** decision accepted (logic-in-service; DB views minimal) (§3.3).
- [x] **Seed dataset** spec approved (all roles + all 8 states + TG/AP coords) and the idempotent-load mechanism agreed (§3.4).
- [x] **User workflows & journeys** (① – ⑤) approved as the behavioural backbone (§3.5).

> When these five boxes are ticked, the foundation is poured. **Only then** does §13's module-by-module build
> (starting with Users/Auth) begin — and the promised reminder fires (recorded in
> [`../instructions.txt`](../instructions.txt) §15, Task J).

---

## 4. The API layer — the contract every client speaks

With the foundation poured (§3), we build the **taps and switches**: the **API**. If §3 was *what the house
remembers*, §4 is *how anything makes the house do something*.

> **Why this matters so much:** IDRM is **API-first**. The very same API is used by the MVP's HTML/JavaScript
> pages **today** and, unchanged, by future React and mobile apps **tomorrow**. So the contract is a **product**,
> and its addresses (URIs) are **frozen for the whole life of the project** — the FFP only *adds* new endpoints at
> the same paths; it never renames one. Get this right once and every client, now and later, just works.

New to web APIs? Read [`rest-api-101.md`](../idrm-mvp-guides/learn/rest-api-101.md) first; this section then shows how
IDRM applies it. **The authoritative contract is [`40-api-specification.md`](40-api-specification.md) (human) +
[`40-api-openapi.yaml`](40-api-openapi.yaml) (machine-readable).** This roadmap teaches and orients — it does not
re-print every endpoint.

### 4.1 What "REST API" means (plain terms)

- **API — *Application Programming Interface*** — the agreed way one program asks another to do something.
- **REST** is a popular *style* of web API: you act on **resources** (nouns like *incidents*, *users*) that live at
  **URIs** (web addresses), using a few standard **HTTP methods** (verbs like *GET* and *POST*).
- **Endpoint** = one method + one path (e.g. `GET /api/v1/incidents` = "list the help requests").
- **Request / response** travel as **JSON** (plain-text data). Every response carries a **status code** — a
  3-digit number that says how it went (`200` OK, `201` created, `404` not found, and so on).
- **The naming bridge, again:** the UI says **"help request"**; the API resource is **`incident`**. Same thing.

### 4.2 The frozen conventions (learn once, they apply to *every* endpoint)

These are the house rules. Full statement in [`40-api-specification.md`](40-api-specification.md) §2; the essentials:

- **Base & version:** everything lives under **`/api/v1`**. The version sits *in the path*. Additive changes never
  bump it; only a true breaking change would ever make `/api/v2`. The FFP stays on `/api/v1`.
- **URIs are plural, lowercase nouns** (`/incidents`, `/organizations`, `/audit-logs`); a collection is
  `/incidents`, one item is `/incidents/{id}`, and a sub-list nests **one** level: `/incidents/{id}/updates`.
- **HTTP methods** map cleanly to intent:

  | Method | Means | IDRM use |
  |---|---|---|
  | `GET` | read | fetch a list or one record (never changes anything) |
  | `POST` | create **or** perform an action | create a record; drive a lifecycle transition |
  | `PATCH` | partial update | change a few fields of a record |
  | `DELETE` | *reserved* | records are **soft-cancelled**, never truly deleted |

- **JSON bodies** obey fixed shapes: field names are `snake_case`; ids are **UUID** strings; every timestamp is
  ISO-8601 **UTC** and ends in `_at`; location **inputs** are `{"latitude": …, "longitude": …}` while map
  **outputs** are GeoJSON; enum values are the exact lowercase strings from §3.2 (`"medical"`, `"in_progress"`).
- **Response shape** is predictable: **one record → a bare object**; **a list → wrapped** with paging:
  ```json
  { "data": [ /* … */ ], "pagination": { "page": 1, "limit": 20, "total": 137, "total_pages": 7 } }
  ```
  Lists support `?page=&limit=` (max 100), `?status=&service_type=&priority=` filters, `?sort=-created_at`
  (leading `-` = newest first), `?q=` search, and `?latitude=&longitude=&radius_km=` proximity.
- **Auth header:** authenticated calls send `Authorization: Bearer <access_token>`. **Language:**
  `Accept-Language: en|hi|te` picks the message language. **Tracing:** every response echoes an `X-Request-Id`
  (remember this — it reappears in §7 Logging as the thread that ties a request to its log lines).

### 4.3 The resource catalog (the URI map)

The MVP exposes twelve resource families — one per module area, plus a health probe (full map:
[`40-api-specification.md`](40-api-specification.md) §4–§5):

| Resource root | What it's for |
|---|---|
| `/auth`, `/users` | register, log in, refresh, profile, admin user management |
| **`/incidents`** | the core: create, list/map, detail, timeline, **and the lifecycle transitions** |
| `/organizations`, `/resources` | providers and their assets (ambulances, boats, beds) |
| `/locations` | PostGIS proximity, distance, reverse-geocode, GeoJSON map layers |
| `/alerts`, `/notifications` | coordinator broadcasts; per-user messages + preferences |
| `/reports`, `/audit-logs` | operational reports/exports; the read-only audit trail |
| `/files` | upload photos/PDFs (stored in MinIO; DB holds the key) |
| `/health` | liveness/readiness probe for operations |
| *`/disasters`, `/financial`, websockets* | **→ FFP** (event entity, donations, deep realtime) |

### 4.4 The incident lifecycle as dedicated endpoints (IDRM's signature pattern)

Most systems would let you `PATCH` a status field to anything. IDRM deliberately does **not** — because a status
change is never *just* a field: it has a **who** (which role may do it), a **body** (an ETA, a reason, a rating),
and **side-effects** (notifications, audit entries). So each transition is its **own** `POST` endpoint that guards
the rules of the lifecycle (`created → (approved) → accepted → in_progress → completed → verified`, plus
`cancelled`/`rejected`):

`POST /incidents/{id}/approve` · `/reject` · `/accept` · `/assign` · `/start` · `/complete` · `/verify` ·
`/cancel` — each restricted to the right role, each rejecting an **illegal jump** with `409 invalid_transition`.

> **Two guarantees worth remembering** (they come straight from the locked rules): **single-claim** — the first
> provider to `accept` wins and binds; a racing second attempt gets `409 already_accepted`. And **only the
> assigned provider** may `start`/`complete` — anyone else gets `403`. These two rules prevent the two classic
> disasters of relief coordination: *two teams racing to the same call* and *the wrong team closing someone
> else's job.* (Contract detail: [`40-api-specification.md`](40-api-specification.md) §5.2.)

### 4.5 A worked example (create → list → transition → error)

**Create a help request** — a citizen (or guest) `POST`s to `/api/v1/incidents`:
```http
POST /api/v1/incidents          Authorization: Bearer <token>
{ "service_type": "medical", "priority": "critical",
  "description": "Injured, need medical help near the bus stand",
  "location": { "latitude": 17.390, "longitude": 78.470 } }
```
```http
201 Created
{ "id": "9f1c…", "status": "created", "service_type": "medical", "priority": "critical",
  "location": { "latitude": 17.390, "longitude": 78.470 }, "created_at": "2026-08-17T09:12:00Z" }
```
*(A **guest** submission returns the same object plus a `tracking_token` to follow that one request without an
account.)*

**A list** comes back wrapped: `GET /api/v1/incidents?status=created&priority=critical` →
`{ "data": [ { … } ], "pagination": { "page": 1, "limit": 20, "total": 3, "total_pages": 1 } }`.

**A provider claims it:** `POST /api/v1/incidents/9f1c…/accept` with `{ "eta": "20m" }` → `200 OK` with the
incident now `"status": "accepted"`. If another provider already accepted, the contract returns the error below.

### 4.6 When things go wrong — the error envelope & fallback behaviour

**Every** error, everywhere, uses the *same* envelope — so a novice (and every client) only learns one shape:
```json
{ "error": { "code": "already_accepted",
             "message": "This request was already accepted by another provider.",
             "details": [] } }
```
`details` carries per-field problems, e.g. `[{ "field": "location.latitude", "issue": "must be between -90 and 90" }]`.
The shared status/`code` catalog (400, 401, 403, 404, 409, 410, 413, 422, 429, 500/503) is
[`40-api-specification.md`](40-api-specification.md) §6.

**"Fallback behaviour"** — *what the system does when a call can't simply succeed* — was on your wishlist, so here
it is pulled together in one place. The guiding principle is a life-safety one:

> **A primary life-safety action must never be lost because a *secondary* effect failed.** Raising an incident, or
> moving it forward, always succeeds and is recorded — even if a text message, an email, or a report can't be sent
> right now.

| Situation | What the client sees | The fallback |
|---|---|---|
| **Bad input** (missing field, impossible coordinate) | `422 validation_error` + `details` | Nothing is saved; the user is told exactly which field to fix. |
| **Access token expired** | `401 unauthorized` | Client silently calls `POST /auth/refresh` for a new token, then **retries** the original call once. |
| **Too many requests** | `429 rate_limit_exceeded` + `Retry-After: <seconds>` | Client **waits** the stated seconds, then retries (exponential back-off). Guest incident-create has a stricter budget than logged-in users. |
| **Concurrency clash** (two providers accept at once) | `409 already_accepted` | The loser is told cleanly; no double-assignment. Reads (`GET`) are always safe to retry; a create is **not** blindly auto-retried (to avoid duplicates). |
| **A notification channel is down** (SMS/email) | *the state change still returns success* | The transition commits; the message is **queued and retried** in the background. Near-real-time delivery is acceptable in the MVP (deep push → FFP). |
| **Weak / congested network** | slow or failing uploads | **Emergency "lite" mode**: capture one small (~≤ 500 KB) photo so it sends in seconds; files are shrunk on-device and **re-checked** server-side (never trust the client). |
| **Server fault / maintenance** | `500 internal_error` / `503 service_unavailable` | The `/health` probe lets operations detect it; clients set a sensible **timeout** and retry only **idempotent** (safe-to-repeat) operations with back-off. |

This table is also the seed of the **negative tests** in §10 — every row becomes an automated test that proves the
fallback actually happens.

### 4.7 How the API is proven (the tie to testing)

The contract is not just prose: [`40-api-openapi.yaml`](40-api-openapi.yaml) is a **machine-readable** description
that is validated automatically, and every endpoint gets **API tests** (§10) asserting its roles, its happy path,
and its error/fallback rows above. New to that idea? [`api-testing-101.md`](../idrm-mvp-guides/learn/api-testing-101.md).
Per Task N, each module owns its own API tests, so a module's contract can be verified in isolation.

---

## 5. Code structure — the FFP-extensible scaffold

Now the **wiring diagram** of the house: where every file lives. We draw it so carefully because of habit #5
(§2.5) — the MVP is *one* application today, but each module must be liftable into its own service *tomorrow*
**without surprises**. A good folder layout is what makes that future cheap.

New to how projects are organised, or to Git? Skim [`sdlc-101.md`](../idrm-mvp-guides/learn/sdlc-101.md) and
[`git-github-101.md`](../idrm-mvp-guides/learn/git-github-101.md). The authoritative layout is
[`20-architecture-system.md`](20-architecture-system.md) §; here we expand it to the file level and explain the
*why*.

### 5.1 The whole-repository layout

```text
idrm/
├── app/
│   ├── main.py                 # assembles the FastAPI app; wires every module's router
│   ├── core/                   # cross-cutting concerns shared by ALL modules
│   │   ├── config.py           #   settings, read from the environment (Pydantic BaseSettings)
│   │   ├── security.py         #   JWT sign/verify, bcrypt hashing, RBAC dependencies (→ §8)
│   │   ├── logging.py          #   structured-JSON logging setup (→ §7)
│   │   ├── dependencies.py     #   shared FastAPI deps: get_db, get_current_user
│   │   └── exceptions.py       #   the one error envelope + handlers (→ §4.6)
│   ├── infrastructure/
│   │   └── database/
│   │       ├── engine.py       #   SQLAlchemy engine + session (PostgreSQL + PostGIS)
│   │       └── base.py         #   declarative Base + shared mixins (timestamps, soft-delete)
│   └── modules/                # the TEN rooms — one folder each, IDENTICAL skeleton
│       ├── users/
│       │   ├── router.py       #   HTTP endpoints — thin: parse, authorize, call the service
│       │   ├── schemas.py      #   Pydantic request/response models (the API's JSON shapes)
│       │   ├── service.py      #   business logic — the rules; no HTTP, no raw SQL
│       │   ├── repository.py   #   data access — the ONLY place that talks to the database
│       │   └── models.py       #   SQLAlchemy / GeoAlchemy2 ORM tables (→ §3.2)
│       ├── incidents/          #   … same five files …
│       ├── resources/  locations/  alerts/  notifications/
│       └── reports/    files/       audit/  administration/
├── tests/
│   ├── conftest.py             # shared fixtures: disposable test DB + per-module seed PROFILES (§3.4, Task N)
│   ├── unit/<module>/          # UT — one folder per module (logic in isolation)
│   ├── integration/<module>/   # cross-layer + real DB behaviour
│   └── api/<module>/           # endpoint/contract tests (roles, happy path, the §4.6 fallbacks)
├── alembic/versions/           # migrations — the schema is created/changed ONLY here (§3.2)
├── frontend/                   # the served web UI (→ §9)
│   ├── templates/              #   server-rendered HTML
│   └── static/{css,js,img}     #   Tailwind CSS, vanilla JS, Leaflet, images
├── scripts/                    # seed.py (§3.4) and dev helpers
├── Makefile                    # the one-word task menu (→ §11)
├── pyproject.toml              # dependencies + tool config (black / flake8 / mypy / pytest)
├── .github/workflows/          # CI: lint + tests + coverage (→ §12)
└── README.md
```

### 5.2 The per-module skeleton — five files, one shape

Every module repeats the **same five files**, arranged as **layers** that only ever call *inward*. This is the
single most important structural idea in the codebase, so here it is with the *why*:

| File | Layer (role) | Knows about | Must **not** know about |
|---|---|---|---|
| `router.py` | **Edge** — HTTP in/out | request/response, roles, calling the service | the database, SQL |
| `schemas.py` | **Contract** — the JSON shapes | Pydantic validation of inputs/outputs | business rules |
| `service.py` | **Brain** — business logic | the rules, the lifecycle, RBAC decisions, audit | HTTP details, SQL syntax |
| `repository.py` | **Memory** — data access | SQLAlchemy queries, transactions | HTTP, business rules |
| `models.py` | **Shape** — ORM tables | table/column definitions (→ §3.2) | everything above it |

> **Why split it this way (Separation of Concerns, plainly):** each file has *one job*, so each is small, readable,
> and **testable on its own**. The `service` — where the important decisions live — has **no** web or database
> clutter, so you can unit-test the rules with fake data in milliseconds. HTTP quirks stay in `router`; SQL stays
> in `repository`. Change the database later and only `repository` moves; change the web framework later and only
> `router` moves. That is exactly the low-coupling that habit #2/Task N demands.

**A request's path through the layers** (this is [`30-design-data-flow-and-modules.md`](30-design-data-flow-and-modules.md)
made concrete): a call arrives → `router` checks the token and role, validates the body against `schemas` →
hands clean data to `service` → `service` applies the rules (e.g. "is this a legal lifecycle transition?"),
writes an audit entry, and asks `repository` to persist → `repository` runs one database transaction against the
`models` tables → the result travels back up, is shaped by `schemas`, and returns as JSON.

### 5.3 Cross-cutting `core/` — write it once, every module uses it

The `core/` folder holds what *all* modules share, so no module reinvents it: reading configuration from the
environment (`config.py`), the JWT + password + RBAC helpers (`security.py`, → §8), the **structured-JSON logging**
setup (`logging.py`, → §7), the shared FastAPI dependencies (`dependencies.py` — e.g. "give me the current user"),
and the **single error-envelope** handler (`exceptions.py`, → §4.6). This is the DRY principle — *Don't Repeat
Yourself* — in physical form.

### 5.4 Docstrings & naming (Task K) — the code explains itself

From the very first function (Task K, recorded in [`../instructions.txt`](../instructions.txt)
§15), **every apt function, method, and module carries a docstring** — a short built-in note, in triple quotes,
that a newcomer (or a tool) can read to understand it without deciphering the code:

```python
def accept_incident(incident_id: UUID, provider: Organization) -> Incident:
    """Assign an open incident to a provider (the single-claim rule).

    Args:
        incident_id: the incident to claim.
        provider:    the accepting provider organization.
    Returns:
        The updated incident, now status='accepted'.
    Raises:
        InvalidTransition: if the incident is not in a claimable state.
        AlreadyAccepted:   if another provider already claimed it (→ HTTP 409).
    """
```

Names follow ordinary Python style (`snake_case` functions/variables, `PascalCase` classes), enforced
automatically by **black / flake8 / mypy** (§10, `PICS-STK-QUALITY-01`). Good names + docstrings are not
decoration — they are what lets a *complete novice* return to this code in six months and still understand it.

### 5.5 Independent testability (Task N) & the FFP seam

Because a module is a **self-contained slice** — its own five files *and* its own `tests/unit|integration|api/<module>/`
folders with **default seed profiles** (§3.4) — you can exercise it **alone**, without standing up the whole app.
When one module needs another (say, *incidents* needs to know a *user's* role), it calls that module's **service**
— a clean, named doorway — never reaching into its tables directly.

> **This is the FFP payoff, and why §5 is worth the care.** That "clean doorway between modules" is *already the
> shape of a network boundary*. To grow into the FFP you lift, say, `modules/users/` into its own service, put the
> **APISIX** gateway in front, and turn the in-process service call into a network call — **and nothing else in the
> code changes.** That gradual, one-module-at-a-time extraction is the **Strangler Fig** pattern (a locked FFP
> decision, [`21-architecture-decisions.md`](21-architecture-decisions.md)). The scaffold you build for the MVP is,
> quite literally, the enterprise architecture in miniature — *designed-in, not bolted-on* (habit #5).

Secure-by-default coding habits that ride along in every layer (input validation at the edge, no secrets in code,
least privilege) are taught in [`secure-coding-101.md`](../idrm-mvp-guides/learn/secure-coding-101.md) and enforced in
§8. Per-module depth (what each of the ten actually does) is [`25-module-elucidation.md`](25-module-elucidation.md).

---

## 6. Concurrency & thread LLD — how many "things at once", safely

A web server must do **many things at once**, and during a disaster the requests **surge**. Sizing that "how many
at once" *on purpose* — with enough spare capacity that a surge never tips the box over — is what this section
settles. Your rule anchors it: **never plan to exceed ~70 % CPU** (the spare 30 % is the shock-absorber).

> **The full worked design — the formula, the math, the load-test plan — lives in the deep-dive
> [`31-concurrency-and-thread-model.md`](31-concurrency-and-thread-model.md).** Here is the orientation.

**How FastAPI runs work — three tiers:** ① a few **worker processes** (uvicorn, one per core-ish, for parallelism +
resilience); ② one **async event loop** per worker that juggles many **waiting** (I/O-bound) requests cheaply; ③ a
bounded **thread pool** for **heavy computing** (blocking, CPU-bound work) so it never freezes the loop. *The
golden rule: keep the event loop free — waits stay on the loop, heavy compute goes to the pool.*

**Every IDRM activity, classified** (so nothing is unaccounted for):

| Kind | Examples | Where it runs |
|---|---|---|
| **I/O-bound** (mostly waiting) | most API calls, DB reads/writes, MinIO uploads | the event loop (async) |
| **CPU-bound** (mostly computing) | password hashing (bcrypt), image resize/blur-check | bounded CPU thread pool |
| **Background** | notification send + retry, report generation, session cleanup | in-process scheduler + small pool (no Redis in MVP) |
| **Front-end-bound** | serving static files + HTML | reverse proxy (static) + loop |
| **Chatbot / ML** | — | **none in the MVP → reserved for FFP** |

**The formula, anchored to 4 vCPU / 16 GB** (parameterized on vCPU count `C`, so it auto-recomputes for any box —
your Round-1 choice). The whole *single box* also runs PostgreSQL + MinIO, so the 70 % ceiling is shared:

| Knob (at the 4 vCPU baseline) | Value | In one line |
|---|---|---|
| CPU ceiling `0.70 × C` | **2.8 vCPU** | the most we ever plan to use |
| Uvicorn workers `max(2, round(C/2))` | **2** | app processes (I/O-bound → few needed) |
| CPU-bound limit `max(1, floor(0.25×C))` | **1** | ≤1 heavy compute at once → no CPU blow-out |
| Background threads | **2** | jobs, scheduled off-peak |
| DB connections `W×5 + bg` | **12** | ≪ Postgres's 100 |

At 8 vCPU / 32 GB the same crank gives **4** workers, **2** concurrent heavy tasks, **22** DB connections — no
redesign. **Chatbot/ML reserve zero threads now** and gain their own service in the FFP (honest sizing today, clean
insertion later). These are **starting points confirmed by load testing** — the how (k6/Locust, watch CPU ≤ 70 %,
p95 latency, event-loop lag) is in [`31`](31-concurrency-and-thread-model.md) §7.

---

## 7. Logging & diagnostics — the app's diary, done right

When something fails during a flood at 2 a.m., an engineer must find *the one request that broke* in seconds — and
no citizen's private data must ever leak into a log file. That is what logging design buys us.

> **The full specification — fields, levels, redaction, retention, the diagnosis workflow — is the deep-dive
> [`32-logging-and-diagnostics.md`](32-logging-and-diagnostics.md).** Here is the orientation.

**First, a distinction a novice must not blur:**

- **Application logs** (this section) = the operational **diary** for *engineers* — requests, timings, errors —
  written to the OS log stream.
- **Audit trail** (`audit_logs` table, [`22`](22-architecture-security-and-iam.md)) = the tamper-evident **business
  record** of *who did what to which resource*, read via `GET /audit-logs`.

*If it helps an engineer fix/run the system, it's a log; if it holds someone accountable, it's an audit entry.*
IDRM keeps both.

**Structured JSON (your choice).** Every log line is a small JSON record, so it's searchable and FFP-ready. Its
fields capture the **elements of circumstance** — *who / what / when / where / outcome*:
```json
{ "ts":"…Z", "level":"INFO", "logger":"incidents.service", "event":"incident.create",
  "request_id":"req_7f3a…", "user_id":"9f1c…", "role":"citizen", "status":201, "latency_ms":42, "outcome":"success" }
```

**The four things that make logs useful (all detailed in [`32`](32-logging-and-diagnostics.md)):**

1. **Levels** — `DEBUG` (off in prod) · `INFO` (normal events) · `WARNING` (recoverable oddities) · `ERROR`
   (a failure, with stack trace) · `CRITICAL` (system in danger). Default production level = `INFO`.
2. **The `request_id` thread** — the `X-Request-Id` (§4.2) is stamped on a request and **auto-attached to every
   log line** it produces, then echoed to the client. Filter by it → the *complete story* of one request.
3. **Redaction (DPDP Act 2023)** — a filter in `core/logging.py` guarantees **secrets are never logged**
   (passwords, tokens) and **personal data is masked** (`+9198••••3210`); photo EXIF/GPS is stripped, file bytes
   never logged. Designed in, so a naïve log line *can't* leak.
4. **Where they go (MVP)** — JSON to **stdout → journald** (and/or a rotating `/var/log/idrm/` file), kept ~14–30
   days via `logrotate`; the audit trail is kept longer. **No central aggregation in the MVP** — Loki/ELK,
   OpenTelemetry traces, and Prometheus/Grafana metrics are the **→ FFP** upgrade the JSON format makes drop-in.

**The payoff:** a user hits an error and sees a support code (the `X-Request-Id`); the engineer greps journald for
that one id and sees every line of that request — minutes to diagnosis, not hours. Verified by tests that assert
JSON shape, a present `request_id`, and **no PII leakage** (§10; [`32`](32-logging-and-diagnostics.md) §9).

---

## 8. Security in practice — who gets in, and what they may do

Security in IDRM is **built in, not bolted on** — it exists from day one, before features. Five principles guide
every choice below: **Zero Trust** (never trust, always verify), **Least Privilege** (minimum access),
**Secure by Default**, **Defense in Depth** (layered checks), and **Accountability** (everything significant is
audited). The authoritative spec is [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md);
this section is the *practitioner's* view and maps directly onto the code layers of §5. Primers:
[`iam-101.md`](../idrm-mvp-guides/learn/iam-101.md) · [`rbac-abac-101.md`](../idrm-mvp-guides/learn/rbac-abac-101.md) ·
[`secure-coding-101.md`](../idrm-mvp-guides/learn/secure-coding-101.md) · [`threat-modeling-101.md`](../idrm-mvp-guides/learn/threat-modeling-101.md).

### 8.1 Authentication — proving *who you are*

- **Lifecycle:** register → **verify email** (`pending → active`) → sign in. You can't act until verified (except
  the guest life-safety path, below).
- **Tokens:** on login you get a short-lived **access token** (a **JWT — JSON Web Token** — signed with **RS256**,
  ~60 min) sent as `Authorization: Bearer …` on every call, plus a longer-lived **refresh token** (~7 days) to get
  new access tokens. *Why RS256 (asymmetric):* the app signs with a **private** key; anyone verifies with the
  **public** key holding no secret — so when the FFP splits modules into services behind APISIX, they verify the
  *same* tokens with zero code change.
- **Passwords:** stored only as a **bcrypt** hash (cost 12); policy follows NIST — **length beats forced
  composition** (≥ 8, all characters allowed), **breached/common passwords are blocked**, and there is **no forced
  rotation**. *Why gentler:* IDRM's users are often stressed, on phones, with low digital literacy — "long but
  simple" is both more secure in practice and less likely to lock out someone who needs help.

### 8.2 Sessions & cookies

- **Sessions live in PostgreSQL** (the `user_sessions` table) — **no Redis** in the MVP. Each refresh token is a
  row; **logout deletes the row**, which is what makes a session instantly **revocable**. Refresh tokens are
  **rotated on use** (a used one is retired), so a stolen old token is useless.
- **Cookies, handled safely:** where the web UI stores a token in a cookie, the cookie is **`HttpOnly`** (JavaScript
  cannot read it → defeats token theft via XSS), **`Secure`** (sent only over HTTPS), and **`SameSite`** (blunts
  CSRF — a forged cross-site request). These, plus security headers (**CSP, HSTS**) and a **CORS allow-list** of
  known origins, are the "secure defaults" every response inherits from `core/` (§5.3).

### 8.3 Rate-limiting & lockout — abuse protection

- **Account lockout:** **5 failed logins → 15-minute lock** (`failed_login_attempts`, `locked_until`). *Why 15,
  not 30:* short enough that a fumbling user in an emergency isn't shut out for long.
- **Per-endpoint rate limits** (login 5/min, register 10/min, create-incident 20/min, **guest create 5/min** — the
  tightest); over budget → **`429` + `Retry-After`** (the fallback in §4.6). The MVP enforces these **in the app**;
  centralised/distributed rate-limiting and a **WAF** arrive with the **APISIX** gateway → FFP.

### 8.4 Allow-lists & deny-lists (what "black/white-listing" means in the MVP)

You asked about black/white-listing, prioritization, and blocking. Here is the **honest MVP picture** — these exist
today as **static, rule-based** controls, not yet as intelligent, adaptive ones:

| Control | Kind | How it works in the MVP |
|---|---|---|
| **Account status** `suspended`/`deactivated` | user **deny-list** | a suspended user is blocked from acting |
| **Verified organizations** | provider **allow-list** | only a coordinator-**verified** org can fully claim/act |
| **Token revocation** (logout / rotation) | credential **deny-list** | a revoked/rotated refresh token can't be used |
| **Blocked passwords** | value **deny-list** | breached/common passwords rejected at registration |
| **CORS origins** | request **allow-list** | only known front-end origins may call the API |
| **Guest path** | scoped **allow** | an unauthenticated person may do exactly one thing (§8.5) |

> **The FFP line (important, and it's your Task M):** *dynamic, intelligence-driven* lists — reputation-based
> **IP/user blacklisting**, **prioritization** of users/sessions under load, and **anomaly-driven** throttling — are
> **→ FFP**, specified by the **Anomaly-Detection (AD) engine #1** white paper (Task M,
> [`../instructions.txt`](../instructions.txt) §15). The MVP's rule-based controls above are
> the seam those engines later plug into — designed-in, not bolted-on.

### 8.5 Where authorization is enforced — defense in depth

**RBAC — Role-Based Access Control** — over four roles (**citizen · provider · coordinator · admin**) plus the
narrow **guest** path. Enforcement is **two-layered**, matching §5:

1. **Role check at the router (edge):** a dependency on every protected route confirms the token's role may perform
   the operation — the full **role → operation** map is [`22`](22-architecture-security-and-iam.md) §3. A failed
   check → **`403 forbidden`**; an unauthenticated call to a protected route → **`401`**.
2. **Ownership / assignment check in the service (brain):** on top of the role, the service confirms *this* user may
   touch *this* record — a citizen edits only **their own** incident; only the **assigned** provider may
   `start`/`complete`. Everything is **deny-by-default**.

The **guest** gets a single scoped door: `POST /incidents` for life-safety, returning a **tracking token** that
grants read-only access to that **one** incident and its photo upload — nothing else.

### 8.6 Data protection, secrets & accountability (in brief)

- **In transit:** all HTTPS / **TLS 1.2+**. **Injection-proof:** Pydantic validates at the edge; SQLAlchemy uses
  **parameterised queries** (never string-built SQL). **Files:** the MinIO bucket is **private**, served as
  time-limited **pre-signed URLs**, EXIF/GPS-stripped.
- **Secrets** (DB, MinIO, JWT signing keys) are read from **environment variables**, **never committed to code**;
  the setup script's placeholder credentials **must be changed** before any non-local use. *(A secrets **vault/KMS**
  and field-level **AES-256** at rest are → FFP.)*
- **Accountability:** the append-only **audit trail** (§7's other half) records every sensitive action — logins,
  lockouts, each lifecycle transition, org verification, role changes — kept **≥ 1 year** (7-year compliance
  target). This is the **`record`** beat of `sense → route → record`.

### 8.7 How it's proven, and the FFP seam

Security is **tested per operation** (§10): the RBAC map becomes a test that asserts every role gets ✓ or `403`
correctly; lockout and rate-limits get their own tests; and the no-PII log test (§7) guards privacy. All of it is
part of the **Definition of Done** (§14). Deferred to FFP (recorded, not dropped): **OIDC/SSO, MFA, ABAC**, the
**APISIX WAF/gateway**, a **secrets vault**, and the **AD-driven dynamic lists** of §8.4 — see
[`21-architecture-decisions.md`](21-architecture-decisions.md) and [`22`](22-architecture-security-and-iam.md) §9.

---

## 9. Web layer & design system — one coherent, accessible face

The web UI is where a frightened person meets IDRM, so it must be **consistent, high-contrast, and obvious on a
basic phone**. The **stack** is deliberately simple (ADR-004): **HTML5 · Tailwind CSS v4 · vanilla JavaScript ·
Leaflet** for the map — **served same-origin by FastAPI** (so no CORS in the MVP). No React/TypeScript — those are
**→ FFP**, and because every screen names the API it calls, a React client later rebuilds the same UI against the
**same** endpoints.

> **The full design system — tokens, components, templates, the page-transition map, accessibility — is the
> deep-dive [`33-design-system.md`](33-design-system.md).** Screens and their API calls are
> [`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md). Here is the orientation.

- **A design system = the reusable rulebook** (colours, type, spacing, components) so every page is one product,
  not a patchwork — the house's interior-design scheme.
- **Tokens** (named values like `--color-primary`, `--space-4`) are the single source of visual truth, defined once
  in Tailwind v4's `@theme`; change a token, change the whole app. Colours are **accessibility-checked (WCAG 2.2
  AA)** and **priority colours are locked** (critical=red, high=orange, medium=amber, low=green) — always paired
  with an icon + label, **never colour alone**.
- **Visual hierarchy:** one primary action per screen; critical info (priority, status) loudest; generous spacing +
  large tap targets for a phone in a crisis.
- **Components** (buttons, forms, cards, tables, status badges, map markers, toasts, the alert banner, modals, the
  nav) are built **once** as HTML partials + shared classes + tiny JS, each with defined **states** and
  **accessibility** baked in.
- **Templates & transitions:** one **app shell** (header · role-aware nav · alerts banner · content · footer) and a
  shallow, predictable **page-transition map** (rarely more than two clicks to any action); role-forbidden nav is
  hidden **and** server-enforced (§8.5).
- **Low bandwidth & a11y:** system fonts (no downloads), client-side image compression, lazy map tiles;
  keyboard-operable, visible focus, semantic HTML, `prefers-reduced-motion` respected — verified by automated
  accessibility checks (§10) as part of the Definition of Done.

Rich data-viz dashboards, offline-first capture, deep real-time push, and full localization are **→ FFP**.

---

## 10. Quality & test automation — proving each room is safe

This is the **safety inspection** of the house (§0.1). By habit #3 (test-as-you-go), tests are written *alongside*
the code, run on *every* change, and a feature isn't "done" until its acceptance criteria each have a **passing
test**. The authoritative plan is [`70-quality-test-strategy.md`](70-quality-test-strategy.md); primers:
[`testing-101.md`](../idrm-mvp-guides/learn/testing-101.md) · [`api-testing-101.md`](../idrm-mvp-guides/learn/api-testing-101.md) ·
[`accessibility-testing-101.md`](../idrm-mvp-guides/learn/accessibility-testing-101.md).

### 10.1 The testing pyramid (many small tests, few big ones)

The guiding shape is **shift-left**: lots of fast, cheap tests at the bottom, a few slow, broad ones on top.

| Level | Share | What it checks (IDRM examples) | Tool |
|---|---:|---|---|
| **Unit (UT)** | ~60 % | one function in isolation: the **lifecycle state machine** (legal/illegal transitions), the **single-claim** rule, RBAC checks, validators, metric math | `pytest` |
| **API** | ~20 % | each endpoint's **contract**: status codes, body shape vs the OpenAPI, auth (401/403), validation (422), conflicts (409) | `pytest` + FastAPI `TestClient`/`httpx` |
| **Integration (IT)** | ~15 % | flows through **real PostgreSQL + PostGIS**: full `create→verified` walk, **proximity** search, **concurrent claim** resolves to one winner, audit rows written, MinIO put/get | `pytest` + disposable test DB + test bucket |
| **System / E2E** | ~5 % | a few whole journeys in a browser: citizen report → provider claim → complete → verify; guest submit | Playwright *(kept light; heavy E2E → FFP)* |

> **Novice translation:** a **unit** test asks "does this one gear turn correctly?"; an **API** test asks "does this
> one tap give the right water?"; an **integration** test asks "does turning the tap actually fill the tank?"; a
> **system/E2E** test asks "can a real person wash their hands end to end?"

### 10.2 Per-module independent tests (Task N)

Matching the code layout (§5.1), each module owns its own tests: `tests/unit/<module>/`,
`tests/integration/<module>/`, `tests/api/<module>/`, plus **default seed profiles** in `conftest.py` (the §3.4
personas/fixtures). So any module can be exercised **in isolation** — you can prove *incidents* works without
standing up *reports* — which is exactly the low-coupling that lets a module later become its own service. Fixtures
build users per role, orgs, and incidents in known states; **spatial fixtures use real Telangana/AP coordinates** so
PostGIS proximity tests are meaningful; SMS/email and other externals are **stubbed** (never really called).

### 10.3 The tests that guard the hard parts

The earlier sections seeded specific test suites — here they come home:

- **Fallback/negative tests (from §4.6):** every row of the fallback table becomes a test — bad input → 422,
  expired-token → refresh-and-retry, over-budget → 429, concurrent-accept → 409, notification-down → state still
  commits.
- **Security suite (from §8):** the **RBAC matrix** becomes a test asserting every role gets ✓ or `403` correctly on
  every operation; **lockout** (5 fails → 15-min) and **rate-limit** (429) each get a test; injection resistance is
  checked. *(This is the "auth / authz / rate-limiting automated testing" you asked for.)*
- **Privacy test (from §7):** a login/upload test proves **no secret or PII** appears in the emitted logs.
- **Accessibility test (from §9):** automated **axe** checks + keyboard-only walkthroughs on key templates assert
  WCAG 2.2 AA (contrast, labels, focus, ARIA).

### 10.4 Quality gates (the automatic bar every change must clear)

Run locally before a pull request, then enforced in CI (§12):

| Gate | Standard |
|---|---|
| **Format** | Black + isort (auto-applied) |
| **Lint** | Ruff — no errors |
| **Types** | mypy — clean (Python type hints throughout) |
| **Docstrings** | present on apt functions/modules (Task K) |
| **Tests** | full suite green |
| **Coverage** | **≥ 80 %** overall (hard floor 70 %), higher on critical paths (lifecycle, auth, claim) |
| **Security** | no high/critical dependency vulns; the authz suite green |

**Coverage** = the share of code lines actually exercised by tests; 80 % is the agreed confidence bar. Every gate is
a one-word `make` target (§11) and a CI check (§12), so "is it good enough?" is answered by a machine, not opinion.
Heavier testing — surge **performance/load** (k6/Locust), **DAST** (OWASP ZAP), cross-browser grids, **DORA**
delivery metrics, cross-service **contract** tests — is **→ FFP** ([`70`](70-quality-test-strategy.md) §6). Tests are
how each [`26-conformance-pics.md`](26-conformance-pics.md) row earns its ✅.

---

## 11. Build & run automation — one-word commands via `make`

A **Makefile** is a **menu of one-word commands** that each hide a long, easy-to-mistype command underneath. Instead
of remembering `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`, a novice types `make run`. You chose the
**full generic task menu**, so *every* routine job — setup, run, seed, test, lint, migrate — is one reliable word,
identical on a laptop and on the server and in CI (§12). Primers:
[`linux-101.md`](../idrm-mvp-guides/learn/linux-101.md) · [`git-github-101.md`](../idrm-mvp-guides/learn/git-github-101.md).

### 11.1 First, the platform (recap of [`80-ops-deployment-and-operations.md`](80-ops-deployment-and-operations.md))

The MVP runs **natively on Ubuntu** (no Docker): the idempotent installer
[`setup-idrm-ubuntu.sh`](../../archive/scripts/setup-idrm-ubuntu.sh) provisions **PostgreSQL 16 + PostGIS 3.4**,
**MinIO** (S3-compatible object storage), and a **Miniconda** env `idrm-mvp` with the Python dependencies. All
settings/secrets come from a git-ignored **`.env`** (`DATABASE_URL`, `S3_*`, the RS256 `JWT_*` key paths, …) — never
committed. **The installer ships placeholder credentials that must be changed before any non-local use.** In
production the app is a **systemd** service (`idrm`) running uvicorn behind a lightweight reverse proxy (TLS on 443).

### 11.2 The Makefile (the generic menu)

```makefile
# IDRM MVP — task menu.  Run `make help` to list targets.
.DEFAULT_GOAL := help

setup:      ## one-time: create the conda env + install dependencies (or run the Ubuntu installer)
	conda env create -f environment.yml || conda env update -f environment.yml
install:    ## refresh Python dependencies from pyproject.toml
	pip install -e ".[dev]"
migrate:    ## apply DB schema to latest (Alembic)
	alembic upgrade head
seed:       ## load the rich, idempotent sample data (§3.4)
	python scripts/seed.py
run:        ## start the app locally with auto-reload (http://127.0.0.1:8000)
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

format:     ## auto-apply Black + isort
	black app tests && isort app tests
lint:       ## Ruff — no errors allowed
	ruff check app tests
typecheck:  ## mypy — clean
	mypy app
test:       ## run the whole pytest suite
	pytest
test-unit:  ## just the fast unit tests
	pytest tests/unit
test-integration: ## integration tests (needs the test DB + bucket)
	pytest tests/integration
test-api:   ## API contract tests
	pytest tests/api
coverage:   ## tests + coverage report, fail under 80%
	pytest --cov=app --cov-report=term-missing --cov-fail-under=80

qa:         ## the pre-PR gate: everything a machine can check, in order
	$(MAKE) format lint typecheck coverage
clean:      ## remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
help:       ## list every target with its description
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n",$$1,$$2}'
```

### 11.3 What the everyday flows look like

- **A fresh laptop, from zero to a running app with data:**
  ```bash
  make setup      # env + dependencies (once)
  make migrate    # build the schema
  make seed       # load the personas + incidents across all 8 states (§3.4)
  make run        # open http://127.0.0.1:8000
  ```
- **Before every pull request (one command):** `make qa` — formats, lints, type-checks, and runs the full suite
  with the **≥ 80 % coverage** gate (§10.4). If `make qa` is green, your change meets the bar.
- **On the Ubuntu server:** the installer + `.env` + `make migrate` + `sudo systemctl restart idrm`; health via
  `systemctl status postgresql minio idrm` and `journalctl -u idrm -e` (the §7 logs).

> **Why a generic menu matters (habit-forming, novice-proof):** the *same* words work everywhere, so nobody memorises
> fragile incantations, onboarding is "run `make help`", and — crucially — **CI (§12) runs these exact targets**.
> There is one definition of "how to build, run, and check IDRM", and it lives in the Makefile. *(Make is native on
> the Ubuntu target and in CI; on a Windows dev box use WSL or the Git-Bash shell.)*

---

## 12. CI pipeline — the tireless robot that checks every change

**CI — Continuous Integration** — is a robot (here, **GitHub Actions**) that, **every time code is pushed or a pull
request is opened**, spins up a clean machine and runs the same checks a developer runs locally. It catches mistakes
the moment they happen, before they reach anyone else. You chose a **minimal MVP CI** (lint + tests + coverage);
heavy delivery pipelines, containers, and deploy automation stay **→ FFP**. Primer:
[`ci-cd-101.md`](../idrm-mvp-guides/learn/ci-cd-101.md).

### 12.1 What the pipeline does

On every push to `main` and every pull request, it: starts a throwaway **PostgreSQL + PostGIS** and **MinIO** (so
integration tests have a real database and object store), installs dependencies, applies migrations, then runs the
**exact same `make` targets** from §11 — `lint`, `typecheck`, `coverage` (with the **≥ 80 %** gate) — plus a
**dependency vulnerability scan**. Because CI reuses the Makefile, "what CI checks" and "what you run locally" can
never drift apart.

### 12.2 The workflow (`.github/workflows/ci.yml`)

```yaml
name: CI
on:
  push: { branches: [ main ] }
  pull_request:
jobs:
  quality:
    runs-on: ubuntu-latest
    services:
      postgres:                       # a real PostGIS DB for integration tests
        image: postgis/postgis:16-3.4
        env: { POSTGRES_USER: idrm_user, POSTGRES_PASSWORD: test, POSTGRES_DB: idrm_db }
        ports: [ "5432:5432" ]
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      minio:                          # a real S3-compatible store (auto-starts, makes the bucket)
        image: bitnami/minio:latest
        env: { MINIO_ROOT_USER: idrm, MINIO_ROOT_PASSWORD: idrm-secret, MINIO_DEFAULT_BUCKETS: idrm-uploads }
        ports: [ "9000:9000" ]
    env:
      DATABASE_URL: postgresql+asyncpg://idrm_user:test@localhost:5432/idrm_db
      S3_ENDPOINT: http://localhost:9000
      S3_BUCKET: idrm-uploads
      S3_ACCESS_KEY: idrm
      S3_SECRET_KEY: idrm-secret
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: make install            # pip install -e ".[dev]"
      - run: make migrate            # alembic upgrade head
      - run: make lint typecheck     # ruff + mypy
      - run: make coverage           # pytest --cov ... --cov-fail-under=80
      - run: pip-audit               # fail on known high/critical dependency vulnerabilities
```

### 12.3 Branch protection & the FFP seam

- **Branch protection:** `main` is configured to **require the `quality` check to pass before a pull request can
  merge** — so unreviewed or failing code simply cannot land. This is where the Definition of Done (§14) becomes
  *enforced*, not just aspirational.
- **Deliberately NOT in the MVP (→ FFP):** automated **deployment/CD** to the server, container image builds,
  Kubernetes, blue-green/canary releases, **DAST** (OWASP ZAP) and **DORA** delivery metrics. The MVP deploys the
  old-fashioned safe way (§11.3: installer + `make migrate` + `systemctl restart`); CI's job here is purely to
  **guard quality**, and it does so from day one at almost no cost.

> **The whole quality story in one line:** developers run `make qa` locally → CI runs the same targets on every
> push → `main` won't accept anything that fails → every merged change already meets the bar. Simple, cheap, and
> exactly the good habit a novice team benefits from most.

---

## 13. Module-by-module build plan — building the ten rooms

This is where everything above becomes a **sequence of concrete work**. We build **one module (room) at a time**
(habit #2), each finished — code + tests + docs + its ✅ PICS rows — before the next begins.

> **⛔ The gate, restated (your directive):** this plan is the *how*; it does **not** start until the **data
> foundation (§3) is signed off** (§3.6). Writing code before the model is settled means smashing the floor later.
> When we reach that point, the promised reminder fires (recorded in
> [`../instructions.txt`](../instructions.txt) §15, Task J). Everything below is the plan we
> execute *after* that sign-off.

### 13.1 The universal module recipe (the same ten steps, every room)

Because §5 gave every module the *same five-file shape*, every module is built with the **same repeatable recipe** —
learn it once, apply it ten times:

1. **Models** — the SQLAlchemy/GeoAlchemy2 tables (§3.2) + an **Alembic migration** (`make migrate`).
2. **Schemas** — the Pydantic request/response shapes (the API contract, §4.2).
3. **Repository** — the data-access queries (the only DB-touching layer).
4. **Service** — the business rules + RBAC decisions + audit writes (§8, §5.2).
5. **Router** — the endpoints, each with its role dependency (§8.5).
6. **Fixtures/seed profile** — the module's default test data (§3.4, Task N).
7. **Tests** — **UT + API + IT** for this module (§10), including its RBAC and fallback rows.
8. **Docstrings** — on every apt function (Task K); `make lint typecheck` clean.
9. **Flip PICS rows** — turn this module's [`26-conformance-pics.md`](26-conformance-pics.md) rows `Planned → ✅`
   **only** when code + a passing test exist (habit #4).
10. **Definition of Done** — run the §14 checklist; update the CHANGELOG; merge behind green CI (§12).

Per-module depth (the *what/why/how* of each) is [`25-module-elucidation.md`](25-module-elucidation.md); the exact
endpoints are [`40-api-specification.md`](40-api-specification.md); the RBAC cells are
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) §3.

### 13.2 The build order (dependency-justified)

| # | Module(s) | Why here |
|---|---|---|
| 1 | **USR** users/auth | everything needs a logged-in user with a role; nothing works without identity |
| — | **AUD** audit · **FIL** files | **cross-cutting — started with USR/INC**: audit is written by every module from day one; files (incident photos) are needed by INC |
| 2 | **INC** incidents | the heart — the lifecycle the whole product exists for |
| 3 | **ORG** organizations · **RES** resources | the providers (and their assets) who *claim* incidents |
| 4 | **LOC** locations/geo | proximity, distance, map layers — enriches INC + ORG |
| 5 | **ALR** alerts · **NTF** notifications | the comms layer over the now-working core |
| 6 | **RPT** reports | needs accumulated incident/audit data to report on |
| 7 | **ADM** administration | user/org management + verification surface (rides on USR + ORG) |

### 13.3 Worked module ①: **USR — Users & Auth** (the template, built first)

| Aspect | Plan |
|---|---|
| **Purpose** | identity, roles, sessions — the security foundation |
| **Entities** | `users`, `user_sessions`, `password_reset_tokens`, `email_verification_tokens` ([`50`](50-data-model.md) §5.1–5.2) |
| **Key endpoints** | `POST /auth/register · verify-email · login · refresh · logout · forgot/reset-password`; `GET/PATCH /users/me`; admin `GET /users`, `PATCH /users/{id}` ([`40`](40-api-specification.md) §5.1) |
| **Rules** | RS256 JWT (access ~60 min + rotating refresh ~7 d); **bcrypt cost-12**; NIST password policy; **5-fail/15-min lockout**; sessions in Postgres |
| **RBAC** | public auth routes; `me` = own; user management = coordinator/admin; role/status change = admin only |
| **Tests** | UT: password policy, lockout counter, token sign/verify · API: 200/401/403/409 on each route · IT: register→verify→login→refresh→logout round-trip |
| **PICS** | flip `PICS-USR-*` (incl. `USR-007` guest) as each lands |
| **✅ Done when** | all USR endpoints pass, the RBAC + lockout + no-PII tests are green, `PICS-USR-*` are ✅ |

### 13.4 Worked module ②: **INC — Incidents** (the core, built second)

| Aspect | Plan |
|---|---|
| **Purpose** | capture and drive help requests through the 8-state lifecycle |
| **Entities** | `incidents`, `incident_updates` (+ geometry; uses `files` for photos) ([`50`](50-data-model.md) §5.5–5.6) |
| **Key endpoints** | `POST /incidents` (+ guest); `GET /incidents`, `/{id}`, `/mine`, `/assigned`, `/nearby`, `/{id}/updates`; transitions `POST …/approve·reject·accept·assign·start·complete·verify·cancel` ([`40`](40-api-specification.md) §5.2) |
| **Rules** | the **state machine** (illegal transition → `409`); **single-claim** (first `accept` wins → `409 already_accepted`); assigned-provider-only `start`/`complete` (→ `403`); rating 1–5 at `verify` |
| **RBAC** | citizen creates/verifies/cancels own; provider accepts/starts/completes assigned; coordinator approves/rejects/assigns; guest creates one (tracked) |
| **Tests** | UT: the state machine (every legal + illegal transition), single-claim rule · API: each transition's role + 409/403 · IT: full `create→verified` walk on real PostGIS; **concurrent-claim resolves to one winner** |
| **PICS** | flip `PICS-INC-*` (incl. `INC-013` role-scoped read) as each lands |
| **✅ Done when** | the full lifecycle + single-claim + RBAC tests are green on real PostGIS, and `PICS-INC-*` are ✅ |

### 13.5 The remaining modules (same recipe; depth in [`25`](25-module-elucidation.md))

| Module | Purpose | Key endpoints | Entities | PICS |
|---|---|---|---|---|
| **ORG** organizations | providers who claim | `POST/GET/PATCH /organizations`, `/{id}/verify`, `…/capacity`, `…/availability` | `organizations` | `PICS-RES-*`/org rows |
| **RES** resources | provider assets on the map | `GET/POST/PATCH /resources` | `resources` | `PICS-RES-*` |
| **LOC** locations/geo | proximity, distance, map layers | `GET /locations/nearby · reverse-geocode · map/{layer}`, `POST /locations/distance` | (uses geometry) | `PICS-LOC-*` |
| **ALR** alerts | coordinator area broadcasts | `POST/GET /alerts` | `alerts` | `PICS-ALR-*` |
| **NTF** notifications | per-user messages + prefs | `GET /notifications`, `…/read`, `read-all`, `preferences` | `notifications`, `notification_preferences` | `PICS-NTF-*` |
| **RPT** reports | operational reports/exports | `GET /reports/dashboard · response-times · fulfillment · {name}/export` | (reads live data) | `PICS-RPT-*` |
| **FIL** files *(cross-cutting, early)* | uploads to MinIO (key, not blob) | `POST /files`, `GET /files/{id}` | `files` | `PICS-FIL-*` |
| **AUD** audit *(cross-cutting, from day 1)* | append-only accountability record | `GET /audit-logs` (write is a side-effect) | `audit_logs` | `PICS-AUD-*` |
| **ADM** administration | user/org management + verification | (admin-scoped `PATCH /users/{id}`, `POST /organizations/{id}/verify`) | (rides on USR/ORG) | `PICS-ADM-*` |

Plus the two features flagged earlier, slotted in as their modules land: the **FAQ chatbot stub** (Task L — a fixed
acknowledgement, no ML) as a small NTF/UI component, and **docstrings** (Task K) on every function throughout.

### 13.6 The per-module finish line

A module is **done** only when its slice of §14's checklist is fully green: code + docstrings, its **UT + API + IT**
passing (incl. RBAC + fallback), coverage in the money, its **`PICS-<MOD>-*` rows flipped ✅**, CHANGELOG updated,
merged behind green CI. Ten green modules = a finished, conformance-proven MVP.

---

## 14. Definition of Done + conformance — "is it *truly* finished?"

A team without a shared definition of "done" argues about it forever, and ships half-built things. IDRM removes the
argument: **"done" is an explicit, checkable list, not an opinion.** "It runs on my screen" is never done (§0.4).
Done exists at three nested levels:

**① A feature is done** when *each* of its acceptance criteria (F1–F11,
[`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) §5) has **at least one passing
automated test** and the behaviour matches the API contract. This is the doc-11 §7 feature Definition of Done.

**② A module is done** when its §13.1 recipe is fully green — code + docstrings, its **UT + API + IT** passing (incl.
RBAC + fallback), coverage in the money, and its **`PICS-<MOD>-*` rows flipped ✅** — merged behind green CI.

**③ The MVP is done** when **every row of the conformance checklist
[`26-conformance-pics.md`](26-conformance-pics.md) is ✅** — every module obligation *and* every stack obligation,
each with code + test evidence. The PICS is the **master ledger of doneness**, already **signed off** as the gate
(§2.4); a row moves `Planned → ✅` *only* when code + a passing test exist — never on a promise.

### 14.1 The code Definition-of-Done checklist (per change)

A change is ready to merge only when **all** of these hold (they are the §10.4 gates plus their human-judgement
companions):

- [ ] The acceptance criteria it touches each have a **passing test** (UT/API/IT as appropriate).
- [ ] **`make qa` is green** — Black/isort formatted, Ruff clean, mypy clean, full suite passing, **coverage ≥ 80 %**.
- [ ] **Docstrings** on apt functions/modules (Task K); names clear.
- [ ] **RBAC + fallback + no-PII** tests for the affected area pass (§8, §4.6, §7).
- [ ] **Audit** entries written for any new sensitive action (§8.6); **accessibility** holds if UI changed (§9).
- [ ] The relevant **`PICS` rows** are flipped ✅ with their evidence; the **CHANGELOG** is updated (C6).
- [ ] **CI is green** and the change is reviewed — branch protection (§12.3) enforces this automatically.

### 14.2 Documentation is held to the same bar

Docs and guides (this roadmap included) finalize against the **Definition of Documentation Done** —
[`../instructions/definition-of-done.md`](../instructions/definition-of-done.md) (14 criteria:
header line, phase-honest, cross-link-don't-duplicate, novice→mastery, CHANGELOG, links verified…). It's why every
section of this file is mirrored, link-checked, and logged as it lands.

> **The finish line, in one sentence:** the IDRM MVP is *done* when every conformance row in
> [`26`](26-conformance-pics.md) is ✅, every quality gate is green in CI, and every feature's acceptance criteria
> are backed by a passing test — an outcome that is **demonstrable and auditable**, not a matter of anyone's word.
> Ownership of each done-check sits with the roles in [`90-governance-and-raci.md`](90-governance-and-raci.md).

---

## 15. What's deferred to FFP — and *why* (nothing dropped)

Throughout this roadmap you've met the tag **→ FFP** many times. This closing section gathers every deferral in one
place, because understanding *why something is **not** in the MVP* is as important as understanding what is (habit
#5). **A deferral is a decision, not an oversight** — each item waits for a concrete **trigger** (real scale, a real
regulatory need, a real user demand) that justifies its cost, and each already has a **seam** designed into the MVP
so it slots in later **without a rewrite**. The authoritative reasons are the ADRs
([`21-architecture-decisions.md`](21-architecture-decisions.md)) and the FFP charter
([`../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md`](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md)).

| Area | Deferred to FFP | Why it waits | The seam already built (MVP) |
|---|---|---|---|
| **Clients** | React SPA · React Native/Expo mobile · offline-first capture · deep real-time push (websockets) · in-app messaging · full 12-language localization | the MVP web UI proves the product first; rich clients cost more to build/maintain | one **frozen API** (§4) + tokenised **design system** (§9) that any client rebuilds against |
| **Scale / infra** | selective **microservices** · **APISIX** gateway · Bun/Node edge · **Redis** + brokers (RabbitMQ/Kafka) + workers/queues · **Docker → Kubernetes** · horizontal scaling | one box is enough at MVP load; distribution adds real complexity | the **module→service seam** (§5.5 Strangler Fig) + in-process background tier (§6.8) |
| **Observability** | Loki/ELK log aggregation · **OpenTelemetry** tracing · Prometheus/Grafana metrics & alerting | central telemetry matters at multi-node scale, not one box | **structured-JSON logs** (§7) that flow in drop-in |
| **Security** | OIDC/SSO · MFA/OTP · ABAC · full role hierarchy + Auditor · per-request privacy levels · biometric FaceNet recognition · WAF · DAST | stronger/second-factor auth + biometric consent (DPDP) arrive with org rollout | RS256 tokens verifiable with no shared secret; RBAC + the static allow/deny lists (§8.4) |
| **Domain** | money/**donations + financial module** · **disaster-event entity + COP** · national rollout · advanced analytics · multi-channel intake | keeps the MVP request-centric and lean; money & national scale are big commitments | the API/data model *grow* (never rename) — the deferred tables are catalogued in [`50`](50-data-model.md) §10 |
| **Intelligence (ML)** | FAQ-chatbot NLP · **AD engine #1** (rate-limit/prioritization/black-white-listing) · **AD engine #2** (credibility) · **recommenders** (financial; incident-notification) · **churn detection** · MLOps | ML needs data, its own compute, and privacy safeguards; premature ML is risk, not value | the **rule-based** versions today (§8.4) + the **Task-M white papers** (design-now / build-FFP) |
| **Delivery / QA** | automated **CD/deploy** · heavy E2E & cross-browser · surge **performance/load** · **DAST** · **DORA** metrics · chaos · cross-service contract tests | the MVP deploys safely by hand; heavy delivery tooling suits a bigger team/scale | the **Makefile + CI** (§11–§12) that CD later extends |

> **The FAQ chatbot, precisely:** the MVP ships only the **non-intelligent stub** (Task L — a fixed *"Your input is
> noted, we'll try to get back to you shortly, if possible"*). Its evolution into a real NLP assistant, and all the
> AD/recommender/churn engines, are the **six Task-M technical white papers** — authored now as forward-looking
> designs, built in the FFP ([`../instructions.txt`](../instructions.txt) §15).

### 15.1 The roadmap ends where the code begins

You now have the **complete builder's path**, novice → mastery: the data foundation (§3), the API (§4), the code
structure (§5), the concurrency (§6), logging (§7), security (§8), the web design system (§9), testing (§10),
build/run automation (§11), CI (§12), the module-by-module plan (§13), and the definition of done (§14) — with the
deep-dives [`31`](31-concurrency-and-thread-model.md), [`32`](32-logging-and-diagnostics.md), and
[`33`](33-design-system.md) for the flagged gaps.

> **The one thing that must happen next (your directive):** execution begins **only after the data foundation (§3)
> is signed off** (§3.6) — data modeling, schema, indexes/views, seed data, and user workflows finalized, each with
> a recommendation and your confirmation. At that point the build (Task G) starts with **Users/Auth**, module by
> module, flipping [`26-conformance-pics.md`](26-conformance-pics.md) rows to ✅ until the MVP is demonstrably,
> auditably done. *Pour the foundation first — then build the house.*

---

*Related:* big-picture roadmap [`../../docs/09-roadmap.md`](../../docs/09-roadmap.md) · module elucidation [`25-module-elucidation.md`](25-module-elucidation.md) ·
conformance gate [`26-conformance-pics.md`](26-conformance-pics.md) · component map [`../idrm-mvp-guides/learn/tech-stack-101.md`](../idrm-mvp-guides/learn/tech-stack-101.md) ·
architecture [`20-architecture-system.md`](20-architecture-system.md) · working instructions [`../instructions.txt`](../instructions.txt) (§15 status).

<!-- ROADMAP STATUS: ALL SECTIONS §0–§15 DRAFTED 2026-08-17. Sub-docs 31 (concurrency) + 32 (logging) + 33 (design system) created. Optional seed-data sub-doc 34 pending the seed script. Next real step: user sign-off of the data foundation (§3.6) → then Task G coding. Archive mirror kept in sync (C3). -->
