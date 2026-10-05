# IDRM FFP — Conformance Checklist (PICS-style · DELTA)

> ✅ **SIGNED OFF 2026-08-16** (task-I gate) — approved alongside the MVP twin. 32 trigger-gated delta rows.

> *Type: Document (conformance / normative · DELTA on the MVP) · Audience: builders, reviewers, QA · Status: FFP — trigger-gated*
> *The FFP counterpart of [`../mvp/26-conformance-pics.md`](../mvp/26-conformance-pics.md): only the **added** obligations,
> each **trigger-gated** and each preserving the frozen `/api/v1` contract. Informative twin:
> [`25-module-elucidation.md`](25-module-elucidation.md). Grown document-wise from the `_removed` cleanup (ledger:
> [`../../archive/_removed/_CLEANUP-LEDGER.md`](../../archive/_removed/_CLEANUP-LEDGER.md)).*

---

## How to read a PICS row (FFP)

Same columns as the MVP sheet, plus every row is **conditional on a trigger** (scale / ownership / performance /
reliability). **Status:** M = mandatory *once the trigger fires* · O = optional · C = conditional. **Supported:**
Planned until the FFP work begins. Read the MVP sheet first — the FFP only **adds**.

---

## A. Module conformance (delta)

### INC — Incidents (FFP delta)
<!-- IDRM-ELUCID src=v0-10§4.4 src=v0-10§3.2 -->

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-INC-F01 | Add `disputed` state + appeal/evidence rules | M | workflow-richness | Planned | [25](25-module-elucidation.md) · [11](11-requirements-scope-and-roadmap.md) | v0-10§4.4 |
| PICS-INC-F02 | Add auto-close on defined conditions | O | ops-scale | Planned | [11](11-requirements-scope-and-roadmap.md) | v0-10§4.4 |
| PICS-INC-F03 | Emit versioned domain events on state change (outbox → broker) | M | events/real-time | Planned | [81 §3](81-ops-messaging-and-async.md) | v0-10§4.4 |
| PICS-INC-F04 | Deep real-time push of incident updates to web/mobile | M | real-time | Planned | [81](81-ops-messaging-and-async.md) | v0-10§4.6 |
| PICS-INC-F05 | Extract incidents as a microservice behind APISIX, same paths | C (extraction trigger) | scale/ownership | Planned | [20](20-architecture-system.md) | v0-10§3.2 |
| PICS-INC-F06 | Public `/api/v1` incident paths unchanged (add-only) | M | always | Planned | [40](40-api-specification.md) | v0-10§6 |

### USR — Users (FFP delta)
<!-- IDRM-ELUCID src=v0-20§3.2 src=v0-20§6.2 -->

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-USR-F01 | Extract auth as the **first** microservice behind APISIX (same paths) | M | ownership / pattern | Planned | [20](20-architecture-system.md) | v0-20§3.2 |
| PICS-USR-F02 | Add OIDC / SSO login | M | federation | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.2 |
| PICS-USR-F03 | Add MFA (multi-factor) | M | assurance | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.2 |
| PICS-USR-F04 | Add ABAC + full role hierarchy + **Auditor** | M | fine-grained authz | Planned | [22](22-architecture-security-and-iam.md) | v0-20§6.3 |

### LOC — Locations (FFP delta)

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-LOC-F01 | Add disaster-event entity + live **Common Operational Picture** | O | national COP | Planned | [25](25-module-elucidation.md) | v0-20§3.4 |
| — | Python GeoPandas/Shapely geospatial service | — | heavy geo | Planned | see `PICS-STK-GEO-F01` | v0-20§3.4 |

### NTF — Notifications (FFP delta)
<!-- IDRM-ELUCID src=v0-20§3.5 -->

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-NTF-F01 | Broker-backed **deep real-time push** (websockets/SSE + workers) | M | real-time | Planned | [81](81-ops-messaging-and-async.md) | v0-20§3.5 |
| PICS-NTF-F02 | Multi-channel intake/out (SMS / email / push) | O | reach | Planned | [81](81-ops-messaging-and-async.md) | v0-20§3.5 |

### RES — Resources (FFP delta)

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-RES-F01 | AI-assisted incident↔resource matching | O | matching quality | Planned | [25](25-module-elucidation.md) | v0-50§5.2 |
| PICS-RES-F02 | Per-service ownership of resource data | C (extraction) | ownership | Planned | [50](50-data-model.md) | v0-50§5.2 |

