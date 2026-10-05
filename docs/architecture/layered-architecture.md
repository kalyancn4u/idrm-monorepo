# Layered Architecture - The Definitive Blueprint

## What this document is

The single authoritative description of how IDRM is layered, from the browser
to the database. Read it once. Return to it whenever a design question comes
up. It settles the debate.

## The one-diagram overview

    TIER 1 - PRESENTATION  (apps/)
      Pure Web  |  React Web  |  Expo Mobile
           |
           v
    TIER 2 - EDGE  (gateway/ plus optional BFFs)
      API Gateway: routing, auth, rate limiting
      BFF: optional aggregation per interface
           |
           v
    TIER 3 - DOMAIN  (services/)
      Monolith (MVP) becomes Microservices (FFP)
      Inside each: Controller, Service, Domain, Repository
           |
           v
    TIER 4 - DATA
      PostgreSQL  |  Redis  |  MinIO  |  Search

Four network tiers. Four internal layers per service.

## Why layers at all

Layering is not decoration. Each layer solves a problem the layer below
cannot solve as well:

| Layer | Solves |
|---|---|
| Presentation | How a human interacts with the system |
| Edge | Cross-cutting concerns: auth, rate limits, routing, TLS |
| Domain | Business rules, data ownership, transactional integrity |
| Data | Persistence, caching, search, object storage |

Adding a layer that solves no problem is over-engineering. Skipping a layer
that solves a real problem is under-engineering.

## Tier 1 - Presentation

Every user-facing application lives in apps/. Apps:

- Render UI.
- Call the backend over HTTP.
- Never touch the database.
- Never contain business logic beyond UI concerns.

Current: pure web (MVP active), React web (FFP placeholder), Expo mobile
(FFP placeholder).

## Tier 2 - Edge

Two parts.

### API Gateway

The single entry point. Validates JWTs. Enforces rate limits. Terminates TLS.
Routes requests. Adds correlation IDs. Breaks circuits.

In the MVP the gateway is config-only. The FastAPI monolith serves /api/v1/*
directly. The config at gateway/config/routes.yaml documents the future
routing. In the FFP, APISIX activates it.

### BFF (Backend for Frontend) - optional

A BFF aggregates calls from several backend services into one response
tailored to one interface. It is added only when needed:

- A screen requires data from three or more services.
- Mobile needs materially smaller payloads than web.
- Frontend velocity is blocked by backend composite endpoints.

In the MVP, there is no BFF. The monolith serves both frontends directly.

## Tier 3 - Domain

Every backend application lives in services/. In the MVP there is one: the
monolith. In the FFP there will be many.

### The four internal layers

Every service, in every language, has the same four internal layers.

Layer 1 - Controller / API
    HTTP handlers, validation, response shaping.
    Never contains business logic.

Layer 2 - Service / Application
    Business rules. Orchestrates use cases.
    Depends on ports (interfaces).
    No HTTP, no SQL.

Layer 3 - Domain Model
    Entities, value objects, business rules.
    Zero framework dependencies.

Layer 4 - Repository / Infrastructure
    Database access, external clients.
    Implements the ports defined in Layer 2.

### The dependency rule

Dependencies point inward. Controllers depend on services. Services depend on
domain models and ports. Repositories implement ports. The domain model
depends on nothing.

This is what makes the code testable and replaceable.

## Tier 4 - Data

Managed stores. Only Tier 3 touches them.

| Store | Purpose | MVP | FFP |
|---|---|---|---|
| PostgreSQL | System of record | yes | yes |
| Redis | Cache, sessions | optional | yes |
| MinIO / S3 | Object storage | yes | yes |
| Search index | Full-text search | no | yes |

## The request lifecycle, end to end

    1.  User clicks a button in the React web app.
    2.  The app calls a typed function from @idrm/api-client.
    3.  HTTP request goes to /api/v1/incidents with a JWT.
    4.  API Gateway validates the JWT and routes to the incidents service.
    5.  Controller validates the JSON body against the schema.
    6.  Service applies business rules and calls the repository.
    7.  Repository writes to PostgreSQL.
    8.  Service returns the saved entity.
    9.  Controller serialises it to the response schema.
    10. Gateway forwards the response.
    11. The typed client returns a fully typed object.
    12. React updates the UI.

Every layer does one job. No layer does another's job.

## MVP versus FFP

| Aspect | MVP | FFP |
|---|---|---|
| Presentation | pure web only | pure web + React web + mobile |
| Gateway | config-only | active APISIX |
| BFF | none | optional per interface |
| Domain | one monolith | many microservices |
| Languages | Python | Python + Go + Java + TS |
| Data | Postgres + MinIO | plus Redis and search |
| Deploy | systemd on one host | Kubernetes |

The tree does not change between phases. Only the contents.

## The principles that hold it together

| Principle | Where applied | Effect |
|---|---|---|
| High cohesion | Each module does one thing | Easy to understand |
| Low coupling | Depend on interfaces, not implementations | Easy to replace |
| Dependency inversion | Services depend on ports | Testable, extractable |
| Single responsibility | Each layer, class, function | One reason to change |
| Repository pattern | All data access through a repository | Persistence is replaceable |
| Contract-first | OpenAPI is the source of truth | Frontends stay in sync |

## How the layers grow into the FFP

The monolith becomes microservices one module at a time (Strangler Fig). The
four internal layers do not change. Only the deployment changes: what was a
function call becomes an HTTP call, and the port implementation is swapped
from a local repository to an HTTP client.

## Summary

Four network tiers. Four internal layers. One dependency rule. The tree never
changes between MVP and FFP. Only the contents grow. Everything else in this
folder is a specific view of this blueprint.
