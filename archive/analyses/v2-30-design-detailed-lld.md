> *Type: Document (specification) · Audience: Developers · Status: Archived — v2 historical generation*

# IDRM MVP - Low-Level Design (LLD)
## Integrated Disaster Response Management Platform

**Document Type**: Low-Level Design  
**Version**: 2.0  
**Date**: May 10, 2026  
**Status**: Final  
**Classification**: Internal Use

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2, 2024 | Technical Team | Initial detailed design |
| 2.0 | May 10, 2026 | Technical Team | Updated for v2.0 stack (Bun, Python geospatial, Miniconda) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Detailed API Specifications](#2-detailed-api-specifications)
3. [Database Schema (Detailed)](#3-database-schema-detailed)
4. [Component Class Diagrams](#4-component-class-diagrams)
5. [Sequence Diagrams](#5-sequence-diagrams)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [State Machines](#7-state-machines)
8. [Data Structures](#8-data-structures)
9. [Error Handling](#9-error-handling)
10. [Performance Optimization](#10-performance-optimization)

---

## 1. Executive Summary

### 1.1 Purpose

This Low-Level Design (LLD) document provides **DETAILED TECHNICAL SPECIFICATIONS** for implementing the IDRM platform. It includes:
- Complete API endpoint specifications
- Database schema with all constraints
- Class diagrams for each service
- Sequence diagrams for workflows
- Algorithms with pseudocode
- Error handling patterns
- Performance optimization techniques

### 1.2 Audience

This document is for:
- **Developers**: Implement services following these specs
- **Code Reviewers**: Verify implementation matches design
- **QA Engineers**: Understand expected behavior for testing
- **Technical Leads**: Review implementation approach

---

## 2. Detailed API Specifications

### 2.1 Authentication Service API

**Base URL**: `/auth`

#### 2.1.1 POST /auth/register

**Description**: Register a new user account

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "9876543210",
  "role": "CITIZEN"
}
```

**Request Schema**:
```typescript
interface RegisterRequest {
  email: string;           // Valid email format, max 255 chars
  password: string;        // Min 8 chars, 1 upper, 1 lower, 1 number
  full_name: string;       // Max 255 chars
  phone: string;           // 10 digits, Indian mobile
  role?: UserRole;         // Optional, defaults to CITIZEN
}

enum UserRole {
  CITIZEN = "CITIZEN",
  SERVICE_PROVIDER = "SERVICE_PROVIDER",
  // Other roles assigned by admin only
}
```

**Response (201 Created)**:
```json
{
  "status": "success",
  "message": "Verification email sent to user@example.com",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false,
    "created_at": "2026-05-10T10:30:00Z"
  }
}
```

**Error Responses**:
```json
// 400 Bad Request - Validation error
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Email already registered"
    },
    {
      "field": "password",
      "message": "Password must be at least 8 characters"
    }
  ]
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Too many registration attempts. Please try again in 1 hour.",
  "retry_after": 3600
}
```

**Validation Rules**:
```python
def validate_registration(data: RegisterRequest):
    errors = []
    
    # Email validation
    if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', data.email):
        errors.append({"field": "email", "message": "Invalid email format"})
    
    if User.query.filter_by(email=data.email).first():
        errors.append({"field": "email", "message": "Email already registered"})
    
    # Password strength
    if len(data.password) < 8:
        errors.append({"field": "password", "message": "Minimum 8 characters"})
    
    if not re.search(r'[A-Z]', data.password):
        errors.append({"field": "password", "message": "Must contain uppercase"})
    
    if not re.search(r'[a-z]', data.password):
        errors.append({"field": "password", "message": "Must contain lowercase"})
    
    if not re.search(r'\d', data.password):
        errors.append({"field": "password", "message": "Must contain number"})
    
    # Phone validation
    if not re.match(r'^\d{10}$', data.phone):
        errors.append({"field": "phone", "message": "Must be 10 digits"})
    
    return errors
```

---

#### 2.1.2 POST /auth/login

**Description**: Authenticate user and receive tokens

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN",
      "organization_id": null
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**JWT Payload Structure**:
```json
{
  "sub": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "user@example.com",
  "role": "CITIZEN",
  "org_id": null,
  "exp": 1715345400,
  "iat": 1715344500,
  "type": "access"
}
```

**Error Responses**:
```json
// 401 Unauthorized - Invalid credentials
{
  "status": "error",
  "message": "Invalid email or password"
}

// 403 Forbidden - Account not verified
{
  "status": "error",
  "message": "Please verify your email before logging in",
  "verification_required": true
}

// 429 Too Many Requests - Rate limit
{
  "status": "error",
  "message": "Too many failed login attempts. Account locked for 30 minutes.",
  "retry_after": 1800,
  "locked_until": "2026-05-10T11:00:00Z"
}
```

**Rate Limiting Logic**:
```python
def check_login_rate_limit(email: str) -> bool:
    """
    Allow max 5 failed attempts in 15 minutes
    Lock account for 30 minutes after 5 failures
    """
    key = f"login_attempts:{email}"
    lock_key = f"login_locked:{email}"
    
    # Check if locked
    if redis.exists(lock_key):
        return False  # Account locked
    
    # Get attempt count
    attempts = redis.get(key) or 0
    
    if attempts >= 5:
        # Lock account for 30 minutes
        redis.setex(lock_key, 1800, "1")
        redis.delete(key)
        return False
    
    return True

def record_failed_login(email: str):
    key = f"login_attempts:{email}"
    redis.incr(key)
    redis.expire(key, 900)  # 15 minutes
```

---

### 2.2 Service Request API

**Base URL**: `/services`

#### 2.2.1 POST /services

**Description**: Create a new service request

**Request**:
```json
{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad, Telangana 500002",
  "description": "Urgent medical attention needed for elderly person with chest pain",
  "privacy_level": "PROTECTED",
  "disaster_event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"]
  }
}
```

**Request Schema**:
```typescript
interface CreateServiceRequest {
  service_type: ServiceType;       // MEDICAL, FOOD, SHELTER, etc.
  priority: PriorityLevel;         // CRITICAL, HIGH, MEDIUM, LOW
  location: GeoJSONPoint;          // Valid point geometry
  address: string;                 // Max 500 chars
  description: string;             // Max 1000 chars
  privacy_level?: PrivacyLevel;    // PUBLIC, PROTECTED, PRIVATE (default: PROTECTED)
  disaster_event_id?: string;      // UUID, optional
  metadata?: Record<string, any>;  // Optional JSON metadata
  photo?: string;                  // Base64 encoded image, max 5MB
}
```

**Response (201 Created)**:
```json
{
  "status": "success",
  "message": "Service request created successfully",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "SUBMITTED",
    "created_at": "2026-05-10T10:45:00Z",
    "estimated_response_time": "30 minutes",
    "next_action": "Request is being reviewed by authorities"
  }
}
```

**Business Logic**:
```python
async def create_service_request(
    request: CreateServiceRequest,
    user: User
) -> ServiceRequest:
    """
    Create service request with business rules
    """
    # Auto-approve CRITICAL requests
    if request.priority == PriorityLevel.CRITICAL:
        status = ServiceStatus.APPROVED
        # Auto-assign to nearest provider
        provider = await find_nearest_provider(request)
        if provider:
            assigned_to = provider.user_id
            await send_critical_alert(provider, request)
    else:
        status = ServiceStatus.SUBMITTED
        assigned_to = None
    
    # Create service request
    service = ServiceRequest(
        requestor_id=user.user_id,
        service_type=request.service_type,
        priority=request.priority,
        location=request.location,
        address=request.address,
        description=request.description,
        privacy_level=request.privacy_level or PrivacyLevel.PROTECTED,
        status=status,
        assigned_to=assigned_to,
        disaster_event_id=request.disaster_event_id,
        metadata=request.metadata
    )
    
    db.add(service)
    await db.commit()
    
    # Send notifications
    await notify_authorities(service)
    if status == ServiceStatus.APPROVED:
        await notify_provider(assigned_to, service)
    
    return service
