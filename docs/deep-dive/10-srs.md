# Software Requirements Specification (MVP)

> **⚠️ Stack note (ADR-012):** MVP view layer = FastAPI-served HTML+Tailwind+JS+Leaflet (not Flask/Jinja/Bootstrap); no Redis (sessions in Postgres) + MinIO for files; where this file says Flask/Bootstrap/Redis, defer to [`../mvp/`](../mvp/) and [`../99-decisions-and-history.md`](../99-decisions-and-history.md) (ADR-012).

> **Part of:** IDRM Documentation · `deep-dive/10-srs.md`
> **Answers:** What exactly must the IDRM MVP do, and how well?
> **Source posters:** Poster 2 (Problem & PRD), Poster 1 (Vision); conforms to the domains in
> [`../01-foundation.md`](../01-foundation.md) and entities in [`13-data-model.md`](13-data-model.md).
> **Standards:** ISO/IEC/IEEE 29148:2018 (requirements engineering)
> **Audience:** Developers, QA, architects · **Depth:** Deep
> **Status:** Draft

---

## 1. Introduction

### 1.1 Purpose
This document specifies the requirements for the IDRM MVP — a standalone modular monolith for integrated
disaster response. It is the authoritative list of *what must be true* of the system, written so each
requirement is uniquely identified and verifiable (per ISO/IEC/IEEE 29148).

### 1.2 Scope
In scope and out of scope are defined by Poster 2 and restated in
[`../01-foundation.md`](../01-foundation.md) §3. In short: the MVP covers situational awareness, incident
reporting & alerts, resource and responder coordination, communication, basic analytics, user/role
management, mobile & web access, and data security & audit. Advanced AI/ML, complex finance, long-term
recovery planning, and deep third-party integration are out of scope for the MVP.

### 1.3 Definitions & references
Terms are defined in [`../90-glossary.md`](../90-glossary.md). Key references: the posters (`posters/`), the
data model ([`13-data-model.md`](13-data-model.md)), and the API ([`12-api-spec.md`](12-api-spec.md)).

### 1.4 Requirement identifiers
- **Functional:** `FR-<MODULE>-NNN` (e.g. `FR-INC-001`).
- **Non-functional:** `NFR-<QUALITY>-NNN`.
- Each requirement has a **verification method**: **T** (test), **D** (demonstration), **I** (inspection),
  **A** (analysis).

---

## 2. Overall description

- **Product perspective:** one Python 3.12 application (Flask web UI + FastAPI APIs + in-process background
  jobs) on PostgreSQL/PostGIS + Redis, deployed on a standalone Ubuntu server.
- **Users:** Citizen, Volunteer/Responder, Coordinator, Administrator, plus government/agency stakeholders
  (see [`../01-foundation.md`](../01-foundation.md) §5).
- **Constraints:** modular monolith; server-rendered UI; standards-based APIs; WCAG 2.2 AA; DPDP Act 2023.
- **Assumptions:** single-server MVP scale; internet/network available; agencies supply reference data.

---

## 3. Functional requirements

Each requirement traces to a data entity ([`13-data-model.md`](13-data-model.md)) and an API operation
([`openapi.yaml`](openapi.yaml)); consolidated in [`14-traceability-matrix.md`](14-traceability-matrix.md).

### 3.1 Authentication & access (AUTH)
| ID | Requirement | Verify |
|---|---|---|
| FR-AUTH-001 | Users can register and authenticate with email + password; passwords are stored only as hashes. | T |
| FR-AUTH-002 | The system issues a JWT on login and validates it on each protected request. | T |
| FR-AUTH-003 | Access is governed by role-based permissions (RBAC) tied to the user's role. | T |
| FR-AUTH-004 | Administrators can manage users, roles, and account status. | T |

### 3.2 Incident management (INC)
| ID | Requirement | Verify |
|---|---|---|
| FR-INC-001 | A user can report an incident with type, severity, location, and description. | T |
| FR-INC-002 | Each incident is assigned a unique incident number and an initial status. | T |
| FR-INC-003 | Incidents can be listed and filtered by status, severity, type, and area (bbox). | T |
| FR-INC-004 | Authorised users can update an incident's status through its lifecycle. | T |
| FR-INC-005 | A timeline of incident updates is recorded and viewable. | T |
| FR-INC-006 | Incident status transitions only move forward through the defined lifecycle. | T |

