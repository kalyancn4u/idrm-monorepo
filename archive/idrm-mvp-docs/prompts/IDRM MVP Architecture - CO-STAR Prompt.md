# CO-STAR Prompt — Generate the IDRM MVP Architecture Document

## C — Context

You are documenting the **IDRM (Incident / Disaster Response Management) MVP**.

The objective is to produce a **clear, comprehensive, beginner-friendly yet technically rigorous Markdown architecture document** that explains how the IDRM MVP should be designed and built.

The intended contributors include:

- complete beginners
- students
- rookies/new developers
- experienced developers
- architects/technical leads

Therefore, the document must explain concepts from first principles without sacrificing architectural correctness.

### Core architectural decision

IDRM MVP is a:

> **Modular Monolith**

It is **one deployable Python/FastAPI application**, but internally divided into cohesive, loosely coupled functional modules.

The project must **not** begin as a microservices architecture.

The architecture should deliberately establish boundaries so that individual modules can later be extracted into independent microservices if actual scale, ownership, deployment, performance, or reliability requirements justify doing so.

### MVP philosophy

Use the simplest architecture that can satisfy the MVP requirements:

> **Simple to learn → simple to build → easy to test → modular by design → ready to evolve.**

Do not introduce infrastructure merely because it is considered "enterprise" or "modern".

Every technology must have a concrete justification.

---

## S — Situation

The IDRM MVP should initially provide a **web-based interface** using:

- HTML5
- Tailwind CSS v4
- JavaScript

Do **not** use React for the MVP.

React may be introduced later as an alternative web client consuming the same APIs.

React Native / Expo may similarly be introduced later for mobile applications.

### Initial architecture

```text
Browser
  │
  ├── HTML
  ├── Tailwind CSS
  └── JavaScript
          │
          ▼
     FastAPI / Python
          │
          ▼
 PostgreSQL + PostGIS
```

The FastAPI application should expose well-designed REST APIs and an OpenAPI specification.

The API must be considered a **first-class product contract**, not merely an implementation detail.

The initial web interface may use server-rendered HTML/templates and JavaScript to progressively enhance the UI.

---

## T — Task

Create a polished Markdown document titled:

# IDRM MVP — Modular Monolith Architecture

The document must explain the complete MVP architecture in a manner that a **complete novice can understand**, while remaining useful to experienced developers.

The document should answer:

1. What is IDRM?
2. What is an MVP?
3. What is a monolith?
4. What is a modular monolith?
5. Why is a modular monolith appropriate for IDRM?
6. Why not start with microservices?
7. What technologies are used in the MVP?
8. What does each technology do?
9. How does a browser request travel through IDRM?
10. How are the Python modules organized?
11. How should business logic be structured?
12. How should database access be separated from business logic?
13. How should the application remain cohesive and loosely coupled?
14. How does this architecture support future microservice extraction?
15. Why is Redis NOT required for the MVP?
16. When might Redis become useful?
17. How could Redis Streams later support queues/background processing?
18. When would RabbitMQ become justified?
19. Why is Docker deferred?
20. Why is Docker Swarm deferred?
21. Why is React deferred?
22. How can React later consume the same APIs?
23. How can React Native / Expo later consume the same APIs?
24. How should students and rookies contribute safely?
25. What should be tested?
26. What security principles must exist from the beginning?
27. How can the architecture evolve toward production and enterprise scale?

---

## A — Architectural Requirements

### 1. MVP technology stack

The document must clearly distinguish **MVP technologies** from **future technologies**.

### Required MVP stack

```text
HTML5
Tailwind CSS v4
JavaScript
Python
FastAPI
Pydantic
SQLAlchemy
PostgreSQL
PostGIS
Alembic
pytest
Git
```

### Explicitly NOT required for MVP

```text
React
React Native / Expo
Redis
RabbitMQ
Kafka
Background Workers
Docker
Docker Swarm
Kubernetes
Microservices
Advanced distributed observability
```

Explain that these technologies are not rejected; they are **deferred until a concrete requirement justifies them**.

---

## 2. PostgreSQL is the source of truth

Clearly establish:

> **PostgreSQL is the authoritative system of record for IDRM.**

Use it for durable business data such as:

- users
- organizations
- incidents
- resources
- locations
- alerts
- reports
- audit information
- workflows
- other authoritative application data

Do not make Redis, a message broker, or an application cache the source of truth.

---

## 3. PostGIS

Explain that PostGIS extends PostgreSQL with geospatial capabilities.

Relate it specifically to IDRM:

- incident locations
- affected areas
- administrative boundaries
- evacuation zones
- shelters
- routes
- resource locations
- spatial queries
- geographic analysis

---

## 4. FastAPI

Explain FastAPI as the backend/API layer.

