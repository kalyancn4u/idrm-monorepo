# IDRM FFP — Ownership, Governance & RACI (delta)

> *Type: Document (specification / governance) · Audience: leads, PM, architects, SRE, security · Status: FFP — next-phase (planned)*
> *A **delta** on the MVP governance model
> ([`../idrm-mvp-docs/90-governance-and-raci.md`](../mvp/90-governance-and-raci.md)). Same rule —
> **every capability has exactly one Accountable owner** — extended for a distributed, multi-team, multi-agency
> system. IAM specifics live in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).*

> **Invariant:** the MVP ownership matrix stays valid. FFP adds **per-service** ownership and new governance
> roles as services are extracted — it does not remove owners.

---

## 1. Per-service ownership

As modules are extracted into microservices (Strangler Fig, on a trigger —
[`20-architecture-system.md`](20-architecture-system.md)), **each extracted service gets exactly one Accountable
owner** and its own on-call. The MVP capability matrix still holds; FFP just makes ownership **service-grained**:

| Service (extracted on trigger) | Accountable | On-call |
|--------------------------------|-------------|---------|
| Auth / Identity (extract first) | Security | Platform |
| Incidents | Domain / Product | Backend |
| GIS / geospatial | Domain | GIS/Data |
| Notifications / edge | Domain | Backend |
| Gateway (APISIX) | SRE | Platform |
| Messaging backbone | SRE | Platform |

## 2. New governance roles (FFP)

- **Auditor** — a read-only role over the audit trail and evidence (compliance oversight). New in FFP
  ([`22-…`](22-architecture-security-and-iam.md)).
- **Formal role hierarchy** — beyond the MVP's 4 roles + guest, with delegated administration and multi-agency
  boundaries (ABAC).
- **On-call / SRE rotations** — formal incident-response ownership per service (SLOs, error budgets —
  [`../idrm-mvp-guides/learn/sre-101.md`](../../guides/mvp/learn/sre-101.md)).

## 3. Decision governance at scale

- **ADRs stay the source of truth**, each **trigger-gated** ([`21-architecture-decisions.md`](21-architecture-decisions.md)):
  extraction is a governed decision, not ad hoc.
- **Public contract governance:** the `/api/v1` contract is owned centrally; services may add endpoints at the
  same paths but never rename — contract changes require the contract owner's sign-off.
- **Compliance ownership:** each standard (ISO 22320, NIST CSF 2.0, 800-63-4, WCAG 2.2, DPDP) has an Accountable
  owner; controls trace in [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md).
- **Definition of Done** (blueprint T4) governs "done" for every doc/feature —
  [`../instructions/definition-of-done.md`](../../archive/instructions/definition-of-done.md) — with the FFP addition that
  operational evidence (SLO/audit/restore-drill), not just tests, is required.

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · MVP counterpart [`../idrm-mvp-docs/90-governance-and-raci.md`](../mvp/90-governance-and-raci.md) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) · [`20-architecture-system.md`](20-architecture-system.md).