```

---

#### 2.2.2 GET /services

**Description**: List service requests with filtering

**Query Parameters**:
```
?lat=17.3850
&lng=78.4867
&radius=5000              # meters
&service_type=MEDICAL
&status=APPROVED
&priority=HIGH
&disaster_event_id=<uuid>
&page=1
&per_page=20
&sort_by=created_at
&sort_order=desc
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "services": [
      {
        "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "status": "APPROVED",
        "location": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "address": "Charminar, Hyderabad",
        "description": "Urgent medical attention needed...",
        "distance_meters": 1250.5,
        "created_at": "2026-05-10T10:45:00Z",
        "assigned_to": {
          "user_id": "...",
          "full_name": "Dr. Smith",
          "organization": "City Hospital"
        }
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 145,
      "pages": 8,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

**Spatial Query Implementation**:
```python
def get_services_nearby(
    lat: float,
    lng: float,
    radius: int,
    filters: dict,
    page: int = 1,
    per_page: int = 20
) -> tuple[List[ServiceRequest], int]:
    """
    Query services within radius using PostGIS
    """
    query = db.query(
        ServiceRequest,
        ST_Distance(
            ServiceRequest.location.cast(Geography),
            ST_MakePoint(lng, lat).cast(Geography)
        ).label('distance')
    ).filter(
        ST_DWithin(
            ServiceRequest.location.cast(Geography),
            ST_MakePoint(lng, lat).cast(Geography),
            radius
        )
    )
    
    # Apply filters
    if filters.get('service_type'):
        query = query.filter(
            ServiceRequest.service_type == filters['service_type']
        )
    
    if filters.get('status'):
        query = query.filter(
            ServiceRequest.status == filters['status']
        )
    
    if filters.get('priority'):
        query = query.filter(
            ServiceRequest.priority == filters['priority']
        )
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * per_page
    services = query.order_by('distance').offset(offset).limit(per_page).all()
    
    return services, total
```

---

### 2.3 Provider Matching API

#### 2.3.1 POST /services/{service_id}/match-providers

**Description**: Find matching providers for a service request

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "matches": [
      {
        "provider_id": "p1",
        "user_id": "u1",
        "organization": {
          "org_id": "o1",
          "name": "City Hospital",
          "type": "GOVERNMENT"
        },
        "distance_meters": 850.2,
        "rating": 4.8,
        "completed_services": 245,
        "current_load": 2,
        "capacity": 5,
        "availability": true,
        "match_score": 0.95
      }
    ],
    "match_criteria": {
      "max_distance": 10000,
      "min_rating": 3.0,
      "service_type": "MEDICAL"
    }
  }
}
```

**Matching Algorithm**:
```python
def match_providers(
    service: ServiceRequest
) -> List[tuple[Provider, float]]:
    """
    Match providers using multi-factor scoring
    
    Score components:
    - Distance (40%): Closer is better
    - Rating (30%): Higher is better
    - Load (20%): Lower is better
    - Response time (10%): Faster is better
    """
    # Get distance threshold by priority
    max_distance = {
        PriorityLevel.CRITICAL: 10000,   # 10km
        PriorityLevel.HIGH: 25000,       # 25km
        PriorityLevel.MEDIUM: 50000,     # 50km
        PriorityLevel.LOW: 50000         # 50km
    }[service.priority]
    
    # Query providers
    providers = db.query(
        Provider,
        ST_Distance(
            Provider.location.cast(Geography),
            service.location.cast(Geography)
        ).label('distance')
    ).filter(
        ST_DWithin(
            Provider.location.cast(Geography),
            service.location.cast(Geography),
            max_distance
        ),
        Provider.service_types.contains([service.service_type]),
        Provider.is_available == True,
        Provider.current_load < Provider.capacity
    ).all()
    
    # Calculate match scores
    matches = []
    for provider, distance in providers:
        score = calculate_match_score(
            provider, distance, max_distance
        )
        matches.append((provider, score))
    
    # Sort by score (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return matches[:20]  # Top 20 matches

def calculate_match_score(
    provider: Provider,
    distance: float,
    max_distance: float
) -> float:
    """
    Calculate match score (0-1)
    """
    # Distance score (40%)
    distance_score = 1 - (distance / max_distance)
    distance_score = max(0, distance_score) * 0.4
    
    # Rating score (30%)
    rating_score = (provider.rating / 5.0) * 0.3
    
    # Load score (20%) - lower is better
    load_ratio = provider.current_load / provider.capacity
    load_score = (1 - load_ratio) * 0.2
    
    # Response time score (10%)
    avg_response_minutes = provider.avg_response_time_minutes or 60
    response_score = max(0, 1 - (avg_response_minutes / 120)) * 0.1
    
    total_score = (
        distance_score +
        rating_score +
        load_score +
        response_score
    )
    
    return total_score
