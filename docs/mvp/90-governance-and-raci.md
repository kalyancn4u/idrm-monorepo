# IDRM MVP — Ownership, Governance & RACI

> *Type: Document (specification / governance) · Audience: leads, PM, architects, ops · Status: MVP — current*
> *Who is **accountable** for each capability, and how decisions and changes are governed. Source: documentation
> blueprint §21.*

> **Why this doc exists (T1 gap):** the specs describe the system; none said *who owns what*. The governing rule:
> **every critical capability has exactly one Accountable owner** — so nothing important is orphaned.

---

## 1. RACI in one line

- **R**esponsible — does the work.
- **A**ccountable — the single owner answerable for it (**exactly one** per capability).
- **C**onsulted — gives input before decisions.
- **I**nformed — kept up to date.

*(In a small MVP team one person may wear several hats — but each capability still has **one** named Accountable
owner.)*

## 2. Capability ownership matrix

Capabilities from [`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md):

| Capability | Accountable (1) | Responsible | Consulted | Evidence |
|-----------|-----------------|-------------|-----------|----------|
| Incident lifecycle | Product / Domain | Engineering + QA | Security, Ops | PRD + tests + audit |
| Identity & Org (IAM) | Security | Platform / Backend | Product, Domain | access reviews, auth tests |
| GIS / COP | Domain | GIS / Data | Ops, UX | layer catalogue, spatial tests |
| Tasking & Dispatch | Domain | Engineering | QA, Ops | workflow tests |
| Resources & Logistics | Domain | Engineering | Ops | resource/API tests |
| Communications | Domain | Engineering | Product | notification tests |
| Evidence & Audit | Security | Backend | Product, Domain | audit tests, retention |
| Reporting & Analytics | Product | Engineering / Data | Ops | report tests |
| Administration | Product | Backend | Security | admin tests |
| Deployment | SRE | DevOps | Security, QA | pipeline/runbook, install log |
| Backup / DR | SRE | Platform | Security, Product | **restore drill** evidence |
| Security posture | Security | All engineers | Product | scans, threat model, reviews |

*(Names/titles are role-based; assign real people per team. Keep this the single ownership source of truth.)*

## 3. Decision governance

- **Architecture decisions** → recorded as **ADRs** ([`21-architecture-decisions.md`](21-architecture-decisions.md)),
  each with its rationale and (for FFP) its **trigger**. One source of truth per decision.
- **Changes** → follow the workflow ([`../instructions.txt`](../../archive/instructions.txt) §7): for a change, give options +
  a recommendation, decide, then update the **doc + CHANGELOG** (dated). Cross-link, don't duplicate.
- **Locked decisions** ([`../instructions.txt`](../../archive/instructions.txt) §4) are not re-litigated without the
  Accountable owner + the user.
- **Definition of Done** (blueprint T4) governs when a doc/feature is "done" — the checklist lives at
  [`../instructions/definition-of-done.md`](../../archive/instructions/definition-of-done.md) and traces to
  [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) (must reach a test + evidence).

## 4. Compliance ownership

Each standard (T3) has an Accountable owner: identity → Security (NIST SP 800-63-4); UI accessibility → UX/Frontend
(WCAG 2.2 AA); privacy → Security/Product (DPDP Act 2023); cybersecurity → Security (NIST CSF 2.0);
emergency-management alignment → Domain (ISO 22320 /
NIMS, FFP). Controls trace in [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) §3–4.

## 5. Follow-up
- **FFP delta (planned):** an **Auditor** role, formal role hierarchy, per-service ownership (each extracted
  service gets an Accountable owner), and on-call/SRE rotations — see
  [`../idrm-ffp-docs/22-architecture-security-and-iam.md`](../ffp/22-architecture-security-and-iam.md).

*Related:* [`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md) ·
[`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) ·
[`21-architecture-decisions.md`](21-architecture-decisions.md) ·
[`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md).
