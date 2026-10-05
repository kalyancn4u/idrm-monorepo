# CO-STAR Prompt — Generate the IDRM FFP Architecture Document

> **STATUS: FIRST DRAFT — to be refined into a coherent, valid, comprehensive prompt later.**
> Mirrors the MVP prompt (`../../idrm-mvp-docs/prompts/IDRM MVP Architecture - CO-STAR Prompt.md`)
> but targets the **FFP (Full-Fledged Product)** — the *next phase* after the MVP. See the FFP charter
> [`instructions_idrm_ffp_docs.md`](instructions_idrm_ffp_docs.md).

## C — Context

You are documenting the **IDRM FFP (Full-Fledged Product)** — the enterprise, full-scale evolution of
the IDRM MVP. The MVP is a **pure-Python modular monolith**; the FFP introduces the technologies the
MVP deliberately deferred, **one at a time, only when a concrete requirement justifies it**.

Intended contributors span complete beginners → experienced engineers → architects, so explain from
first principles while remaining architecturally rigorous.

### Core decision
The FFP evolves the monolith into **selective microservices** — extracting individual modules into
independently deployable services **when scale, ownership, deployment independence, performance, or
reliability demands it** — never as a big-bang rewrite. The MVP's public **API contract and module
boundaries are preserved** throughout.

## S — Situation

The FFP builds directly on the MVP. Its additions:

- **Web:** a **React** single-page app (alongside/replacing the MVP's HTML + Tailwind CSS v4 + JS), consuming the same APIs.
- **Mobile:** **React Native / Expo** apps consuming the same APIs.
- **API gateway:** **APISIX** with apt plugins/extensions — reverse proxy, caching, authentication, rate limiting, TLS termination, routing, load balancing, and observability (covering all NGINX reverse-proxy capabilities). This is the FFP's API gateway.
- **Edge / runtime:** **Bun / Node / Deno** edge / BFF / websocket / SSR services running **behind APISIX** (not the gateway itself).
- **Services:** selected modules extracted into microservices behind the gateway.
- **Service runtimes (polyglot):** performance-, security-, and resilience-critical services may be implemented in **Java / Go / a JS runtime** for better scaling, fault isolation, and runtime diversity (resilience & backup strategy). **Python is retained for rapid prototyping and DS/ML tasks & modeling.** Adopted per-service, as time permits.
- **Async / messaging:** **Redis / Redis Streams**, then **RabbitMQ / Kafka**, with background **workers & queues**.
- **Platform / ops:** **Docker**, **Docker Swarm / Kubernetes**, CI/CD, distributed **observability**, HA & scaling.

PostgreSQL/PostGIS remains the system of record; per-service data ownership and replication are introduced deliberately.

## T — Task

Create a polished Markdown document titled:

# IDRM FFP — Enterprise Architecture (Selective Microservices)

Answer, at minimum:
1. What is the FFP and how does it differ from the MVP?
2. What concrete triggers justify moving from monolith to services?
3. How is a module extracted into a service without a rewrite?
4. What is the role of the **APISIX** API gateway (plugins for reverse proxy, caching, auth, rate limiting, TLS), and of the Bun/Node/Deno edge services behind it?
5. How do React web and React Native/Expo clients reuse the MVP API contract?
6. When is Redis / Redis Streams introduced, and for what?
7. When do RabbitMQ / Kafka become justified vs Redis Streams?
8. How is background/async work handled (workers, queues)?
9. How are services containerised and orchestrated (Docker → Swarm/Kubernetes)?
10. How is data ownership, consistency, and replication handled across services?
11. What does enterprise security/IAM look like (gateway auth, zero-trust, secrets)?
12. What observability, HA, and reliability practices apply at scale?
13. What is the staged migration roadmap from MVP → FFP?

## A — Architectural Requirements

- **Preserve the public API contract** so existing MVP clients keep working.
- **Incremental extraction** — one service at a time, least-coupled first (e.g. auth).
- **Every addition = one ADR** naming the concrete trigger; nothing added "because enterprise".
- Clearly distinguish **which MVP pieces are kept** vs **which are added** at FFP scale.
- Show representative service boundaries (users/auth, incidents, resources, locations, alerts, notifications, reports, administration).
- **APISIX as the API gateway:** specify the plugins/extensions that deliver reverse proxy, caching, authentication, authorization, rate limiting, TLS termination, routing, load balancing, and observability — i.e. all NGINX reverse-proxy capabilities and more — and how services sit behind it.
- **Polyglot service runtimes:** state which services warrant **Java / Go / JS** (for scale, security, resilience) versus **Python** (rapid prototyping, DS/ML), why, and how a common API contract + shared data conventions keep them interoperable. Treat runtime diversity as part of the resilience/backup strategy; adopt it per-service, as time permits.

## R — Response Requirements

Produce a single polished Markdown document: beginner-friendly, technically accurate, logically
ordered, professional. Use tables for comparison and **Mermaid diagrams** (monolith→services
evolution, gateway routing, client/API reuse, messaging flows, deployment/orchestration, migration
roadmap), each with a short explanation. Include a **GenAI Visual / Poster Prompts** section (≥5) and
end with a prominent set of FFP architectural principles.

## A — Acceptance Criteria

Before finalizing, review for: correct MVP→FFP evolution (not a rewrite); preserved API contract;
justified (trigger-based) introduction of each technology; clear service boundaries and data
ownership; enterprise security/observability; and beginner comprehensibility.

---

*To refine this draft, consolidate the microservices/Bun/React material already present in the
archived generations (`../../idrm-docs-v2/docs/`, `../../idrm-docs-v3/docs/`, `../../idrm-docs-v0..v1/docs/`)
per the [FFP charter](instructions_idrm_ffp_docs.md).*
