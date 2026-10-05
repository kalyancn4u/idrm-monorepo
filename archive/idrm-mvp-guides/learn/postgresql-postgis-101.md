# PostgreSQL / PostGIS 101

> *Type: Guide (101 / foundational) · Audience: developers (readable by all) · Status: MVP — current · Track: Software Engineering (#13)*
> *[Database 101](database-101.md) taught the general ideas; this guide is about the **specific** engine IDRM
> runs — PostgreSQL — and the extension that makes it map-aware — PostGIS — plus the Python tools around them.*

---

## 1. Why PostgreSQL

**PostgreSQL** ("Postgres") is a powerful, free, open-source relational database. IDRM chose it because it is
rock-solid on ACID guarantees, rich in data types, extensible, and — crucially — has **PostGIS**, the best
open-source spatial engine. IDRM standardises on **PostgreSQL 16**.

Beyond the basics, useful Postgres features IDRM leans on:

- Rich **data types**: `uuid`, `timestamptz` (timezone-aware time), `jsonb` (structured JSON), native `enum`.
- **Schemas** (namespaces to organise tables) and **extensions** (add-on capabilities — PostGIS is one).
- Strong concurrency (many readers/writers without blocking each other).

---

## 2. PostGIS: making Postgres understand places

**PostGIS** is an **extension** that adds geographic types and operations to Postgres — turning it into a full
GIS. (Enable it once with `CREATE EXTENSION postgis;`.) It adds:

- **Geometry / geography columns** — store a Point, LineString, or Polygon in a row.
- **SRID 4326** — the coordinate system tag meaning "GPS lat/long" (WGS 84). Every IDRM location uses it.
- **Spatial indexes (GiST)** — make "what's nearby?" fast at scale.
- **`ST_*` functions** — the spatial toolkit: `ST_DWithin` (within a distance), `ST_Contains` (inside an area),
  `ST_Distance`, `ST_MakePoint`, `ST_IsValid`.

**Worked example** — *high-priority incidents within 5 km of a team:*

```sql
SELECT id, service_type
FROM incidents
WHERE priority = 'high'
  AND ST_DWithin(location::geography, ST_MakePoint(72.877, 19.076)::geography, 5000);
```

> This is the same power a standalone GIS server gives — but native to the database. That's why IDRM's MVP uses
> **PostGIS + Python, not GeoServer**. The response-side view of maps is in
> [GIS for Emergency Response](gis-for-emergency-response.md).

---

## 3. The Python layer IDRM uses

Developers rarely write raw SQL in IDRM; they use Python tools that generate it safely:

- **SQLAlchemy** — an **ORM** (Object-Relational Mapper): Python classes ↔ database tables, so you work with
  objects and it writes the SQL.
- **GeoAlchemy2** — the SQLAlchemy add-on for PostGIS geometry columns.
- **Alembic** — **migrations**: versioned, reviewable scripts that change the schema over time. **Never** edit
  the schema by hand — every change is an Alembic migration, so the database structure has a history just like
  the code.
- **Pydantic** — validates data shapes at the API boundary (pairs with the DB models).

---

## 4. Where this sits in a module

Each module's `models.py` defines the tables (SQLAlchemy/GeoAlchemy2); its `repository.py` is the only code that
queries them; `service.py` calls the repository. Schema evolution = an Alembic migration reviewed in a PR.
(See the [module shape](../../instructions/domain.md) and [Database 101](database-101.md).)

---

## 5. Operating it (the essentials)

- Runs as a native **systemd** service on **Ubuntu** in the MVP (no Docker).
- Backups + Point-In-Time Recovery matter from day one — see [Backup & Restore 101](backup-restore-101.md) and
  the [backup spoke](../../instructions/backup-and-dr.md).

---

## 6. Mastery check

1. Say why IDRM chose PostgreSQL, and name three Postgres features it uses.
2. Explain what **PostGIS** adds and what **SRID 4326** means.
3. Write (or read) an `ST_DWithin` proximity query.
4. Explain **SQLAlchemy**, **GeoAlchemy2**, and why schema changes go through **Alembic**.
5. Say why IDRM uses PostGIS instead of a separate GeoServer.

---

## 7. Go deeper

- PostgreSQL 16 — postgresql.org/docs/16 · PostGIS — postgis.net/documentation
- SQLAlchemy — docs.sqlalchemy.org · GeoAlchemy2 — geoalchemy-2.readthedocs.io · Alembic — alembic.sqlalchemy.org
- IDRM data model: [`../../idrm-mvp-docs/50-data-model.md`](../../idrm-mvp-docs/50-data-model.md)

---
*Next:* [Observability 101](observability-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
