# Operations — How We Run It

> **Part of:** IDRM Documentation · `07-operations.md`
> **Answers:** How is IDRM deployed, watched, and kept running on a standalone Ubuntu server?
> **Source posters:** Posters 28–30 (Phase 7 Operations)
> **Audience:** Operators & DevOps/SRE (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

1. [Deployment on Ubuntu](#1-deployment-on-a-standalone-ubuntu-server) — the primary target.
2. [How it runs](#2-how-it-runs) — the processes and how they're kept alive.
3. [Observability](#3-observability) — logs, metrics, traces, alerts.
4. [Disaster recovery](#4-disaster-recovery) — backup, restore, failover, RPO/RTO.
5. [AWS appendix](#5-appendix--aws-variant) — a future cloud variant.

---

## 1. Deployment on a standalone Ubuntu server

IDRM's primary home is a **single standalone Ubuntu server** — well suited to an enterprise or academic
campus, on-premises. Because IDRM is one application, the whole system fits comfortably on one machine.

```
                 Users (browser · mobile · API clients)
                                  │  HTTPS
                                  ▼
        ┌──────────────── Ubuntu Server ────────────────┐
        │                                                │
        │   NGINX  (reverse proxy · TLS · static files)  │
        │      │                                         │
        │      ▼                                         │
        │   IDRM application                             │
        │     • Gunicorn → manages Uvicorn workers       │
        │     • Uvicorn  → FastAPI app (UI + APIs)       │
        │     • in-process background jobs & scheduler   │
        │      │                                         │
        │      ▼                                         │
        │   PostgreSQL + PostGIS      MinIO (files)      │
        │   File / object storage                        │
        │                                                │
        │   UFW firewall · systemd services · backups    │
        └────────────────────────────────────────────────┘
```

**The building blocks:**

| Piece | Role on the server |
|---|---|
| **NGINX** | Front door — terminates HTTPS/TLS, serves static files, forwards requests. |
| **Gunicorn** | Process manager for the FastAPI app (manages Uvicorn workers). |
| **Uvicorn** | ASGI server running the single FastAPI app (web UI + APIs). |
| **PostgreSQL + PostGIS** | The database, with map/location support (also holds sessions). |
| **MinIO** | S3-compatible object storage for uploaded files. *(No Redis in the MVP.)* |
| **UFW** | The firewall — only necessary ports are open. |
| **systemd** | Starts services at boot and restarts them if they stop. |

> **Packaging note.** For the MVP, services run **natively under systemd** (Gunicorn/Uvicorn for the FastAPI app,
> PostgreSQL, MinIO). **Docker Compose** is an equally valid packaging option and is the expected path as the deployment
> grows — an additive change, not a redesign (see [`99-decisions-and-history.md`](99-decisions-and-history.md)).

### 1.1 Server specification (recommended)

| Item | Recommendation |
|---|---|
| **OS** | Ubuntu 22.04 LTS (64-bit) |
| **CPU** | ~4 vCPU (Intel/AMD) |
| **RAM** | 16 GB |
| **Storage** | 500 GB SSD or higher |
| **Network** | 1 Gbps, static private IP |
| **Hostname** | e.g. `idrm-server.campus.local` |

### 1.2 Network & ports

Only the required inbound ports are open (via **UFW**); everything else is blocked. All traffic is HTTPS
(TLS 1.2+).

| Port | Use |
|---|---|
| **22** | SSH — admin access only (key-based) |
| **80** | HTTP — redirects to HTTPS |
| **443** | HTTPS — web & API |
| *all others* | Blocked |

### 1.3 Data & volume layout

| Path | Contents |
|---|---|
| `/var/lib/postgresql` | Database (PostgreSQL + PostGIS) |
| `/data/…` (or MinIO) | Object / file storage (uploads, media) |
| `/var/log/idrm` | Application & access logs |
| `/etc/idrm` | Configuration |
| `/backups/idrm` | Local backups |

### 1.4 Hardening

- **SSH key-based** access (no password login); **Fail2Ban** for brute-force protection.
- **UFW firewall** (ports above); **Let's Encrypt** for SSL/TLS with auto-renewal.
- **Secrets** in environment files (`.env`), never in code; **regular updates & patch management**.

---

## 2. How it runs

- **Managed services.** The application, database, and cache run as **systemd** services, so they start
  automatically on boot and recover if they crash.
- **One deployment unit.** Because IDRM is a modular monolith, "deploying" means updating one application —
  no orchestration of many services.
- **Configuration by environment.** Production settings and secrets live in environment files, never in code.
- **Predictable footprint.** A single, appropriately-sized server handles the MVP's load; capacity is grown
  by scaling the server up first, and out later only when measured load requires it.

---

## 3. Observability

You can't run what you can't see. IDRM is built to be observable across four signals:

| Signal | What it tells you | Tooling |
|---|---|---|
| **Logs** | What happened (structured JSON with correlation IDs). | Filebeat → Loki or Elasticsearch; Kibana/Grafana |
| **Metrics** | How the system performs (throughput, latency, resources). | Prometheus (+ node/cAdvisor/postgres/nginx exporters); Grafana |
| **Traces** | A request's path, to find slow spots. | OpenTelemetry Collector → Tempo; Grafana |
| **Alerts** | Automatic warnings on thresholds. | Alertmanager → email / SMS / webhook |

### 3.1 Service-level targets (SLO/SLA)

| Objective | Target |
|---|---|
| Availability (uptime) | ≥ 99.5% |
| API latency (p95) | < 800 ms |
| Error rate | < 1% |
| Incident acknowledgement | < 5 min |
| P1 incident resolution | < 1 hr |

### 3.2 Data retention (recommended)

| Data | Retention |
|---|---|
| Logs (hot / warm) | 7–14 days / 30–90 days |
| Metrics (raw / downsampled) | 15–30 days / 1–2 years |
| Traces | 7–14 days |
| Alerts | 90 days |

### 3.3 Alerting playbook (examples)

| Alert | Condition | Severity | Action |
|---|---|---|---|
| High CPU | > 85% for 5 min | Warning | Scale / investigate |
| Disk space low | < 15% free | Critical | Clean up / expand |
| Service down | Unreachable 2 min | Critical | Restart / failover |
| High error rate | 5xx > 5% for 5 min | Critical | Investigate / rollback |
| High latency | p95 > 1 s | Warning | Investigate |

**On-call & escalation:** alert triggered → on-call engineer → secondary → manager. **Health checks** cover
app `/health`, database connectivity, disk/inodes, SSL expiry, and dependency uptime. Audit logs from
[`05-security.md`](05-security.md) also feed this picture.

---

## 4. Disaster recovery

For a disaster-response platform, resilience is non-negotiable. IDRM plans for failure and recovery:

| Element | Meaning | Approach |
|---|---|---|
| **Backup** | Regular copies of the database and files. | Scheduled backups (e.g. hourly → daily → weekly → monthly), kept locally and, optionally, off-site. |
| **Restore** | Bringing data back from a backup. | Tested restore procedure — a backup is only as good as its last successful restore. |
| **Failover** | Continuing service after a failure. | Standby/recovery procedures; grows into redundancy as the deployment scales. |
| **RPO** — Recovery Point Objective | How much recent data you can afford to lose. | Set by backup frequency — the more frequent, the smaller the possible loss. |
| **RTO** — Recovery Time Objective | How quickly you must be back up. | Set by the restore/failover procedure. |

### 4.1 Backup plan

| Component | What | Frequency | Retention | Location |
|---|---|---|---|---|
| Database (PostgreSQL/PostGIS) | Full + WAL logs | Daily + continuous | 30 days | Local + off-site |
| Application code & configs | Source, `.env`, configs | Daily | 30 days | Local + off-site |
| User uploads / files | Documents, media | Daily | 30 days | Local + off-site |
| System & OS | Key configs, crontab, firewall rules | Weekly | 12 weeks | Local + off-site |
| Logs | Application & access logs | Daily | 30 days | Local |

### 4.2 RPO / RTO targets (example)

| Service | RPO | RTO | Priority |
|---|---|---|---|
| Web application | 1 hr | 2 hr | High |
| Database | 1 hr | 2 hr | High |
| File storage | 4 hr | 4 hr | Medium |
| Logs & monitoring | 24 hr | 24 hr | Low |

### 4.3 DR runbook (high level)

**Detect → Assess impact → Decide failover → Recover systems → Validate → Communicate → Review & improve.**

### 4.4 Practices & tools

- **3-2-1 rule:** 3 copies, 2 media types, 1 off-site. Encrypt backups; monitor and **test restores**.
- **Testing cadence:** full restore test **quarterly**; failover drill **semi-annually**; review RPO/RTO annually.
- **Tools:** `pg_dump` / `pg_basebackup`, `borgbackup` / `restic`, `rsync` / `tar`, `cron` for scheduling.
- **Off-site options:** external/NAS, cloud (S3 / Glacier), or another campus.

Backups are stored so a single machine failure never means lost data. As the deployment grows, redundancy and
faster failover are added — an additive step, not a redesign.

---

## 5. Appendix — AWS variant

The same application can run in the cloud when that fits an organisation better. On **AWS**, the on-server
pieces map to managed equivalents (for example: a load balancer in front, managed PostgreSQL/PostGIS, managed
object storage (S3) for files, cloud monitoring, and managed Redis *if* introduced at scale — Redis is not in the
MVP). This is a **future variant**, documented so the path
is clear; the standalone Ubuntu deployment remains the primary target for the MVP. A detailed cloud runbook is
part of the later deep pass.

---

## Where this leads

- Who owns operations and on-call → [`08-organization.md`](08-organization.md)
- How the system is secured and audited → [`05-security.md`](05-security.md)
- The data being backed up → [`04-data.md`](04-data.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"Reliable operations. Prepared for the worst, built to keep serving."*
