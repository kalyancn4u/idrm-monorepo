# Database 101

> *Type: Guide (101 / foundational) · Audience: novices → developers · Status: MVP — current · Track: Software Engineering (#12)*
> *A database is where IDRM's truth lives — every incident, resource, and user. This guide explains databases
> from first principles, then the specific ideas (keys, SQL, transactions) developers use daily.*

---

## 1. What a database is (and why not just files)

A **database** is organised, queryable storage that many users can read and write **safely at the same time**.
You *could* keep data in files, but you'd lose the guarantees a database gives: no half-written records, no two
people corrupting the same row, and fast search over millions of entries.

IDRM uses a **relational database** — data lives in **tables** (like spreadsheets) that relate to each other.

---

## 2. Tables, rows, columns

- **Table** — one kind of thing (e.g. `incidents`).
- **Column** — a field every row has (`id`, `service_type`, `priority`, `status`, `created_at`).
- **Row** — one record (one specific help request).

| id | service_type | priority | status | created_at |
|----|--------------|----------|--------|-----------|
| 3f2a… | rescue | high | created | 2026-08-14T09:00Z |

---

## 3. Keys: how rows are identified and linked

- **Primary key** — the unique id of a row. IDRM uses **UUIDs** (long unique strings) as primary keys.
- **Foreign key** — a column that points to another table's primary key, creating a **relationship**. Example:
  an `incident_assignments` row has a foreign key to the `incidents` it belongs to and the `users` (provider)
  assigned. This is the "relational" in relational database.

---

## 4. SQL: talking to the database

**SQL = Structured Query Language** — the language for asking a database to do things. The four everyday
operations are **CRUD** (Create, Read, Update, Delete):

```sql
INSERT INTO incidents (id, service_type, priority) VALUES (…, 'rescue', 'high');  -- Create
SELECT * FROM incidents WHERE status = 'created';                                 -- Read
UPDATE incidents SET status = 'accepted' WHERE id = '3f2a…';                       -- Update
DELETE FROM incidents WHERE id = '3f2a…';                                          -- Delete (rare in IDRM)
```

---

## 5. Integrity: constraints, transactions, ACID

- **Constraints** keep data valid: `NOT NULL`, uniqueness, and **enum checks** (e.g. `priority` must be one of
  low/medium/high/critical).
- **Transaction** — a group of changes that must **all succeed or all fail together**. If assigning a provider
  and updating an incident's status must happen together, a transaction guarantees you never get one without the
  other.
- **ACID** — the four promises a good relational DB makes: **A**tomicity (all-or-nothing), **C**onsistency (rules
  always hold), **I**solation (concurrent users don't corrupt each other), **D**urability (once saved, it stays).
  These are why IDRM trusts the database as its **single source of truth**.

---

## 6. Indexes: making queries fast

An **index** is like a book's index — it lets the database jump to matching rows without scanning every one. You
index the columns you filter/sort by (status, priority, location). More on the spatial kind in
[PostgreSQL / PostGIS 101](postgresql-postgis-101.md).

---

## 7. How IDRM uses it

- One database is the **sole source of truth**; the ten modules map to related tables.
- Code never scatters raw SQL — the **repository** layer of each module owns all DB access (the
  `service` layer calls it). Schema changes go through **migrations** (see the PostgreSQL/PostGIS guide), never by
  hand.
- Files (photos, proofs) are **not** stored in the DB — only their **keys/URLs** are; the bytes live in MinIO.

---

## 8. Mastery check

1. Explain why a database beats loose files for shared data.
2. Define **table, row, column, primary key, foreign key**.
3. Write the four CRUD statements in SQL for `incidents`.
4. Explain a **transaction** and each letter of **ACID**.
5. Say what an **index** is for, and where DB access lives in IDRM's module shape.

---

## 9. Go deeper

- IDRM data model: [`../../idrm-mvp-docs/50-data-model.md`](../../idrm-mvp-docs/50-data-model.md) ·
  modeling spoke [`../../instructions/data-modeling.md`](../../instructions/data-modeling.md)
- SQL tutorial — postgresql.org/docs · Relational model & normalization (reference)

---
*Next:* [PostgreSQL / PostGIS 101](postgresql-postgis-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
