# IDRM FFP — Learning Paths (delta on the MVP guides)

> *Type: Guide (orientation / index) · Audience: everyone moving from MVP to FFP · Status: FFP — next-phase*
> *This is a **delta**, not a copy. The full novice→mastery library lives once, in
> [`../idrm-mvp-guides/`](../mvp/00-start-learning-paths.md) — every 101 guide and role guide there is
> already **phase-tagged** (MVP vs FFP). This page routes you to the **FFP-specific** rungs and the FFP docs.*

> **Why no duplicate library?** One source of truth (guardrail: *cross-link, don't duplicate*). The shared
> `learn/` library and `roles/` journeys teach both phases; this hub simply sequences the FFP path through them.

---

## 1. What FFP adds (the whole delta in one view)

Same product, same **`/api/v1` contract**, evolved on concrete **triggers** — never a rewrite:

| Area | MVP (now) | FFP (this hub's focus) |
|---|---|---|
| Frontend | HTML + Tailwind + JS + Leaflet | **React SPA + React Native/Expo** (offline-first) |
| Gateway | none (FastAPI direct) | **APISIX** (Kong evaluated, not chosen — free build) |
| Services | one modular monolith | **selective microservices** (Strangler Fig, on a trigger) |
| Runtimes | pure Python | **polyglot** (Java/Go/JS) + edge (Bun/Node/Deno) |
| Identity | RS256 JWT + RBAC | **OIDC, OAuth 2.1+PKCE, MFA, ABAC** + Auditor |
| Async | synchronous | **Redis Streams → RabbitMQ/Kafka**, real-time push |
| Deploy | native systemd on Ubuntu | **Docker → Kubernetes**, full CI/CD |
| Observability | logs + health endpoints | **Prometheus/OTel/tracing**, SLOs, RUM |
| Data | one PostgreSQL+PostGIS | per-service ownership (PostGIS stays source of truth) |

---

## 2. The FFP reading path (through the shared 101 library)

Read these FFP-tagged 101s, in order — all in [`../idrm-mvp-guides/learn/`](../mvp/learn/README.md):

1. **Frontend:** [`gis-for-emergency-response`](../mvp/learn/gis-for-emergency-response.md) →
   [`common-operational-picture-101`](../mvp/learn/common-operational-picture-101.md) → then the FFP
   frontend spec [`../idrm-ffp-docs/61-frontend-engineering-standards.md`](../../docs/ffp/61-frontend-engineering-standards.md)
2. **Identity:** [`iam-101`](../mvp/learn/iam-101.md) → [`oidc-101`](../mvp/learn/oidc-101.md) →
   [`oauth-2.1-pkce-101`](../mvp/learn/oauth-2.1-pkce-101.md) → [`mfa-101`](../mvp/learn/mfa-101.md) →
   [`rbac-abac-101`](../mvp/learn/rbac-abac-101.md) (ABAC part)
3. **Async & scale:** [`event-driven-architecture-101`](../mvp/learn/event-driven-architecture-101.md) →
   [`caching-messaging spoke`](../../archive/instructions/caching-messaging.md) →
   [`performance-testing-101`](../mvp/learn/performance-testing-101.md)
4. **Platform:** [`docker-101`](../mvp/learn/docker-101.md) →
   [`ci-cd-101`](../mvp/learn/ci-cd-101.md) → [`cloud-101`](../mvp/learn/cloud-101.md) →
   [`sre-101`](../mvp/learn/sre-101.md)
5. **Gateway & services:** [`api-gateway spoke`](../../archive/instructions/api-gateway.md) →
   [`backend-services spoke`](../../archive/instructions/backend-services.md) →
   [`../idrm-ffp-docs/20-architecture-system.md`](../../docs/ffp/20-architecture-system.md)

---

## 3. FFP deltas per role

Each role's full journey is in [`../idrm-mvp-guides/roles/`](../mvp/roles/README.md); the FFP-specific
"next" for each:

- **Frontend Engineer** → React + TypeScript + TanStack Query/RHF/Zod, offline-first RN (doc 61).
- **Backend Engineer** → service extraction (Strangler Fig), events/brokers, polyglot.
- **Security Engineer** → OIDC/OAuth 2.1+PKCE/MFA/ABAC, WAF (`coraza-waf`), DAST/pen tests, vault.
- **DevOps/SRE** → Docker→K8s, CI/CD, distributed observability, formal SLOs, multi-region DR.
- **Data Engineer** → per-service data ownership, event streams, ETL/ELT, analytics platform.
- **Architect** → the microservices extraction strategy + APISIX gateway (trigger-gated ADRs).
- **GIS / QA / PM / BA / Ops Manager / Support** → richer live COP, chaos/perf suites, national-scale scope,
  multi-agency workflows, distributed-system support — all on the same contract.

---

## 4. FFP specification docs (the authoritative source)

- Architecture: [`20-architecture-system.md`](../../docs/ffp/20-architecture-system.md) ·
  [`21-architecture-decisions.md`](../../docs/ffp/21-architecture-decisions.md)
- Security/IAM: [`22-architecture-security-and-iam.md`](../../docs/ffp/22-architecture-security-and-iam.md)
- Frontend: [`60-uidesign-frontend.md`](../../docs/ffp/60-uidesign-frontend.md) +
  [`61-frontend-engineering-standards.md`](../../docs/ffp/61-frontend-engineering-standards.md)
- Messaging/async: [`81-ops-messaging-and-async.md`](../../docs/ffp/81-ops-messaging-and-async.md)
- Contributing across services: [`30-contribute-developer-guide.md`](30-contribute-developer-guide.md)

---

*Related:* component map [`tech-stack-101.md`](../mvp/learn/tech-stack-101.md) · FFP elucidation + conformance
[`25-module-elucidation.md`](../../docs/ffp/25-module-elucidation.md) / [`26-conformance-pics.md`](../../docs/ffp/26-conformance-pics.md) ·
MVP learning hub [`../idrm-mvp-guides/00-start-learning-paths.md`](../mvp/00-start-learning-paths.md) ·
the topic spokes [`../instructions/00-README.md`](../../archive/instructions/00-README.md).
