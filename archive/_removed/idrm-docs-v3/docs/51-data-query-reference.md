> *Type: Document (specification) · Audience: Backend devs, DBAs · Status: Archived — v3 historical generation*

# IDRM: Complete Database Query Reference

<!-- IDRM-CLEANUP doc=v3-51-queryref status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — query reference (teaching)
> SQL/PostGIS query examples → taught in [`../../../../guides/mvp/learn/postgresql-postgis-101.md`](../../../../guides/mvp/learn/postgresql-postgis-101.md)
> + schema in `docs/mvp/50`. Reusable as a query cookbook; not normative. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## All SQL & Spatial Queries Explained for Beginners

**Version**: 3.0 Consolidated  
**Audience**: Backend developers, Database administrators, Complete beginners  
**Reading Time**: 60-90 minutes  
**Last Updated**: May 16, 2026

---

## 📚 **Table of Contents**

1. [What Are Database Queries?](#1-what-are-database-queries)
2. [Quick Reference: All Query Types](#2-quick-reference-all-query-types)
3. [Basic CRUD Queries](#3-basic-crud-queries)
4. [Spatial Queries (PostGIS)](#4-spatial-queries-postgis)
5. [Complex Joins & Relationships](#5-complex-joins--relationships)
6. [Database Views](#6-database-views)
7. [Analytics Queries](#7-analytics-queries)
8. [Performance-Optimized Queries](#8-performance-optimized-queries)
9. [Common Query Patterns](#9-common-query-patterns)
10. [Query Cookbook](#10-query-cookbook)

---

## 1. **What Are Database Queries?**

### 1.1 Simple Explanation

**Database queries** are like asking questions to a super-organized filing cabinet!

**Real-World Analogy**:

```
Physical Filing Cabinet:
┌─────────────────────────────┐
│ "Show me all medical files  │ ← Your question
│  from last month"            │
└─────────────────────────────┘
         ↓
    [Search files]
         ↓
┌─────────────────────────────┐
│ Here are 47 medical files!  │ ← Answer
└─────────────────────────────┘

Database Query:
SELECT * FROM service_requests 
WHERE service_type = 'MEDICAL' 
  AND created_at >= '2026-04-01'
```

**That's it!** Queries are just questions in a special language (SQL).

---

### 1.2 The 4 Basic Operations (CRUD)

Every database operation is one of these:

| Operation | SQL Command | What It Does | Real-World Example |
|-----------|-------------|--------------|---------------------|
| **C**reate | INSERT | Add new data | Register new user |
| **R**ead | SELECT | Get existing data | View service requests |
| **U**pdate | UPDATE | Change data | Mark service complete |
| **D**elete | DELETE | Remove data | Cancel request |

**Plus Special Operations**:
- **Spatial Queries**: Find things near me on a map
- **Joins**: Combine related data
- **Views**: Pre-saved queries for quick access

---

### 1.3 What Makes IDRM Special? PostGIS!

**Regular Database**:
```sql
-- Can only do: "Find user by ID"
SELECT * FROM users WHERE user_id = '123';
```

**PostGIS (Spatial Database)**:
```sql
-- Can do: "Find all services within 5km of my location"
SELECT * FROM service_requests 
WHERE ST_DWithin(
  location,
  ST_MakePoint(78.4867, 17.3850),
  5000  -- 5km in meters
);
```

**Why this matters**: Disaster response needs "near me" queries!

---

## 2. **Quick Reference: All Query Types**

### 2.1 Complete Query Catalog

| # | Query Type | Purpose | Frequency | Complexity |
|---|------------|---------|-----------|------------|
| **BASIC CRUD** |
| 1 | Insert User | Create account | High | 🟢 Easy |
| 2 | Get User | Fetch profile | High | 🟢 Easy |
| 3 | Update User | Edit profile | Medium | 🟢 Easy |
| 4 | Delete User | Remove account | Low | 🟢 Easy |
| 5 | Insert Service | Create request | High | 🟢 Easy |
| 6 | Get Service | View request | High | 🟢 Easy |
| 7 | Update Service | Change status | High | 🟢 Easy |
| 8 | List Services | Browse requests | High | 🟡 Medium |
| **SPATIAL QUERIES** |
| 9 | Find Nearby | Services within radius | High | 🟡 Medium |
| 10 | Distance Calculation | How far away? | High | 🟡 Medium |
| 11 | Within Polygon | Services in area | Medium | 🟡 Medium |
| 12 | Clustering | Group nearby services | Medium | 🔴 Hard |
| 13 | Route Planning | Path between points | Low | 🔴 Hard |
| **JOINS** |
| 14 | Service + User | Request with requestor | High | 🟡 Medium |
| 15 | Service + Provider | Request with assigned | High | 🟡 Medium |
| 16 | Service + Organization | Provider's org | Medium | 🟡 Medium |
| 17 | Full Service Details | Everything joined | Medium | 🔴 Hard |
| **ANALYTICS** |
| 18 | Count by Type | How many medical? | High | 🟢 Easy |
| 19 | Count by Status | How many pending? | High | 🟢 Easy |
| 20 | Avg Response Time | Performance metric | Medium | 🟡 Medium |
| 21 | Provider Rankings | Top performers | Medium | 🟡 Medium |
| 22 | Time-Series Data | Requests per day | Medium | 🔴 Hard |
| **VIEWS** |
| 23 | Active Services View | Pre-filtered list | High | 🟢 Easy |
| 24 | Dashboard View | Pre-aggregated metrics | High | 🟡 Medium |
| 25 | Map View | GeoJSON ready data | High | 🟡 Medium |

**Total Queries**: 25 essential queries

---

### 2.2 Usage Statistics

**How often you'll use each type**:

```
Daily Use (10+ times/day):
├─ Basic CRUD (Users, Services)      60%
├─ Spatial Queries (Find Nearby)     25%
├─ Simple Joins                      10%
└─ Analytics (Counts)                 5%

Weekly Use (1-10 times/week):
├─ Complex Joins                     40%
├─ Advanced Spatial (Clustering)     30%
└─ Complex Analytics                 30%

Monthly Use (as needed):
├─ Route Planning                    50%
└─ Data Export                       50%
```

---

## 3. **Basic CRUD Queries**

### 3.1 INSERT - Creating New Records

**What it does**: Add new data to a table

**Analogy**: Like writing a new entry in a notebook

#### **Query #1: Insert New User**

```sql
-- Create a new user account
INSERT INTO users (
    user_id,
    email,
    password_hash,
    full_name,
    phone,
    role,
    created_at
) VALUES (
    gen_random_uuid(),                    -- Auto-generate ID
    'john@example.com',                   -- Email
    '$2b$12$hashedpasswordhere',         -- Password (hashed!)
    'John Doe',                           -- Full name
    '9876543210',                         -- Phone
    'CITIZEN',                            -- Role
    NOW()                                 -- Current timestamp
)
RETURNING user_id, email, created_at;
```

**Explanation for Beginners**:
- `INSERT INTO users`: "Put new data into the users table"
- `(user_id, email, ...)`: "These are the columns I'm filling"
- `VALUES (...)`: "Here are the actual values"
- `gen_random_uuid()`: "Generate a unique ID automatically"
- `NOW()`: "Use the current date/time"
- `RETURNING`: "Show me what was created"

**Result**:
```
user_id                              | email              | created_at
-------------------------------------|--------------------|--------------------------
a1b2c3d4-e5f6-7890-abcd-ef1234567890 | john@example.com   | 2026-05-16 10:30:00+00
```

---

#### **Query #2: Insert New Service Request**

```sql
-- Create a new service request
INSERT INTO service_requests (
    service_id,
    requestor_id,
    service_type,
    priority,
    location,
    address,
    description,
    privacy_level,
    status,
    created_at
) VALUES (
    gen_random_uuid(),
    'a1b2c3d4-e5f6-7890-abcd-ef1234567890',  -- User ID from above
    'MEDICAL',
    'CRITICAL',
    ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326),  -- GPS coordinates
    'Charminar, Hyderabad, Telangana 500002',
    'Urgent medical attention needed for elderly person',
    'PROTECTED',
    'SUBMITTED',
    NOW()
)
RETURNING service_id, service_type, status, created_at;
```

**Spatial Part Explained**:
```sql
ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)
│          │           │       │           │
│          │           │       │           └─ SRID 4326 = GPS coordinates
│          │           │       └───────────── Latitude
│          │           └───────────────────── Longitude
│          └───────────────────────────────── Create a point
└──────────────────────────────────────────── Set coordinate system
```

**Think of it as**: "Make a pin on a map at these GPS coordinates"

---

### 3.2 SELECT - Reading Data

**What it does**: Get data from a table

**Analogy**: Like asking "show me all red files"

#### **Query #3: Get User by ID**

```sql
-- Fetch a specific user's profile
SELECT 
    user_id,
    email,
    full_name,
    phone,
    role,
    is_verified,
    created_at
FROM users
WHERE user_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

**Explanation**:
- `SELECT user_id, email, ...`: "I want these columns"
- `FROM users`: "From the users table"
- `WHERE user_id = '...'`: "Only the row matching this ID"

**Result**:
```
user_id      | email            | full_name | role    | is_verified
-------------|------------------|-----------|---------|-------------
a1b2c3d4...  | john@example.com | John Doe  | CITIZEN | true
```

---

#### **Query #4: List All Medical Services**

```sql
-- Get all medical service requests
SELECT 
    service_id,
    service_type,
    priority,
    status,
    address,
    created_at,
    ST_AsText(location) AS location_readable  -- Convert GPS to text
FROM service_requests
WHERE service_type = 'MEDICAL'
ORDER BY created_at DESC
LIMIT 20;
```

**New Concepts**:
- `ST_AsText(location)`: Converts GPS point to readable text like "POINT(78.4867 17.3850)"
- `ORDER BY created_at DESC`: Newest first
- `LIMIT 20`: Only show 20 results

---

#### **Query #5: List Services with Filters**

```sql
-- Get critical medical services from last week
SELECT 
    service_id,
    priority,
    status,
    address,
    created_at
FROM service_requests
WHERE service_type = 'MEDICAL'
    AND priority = 'CRITICAL'
    AND status IN ('SUBMITTED', 'APPROVED', 'IN_PROGRESS')
    AND created_at >= NOW() - INTERVAL '7 days'
ORDER BY created_at DESC;
```

**Filter Breakdown**:
- `service_type = 'MEDICAL'`: Only medical
- `priority = 'CRITICAL'`: Only critical
- `status IN (...)`: Status is one of these
- `created_at >= NOW() - INTERVAL '7 days'`: Last 7 days

---

### 3.3 UPDATE - Changing Data

**What it does**: Modify existing data

**Analogy**: Like crossing out old info and writing new

#### **Query #6: Update Service Status**

```sql
-- Mark service as completed
UPDATE service_requests
SET 
    status = 'COMPLETED',
    completed_at = NOW(),
    updated_at = NOW()
WHERE service_id = 'f9e8d7c6-b5a4-3210-fedc-ba9876543210'
    AND status = 'IN_PROGRESS'  -- Safety check: only if in progress
RETURNING service_id, status, completed_at;
```

**Safety Feature**:
- `WHERE status = 'IN_PROGRESS'`: Only update if currently in progress
- Prevents accidentally completing an already-completed service

---

#### **Query #7: Assign Provider to Service**

```sql
-- Assign a provider to a service request
UPDATE service_requests
SET 
    assigned_to = 'p1b2c3d4-e5f6-7890-abcd-ef1234567890',  -- Provider ID
    status = 'ASSIGNED',
    updated_at = NOW()
WHERE service_id = 'f9e8d7c6-b5a4-3210-fedc-ba9876543210'
    AND status = 'APPROVED'  -- Only assign if approved
RETURNING service_id, assigned_to, status;
```

---

### 3.4 DELETE - Removing Data

**What it does**: Remove data from table

**Analogy**: Like throwing away a file

#### **Query #8: Delete (Soft Delete)**

```sql
-- Soft delete: mark as cancelled instead of removing
UPDATE service_requests
SET 
    status = 'CANCELLED',
    updated_at = NOW()
WHERE service_id = 'f9e8d7c6-b5a4-3210-fedc-ba9876543210'
    AND requestor_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'  -- Security: only own requests
    AND status IN ('SUBMITTED', 'APPROVED')  -- Only if not in progress
RETURNING service_id, status;
```

**Why Soft Delete?**
- ✅ Keep audit trail
- ✅ Can undo if needed
- ✅ Analytics still work
- ❌ Real DELETE loses data forever!

---

## 4. **Spatial Queries (PostGIS)**

### 4.1 Understanding Spatial Queries

**What are they?** Queries that work with maps and locations!

**Why they matter**: Disaster response is all about "where" things are!

---

### 4.2 Find Nearby Services

**Use Case**: "Show me all medical services within 5km of my location"

#### **Query #9: Find Services Within Radius**

```sql
-- Find all services within 5km of Charminar
SELECT 
    service_id,
    service_type,
    priority,
    status,
    address,
    ST_Distance(
        location,
        ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)
    ) AS distance_meters
FROM service_requests
WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326),
    5000  -- 5km = 5000 meters
)
    AND status IN ('APPROVED', 'ASSIGNED', 'IN_PROGRESS')
ORDER BY distance_meters ASC
LIMIT 20;
```

**Breaking Down the Spatial Magic**:

```sql
ST_MakePoint(78.4867, 17.3850)
│             │       │
│             │       └─ Latitude (North-South: 17.3850°N)
│             └───────── Longitude (East-West: 78.4867°E)
└─────────────────────── Make a GPS point

ST_SetSRID(..., 4326)
│              │
│              └─ SRID 4326 = WGS84 (GPS coordinate system)
└────────────── Set the coordinate reference system

ST_DWithin(location, point, 5000)
│          │        │     │
│          │        │     └─ Distance in meters (5km)
│          │        └─────── The point to search from
│          └──────────────── Column with GPS data
└─────────────────────────── "Within distance of"

ST_Distance(location, point)
└─ Calculate exact distance in meters
```

**Result**:
```
service_id   | service_type | priority | address         | distance_meters
-------------|--------------|----------|-----------------|----------------
f9e8d7c6...  | MEDICAL      | CRITICAL | Old City        | 850.5
e8d7c6b5...  | FOOD         | HIGH     | Charminar       | 1250.3
d7c6b5a4...  | SHELTER      | MEDIUM   | Falaknuma       | 3200.7
```

---

### 4.3 Distance Calculations

#### **Query #10: Calculate Distance Between Two Points**

```sql
-- How far is the provider from the service location?
SELECT 
    s.service_id,
    s.address AS service_location,
    u.full_name AS provider_name,
    ST_Distance(
        s.location,
        u.current_location
    ) AS distance_meters,
    ROUND(
        ST_Distance(s.location, u.current_location) / 1000.0, 
        2
    ) AS distance_km
FROM service_requests s
JOIN users u ON s.assigned_to = u.user_id
WHERE s.status = 'ASSIGNED';
```

**Conversion to KM**:
```sql
ST_Distance(...) / 1000.0
│                  │
│                  └─ Divide by 1000 to convert meters to kilometers
└──────────────────── Distance in meters

ROUND(..., 2)
└─ Round to 2 decimal places (e.g., 3.45 km)
```

---

### 4.4 Within Polygon (Area Search)

#### **Query #11: Find Services in a District**

```sql
-- Find all services within Hyderabad district boundaries
SELECT 
    service_id,
    service_type,
    address,
    ST_AsText(location) AS coordinates
FROM service_requests
WHERE ST_Within(
    location,
    ST_GeomFromText(
        'POLYGON((
            78.3 17.3,
            78.6 17.3,
            78.6 17.5,
            78.3 17.5,
            78.3 17.3
        ))',
        4326
    )
)
AND status != 'CANCELLED';
```

**Polygon Explained**:
```
        (78.3, 17.5) ────── (78.6, 17.5)
              │                    │
              │    Hyderabad       │
              │     District       │
              │                    │
        (78.3, 17.3) ────── (78.6, 17.3)

First and last point must be the same to close the polygon!
```

---

### 4.5 Clustering Nearby Services

#### **Query #12: K-Means Clustering**

```sql
-- Group nearby services into 5 clusters for visualization
SELECT 
    ST_ClusterKMeans(location, 5) OVER () AS cluster_id,
    service_id,
    service_type,
    priority,
    address,
    ST_AsText(location) AS coordinates
FROM service_requests
WHERE status IN ('APPROVED', 'ASSIGNED', 'IN_PROGRESS')
ORDER BY cluster_id;
```

**What This Does**:
- Groups services into 5 clusters
- Each cluster has nearby services
- Used for map visualization (show "12 services" instead of 12 markers)

**Result**:
```
cluster_id | service_id   | service_type | address
-----------|--------------|--------------|----------------
0          | f9e8d7c6...  | MEDICAL      | Old City
0          | e8d7c6b5...  | FOOD         | Charminar
1          | d7c6b5a4...  | SHELTER      | Secunderabad
1          | c6b5a4b3...  | MEDICAL      | Paradise
```

---

### 4.6 Get Cluster Centers

#### **Query #13: Find Center of Each Cluster**

```sql
-- Get the center point of each cluster
WITH clustered AS (
    SELECT 
        ST_ClusterKMeans(location, 5) OVER () AS cluster_id,
        location,
        service_type,
        priority
    FROM service_requests
    WHERE status IN ('APPROVED', 'ASSIGNED', 'IN_PROGRESS')
)
SELECT 
    cluster_id,
    COUNT(*) AS service_count,
    ST_AsText(ST_Centroid(ST_Collect(location))) AS cluster_center,
    array_agg(DISTINCT service_type) AS service_types,
    COUNT(*) FILTER (WHERE priority = 'CRITICAL') AS critical_count
FROM clustered
GROUP BY cluster_id
ORDER BY critical_count DESC;
```

**Result**:
```
cluster_id | service_count | cluster_center           | service_types        | critical_count
-----------|---------------|--------------------------|----------------------|---------------
0          | 12            | POINT(78.48 17.38)       | {MEDICAL,FOOD}       | 3
1          | 8             | POINT(78.52 17.42)       | {SHELTER,MEDICAL}    | 1
```

---

## 5. **Complex Joins & Relationships**

### 5.1 Understanding Joins

**What are joins?** Combining data from multiple tables!

**Analogy**: Like matching employee badges with parking permits

```
Table: employees          Table: parking
┌────────┬────────┐      ┌────────┬────────┐
│ emp_id │ name   │      │ emp_id │ spot   │
├────────┼────────┤      ├────────┼────────┤
│ 1      │ Alice  │  ←→  │ 1      │ A-12   │
│ 2      │ Bob    │      │ 2      │ B-05   │
└────────┴────────┘      └────────┴────────┘

JOIN: "Show me each employee AND their parking spot"
Result: Alice → A-12, Bob → B-05
```

---

### 5.2 Service with Requestor Details

#### **Query #14: Service Request + User Info**

```sql
-- Get service requests with requestor information
SELECT 
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    s.address,
    s.created_at,
    u.full_name AS requestor_name,
    u.email AS requestor_email,
    u.phone AS requestor_phone,
    ST_AsText(s.location) AS coordinates
FROM service_requests s
INNER JOIN users u ON s.requestor_id = u.user_id
WHERE s.status IN ('APPROVED', 'ASSIGNED', 'IN_PROGRESS')
ORDER BY s.created_at DESC
LIMIT 20;
```

**Join Explained**:
```sql
FROM service_requests s
INNER JOIN users u ON s.requestor_id = u.user_id
│          │     │ │  │              │
│          │     │ │  │              └─ Match this column
│          │     │ │  └────────────────── To this column
│          │     │ └───────────────────── Condition
│          │     └─────────────────────── Alias for users
│          └───────────────────────────── Join users table
└──────────────────────────────────────── Start from service_requests
```

**Result**: Each service row now includes requestor details!

---

### 5.3 Service with Provider and Organization

#### **Query #15: Complete Service Details**

```sql
-- Get service with requestor, provider, and organization
SELECT 
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    s.address,
    
    -- Requestor info
    req.full_name AS requestor_name,
    req.phone AS requestor_phone,
    
    -- Provider info
    prov.full_name AS provider_name,
    prov.phone AS provider_phone,
    
    -- Organization info
    org.name AS organization_name,
    org.type AS organization_type,
    
    -- Timestamps
    s.created_at,
    s.completed_at,
    
    -- Spatial data
    ST_AsText(s.location) AS service_location,
    CASE 
        WHEN prov.current_location IS NOT NULL THEN
            ROUND(ST_Distance(s.location, prov.current_location)::numeric / 1000, 2)
        ELSE NULL
    END AS provider_distance_km
    
FROM service_requests s
INNER JOIN users req ON s.requestor_id = req.user_id
LEFT JOIN users prov ON s.assigned_to = prov.user_id
LEFT JOIN organizations org ON prov.organization_id = org.org_id
WHERE s.service_id = 'f9e8d7c6-b5a4-3210-fedc-ba9876543210';
```

**INNER vs LEFT JOIN**:
```
INNER JOIN: Only show if match exists
LEFT JOIN: Show even if no match (NULL if missing)

Example:
Service assigned_to = NULL
├─ INNER JOIN users → No result (no provider yet)
└─ LEFT JOIN users → Shows service with provider = NULL
```

---

## 6. **Database Views**

### 6.1 What Are Views?

**Views** = Pre-saved queries that act like virtual tables!

**Analogy**: Like a smart folder that auto-updates

```
Instead of running this query every time:
SELECT ... FROM service_requests WHERE status = 'ACTIVE' ...

Create a view once:
CREATE VIEW active_services AS SELECT ...

Then use it like a table:
SELECT * FROM active_services;
```

---

### 6.2 Active Services View

#### **View #1: Active Services for Map Display**

```sql
-- Create view for active services (frequently accessed)
CREATE OR REPLACE VIEW active_services_view AS
SELECT 
    s.service_id,
    s.service_type,
    s.priority,
    s.status,
    s.location,
    s.address,
    s.description,
    s.created_at,
    
    -- Requestor (basic info only for privacy)
    req.full_name AS requestor_name,
    
    -- Provider (if assigned)
    prov.full_name AS provider_name,
    org.name AS organization_name,
    
    -- Time calculations
    EXTRACT(EPOCH FROM (NOW() - s.created_at))/60 AS age_minutes,
    
    -- GeoJSON ready format
    ST_AsGeoJSON(s.location)::json AS location_geojson
    
FROM service_requests s
INNER JOIN users req ON s.requestor_id = req.user_id
LEFT JOIN users prov ON s.assigned_to = prov.user_id
LEFT JOIN organizations org ON prov.organization_id = org.org_id
WHERE s.status IN ('SUBMITTED', 'APPROVED', 'ASSIGNED', 'IN_PROGRESS');
```

**Usage**:
```sql
-- Now just query the view!
SELECT * FROM active_services_view 
WHERE service_type = 'MEDICAL' 
ORDER BY age_minutes DESC;
```

---

### 6.3 Dashboard Metrics View

#### **View #2: Pre-Aggregated Dashboard Data**

```sql
-- Create view for dashboard (expensive aggregations)
CREATE OR REPLACE VIEW dashboard_metrics_view AS
SELECT 
    -- Totals
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE status = 'SUBMITTED') AS submitted_count,
    COUNT(*) FILTER (WHERE status = 'APPROVED') AS approved_count,
    COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress_count,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed_count,
    COUNT(*) FILTER (WHERE status = 'VERIFIED') AS verified_count,
    
    -- By Priority
    COUNT(*) FILTER (WHERE priority = 'CRITICAL') AS critical_count,
    COUNT(*) FILTER (WHERE priority = 'HIGH') AS high_count,
    COUNT(*) FILTER (WHERE priority = 'MEDIUM') AS medium_count,
    COUNT(*) FILTER (WHERE priority = 'LOW') AS low_count,
    
    -- By Service Type
    COUNT(*) FILTER (WHERE service_type = 'MEDICAL') AS medical_count,
    COUNT(*) FILTER (WHERE service_type = 'FOOD') AS food_count,
    COUNT(*) FILTER (WHERE service_type = 'SHELTER') AS shelter_count,
    
    -- Performance Metrics
    AVG(
        EXTRACT(EPOCH FROM (completed_at - created_at))/60
    ) FILTER (WHERE completed_at IS NOT NULL) AS avg_completion_minutes,
    
    (COUNT(*) FILTER (WHERE status = 'COMPLETED')::float / 
     NULLIF(COUNT(*) FILTER (WHERE status IN ('APPROVED', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED')), 0)
    ) AS completion_rate

FROM service_requests
WHERE created_at >= NOW() - INTERVAL '30 days';
```

**Usage**:
```sql
-- Get all metrics instantly!
SELECT * FROM dashboard_metrics_view;
```

**Result**:
```
total_requests | critical_count | medical_count | avg_completion_minutes | completion_rate
---------------|----------------|---------------|------------------------|----------------
1250           | 12             | 350           | 42.5                   | 0.85
```

---

### 6.4 Map GeoJSON View

#### **View #3: Map-Ready GeoJSON**

```sql
-- Create view that outputs GeoJSON for map display
CREATE OR REPLACE VIEW map_geojson_view AS
SELECT 
    json_build_object(
        'type', 'FeatureCollection',
        'features', json_agg(
            json_build_object(
                'type', 'Feature',
                'geometry', ST_AsGeoJSON(location)::json,
                'properties', json_build_object(
                    'service_id', service_id,
                    'service_type', service_type,
                    'priority', priority,
                    'status', status,
                    'address', address,
                    'created_at', created_at,
                    'age_minutes', EXTRACT(EPOCH FROM (NOW() - created_at))/60
                )
            )
        )
    ) AS geojson
FROM service_requests
WHERE status IN ('APPROVED', 'ASSIGNED', 'IN_PROGRESS')
    AND created_at >= NOW() - INTERVAL '7 days';
```

**Usage**:
```sql
-- Get complete GeoJSON for Leaflet/Google Maps
SELECT geojson FROM map_geojson_view;
```

**Result**: Ready-to-use GeoJSON!
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {"type": "Point", "coordinates": [78.4867, 17.3850]},
      "properties": {
        "service_id": "f9e8d7c6...",
        "service_type": "MEDICAL",
        "priority": "CRITICAL"
      }
    }
  ]
}
```

---

## 7. **Analytics Queries**

### 7.1 Count Aggregations

#### **Query #16: Count by Service Type**

```sql
-- How many requests of each type?
SELECT 
    service_type,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed,
    ROUND(
        COUNT(*) FILTER (WHERE status = 'COMPLETED')::numeric / 
        COUNT(*)::numeric * 100, 
        1
    ) AS completion_percentage
FROM service_requests
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY service_type
ORDER BY total DESC;
```

**Result**:
```
service_type | total | completed | completion_percentage
-------------|-------|-----------|----------------------
MEDICAL      | 450   | 380       | 84.4
FOOD         | 350   | 310       | 88.6
SHELTER      | 250   | 200       | 80.0
```

---

#### **Query #17: Count by Priority and Status**

```sql
-- Matrix of priority vs status
SELECT 
    priority,
    COUNT(*) FILTER (WHERE status = 'SUBMITTED') AS submitted,
    COUNT(*) FILTER (WHERE status = 'APPROVED') AS approved,
    COUNT(*) FILTER (WHERE status = 'IN_PROGRESS') AS in_progress,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed,
    COUNT(*) AS total
FROM service_requests
WHERE created_at >= NOW() - INTERVAL '7 days'
GROUP BY priority
ORDER BY 
    CASE priority
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH' THEN 2
        WHEN 'MEDIUM' THEN 3
        WHEN 'LOW' THEN 4
    END;
```

---

### 7.2 Performance Metrics

#### **Query #18: Average Response Time**

```sql
-- How fast are services completed?
SELECT 
    service_type,
    COUNT(*) AS completed_count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))/60) AS avg_minutes,
    MIN(EXTRACT(EPOCH FROM (completed_at - created_at))/60) AS fastest_minutes,
    MAX(EXTRACT(EPOCH FROM (completed_at - created_at))/60) AS slowest_minutes,
    PERCENTILE_CONT(0.5) WITHIN GROUP (
        ORDER BY EXTRACT(EPOCH FROM (completed_at - created_at))/60
    ) AS median_minutes
FROM service_requests
WHERE status = 'COMPLETED'
    AND completed_at IS NOT NULL
    AND created_at >= NOW() - INTERVAL '30 days'
GROUP BY service_type
ORDER BY avg_minutes ASC;
```

**Result**:
```
service_type | completed | avg_minutes | fastest | slowest | median
-------------|-----------|-------------|---------|---------|--------
MEDICAL      | 380       | 35.2        | 8.5     | 120.3   | 32.0
FOOD         | 310       | 45.8        | 12.0    | 180.5   | 42.0
```

---

### 7.3 Provider Rankings

#### **Query #19: Top Performing Providers**

```sql
-- Who are the best providers?
SELECT 
    u.user_id,
    u.full_name,
    org.name AS organization,
    COUNT(*) AS services_completed,
    AVG(sr.rating) AS avg_rating,
    AVG(EXTRACT(EPOCH FROM (sr.completed_at - sr.created_at))/60) AS avg_response_minutes,
    COUNT(*) FILTER (WHERE sr.priority = 'CRITICAL') AS critical_handled
FROM service_requests sr
JOIN users u ON sr.assigned_to = u.user_id
LEFT JOIN organizations org ON u.organization_id = org.org_id
WHERE sr.status = 'VERIFIED'
    AND sr.completed_at >= NOW() - INTERVAL '90 days'
GROUP BY u.user_id, u.full_name, org.name
HAVING COUNT(*) >= 5  -- At least 5 completed services
ORDER BY avg_rating DESC, avg_response_minutes ASC
LIMIT 10;
```

---

### 7.4 Time-Series Data

#### **Query #20: Requests Per Day (Last 30 Days)**

```sql
-- How many requests each day?
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS total_requests,
    COUNT(*) FILTER (WHERE priority = 'CRITICAL') AS critical_requests,
    COUNT(*) FILTER (WHERE service_type = 'MEDICAL') AS medical_requests,
    COUNT(*) FILTER (WHERE status = 'COMPLETED') AS completed_on_same_day
FROM service_requests
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

**Result** (for charting):
```
date       | total_requests | critical | medical | completed
-----------|----------------|----------|---------|----------
2026-05-16 | 52             | 3        | 18      | 45
2026-05-15 | 48             | 2        | 15      | 42
2026-05-14 | 45             | 1        | 12      | 40
```

---

## 8. **Performance-Optimized Queries**

### 8.1 Using Indexes

**What are indexes?** Like a book's index - find things faster!

#### **Query #21: Efficiently Find User's Services**

```sql
-- Fast lookup using index on (requestor_id, status)
SELECT 
    service_id,
    service_type,
    priority,
    status,
    created_at
FROM service_requests
WHERE requestor_id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890'
    AND status IN ('SUBMITTED', 'APPROVED', 'IN_PROGRESS')
ORDER BY created_at DESC;

-- This query uses index: idx_service_requests_requestor_status
```

**Index Definition**:
```sql
CREATE INDEX idx_service_requests_requestor_status 
ON service_requests(requestor_id, status);
```

---

### 8.2 Spatial Index Usage

#### **Query #22: Fast Nearby Search**

```sql
-- Fast spatial search using GIST index
SELECT 
    service_id,
    service_type,
    ST_Distance(
        location,
        ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)
    ) AS distance
FROM service_requests
WHERE ST_DWithin(
    location,
    ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326),
    5000
)
AND status = 'APPROVED'
ORDER BY location <-> ST_SetSRID(ST_MakePoint(78.4867, 17.3850), 4326)
LIMIT 20;

-- This query uses index: idx_service_requests_location_gist
```

**Spatial Index**:
```sql
CREATE INDEX idx_service_requests_location_gist 
ON service_requests USING GIST(location);
```

---

## 9. **Common Query Patterns**

### 9.1 Pagination

```sql
-- Page 2, showing 20 items per page
SELECT 
    service_id,
    service_type,
    status,
    created_at
FROM service_requests
WHERE status = 'APPROVED'
ORDER BY created_at DESC
LIMIT 20 OFFSET 20;  -- Skip first 20 (page 1), show next 20 (page 2)
```

**Formula**:
```
OFFSET = (page_number - 1) × items_per_page

Page 1: OFFSET 0   (show 1-20)
Page 2: OFFSET 20  (show 21-40)
Page 3: OFFSET 40  (show 41-60)
```

---

### 9.2 Search with Filters

```sql
-- Dynamic filter query
SELECT *
FROM service_requests
WHERE 1=1  -- Always true, makes adding filters easier
    AND ($1 IS NULL OR service_type = $1)
    AND ($2 IS NULL OR priority = $2)
    AND ($3 IS NULL OR status = $3)
    AND ($4 IS NULL OR created_at >= $4)
ORDER BY created_at DESC;
```

**Parameterized** (prevents SQL injection):
- `$1` = service_type filter (or NULL to skip)
- `$2` = priority filter (or NULL to skip)
- `$3` = status filter (or NULL to skip)
- `$4` = date filter (or NULL to skip)

---

### 9.3 Full-Text Search

```sql
-- Search service descriptions
SELECT 
    service_id,
    service_type,
    description,
    ts_rank(
        to_tsvector('english', description),
        plainto_tsquery('english', 'medical emergency')
    ) AS relevance
FROM service_requests
WHERE to_tsvector('english', description) @@ plainto_tsquery('english', 'medical emergency')
ORDER BY relevance DESC;
```

---

## 10. **Query Cookbook**

### 10.1 Essential Queries Summary

| Need | Query | Complexity |
|------|-------|------------|
| **Create user** | INSERT INTO users | 🟢 Easy |
| **Create service** | INSERT INTO service_requests | 🟢 Easy |
| **Get my services** | SELECT WHERE requestor_id = me | 🟢 Easy |
| **Find nearby** | SELECT ST_DWithin(...) | 🟡 Medium |
| **Service + user** | SELECT ... JOIN users | 🟡 Medium |
| **Dashboard metrics** | Use dashboard_metrics_view | 🟢 Easy |
| **Map GeoJSON** | Use map_geojson_view | 🟢 Easy |
| **Rankings** | SELECT with AVG, GROUP BY | 🟡 Medium |
| **Time-series** | SELECT DATE(...) GROUP BY | 🟡 Medium |
| **Clustering** | ST_ClusterKMeans | 🔴 Hard |

---

### 10.2 Most Common Operations (95% of Queries)

```sql
-- 1. List user's services
SELECT * FROM service_requests 
WHERE requestor_id = $1 
ORDER BY created_at DESC;

-- 2. Find nearby services
SELECT * FROM service_requests 
WHERE ST_DWithin(location, ST_MakePoint($1, $2), $3);

-- 3. Get service details with user
SELECT s.*, u.full_name 
FROM service_requests s 
JOIN users u ON s.requestor_id = u.user_id 
WHERE s.service_id = $1;

-- 4. Update service status
UPDATE service_requests 
SET status = $1, updated_at = NOW() 
WHERE service_id = $2;

-- 5. Get dashboard metrics
SELECT * FROM dashboard_metrics_view;
```

---

## 🎯 **Summary for Beginners**

### **What You Learned**:

1. ✅ **CRUD Operations** - Create, Read, Update, Delete data
2. ✅ **Spatial Queries** - Find things near a location (PostGIS)
3. ✅ **Joins** - Combine data from multiple tables
4. ✅ **Views** - Pre-saved queries for speed
5. ✅ **Analytics** - Count, average, rank data
6. ✅ **Performance** - Use indexes for speed

### **25 Essential Queries**:
- 8 Basic CRUD
- 6 Spatial queries
- 4 Joins
- 3 Views
- 4 Analytics

### **Next Steps**:
1. Practice CRUD queries (start here!)
2. Try spatial queries (find nearby)
3. Use views (easier than raw queries)
4. Add analytics (dashboard)

---

**Document Complete!**  
**Total Queries Documented**: 25+  
**Difficulty**: 🟢 Beginner-friendly  
**Ready for Development**: ✅ YES

**See Also**:
- [22-DATABASE-DESIGN.md](22-DATABASE-DESIGN.md) - Database schema
- [25-BACKEND-IMPLEMENTATION.md](25-BACKEND-IMPLEMENTATION.md) - Using these queries in code
- [42-VERIFICATION-CHECKLISTS.md](42-VERIFICATION-CHECKLISTS.md) - Testing queries
