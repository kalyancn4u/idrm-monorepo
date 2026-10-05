# IDRM FFP — Operations & Platform (Containers, Orchestration, Observability, HA)

> *Type: Document (specification) · Audience: DevOps/SRE, admins · Status: FFP — next-phase (planned)*
> *Extends the MVP ops doc [`../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../mvp/80-ops-deployment-and-operations.md). Adds **containers, orchestration, CI/CD, full observability, HA, and a cloud variant**. Consolidates `v3/80-ops-ci-cd.md`, `v2/80-ops-ci-cd.md`, `v0/*devops*`, and `../../docs/07-operations.md` §5. (v1 CI/CD + setup notes were consolidated, then v1 retired → `_removed/`.)*

> **Invariant:** the MVP's **native-systemd Ubuntu** deploy stays valid as the entry point. The FFP
> **containerises and orchestrates** as scale/HA demands (FFP-ADR-007) — additive, not a redesign.

> **FFP acronyms (expanded once):** **CI/CD** = Continuous Integration / Continuous Delivery (automated
> build-test-deploy) · **K8s** = Kubernetes · **HA** = High Availability · **IaC** = Infrastructure as Code ·
> **OTel** = OpenTelemetry (tracing/metrics standard) · **SLO / SLI** = Service-Level Objective / Indicator
> (reliability targets + their measurements) · **DR / RPO / RTO** = Disaster Recovery / Recovery-Point Objective
> (max data loss) / Recovery-Time Objective (max downtime).

---

## 1. Packaging & orchestration

| Stage | Approach | Trigger |
|---|---|---|
| MVP | native **systemd** on Ubuntu | baseline |
| FFP-1 | **Docker** images per service; **Docker Compose** | reproducible multi-service local/staging |
| FFP-2 | **Docker Swarm** | simple multi-node HA |
| FFP-3 | **Kubernetes** | autoscaling, rolling deploys, large fleets |

## 2. CI/CD pipeline
`commit → lint/unit → SAST/SCA → build → SBOM/artifact-scan → integration → staging → E2E/UAT → approval →
production` (GitHub Actions). Protected main, dependency pinning, migration testing, **rollback** strategy,
artifact provenance. Per-service pipelines + contract tests gate cross-service releases.

## 3. Observability stack
Full four-signal observability (MVP watched logs+health; FFP adds the stack):

| Signal | Tooling |
|---|---|
| Metrics | **Prometheus** + exporters → **Grafana** |
| Logs | structured JSON → **Loki** (or ELK) |
| Traces | **OpenTelemetry** → **Tempo** |
| Domain health | active/critical incidents, unacked/overdue tasks, responder availability, GIS freshness, notification failures, resolution time |
| Alerts | Alertmanager → email/SMS/webhook; on-call escalation |

## 4. HA, scaling & DR
- **HA:** no single point of failure — multiple service replicas, gateway/DB/broker redundancy.
- **Scale:** horizontal autoscaling of hot paths; PostgreSQL read replicas; Redis/broker scaling.
- **DR:** tighter RTO/RPO than MVP; tested restore + failover drills; the MVP's 3-2-1 backup extended
  per-service; distributed MinIO/cloud S3.

## 5. Environments & network
`LOCAL → DEV → TEST → STAGING → PRODUCTION`, each with documented network/DNS/TLS/secrets/DB/storage/
scaling/deploy-strategy/rollback. Zero-trust network segmentation; secrets from vault/KMS.

## 6. Cloud variant (AWS)
On-server pieces map to managed equivalents: ALB/API-gateway, **RDS** (PostgreSQL/PostGIS), **ElastiCache**
(Redis), **S3** (objects), **MSK** (Kafka), EKS (Kubernetes), CloudWatch/managed-Grafana. The **standalone
Ubuntu** deploy remains a supported target; cloud is an option, not a requirement.

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`20-architecture-system.md`](20-architecture-system.md) · [`70-quality-test-strategy.md`](70-quality-test-strategy.md) ·
[`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md) · MVP ops [`../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../mvp/80-ops-deployment-and-operations.md) ·
[`../../docs/07-operations.md`](../../docs/07-operations.md).
