# IDRM Instructions — Data Modeling

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> Engines & ops live in [`data-stores.md`](data-stores.md); this spoke = **how to shape the schema**.

## Modeling conventions (align with the API contract)
- Keys: **UUID** primary keys. Timestamps: **ISO-8601 UTC**, columns named `*_at`.
- Naming: `snake_case` tables/columns; enum values lowercase `snake_case` (match the API exactly).
- Every state-bearing entity carries an explicit lifecycle column; incident lifecycle (8 states):
  `created → (approved if critical) → accepted → in_progress → completed → verified` (+ `cancelled`, `rejected`).
- Domain modules map to schema areas: users, incidents, resources, locations, alerts, notifications,
  reports, files, audit, administration.
- Files: DB stores **keys/URLs only** (blobs live in MinIO — see [`data-stores.md`](data-stores.md)).

## Per-type modeling notes
- **Relational (Postgres, primary):** normalize first; denormalize only with evidence. FK integrity,
  check constraints on enums, indexes on filter/sort columns. Migrations via **Alembic**.
- **Spatial (PostGIS):** geometry/geography columns, SRID **4326**; **GiST** indexes; query by bounding box +
  `ST_*` predicates; keep geometry validity (`ST_IsValid`). Native geospatial — **no GeoServer** (Python
  GeoPandas/Shapely service only if FFP needs it).
- **Time-series (FFP, if needed):** metrics/telemetry → partition by time; consider a TS extension only on a trigger.
- **Key-value / cache (FFP):** Redis for ephemeral/derived data — **never the source of truth**; model TTLs
  and invalidation explicitly. See [`caching-messaging.md`](caching-messaging.md).

## Canonical docs
- [`../idrm-mvp-docs/50-data-model.md`](../idrm-mvp-docs/50-data-model.md) ·
  [`../idrm-ffp-docs/50-data-model.md`](../idrm-ffp-docs/50-data-model.md)

## Trusted external references
- PostGIS — postgis.net/documentation · SRID/EPSG:4326 — epsg.io/4326
- PostgreSQL data types & indexing — postgresql.org/docs · Database normalization (reference) — Codd/1NF-3NF
- Pydantic — docs.pydantic.dev (MVP validation mirrors the schema)