```

---

## 3. Database Schema (Detailed)

### 3.1 Users Table

**Table Name**: `users`

**Schema**:
```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    role VARCHAR(50) NOT NULL CHECK (role IN (
        'SYSTEM_ADMIN',
        'DM_AUTHORITY',
        'ORG_ADMIN',
        'EVENT_MANAGER',
        'SERVICE_PROVIDER',
        'VOLUNTEER',
        'CITIZEN',
        'AUDITOR'
    )),
    organization_id UUID REFERENCES organizations(organization_id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    email_verification_token VARCHAR(255),
    email_verification_expires TIMESTAMP,
    password_reset_token VARCHAR(255),
    password_reset_expires TIMESTAMP,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'),
    CONSTRAINT phone_format CHECK (phone ~ '^\d{10}$')
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_organization ON users(organization_id);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = TRUE;

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Sample Data**:
```sql
INSERT INTO users (email, password_hash, full_name, phone, role, is_verified) VALUES
('admin@idrm.gov.in', '$2b$12$...', 'System Administrator', '9999999999', 'SYSTEM_ADMIN', TRUE),
('collector@telangana.gov.in', '$2b$12$...', 'District Collector', '9999999998', 'DM_AUTHORITY', TRUE),
('john@example.com', '$2b$12$...', 'John Doe', '9876543210', 'CITIZEN', TRUE);
```

---

### 3.2 Service Requests Table

**Table Name**: `service_requests`

**Schema**:
```sql
CREATE TYPE service_type AS ENUM (
    'MEDICAL', 'FOOD', 'SHELTER', 'RESCUE',
    'SANITATION', 'COMMUNICATION', 'TRANSPORT',
    'PSYCHOSOCIAL', 'LEGAL', 'OTHER'
);

CREATE TYPE priority_level AS ENUM (
    'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
);

CREATE TYPE service_status AS ENUM (
    'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED',
    'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED',
    'CANCELLED', 'DISPUTED'
);

CREATE TYPE privacy_level AS ENUM (
    'PUBLIC', 'PROTECTED', 'PRIVATE'
);

CREATE TABLE service_requests (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requestor_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    service_type service_type NOT NULL,
    priority priority_level NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    address TEXT NOT NULL,
    description TEXT NOT NULL CHECK (length(description) <= 1000),
    privacy_level privacy_level DEFAULT 'PROTECTED' NOT NULL,
    status service_status DEFAULT 'SUBMITTED' NOT NULL,
    assigned_to UUID REFERENCES users(user_id) ON DELETE SET NULL,
    disaster_event_id UUID REFERENCES disaster_events(event_id) ON DELETE SET NULL,
    estimated_completion TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    rating DECIMAL(2,1) CHECK (rating >= 1.0 AND rating <= 5.0),
    rejection_reason TEXT,
    cancellation_reason TEXT,
    proof_photo_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    metadata JSONB,
    
    -- Constraints
    CONSTRAINT valid_location CHECK (
        ST_X(location) BETWEEN 68.0 AND 97.5 AND
        ST_Y(location) BETWEEN 6.0 AND 35.5
    ),  -- India bounds
    CONSTRAINT rejection_requires_reason CHECK (
        status != 'REJECTED' OR rejection_reason IS NOT NULL
    ),
    CONSTRAINT cancellation_requires_reason CHECK (
        status != 'CANCELLED' OR cancellation_reason IS NOT NULL
    ),
    CONSTRAINT completed_requires_photo CHECK (
        status NOT IN ('COMPLETED', 'VERIFIED') OR
        priority NOT IN ('HIGH', 'CRITICAL') OR
        proof_photo_url IS NOT NULL
    )
);

-- Indexes
CREATE INDEX idx_service_requests_location 
    ON service_requests USING GIST(location);

CREATE INDEX idx_service_requests_status 
    ON service_requests(status);

CREATE INDEX idx_service_requests_priority 
    ON service_requests(priority);

CREATE INDEX idx_service_requests_type 
    ON service_requests(service_type);

CREATE INDEX idx_service_requests_event 
    ON service_requests(disaster_event_id);

CREATE INDEX idx_service_requests_requestor 
    ON service_requests(requestor_id);

CREATE INDEX idx_service_requests_assigned 
    ON service_requests(assigned_to);

CREATE INDEX idx_service_requests_status_priority 
    ON service_requests(status, priority);

CREATE INDEX idx_service_requests_metadata 
    ON service_requests USING GIN(metadata);

-- Spatial index for nearby queries
CREATE INDEX idx_service_requests_location_geog 
    ON service_requests USING GIST((location::geography));

-- Trigger for updated_at
CREATE TRIGGER update_service_requests_updated_at 
    BEFORE UPDATE ON service_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 3.3 Organizations Table

**Schema**:
```sql
CREATE TYPE organization_type AS ENUM (
    'NGO', 'GOVERNMENT', 'INTERNATIONAL_ORG', 'PRIVATE'
);

CREATE TABLE organizations (
    organization_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    type organization_type NOT NULL,
    registration_number VARCHAR(100) UNIQUE,
    address TEXT,
    location GEOMETRY(Point, 4326),
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20),
    description TEXT,
    is_verified BOOLEAN DEFAULT FALSE NOT NULL,
    verified_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT email_format CHECK (
        contact_email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    )
);

-- Indexes
CREATE INDEX idx_organizations_location 
    ON organizations USING GIST(location);

CREATE INDEX idx_organizations_type 
    ON organizations(type);

CREATE INDEX idx_organizations_verified 
    ON organizations(is_verified) WHERE is_verified = TRUE;

CREATE TRIGGER update_organizations_updated_at 
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 3.4 Service Providers Table

