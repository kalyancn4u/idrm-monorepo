# IDRM FFP — API & Contracts (Gateway + Inter-Service)

> *Type: Document (specification) · Audience: developers, integrators · Status: FFP — next-phase (planned)*
> *Extends the MVP API [`../idrm-mvp-docs/40-api-specification.md`](../idrm-mvp-docs/40-api-specification.md) (+ its OpenAPI). **The public API contract does not change** — the FFP routes it through a gateway, adds inter-service contracts, and *adds* endpoints at stable paths. Consolidates `v3/40-api-specification.md`, `82-api-gateway`, `v2/41-api-json-formats.md`.*

> **Invariant (MVP ADR-003):** every `/api/v1/...` URI the MVP defined keeps the **same path, method, and
> semantics** in the FFP. The FFP only **adds** endpoints and moves the *implementation* behind services —
> never renames.

---

## 1. Three contract layers
1. **Public API** — the MVP `/api/v1/...` contract, unchanged. All clients (HTML, React, React Native,
   integrators) use it.
2. **Gateway routing (APISIX)** — maps public paths to services (or the monolith for not-yet-extracted
   modules); adds TLS, auth, rate-limit, cache, LB, observability. Transparent to clients.
3. **Inter-service contracts** — how services talk to each other: **synchronous** (internal REST/gRPC,
   never bypassing ownership) and **asynchronous** (domain **events** on Redis Streams/Kafka).

```mermaid
flowchart LR
    C["Clients (HTML·React·RN·integrators)"] -->|/api/v1 (unchanged)| GW["APISIX gateway"]
    GW --> S1["auth svc"]
    GW --> S2["incidents svc"]
    GW --> MONO["monolith (unextracted modules)"]
    S2 -. events .-> BUS[("Redis Streams / Kafka")]
    BUS --> S3["notifications svc"]
    BUS --> S4["analytics svc"]
```

## 2. Added public endpoints (at stable paths)
The FFP realises the resources the MVP catalogued as "→ FFP", at the **paths the MVP reserved**:
`/api/v1/disasters`, `/api/v1/financial/*`, and a **realtime** channel (websocket) for live COP/push. Same
conventions (snake_case, UUID, ISO-8601, enum-only-grows, `{data,pagination}`, error envelope). New enum
values (e.g. incident `disputed`) are **added**, never renaming existing ones.

## 3. Async / event contracts
Domain events are **versioned**, carry **correlation/request IDs** and are **idempotent**. Examples:
`incident.created`, `incident.accepted`, `incident.status_changed`, `donation.received`. Consumers (analytics,
notifications, projections) subscribe; **dead-letter** + retry handle failures. Full patterns in
[`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md).

## 4. Versioning & compatibility
Backward-compatible/additive changes stay on `/api/v1`; a breaking change would introduce `/api/v2`
side-by-side (MVP clients keep working). Inter-service event schemas are versioned independently of the
public API.

## 5. Gateway concerns (per route)
Each route declares: upstream service(s), auth (OIDC/JWT), authz (RBAC/ABAC), rate-limit, cache policy,
timeout/retry, and observability — replacing the MVP's in-app enforcement without changing client-visible
behaviour.

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`20-architecture-system.md`](20-architecture-system.md) · [`50-data-model.md`](50-data-model.md) ·
[`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md) · MVP API [`../idrm-mvp-docs/40-api-specification.md`](../idrm-mvp-docs/40-api-specification.md).