Show:

```text
Browser
   ↓
FastAPI
   ↓
IDRM Module
   ↓
Business Logic
   ↓
Database Access
   ↓
PostgreSQL/PostGIS
```

Explain:

- routing
- request/response handling
- validation
- API versioning
- OpenAPI
- authentication/authorization integration
- error handling

---

## 5. Pydantic

Explain Pydantic as the data validation/schema layer.

Show:

```text
HTTP Request
      ↓
Pydantic Schema
      ↓
Validated Data
      ↓
Business Logic
```

Explain why validation should happen before business logic.

---

## 6. SQLAlchemy

Explain SQLAlchemy as the database-access layer between Python application logic and PostgreSQL.

Emphasize that application/business logic should not be tightly coupled to raw database operations.

---

## 7. Alembic

Explain Alembic as the mechanism for controlled database schema evolution.

Show examples conceptually:

```text
Schema v1
   ↓
Migration
   ↓
Schema v2
```

Do not assume developers manually edit production databases.

---

## 8. pytest

Testing must be part of the architecture from the beginning.

Explain:

- unit tests
- integration tests
- API tests
- database tests
- module-level tests

Show:

```text
                 Tests
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
      Unit     Integration    API
```

---

# 9. Modular monolith structure

Provide a recommended Python project structure similar to:

```text
idrm/
│
├── app/
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── exceptions.py
│   │   ├── dependencies.py
│   │   └── logging.py
│   │
│   ├── modules/
│   │   ├── users/
│   │   ├── incidents/
│   │   ├── resources/
│   │   ├── locations/
│   │   ├── alerts/
│   │   ├── notifications/
│   │   ├── reports/
│   │   └── administration/
│   │
│   ├── infrastructure/
│   │   └── database/
│   │
│   └── main.py
│
├── tests/
├── alembic/
├── docs/
├── pyproject.toml
└── README.md
```

Explain every major directory.

---

# 10. Internal module structure

Show an example such as:

```text
incidents/
├── router.py
├── schemas.py
├── models.py
├── service.py
├── repository.py
└── tests/
```

Explain:

### router.py

HTTP/API concerns.

### schemas.py

Pydantic request/response models.

### models.py

Persistence/database models.

### service.py

Business/application logic.

### repository.py

Database persistence operations.

### tests/

Tests for the module.

---

# 11. Functional and cohesive Python

The architecture should favor:

- small functions
- pure functions where practical
- explicit inputs and outputs
- minimal global state
- separation of I/O from business logic
- high cohesion
- low coupling
- deterministic business rules where possible

Illustrate:

```text
HTTP / Database / External I/O
            │
            ▼
     Application Layer
            │
            ▼
      Business Logic
       / Pure Logic
            │
            ▼
       Result / State
```

Explain why this helps:

- testing
- maintainability
- performance analysis
- debugging
- reuse
- parallel development
- eventual microservice extraction

---

# 12. API-first architecture

The API should be treated as a stable contract.

Show:

```text
                    IDRM API
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Web UI       Future React   Future Mobile
     HTML/Tailwind CSS/JS       Web        React Native
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                     FastAPI
```

Explain that the initial web interface and future clients should consume the same API contracts.

Include representative API examples:

```text
GET    /api/v1/incidents
GET    /api/v1/incidents/{id}
POST   /api/v1/incidents
PUT    /api/v1/incidents/{id}
DELETE /api/v1/incidents/{id}
```

Do not over-specify APIs that are not yet finalized.

---

# 13. Redis — explicitly explain why it is NOT in the MVP

This is important.

State clearly:

> **Redis is not required for the initial IDRM MVP.**

Explain possible future uses:

- caching
- rate limiting
- temporary state
- distributed coordination
- background-job queues
- Redis Streams

But emphasize:

> **Do not add Redis unless a measurable or concrete requirement justifies it.**

Explain that PostgreSQL should first be optimized through:

- proper schema design
- indexes
- query optimization
- connection pooling
- appropriate transactions
- measurement/profiling

Do not use Redis to hide poor database design.

---

# 14. Redis Streams — future phase

Explain that if asynchronous work becomes necessary, Redis Streams can potentially provide:

- durable stream entries
- consumer groups
- acknowledgements
- pending message tracking
- message recovery/claiming
- multiple independent consumer groups

Show:

```text
FastAPI
   ↓
Redis Stream
   ↓
Consumer Group
   ↓
Workers
```

Explain that Redis Streams can cover many IDRM queue/event requirements without immediately introducing RabbitMQ.

---

# 15. RabbitMQ — future and conditional

Explain:

> Redis Streams and RabbitMQ are not identical technologies.

RabbitMQ becomes attractive when IDRM needs more sophisticated broker-centric messaging such as:

