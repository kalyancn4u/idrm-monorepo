# IDRM Complete Database Guide
## Schema, PostGIS Queries, and Mock Data

**Version**: 3.0  
**Database**: PostgreSQL 16 + PostGIS 3.4  
**Sources**: `DATABASE-SCHEMAS-v3.md` · `45-DATABASE-QUERY-REFERENCE.md` · `MOCK-DATA-GUIDE-v3.md`

---

## Table of Contents

1. [Database Setup](#1-database-setup)
2. [Schema Overview](#2-schema-overview)
3. [Core Table Definitions](#3-core-table-definitions)
4. [Indexes and Performance](#4-indexes-and-performance)
5. [PostGIS Spatial Queries](#5-postgis-spatial-queries)
6. [Common Query Patterns](#6-common-query-patterns)
7. [Database Views](#7-database-views)
8. [Mock Data](#8-mock-data)
9. [Migrations](#9-migrations)

---

## 1. Database Setup

```sql
-- Enable required extensions
\c idrm_db

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";    -- UUID generation
CREATE EXTENSION IF NOT EXISTS "postgis";      -- Geospatial support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";      -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gist";   -- GiST index support
```

**Why PostGIS?** — 4.7× faster spatial queries than MongoDB. 500+ spatial functions. Native `GEOMETRY` column type.

---

## 2. Schema Overview

```
┌──────────────────┐
│      users       │─────────────────────────┐
└────────┬─────────┘                         │
         │ 1                                 │
         │ N                                 │
┌────────▼──────────────────┐               │
│     service_requests      │               │
│  - requestor_id (FK)      │               │
│  - provider_id (FK)       │               │
└────────┬──────────────────┘               │
         │ N                                │
         │ 1                                │
┌────────▼──────────────┐                  │
│    organizations      │◄─────────────────┘
│  (NGOs, hospitals)    │
└───────────────────────┘

┌──────────────────┐    ┌──────────────────┐
│  notifications   │    │   audit_logs     │
└──────────────────┘    └──────────────────┘
```

| Table | Rows (full dataset) | Purpose |
|-------|--------------------|---------| 
| `users` | ~1,500 | All user accounts |
| `service_requests` | ~8,000 | All help requests |
| `organizations` | ~150 | NGOs, hospitals, agencies |
| `notifications` | ~40,000 | In-app notifications |
| `audit_logs` | ~50,000 | Security + action history |

---

## 3. Core Table Definitions

### 3.1 users

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,    -- bcrypt, cost=12

    -- Profile
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,

    -- Role
    role VARCHAR(50) NOT NULL DEFAULT 'CITIZEN'
        CHECK (role IN (
            'CITIZEN', 'VOLUNTEER', 'ORGANIZER', 'PROVIDER', 'MANAGER',
            'EVENT_MANAGER', 'EXECUTIVE', 'DM_AUTHORITY', 'AUDITOR', 'ADMIN'
        )),    -- EXECUTIVE reserved for Post-MVP; "Public" = no account (not stored). See IDRM-FS.md §3.3.
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,

    -- Preferences (flexible JSONB)
    preferences JSONB NOT NULL DEFAULT '{
        "language": "en",
        "notifications": {"email": true, "sms": true, "push": false},
        "theme": "light"
    }'::jsonb,

    -- Metadata
    email_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip INET,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT email_format CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT phone_format CHECK (
        phone IS NULL OR phone ~* '^\+[1-9][0-9]{1,14}$'
    )
);
```

### 3.2 service_requests

```sql
CREATE TABLE service_requests (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Foreign keys
    requestor_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    provider_id UUID REFERENCES organizations(org_id) ON DELETE SET NULL,

    -- Service details
    service_type VARCHAR(50) NOT NULL
        CHECK (service_type IN ('RESCUE','MEDICAL','FOOD','SHELTER','WATER','OTHER')),
    priority VARCHAR(20) NOT NULL
        CHECK (priority IN ('CRITICAL','HIGH','MEDIUM','LOW')),
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED'
        CHECK (status IN (
            'SUBMITTED','APPROVED','ACCEPTED','IN_PROGRESS',
            'COMPLETED','VERIFIED','REJECTED','CANCELLED','EXPIRED','DISPUTED'
        )),

    -- PostGIS geometry (longitude, latitude in WGS84/EPSG:4326)
    location GEOMETRY(Point, 4326) NOT NULL,
    address TEXT,

    -- Content
    description TEXT NOT NULL
        CHECK (char_length(description) BETWEEN 10 AND 500),
    num_people_affected INTEGER NOT NULL DEFAULT 1
        CHECK (num_people_affected BETWEEN 1 AND 1000),
    privacy_level VARCHAR(20) NOT NULL DEFAULT 'PROTECTED'
        CHECK (privacy_level IN ('PUBLIC','PROTECTED','PRIVATE')),

    -- Timeline
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Feedback
    rating INTEGER CHECK (rating IS NULL OR rating BETWEEN 1 AND 5),
    feedback TEXT,
    rejection_reason TEXT,

    -- Timeline integrity constraints
    CONSTRAINT valid_acceptance_time CHECK (
        accepted_at IS NULL OR accepted_at >= created_at),
    CONSTRAINT valid_completion_time CHECK (
        completed_at IS NULL OR (completed_at >= accepted_at AND accepted_at IS NOT NULL)),
    CONSTRAINT valid_verification_time CHECK (
        verified_at IS NULL OR (verified_at >= completed_at AND completed_at IS NOT NULL)),
    CONSTRAINT rating_requires_verification CHECK (
        rating IS NULL OR (verified_at IS NOT NULL AND status = 'VERIFIED'))
);
```

### 3.3 organizations

```sql
CREATE TABLE organizations (
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(50) NOT NULL
        CHECK (org_type IN ('NGO','HOSPITAL','GOVT_AGENCY','VOLUNTEER_GROUP')),
    registration_number VARCHAR(100) UNIQUE,
    service_types VARCHAR(50)[] NOT NULL,    -- e.g. ARRAY['MEDICAL','FOOD']
    coverage_area GEOMETRY(Point, 4326),     -- Center of coverage
    coverage_radius_km DECIMAL(8,2),
    capacity INTEGER,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 audit_logs

```sql
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,           -- e.g. SERVICE_CREATED, LOGIN_FAILED
    resource_type VARCHAR(100),             -- e.g. ServiceRequest, User
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

---

## 4. Indexes and Performance

```sql
-- Spatial index (required for ST_DWithin, ST_Distance queries)
CREATE INDEX idx_service_requests_location
    ON service_requests USING GIST (location);

-- Composite status + type (most common filter combination)
CREATE INDEX idx_service_requests_status_type
    ON service_requests (status, service_type);

-- Priority queries
CREATE INDEX idx_service_requests_priority
    ON service_requests (priority, created_at DESC);

-- User lookup
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_role ON users (role);

-- Organization spatial index
CREATE INDEX idx_organizations_coverage
    ON organizations USING GIST (coverage_area);

-- Text search on service descriptions
CREATE INDEX idx_service_requests_description_trgm
    ON service_requests USING GIN (description gin_trgm_ops);

-- Audit log time-based queries
CREATE INDEX idx_audit_logs_timestamp
    ON audit_logs (timestamp DESC);
CREATE INDEX idx_audit_logs_user_action
    ON audit_logs (user_id, action);
```

---

## 5. PostGIS Spatial Queries

### Find Requests Within Radius

```sql
-- Find all MEDICAL requests within 10km of coordinates
SELECT
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    s.address,
    ST_Distance(
        s.location::geography,
        ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)::geography
    ) / 1000 AS distance_km
FROM service_requests s
WHERE
    s.status IN ('SUBMITTED', 'APPROVED')
    AND s.service_type = 'MEDICAL'
    AND ST_DWithin(
        s.location::geography,
        ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)::geography,
        10000    -- radius in meters
    )
ORDER BY distance_km ASC;
```

### Find Nearest Provider

```sql
SELECT
    o.org_id,
    o.name,
    o.org_type,
    o.capacity,
    ST_Distance(
        o.coverage_area::geography,
        ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)::geography
    ) / 1000 AS distance_km
FROM organizations o
WHERE
    o.is_verified = TRUE
    AND 'MEDICAL' = ANY(o.service_types)
    AND ST_DWithin(
        o.coverage_area::geography,
        ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)::geography,
        o.coverage_radius_km * 1000
    )
ORDER BY distance_km ASC
LIMIT 5;
```

### Bounding Box Query

```sql
SELECT service_id, service_type, status,
       ST_AsGeoJSON(location) AS geojson_location
FROM service_requests
WHERE
    location && ST_MakeEnvelope(78.0, 17.0, 79.0, 18.0, 4326)
    AND status NOT IN ('COMPLETED', 'VERIFIED', 'CANCELLED');
```

### Insert Service Request with Location

```sql
INSERT INTO service_requests (
    requestor_id, service_type, priority,
    location, address, description, num_people_affected
) VALUES (
    '550e8400-e29b-41d4-a716-446655440000',
    'MEDICAL',
    'CRITICAL',
    ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326),  -- lon, lat order!
    '123 Main Street, Hyderabad',
    'Elderly person with chest pain, water level 3 feet',
    1
);
```

**Important**: PostGIS `ST_MakePoint(longitude, latitude)` — longitude first.

---

## 6. Common Query Patterns

### Get Service with Provider Details

```sql
SELECT
    s.service_id, s.service_type, s.priority, s.status,
    s.description, s.address,
    ST_AsGeoJSON(s.location) AS location,
    s.created_at,
    u.full_name AS requestor_name,
    o.name AS provider_name, o.contact_phone AS provider_phone
FROM service_requests s
JOIN users u ON s.requestor_id = u.user_id
LEFT JOIN organizations o ON s.provider_id = o.org_id
WHERE s.service_id = $1;
```

### Dashboard Statistics

```sql
SELECT
    COUNT(*) FILTER (WHERE status = 'SUBMITTED') AS pending,
    COUNT(*) FILTER (WHERE status IN ('ACCEPTED','IN_PROGRESS')) AS active,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed,
    COUNT(*) FILTER (WHERE status = 'VERIFIED') AS verified,
    AVG(
        EXTRACT(EPOCH FROM (completed_at - created_at)) / 60
    ) FILTER (WHERE completed_at IS NOT NULL) AS avg_response_min,
    COUNT(*) FILTER (WHERE priority = 'CRITICAL') AS critical_count
FROM service_requests
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days';
```

### Full-Text Search on Descriptions

```sql
SELECT service_id, description, priority, status
FROM service_requests
WHERE description ILIKE '%chest pain%'
   OR similarity(description, 'medical emergency') > 0.3
ORDER BY similarity(description, 'medical emergency') DESC
LIMIT 20;
```

---

## 7. Database Views

### v_active_services (read-optimized)

```sql
CREATE VIEW v_active_services AS
SELECT
    s.service_id, s.service_type, s.priority, s.status,
    s.address, ST_AsGeoJSON(s.location) AS location,
    s.num_people_affected, s.created_at,
    u.full_name AS requestor_name, u.phone AS requestor_phone,
    o.name AS provider_name
FROM service_requests s
JOIN users u ON s.requestor_id = u.user_id
LEFT JOIN organizations o ON s.provider_id = o.org_id
WHERE s.status NOT IN ('COMPLETED','VERIFIED','CANCELLED','EXPIRED');
```

### v_organization_stats

```sql
CREATE VIEW v_organization_stats AS
SELECT
    o.org_id, o.name, o.org_type,
    COUNT(s.service_id) AS total_services,
    COUNT(s.service_id) FILTER (WHERE s.status = 'VERIFIED') AS completed,
    AVG(EXTRACT(EPOCH FROM (s.completed_at - s.accepted_at)) / 60)
        FILTER (WHERE s.completed_at IS NOT NULL) AS avg_response_min,
    AVG(s.rating) FILTER (WHERE s.rating IS NOT NULL) AS avg_rating
FROM organizations o
LEFT JOIN service_requests s ON o.org_id = s.provider_id
GROUP BY o.org_id, o.name, o.org_type;
```

---

## 8. Mock Data

Three data sets are available for different testing needs:

| Dataset | File | Users | Requests | Use For |
|---------|------|-------|----------|---------|
| Unit test | `mock_data_unittest.sql` | 10 | 25 | Fast unit tests |
| Integration | `mock_data_integration.sql` | 100 | 500 | API integration tests |
| Full | `mock_data_full.sql` | 1,500 | 8,000 | Load testing, demos |

### Loading Mock Data

```bash
# Unit test scale
psql -U idrm_user -d idrm_db -f database/init/mock_data_unittest.sql

# Integration scale
psql -U idrm_user -d idrm_db -f database/init/mock_data_integration.sql

# Full dataset
psql -U idrm_user -d idrm_db -f database/init/mock_data_full.sql
```

### Generating New Mock Data

```bash
conda activate idrm-mvp
python database/init/generators/generate_users.py
python database/init/generators/generate_services.py
python database/init/generators/generate_disaster_scenarios.py
```

### Sample Coordinates (Hyderabad Area)

| Location | Latitude | Longitude |
|----------|----------|-----------|
| Hyderabad center | 17.3850 | 78.4867 |
| Secunderabad | 17.4401 | 78.4989 |
| Kukatpally | 17.4947 | 78.3996 |
| LB Nagar | 17.3436 | 78.5560 |

---

## 9. Migrations

IDRM uses **Alembic** for database migrations (managed with the Conda Python environment).

```bash
conda activate idrm-mvp
cd src/backend/app-python

# Generate migration from model changes
alembic revision --autogenerate -m "add service rating table"

# Apply all pending migrations
alembic upgrade head

# Roll back one step
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

### Migration File Naming

Alembic files land in `backend/alembic/versions/`. Each file has a revision ID, up/down functions, and dependency chain. Always review auto-generated files before applying.

### Production Migration Procedure

```bash
# 1. Backup first
./scripts/backup.sh

# 2. Test on staging
ssh staging-server "cd /app && alembic upgrade head"

# 3. Verify staging
psql $STAGING_DB -c "\dt"

# 4. Apply to production (via CI/CD)
# GitHub Actions runs: alembic upgrade head
# If fails, automatic rollback: alembic downgrade -1
```

---

**Full source documents**:
- Table definitions: [../docs/development/IDRM-LLD.md](../docs/development/IDRM-LLD.md) §9–11 — Full schema DDL
- Query cookbook: [../docs/IDRM-Database-Query-Reference.md](../docs/IDRM-Database-Query-Reference.md) 
- Mock data scripts: [../docs/IDRM-Mock-Data-Guide.md](../docs/IDRM-Mock-Data-Guide.md)
