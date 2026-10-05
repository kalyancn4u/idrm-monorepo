# IDRM MVP — Requirements Traceability & Compliance Matrix

> *Type: Document (specification / audit spine) · Audience: PM, BA, QA, architects, auditors · Status: MVP — current*
> *The **audit spine**: the single place that links every business need to its requirement, design, API, data,
> test, security control, and evidence. Consolidates the per-doc traceability sections (security §10, quality §4,
> data §11, api §7) into one project-wide thread. Source: documentation blueprint §22.*

> **Why this doc exists (T1 gap):** each spec traces *within* its own scope; nothing traced *across* them.
> This matrix is that missing horizontal thread — so you can answer "where is need X implemented and proven?"
> in one lookup, and spot any requirement with no test or no evidence.

---

## 1. The traceability chain

```mermaid
flowchart LR
    A["Business Need"] --> B["Requirement"]
    B --> C["Design / ADR"]
    C --> D["API + Data"]
    D --> E["Implementation (module)"]
    E --> F["Test"]
    F --> G["Evidence"]
    G --> H["Release"]
```

**Rule:** every requirement must reach **at least one test** and **evidence**. A requirement with no test is a
gap; a design element with no requirement is scope creep.

> **Companion:** this matrix is the *audit spine* (need → … → evidence). Its **checkable, signed-off** counterpart
> — every obligation with an M/O/C status + evidence — is [`26-conformance-pics.md`](26-conformance-pics.md); the
> module-level *what/why/how* behind each capability is [`25-module-elucidation.md`](25-module-elucidation.md).

---

## 2. Feature → capability → requirement → design → API → data → test

Columns: **Feature** (F1–F11 from [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md)) ·
**Capability** ([`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md)) ·
**Design/ADR** ([`21-architecture-decisions.md`](21-architecture-decisions.md)) · **API**
([`40-api-specification.md`](40-api-specification.md)) · **Data** ([`50-data-model.md`](50-data-model.md)) ·
**Test** ([`70-quality-test-strategy.md`](70-quality-test-strategy.md)).

| Feature | Capability | Design / ADR | API (resource) | Data (table) | Test |
|---------|-----------|--------------|----------------|--------------|------|
| F1 Register / auth | Identity | RS256, RBAC (ADR-sec) | `/auth/*` | users, sessions | auth unit + API |
| F2 Report help request | Incident Mgmt | lifecycle ADR | `POST /incidents` | incidents | API + lifecycle |
| F3 Upload media | Evidence & Audit | MinIO ADR | `/incidents/{id}/files` | files (keys) | upload + validation |
| F4 Triage / prioritise | Incident Mgmt | lifecycle | `PATCH /incidents/{id}` | incidents (priority) | rule tests |
| F5 Approve critical | Incident Mgmt | approval gate | `PATCH …/approve` | incidents (status) | RBAC + state |
| F6 Accept / progress / complete | Tasking | lifecycle | `PATCH …/status` | incident_assignments | state-machine |
| F7 Verify | Incident Mgmt | lifecycle | `PATCH …/verify` | incidents | RBAC + state |
| F8 Map / list (COP) | Situation / GIS | PostGIS ADR | `GET /incidents?bbox=` | locations (PostGIS) | spatial query + a11y |
| F9 Resources | Resources | — | `/resources` | resources | API |
| F10 Alerts / notifications | Communications | — | `/notifications` | alerts, notifications | API |
| F11 Reporting / audit | Reporting / Audit | audit ADR | `/reports`, `/audit` | reports, audit | API + audit |

*(This is the MVP skeleton; the authoritative row detail lives in the linked docs — update this matrix whenever a
feature/endpoint/table/test changes. Keep it the single cross-doc index.)*

---

## 3. Security-control traceability

Security requirements trace separately to their controls and evidence (from
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) §10):

| Control | Requirement | Where enforced | Evidence |
|---------|-------------|----------------|----------|
| AuthN (RS256 JWT) | only valid users act | auth module | auth tests |
| AuthZ (RBAC) | role-appropriate actions | every router/service | per-role API tests |
| Audit trail | every state change recorded | audit module | audit tests |
| Input validation | reject bad/oversized input | Pydantic schemas | validation tests |
| Privacy (DPDP) | EXIF strip, no PII in logs | files module, logging | media + log review |

---

## 4. Compliance & standards mapping (T3)

The **single compliance index**: each standard IDRM aligns to, what it requires, where that's addressed, and its
Accountable owner ([`90-governance-and-raci.md`](90-governance-and-raci.md)). Controls also appear in §3.

| Standard | Domain | What it requires (in brief) | Where addressed in IDRM | Owner | Phase |
|----------|--------|------------------------------|-------------------------|-------|-------|
| **ISO 22320** | Emergency management | command/coordination roles, information flow, interoperability | [`12-…operating-model.md`](12-domain-capability-and-operating-model.md); incident lifecycle | Domain | align (MVP) → deeper (FFP) |
| **ICS / NIMS** *(reference)* | Incident command | clear command structure, unity of command, span of control | coordinator/admin chain; incident-command guide | Domain | align — *India uses NDMA / DM Act 2005; NIMS is the US analog, cited for structure only* |
| **NIST CSF 2.0** | Cybersecurity | Govern·Identify·Protect·Detect·Respond·Recover | [`22-…security-and-iam.md`](22-architecture-security-and-iam.md); threat modeling; incident response | Security | core (MVP) → full (FFP) |
| **NIST SP 800-63-4 / 63B-4** | Digital identity | authenticator + password guidance (length>composition, rate-limit, secure storage) | `22` §2.3 (RS256 JWT, bcrypt-12, 5/15 lockout) | Security | MVP |
| **WCAG 2.2 AA** | Accessibility | POUR (Perceivable · Operable · Understandable · Robust — the 4 WCAG principles); keyboard/screen-reader; contrast; target size; consistent help; accessible auth; **map→list** | [`60-uidesign-web-interaction.md`](60-uidesign-web-interaction.md); accessibility-testing guide | UX/Frontend | **both phases** |
| **DPDP Act 2023** | Privacy (India) | data minimisation, consent, no unnecessary PII; biometric only with consent | `22`; files module (EXIF strip, face **detection-only**); logging | Security/Product | core (MVP) → consented features (FFP) |

> **WCAG note (T3 decision, 2026-08-14):** the MVP target was raised from 2.1 AA to **2.2 AA** (both phases now
> 2.2 AA), so the whole platform shares one forward accessibility standard.

The **FFP** compliance view (added columns: release, service, operational evidence) is in
[`../idrm-ffp-docs/13-requirements-traceability-matrix.md`](../ffp/13-requirements-traceability-matrix.md).

---

## 5. How to use & maintain

- **Adding a feature?** add a row; ensure it reaches a test + evidence before "done"
  ([`../instructions/`](../../archive/instructions/00-README.md) workflow).
- **Auditing?** read top-to-bottom: need → … → evidence, with no broken links.
- **FFP delta (planned):** add release/operational-evidence columns and the FFP-only features (money, disaster
  entity, AI matching) as they move from deferred to built.

*Related:* [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) ·
[`12-domain-capability-and-operating-model.md`](12-domain-capability-and-operating-model.md) ·
[`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) ·
[`70-quality-test-strategy.md`](70-quality-test-strategy.md) · [`90-governance-and-raci.md`](90-governance-and-raci.md).
