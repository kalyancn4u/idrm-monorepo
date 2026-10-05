# Layered Architecture - The Reasoning

## What this document is

The reasoning behind the layered architecture described in
layered-architecture.md. That document shows WHAT the layers are. This
document explains WHY they are that way, using six dimensions of analysis.
Read this after the blueprint.

## The core distinction: logical vs physical layers

A "layer" in architecture does not always mean a separate process on a
separate machine. Two kinds exist:

- Logical layers: code organisation inside one process. The monolith has
  Controllers, Services, Repositories - three logical layers, one process.
- Physical layers: separate deployable units. The API gateway and the
  monolith are two physical layers, two processes.

Confusing them leads to over-engineering in the MVP and under-engineering in
the FFP. The IDRM blueprint uses logical layering inside each service and
adds physical layering between services only when a real pain point demands
it.

## The four network tiers

| Tier | Purpose | MVP | FFP |
|---|---|---|---|
| Presentation (apps/) | Render UI, handle interaction | Pure web | Plus React web, mobile |
| Edge (gateway/) | Routing, auth, rate limiting, TLS | Config only | Active APISIX + BFFs |
| Domain (services/) | Business rules, data ownership | One monolith | Many microservices |
| Data | Persistence, cache, storage | Postgres + MinIO | Plus Redis, search |

## Why each tier earns its place

Layering is only justified when each layer solves a problem the layer below
cannot solve as well.

| Layer | Solves | Without it |
|---|---|---|
| Presentation | Human interaction | No user experience |
| Edge | Cross-cutting concerns (auth, rate limits, TLS) | Every client implements auth independently |
| BFF | Tailored responses per interface | One generic API serves all clients poorly |
| Domain | Business rules, data integrity | Logic scattered across clients |
| Data | Persistence, caching | No state; every request recomputes |

The API Gateway pattern exists because direct client-to-microservice
communication "tightly couples front-end clients to core back-end services"
and duplicates cross-cutting concerns across every microservice. The BFF
pattern exists because a single shared backend becomes a bottleneck of
competing demands when multiple interfaces diverge.

## The six dimensions of analysis

### 1. Efficacy - does it solve the right problems?

Each layer must have a distinct responsibility no other layer fulfils.
Adding a BFF when there is only one interface is premature. Adding a gateway
when there is one backend and no external consumers is over-engineering.

Verdict: efficacious when each layer earns its place.

### 2. Effectiveness - does it produce the intended outcome?

Effectiveness comes from dependency direction enforcement. A controller
cannot bypass the service to touch the database. A UI component cannot
import a database driver. This is machine-checkable with importlinter
(Python) or ESLint boundary rules (TypeScript).

Verdict: effective because it turns architectural intent into checkable
constraints.

### 3. Efficiency - does it minimise effort and waste?

| Layer count | Effort to add a feature | Risk |
|---|---|---|
| 1 (no layers) | Lowest | Untestable, unscalable |
| 3 (presentation, domain, data) | Low | Optimal for most apps |
| 5+ (plus gateway, BFF) | High | Each hop adds latency and ops surface |
| 10+ (full microservices) | Very high | Justified only at large scale |

The BFF pattern documentation warns: "Maintaining and deploying more
services means increased operational overhead. Each service has its own
lifecycle, deployment and maintenance requirements, and security
requirements. Latency may increase because the client is not contacting
your service directly."

Verdict: efficiency is maximised by starting with the fewest layers that
solve the problem. For the IDRM MVP, three layers (presentation, monolith,
data) are sufficient.

### 4. Minimal effort - the MVP principle

The MVP has three network tiers and three internal layers:

    Pure Web (apps/web/)
            |
            v
    FastAPI Monolith (services/monolith/)
      Controllers (HTTP handlers)
      Services (business logic)
      Repositories (data access)
            |
            v
    PostgreSQL + MinIO

No API gateway. No BFF. No microservices. The monolith serves the pure web
interface directly. The internal layering is logical - one process, no
network hops - but it delivers testability and maintainability.

### 5. Long-term scalability - pain points trigger layers

As the system grows, specific pain points trigger specific new layers:

| Pain point | Layer that solves it | When to add |
|---|---|---|
| Multiple frontends need different data shapes | BFF | When mobile diverges from web |
| Multiple backend services need one entry | API gateway | When the monolith becomes 2+ services |
| Read traffic overwhelms the database | Cache (Redis) | When read latency exceeds thresholds |
| One domain's load affects another | Microservice extraction | When scaling profiles differ |
| Auth duplicated across services | Gateway + shared middleware | When 3+ services implement auth |

