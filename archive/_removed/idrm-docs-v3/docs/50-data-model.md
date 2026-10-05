# IDRM v3 · Data Model & Database Design

<!-- IDRM-CLEANUP doc=v3-50-data status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — data model → `docs/mvp/50`
> Canonical schema = [`../../../../docs/mvp/50-data-model.md`](../../../../docs/mvp/50-data-model.md) (13 tables,
> PostGIS SRID 4326, native enums = wire values). For section-level data mapping see the v0 Section Map
> [`../../idrm-docs-v0/docs/50-data-model.md`](../../idrm-docs-v0/docs/50-data-model.md). Financial/analytics tables → FFP.
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Document (specification) · Audience: DBAs, backend devs · Status: Archived — v3 historical generation*
*Consolidated from: 22-DATABASE-DESIGN.md, DATABASE-SCHEMAS-v3.md*

## Contents
- [IDRM: Database Design](#idrm-database-design)
- [IDRM: Database Schemas - Version 3](#idrm-database-schemas---version-3)

---

## IDRM: Database Design

### Complete PostgreSQL + PostGIS Schema

**Version**: 3.0 Consolidated  
**Audience**: Database administrators, backend developers  
**Reading Time**: 60 minutes  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [Overview](#1-overview)
2. [Database Architecture](#2-database-architecture)
3. [Core Tables](#3-core-tables)
4. [Relationship Diagrams](#4-relationship-diagrams)
5. [Indexes & Constraints](#5-indexes--constraints)
6. [Sample Queries](#6-sample-queries)
7. [Migration Strategy](#7-migration-strategy)

---

### 1. **Overview**

#### 1.1 Database Technology

**PostgreSQL 16** with **PostGIS 3.4** extension for geospatial data.

**Why PostgreSQL + PostGIS?**:
- Industry-leading geospatial support
- 4-5x faster spatial queries than alternatives
- ACID compliance for data integrity
- Rich set of spatial functions (500+)
- Excellent performance at scale

#### 1.2 Schema Organization

```
idrm_db (Database)
├── public schema (default)
│   ├── Users & Authentication
│   ├── Service Requests
│   ├── Service Providers
│   ├── Disaster Events
│   ├── Financial Transactions
│   └── System Tables
└── Extensions
    ├── postgis (spatial data)
    ├── postgis_topology
    └── uuid-ossp (UUID generation)
```

---

### 2. **Database Architecture**

#### 2.1 Entity Relationship Overview

```
Users (1) ────< (N) ServiceRequests
                    │
                    ├──> (1) ServiceProvider (assigned)
                    └──> (1) DisasterEvent

ServiceProvider (1) ────< (N) ProviderCapacity
                │
                └───< (N) ProviderServiceAreas (PostGIS)

DisasterEvent (1) ────< (N) ServiceRequests
              │
              └───< (N) EventBoundaries (PostGIS)

Donations (1) ────< (N) Transactions
          │
          └──> (N) FundAllocations
```

---

### 3. **Core Tables**

#### 3.1 Users & Authentication

##### **users** table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(50) NOT NULL DEFAULT 'CITIZEN',
    organization_id UUID REFERENCES service_providers(id),
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT phone_format CHECK (phone ~* '^\d{10}$' OR phone IS NULL)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_org ON users(organization_id);
```

**Roles**: CITIZEN, VOLUNTEER, ORGANIZER, SERVICE_PROVIDER, MANAGER, EXECUTIVE, EVENT_ADMIN, SYSTEM_ADMIN, AUDITOR

---

##### **password_resets** table
```sql
CREATE TABLE password_resets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_expiry CHECK (expires_at > created_at)
);

CREATE INDEX idx_password_reset_token ON password_resets(token);
CREATE INDEX idx_password_reset_user ON password_resets(user_id);
```

---

#### 3.2 Service Management

##### **service_requests** table
```sql
CREATE TABLE service_requests (
    id SERIAL PRIMARY KEY,
    requester_id UUID NOT NULL REFERENCES users(id),
    service_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,  -- PostGIS: WGS 84
    address VARCHAR(500),
    urgency VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    privacy_level VARCHAR(20) NOT NULL DEFAULT 'PROTECTED',
    assigned_provider_id UUID REFERENCES service_providers(id),
    disaster_event_id INTEGER REFERENCES disaster_events(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_service_type CHECK (
        service_type IN ('MEDICAL', 'FOOD', 'SHELTER', 'RESCUE', 'WATER', 'CLOTHING', 'OTHER')
    ),
    CONSTRAINT valid_urgency CHECK (
        urgency IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')
    ),
    CONSTRAINT valid_status CHECK (
        status IN ('DRAFT', 'SUBMITTED', 'APPROVED', 'ASSIGNED', 'IN_PROGRESS', 
                  'COMPLETED', 'VERIFIED', 'DISPUTED', 'REJECTED', 'CLOSED')
    ),
    CONSTRAINT valid_privacy CHECK (
        privacy_level IN ('PUBLIC', 'PROTECTED', 'PRIVATE')
    )
);

-- Spatial index (CRITICAL for performance)
CREATE INDEX idx_service_location ON service_requests USING GIST(location);

-- Other indexes
CREATE INDEX idx_service_status ON service_requests(status);
CREATE INDEX idx_service_type ON service_requests(service_type);
CREATE INDEX idx_service_urgency ON service_requests(urgency);
CREATE INDEX idx_service_requester ON service_requests(requester_id);
CREATE INDEX idx_service_provider ON service_requests(assigned_provider_id);
CREATE INDEX idx_service_event ON service_requests(disaster_event_id);
CREATE INDEX idx_service_created ON service_requests(created_at DESC);
```

---

##### **service_history** table
```sql
CREATE TABLE service_history (
    id SERIAL PRIMARY KEY,
    service_id INTEGER NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    old_status VARCHAR(50) NOT NULL,
    new_status VARCHAR(50) NOT NULL,
    changed_by UUID NOT NULL REFERENCES users(id),
    reason TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_history_service ON service_history(service_id);
CREATE INDEX idx_history_timestamp ON service_history(timestamp DESC);
```

---

#### 3.3 Service Providers

##### **service_providers** table
```sql
CREATE TABLE service_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(50) NOT NULL,
    registration_number VARCHAR(100) UNIQUE,
    service_types TEXT[] NOT NULL,  -- Array of service types
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    location GEOMETRY(Point, 4326),  -- Office/headquarters location
    service_area GEOMETRY(Polygon, 4326),  -- Geographic coverage area
    max_capacity INTEGER DEFAULT 10,
    current_load INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_org_type CHECK (
        organization_type IN ('NGO', 'GOVERNMENT', 'PRIVATE', 'VOLUNTEER_GROUP')
    ),
    CONSTRAINT valid_capacity CHECK (max_capacity > 0),
    CONSTRAINT valid_load CHECK (current_load >= 0 AND current_load <= max_capacity),
    CONSTRAINT valid_rating CHECK (rating >= 0.00 AND rating <= 5.00)
);

-- Spatial indexes
CREATE INDEX idx_provider_location ON service_providers USING GIST(location);
CREATE INDEX idx_provider_service_area ON service_providers USING GIST(service_area);

-- Other indexes
CREATE INDEX idx_provider_type ON service_providers(organization_type);
CREATE INDEX idx_provider_services ON service_providers USING GIN(service_types);
```

---

#### 3.4 Disaster Events

##### **disaster_events** table
```sql
CREATE TABLE disaster_events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    area GEOMETRY(Polygon, 4326) NOT NULL,  -- Affected geographic area
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_event_type CHECK (
        event_type IN ('FLOOD', 'EARTHQUAKE', 'CYCLONE', 'DROUGHT', 'LANDSLIDE', 
                      'FIRE', 'INDUSTRIAL_ACCIDENT', 'OTHER')
    ),
    CONSTRAINT valid_severity CHECK (
        severity IN ('MINOR', 'MODERATE', 'SEVERE', 'CATASTROPHIC')
    ),
    CONSTRAINT valid_status CHECK (
        status IN ('ACTIVE', 'RESOLVED', 'CLOSED')
    ),
    CONSTRAINT valid_dates CHECK (end_date IS NULL OR end_date > start_date)
);

-- Spatial index
CREATE INDEX idx_event_area ON disaster_events USING GIST(area);

-- Other indexes
CREATE INDEX idx_event_type ON disaster_events(event_type);
CREATE INDEX idx_event_status ON disaster_events(status);
CREATE INDEX idx_event_dates ON disaster_events(start_date, end_date);
```

---

#### 3.5 Financial

##### **donations** table
```sql
CREATE TABLE donations (
    id SERIAL PRIMARY KEY,
    donor_name VARCHAR(255),  -- NULL if anonymous
    donor_email VARCHAR(255),
    amount DECIMAL(12,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_method VARCHAR(50),
    transaction_id VARCHAR(255) UNIQUE,
    is_anonymous BOOLEAN DEFAULT FALSE,
    disaster_event_id INTEGER REFERENCES disaster_events(id),
    donated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_amount CHECK (amount > 0)
);

CREATE INDEX idx_donation_event ON donations(disaster_event_id);
CREATE INDEX idx_donation_date ON donations(donated_at DESC);
```

---

##### **fund_allocations** table
```sql
CREATE TABLE fund_allocations (
    id SERIAL PRIMARY KEY,
    disaster_event_id INTEGER REFERENCES disaster_events(id),
    amount DECIMAL(12,2) NOT NULL,
    purpose TEXT NOT NULL,
    allocated_by UUID NOT NULL REFERENCES users(id),
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT positive_amount CHECK (amount > 0)
);

CREATE INDEX idx_allocation_event ON fund_allocations(disaster_event_id);
```

---

### 4. **Relationship Diagrams**

#### 4.1 Core Entity Relationships

```
User ──┐
       ├─< ServiceRequest ──> ServiceProvider
       │                  └──> DisasterEvent
       │
       └─< ServiceProvider (as member)
```

#### 4.2 Complete Schema (30+ tables)

**Full table list**:
1. users
2. password_resets
3. email_verifications
4. user_roles
5. service_requests
6. service_history
7. service_assignments
8. service_feedback
9. service_providers
10. provider_capacity
11. provider_service_areas
12. provider_performance
13. disaster_events
14. event_updates
15. disaster_boundaries
16. donations
17. fund_allocations
18. transactions
19. notifications_log
20. audit_log
21. system_config
22. (and 9 more support tables)

---

### 5. **Indexes & Constraints**

#### 5.1 Spatial Indexes (PostGIS)

```sql
-- GIST indexes for spatial queries (CRITICAL)
CREATE INDEX idx_service_location ON service_requests USING GIST(location);
CREATE INDEX idx_provider_location ON service_providers USING GIST(location);
CREATE INDEX idx_provider_service_area ON service_providers USING GIST(service_area);
CREATE INDEX idx_event_area ON disaster_events USING GIST(area);
```

**Why GIST?** Generalized Search Tree - optimized for 2D spatial data, makes nearby/within queries 100-1000x faster.

#### 5.2 Regular B-Tree Indexes

```sql
-- Frequently queried columns
CREATE INDEX idx_service_status ON service_requests(status);
CREATE INDEX idx_service_created ON service_requests(created_at DESC);
CREATE INDEX idx_users_email ON users(email);
```

---

### 6. **Sample Queries**

#### 6.1 Find Services Within Radius

```sql
-- Find all MEDICAL service requests within 5km of Chennai
SELECT 
    id,
    service_type,
    description,
    ST_Distance(
        location::geography,
        ST_MakePoint(80.2707, 13.0827)::geography
    ) / 1000 as distance_km
FROM service_requests
WHERE 
    service_type = 'MEDICAL'
    AND status IN ('APPROVED', 'ASSIGNED')
    AND ST_DWithin(
        location::geography,
        ST_MakePoint(80.2707, 13.0827)::geography,
        5000  -- 5km in meters
    )
ORDER BY distance_km;
```

#### 6.2 Find Providers Covering Area

```sql
-- Find service providers whose coverage area includes a specific location
SELECT 
    organization_name,
    service_types,
    contact_phone
FROM service_providers
WHERE 
    is_active = TRUE
    AND ST_Contains(
        service_area,
        ST_SetSRID(ST_MakePoint(80.2707, 13.0827), 4326)
    )
    AND 'MEDICAL' = ANY(service_types);
```

#### 6.3 Service Request Statistics

```sql
-- Get service request summary by status
SELECT 
    status,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) / 3600 as avg_hours
FROM service_requests
WHERE disaster_event_id = 1
GROUP BY status
ORDER BY count DESC;
```

---

### 7. **Migration Strategy**

#### 7.1 Initial Setup

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create all tables in order (respecting dependencies)
-- 1. Independent tables first
CREATE TABLE users (...);
CREATE TABLE disaster_events (...);

-- 2. Dependent tables next
CREATE TABLE service_requests (...);
CREATE TABLE service_providers (...);

-- 3. Junction/history tables last
CREATE TABLE service_history (...);
CREATE TABLE fund_allocations (...);
```

#### 7.2 Data Seeding

```sql
-- Insert admin user
INSERT INTO users (email, hashed_password, full_name, role, is_verified)
VALUES ('admin@idrm.gov.in', '<bcrypt_hash>', 'System Admin', 'SYSTEM_ADMIN', TRUE);

-- Insert sample disaster event
INSERT INTO disaster_events (event_name, event_type, severity, area, start_date, created_by)
VALUES (
    'Chennai Floods 2026',
    'FLOOD',
    'SEVERE',
    ST_GeomFromText('POLYGON((80.1 13.0, 80.3 13.0, 80.3 13.2, 80.1 13.2, 80.1 13.0))', 4326),
    '2026-05-01',
    (SELECT id FROM users WHERE role = 'SYSTEM_ADMIN' LIMIT 1)
);
```

---

### ✅ **Database Design Summary**

**Schema includes**:
- ✅ 30+ tables covering all system functionality
- ✅ PostGIS spatial data types for geographic queries
- ✅ Proper indexes (spatial + regular) for performance
- ✅ Foreign key constraints for referential integrity
- ✅ Check constraints for data validation
- ✅ Audit trails (history tables)

**Developers can now**:
- Understand complete data model
- Write efficient queries
- Implement data access layer
- Maintain database integrity

---

### 📖 **What's Next?**

→ [23-API-SPECIFICATION.md](23-API-SPECIFICATION.md) - Complete API reference  
→ [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md) - Local setup guide

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Previous**: [21-TECHNICAL-DESIGN.md](21-TECHNICAL-DESIGN.md)  
**Next**: [23-API-SPECIFICATION.md](23-API-SPECIFICATION.md)

---

## IDRM: Database Schemas - Version 3

### Complete SQL Schema Definitions

**Document Version**: 3.0  
**Date**: May 24, 2026  
**Status**: ✅ Production-Ready  
**Database**: PostgreSQL 15.5 + PostGIS 3.3  
**Target Audience**: Database administrators, backend developers

---

### 📚 **Table of Contents**

1. [Schema Overview](#1-schema-overview)
2. [Core Tables](#2-core-tables)
3. [Reference Tables](#3-reference-tables)
4. [Indexes](#4-indexes)
5. [Views](#5-views)
6. [Functions](#6-functions)
7. [Triggers](#7-triggers)
8. [Constraints](#8-constraints)
9. [Migrations](#9-migrations)

---

## 1. **Schema Overview**

### 1.1 Database Setup

```sql
-- Create database
CREATE DATABASE idrm
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Connect to database
\c idrm

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";      -- UUID generation
CREATE EXTENSION IF NOT EXISTS "postgis";        -- Geospatial support
CREATE EXTENSION IF NOT EXISTS "pg_trgm";        -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "btree_gist";     -- GiST index support
```

---

### 1.2 Schema Diagram

```
┌──────────────┐
│    users     │
└──────┬───────┘
       │ 1
       │
       │ N
┌──────▼──────────────────┐
│  service_requests       │
└──────┬──────────────────┘
       │ N                  
       │                    
       │ 1                  
┌──────▼──────────────┐
│  organizations      │
└─────────────────────┘

┌──────────────────┐
│  notifications   │
└──────────────────┘

┌──────────────────┐
│   audit_logs     │
└──────────────────┘
```

---

## 2. **Core Tables**

### 2.1 users Table

```sql
-- ============================================================================
-- TABLE: users
-- PURPOSE: Store all user accounts (citizens, providers, coordinators, admins)
-- ============================================================================

CREATE TABLE users (
    -- Primary Key
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    
    -- Role & Status
    role VARCHAR(50) NOT NULL DEFAULT 'CITIZEN'
        CHECK (role IN (
            'CITIZEN',
            'PROVIDER',
            'VOLUNTEER',
            'EVENT_MANAGER',
            'DM_AUTHORITY',
            'ADMIN'
        )),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Preferences (JSONB for flexibility)
    preferences JSONB NOT NULL DEFAULT '{
        "language": "en",
        "notifications": {
            "email": true,
            "sms": true,
            "push": false
        },
        "theme": "light"
    }'::jsonb,
    
    -- Metadata
    email_verified_at TIMESTAMP,
    phone_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    last_login_ip INET,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT email_format CHECK (
        email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    CONSTRAINT phone_format CHECK (
        phone IS NULL OR phone ~* '^\+[1-9][0-9]{1,14}$'
    ),
    CONSTRAINT full_name_length CHECK (
        char_length(full_name) >= 2
    )
);

-- Comments
COMMENT ON TABLE users IS 'All user accounts in the system';
COMMENT ON COLUMN users.user_id IS 'Unique identifier for user';
COMMENT ON COLUMN users.email IS 'Email address (unique, used for login)';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt hash of password (cost factor 12)';
COMMENT ON COLUMN users.role IS 'User role determining permissions';
COMMENT ON COLUMN users.preferences IS 'User preferences stored as JSON';
```

---

### 2.2 service_requests Table

```sql
-- ============================================================================
-- TABLE: service_requests
-- PURPOSE: Store all disaster response service requests
-- ============================================================================

CREATE TABLE service_requests (
    -- Primary Key
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    requestor_id UUID NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    provider_id UUID
        REFERENCES organizations(org_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    -- Service Details
    service_type VARCHAR(50) NOT NULL
        CHECK (service_type IN (
            'RESCUE',
            'MEDICAL',
            'FOOD',
            'SHELTER',
            'WATER',
            'OTHER'
        )),
    priority VARCHAR(20) NOT NULL
        CHECK (priority IN (
            'CRITICAL',
            'HIGH',
            'MEDIUM',
            'LOW'
        )),
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED'
        CHECK (status IN (
            'SUBMITTED',
            'APPROVED',
            'ACCEPTED',
            'IN_PROGRESS',
            'COMPLETED',
            'VERIFIED',
            'REJECTED',
            'CANCELLED',
            'EXPIRED'
        )),
    
    -- Location (PostGIS)
    location GEOMETRY(Point, 4326) NOT NULL,
    address TEXT,
    
    -- Description
    description TEXT NOT NULL
        CHECK (
            char_length(description) >= 10 AND 
            char_length(description) <= 500
        ),
    num_people_affected INTEGER NOT NULL DEFAULT 1
        CHECK (
            num_people_affected >= 1 AND 
            num_people_affected <= 1000
        ),
    
    -- Privacy
    privacy_level VARCHAR(20) NOT NULL DEFAULT 'PUBLIC'
        CHECK (privacy_level IN ('PUBLIC', 'PRIVATE')),
    
    -- Contact Override
    contact_phone VARCHAR(20)
        CHECK (
            contact_phone IS NULL OR 
            contact_phone ~* '^\+[1-9][0-9]{1,14}$'
        ),
    
    -- Timeline
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Rating & Feedback (after verification)
    rating INTEGER
        CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
    feedback TEXT,
    
    -- Notes
    acceptance_notes TEXT,
    completion_notes TEXT,
    rejection_reason TEXT,
    
    -- Constraints
    CONSTRAINT valid_timeline_acceptance CHECK (
        accepted_at IS NULL OR accepted_at >= created_at
    ),
    CONSTRAINT valid_timeline_completion CHECK (
        completed_at IS NULL OR 
        (completed_at >= accepted_at AND accepted_at IS NOT NULL)
    ),
    CONSTRAINT valid_timeline_verification CHECK (
        verified_at IS NULL OR 
        (verified_at >= completed_at AND completed_at IS NOT NULL)
    ),
    CONSTRAINT rating_requires_verification CHECK (
        rating IS NULL OR 
        (verified_at IS NOT NULL AND status = 'VERIFIED')
    ),
    CONSTRAINT provider_required_for_acceptance CHECK (
        status NOT IN ('ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED') OR 
        provider_id IS NOT NULL
    )
);

-- Comments
COMMENT ON TABLE service_requests IS 'All disaster response service requests';
COMMENT ON COLUMN service_requests.location IS 'Geographic location (PostGIS Point in WGS84)';
COMMENT ON COLUMN service_requests.priority IS 'Urgency level of request';
COMMENT ON COLUMN service_requests.status IS 'Current status in workflow';
```

---

### 2.3 organizations Table

```sql
-- ============================================================================
-- TABLE: organizations
-- PURPOSE: Store NGOs, hospitals, government agencies providing services
-- ============================================================================

CREATE TABLE organizations (
    -- Primary Key
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(50) NOT NULL
        CHECK (org_type IN (
            'NGO',
            'HOSPITAL',
            'GOVT_AGENCY',
            'VOLUNTEER_GROUP'
        )),
    registration_number VARCHAR(100) UNIQUE,
    
    -- Services
    service_types VARCHAR(50)[] NOT NULL
        CHECK (
            array_length(service_types, 1) > 0 AND
            service_types <@ ARRAY[
                'RESCUE', 'MEDICAL', 'FOOD', 'SHELTER', 'WATER', 'OTHER'
            ]::VARCHAR[]
        ),
    
    -- Capacity
    capacity INTEGER NOT NULL DEFAULT 10
        CHECK (capacity >= 1 AND capacity <= 1000),
    available_capacity INTEGER NOT NULL DEFAULT 10
        CHECK (
            available_capacity >= 0 AND 
            available_capacity <= capacity
        ),
    
    -- Coverage Area (JSONB for flexibility)
    -- Example: {"type": "circle", "center": [78.4867, 17.3850], "radius_km": 25}
    coverage_area JSONB NOT NULL,
    
    -- Contact
    contact_person VARCHAR(255),
    contact_phone VARCHAR(20) NOT NULL
        CHECK (contact_phone ~* '^\+[1-9][0-9]{1,14}$'),
    contact_email VARCHAR(255)
        CHECK (
            contact_email IS NULL OR
            contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
        ),
    
    -- Verification
    is_verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_at TIMESTAMP,
    verified_by UUID
        REFERENCES users(user_id)
        ON DELETE SET NULL,
    
    -- Documents (store file paths or base64)
    documents JSONB DEFAULT '{}'::jsonb,
    
    -- Statistics (denormalized for performance)
    total_services_completed INTEGER NOT NULL DEFAULT 0,
    average_rating NUMERIC(3,2) DEFAULT 0.00
        CHECK (
            average_rating >= 0.00 AND 
            average_rating <= 5.00
        ),
    average_response_time_minutes INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT positive_statistics CHECK (
        total_services_completed >= 0 AND
        average_response_time_minutes >= 0
    )
);

-- Comments
COMMENT ON TABLE organizations IS 'Service provider organizations';
COMMENT ON COLUMN organizations.service_types IS 'Array of service types this org provides';
COMMENT ON COLUMN organizations.coverage_area IS 'Geographic coverage area (JSONB)';
COMMENT ON COLUMN organizations.available_capacity IS 'Current available capacity for new requests';
```

---

### 2.4 notifications Table

```sql
-- ============================================================================
-- TABLE: notifications
-- PURPOSE: Store all notifications sent to users
-- ============================================================================

CREATE TABLE notifications (
    -- Primary Key
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Recipient
    user_id UUID NOT NULL
        REFERENCES users(user_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    
    -- Type & Channel
    type VARCHAR(50) NOT NULL
        CHECK (type IN (
            'SERVICE_CREATED',
            'SERVICE_ACCEPTED',
            'SERVICE_COMPLETED',
            'VERIFICATION_REQUEST',
            'GENERAL',
            'SYSTEM'
        )),
    channel VARCHAR(20) NOT NULL
        CHECK (channel IN (
            'EMAIL',
            'SMS',
            'PUSH',
            'IN_APP'
        )),
    
    -- Content
    subject VARCHAR(255),
    body TEXT NOT NULL,
    
    -- Metadata
    related_service_id UUID
        REFERENCES service_requests(service_id)
        ON DELETE CASCADE,
    related_org_id UUID
        REFERENCES organizations(org_id)
        ON DELETE SET NULL,
    
    -- Status
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING'
        CHECK (status IN (
            'PENDING',
            'SENT',
            'FAILED',
            'READ'
        )),
    sent_at TIMESTAMP,
    read_at TIMESTAMP,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT sent_before_read CHECK (
        read_at IS NULL OR 
        (sent_at IS NOT NULL AND read_at >= sent_at)
    ),
    CONSTRAINT subject_required_for_email CHECK (
        channel != 'EMAIL' OR subject IS NOT NULL
    )
);

-- Comments
COMMENT ON TABLE notifications IS 'All notifications sent to users';
COMMENT ON COLUMN notifications.channel IS 'Delivery channel (EMAIL, SMS, etc.)';
COMMENT ON COLUMN notifications.status IS 'Delivery status';
```

---

### 2.5 audit_logs Table

```sql
-- ============================================================================
-- TABLE: audit_logs
-- PURPOSE: Store audit trail of all important actions
-- ============================================================================

CREATE TABLE audit_logs (
    -- Primary Key (BIGSERIAL for high volume)
    log_id BIGSERIAL PRIMARY KEY,
    
    -- Actor
    user_id UUID
        REFERENCES users(user_id)
        ON DELETE SET NULL,
    user_email VARCHAR(255),  -- Denormalized for deleted users
    user_role VARCHAR(50),
    
    -- Action
    action VARCHAR(100) NOT NULL,
    
    -- Resource
    resource_type VARCHAR(50) NOT NULL,
    resource_id UUID,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id UUID,  -- For request tracing
    
    -- Changes (JSONB for flexibility)
    changes JSONB,  -- Example: {"before": {...}, "after": {...}}
    
    -- Metadata
    success BOOLEAN NOT NULL DEFAULT TRUE,
    error_message TEXT,
    
    -- Timestamp
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT valid_resource CHECK (
        resource_type IN (
            'User',
            'ServiceRequest',
            'Organization',
            'Notification',
            'System'
        )
    )
);

-- Comments
COMMENT ON TABLE audit_logs IS 'Audit trail of all system actions';
COMMENT ON COLUMN audit_logs.changes IS 'JSONB object with before/after state';
COMMENT ON COLUMN audit_logs.request_id IS 'UUID for tracing requests across services';

-- Partitioning by month (for better performance)
-- CREATE TABLE audit_logs_2026_05 PARTITION OF audit_logs
--     FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
```

---

## 3. **Reference Tables**

### 3.1 disaster_types Table

```sql
-- ============================================================================
-- TABLE: disaster_types (Reference/Lookup)
-- PURPOSE: Store predefined disaster types
-- ============================================================================

CREATE TABLE disaster_types (
    disaster_type_id SERIAL PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    severity_level INTEGER CHECK (severity_level BETWEEN 1 AND 5),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed data
INSERT INTO disaster_types (code, name, description, severity_level) VALUES
    ('FLOOD', 'Flood', 'Water overflow causing property damage and displacement', 4),
    ('CYCLONE', 'Cyclone', 'Severe storm with high winds and heavy rainfall', 5),
    ('EARTHQUAKE', 'Earthquake', 'Ground shaking and surface rupture', 5),
    ('DROUGHT', 'Drought', 'Prolonged period of abnormally low rainfall', 3),
    ('FIRE', 'Fire', 'Uncontrolled fire in buildings or forests', 4),
    ('LANDSLIDE', 'Landslide', 'Downward movement of rock, soil, debris', 4),
    ('TSUNAMI', 'Tsunami', 'Series of waves caused by displacement of water', 5),
    ('EPIDEMIC', 'Epidemic', 'Widespread disease outbreak', 4),
    ('OTHER', 'Other', 'Other types of disasters', 1);
```

---

## 4. **Indexes**

### 4.1 Users Indexes

```sql
-- Primary lookup indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone) WHERE phone IS NOT NULL;
CREATE INDEX idx_users_role ON users(role);

-- Active users (partial index)
CREATE INDEX idx_users_active ON users(is_active) 
    WHERE is_active = TRUE;

-- Created date for analytics
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- Full-text search on name
CREATE INDEX idx_users_full_name_fts ON users 
    USING GIN(to_tsvector('english', full_name));
```

---

### 4.2 Service Requests Indexes

```sql
-- Foreign keys
CREATE INDEX idx_service_requests_requestor_id ON service_requests(requestor_id);
CREATE INDEX idx_service_requests_provider_id ON service_requests(provider_id);

-- Status workflow
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_priority ON service_requests(priority);
CREATE INDEX idx_service_requests_service_type ON service_requests(service_type);

-- Spatial index (GIST for PostGIS)
CREATE INDEX idx_service_requests_location ON service_requests 
    USING GIST(location);

-- Composite indexes for common queries
CREATE INDEX idx_service_requests_status_priority ON service_requests(status, priority);
CREATE INDEX idx_service_requests_status_created ON service_requests(status, created_at DESC);
CREATE INDEX idx_service_requests_type_status ON service_requests(service_type, status);

-- Timeline indexes
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at DESC);
CREATE INDEX idx_service_requests_accepted_at ON service_requests(accepted_at DESC) 
    WHERE accepted_at IS NOT NULL;
CREATE INDEX idx_service_requests_completed_at ON service_requests(completed_at DESC) 
    WHERE completed_at IS NOT NULL;

-- Full-text search on description
CREATE INDEX idx_service_requests_description_fts ON service_requests 
    USING GIN(to_tsvector('english', description));

-- Partial indexes for active requests
CREATE INDEX idx_service_requests_active ON service_requests(created_at DESC)
    WHERE status IN ('SUBMITTED', 'APPROVED', 'ACCEPTED', 'IN_PROGRESS');

CREATE INDEX idx_service_requests_critical ON service_requests(created_at DESC)
    WHERE priority = 'CRITICAL' AND status IN ('SUBMITTED', 'APPROVED');
```

---

### 4.3 Organizations Indexes

```sql
-- Basic lookups
CREATE INDEX idx_organizations_org_type ON organizations(org_type);
CREATE INDEX idx_organizations_registration_number ON organizations(registration_number);

-- Verified organizations
CREATE INDEX idx_organizations_verified ON organizations(is_verified, org_type)
    WHERE is_verified = TRUE;

-- Service types (GIN for array)
CREATE INDEX idx_organizations_service_types ON organizations 
    USING GIN(service_types);

-- Timestamps
CREATE INDEX idx_organizations_created_at ON organizations(created_at DESC);

-- Available capacity
CREATE INDEX idx_organizations_available_capacity ON organizations(available_capacity)
    WHERE available_capacity > 0 AND is_verified = TRUE;

-- Coverage area (JSONB)
CREATE INDEX idx_organizations_coverage_area ON organizations 
    USING GIN(coverage_area);
```

---

### 4.4 Notifications Indexes

```sql
-- User notifications
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);

-- Unread notifications
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, created_at DESC)
    WHERE status IN ('SENT', 'PENDING');

-- Status & channel
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_channel ON notifications(channel);

-- Related entities
CREATE INDEX idx_notifications_service ON notifications(related_service_id)
    WHERE related_service_id IS NOT NULL;

-- Created date
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- Failed notifications for retry
CREATE INDEX idx_notifications_failed ON notifications(created_at)
    WHERE status = 'FAILED' AND retry_count < 3;
```

---

### 4.5 Audit Logs Indexes

```sql
-- User actions
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);

-- Action type
CREATE INDEX idx_audit_logs_action ON audit_logs(action);

-- Resource
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);

-- Timestamp (most important for audit logs)
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Composite for common queries
CREATE INDEX idx_audit_logs_user_timestamp ON audit_logs(user_id, timestamp DESC);
CREATE INDEX idx_audit_logs_action_timestamp ON audit_logs(action, timestamp DESC);

-- Failed actions
CREATE INDEX idx_audit_logs_failed ON audit_logs(timestamp DESC)
    WHERE success = FALSE;
```

---

## 5. **Views**

### 5.1 Active Service Requests View

```sql
CREATE VIEW v_active_service_requests AS
SELECT 
    sr.service_id,
    sr.service_type,
    sr.priority,
    sr.status,
    sr.location,
    ST_X(sr.location::geometry) as longitude,
    ST_Y(sr.location::geometry) as latitude,
    sr.address,
    sr.description,
    sr.num_people_affected,
    sr.created_at,
    sr.accepted_at,
    u.user_id as requestor_id,
    u.full_name as requestor_name,
    u.phone as requestor_phone,
    u.email as requestor_email,
    o.org_id as provider_id,
    o.name as provider_name,
    o.contact_phone as provider_phone,
    EXTRACT(EPOCH FROM (COALESCE(sr.accepted_at, NOW()) - sr.created_at)) / 60 as wait_time_minutes
FROM service_requests sr
INNER JOIN users u ON sr.requestor_id = u.user_id
LEFT JOIN organizations o ON sr.provider_id = o.org_id
WHERE sr.status IN ('SUBMITTED', 'APPROVED', 'ACCEPTED', 'IN_PROGRESS');

COMMENT ON VIEW v_active_service_requests IS 'All currently active service requests with user details';
```

---

### 5.2 Organization Statistics View

```sql
CREATE VIEW v_organization_stats AS
SELECT 
    o.org_id,
    o.name,
    o.org_type,
    o.is_verified,
    o.capacity,
    o.available_capacity,
    COUNT(sr.service_id) as total_services,
    COUNT(sr.service_id) FILTER (WHERE sr.status = 'COMPLETED') as completed_services,
    COUNT(sr.service_id) FILTER (WHERE sr.status = 'VERIFIED') as verified_services,
    COALESCE(AVG(sr.rating) FILTER (WHERE sr.rating IS NOT NULL), 0) as average_rating,
    COALESCE(
        AVG(EXTRACT(EPOCH FROM (sr.accepted_at - sr.created_at)) / 60) 
        FILTER (WHERE sr.accepted_at IS NOT NULL),
        0
    ) as avg_acceptance_time_minutes,
    COALESCE(
        AVG(EXTRACT(EPOCH FROM (sr.completed_at - sr.accepted_at)) / 60) 
        FILTER (WHERE sr.completed_at IS NOT NULL),
        0
    ) as avg_completion_time_minutes,
    o.created_at
FROM organizations o
LEFT JOIN service_requests sr ON o.org_id = sr.provider_id
GROUP BY o.org_id, o.name, o.org_type, o.is_verified, o.capacity, o.available_capacity, o.created_at;

COMMENT ON VIEW v_organization_stats IS 'Organization statistics including service counts and performance metrics';
```

---

## 6. **Functions**

### 6.1 Update Updated_At Function

```sql
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION update_updated_at_column IS 'Automatically update updated_at timestamp';
```

---

### 6.2 Calculate Distance Function

```sql
CREATE OR REPLACE FUNCTION calculate_distance_km(
    lon1 NUMERIC,
    lat1 NUMERIC,
    lon2 NUMERIC,
    lat2 NUMERIC
)
RETURNS NUMERIC AS $$
BEGIN
    RETURN ST_Distance(
        ST_SetSRID(ST_Point(lon1, lat1), 4326)::geography,
        ST_SetSRID(ST_Point(lon2, lat2), 4326)::geography
    ) / 1000;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calculate_distance_km IS 'Calculate distance between two points in kilometers';
```

---

### 6.3 Get Nearby Providers Function

```sql
CREATE OR REPLACE FUNCTION get_nearby_providers(
    search_lon NUMERIC,
    search_lat NUMERIC,
    search_radius_km NUMERIC DEFAULT 50,
    search_service_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    org_id UUID,
    name VARCHAR,
    org_type VARCHAR,
    distance_km NUMERIC,
    available_capacity INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.org_id,
        o.name,
        o.org_type,
        ST_Distance(
            ST_SetSRID(ST_Point(search_lon, search_lat), 4326)::geography,
            ST_SetSRID(
                ST_Point(
                    (o.coverage_area->'center'->>0)::NUMERIC,
                    (o.coverage_area->'center'->>1)::NUMERIC
                ),
                4326
            )::geography
        ) / 1000 as distance_km,
        o.available_capacity
    FROM organizations o
    WHERE o.is_verified = TRUE
        AND o.available_capacity > 0
        AND (search_service_type IS NULL OR search_service_type = ANY(o.service_types))
        AND ST_DWithin(
            ST_SetSRID(ST_Point(search_lon, search_lat), 4326)::geography,
            ST_SetSRID(
                ST_Point(
                    (o.coverage_area->'center'->>0)::NUMERIC,
                    (o.coverage_area->'center'->>1)::NUMERIC
                ),
                4326
            )::geography,
            search_radius_km * 1000
        )
    ORDER BY distance_km ASC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_nearby_providers IS 'Find verified providers within radius of a location';
```

---

## 7. **Triggers**

### 7.1 Updated_At Triggers

```sql
-- Users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Service Requests
CREATE TRIGGER update_service_requests_updated_at
    BEFORE UPDATE ON service_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Organizations
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 7.2 Organization Stats Auto-Update Trigger

```sql
CREATE OR REPLACE FUNCTION update_organization_stats()
RETURNS TRIGGER AS $$
BEGIN
    -- When service completed, free up capacity
    IF NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED' THEN
        UPDATE organizations
        SET 
            total_services_completed = total_services_completed + 1,
            available_capacity = LEAST(capacity, available_capacity + 1)
        WHERE org_id = NEW.provider_id;
    END IF;
    
    -- When service verified with rating, update average
    IF NEW.status = 'VERIFIED' AND OLD.status = 'COMPLETED' AND NEW.rating IS NOT NULL THEN
        UPDATE organizations
        SET average_rating = (
            SELECT COALESCE(AVG(rating), 0)
            FROM service_requests
            WHERE provider_id = NEW.provider_id AND rating IS NOT NULL
        )
        WHERE org_id = NEW.provider_id;
    END IF;
    
    -- When service accepted, decrease capacity
    IF NEW.status = 'ACCEPTED' AND OLD.status IN ('SUBMITTED', 'APPROVED') THEN
        UPDATE organizations
        SET available_capacity = GREATEST(0, available_capacity - 1)
        WHERE org_id = NEW.provider_id;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_organization_stats
    AFTER UPDATE ON service_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_organization_stats();
```

---

### 7.3 Audit Log Trigger

```sql
CREATE OR REPLACE FUNCTION audit_service_request_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (user_id, user_email, action, resource_type, resource_id, changes)
        VALUES (
            NEW.requestor_id,
            (SELECT email FROM users WHERE user_id = NEW.requestor_id),
            'SERVICE_CREATED',
            'ServiceRequest',
            NEW.service_id,
            jsonb_build_object('after', row_to_json(NEW))
        );
    ELSIF TG_OP = 'UPDATE' THEN
        IF OLD.status != NEW.status THEN
            INSERT INTO audit_logs (
                user_id, 
                user_email, 
                action, 
                resource_type, 
                resource_id, 
                changes
            )
            VALUES (
                COALESCE(NEW.provider_id, NEW.requestor_id),
                (SELECT email FROM users WHERE user_id = COALESCE(NEW.provider_id, NEW.requestor_id)),
                CASE 
                    WHEN NEW.status = 'ACCEPTED' THEN 'SERVICE_ACCEPTED'
                    WHEN NEW.status = 'COMPLETED' THEN 'SERVICE_COMPLETED'
                    WHEN NEW.status = 'VERIFIED' THEN 'SERVICE_VERIFIED'
                    WHEN NEW.status = 'REJECTED' THEN 'SERVICE_REJECTED'
                    WHEN NEW.status = 'CANCELLED' THEN 'SERVICE_CANCELLED'
                    ELSE 'SERVICE_UPDATED'
                END,
                'ServiceRequest',
                NEW.service_id,
                jsonb_build_object(
                    'before', row_to_json(OLD),
                    'after', row_to_json(NEW),
                    'changed_fields', jsonb_build_object('status', NEW.status)
                )
            );
        END IF;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_audit_service_requests
    AFTER INSERT OR UPDATE ON service_requests
    FOR EACH ROW
    EXECUTE FUNCTION audit_service_request_changes();
```

---

## 8. **Constraints**

### 8.1 Foreign Key Constraints Summary

```sql
-- service_requests
ALTER TABLE service_requests
    ADD CONSTRAINT fk_service_requests_requestor
        FOREIGN KEY (requestor_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_service_requests_provider
        FOREIGN KEY (provider_id) REFERENCES organizations(org_id)
        ON DELETE SET NULL ON UPDATE CASCADE;

-- organizations
ALTER TABLE organizations
    ADD CONSTRAINT fk_organizations_verified_by
        FOREIGN KEY (verified_by) REFERENCES users(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE;

-- notifications
ALTER TABLE notifications
    ADD CONSTRAINT fk_notifications_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    ADD CONSTRAINT fk_notifications_service
        FOREIGN KEY (related_service_id) REFERENCES service_requests(service_id)
        ON DELETE CASCADE,
    ADD CONSTRAINT fk_notifications_org
        FOREIGN KEY (related_org_id) REFERENCES organizations(org_id)
        ON DELETE SET NULL;

-- audit_logs
ALTER TABLE audit_logs
    ADD CONSTRAINT fk_audit_logs_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL ON UPDATE CASCADE;
```

---

## 9. **Migrations**

### 9.1 Migration Script Example

```sql
-- migrations/001_initial_schema.sql
-- Run: psql -U postgres -d idrm -f migrations/001_initial_schema.sql

BEGIN;

-- 1. Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- 2. Create tables (in dependency order)
\i schema/01_users.sql
\i schema/02_organizations.sql
\i schema/03_service_requests.sql
\i schema/04_notifications.sql
\i schema/05_audit_logs.sql

-- 3. Create indexes
\i schema/06_indexes.sql

-- 4. Create views
\i schema/07_views.sql

-- 5. Create functions
\i schema/08_functions.sql

-- 6. Create triggers
\i schema/09_triggers.sql

COMMIT;
```

---

**END OF DATABASE SCHEMAS v3.0**

**Total Tables**: 5 core + 1 reference  
**Total Indexes**: 40+  
**Total Views**: 2  
**Total Functions**: 3  
**Total Triggers**: 6  
**Status**: ✅ Production-ready