**Schema**:
```sql
CREATE TABLE service_providers (
    provider_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organizations(organization_id) ON DELETE CASCADE,
    service_types service_type[] NOT NULL,
    coverage_area GEOMETRY(Polygon, 4326),
    capacity INTEGER NOT NULL CHECK (capacity >= 1 AND capacity <= 100),
    current_load INTEGER DEFAULT 0 NOT NULL CHECK (current_load >= 0),
    is_available BOOLEAN DEFAULT TRUE NOT NULL,
    unavailable_reason TEXT,
    unavailable_until TIMESTAMP,
    rating DECIMAL(3,2) DEFAULT 0.0 CHECK (rating >= 0.0 AND rating <= 5.0),
    total_completed INTEGER DEFAULT 0 NOT NULL,
    total_ratings INTEGER DEFAULT 0 NOT NULL,
    avg_response_time_minutes INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT current_load_valid CHECK (current_load <= capacity),
    CONSTRAINT unavailable_has_reason CHECK (
        is_available = TRUE OR unavailable_reason IS NOT NULL
    )
);

-- Indexes
CREATE INDEX idx_service_providers_user 
    ON service_providers(user_id);

CREATE INDEX idx_service_providers_org 
    ON service_providers(organization_id);

CREATE INDEX idx_service_providers_coverage 
    ON service_providers USING GIST(coverage_area);

CREATE INDEX idx_service_providers_types 
    ON service_providers USING GIN(service_types);

CREATE INDEX idx_service_providers_available 
    ON service_providers(is_available) WHERE is_available = TRUE;

CREATE INDEX idx_service_providers_capacity 
    ON service_providers((capacity - current_load)) 
    WHERE is_available = TRUE;

CREATE TRIGGER update_service_providers_updated_at 
    BEFORE UPDATE ON service_providers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 3.5 Audit Logs Table

**Schema**:
```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id UUID,
    changes JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    
    CONSTRAINT valid_action CHECK (action IN (
        'CREATE', 'UPDATE', 'DELETE',
        'LOGIN', 'LOGOUT', 'PASSWORD_RESET',
        'APPROVE', 'REJECT', 'ASSIGN',
        'COMPLETE', 'VERIFY', 'CANCEL',
        'ALLOCATE_FUNDS', 'VIEW_PII'
    ))
);

-- Indexes
CREATE INDEX idx_audit_logs_user 
    ON audit_logs(user_id);

CREATE INDEX idx_audit_logs_entity 
    ON audit_logs(entity_type, entity_id);

CREATE INDEX idx_audit_logs_action 
    ON audit_logs(action);

CREATE INDEX idx_audit_logs_created 
    ON audit_logs(created_at DESC);