The BFF pattern documentation notes: "The frontend team independently
manages its own BFF service, controlling language choice, release cadence,
workload priorities, and feature integration. This autonomy allows them to
operate efficiently without depending on a centralized backend development
team."

Verdict: scalability is achieved not by pre-building all layers, but by
having a structure that absorbs new layers without reorganisation.

### 6. Reliability and robustness

| Concern | How layering helps |
|---|---|
| Fault isolation | A failing BFF does not crash the domain service |
| Graceful degradation | Redis down: fall back to database |
| Independent deployment | A mobile BFF bug cannot break the web |
| Testability | Each layer tests in isolation with mocks |
| Observability | Each layer emits its own metrics and traces |
| Circuit breaking | Gateway detects a failing backend and fails fast |

The CQRS pattern extends this: reads go through a cache optimised for
queries, writes go to the system of record. AWS guidance confirms: "When a
read request arrives, check ElastiCache using a unique key. Cache Hit:
Return the cached JSON payload directly. Cache Miss: Query the RDS read
replica, write the result into ElastiCache with a TTL, and return the data."

## Where the "Bun server" fits

The "Bun server" proposed in early discussions is best understood as a BFF
implementation. Bun's strengths - native TypeScript, fast startup, small
Docker images (~90MB), ~100k req/s throughput - make it an excellent BFF
runtime. A Bun + Hono BFF would aggregate multiple backend calls into one
frontend-friendly response, transform payloads, and cache aggressively.

But a BFF is not needed in the MVP. It becomes valuable when:

1. Mobile and web need materially different data shapes.
2. A screen requires 3+ backend service calls (aggregation pays off).
3. Frontend teams are blocked waiting for backend composite endpoints.

Until then, the monolith's controllers serve the frontend directly.

## Reasoning summary across dimensions

| Dimension | MVP | FFP | Why |
|---|---|---|---|
| Efficacy | 3 tiers solve the problem | 5 tiers solve independent scaling | Each layer earns its place |
| Effectiveness | Internal layering enforces testability | Network layering enforces fault isolation | Constraints become checkable |
| Efficiency | Lowest latency, fewest deploys | Higher latency, independent scaling | Cost justified by scaling benefit |
| Minimal effort | One service, one pipeline | N services, N pipelines | Effort shifts from coordination to independent execution |
| Scalability | Vertical (bigger machine) | Horizontal (more replicas) | Layer isolation enables selective scaling |
| Reliability | Single point of failure | Fault isolation, cache fallbacks | Failures contained within a layer |
| Robustness | Manual recovery | Automated failover | Layered health checks |

## Mapping to the monorepo structure

| Layer | Folder | MVP populated? | FFP populated? |
|---|---|---|---|
| Presentation | apps/ | web/ only | web/, web-react/, mobile/ |
| Edge | gateway/ | Config only | Active APISIX |
| BFF | services/bff-*/ | Empty | bff-web/, bff-mobile/ |
| Domain | services/monolith/ | Yes | services/*-service/ |
| Shared infra | services/*-service/ | Empty | notifications/, audit/, files/ |
| Data | Managed externally | PostgreSQL + MinIO | Plus Redis, search |
| Shared libs | packages/, shared/libs/ | api-client/, types/ | All populated |

The structure absorbs the layers without reorganisation. Adding a BFF in the
FFP means creating services/bff-web/ - the folder tree already has a place
for it.

## Trade-offs and anti-patterns

| Anti-pattern | Why it fails | Correct approach |
|---|---|---|
| Gateway as monolithic aggregator | Violates microservice autonomy | Gateway routes; BFFs aggregate |
| BFF for one interface | Adds a hop for no benefit | Start without BFF |
| Sharing a BFF across interfaces | Different requirements complicate growth | One BFF per interface family |
| Microservices in MVP | Distributed complexity without scale | Monolith with internal layers |
| Cache without invalidation | Stale data causes correctness bugs | Cache-aside with TTL |
| Layering for its own sake | Every layer adds latency and ops cost | Each layer must solve a named pain |

## The one-paragraph summary

Layering is ideal when each layer solves a problem the layer below cannot.
For the IDRM MVP, three network tiers (presentation, monolith, data) with
three internal layers (controllers, services, repositories) deliver maximum
efficacy at minimum effort. The API gateway and BFF layers earn their place
in the FFP when multiple frontends need tailored responses and multiple
backend services need a single entry point. The Bun server is best
understood as a BFF implementation - powerful when needed, premature when
not. The idrm-monorepo structure already provides homes for every layer;
they remain empty until a real pain point demands them.

## Next steps

- The blueprint itself: ./layered-architecture.md
- The monorepo structure: ./monorepo-structure.md
- The tooling decisions: ./tooling-decisions.md
