# IDRM FFP — Product Requirements Document (PRD)

> *Type: Document (specification) · Audience: everyone · Status: FFP — next-phase (planned)*
> *Extends the MVP PRD [`../idrm-mvp-docs/10-requirements-prd.md`](../idrm-mvp-docs/10-requirements-prd.md). This states the **enterprise-scale needs** the FFP adds — **needs only, no technology** (stack lives in [`20-architecture-system.md`](20-architecture-system.md)). Every item here is a deliberate **MVP deferral** now being chartered (see the [FFP charter](prompts/instructions_idrm_ffp_docs.md)).*

> **Golden rule:** the FFP is the MVP **grown up**, not a different product. Everything the MVP proved
> stays true; the FFP adds scale, reach, and depth **only when a concrete need justifies it**.

---

## 1. Vision (at FFP scale)

The MVP proved "Uber for disaster relief" for an initial region. The **FFP** takes that proven core to
**national scale and multi-agency coordination** — many states, thousands of organizations, millions of
citizens — as an **enterprise resilience platform** that senses, decides, coordinates, acts, verifies,
records, and learns across the full disaster lifecycle (Prepare → Detect → Assess → Respond → Coordinate →
Stabilize → Recover → Review → Learn).

## 2. What the FFP adds (vs the MVP)

| Area | MVP (proven) | FFP (this document) |
|---|---|---|
| Reach | 2 states, 50+ districts | **National** — all states/UTs, multi-agency |
| Users | 10k+ | **Millions** MAU; 10k+ concurrent, surge to 25k+ |
| Clients | one responsive web app | **React web SPA** + **native mobile** (field/offline) |
| Matching | rule-based | **AI-assisted** matching/routing & decision support |
| Money | — | **Donations, fund allocation, financial transparency** |
| Events | request-centric | first-class **disaster events**, affected-area mapping, COP |
| Analytics | basic reports | **predictive/advanced analytics**, dashboards |
| Language | English + 1 regional | **full localization** (12+ Indian languages) |
| Intake | web + SMS fallback | **multi-channel** (WhatsApp / voice / IVR) |
| Realtime | near-real-time | **deep real-time push** (live COP) |
| Identity | photo quality gate | **biometric matching** (missing-person), with consent |

## 3. Enterprise objectives & outcomes
Extends MVP O1–O3 (save lives · efficiency · trust) with: **O4 multi-agency interoperability**,
**O5 national situational awareness (COP)**, **O6 predictive readiness**, **O7 auditable accountability &
compliance at scale**. Success is measured by capability (operational drills passed), not features shipped.

## 4. Stakeholders & personas (broadened)
MVP personas remain (Rajesh/Priya/Arjun/Lakshmi). FFP adds the **command structure** (Incident Commander,
Operations/Planning/Logistics/Safety leads), **response services** (Police/Fire/EMS/SAR), **EOC / district
authority**, **auditors**, **donors**, and the wider **support ecosystem** (hospitals, shelters, utilities,
transport, volunteers). Each persona keeps the MVP contract: *Goal → Responsibility → Information → Actions →
Permissions → Inputs → Outputs → Failure scenarios* (detailed in the FFP security/IAM doc).

## 5. FFP functional requirements (extend FR-1…12)

| ID | Requirement |
|---|---|
| **FFP-FR-1** | **Disaster events** — authorities declare events, draw affected areas, and auto-link incidents; live **Common Operational Picture (COP)**. |
| **FFP-FR-2** | **AI-assisted matching/routing** and decision support (suggested providers, hotspots, resource optimization). |
| **FFP-FR-3** | **Financial transparency** — donations, fund allocation, disbursement, receipts, audit. |
| **FFP-FR-4** | **Native mobile apps** (field responder, offline-first) + a **rich web SPA**. |
| **FFP-FR-5** | **Multi-channel intake** — WhatsApp / voice / IVR, in addition to web/SMS. |
| **FFP-FR-6** | **Full localization** (12+ Indian languages) across all clients. |
| **FFP-FR-7** | **Advanced / predictive analytics** and executive dashboards. |
| **FFP-FR-8** | **Deep real-time** collaboration/push (live map, tasking, chat). |
| **FFP-FR-9** | **Enterprise IAM** — OIDC/SSO, MFA, ABAC, org/jurisdiction boundaries, full role hierarchy + Auditor. |
| **FFP-FR-10** | **Biometric matching** (missing persons) with explicit consent & DPDP safeguards. |
| **FFP-FR-11** | **Multi-agency interoperability** — federation & external-system integration (same public API). |

*(All MVP FR-1…12 remain in force and unchanged; the FFP is additive.)*

## 6. Non-functional requirements (enterprise SLAs)

| ID | Requirement | Target |
|---|---|---|
| **FFP-NFR-1 Availability** | HA, no single point of failure | **≥ 99.9%**; graceful degradation under surge |
| **FFP-NFR-2 Scale** | Horizontal scale of hot paths | millions MAU; 10k+ concurrent; 25k+ surge |
| **FFP-NFR-3 Performance** | Responsive at scale | API p95 < 300–500 ms behind the gateway |
| **FFP-NFR-4 Security & privacy** | Zero-trust, DPDP compliance, biometric consent | see FFP security doc |
| **FFP-NFR-5 Observability** | Full logs/metrics/traces + domain-health | see FFP ops doc |
| **FFP-NFR-6 Resilience/DR** | Backup/restore/failover tested | RTO/RPO tightened vs MVP |
| **FFP-NFR-7 Interoperability** | Standards-aligned (ISO 22320, NIMS) | multi-agency ready |

## 7. Constraints, assumptions, dependencies
India-focused, government-endorsed and governed; **preserve the MVP public API contract**; introduce each
capability **only when a real trigger justifies it** (no big-bang). Depends on partner-org onboarding at
scale, payment-gateway partners (financial), messaging/telephony partners (multi-channel), and identity
providers (OIDC).

## 8. Success criteria (FFP horizon)
National coverage; multi-agency adoption; sustained sub-second response at surge; measurable reductions in
response time and duplication vs MVP baselines; audited financial transparency; and demonstrated
**operational-drill** readiness. Precise phase gates live in [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md).

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md) · [`20-architecture-system.md`](20-architecture-system.md) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) · MVP PRD [`../idrm-mvp-docs/10-requirements-prd.md`](../idrm-mvp-docs/10-requirements-prd.md).
Charter: [`prompts/instructions_idrm_ffp_docs.md`](prompts/instructions_idrm_ffp_docs.md).