-- Partition by month (for large scale)
-- CREATE TABLE audit_logs_2026_05 PARTITION OF audit_logs
-- FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
```

**Audit Log Example**:
```json
{
  "log_id": 12345,
  "user_id": "a1b2c3d4...",
  "action": "UPDATE",
  "entity_type": "service_request",
  "entity_id": "f9e8d7c6...",
  "changes": {
    "status": {
      "old": "SUBMITTED",
      "new": "APPROVED"
    },
    "approved_by": "a1b2c3d4...",
    "approved_at": "2026-05-10T11:00:00Z"
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "created_at": "2026-05-10T11:00:00Z"
}
```

---

## 4. Component Class Diagrams

### 4.1 Auth Service Class Diagram

```
┌─────────────────────────┐
│      AuthService        │
├─────────────────────────┤
│ - db: Database          │
│ - redis: Redis          │
│ - jwt_secret: str       │
├─────────────────────────┤
│ + register(data)        │
│ + login(email, pass)    │
│ + logout(token)         │
│ + refresh_token(token)  │
│ + verify_email(token)   │
│ + forgot_password(email)│
│ + reset_password(token) │
│ - hash_password(pass)   │
│ - verify_password(...)  │
│ - generate_jwt(user)    │
│ - validate_jwt(token)   │
└─────────────────────────┘
          │
          │ uses
          ▼
┌─────────────────────────┐
│         User            │
├─────────────────────────┤
│ + user_id: UUID         │
│ + email: str            │
│ + password_hash: str    │
│ + full_name: str        │
│ + phone: str            │
│ + role: UserRole        │
│ + organization_id: UUID │
│ + is_active: bool       │
│ + is_verified: bool     │
├─────────────────────────┤
│ + to_dict()             │
│ + to_public_dict()      │
│ + check_password(pass)  │
└─────────────────────────┘
```

**Python Implementation**:
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from passlib.context import CryptContext
import uuid

Base = declarative_base()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True)
    role = Column(String(50), nullable=False)
    organization_id = Column(UUID(as_uuid=True))
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    
    def check_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password_hash)
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    def to_dict(self) -> dict:
        return {
            'user_id': str(self.user_id),
            'email': self.email,
            'full_name': self.full_name,
            'phone': self.phone,
            'role': self.role,
            'organization_id': str(self.organization_id) if self.organization_id else None,
            'is_active': self.is_active,
            'is_verified': self.is_verified
        }

class AuthService:
    def __init__(self, db, redis, jwt_secret: str):
        self.db = db
        self.redis = redis
        self.jwt_secret = jwt_secret
    
    async def register(self, data: RegisterRequest) -> User:
        # Validate
        errors = validate_registration(data)
        if errors:
            raise ValidationError(errors)
        
        # Create user
        user = User(
            email=data.email,
            password_hash=User.hash_password(data.password),
            full_name=data.full_name,
            phone=data.phone,
            role=data.role or 'CITIZEN'
        )
        
        self.db.add(user)
        await self.db.commit()
        
        # Send verification email
        await self.send_verification_email(user)
        
        return user
    
    async def login(self, email: str, password: str) -> dict:
        # Check rate limit
        if not await self.check_rate_limit(email):
            raise RateLimitError("Too many login attempts")
        
        # Find user
        user = self.db.query(User).filter_by(email=email).first()
        if not user or not user.check_password(password):
            await self.record_failed_login(email)
            raise AuthenticationError("Invalid credentials")
        
        if not user.is_verified:
            raise AuthenticationError("Email not verified")
        
        # Generate tokens
        access_token = self.generate_jwt(user, token_type='access')
        refresh_token = self.generate_jwt(user, token_type='refresh')
        
        # Store refresh token in Redis
        await self.redis.setex(
            f"refresh:{user.user_id}",
            7 * 24 * 3600,  # 7 days
            refresh_token
        )
        
        return {
            'user': user.to_dict(),
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_in': 900  # 15 minutes
        }
```

---

### 4.2 Service Management Class Diagram

```
┌──────────────────────────────┐
│    ServiceManagementService  │
├──────────────────────────────┤
│ - db: Database               │
│ - redis: Redis               │
│ - notification_service       │
│ - geospatial_service         │
├──────────────────────────────┤
│ + create_request(data, user) │
│ + get_requests(filters)      │
│ + get_request(id)            │
│ + update_request(id, data)   │
│ + approve_request(id, user)  │
│ + assign_provider(id, prov)  │
│ + update_status(id, status)  │
│ + complete_service(id, proof)│
│ + verify_completion(id, user)│
│ - match_providers(request)   │
│ - notify_stakeholders(...)   │
└──────────────────────────────┘
          │
          │ uses
          ▼
┌──────────────────────────────┐
│      ServiceRequest          │
├──────────────────────────────┤
│ + service_id: UUID           │
│ + requestor_id: UUID         │
│ + service_type: enum         │
│ + priority: enum             │
│ + location: Point            │
│ + address: str               │
│ + description: str           │
│ + privacy_level: enum        │
│ + status: enum               │
│ + assigned_to: UUID          │
│ + disaster_event_id: UUID    │
│ + metadata: dict             │
├──────────────────────────────┤
│ + to_dict()                  │
│ + to_geojson()               │
│ + can_be_edited_by(user)     │
│ + transition_to(new_status)  │
└──────────────────────────────┘
```

---

## 5. Sequence Diagrams

### 5.1 Service Request Creation Flow

```
┌──────┐     ┌──────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐
│Client│     │ Bun  │     │ Service  │     │Database │     │  Notif   │
│      │     │Gateway│    │   Mgmt   │     │         │     │ Service  │
└───┬──┘     └───┬──┘     └────┬─────┘     └────┬────┘     └────┬─────┘
    │            │             │                │              │
    │ POST /services          │                │              │
    │ {service_type, ...}     │                │              │
    ├───────────>│             │                │              │
    │            │             │                │              │
    │            │ Validate JWT│                │              │
    │            ├─────────────┤                │              │
    │            │             │                │              │
    │            │ Check RBAC  │                │              │
    │            ├─────────────┤                │              │
    │            │             │                │              │
    │            │ POST /services               │              │
    │            │ {data}                       │              │
    │            ├────────────>│                │              │
    │            │             │                │              │
    │            │             │ Validate schema│              │
    │            │             ├───────────────┤│              │
    │            │             │                │              │
    │            │             │ Check CRITICAL?│              │
    │            │             │ Auto-approve   │              │
    │            │             ├───────────────┤│              │
    │            │             │                │              │
    │            │             │ INSERT request │              │
    │            │             ├───────────────>│              │
    │            │             │                │              │
    │            │             │<───────────────┤              │
    │            │             │ service_id     │              │
    │            │             │                │              │
    │            │             │ If CRITICAL:   │              │
    │            │             │ Match providers│              │
    │            │             ├───────────────┤│              │
    │            │             │                │              │
    │            │             │ UPDATE assign  │              │
    │            │             ├───────────────>│              │
    │            │             │                │              │
    │            │             │ Send notifications            │
    │            │             ├──────────────────────────────>│
    │            │             │                │              │
    │            │             │                │              │ Email/SMS
    │            │             │                │              ├──────────>
    │            │ {service_id,│                │              │
    │            │  status}    │                │              │
    │            │<────────────┤                │              │
    │            │             │                │              │
    │ 201 Created│             │                │              │
    │ {data}     │             │                │              │
    │<───────────┤             │                │              │
    │            │             │                │              │
```

---

### 5.2 Provider Matching and Assignment

```
┌──────────┐     ┌─────────┐     ┌──────────┐     ┌──────────┐
│ Service  │     │Database │     │Geospatial│     │  Notif   │
│   Mgmt   │     │         │     │          │     │ Service  │
└────┬─────┘     └────┬────┘     └────┬─────┘     └────┬─────┘
     │                │               │              │
     │ match_providers(request)       │              │
     ├────────────────┤               │              │
     │                │               │              │
     │ Query providers│               │              │
     │ ST_DWithin()   │               │              │
     ├───────────────>│               │              │
     │                │               │              │
     │<───────────────┤               │              │
     │ [providers]    │               │              │
     │                │               │              │
     │ Calculate match│               │              │
     │ scores         │               │              │
     ├───────────────┤│               │              │
     │                │               │              │
     │ Sort by score  │               │              │
     ├───────────────┤│               │              │
     │                │               │              │
     │ Top 3 matches  │               │              │
     │<───────────────┤               │              │
     │                │               │              │
     │ UPDATE service │               │              │
     │ SET assigned_to│               │              │
     ├───────────────>│               │              │
     │                │               │              │
     │ Send assignment│               │              │
     │ notification   ├──────────────────────────────>│
     │                │               │              │
     │                │               │              │ SMS/Email
     │                │               │              ├─────────>
     │                │               │              │
     │ Wait for accept│               │              │
     │ (10 min timeout)│              │              │
     ├───────────────┤│               │              │
     │                │               │              │
```

---

## 6. Algorithms & Pseudocode

### 6.1 Provider Matching Algorithm

**Algorithm**: Multi-Factor Scoring with Spatial Filtering

**Inputs**:
- `service_request`: ServiceRequest object
- `max_distance`: Distance threshold (based on priority)

**Output**:
- List of matched providers with scores

**Pseudocode**:
```
FUNCTION match_providers(service_request, max_distance):
    // Step 1: Spatial filtering
    candidates = QUERY providers WHERE:
        ST_DWithin(provider.location, service_request.location, max_distance)
        AND service_request.service_type IN provider.service_types
        AND provider.is_available = TRUE
        AND provider.current_load < provider.capacity
    
    // Step 2: Score each candidate
    scored_providers = []
    FOR EACH provider IN candidates:
        distance = ST_Distance(provider.location, service_request.location)
        
        // Distance component (40%)
        distance_score = (1 - distance / max_distance) * 0.4
        
        // Rating component (30%)
        rating_score = (provider.rating / 5.0) * 0.3
        
        // Load component (20%)
        load_ratio = provider.current_load / provider.capacity
        load_score = (1 - load_ratio) * 0.2
        
        // Response time component (10%)
        avg_response = provider.avg_response_time_minutes OR 60
        response_score = MAX(0, 1 - avg_response / 120) * 0.1
        
        total_score = distance_score + rating_score + load_score + response_score
        
        scored_providers.APPEND((provider, total_score, distance))
    
    // Step 3: Sort by score
    scored_providers.SORT_BY(total_score DESC)
    
    // Step 4: Return top 20
    RETURN scored_providers[0:20]
```

**Time Complexity**: O(n log n) where n = number of providers in radius  
**Space Complexity**: O(n)

---

### 6.2 Service Request Clustering (K-means)

**Algorithm**: Modified K-means for geographic clustering

**Inputs**:
- `requests`: List of service requests with locations
- `k`: Number of clusters

**Output**:
- List of cluster centers with request counts

**Pseudocode**:
```
FUNCTION cluster_requests(requests, k):
    // Step 1: Extract coordinates
    points = [request.location FOR request IN requests]
    
    // Step 2: Initialize centroids (k-means++)
    centroids = kmeans_plus_plus_init(points, k)
    
    // Step 3: Iterate until convergence
    max_iterations = 100
    FOR iteration IN range(max_iterations):
        // Assign points to nearest centroid
        clusters = assign_to_clusters(points, centroids)
        
        // Recalculate centroids
        new_centroids = []
        FOR cluster IN clusters:
            center = calculate_geographic_center(cluster.points)
            new_centroids.APPEND(center)
        
        // Check convergence
        IF distance(centroids, new_centroids) < threshold:
            BREAK
        
        centroids = new_centroids
    
    // Step 4: Build result
    result = []
    FOR i, centroid IN ENUMERATE(centroids):
        cluster_requests = clusters[i].requests
        result.APPEND({
            "center": centroid,
            "count": LENGTH(cluster_requests),
            "requests": cluster_requests,
            "service_types": aggregate_service_types(cluster_requests)
        })
    
    RETURN result

FUNCTION calculate_geographic_center(points):
    // Convert to Cartesian coordinates
    x_sum, y_sum, z_sum = 0, 0, 0
    FOR point IN points:
        lat, lng = point.latitude, point.longitude
        x = cos(lat) * cos(lng)
        y = cos(lat) * sin(lng)
        z = sin(lat)
        x_sum += x
        y_sum += y
        z_sum += z
    
    // Average
    x_avg = x_sum / LENGTH(points)
    y_avg = y_sum / LENGTH(points)
    z_avg = z_sum / LENGTH(points)
    
    // Convert back to lat/lng
    lng_center = atan2(y_avg, x_avg)
    hyp = sqrt(x_avg^2 + y_avg^2)
    lat_center = atan2(z_avg, hyp)
    
    RETURN Point(lat_center, lng_center)
```

---

### 6.3 Duplicate Detection Algorithm

**Algorithm**: Spatial-Temporal Similarity

**Inputs**:
- `new_request`: New service request
- `time_window`: Time window to check (default 24 hours)
- `distance_threshold`: Max distance to consider duplicate (default 1km)

**Output**:
- Boolean: is_duplicate

**Pseudocode**:
```
FUNCTION detect_duplicate(new_request, time_window=24h, distance_threshold=1000m):
    // Query recent requests of same type
    recent_requests = QUERY service_requests WHERE:
        service_type = new_request.service_type
        AND created_at > (NOW() - time_window)
        AND ST_DWithin(location, new_request.location, distance_threshold)
    
    // Check each for similarity
    FOR EACH existing IN recent_requests:
        // Spatial similarity (already filtered)
        distance = ST_Distance(existing.location, new_request.location)
        
        // Temporal similarity
        time_diff_hours = (new_request.created_at - existing.created_at).hours
        
        // Description similarity (Jaccard)
        desc_similarity = jaccard_similarity(
            tokenize(existing.description),
            tokenize(new_request.description)
        )
        
        // Composite similarity score
        similarity = (
            (1 - distance / distance_threshold) * 0.4 +
            (1 - time_diff_hours / 24) * 0.3 +
            desc_similarity * 0.3
        )
        
        IF similarity > 0.8:  // Threshold
            RETURN TRUE  // Duplicate
    
    RETURN FALSE  // Not duplicate

FUNCTION jaccard_similarity(set1, set2):
    intersection = LENGTH(set1 INTERSECT set2)
    union = LENGTH(set1 UNION set2)
    RETURN intersection / union
```

---

## 7. State Machines

### 7.1 Service Request State Machine

**States**:
- SUBMITTED
- UNDER_REVIEW
- APPROVED
- REJECTED
- ASSIGNED
- IN_PROGRESS
- COMPLETED
- VERIFIED
- CANCELLED
- DISPUTED

**Valid Transitions**:
```
SUBMITTED → UNDER_REVIEW (auto/manual)
SUBMITTED → APPROVED (if CRITICAL)

UNDER_REVIEW → APPROVED (authority approves)
UNDER_REVIEW → REJECTED (authority rejects)

APPROVED → ASSIGNED (provider accepts)
APPROVED → REJECTED (no providers available after 3 retries)

ASSIGNED → IN_PROGRESS (provider starts)
ASSIGNED → CANCELLED (provider cannot complete)

IN_PROGRESS → COMPLETED (provider finishes)
IN_PROGRESS → CANCELLED (cannot complete)

COMPLETED → VERIFIED (requestor confirms)
COMPLETED → DISPUTED (requestor disputes)

DISPUTED → VERIFIED (resolved, service OK)
DISPUTED → IN_PROGRESS (resolved, redo service)

CANCELLED → APPROVED (reassign)
```

**Implementation**:
```python
class ServiceStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    UNDER_REVIEW = "UNDER_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    CANCELLED = "CANCELLED"
    DISPUTED = "DISPUTED"

# Valid transitions map
VALID_TRANSITIONS = {
    ServiceStatus.SUBMITTED: [
        ServiceStatus.UNDER_REVIEW,
        ServiceStatus.APPROVED
    ],
    ServiceStatus.UNDER_REVIEW: [
        ServiceStatus.APPROVED,
        ServiceStatus.REJECTED
    ],
    ServiceStatus.APPROVED: [
        ServiceStatus.ASSIGNED,
        ServiceStatus.REJECTED
    ],
    ServiceStatus.ASSIGNED: [
        ServiceStatus.IN_PROGRESS,
        ServiceStatus.CANCELLED
    ],
    ServiceStatus.IN_PROGRESS: [
        ServiceStatus.COMPLETED,
        ServiceStatus.CANCELLED
    ],
    ServiceStatus.COMPLETED: [
        ServiceStatus.VERIFIED,
        ServiceStatus.DISPUTED
    ],
    ServiceStatus.DISPUTED: [
        ServiceStatus.VERIFIED,
        ServiceStatus.IN_PROGRESS
    ],
    ServiceStatus.CANCELLED: [
        ServiceStatus.APPROVED
    ],
    ServiceStatus.REJECTED: [],  # Terminal
    ServiceStatus.VERIFIED: []   # Terminal
}

def can_transition(current: ServiceStatus, new: ServiceStatus) -> bool:
    """Check if transition is valid"""
    return new in VALID_TRANSITIONS.get(current, [])

def transition_status(
    service: ServiceRequest,
    new_status: ServiceStatus,
    user: User,
    reason: str = None
) -> ServiceRequest:
    """
    Transition service status with validation
    """
    if not can_transition(service.status, new_status):
        raise InvalidTransitionError(
            f"Cannot transition from {service.status} to {new_status}"
        )
    
    # Log old status
    old_status = service.status
    
    # Update status
    service.status = new_status
    service.updated_at = datetime.now()
    
    # Status-specific logic
    if new_status == ServiceStatus.APPROVED:
        # Trigger provider matching
        match_providers(service)
    
    elif new_status == ServiceStatus.REJECTED:
        if not reason:
            raise ValueError("Rejection requires reason")
        service.rejection_reason = reason
    
    elif new_status == ServiceStatus.COMPLETED:
        service.completed_at = datetime.now()
        # Update provider capacity
        update_provider_load(service.assigned_to, -1)
    
    elif new_status == ServiceStatus.VERIFIED:
        service.verified_at = datetime.now()
    
    # Log transition in audit
    log_audit(
        user=user,
        action="STATUS_CHANGE",
        entity_type="service_request",
        entity_id=service.service_id,
        changes={
            "status": {
                "old": old_status,
                "new": new_status
            },
            "reason": reason
        }
    )
    
    # Notify stakeholders
    notify_status_change(service, old_status, new_status)
    
    return service
```

---

## 8. Data Structures

### 8.1 Spatial Data Structures

**PostGIS Geometry Storage**:
```sql
-- Point: Service request location
location GEOMETRY(Point, 4326)
-- Stored as WKB (Well-Known Binary)
-- Example: POINT(78.4867 17.3850)

-- Polygon: Coverage area
coverage_area GEOMETRY(Polygon, 4326)
-- Example: POLYGON((78.0 17.0, 79.0 17.0, 79.0 18.0, 78.0 18.0, 78.0 17.0))

-- SRID 4326: WGS 84 (latitude, longitude)
```

**GeoJSON Format** (for API responses):
```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]  // [longitude, latitude]
  },
  "properties": {
    "service_id": "...",
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "status": "APPROVED"
  }
}
```

---

### 8.2 Cache Data Structures

**Redis Data Structures**:

```python
# 1. Hash: User session
redis.hset('session:user_id', {
    'user_id': 'a1b2c3d4...',
    'refresh_token': 'eyJhbGci...',
    'created_at': '2026-05-10T10:00:00Z',
    'last_accessed': '2026-05-10T11:30:00Z'
})
redis.expire('session:user_id', 7 * 24 * 3600)  # 7 days

# 2. String: JWT blacklist (just existence check)
redis.setex('blacklist:token_hash', 7 * 24 * 3600, '1')

# 3. Hash: User profile cache
redis.hset('user:user_id', {
    'email': 'user@example.com',
    'full_name': 'John Doe',
    'role': 'CITIZEN',
    'org_id': None
})
redis.expire('user:user_id', 3600)  # 1 hour

# 4. Sorted Set: Nearby services (by distance)
redis.zadd('services:nearby:17.385:78.487', {
    'service_id_1': 850.5,    # distance in meters
    'service_id_2': 1250.3,
    'service_id_3': 2100.7
})
redis.expire('services:nearby:17.385:78.487', 300)  # 5 minutes

# 5. String (binary): Map tile cache
tile_png_bytes = generate_tile(z, x, y)
redis.setex(f'tile:{z}:{x}:{y}', 3600, tile_png_bytes)  # 1 hour
```

---

## 9. Error Handling

### 9.1 Error Response Schema

**Standard Error Format**:
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {
    // Optional additional details
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

### 9.2 Error Codes

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | VALIDATION_ERROR | Input validation failed |
| 401 | UNAUTHORIZED | Authentication required |
| 403 | FORBIDDEN | Insufficient permissions |
| 404 | NOT_FOUND | Resource not found |
| 409 | CONFLICT | Resource conflict (duplicate) |
| 422 | UNPROCESSABLE_ENTITY | Semantic error |
| 429 | RATE_LIMIT_EXCEEDED | Too many requests |
| 500 | INTERNAL_SERVER_ERROR | Server error |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable |

### 9.3 Error Handling Pattern

```python
class APIException(Exception):
    """Base API exception"""
    status_code = 500
    code = "INTERNAL_SERVER_ERROR"
    message = "An internal error occurred"
    
    def __init__(self, message=None, details=None):
        if message:
            self.message = message
        self.details = details or {}
    
    def to_dict(self):
        return {
            "status": "error",
            "message": self.message,
            "code": self.code,
            "details": self.details,
            "timestamp": datetime.now().isoformat(),
            "request_id": get_request_id()
        }

class ValidationError(APIException):
    status_code = 400
    code = "VALIDATION_ERROR"

class AuthenticationError(APIException):
    status_code = 401
    code = "UNAUTHORIZED"

class AuthorizationError(APIException):
    status_code = 403
    code = "FORBIDDEN"

class NotFoundError(APIException):
    status_code = 404
    code = "NOT_FOUND"

class RateLimitError(APIException):
    status_code = 429
    code = "RATE_LIMIT_EXCEEDED"

# Usage
@app.exception_handler(APIException)
async def api_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# In route
@app.post("/services")
async def create_service(request: CreateServiceRequest):
    try:
        # Validate
        errors = validate_service_request(request)
        if errors:
            raise ValidationError("Validation failed", details=errors)
        
        # Create
        service = await service_manager.create(request)
        return service
        
    except ValidationError as e:
        raise  # Re-raise to be caught by exception handler
    
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise APIException("An unexpected error occurred")
```

---

## 10. Performance Optimization

### 10.1 Database Query Optimization

**Use EXPLAIN ANALYZE**:
```sql
EXPLAIN ANALYZE
SELECT s.*, 
       ST_Distance(s.location::geography, ST_MakePoint(78.4867, 17.3850)::geography) as distance
FROM service_requests s
WHERE ST_DWithin(
    s.location::geography,
    ST_MakePoint(78.4867, 17.3850)::geography,
    5000
)
AND s.status = 'APPROVED'
ORDER BY distance
LIMIT 20;

-- Expected plan:
-- Bitmap Heap Scan on service_requests
--   Recheck Cond: (location is within 5000m of point)
--   Filter: (status = 'APPROVED')
--   -> Bitmap Index Scan on idx_service_requests_location_geog
--       Index Cond: (location within 5000m)
-- Planning Time: 0.5 ms
-- Execution Time: 12.3 ms
```

**Optimization Techniques**:

1. **Use Spatial Indexes**:
```sql
-- GiST index for spatial queries
CREATE INDEX idx_service_requests_location_geog 
    ON service_requests USING GIST((location::geography));
```

2. **Use Covering Indexes**:
```sql
-- Include frequently queried columns in index
CREATE INDEX idx_services_status_priority_incl 
    ON service_requests(status, priority)
    INCLUDE (service_type, created_at);
```

3. **Partial Indexes**:
```sql
-- Index only active providers
CREATE INDEX idx_active_providers 
    ON service_providers(is_available, capacity - current_load)
    WHERE is_available = TRUE;
```

4. **Materialized Views**:
```sql
-- Pre-compute analytics
CREATE MATERIALIZED VIEW service_stats AS
SELECT 
    service_type,
    status,
    DATE(created_at) as date,
    COUNT(*) as count,
    AVG(EXTRACT(EPOCH FROM (completed_at - created_at))) as avg_duration_seconds
FROM service_requests
GROUP BY service_type, status, DATE(created_at);

-- Refresh daily
REFRESH MATERIALIZED VIEW CONCURRENTLY service_stats;
```

---

### 10.2 Caching Strategy

**Cache Layers**:

```
┌─────────────────────────────────────┐
│  Application Cache (Redis)          │
│  - User profiles (1 hour)           │
│  - Service lists (5 min)            │
│  - Analytics (15 min)               │
│  TTL: Minutes to hours              │
└─────────────────────────────────────┘
          ↓ Cache miss
┌─────────────────────────────────────┐
│  Database Query Cache (PostgreSQL)  │
│  - Query result cache               │
│  - Shared buffer pool               │
└─────────────────────────────────────┘
          ↓ Not in cache
┌─────────────────────────────────────┐
│  Disk Storage                       │
└─────────────────────────────────────┘
```

**Cache Invalidation**:
```python
async def update_service_status(
    service_id: UUID,
    new_status: ServiceStatus
):
    # Update database
    service = await db.query(ServiceRequest).get(service_id)
    service.status = new_status
    await db.commit()
    
    # Invalidate caches
    await redis.delete(f'service:{service_id}')
    await redis.delete('services:recent')
    
    # Invalidate nearby services cache
    lat, lng = service.location.y, service.location.x
    lat_key = f"{lat:.3f}"
    lng_key = f"{lng:.3f}"
    await redis.delete(f'services:nearby:{lat_key}:{lng_key}')
    
    # Invalidate user-specific caches
    await redis.delete(f'services:user:{service.requestor_id}')
    if service.assigned_to:
        await redis.delete(f'services:provider:{service.assigned_to}')
```

---

### 10.3 API Performance

**Response Time Targets**:
```
GET  /services                 → < 300ms (p95)
POST /services                 → < 500ms (p95)
GET  /services/{id}            → < 100ms (p95)
GET  /tiles/{z}/{x}/{y}.png    → < 100ms (p95)
POST /services/{id}/assign     → < 200ms (p95)
GET  /analytics/dashboard      → < 2000ms (p95)
```

**Optimization Techniques**:

1. **Connection Pooling**:
```python
# SQLAlchemy connection pool
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

2. **Pagination**:
```python
# Always paginate large result sets
def get_services(page: int = 1, per_page: int = 20):
    if per_page > 100:
        per_page = 100  # Max limit
    
    offset = (page - 1) * per_page
    return db.query(ServiceRequest).offset(offset).limit(per_page).all()
```

3. **Field Selection (Sparse Fieldsets)**:
```python
# Allow clients to request specific fields
@app.get("/services")
async def get_services(fields: str = None):
    if fields:
        # SELECT only requested fields
        field_list = fields.split(',')
        query = db.query(
            *[getattr(ServiceRequest, f) for f in field_list]
        )
    else:
        query = db.query(ServiceRequest)
    
    return query.all()
```

4. **Response Compression**:
```python
# NGINX gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1000;
gzip_types application/json text/plain text/css application/javascript;
```

---

## Appendices

### A.1 Database Indexes Summary

| Table | Index Name | Type | Columns | Purpose |
|-------|-----------|------|---------|---------|
| users | idx_users_email | B-tree | email | Login lookup |
| users | idx_users_role | B-tree | role | Filter by role |
| service_requests | idx_service_requests_location | GiST | location | Spatial queries |
| service_requests | idx_service_requests_location_geog | GiST | location::geography | Distance queries |
| service_requests | idx_service_requests_status | B-tree | status | Filter by status |
| service_requests | idx_service_requests_status_priority | B-tree | status, priority | Combined filter |
| service_providers | idx_providers_coverage | GiST | coverage_area | Spatial coverage |
| service_providers | idx_providers_types | GIN | service_types | Array search |

---

### A.2 Redis Key Patterns

| Pattern | Type | TTL | Purpose |
|---------|------|-----|---------|
| `session:{user_id}` | Hash | 7 days | User session |
| `blacklist:{token}` | String | 7 days | Revoked tokens |
| `user:{user_id}` | Hash | 1 hour | User profile cache |
| `service:{service_id}` | Hash | 5 min | Service details cache |
| `services:recent` | List | 5 min | Recent services list |
| `services:nearby:{lat}:{lng}` | Sorted Set | 5 min | Nearby services |
| `tile:{z}:{x}:{y}` | String (binary) | 1 hour | Map tiles |
| `analytics:dashboard:{user_id}` | Hash | 15 min | Dashboard cache |
| `ratelimit:{user_id}:{endpoint}` | String | 1 min | Rate limiting |

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Technical Lead | TBD | | |
| Senior Developer | TBD | | |
| Database Architect | TBD | | |
| QA Lead | TBD | | |

---

**END OF LOW-LEVEL DESIGN**

**Document Version**: 2.0  
**Last Updated**: May 10, 2026  
**Status**: Final for MVP  
**Next Review**: Post-Implementation

---

**Note to Developers**: This LLD provides detailed specifications for implementation. Any deviations from this design must be reviewed and approved by the Technical Lead. All code must follow the patterns and structures defined here for consistency across the platform.
