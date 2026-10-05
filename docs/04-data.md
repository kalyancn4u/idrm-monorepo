# Data — The Data & Maps

> **Part of:** IDRM Documentation · `04-data.md`
> **Answers:** What data does IDRM keep, how is it organised, and how do the maps work?
> **Source posters:** Posters 21–23 (Phase 4 Data)
> **Audience:** Data / GIS engineers (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

1. [Where data lives](#1-where-data-lives) — the stores and their roles.
2. [What IDRM stores](#2-what-idrm-stores) — the main kinds of data.
3. [Entity-relationship overview](#3-entity-relationship-overview) — the core things and how they connect.
4. [Maps & geospatial](#4-maps--geospatial) — how location works.
5. [Keeping data safe & correct](#5-keeping-data-safe--correct) — integrity, migrations, backups.

---

## 1. Where data lives

IDRM uses one primary database plus a couple of supporting stores, each with a clear role:

| Store | Role |
|---|---|
| **PostgreSQL** | The single source of truth — all core records live here. |
| **PostGIS** | An extension of PostgreSQL that understands locations and shapes, enabling map queries (e.g. "what's within 5 km?"). |
| **MinIO** (object storage) | S3-compatible store for uploaded files, documents, and images (on-prem; DB keeps only keys/URLs). |
| *(No Redis in the MVP)* | Caching/sessions live in **PostgreSQL**; Redis is deferred to the FFP scale-out phase. |

Keeping PostgreSQL as the one authoritative store — with PostGIS built in — is what lets IDRM be
data-rich *and* simple to operate.

---

## 2. What IDRM stores

The data mirrors the business modules from [`02-architecture.md`](02-architecture.md):

| Data area | Examples |
|---|---|
| **Users & access** | Users, roles, permissions, sessions. |
| **Incidents** | Incidents, types, statuses, timelines, escalations. |
| **Resources** | Inventory, fleet, equipment, shelters, availability. |
| **Volunteers** | Registrations, skills, assignments, attendance. |
| **Geospatial** | Locations, map layers, boundaries, points of interest. |
| **Communication** | Alerts, notifications, subscriptions, message logs. |
| **Documents** | Files, attachments, images, metadata. |
| **Audit** | Immutable records of who did what, when. |
| **Configuration** | Settings, reference data, system options. |

---

## 3. Entity-relationship overview

At an overview level, the core entities relate like this (one-to-many shown as "→ many"):

```
User ──→ many Incidents (reported)          Role ──→ many Users
User ──→ many Assignments                   Incident ──→ one Location (PostGIS)
Volunteer ──→ many Assignments              Incident ──→ many Notifications
Resource ──→ many Allocations               Incident ──→ many Documents
Shelter ──→ many Occupancies                Any action ──→ one Audit record
```

In words:

- A **User** has a **Role** (which grants permissions) and can **report Incidents**.
- An **Incident** has a **Location** (stored as PostGIS geometry), and generates **Notifications**,
  **Documents**, and **Audit** entries.
- **Volunteers** and **Resources** are connected to incidents through **Assignments/Allocations**.
- Every meaningful action leaves an **Audit** record.

A complete, field-level data model (every table and column) is produced in a later, deeper pass; this
overview is enough to understand how the pieces fit.

---

## 4. Maps & geospatial

Location is central to disaster response, so IDRM treats maps as a first-class capability — handled with
Python and the database, no separate map server required.

| Piece | Role |
|---|---|
| **PostGIS** | Stores locations and shapes; answers spatial questions (distance, containment, nearest). |
| **GDAL (via Python)** | The engine for reading, writing, and transforming geospatial data. |
| **Miniconda environment** | Provisions GDAL and the geospatial libraries reliably. |
| **Leaflet** | Draws the interactive map in the browser. |
| **Map layers** | Base maps, incident locations, resources, shelters, boundaries, heatmaps. |

**Typical geospatial features:**

- Show incidents, resources, and shelters on a live map.
- Find what's **nearby** (e.g. responders within a radius of an incident).
- **Geocoding** (turn an address into a point) and **routing** (paths between points).
- **Geofencing** (alerts when something enters/leaves an area) and **heatmaps** (where demand concentrates).

---

## 5. Keeping data safe & correct

- **Structure changes are versioned.** Every change to the database shape is an **Alembic** migration, so the
  database can be rebuilt or upgraded predictably.
- **Access is controlled.** Roles and permissions (see [`05-security.md`](05-security.md)) govern who can read
  or change what; every change is audited.
- **Data is backed up.** Backup, restore, and recovery targets (how fresh, how fast) are covered in
  [`07-operations.md`](07-operations.md).
- **Validation at the edges.** Incoming data is validated (Pydantic) before it ever reaches the database, so
  bad data is rejected early.

---

## Where this leads

- How access and privacy are enforced → [`05-security.md`](05-security.md)
- How data correctness is tested → [`06-quality.md`](06-quality.md)
- How data is backed up and recovered → [`07-operations.md`](07-operations.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"Data-driven decisions, built on one reliable foundation."*
