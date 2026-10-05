# IDRM MVP — Deployment & Operations

> *Type: Document (specification) · Audience: DevOps, admins, developers · Status: MVP — current*
> *How to install, configure, run, back up, and operate the MVP on a **standalone Ubuntu server** — natively under systemd, no containers. Grounded in the authoritative [`../../docs/07-operations.md`](../../docs/07-operations.md), scoped to the locked MVP stack. Docker/Swarm/Kubernetes, the APISIX gateway, Redis, and the full observability stack are **→ FFP**.*

> **MVP deviations from the finished ops overview** (all follow locked decisions): the MVP has **no Flask/
> Gunicorn** (FastAPI/**uvicorn** serves the API *and* the static HTML UI), **no Redis** (sessions live in
> PostgreSQL), and file storage is **MinIO**. A reverse proxy is used **only** for TLS/static — it is *not*
> the FFP APISIX gateway.

---

## 1. Target server

| Item | Recommendation |
|---|---|
| OS | **Ubuntu 22.04 LTS** (64-bit) |
| CPU / RAM | ~4 vCPU / 16 GB |
| Storage | 500 GB SSD |
| Network | 1 Gbps, static private IP; hostname e.g. `idrm-server.campus.local` |

One app on one machine (modular monolith, ADR-001) — no orchestration.

---

## 2. What runs on the box (systemd services)

| Service | Role | Port |
|---|---|---|
| **uvicorn** (FastAPI app) | Serves the `/api/v1` API **and** the static HTML/Tailwind/JS UI | 8000 (local) |
| **PostgreSQL 16 + PostGIS 3.4** | System of record + geospatial | 5432 (local) |
| **MinIO** | S3-compatible object storage (uploads) | 9000 API / 9001 console (local) |
| **Reverse proxy** (NGINX or Caddy) | **TLS termination** (Let's Encrypt) + static files + forward to uvicorn | 80→443 (public) |

Only the app service is bespoke; PostgreSQL and MinIO are installed by
[`../scripts/setup-idrm-ubuntu.sh`](../../archive/scripts/setup-idrm-ubuntu.sh) (§3). Everything runs under **systemd**
so it starts on boot and restarts on crash.

> **Reverse proxy (MVP):** a public deployment needs HTTPS. Put a **lightweight** proxy in front of uvicorn
> for **TLS + static** only (Caddy = auto-HTTPS single binary; or NGINX + Let's Encrypt, matching the
> authoritative ops doc). This is deliberately minimal — the full gateway (WAF, centralized rate-limiting,
> multi-service routing) is **APISIX → FFP**.

---

## 3. Install

The reproducible installer is [`../scripts/setup-idrm-ubuntu.sh`](../../archive/scripts/setup-idrm-ubuntu.sh)
(idempotent, logs to `~/idrm-setup.log`). It installs and configures:

- **PostgreSQL 16 + PostGIS 3.4** — creates `idrm_db` + `idrm_user`, enables the PostGIS extension.
- **MinIO** (Step 3B) — native systemd service + `mc` client, `minio-user`, `/var/lib/minio`, the
  `idrm-uploads` bucket (S3 :9000 / console :9001).
- **Miniconda** + the `idrm-mvp` env (Python 3.11; FastAPI, SQLAlchemy, GeoAlchemy2, Alembic, boto3, pytest…).

> ⚠️ The script ships **placeholder credentials** (DB + MinIO). **Change them before any non-local use.**
> *(As of 2026-08-16 the script is a **pure-MVP installer** — Bun was removed per ADR-014; the frontend is
> served by FastAPI, no JS runtime.)*

After the script: apply DB schema (§5), configure env (§4), install/enable the reverse proxy, then start the
app service.

---

## 4. Configuration (environment)

All settings and secrets come from **environment variables** (`pydantic-settings`, a git-ignored `.env` —
never in code). Core keys:

```
# Database
DATABASE_URL=postgresql+asyncpg://idrm_user:CHANGE_ME@127.0.0.1:5432/idrm_db
# Object storage (MinIO / S3)
S3_ENDPOINT=http://127.0.0.1:9000
S3_BUCKET=idrm-uploads
S3_ACCESS_KEY=CHANGE_ME
S3_SECRET_KEY=CHANGE_ME
# Auth (RS256 keypair — ADR-008)
JWT_PRIVATE_KEY_PATH=/etc/idrm/jwt_private.pem
JWT_PUBLIC_KEY_PATH=/etc/idrm/jwt_public.pem
ACCESS_TOKEN_TTL_MIN=60
REFRESH_TOKEN_TTL_DAYS=7
# Notifications (SMS/email gateway)
SMS_API_KEY=CHANGE_ME
SMTP_URL=CHANGE_ME
# App
APP_ENV=production
ALLOWED_ORIGINS=https://idrm-server.campus.local
DEFAULT_LANGUAGE=en
```

Config lives under `/etc/idrm/`; logs under `/var/log/idrm/`; backups under `/backups/idrm/`.

---

## 5. Database schema & migrations (Alembic)

- Schema is created/evolved **only** via **Alembic** (ADR-013, [`50-data-model.md`](50-data-model.md) §9):
  ```bash
  conda activate idrm-mvp
  alembic upgrade head      # baseline: PostGIS extension → enums → 13 tables → indexes → triggers
  ```
- Each change is a new revision; applied migrations are never edited. A rollback is `alembic downgrade -1`.
- A first admin user is seeded by an idempotent data migration (or a one-off script).

---

## 6. Run (start / stop)

- Services are managed by **systemd**:
  ```bash
  sudo systemctl status  postgresql minio idrm        # health
  sudo systemctl restart idrm                          # the FastAPI/uvicorn app
  sudo journalctl -u idrm -e                            # app logs
  ```
- The `idrm` unit runs uvicorn (e.g. `uvicorn app.main:app --host 127.0.0.1 --port 8000`), fronted by the
  reverse proxy on 443. On crash, systemd restarts it.

---

## 7. Network & hardening

| Port | Use |
|---|---|
| 22 | SSH — key-based admin only |
| 80 | HTTP → redirects to HTTPS |
| 443 | HTTPS — web & API |
| others | **blocked (UFW)** — PostgreSQL/MinIO/uvicorn bind to localhost only |

- **UFW** firewall (above) · **SSH keys** (no password login) · **Fail2Ban** · **Let's Encrypt** TLS with
  auto-renewal · secrets in `.env` · regular OS/patch updates. (App-level authN/authZ, audit, and rate
  limits are in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).)

---

## 8. Health & logging

- **Health:** `GET /health` (liveness + version); ops checks also cover DB connectivity, MinIO liveness,
  disk/inodes, and SSL expiry.
- **Logging:** structured JSON app logs to `/var/log/idrm/`; access logs at the proxy; the audit trail
  (`audit_logs`) provides the accountability record.
- **SLO targets (MVP):** availability ≥ 99.5%; API p95 < 800 ms; error rate < 1%. *(A full
  Prometheus/Grafana/Loki stack is → FFP; the MVP watches logs + health + basic host metrics.)*

---

## 9. Backup & disaster recovery

For a disaster-response platform, resilience is non-negotiable — follow the **3-2-1 rule** (3 copies, 2
media, 1 off-site) and **test restores**.

| Component | What | Frequency | Retention | Tool |
|---|---|---|---|---|
| Database | `pg_dump` (full) + WAL | daily + continuous | 30 days | `pg_dump`/`pg_basebackup`; the script's `backup-db.sh` |
| Object storage (MinIO) | `idrm-uploads` bucket | daily | 30 days | `mc mirror` to off-site/NAS |
| App config | `.env`, `/etc/idrm`, unit files | daily | 30 days | `rsync`/`tar` |
| System | firewall, crontab, keys | weekly | 12 weeks | `rsync`/`tar` |

- **RPO / RTO (MVP target):** database & web ~1 h / ~2 h; files ~4 h / ~4 h.
- **Restore is tested** (a backup is only as good as its last successful restore); `restore-db.sh` is
  provided. Encrypt off-site copies.
- **DR runbook:** detect → assess → recover (restore DB + files, redeploy app) → validate (`/health`, a smoke
  journey) → communicate → review.

---

## 10. Deferred → FFP

Docker → Swarm/Kubernetes · CI/CD delivery pipeline · **APISIX** gateway (TLS/WAF/rate-limit/routing) ·
Redis cache/sessions · brokers & background workers · full **Prometheus/Grafana/Loki/Tempo** observability ·
managed **AWS** variant (RDS/S3/ElastiCache) · multi-node HA & automated failover. See the
[FFP charter](../ffp/prompts/instructions_idrm_ffp_docs.md).

---

*Related:* [`20-architecture-system.md`](20-architecture-system.md) · [`50-data-model.md`](50-data-model.md) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) · [`25-module-elucidation.md`](25-module-elucidation.md) ·
[`26-conformance-pics.md`](26-conformance-pics.md) · [`../scripts/setup-idrm-ubuntu.sh`](../../archive/scripts/setup-idrm-ubuntu.sh) ·
[`../../docs/07-operations.md`](../../docs/07-operations.md). Plan: [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).
