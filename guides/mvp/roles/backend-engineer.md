# Role-Mastery — Backend Engineer

> *Type: Guide (role-mastery / learning journey) · Audience: backend dev, from novice → mastery · Status: MVP — current · Blueprint §25.4*
> *You build the engine: the FastAPI modules, the API, the data layer, the auth. This journey takes you from
> "I know some Python" to shipping a module end-to-end with tests and observability.*

---

## 1. Your mission

Implement IDRM's server-side behaviour cleanly and safely: each domain module as a well-layered slice
(`router/schemas/models/service/repository/tests`), on the frozen `/api/v1` contract, over PostgreSQL+PostGIS —
correct, secure, tested, and observable.

## 2. Your mastery map

```mermaid
flowchart LR
    A["Programming"] --> B["HTTP / REST"]
    B --> C["API Design"]
    C --> D["IDRM Domain"]
    D --> E["Domain Model"]
    E --> F["Database"]
    F --> G["Transactions"]
    G --> H["AuthN / AuthZ"]
    H --> I["Events"]
    I --> J["Testing"]
    J --> K["Observability"]
    K --> L["Production Debugging"]
    L --> M["Mastery"]
```

## 3. Your learning path (rung → what to read)

1. **Programming + tooling** → [Git/GitHub 101](../learn/git-github-101.md) ·
   the [Developer/Contributor guide](../30-contribute-developer-guide.md) (zero → running app → PR)
2. **HTTP/REST + API design** → [REST API 101](../learn/rest-api-101.md) ·
   [`40-api-specification.md`](../../../docs/mvp/40-api-specification.md) (the frozen contract you implement)
3. **IDRM domain + domain model** → [Incident Management 101](../learn/incident-management-101.md) ·
   the [domain card](../../../archive/instructions/domain.md) (modules, the 8-state lifecycle)
4. **Database + transactions** → [Database 101](../learn/database-101.md) ·
   [PostgreSQL/PostGIS 101](../learn/postgresql-postgis-101.md) ·
   [`50-data-model.md`](../../../docs/mvp/50-data-model.md) · [data-modeling spoke](../../../archive/instructions/data-modeling.md)
5. **AuthN/AuthZ** → [IAM 101](../learn/iam-101.md) · [RBAC/ABAC 101](../learn/rbac-abac-101.md) ·
   [Secure Coding 101](../learn/secure-coding-101.md) · [`22-architecture-security-and-iam.md`](../../../docs/mvp/22-architecture-security-and-iam.md)
6. **Events** (FFP) → [Event-Driven Architecture 101](../learn/event-driven-architecture-101.md) — MVP is synchronous.
7. **Testing + observability + debugging** → [Testing 101](../learn/testing-101.md) ·
   [API Testing 101](../learn/api-testing-101.md) · [Observability 101](../learn/observability-101.md) ·
   [Linux 101](../learn/linux-101.md) (systemd/journalctl for prod debugging)

## 4. The rules you never break

- **Layering:** the `service` layer talks to the DB **only via the repository** — never raw SQL in services.
- **Contract:** implement `/api/v1` exactly (snake_case, UUID, ISO-8601, `{data,pagination}`, error `code`).
- **Lifecycle:** enforce the 8-state machine so illegal transitions are **impossible**, and audit every change.
- **Security:** validate input with Pydantic; check RBAC on the server, every time.
- **Schema changes:** always an **Alembic** migration, never by hand.

## 5. MVP vs FFP for you

- **MVP:** the pure-Python FastAPI monolith, synchronous, native systemd. Master this first.
- **FFP:** service extraction (Strangler Fig), events/brokers, polyglot runtimes — same contract throughout.

## 6. Mastery test

You can take a feature from requirement to production: **design the API, model the data, implement the module
end-to-end, secure it, test it (unit + API), make it observable, and debug it in production** — without breaking
the contract or the layering.

---
*Related:* [Solution Architect](solution-architect.md) · [GIS Engineer](gis-engineer.md) ·
[QA / SDET](qa-sdet.md) · [DevOps / SRE](devops-sre.md)