### FIL — Files (FFP delta)
<!-- IDRM-ELUCID src=v0-50§5.7 -->

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-FIL-F01 | FaceNet recognition/matching (**consent-gated**, DPDP) | O | identity matching | Planned | ADR-011 / FFP-ADR-014 · [22](22-architecture-security-and-iam.md) | v0-50§5.7 |
| PICS-FIL-F02 | Distributed MinIO / cloud S3 | C (scale) | scale | Planned | [80](80-ops-platform-and-deployment.md) | v0-50§5.7 |

### AUD — Audit (FFP delta)

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-AUD-F01 | Cross-service audit aggregation + **Auditor** role | M | multi-service | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.8 |
| PICS-AUD-F02 | Zero-trust controls | O | security posture | Planned | [22](22-architecture-security-and-iam.md) | v0-50§5.8 |

### ADM — Administration (FFP delta)
<!-- IDRM-ELUCID src=v0-50§5.3 -->

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-ADM-F01 | Per-request **privacy levels** (Public/Protected/Private) | M | privacy | Planned | [25](25-module-elucidation.md) | v0-50§5.3 |
| PICS-ADM-F02 | Disaster-**event** entity + national rollout + full localization | O | scale/reach | Planned | [25](25-module-elucidation.md) | v0-50§5.3 |

### ALR — Alerts (FFP delta)

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-ALR-F01 | Multi-channel alert broadcast (SMS/email/push) + event fan-out | O | reach / scale | Planned | [81](81-ops-messaging-and-async.md) | v0-40§dis |

### RPT — Reports (FFP delta)

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-RPT-F01 | Advanced analytics + dashboards (BI) | O | analytics | Planned | [25](25-module-elucidation.md) | v0-40§ana |
| PICS-RPT-F02 | DORA / ops metrics | O | ops maturity | Planned | [80](80-ops-platform-and-deployment.md) | v0-40§ana |

> ✅ **All ten modules now have FFP conformance deltas.**

---

## B. Stack / component conformance (delta)

| ID | Added capability / obligation | Status | Trigger | Supported | Evidence | src |
|---|---|---|---|---|---|---|
| PICS-STK-APISIX-F01 | APISIX gateway fronts services (routing, auth, rate-limit, TLS, WAF) | M | >1 service | Planned | [20](20-architecture-system.md) · `api-gateway` spoke | v0-10§2, §8 |
| PICS-STK-REDIS-F01 | Redis for cache / rate-limit / first-step streams (not sessions) | O | perf/scale | Planned | [81](81-ops-messaging-and-async.md) | v0-10§14 |
| PICS-STK-BROKER-F01 | RabbitMQ/Kafka for durable async + high-volume events | M | async/scale | Planned | [81](81-ops-messaging-and-async.md) | v0-10§2 |
| PICS-STK-K8S-F01 | Docker → Kubernetes for scale/HA (from native systemd) | C (scale trigger) | scale/HA | Planned | [80](80-ops-platform-and-deployment.md) | v0-10§8 |
| PICS-STK-GEO-F01 | Python GeoPandas/Shapely geospatial service (not GeoServer) | O | heavy geoprocessing | Planned | [20 §6.2](20-architecture-system.md) | v0-10§2 |
| PICS-STK-OTEL-F01 | Distributed tracing (OpenTelemetry) + metrics (Prometheus) across services | M | >1 service | Planned | [80](80-ops-platform-and-deployment.md) | v0-20§9 |
| PICS-STK-CLIENT-F01 | React web + React Native/Expo clients on the same `/api/v1` | O | client reach | Planned | [60](60-uidesign-frontend.md) · [61](61-frontend-engineering-standards.md) | v1-30§fsd |
| PICS-STK-POLY-F01 | Polyglot service runtimes (Java/Go/JS + Python for DS/ML), per-service | O | scale/perf | Planned | [20](20-architecture-system.md) | v0-10§2 |

▷ *Component coverage now includes gateway, cache, broker, orchestration, geo, observability, clients, polyglot.*

---

*Related:* MVP baseline [`../mvp/26-conformance-pics.md`](../mvp/26-conformance-pics.md) · elucidation [`25-module-elucidation.md`](25-module-elucidation.md) ·
roadmap/triggers [`11-requirements-scope-and-roadmap.md`](11-requirements-scope-and-roadmap.md) · messaging [`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md).
