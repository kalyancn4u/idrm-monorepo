# IDRM FFP — Business Domain, Capability & Operating Model (delta)

> *Type: Document (specification) · Audience: product, domain, architects · Status: FFP — next-phase (planned)*
> *A **delta** on the MVP capability/operating model
> ([`../idrm-mvp-docs/12-domain-capability-and-operating-model.md`](../idrm-mvp-docs/12-domain-capability-and-operating-model.md)).
> Same ten capabilities and the same disaster operating model — this states only where FFP **deepens** them.
> Requirement/roadmap detail lives in [`10-requirements-prd.md`](10-requirements-prd.md) and
> [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md); this doc keeps the capability
> lens.*

> **Invariant:** the capability set and the operating model **do not change** — only their *depth* grows, on a
> trigger. Nothing here alters the MVP.

---

## 1. Capability depth: MVP → FFP

| Capability | MVP depth | FFP deepening (on trigger) |
|-----------|-----------|-----------------------------|
| Identity & Organization | RBAC, 4 roles + guest | OIDC/SSO, MFA, ABAC, full role hierarchy + **Auditor** |
| Incident Management | 8-state lifecycle | disputed/auto-close states, disaster-event entity, per-request privacy |
| Situation Awareness / COP | basic map + list | **live national COP** (real-time, layered, multi-agency) |
| GIS | native PostGIS | dedicated Python geospatial service, richer spatial analysis |
| Tasking & Dispatch | human-driven | **AI-assisted matching / optimisation** |
| Resources & Logistics | human matching | predictive resourcing, cross-org logistics |
| Communications | in-app alerts | **multi-channel** (SMS/push/email), CAP, deep real-time push |
| Evidence & Audit | audit trail | Auditor role, retention/compliance tooling |
| Reporting & Analytics | MVP metrics | **decision-support analytics**, dashboards |
| Administration | basic | multi-tenant, federation, delegated admin |
| *(new)* Financial | — (deferred) | **donations / funds** capability (money = FFP only) |

## 2. Operating-model deepening

The MVP focuses on **Detect → Assess → Respond → Coordinate → Stabilize**. FFP extends deep support **outward**:

- **Prepare** — readiness, plans, drills, predictive risk.
- **Recover** — longer-term rebuild tracking, financial aid flows.
- **Review → Learn** — richer after-action analytics feeding Prepare (the full cycle closes).

## 3. Traceability

- Capability **depth** requirements trace in [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) (FFP delta).
- Capability **ownership** (per-service, Auditor) in [`90-governance-and-raci.md`](90-governance-and-raci.md) (FFP delta).
- Each deepening is **trigger-gated** — see [`21-architecture-decisions.md`](21-architecture-decisions.md).

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · MVP counterpart [`../idrm-mvp-docs/12-domain-capability-and-operating-model.md`](../idrm-mvp-docs/12-domain-capability-and-operating-model.md) ·
[`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md) · [`20-architecture-system.md`](20-architecture-system.md).
