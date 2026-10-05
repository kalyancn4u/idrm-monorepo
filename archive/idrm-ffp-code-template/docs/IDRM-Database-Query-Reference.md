# IDRM Database Query Reference

## SQL & PostGIS Queries for All Core Operations

**Version**: 3.0**Source**: `backup/45-DATABASE-QUERY-REFERENCE.md`

**Stack**: PostgreSQL 16 + PostGIS 3.4 · Python asyncpg / SQLAlchemy

**Last Updated**: May 30, 2026

> All queries use parameterised placeholders (`$1`, `$2`, …) to prevent SQL injection.
> **Coordinate order**: `ST_MakePoint(longitude, latitude)` — longitude first, latitude second.

---

## Part 1 — Users CRUD

### Insert new user

```sql
INSERT INTO users (
    user_id, email, password_hash, full_name, phone, role, created_at
) VALUES (
    gen_random_uuid(),
    $1,           -- email
    $2,           -- bcrypt hash (cost 12)
    $3,           -- full_name
    $4,           -- phone (E.164 format)
    'CITIZEN',    -- default role
    NOW()
)
RETURNING user_id, email, role, created_at;
```

### Get user by ID

```sql
SELECT user_id, email, full_name, phone, role, is_verified, is_active, created_at
FROM users
WHERE user_id = $1;
```

### Get user by email (login)

```sql
SELECT user_id, email, password_hash, role, is_active, is_verified
FROM users
WHERE email = $1;
-- Never select * — never expose password_hash to API responses
```

### Update profile

```sql
UPDATE users
SET full_name = $2,
    phone     = $3,
    updated_at = NOW()
WHERE user_id = $1
RETURNING user_id, full_name, phone, updated_at;
```

### Change role (admin action)

```sql
UPDATE users
SET role       = $2,
    updated_at = NOW()
WHERE user_id = $1
  AND role != 'SYSTEM_ADMIN'   -- Guard: can never downgrade SYSTEM_ADMIN
RETURNING user_id, role;
```

---

## Part 2 — Service Requests CRUD

### Insert service request

```sql
INSERT INTO service_requests (
    service_id, requestor_id, service_type, priority,
    location,  address,      description, privacy_level,
    status,    created_at
) VALUES (
    gen_random_uuid(),
    $1,   -- requestor_id (authenticated user)
    $2,   -- service_type ENUM
    $3,   -- priority ENUM
    ST_SetSRID(ST_MakePoint($4, $5), 4326),  -- $4=longitude, $5=latitude
    $6,   -- address (reverse-geocoded)
    $7,   -- description
    $8,   -- privacy_level (PUBLIC / PROTECTED / PRIVATE)
    'SUBMITTED',
    NOW()
)
RETURNING service_id, status, created_at;
```

### Get single service request (with requestor + provider)

```sql
SELECT
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    s.address,
    s.description,
    s.num_people_affected,
    s.privacy_level,
    s.created_at,
    s.accepted_at,
    s.completed_at,
    s.rating,
    ST_AsGeoJSON(s.location)::json    AS location,

    -- Requestor
    req.user_id    AS requestor_id,
    req.full_name  AS requestor_name,
    req.phone      AS requestor_phone,

    -- Assigned provider org (nullable until accepted)
    org.org_id     AS provider_org_id,
    org.name       AS provider_org_name,
    org.contact_phone AS provider_phone

FROM service_requests s
INNER JOIN users       req ON s.requestor_id = req.user_id
LEFT  JOIN organizations org ON s.provider_id  = org.org_id
WHERE s.service_id = $1;
```

### List services with filters (paginated)

```sql
SELECT
    s.service_id, s.service_type, s.priority, s.status,
    s.address, s.created_at,
    ST_AsGeoJSON(s.location)::json AS location,
    req.full_name AS requestor_name
FROM service_requests s
INNER JOIN users req ON s.requestor_id = req.user_id
WHERE
    ($1 IS NULL OR s.service_type = $1)   -- service_type filter
    AND ($2 IS NULL OR s.priority   = $2)  -- priority filter
    AND ($3 IS NULL OR s.status     = $3)  -- status filter
    AND ($4 IS NULL OR s.requestor_id = $4) -- own requests filter
ORDER BY s.created_at DESC
LIMIT  $5    -- page_size (default 20, max 100)
OFFSET $6;   -- (page - 1) * page_size
```

### Update service status

```sql
UPDATE service_requests
SET  status      = $2,
     updated_at  = NOW()
WHERE service_id = $1
  AND status     = $3   -- optimistic lock: only update from expected state
RETURNING service_id, status, updated_at;
```

### Accept service (provider — race-condition safe)

```sql
BEGIN;

-- Lock the row; fail if another transaction already assigned it
SELECT service_id
FROM service_requests
WHERE service_id = $1
  AND status     = 'APPROVED'
  AND provider_id IS NULL
FOR UPDATE;

-- Only updates if the SELECT above returned a row
UPDATE service_requests
SET  provider_id = $2,     -- organisation UUID
     status      = 'ACCEPTED',
     accepted_at = NOW(),
     updated_at  = NOW()
WHERE service_id = $1
  AND status     = 'APPROVED'
  AND provider_id IS NULL
RETURNING service_id, status, accepted_at;

COMMIT;
```

