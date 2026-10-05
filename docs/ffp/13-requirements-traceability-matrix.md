# IDRM FFP — Requirements Traceability & Compliance Matrix (delta)

> *Type: Document (specification / audit spine) · Audience: PM, BA, QA, architects, auditors, compliance · Status: FFP — next-phase (planned)*
> *A **delta** on the MVP audit spine
> ([`../idrm-mvp-docs/13-requirements-traceability-matrix.md`](../mvp/13-requirements-traceability-matrix.md)).
> Same chain (Need → Requirement → Design → API/Data → Test → Evidence) — FFP **adds columns** the enterprise
> phase requires and **adds rows** for the deferred capabilities as they are built.*

> **Invariant:** the MVP matrix stays valid. FFP extends it; it never renames or breaks existing links (mirrors
> the frozen `/api/v1` contract discipline).

---

## 1. Added columns (enterprise audit needs)

Beyond the MVP columns, each FFP requirement also traces to:

- **Release version** — which release delivered it (SemVer).
- **Service** — which extracted microservice owns it (per-service ownership — see [`90-…`](90-governance-and-raci.md)).
- **Operational evidence** — post-release proof it works in production (SLO dashboards, audit exports, restore
  drills) — not just test evidence.
- **Trigger** — the concrete trigger that justified building it ([`21-architecture-decisions.md`](21-architecture-decisions.md)).
- **Compliance control** — the standard/control it satisfies (§3).

## 2. Added rows (FFP capabilities)

The MVP-deferred features become traceable requirements as they land: **money/donations**, **disaster-event
entity + COP**, **per-request privacy (Public/Protected/Private)**, **AI matching**, **multi-channel intake**,
**advanced analytics**, **full localization**, **OIDC/MFA/ABAC/Auditor**. Each gets a full row (need → … →
operational evidence) at build time.

## 3. Compliance traceability (T3 hook)

FFP formalises standards mapping; each control has an Accountable owner ([`90-…`](90-governance-and-raci.md)):

| Domain | Standard | Owner |
|--------|----------|-------|
| Emergency management | **ISO 22320**, NIMS | Domain |
| Cybersecurity | **NIST CSF 2.0** | Security |
| Identity | **NIST SP 800-63-4 / 63B-4** | Security |
| Accessibility | **WCAG 2.2 AA** | UX/Frontend |
| Privacy | **DPDP Act 2023** | Security/Product |

## 4. Maintenance

Same rule as MVP: every requirement reaches a test **and** evidence; FFP adds the **operational-evidence** gate
(proven in production, not just in CI). Keep this the single cross-doc, cross-service index.

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · MVP counterpart [`../idrm-mvp-docs/13-requirements-traceability-matrix.md`](../mvp/13-requirements-traceability-matrix.md) ·
[`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md) ·
[`90-governance-and-raci.md`](90-governance-and-raci.md) · [`70-quality-test-strategy.md`](70-quality-test-strategy.md).
