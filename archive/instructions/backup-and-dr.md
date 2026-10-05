# IDRM Instructions — Backup & Disaster Recovery

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Why it matters:** IDRM *is* disaster-response software — losing its own data during a disaster is the
> worst-case failure. Backups are a first-class MVP concern, not a later add-on.

## What must be protected
- **PostgreSQL 16 + PostGIS** (system of record) — the priority.
- **MinIO** object store (incident photos, completion proof) — keys in the DB must match objects in MinIO.
- Config/secrets, migration history (Alembic), and (FFP) etcd (APISIX) + broker state.

## MVP baseline
- **Nightly logical dumps** (`pg_dump`) + **WAL archiving for Point-In-Time Recovery (PITR)**.
- MinIO bucket replication/versioning; verify **DB↔object consistency** (no orphaned keys).
- **Off-host, encrypted** backup copies (native systemd/cron on Ubuntu).
- **Restore drills**: a backup is only real once a **test restore** has succeeded — schedule and record them.

## FFP evolution
- Continuous archiving (e.g. **pgBackRest**), managed/geo-redundant object storage, per-service backup
  ownership, automated cross-region DR, and defined **RPO/RTO** targets per service tier.
- Broker durability (RabbitMQ/Kafka) and stateful-service snapshots enter the plan as those land.

## Rules
- Define and record **RPO** (max acceptable data loss) and **RTO** (max acceptable downtime) per phase.
- **Test restores on a schedule**; document runbooks. Encrypt backups; least-privilege access.

## Canonical docs
- [`../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../idrm-mvp-docs/80-ops-deployment-and-operations.md)
- [`../idrm-ffp-docs/80-ops-platform-and-deployment.md`](../idrm-ffp-docs/80-ops-platform-and-deployment.md)
- Stores: [`data-stores.md`](data-stores.md)

## Trusted external references
- PostgreSQL Backup & PITR — postgresql.org/docs/current/backup.html · pgBackRest — pgbackrest.org
- MinIO bucket replication — min.io/docs · 3-2-1 backup rule (reference) — cisa.gov
- NIST SP 800-34 (Contingency Planning) — csrc.nist.gov · RPO/RTO fundamentals