### 3.3 Resource & response (RES / RSP)
| ID | Requirement | Verify |
|---|---|---|
| FR-RES-001 | Organisations can register resources with type, quantity, unit, owner, and location. | T |
| FR-RES-002 | Resources can be deployed to an incident and later marked returned. | T |
| FR-RES-003 | Tasks can be created for an incident and assigned to a user. | T |
| FR-RSP-001 | Users can act as responders on behalf of an organisation, with recorded skills/status. | T |

### 3.4 Geospatial (GEO)
| ID | Requirement | Verify |
|---|---|---|
| FR-GEO-001 | The system stores locations and features as PostGIS geometry (EPSG:4326). | T |
| FR-GEO-002 | Map layers/features can be retrieved, filtered by layer type and bounding box. | T |
| FR-GEO-003 | The system can find records within a given radius of a point. | T |

### 3.5 Communication & alerts (NOTIF)
| ID | Requirement | Verify |
|---|---|---|
| FR-NOTIF-001 | The system can raise alerts for an incident across channels (email, SMS, push, in-app). | T |
| FR-NOTIF-002 | Communications are logged with channel, direction, and delivery status. | T |
| FR-NOTIF-003 | Alert/notification delivery is retried on failure up to a defined limit. | T |

### 3.6 Documents & media (DOC)
| ID | Requirement | Verify |
|---|---|---|
| FR-DOC-001 | Users can attach documents and media to an incident; files are held in object storage. | T |
| FR-DOC-002 | Media may carry capture time and location. | T |

### 3.7 Analytics & audit (RPT / AUD)
| ID | Requirement | Verify |
|---|---|---|
| FR-RPT-001 | The system provides basic operational dashboards/reports (counts, status, response times). | D |
| FR-AUD-001 | Every significant action is written to an immutable audit log with before/after values. | T |
| FR-AUD-002 | Administrators can view and filter the audit log. | T |

---

## 4. Non-functional requirements

| ID | Quality | Requirement | Verify |
|---|---|---|---|
| NFR-AVL-001 | Availability | Target availability ≥ 99.5% for core operations. | A |
| NFR-PERF-001 | Performance | Read APIs meet targets under load (p95 < 800 ms; error rate < 1%); scales during surge. | T |
| NFR-SEC-001 | Security | Enforce HTTPS/TLS, RBAC, input validation, and the controls in [`../05-security.md`](../05-security.md); mitigate the **OWASP Top 10 (2021)** per the mapping in [`../05-security.md`](../05-security.md) §6.5. | T |
| NFR-SEC-002 | Privacy | Handle personal data per the DPDP Act 2023 (minimisation, access control). | I |
| NFR-USE-001 | Usability/Accessibility | UI meets WCAG 2.2 AA and is multilingual-ready. | T |
| NFR-INT-001 | Interoperability | Expose standards-based APIs described in OpenAPI 3.1. | I |
| NFR-REL-001 | Reliability | Fault-tolerant behaviour with retries, timeouts, and backups/recovery ([`../07-operations.md`](../07-operations.md)). | T |
| NFR-MNT-001 | Maintainability | Modular, tested (target ~80% coverage), observable ([`../06-quality.md`](../06-quality.md)). | A |

---

## 5. External interfaces

- **User interfaces:** server-rendered web pages (Flask + Jinja2 + Bootstrap 5), accessible on web and mobile
  browsers.
- **Application interfaces:** REST API under `/api/v1` (see [`12-api-spec.md`](12-api-spec.md)).
- **Data interfaces:** PostgreSQL/PostGIS, Redis, object storage.
- **External systems (essential only):** e.g. weather/hazard feeds and map/geo services via adapters.

---

## 6. Verification approach

Each requirement's verification method (T/D/I/A) is realised through the testing strategy in
[`../06-quality.md`](../06-quality.md): unit/integration/API/E2E tests for **T**, stakeholder demos/UAT for
**D**, document/config review for **I**, and modelling/measurement for **A**. Coverage of requirements is
tracked in [`14-traceability-matrix.md`](14-traceability-matrix.md).

---

*Requirements derive from Poster 2 (Problem & PRD); identifiers are stable and referenced by design, API, and tests.*