### Cancel service (requestor action — soft delete)

```sql
UPDATE service_requests
SET  status     = 'CANCELLED',
     updated_at = NOW()
WHERE service_id   = $1
  AND requestor_id = $2                         -- ownership check
  AND status IN ('SUBMITTED', 'APPROVED')        -- cannot cancel after acceptance
RETURNING service_id, status;
```

---

## Part 3 — Spatial Queries (PostGIS)

### Find services within radius

```sql
SELECT
    service_id,
    service_type,
    priority,
    status,
    address,
    ST_Distance(
        location::geography,
        ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography
    ) AS distance_m
FROM service_requests
WHERE ST_DWithin(
    location::geography,
    ST_SetSRID(ST_MakePoint($1, $2), 4326)::geography,  -- $1=lng, $2=lat
    $3 * 1000   -- $3 = radius in km, converted to metres
)
  AND status IN ('APPROVED', 'ACCEPTED', 'IN_PROGRESS')
ORDER BY distance_m ASC
LIMIT 50;
```

> **Why `::geography`?** The `geography` cast makes `ST_DWithin` use metres (not degrees) and correctly handles the Earth's curvature. Always cast for distance queries.

### Bounding-box query (map viewport)

```sql
SELECT
    service_id, service_type, priority, status, address,
    ST_AsGeoJSON(location)::json AS location
FROM service_requests
WHERE location && ST_MakeEnvelope($1, $2, $3, $4, 4326)
  -- $1=min_lng, $2=min_lat, $3=max_lng, $4=max_lat
  AND status NOT IN ('CANCELLED', 'REJECTED', 'EXPIRED')
ORDER BY priority DESC, created_at DESC;
```

### K-means clustering (map zoom-out)

```sql
WITH clustered AS (
    SELECT
        ST_ClusterKMeans(location, $1) OVER () AS cluster_id,
        location, service_type, priority
    FROM service_requests
    WHERE status IN ('APPROVED', 'ACCEPTED', 'IN_PROGRESS')
)
SELECT
    cluster_id,
    COUNT(*)                                              AS count,
    ST_AsGeoJSON(ST_Centroid(ST_Collect(location)))::json AS centroid,
    array_agg(DISTINCT service_type)                      AS service_types,
    COUNT(*) FILTER (WHERE priority = 'CRITICAL')         AS critical_count,
    COUNT(*) FILTER (WHERE priority = 'HIGH')             AS high_count
FROM clustered
GROUP BY cluster_id
ORDER BY critical_count DESC;
-- $1 = desired number of clusters (e.g. 10)
```

### Export GeoJSON FeatureCollection

```sql
SELECT json_build_object(
    'type', 'FeatureCollection',
    'features', json_agg(
        json_build_object(
            'type', 'Feature',
            'geometry',   ST_AsGeoJSON(location)::json,
            'properties', json_build_object(
                'service_id',   service_id,
                'service_type', service_type,
                'priority',     priority,
                'status',       status,
                'address',      address,
                'created_at',   created_at
            )
        )
    )
) AS geojson
FROM service_requests
WHERE ($1 IS NULL OR service_type = $1)
  AND status IN ('APPROVED', 'ACCEPTED', 'IN_PROGRESS')
  AND created_at >= NOW() - INTERVAL '7 days';
```

---

## Part 4 — Database Views

Create these views once in your migration scripts; then query them like tables.

### `active_services_view` — Map display

```sql
CREATE OR REPLACE VIEW active_services_view AS
SELECT
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    s.address,
    s.description,
    s.created_at,
    EXTRACT(EPOCH FROM (NOW() - s.created_at)) / 60 AS age_minutes,
    ST_AsGeoJSON(s.location)::json                   AS location,

    req.full_name   AS requestor_name,
    org.name        AS provider_org_name,

    CASE s.priority
        WHEN 'CRITICAL' THEN 4
        WHEN 'HIGH'     THEN 3
        WHEN 'MEDIUM'   THEN 2
        WHEN 'LOW'      THEN 1
    END AS priority_sort

FROM service_requests s
INNER JOIN users req ON s.requestor_id = req.user_id
LEFT  JOIN organizations org ON s.provider_id = org.org_id
WHERE s.status IN ('SUBMITTED', 'APPROVED', 'ACCEPTED', 'IN_PROGRESS');

-- Usage:
SELECT * FROM active_services_view ORDER BY priority_sort DESC, age_minutes DESC;
```

### `dashboard_metrics_view` — Analytics dashboard