- complex routing
- exchanges
- bindings
- multiple queue patterns
- sophisticated delivery semantics
- dead-lettering
- broker-centric messaging topology

State:

> **RabbitMQ should be introduced only when IDRM's messaging requirements justify it.**

---

# 16. Language interoperability

Explain that Redis is language-independent.

A future IDRM ecosystem may contain:

```text
Python / FastAPI
Java / Spring Boot
JavaScript / TypeScript
```

and all can communicate with the same Redis infrastructure.

Show:

```text
                 Redis
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
    Python       Java       JS / TS
   FastAPI     Service      Service
```

Explain that common conventions are necessary for:

- key naming
- serialization
- TTLs
- ownership
- schemas
- namespaces
- error handling

Warn against turning Redis into an uncontrolled shared-data store.

---

# 17. Docker — deferred

Explain why Docker is not an MVP prerequisite.

Initial development may simply use:

```text
Developer machine
├── Python
├── FastAPI
├── PostgreSQL
└── Browser
```

Docker can later provide:

- reproducible environments
- packaging
- deployment consistency
- CI/CD integration

---

# 18. Docker Swarm — deferred

Explain that Swarm is an orchestration/deployment concern, not an application-development prerequisite.

It may later provide:

- service replication
- scheduling
- service discovery
- rolling updates
- deployment management
- failure recovery

Do not introduce it into the MVP.

---

# 19. React — deferred

Explain that React is intentionally postponed.

Initial UI:

```text
HTML + Tailwind CSS + JavaScript
```

Future:

```text
React
   ↓
Same FastAPI APIs
```

The backend should not be redesigned merely because React is introduced.

---

# 20. React Native / Expo — deferred

Explain that mobile development can later consume the same API.

```text
React Web ────────┐
HTML/JS Web ──────┤
React Native ─────┤
                  ▼
               FastAPI
```

---

# 21. Security

Explain that simplicity must never mean weak security.

Include:

- HTTPS
- secure authentication
- authorization
- RBAC
- input validation
- secure password handling
- token/session security
- audit logging
- database access control
- least privilege
- secure error handling
- security headers
- secrets management
- backups and recovery planning

Avoid over-engineering security technologies that are not required for the MVP.

---

# 22. Reliability

Explain basic reliability mechanisms appropriate to the MVP:

- database transactions
- constraints
- validation
- error handling
- logging
- testing
- health checks
- backups
- recovery procedures

Later discuss:

- replication
- load balancing
- container orchestration
- distributed observability
- fault tolerance

---

# 23. Rookie/student contribution model

Make this an explicit section.

Explain that the architecture is intentionally designed so that contributors can work in bounded areas.

Examples:

### Web beginner

```text
HTML
 ↓
Tailwind CSS
 ↓
JavaScript
 ↓
API consumption
```

### Python beginner

```text
Python
 ↓
Functions
 ↓
Modules
 ↓
FastAPI
```

### Backend contributor

```text
FastAPI
 ↓
Pydantic
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

### GIS contributor

```text
PostgreSQL
 ↓
PostGIS
 ↓
GeoJSON
 ↓
Maps
```

### Advanced contributor

```text
Redis
 ↓
Workers
 ↓
Docker
 ↓
Swarm
 ↓
Observability
 ↓
