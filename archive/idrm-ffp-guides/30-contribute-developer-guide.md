# IDRM FFP — Developer / Contributor Guide (Across Services)

> *Type: Guide (tutorial / how-to) · Audience: novices → experienced devs · Status: FFP — next-phase (planned)*
> *Extends the MVP contributor guide [`../idrm-mvp-guides/30-contribute-developer-guide.md`](../idrm-mvp-guides/30-contribute-developer-guide.md). How to contribute once IDRM spans **multiple services + rich clients**. Consolidates `../idrm-docs-v2/docs/30-contribute-guide.md`, `../idrm-docs-v3/docs/30-contribute-guide.md`, `90-project-structure.md`.*

> **Start here only after you know the MVP guide.** The FFP is the same product, extended — the golden rule
> (`router → service → repository`, module boundaries, the `/api/v1` contract) still holds; now some modules
> are their own services.

---

## 1. What's different from the MVP
- The app is **many services behind the APISIX gateway** (not one process). Most modules may still live in
  the monolith; some are extracted.
- Clients include a **React SPA** and **React Native** app (plus the MVP HTML UI).
- There's an **event bus** (Redis Streams/Kafka) and **workers**.
- Everything runs in **containers** (Docker) locally; orchestrated (Swarm/K8s) in shared envs.

## 2. Local setup (multi-service)
Use **Docker Compose** to bring up the stack (gateway + services + PostgreSQL/PostGIS + Redis + MinIO +
broker). Each service keeps the MVP shape (`router/service/repository/tests`) in its own repo/module. Run
only the service you're changing + its dependencies; the gateway routes the rest.

## 3. The rules that don't change
- **Public `/api/v1` contract is sacred** — never rename an endpoint; add, don't break (MVP ADR-003).
- **Own your data** — a service reads its own DB only; cross-service via **events**, not shared tables.
- Same conventions: snake_case, UUID, ISO-8601, enum-only-grows, RS256 auth, audit significant actions.
- Every new tech/service enters via an **ADR with a trigger** ([`../idrm-ffp-docs/21-architecture-decisions.md`](../idrm-ffp-docs/21-architecture-decisions.md)).

## 4. Testing your change
Unit + API + integration for your service, **plus contract tests** (so you don't break consumers) and event
compatibility. Run a **scenario/drill** for cross-service flows. Gates: format/lint/types/tests/≥80% +
SAST/SCA + contract tests (see [`../idrm-ffp-docs/70-quality-test-strategy.md`](../idrm-ffp-docs/70-quality-test-strategy.md)).

## 5. Contributing across services (PRs)
Prefer **small, single-service** PRs. If a change spans services, coordinate via the **event/contract** first
(add the new event/field), deploy the producer, then consumers — never a breaking big-bang. Branch/commit/PR
conventions match the MVP guide.

## 6. Where to go next
Architecture [`../idrm-ffp-docs/20-architecture-system.md`](../idrm-ffp-docs/20-architecture-system.md) ·
API/contracts [`../idrm-ffp-docs/40-api-specification.md`](../idrm-ffp-docs/40-api-specification.md) ·
messaging [`../idrm-ffp-docs/81-ops-messaging-and-async.md`](../idrm-ffp-docs/81-ops-messaging-and-async.md) ·
platform [`../idrm-ffp-docs/80-ops-platform-and-deployment.md`](../idrm-ffp-docs/80-ops-platform-and-deployment.md).

Welcome to the FFP — same mission, bigger system. Keep the contract, own your data, prove it with tests. 🚀