```sql
CREATE OR REPLACE VIEW dashboard_metrics_view AS
SELECT
    COUNT(*)                                              AS total_requests,
    COUNT(*) FILTER (WHERE status = 'SUBMITTED')          AS submitted,
    COUNT(*) FILTER (WHERE status = 'APPROVED')           AS approved,
    COUNT(*) FILTER (WHERE status = 'IN_PROGRESS')        AS in_progress,
    COUNT(*) FILTER (WHERE status = 'COMPLETED')          AS completed,
    COUNT(*) FILTER (WHERE status = 'VERIFIED')           AS verified,

    COUNT(*) FILTER (WHERE priority = 'CRITICAL')         AS critical,
    COUNT(*) FILTER (WHERE priority = 'HIGH')             AS high,

    COUNT(*) FILTER (WHERE service_type = 'MEDICAL')      AS medical,
    COUNT(*) FILTER (WHERE service_type = 'FOOD')         AS food,
    COUNT(*) FILTER (WHERE service_type = 'RESCUE')       AS rescue,
    COUNT(*) FILTER (WHERE service_type = 'SHELTER')      AS shelter,
    COUNT(*) FILTER (WHERE service_type = 'WATER')        AS water,

    ROUND(
        AVG(EXTRACT(EPOCH FROM (completed_at - created_at)) / 60)
        FILTER (WHERE completed_at IS NOT NULL)
    ::numeric, 1)                                          AS avg_completion_min,

    ROUND(
        COUNT(*) FILTER (WHERE status IN ('COMPLETED', 'VERIFIED'))::numeric /
        NULLIF(COUNT(*), 0) * 100
    , 1)                                                   AS completion_pct

FROM service_requests
WHERE created_at >= NOW() - INTERVAL '30 days';

-- Usage:
SELECT * FROM dashboard_metrics_view;
```

---

## Part 5 — Analytics Queries

### Requests per day (time-series chart)

```sql
SELECT
    DATE(created_at)                                      AS date,
    COUNT(*)                                              AS total,
    COUNT(*) FILTER (WHERE priority = 'CRITICAL')         AS critical,
    COUNT(*) FILTER (WHERE service_type = 'MEDICAL')      AS medical,
    COUNT(*) FILTER (WHERE status IN ('COMPLETED','VERIFIED')) AS completed
FROM service_requests
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

### Average response time by service type

```sql
SELECT
    service_type,
    COUNT(*)                                                             AS total_completed,
    ROUND(AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/60)::numeric, 1) AS avg_min,
    ROUND(MIN(EXTRACT(EPOCH FROM (completed_at - created_at))/60)::numeric, 1) AS fastest_min,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))/60
    )::numeric, 1)                                                       AS median_min
FROM service_requests
WHERE status = 'COMPLETED'
  AND completed_at IS NOT NULL
  AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY service_type
ORDER BY avg_min ASC;
```

### Top-performing providers

```sql
SELECT
    org.org_id,
    org.name             AS organization,
    COUNT(*)             AS services_completed,
    ROUND(AVG(sr.rating)::numeric, 2) AS avg_rating,
    ROUND(AVG(EXTRACT(EPOCH FROM (sr.completed_at - sr.created_at))/60)::numeric, 1) AS avg_response_min,
    COUNT(*) FILTER (WHERE sr.priority = 'CRITICAL') AS critical_handled
FROM service_requests sr
JOIN organizations org ON sr.provider_id = org.org_id
WHERE sr.status = 'VERIFIED'
  AND sr.completed_at >= NOW() - INTERVAL '90 days'
GROUP BY org.org_id, org.name
HAVING COUNT(*) >= 5   -- at least 5 completions to qualify
ORDER BY avg_rating DESC, avg_response_min ASC
LIMIT 10;
```

---

## Part 6 — Performance Patterns

### Pagination

```sql
-- Page N, page_size items per page
LIMIT  $page_size
OFFSET ($page - 1) * $page_size
```

### Full-text search on descriptions

```sql
SELECT service_id, service_type, description,
       ts_rank(to_tsvector('english', description),
               plainto_tsquery('english', $1)) AS rank
FROM service_requests
WHERE to_tsvector('english', description) @@ plainto_tsquery('english', $1)
ORDER BY rank DESC
LIMIT 20;
-- Uses GIN index on description — see schema for index definition
```

### Index reference

| Index                      | Type  | Columns                | Used by               |
| -------------------------- | ----- | ---------------------- | --------------------- |
| `idx_sr_requestor`       | BTree | `requestor_id`       | "my requests" query   |
| `idx_sr_provider`        | BTree | `provider_id`        | provider dashboard    |
| `idx_sr_status_priority` | BTree | `(status, priority)` | filter queries        |
| `idx_sr_location`        | GiST  | `location`           | all geo queries       |
| `idx_sr_description`     | GIN   | `description`        | full-text search      |
| `idx_sr_created_at`      | BTree | `created_at`         | sorting & time-series |

---

**See also**:

- [diagrams/IDRM-Database-Schema.md](diagrams/IDRM-Database-Schema.md) — Entity-relationship diagram
- [development/IDRM-LLD.md](development/IDRM-LLD.md) §9–11 — Full schema DDL
- [IDRM-Mock-Data-Guide.md](IDRM-Mock-Data-Guide.md)