Microservices
```

Emphasize:

> A contributor should not need to understand the entire system before making a useful contribution.

---

# 24. Architecture evolution

Provide a clear staged roadmap.

## Phase 1 — MVP

```text
HTML + Tailwind CSS + JS
FastAPI + Python
Pydantic
SQLAlchemy
PostgreSQL + PostGIS
Alembic
pytest
Git
```

## Phase 2 — Async / Performance

Only when required:

```text
Redis
Redis Streams
Background Workers
Queues
```

## Phase 3 — Production

```text
Docker
CI/CD
Deployment
Backups
Monitoring
```

## Phase 4 — HA / Scale

```text
Docker Swarm
Replication
Load balancing
Advanced observability
```

## Phase 5 — Selective distribution

Only when justified:

```text
Multiple services
RabbitMQ / Kafka
Selective microservices
React
React Native / Expo
```

---

# 25. Mermaid diagrams

Use Mermaid diagrams extensively but appropriately.

Include at minimum:

1. High-level architecture
2. Modular monolith structure
3. Browser → FastAPI → database request flow
4. Internal module request flow
5. API-first architecture
6. PostgreSQL/PostGIS relationship
7. Future Redis Streams worker flow
8. Future RabbitMQ architecture
9. Technology evolution roadmap
10. Student/contributor learning path
11. Future microservice extraction
12. Overall IDRM architecture evolution

Every Mermaid diagram must have a short explanation immediately below it.

Do not create diagrams merely for decoration.

---

# 26. GenAI image/poster prompts

At the end of the document, include a section titled:

# GenAI Visual / Poster Prompts

Create at least **5 carefully designed poster/image prompts**.

Each prompt must specify:

- title
- purpose
- intended audience
- visual composition
- major elements
- information hierarchy
- diagram flow
- typography guidance
- style
- color guidance
- accessibility considerations
- aspect ratio recommendation
- negative constraints

Recommended poster topics:

1. **IDRM MVP at a Glance**
2. **What Is a Modular Monolith?**
3. **IDRM Request Journey**
4. **IDRM — Now → Later Evolution**
5. **IDRM Technology Learning Path**

Prompts should be suitable for image-generation systems such as ChatGPT image generation.

Do not ask the image generator to render large amounts of tiny text. Prefer diagrams, labels, icons and concise captions.

---

## R — Response Requirements

Produce a **single polished Markdown document**.

The document must be:

- beginner-friendly
- technically accurate
- logically ordered
- concise but sufficiently comprehensive
- professional
- educational
- suitable for onboarding
- suitable as an architectural reference
- suitable for future project documentation

### Recommended document order

```text
1. Title
2. Executive Summary
3. What Is IDRM?
4. What Is an MVP?
5. Why Modular Monolith?
6. Architecture at a Glance
7. Technology Stack
8. Web Interface
9. FastAPI Backend
10. API-First Architecture
11. Modular Python Architecture
12. Module Structure
13. Functional / Cohesive Python
14. PostgreSQL
15. PostGIS
16. Pydantic
17. SQLAlchemy
18. Alembic
19. Testing
20. Security
21. Reliability
22. Why Redis Is Not in MVP
23. Future Redis / Redis Streams
24. Future Workers and Queues
25. RabbitMQ — When and Why
26. Docker — Later
27. Docker Swarm — Later
28. React — Later
29. React Native / Expo — Later
30. Student/Rookie Contribution Model
31. Future Microservice Extraction
32. Architecture Evolution Roadmap
33. MVP Checklist
34. GenAI Visual / Poster Prompts
35. Final Architectural Principles
```

Use tables where comparison is clearer than prose.

Use callout-style Markdown where useful:

> **Key principle:** Do not add infrastructure until a real requirement justifies it.

Use short examples to explain difficult concepts.

---

## A — Acceptance Criteria

Before finalizing, internally review the document for:

### Architectural correctness

- Does it clearly define a modular monolith?
- Is it genuinely a monolith rather than disguised microservices?
- Are module boundaries explicit?
- Is PostgreSQL the system of record?
- Is PostGIS appropriately positioned?
- Is business logic separated from infrastructure?
- Is the architecture suitable for future extraction?

### MVP simplicity

- Is React excluded from MVP?
- Is Docker excluded from MVP?
- Is Docker Swarm excluded from MVP?
- Is Redis excluded from MVP?
- Are RabbitMQ and Kafka excluded from MVP?
- Are workers and queues deferred?
- Is unnecessary infrastructure avoided?

### API-first design

- Is FastAPI clearly the backend/API layer?
- Is OpenAPI treated as a contract?
- Can future React and React Native clients consume the same API?
- Is the initial HTML/Tailwind CSS/JS interface compatible with this architecture?

### Code quality

- Is Python organized into cohesive modules?
- Are functions small and testable?
- Is business logic separated from I/O?
- Is coupling minimized?
- Are module boundaries suitable for later extraction?

### Educational suitability

- Can a complete novice understand the architecture?
- Can students identify where to contribute?
- Are concepts explained before advanced terminology is used?
- Does the document avoid unnecessary infrastructure jargon?

### Future scalability

- Is there a credible path to:
  - Redis
  - Redis Streams
  - Workers
  - Queues
  - Docker
  - Docker Swarm
  - Observability
  - React
  - React Native/Expo
  - selective microservices
  - RabbitMQ/Kafka when justified?

### Visual quality

- Are Mermaid diagrams useful and accurate?
- Does every diagram have an explanation?
- Are the GenAI poster prompts sufficiently detailed?
- Are the diagrams and visual prompts consistent with the architecture?

---

## Final Architectural Principle

End the document with this statement, prominently formatted:

> # **Build Simple. Design Modularly. Test Thoroughly. Evolve Deliberately.**
>
> **IDRM should begin as a simple, secure, testable FastAPI/Python modular monolith with an HTML/Tailwind CSS/JavaScript web interface and PostgreSQL/PostGIS as its source of truth.**
>
> **Redis, workers, queues, Docker, Swarm, React, mobile clients, message brokers and microservices should be introduced only when real requirements justify them.**
>
> **The goal is not maximum technology. The goal is maximum clarity with a credible path to enterprise scale.**