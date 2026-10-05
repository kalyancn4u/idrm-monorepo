# IDRM MVP — Conformance Checklist (PICS-style)

> ✅ **SIGNED OFF 2026-08-16** (task-I gate) — approved as the build gate for the MVP code. 65 rows; all `Planned`
> until code + passing tests flip them to `Yes`.

> *Type: Document (conformance / normative) · Audience: builders, reviewers, QA · Status: MVP — current*
> *A **PICS** (Protocol Implementation Conformance Statement) states, per capability, whether it is implemented
> and to what obligation. This is the **build gate** for the MVP code and the acceptance/review checklist. It is
> the normative twin of the informative [`25-module-elucidation.md`](25-module-elucidation.md) + component map
> [`../../guides/mvp/learn/tech-stack-101.md`](../../guides/mvp/learn/tech-stack-101.md). Grown document-wise from the
> `_removed` cleanup (ledger: [`../../archive/_removed/_CLEANUP-LEDGER.md`](../../archive/_removed/_CLEANUP-LEDGER.md)).*

---

## How to read a PICS row

| Column | Meaning |
|---|---|
| **ID** | Stable id: `PICS-‹MODULE›-‹NNN›` or `PICS-STK-‹COMPONENT›-‹NN›`. |
| **Capability / obligation** | The single checkable requirement. |
| **Status** | **M** = mandatory · **O** = optional · **C** = conditional (predicate stated in the row). |
| **Phase** | MVP here (FFP items live in [`../ffp/26-conformance-pics.md`](../ffp/26-conformance-pics.md)). |
| **Supported** | Implementation state: **Planned** (spec'd, not built) · **Partial** · **Yes** · **No/NA**. Flips to **Yes** only when code + passing test exist. |
| **Evidence** | The authoritative doc §; later, the code path + test id. |
| **src** | The `_removed` snippet(s) this row was reconciled from. |

> **All rows are `Planned` today** — the MVP code (`../../services/monolith/`) is not built yet. This sheet is what "done"
> will be measured against. Legend for module codes: see the ledger.

---

## A. Module conformance

### INC — Incidents
<!-- IDRM-ELUCID src=v0-10§4.4 src=v0-10§4.5 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-INC-001 | Citizen creates an incident (`service_type`, `priority`, `location`, `description`) | M | MVP | Planned | [40](40-api-specification.md) · [11](11-requirements-scope-and-acceptance.md) | v0-10§4.4 |
| PICS-INC-002 | 8-state lifecycle transitions enforced with role+state guards | M | MVP | Planned | [11](11-requirements-scope-and-acceptance.md) · ADR-009 [21](21-architecture-decisions.md) | v0-10§4.4 |
| PICS-INC-003 | Critical incidents require coordinator **approval** before `accepted` | C (priority = critical) | MVP | Planned | [11](11-requirements-scope-and-acceptance.md) | v0-10§4.4 |
| PICS-INC-004 | Provider `accepted → in_progress → completed` (completion needs proof) | M | MVP | Planned | [11](11-requirements-scope-and-acceptance.md) · FIL | v0-10§4.5 |
| PICS-INC-005 | Coordinator **verifies** completion (`completed → verified`, ReVV) | M | MVP | Planned | [11](11-requirements-scope-and-acceptance.md) | v0-10§4.5 |
| PICS-INC-006 | Citizen may `cancel` own incident (pre-acceptance) | M | MVP | Planned | [11](11-requirements-scope-and-acceptance.md) | v0-10§4.4 |
| PICS-INC-007 | Coordinator may `reject` with a reason | M | MVP | Planned | [11](11-requirements-scope-and-acceptance.md) | v0-10§4.4 |
| PICS-INC-008 | Every endpoint enforces the role→operation RBAC matrix | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-10§4.1, §7 |
| PICS-INC-009 | Inputs validated by Pydantic; enum values fixed (no invented values) | M | MVP | Planned | [40](40-api-specification.md) · [50](50-data-model.md) | v0-10§6 |
| PICS-INC-010 | Every state change written to the audit trail | M | MVP | Planned | [22](22-architecture-security-and-iam.md) (AUD) | v0-10§7 |
| PICS-INC-011 | Location persisted as PostGIS point, SRID 4326 | M | MVP | Planned | [50](50-data-model.md) | v0-10§4.3 |
| PICS-INC-012 | Unit + API tests for each transition; ≥80% coverage | M | MVP | Planned | [70](70-quality-test-strategy.md) | v0-10§9 |
| PICS-INC-013 | List/get incidents **scoped by role**: citizen→own · provider→assigned/in-area · coordinator→all | M | MVP | Planned | [22](22-architecture-security-and-iam.md) · [40](40-api-specification.md) | v0-40§svc |
| — | `disputed` state · auto-close | (deferred) | → FFP | NA | [../ffp/26](../ffp/26-conformance-pics.md) | v0-10§4.4 |

### USR — Users
<!-- IDRM-ELUCID src=v0-20§6.2 src=v0-20§6.3 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-USR-001 | Register/login; RS256 JWT access (~60 min) + rotating/revocable refresh (~7 d) | M | MVP | Planned | ADR-008 · [22](22-architecture-security-and-iam.md) | v0-20§6.2 |
| PICS-USR-002 | Passwords hashed with bcrypt (cost 12); NIST policy (length > composition) | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.2 |
| PICS-USR-003 | 5-attempt / 15-min account lockout | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.2 |
| PICS-USR-004 | Sessions stored in PostgreSQL (no Redis) | M | MVP | Planned | ADR-005 [21](21-architecture-decisions.md) | v0-20§4.4 |
| PICS-USR-005 | RBAC role→operation matrix enforced (4 roles + guest) | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.3 |
| PICS-USR-006 | Refresh-token rotation + revocation on logout | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.2 |
| PICS-USR-007 | Narrow **guest** path: view public info + submit emergency-"lite" request, rate-limited | M | MVP | Planned | [22](22-architecture-security-and-iam.md) · [11](11-requirements-scope-and-acceptance.md) | v0-40§anon |

### LOC — Locations
<!-- IDRM-ELUCID src=v0-20§3.4 src=v0-20§4.2 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-LOC-001 | Locations persisted as PostGIS geometry, SRID 4326 | M | MVP | Planned | [50](50-data-model.md) | v0-20§3.4 |
| PICS-LOC-002 | GiST spatial index on location columns | M | MVP | Planned | [50](50-data-model.md) | v0-20§4.2 |
| PICS-LOC-003 | Proximity query (`ST_DWithin`) for nearest capable providers | M | MVP | Planned | [50](50-data-model.md) · [60](60-uidesign-web-interaction.md) | v0-20§3.4 |
| PICS-LOC-004 | Geofence / point-in-polygon for affected-area checks | O | MVP | Planned | [50](50-data-model.md) | v0-20§3.4 |
| PICS-LOC-005 | Map renders via Leaflet from API geo data | M | MVP | Planned | [60](60-uidesign-web-interaction.md) | v0-20§3.4 |

### NTF — Notifications
<!-- IDRM-ELUCID src=v0-20§3.5 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-NTF-001 | A notification is generated on each incident state change | M | MVP | Planned | [30](30-design-data-flow-and-modules.md) | v0-20§3.5 |
| PICS-NTF-002 | In-app near-real-time delivery (no message broker in MVP) | M | MVP | Planned | ADR-012 [21](21-architecture-decisions.md) | v0-20§3.5 |
| PICS-NTF-003 | Notifications reference the incident and are auditable | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-20§3.5 |
| PICS-NTF-004 | FAQ chatbot stub: a fixed acknowledgement (Task L; real NLP → FFP) | O | MVP | Planned | [21](21-architecture-decisions.md) | v0-20§3.5 |

### RES — Resources
<!-- IDRM-ELUCID src=v0-50§5.2 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-RES-001 | Provider creates/updates a resource typed to a `service_type` | M | MVP | Planned | [50](50-data-model.md) | v0-50§5.2 |
| PICS-RES-002 | Resource tagged with a PostGIS location for proximity matching | M | MVP | Planned | [50](50-data-model.md) | v0-50§5.2 |
| PICS-RES-003 | Rule/geo matching: nearest capable, available provider for an incident | M | MVP | Planned | [50](50-data-model.md) | v0-50§5.2 |
| PICS-RES-004 | Only the owning provider may modify its resources (RBAC) | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.2 |

### FIL — Files
<!-- IDRM-ELUCID src=v0-50§5.7 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-FIL-001 | Uploads stored in MinIO; DB stores the key/URL, never the blob | M | MVP | Planned | ADR-007 [21](21-architecture-decisions.md) | v0-50§5.7 |
| PICS-FIL-002 | Media rules enforced (≤ 10 MB; resize ≤ 1920 px, ≥ 640×480; blur check) | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.7 |
| PICS-FIL-003 | EXIF / GPS stripped on upload | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.7 |
| PICS-FIL-004 | Emergency "lite" path: one ≤ ~500 KB photo | O | MVP | Planned | [60](60-uidesign-web-interaction.md) | v0-50§5.7 |
| PICS-FIL-005 | Face **detection-only** quality gate; no biometric stored | M | MVP | Planned | ADR-011 [21](21-architecture-decisions.md) | v0-50§5.7 |

### AUD — Audit
<!-- IDRM-ELUCID src=v0-50§5.8 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-AUD-001 | Append-only audit entry written on every significant action | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.8 |
| PICS-AUD-002 | Audit entries are immutable (no in-place update/delete) | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.8 |
| PICS-AUD-003 | Coordinator/admin can query the audit trail | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.8 |

### ADM — Administration
<!-- IDRM-ELUCID src=v0-50§5.3 -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-ADM-001 | Admin-only reference data + disaster-type configuration (RBAC) | M | MVP | Planned | [90](90-governance-and-raci.md) | v0-50§5.3 |
| PICS-ADM-002 | User / role administration | M | MVP | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.1 |
| — | Per-request privacy levels (Public/Protected/Private) | (deferred) | → FFP | NA | [../ffp/26](../ffp/26-conformance-pics.md) | v0-50§5.3 |

### ALR — Alerts
<!-- IDRM-ELUCID src=v0-40§dis -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-ALR-001 | Coordinator issues an area-scoped alert (LOC polygon + severity) | M | MVP | Planned | [60](60-uidesign-web-interaction.md) | v0-40§dis |
| PICS-ALR-002 | Users within the affected area receive the alert (in-app) | M | MVP | Planned | [60](60-uidesign-web-interaction.md) | v0-40§dis |

### RPT — Reports
<!-- IDRM-ELUCID src=v0-40§ana -->

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-RPT-001 | Operational report: incidents by status / type / area | M | MVP | Planned | [90](90-governance-and-raci.md) | v0-40§ana |
| PICS-RPT-002 | Verification / resolution-rate report from audit + live data | M | MVP | Planned | [90](90-governance-and-raci.md) · [13](13-requirements-traceability-matrix.md) | v0-40§ana |
| PICS-RPT-003 | Export (CSV) of operational reports | O | MVP | Planned | [90](90-governance-and-raci.md) | v0-40§ana |

> ✅ **All ten modules now have MVP conformance rows.**

---

## B. Stack / component conformance

| ID | Capability / obligation | Status | Phase | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-STK-FASTAPI-01 | All operations are FastAPI routers under `/api/v1` (versioned, snake_case) | M | MVP | Planned | [20](20-architecture-system.md) · [40](40-api-specification.md) | v0-10§2 |
| PICS-STK-PG-01 | PostgreSQL 16 is the single source of truth; sessions in DB (no Redis) | M | MVP | Planned | ADR-002/005 [21](21-architecture-decisions.md) | v0-10§2 |
| PICS-STK-POSTGIS-01 | Geo columns use SRID 4326 + a GiST spatial index | M | MVP | Planned | [50](50-data-model.md) | v0-10§2 |
| PICS-STK-MINIO-01 | Uploads stored in MinIO; DB stores the key/URL, never the blob | M | MVP | Planned | ADR-007 [21](21-architecture-decisions.md) | v0-10§2 |
| PICS-STK-JWT-01 | Auth = RS256 JWT (access ~60 min + rotating/revocable refresh ~7 d) | M | MVP | Planned | ADR-008 · [22](22-architecture-security-and-iam.md) | v0-10§7 |
| PICS-STK-ALEMBIC-01 | Every schema change ships as an Alembic migration | M | MVP | Planned | [80](80-ops-deployment-and-operations.md) | v0-10§5 |
| PICS-STK-VALID-01 | 3-layer validation: Pydantic schema → service rules → DB constraints | M | MVP | Planned | [30](30-design-data-flow-and-modules.md) · [50](50-data-model.md) | v0-20§6.4 |
| PICS-STK-REPO-01 | Data access only through the repository layer (service never touches the DB directly) | M | MVP | Planned | [20](20-architecture-system.md) · [30](30-design-data-flow-and-modules.md) | v0-20§5.3 |
| PICS-STK-POOL-01 | SQLAlchemy connection pool configured/sized for expected load | O | MVP | Planned | [80](80-ops-deployment-and-operations.md) | v0-20§7.3 |
| PICS-STK-ENUM-01 | Native PostgreSQL enums match the API wire values (lowercase snake_case) | M | MVP | Planned | ADR-013 [21](21-architecture-decisions.md) · [50](50-data-model.md) | v0-50§9 |
| PICS-STK-API-01 | Response standards: lists `{data,pagination}`, singles bare object, error envelope w/ machine `code` | M | MVP | Planned | [40](40-api-specification.md) | v0-40§resp |
| PICS-STK-LOGIC-01 | Business logic in the service layer; DB triggers limited to audit / `updated_at` / integrity | M | MVP | Planned | [20](20-architecture-system.md) · [30](30-design-data-flow-and-modules.md) | v0-51§4 |
| PICS-STK-QUALITY-01 | Code style + type checks enforced: black (format), flake8 (lint), mypy + type hints | M | MVP | Planned | [70](70-quality-test-strategy.md) · [contributor guide](../../guides/mvp/30-contribute-developer-guide.md) | v3-71 |
| PICS-STK-OPENAPI-01 | The OpenAPI spec (`40-api-openapi.yaml`) is validated and matches the implemented API | M | MVP | Planned | [40](40-api-specification.md) | v3-72 |
| PICS-STK-TLS-01 | All traffic served over HTTPS/TLS (reverse-proxy termination) | M | MVP | Planned | [80](80-ops-deployment-and-operations.md) · [22](22-architecture-security-and-iam.md) | v0-10§7 |
| PICS-STK-SECRET-01 | Secrets/credentials from env/config only — never in source, logs, or responses | M | MVP | Planned | [22](22-architecture-security-and-iam.md) · [80](80-ops-deployment-and-operations.md) | v0-10§7 |
| PICS-STK-A11Y-01 | Web UI conforms to **WCAG 2.2 AA** (locked standard, both phases) | M | MVP | Planned | [60](60-uidesign-web-interaction.md) · [13 §4](13-requirements-traceability-matrix.md) | v0-10§16 |
| PICS-STK-HEALTH-01 | Liveness/health-check endpoint for the app service | O | MVP | Planned | [80](80-ops-deployment-and-operations.md) | v0-20§9 |

▷ *More component rows (Leaflet, Uvicorn/systemd, bcrypt, pytest…) pending — see component map [`../../guides/mvp/learn/tech-stack-101.md`](../../guides/mvp/learn/tech-stack-101.md).*

---

*Related:* builder's roadmap [`27-implementation-roadmap.md`](27-implementation-roadmap.md) · elucidation [`25-module-elucidation.md`](25-module-elucidation.md) · scope/acceptance [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) ·
traceability [`13-requirements-traceability-matrix.md`](13-requirements-traceability-matrix.md) · Definition of Done [`../../archive/instructions/definition-of-done.md`](../../archive/instructions/definition-of-done.md) ·
FFP twin [`../ffp/26-conformance-pics.md`](../ffp/26-conformance-pics.md).
