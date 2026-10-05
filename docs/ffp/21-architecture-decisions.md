# IDRM FFP — Architecture Decision Records (ADRs)

> *Type: Document (decision log) · Audience: developers, architects · Status: FFP — next-phase (planned)*
> *Extends the MVP ADRs [`../idrm-mvp-docs/21-architecture-decisions.md`](../mvp/21-architecture-decisions.md). Each FFP ADR records an addition the MVP deferred, **with the concrete trigger that justifies it** — nothing is added "because enterprise." Consolidates `v3/22-architecture-decisions.md` (46 ADRs) and `v2/24-architecture-decisions.md`.*

> **Rule:** an FFP ADR is only **Accepted** once its **trigger** is met (see the phase triggers in
> [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md)). Until then it is
> **Proposed**. Each supersedes the matching MVP "→ FFP" deferral, never edits it.

**Format:** Decision · Trigger · Options · Consequences.

---

## FFP-ADR-001 — Selective microservices (extract on trigger)
- **Decision:** Extract monolith modules into services **one at a time**, least-coupled first.
- **Trigger:** a module needs independent scale / ownership / deploy / performance / reliability.
- **Options:** big-bang microservices · **incremental extraction** ✅ · stay monolith.
- **Consequences:** contract preserved; complexity added only where earned. *(Reverses MVP-ADR-001 per module.)*

## FFP-ADR-002 — APISIX as the API gateway
- **Decision:** Front all traffic with **APISIX** (plugins: reverse proxy, TLS, auth, authz, rate-limit, cache, LB, observability).
- **Trigger:** multiple services/clients need centralized routing, TLS, auth, and rate-limiting.
- **Options:** NGINX · Kong · **APISIX** ✅ · per-service edge only.
- **Consequences:** one policy-driven front door; the MVP's light TLS proxy is retired. *(Not NGINX — charter.)*

## FFP-ADR-003 — Bun/Node/Deno edge **behind** APISIX
- **Decision:** JS **edge/BFF/SSR/websocket** services run behind the gateway, not as the gateway.
- **Trigger:** client-facing real-time / SSR / request-composition needs.
- **Consequences:** rich client experiences without touching the public contract.

## FFP-ADR-004 — Polyglot runtimes (Java/Go/JS + Python)
- **Decision:** Hot/critical services may be Java/Go/JS; **Python retained** for prototyping + DS/ML.
- **Trigger:** a service's scale/latency/fault-isolation needs exceed Python's sweet spot.
- **Consequences:** runtime diversity = resilience/backup; one API contract keeps interoperability.

## FFP-ADR-005 — Redis / Redis Streams
- **Decision:** Introduce Redis for **caching + light event streams + sessions**.
- **Trigger:** measured read-latency/session/async needs the DB shouldn't carry.
- **Consequences:** faster hot paths; Redis is never the source of truth. *(Reverses MVP-ADR-005.)*

## FFP-ADR-006 — RabbitMQ / Kafka (after Redis Streams)
- **Decision:** Graduate to a broker when durability/replay/fan-out/throughput demand it.
- **Trigger:** Redis Streams outgrown (durable, high-fan-out, replayable events).
- **Options:** RabbitMQ (routing) · Kafka (log/replay/scale) — pick per need.

## FFP-ADR-007 — Docker → Swarm/Kubernetes
- **Decision:** Containerise services; orchestrate with **Swarm first, Kubernetes at scale**.
- **Trigger:** multi-service deploy, autoscaling, HA. *(Reverses MVP-ADR-006.)*

## FFP-ADR-008 — React web SPA + React Native/Expo mobile
- **Decision:** Add a **React** SPA and **native mobile** apps on the **same API**.
- **Trigger:** rich admin dashboards; field/offline mobile use. *(Reverses MVP-ADR-004; HTML/Tailwind stays valid.)*

## FFP-ADR-009 — Database-per-service + events/projections
- **Decision:** Extracted services **own their data**; cross-service via events + projections (eventual consistency).
- **Trigger:** a service is extracted (ADR-001). PostGIS remains system of record.

## FFP-ADR-010 — Enterprise IAM (OIDC/SSO, MFA, ABAC)
- **Decision:** Add **OIDC/SSO**, **MFA**, and **ABAC** (area/jurisdiction/ownership policy) at the gateway + services.
- **Trigger:** multi-agency onboarding; regulatory identity requirements. *(Extends MVP RBAC.)*

## FFP-ADR-011 — Full observability stack
- **Decision:** Prometheus/Grafana (metrics), Loki (logs), Tempo/OpenTelemetry (traces) + domain-health.
- **Trigger:** distributed services need correlation & SLO monitoring.

## FFP-ADR-012 — Secrets vault / KMS + at-rest AES-256
- **Decision:** Central secrets vault (Vault/KMS); field-level PII encryption at rest.
- **Trigger:** multi-service secrets + compliance (DPDP) at scale. *(Extends MVP env-var secrets.)*

## FFP-ADR-013 — First-class disaster events + COP; financial module
- **Decision:** Add `disasters`/`affected_areas` and the `financial_*` domain as services/tables.
- **Trigger:** multi-agency coordination (events/COP) and donation transparency demand.

## FFP-ADR-014 — Biometric matching (FaceNet) — consent-gated
- **Decision:** Add FaceNet **recognition** for missing-person matching, **only** with explicit consent + DPDP safeguards.
- **Trigger:** validated humanitarian need (reuniting families). *(Reverses MVP ADR-011's deferral, with guardrails.)*

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`20-architecture-system.md`](20-architecture-system.md) · [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) ·
[`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md) · MVP ADRs [`../idrm-mvp-docs/21-architecture-decisions.md`](../mvp/21-architecture-decisions.md).
