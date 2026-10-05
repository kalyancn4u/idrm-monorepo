# Backup & Restore 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/operators · Status: MVP — current · Track: Operations (#37)*
> *IDRM is disaster-response software — losing **its own** data during a disaster is the worst failure imaginable.
> This guide explains backups from scratch and IDRM's day-one approach. (Deeper strategy: the
> [backup & DR spoke](../../instructions/backup-and-dr.md).)*

---

## 1. Why backups are a day-one concern

Hardware fails, humans delete the wrong thing, software has bugs, and disasters damage infrastructure. A
**backup** is a separate copy of your data you can restore from when the original is lost or corrupted. For most
apps this is prudent; for IDRM it's *mission-critical* — the data is people's active help requests.

**The golden truth:** *a backup you have never restored is not a backup — it's a hope.* Restore testing is part
of backup, not an optional extra.

---

## 2. What must be protected in IDRM

- **PostgreSQL + PostGIS** — the system of record (every incident, user, resource). **Top priority.**
- **MinIO** object store — uploaded photos and completion proofs. The DB holds only the *keys*; the files
  themselves live here, so both must be backed up **and stay consistent** (no key pointing at a missing file).
- **Configuration & secrets** and the **migration history** (Alembic) — so you can rebuild the environment.

---

## 3. Key terms

- **Full backup** — a complete copy at a point in time.
- **Incremental** — only what changed since the last backup (smaller, faster).
- **RPO (Recovery Point Objective)** — how much data you can afford to lose, in time (e.g. "at most 1 hour").
- **RTO (Recovery Time Objective)** — how fast you must be back up (e.g. "within 2 hours").
- **PITR (Point-In-Time Recovery)** — restoring the database to an *exact moment* (e.g. just before a bad
  deletion), by replaying its change log.

RPO and RTO turn "back up often" into concrete, testable targets.

---

## 4. IDRM's MVP approach

- **PostgreSQL:** nightly logical dumps with `pg_dump`, **plus WAL archiving** for PITR. *(WAL = Write-Ahead Log,
  Postgres's running record of every change — replaying it enables point-in-time restore.)*

```bash
pg_dump idrm_db > idrm_db_2026-08-14.sql        # a logical backup
psql idrm_db < idrm_db_2026-08-14.sql           # restore it
```

- **MinIO:** bucket versioning/replication; verify **DB ↔ object consistency** (every DB key has its file).
- **Off-host & encrypted:** copies are stored **off the server** and encrypted — a backup sitting only on the
  failed machine is worthless.
- **Scheduled restore drills:** regularly restore into a scratch environment and confirm it works. Document the
  runbook.

---

## 5. Backup vs. Disaster Recovery

- **Backup** = the copies of data.
- **Disaster Recovery (DR)** = the whole plan to get the *service* running again after a major failure (backups +
  spare infrastructure + runbooks + defined RPO/RTO). Backup is a building block of DR.

FFP extends this to continuous archiving (e.g. **pgBackRest**), geo-redundant storage, and automated cross-region
DR — see the [backup & DR spoke](../../instructions/backup-and-dr.md). *Disaster Recovery 101* (FFP) goes deeper.

---

## 6. Mastery check

1. Explain why backups are mission-critical for IDRM specifically.
2. State the golden truth about untested backups.
3. Define **RPO**, **RTO**, and **PITR**.
4. List what IDRM backs up and why DB↔object consistency matters.
5. Distinguish **backup** from **disaster recovery**.

---

## 7. Go deeper

- PostgreSQL Backup & PITR — postgresql.org/docs/current/backup.html · pgBackRest — pgbackrest.org
- MinIO replication — min.io/docs · NIST SP 800-34 (contingency planning) — csrc.nist.gov
- IDRM: [`../../instructions/backup-and-dr.md`](../../instructions/backup-and-dr.md) · [`../../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../../idrm-mvp-docs/80-ops-deployment-and-operations.md)
- Related: [Linux 101](linux-101.md) · [PostgreSQL / PostGIS 101](postgresql-postgis-101.md)

---
*Next:* Role-mastery guides / FFP-only 101s (see [Learning Paths §5](../00-start-learning-paths.md)) · *Up:* [Learning Paths](../00-start-learning-paths.md)
