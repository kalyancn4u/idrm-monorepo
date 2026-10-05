# IDRM Instructions — Data Stores (engines & ops)

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> Schema/modeling lives in [`data-modeling.md`](data-modeling.md); this spoke = which engines, and running them.

## System of record — LOCKED (MVP + FFP)
- **PostgreSQL 16 + PostGIS 3.4** is the **sole source of truth**. It is **never replaced** — FFP adds
  services around it, not instead of it. Per-service data ownership arrives in FFP, PostGIS stays authoritative.
- **MinIO (S3-compatible)** = object storage for uploads (incident photos, completion proof) — **IN the MVP**.
  The DB stores only **keys/URLs, never blobs**. FFP: MinIO → managed S3-compatible at scale.

## Phase-in of additional stores (FFP, on a trigger)
- **Redis** (+ Redis Streams): cache / sessions-at-scale / light queues — see [`caching-messaging.md`](caching-messaging.md).
  (MVP keeps sessions in Postgres; **no Redis in MVP**.)
- Durable eventing (RabbitMQ / Kafka), search, time-series, etc.: only when a concrete trigger justifies it.

## Operations
- Migrations: **Alembic** (never hand-edit schema). Backups/PITR & DR: [`backup-and-dr.md`](backup-and-dr.md).
- Connection pooling, read replicas, partitioning: FFP scale concerns, documented as they land.
- Deploy: native **systemd on Ubuntu** (MVP); Docker→K8s is FFP.

## Canonical docs
- [`../idrm-mvp-docs/50-data-model.md`](../idrm-mvp-docs/50-data-model.md) ·
  [`../idrm-ffp-docs/50-data-model.md`](../idrm-ffp-docs/50-data-model.md)
- Ops/deploy: [`../idrm-mvp-docs/80-ops-deployment-and-operations.md`](../idrm-mvp-docs/80-ops-deployment-and-operations.md)

## Trusted external references
- PostgreSQL — postgresql.org/docs · PostGIS — postgis.net/documentation
- MinIO — min.io/docs · Redis — redis.io/docs
- SQLAlchemy — docs.sqlalchemy.org · GeoAlchemy2 — geoalchemy-2.readthedocs.io · Alembic — alembic.sqlalchemy.org
