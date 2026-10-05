# Operations Runbook (MVP · Ubuntu)

> **⚠️ Stack note (ADR-012):** MVP view layer = FastAPI-served HTML+Tailwind+JS+Leaflet (not Flask/Jinja/Bootstrap); no Redis (sessions in Postgres) + MinIO for files; where this file says Flask/Bootstrap/Redis, defer to [`../mvp/`](../mvp/) and [`../99-decisions-and-history.md`](../99-decisions-and-history.md) (ADR-012).

> **Part of:** IDRM Documentation · `deep-dive/15-ops-runbook.md`
> **Answers:** Step by step, how do I set up, deploy, back up, and recover IDRM on a standalone Ubuntu server?
> **Source posters:** Posters 28 (Deployment), 29 (Observability), 30 (Disaster Recovery). Deepens
> [`../07-operations.md`](../07-operations.md).
> **Standards:** operational runbook · native systemd (Docker Compose optional)
> **Audience:** DevOps / SRE / System administrators · **Depth:** Deep
> **Status:** Draft

---

## 1. Prerequisites

- **Server:** Ubuntu 22.04 LTS (64-bit), ~4 vCPU, 16 GB RAM, 500 GB SSD, static private IP, hostname
  e.g. `idrm-server.campus.local`.
- **Access:** SSH key-based admin account with sudo.
- **Open ports (UFW):** 22 (SSH, admin only), 80 (HTTP→HTTPS), 443 (HTTPS). All others blocked.

> This runbook uses **native systemd** services. **Docker Compose** is an equally valid packaging option and
> follows the same setup/backup/restore logic.

---

## 2. Initial server setup

1. **Update & harden the OS**
   - `sudo apt update && sudo apt upgrade -y`
   - Configure **UFW** (allow 22/80/443, deny the rest); install **Fail2Ban**; disable SSH password login.
2. **Install services**
   - **PostgreSQL + PostGIS**, **Redis**, **NGINX**.
   - **Python 3.12** environment via **Miniconda** (includes the GDAL/GIS toolchain).
3. **Create directories & user**
   - Service user (e.g. `idrm`); data paths: `/var/lib/postgresql`, `/data` (object/file storage),
     `/var/log/idrm`, `/etc/idrm`, `/backups/idrm`.
4. **TLS**
   - Issue certificates with **Let's Encrypt** (Certbot) and enable auto-renewal.

---

## 3. Deploy the application

1. **Get the code & environment**
   - Clone the repo; create the Conda environment from `environment.yml`; install dependencies.
2. **Configure**
   - Create `/etc/idrm/.env` (database URL, Redis URL, secret keys, storage path) — never commit secrets.
3. **Database**
   - Create the database and enable PostGIS; run **Alembic** migrations; load reference/seed data as needed.
4. **Run as services (systemd)**
   - **Gunicorn** → Flask web UI; **Uvicorn** → FastAPI APIs; enable auto-restart (`Restart=always`).
   - Background jobs/scheduler run in-process (threading / APScheduler).
5. **Reverse proxy**
   - Configure **NGINX** to terminate TLS, serve static files, and forward to the app; reload NGINX.
6. **Verify**
   - Health endpoint returns OK; web UI and `/docs` (Swagger) load over HTTPS.

**Zero-downtime update:** pull new code → run migrations → restart the app service → smoke-test → keep or
**roll back** (previous release + `Restart`).

---

## 4. Backups (cron)

Schedule with `cron` (align to the plan in [`../07-operations.md`](../07-operations.md) §4.1):

```
# Daily incremental DB backup (02:00)
0 2 * * *  /usr/local/bin/backup_db_incremental.sh
# Weekly full DB backup (Sun 03:00)
0 3 * * 0  /usr/local/bin/backup_db_full.sh
# Daily files/object-storage backup (01:00)
0 1 * * *  /usr/local/bin/backup_files.sh
# Weekly config backup (Sun 04:00)
0 4 * * 0  /usr/local/bin/backup_configs.sh
```

- **Tools:** `pg_dump` / `pg_basebackup` (database), `borgbackup` / `restic` / `rsync` (files/configs).
- **3-2-1 rule:** 3 copies, 2 media types, 1 off-site. Encrypt backups; monitor backup jobs; keep logs.
- **Retention:** DB 30 days, configs 12 weeks, off-site weekly/monthly (see §4.1 of `07-operations`).

---

## 5. Restore checklist

1. Stop application services.
2. Restore data / files from the chosen backup.
3. Restore the database (with WAL logs for point-in-time, if used).
4. Restore configurations (`/etc/idrm`, NGINX, systemd units).
5. Start services.
6. Validate health & functionality (health endpoint, key workflows, map, logins).

**Confirm success:** services available within **RTO**; data loss within **RPO** (see targets in
`07-operations` §4.2).

---

## 6. Routine operations

- **Health checks:** app `/health`, database connectivity, disk/inodes, SSL expiry, dependency uptime.
- **Observability:** Prometheus + Grafana (metrics), Loki/ELK (logs), Tempo/OpenTelemetry (traces),
  Alertmanager (alerts) — see [`../07-operations.md`](../07-operations.md) §3 and the alerting playbook.
- **Patching:** apply OS and dependency updates regularly; review after changes.
- **DR drills:** full restore **quarterly**; failover drill **semi-annually**; review RPO/RTO **annually**.

---

## 7. Traceability

This runbook operationalises the requirements in [`10-srs.md`](10-srs.md) (NFR-AVL/REL) and the design in
[`11-architecture-and-design.md`](11-architecture-and-design.md) §7 (deployment view).

---

*Note: an MVP single-server runbook — harden the server, keep software updated, monitor continuously, and test
backups regularly.*
