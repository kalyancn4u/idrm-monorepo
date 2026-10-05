# Traceability Matrix (MVP)

> **⚠️ Stack note (ADR-012):** MVP view layer = FastAPI-served HTML+Tailwind+JS+Leaflet (not Flask/Jinja/Bootstrap); no Redis (sessions in Postgres) + MinIO for files; where this file says Flask/Bootstrap/Redis, defer to [`../mvp/`](../mvp/) and [`../99-decisions-and-history.md`](../99-decisions-and-history.md) (ADR-012).

> **Part of:** IDRM Documentation · `deep-dive/14-traceability-matrix.md`
> **Answers:** How does each requirement connect to design, API, tests, and its source?
> **Source posters:** derived from Poster 2 (requirements) through the data/architecture posters.
> **Standards:** ISO/IEC/IEEE 29148:2018 (bidirectional traceability)
> **Audience:** Developers, QA, architects · **Depth:** Deep
> **Status:** Draft

---

## 1. Purpose

This matrix gives **bidirectional traceability**: every requirement in [`10-srs.md`](10-srs.md) links forward
to the design module ([`11-architecture-and-design.md`](11-architecture-and-design.md)), the API operation(s)
([`openapi.yaml`](openapi.yaml)), the data entities ([`13-data-model.md`](13-data-model.md)), and the test
level ([`../06-quality.md`](../06-quality.md)); and backward to its source poster. It makes coverage and gaps
visible at a glance.

Test-level key: **U** unit · **I** integration · **A** API · **E** end-to-end · **D** demo/UAT.

---

## 2. Functional requirements

| Requirement | Design module | API operation(s) | Entities | Tests | Source |
|---|---|---|---|---|---|
| FR-AUTH-001 register/authenticate | Auth & Access | `POST /auth/login` | `users` | U,A,E | Poster 2, 24 |
| FR-AUTH-002 JWT issue/validate | Auth & Access | `POST /auth/login`, `/auth/refresh` | `users` | U,A | Poster 24 |
| FR-AUTH-003 RBAC | Auth & Access | (all protected ops) | `users`,`roles` | U,A | Poster 24 |
| FR-AUTH-004 user/role admin | Auth & Access | `/users`, `/roles` | `users`,`roles` | A,E | Poster 2 |
| FR-INC-001 report incident | Incident | `POST /incidents` | `incidents` | U,A,E | Poster 2, MVP flow |
| FR-INC-002 number + initial status | Incident | `POST /incidents` | `incidents` | U | Poster 22 |
| FR-INC-003 list/filter incidents | Incident | `GET /incidents` | `incidents` | A,E | MVP flow |
| FR-INC-004 update status | Incident | `PUT /incidents/{id}` | `incidents` | U,A | Poster 2 |
| FR-INC-005 timeline updates | Incident | `/incidents/{id}/updates` | `incident_updates` | A,E | Poster 22 |
| FR-INC-006 forward-only lifecycle | Incident | `PUT /incidents/{id}` | `incidents` | U | Poster 22 |
| FR-RES-001 register resource | Resource | `POST /resources` | `resources`,`resource_types` | U,A | Poster 5, 22 |
| FR-RES-002 deploy/return resource | Resource | `/incidents/{id}/deployments` | `deployments` | A,E | Poster 22 |
| FR-RES-003 create/assign task | Resource | `/tasks`, `PATCH /tasks/{id}` | `tasks` | A,E | Poster 22 |
| FR-RSP-001 responder profile | Responder | `/responders` | `responders` | A | Poster 22 |
| FR-GEO-001 PostGIS storage | Geospatial | (persistence) | `locations`,`geospatial_data` | U,I | Poster 21, 23 |
| FR-GEO-002 map layers by bbox | Geospatial | `GET /map/layers` | `geospatial_data` | A,E | Poster 23, MVP flow |
| FR-GEO-003 radius search | Geospatial | `GET /incidents?near=` | `incidents` | I,A | Poster 23 |
| FR-NOTIF-001 raise alerts | Notification | `POST /alerts` | `alerts` | A,E | Poster 2 |
| FR-NOTIF-002 comm logging | Notification | `/communication-logs` | `communication_logs` | A | Poster 22 |
| FR-NOTIF-003 retry on failure | Notification | (background job) | `alerts` | U,I | Poster 22 |
| FR-DOC-001 attach documents/media | Document/Media | `/documents`, `/media` | `documents`,`media` | A,E | Poster 22 |
| FR-DOC-002 media capture time/location | Document/Media | `/media` | `media` | A | Poster 22 |
| FR-RPT-001 basic dashboards/reports | Analytics | `/reports` (read) | (reads) | D,A | Poster 12, 26 |
| FR-AUD-001 immutable audit log | Audit | (write path) | `audit_logs` | U,I | Poster 24, 22 |
| FR-AUD-002 view/filter audit | Audit | `GET /audit-logs` | `audit_logs` | A | Poster 22 |

---

## 3. Non-functional requirements

| Requirement | Where addressed | Verification | Source |
|---|---|---|---|
| NFR-AVL-001 availability ≥99.5% | Operations (single server + backups) — [`../07-operations.md`](../07-operations.md) | Analysis | Poster 2 |
| NFR-PERF-001 performance/surge | Caching (Redis), indexing, load tests — [`../06-quality.md`](../06-quality.md) | Perf test | Poster 2 |
| NFR-SEC-001 security controls | [`../05-security.md`](../05-security.md) | Security tests | Poster 24, 25 |
| NFR-SEC-002 DPDP privacy | Data governance — [`../05-security.md`](../05-security.md) | Inspection | Poster 2 |
| NFR-USE-001 WCAG 2.2 AA + multilingual | UI (Jinja2/Bootstrap) | Accessibility test | Poster 2 |
| NFR-INT-001 OpenAPI 3.1 APIs | [`12-api-spec.md`](12-api-spec.md) | Inspection | Poster 2 |
| NFR-REL-001 reliability/DR | [`../07-operations.md`](../07-operations.md) | Test | Poster 2 |
| NFR-MNT-001 maintainability/coverage | [`../03-engineering.md`](../03-engineering.md), [`../06-quality.md`](../06-quality.md) | Analysis | Poster 18, 26 |

---

## 4. Coverage summary

- **Every functional requirement** maps to at least one API operation and one automated test level.
- **Every data entity** (Poster 22) is exercised by at least one requirement/operation.
- **Every non-functional requirement** has an owning document and a verification method.
- Gaps or `TODO`s are tracked in [`../99-decisions-and-history.md`](../99-decisions-and-history.md) (change log).

---

*Bidirectional traceability per ISO/IEC/IEEE 29148 — requirements ⇄ design ⇄ API ⇄ tests ⇄ posters.*
