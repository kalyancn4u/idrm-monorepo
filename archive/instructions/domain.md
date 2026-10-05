# IDRM Instructions — Domain Quick-Reference (elucidated)

> Spoke of [`../instructions.txt`](../instructions.txt). Unlike the other spokes (thin routers), this one is an
> **elucidated ground-truth card**: the facts a new session needs, PLUS the *why* behind each, so a complete
> novice can use IDRM's real vocabulary correctly and reach mastery.
> **Purpose:** keep every new doc/guide/code artifact **grounded in IDRM's actual nouns, roles, and numbers** —
> not generic disaster-app boilerplate. "Domain" = the real-world subject (disaster relief in India), as opposed
> to the technology.

## 0. Vision in one image — IDRM as a "digital nervous system"
A teaching metaphor for the platform's purpose (folded in from the v0 PRD, 2026-08-16): IDRM aims to be a
**digital nervous system for disaster response** — a **neural network** that carries *information* (who needs
what, where, right now) and a **circulatory system** that moves *resources* (people, supplies, capacity) to
where they are needed. The MVP builds the smallest working version of that loop: **sense** a need (an
`incident`), **route** it to someone who can act (a `provider`), and keep an **honest record** (`audit`).
Everything below is the concrete vocabulary that turns this image into a real system.

## 1. Modules — the ten parts of the system
`users · incidents · resources · locations · alerts · notifications · reports · files · audit · administration`

A **module** is a self-contained slice of functionality inside the single MVP application (the "modular
monolith") — ten rooms in one house: separate purposes, one building. `incidents` is the heart (help requests);
`resources` is what responders can offer; `audit` is the tamper-evident record of who-did-what. See
[`backend-services.md`](backend-services.md).

## 2. Module shape — the internal skeleton every module repeats
`router.py / schemas.py / models.py / service.py / repository.py / tests/`

A **layered pattern** so all ten modules look identical inside (predictable = easy to learn & maintain). The
order is the path a request takes: **router** (URL entry points) → **schemas** (data shapes in/out, validated by
Pydantic) → **service** (business logic, "what should happen") → **repository** (the *only* layer that talks to
the database) → **models** (the DB tables). **Rule:** *service never touches the DB directly — always via the
repository* — so business logic and storage can each change without breaking the other (Separation of Concerns).

## 3. Roles — who uses the system
`citizen · provider (NGO/hospital/volunteer) · coordinator/admin (govt) + guest`

IDRM's **RBAC** roles (Role-Based Access Control = permissions attached to a role, not to each person). A
**citizen** asks for help; a **provider** delivers it; a **coordinator/admin** (government) oversees and approves;
a **guest** has a narrow, logged-out path. Enforcement lives in [`security.md`](security.md).

## 4. Core resource — the INCIDENT
`incident = a citizen "help request" (service_type, priority, location, description)`
`service_type: medical / food / rescue / water / shelter / other`  ·  `priority: low / medium / high / critical`

The single most important object in the system. Note the **naming bridge**: users see **"help request"**, but
the API and database call it an **`incident`** — keep that mapping in one place. `service_type` and `priority`
are **fixed enum lists**; new work MUST use exactly these values, never invented ones. Contract:
[`apis.md`](apis.md).

## 5. Lifecycle — the states an incident moves through
`created → (approved if critical) → accepted → in_progress → completed → verified  (+ cancelled / rejected)`

A **lifecycle / state machine** = the fixed stages a help request can be in, and the legal moves between them. A
citizen *creates* it; if *critical* it needs government *approval*; a provider *accepts* and works it
(*in_progress*), marks it *completed*; a coordinator *verifies* it. `cancelled`/`rejected` are the exit ramps.
This **8-state flow is a LOCKED decision** — UI, API, and DB all obey it. Modeling: [`data-modeling.md`](data-modeling.md).

## 6. Personas — the human faces (v3 PRD)
`Rajesh Kumar (citizen) · Dr. Priya Sharma (provider) · Arjun Reddy (volunteer coordinator) · Lakshmi Iyer/IAS (govt coordinator)`

**Personas** are named, realistic stand-ins for each role, so requirements and guides read as human stories
("Rajesh reports flooding…") instead of abstractions — keeping the writing concrete and India-grounded.

## 7. MVP success targets (Q4 2026) — how we'll know it worked
`2 states · 50+ districts · 10k+ users · 50+ orgs · response 12h→2h · fulfillment 60%→80%`

The **measurable goals** for the first release: scale reached, plus two outcome metrics — cutting average
**response time** from 12 h to 2 h, and raising the **fulfillment rate** (share of requests actually met) from
60% to 80%. This is the "did we succeed?" scoreboard.

## Canonical docs (source of truth)
- PRD & personas: [`../idrm-mvp-docs/10-requirements-prd.md`](../idrm-mvp-docs/10-requirements-prd.md)
- Data model & lifecycle: [`../idrm-mvp-docs/50-data-model.md`](../idrm-mvp-docs/50-data-model.md)
- API contract: [`../idrm-mvp-docs/40-api-specification.md`](../idrm-mvp-docs/40-api-specification.md)
- Roles/security: [`../idrm-ffp-docs/22-architecture-security-and-iam.md`](../idrm-ffp-docs/22-architecture-security-and-iam.md)
