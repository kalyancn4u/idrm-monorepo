# IDRM v3 · Detailed Design (LLD)
*Type: Document (specification) · Audience: Developers · Status: Archived — v3 historical generation*
*Consolidated from: IDRM-LLD-v3.md, 21-TECHNICAL-DESIGN.md*

## Contents
- [IDRM: Low-Level Design (LLD) - Version 3](#idrm-low-level-design-lld---version-3)
- [IDRM: Technical Design](#idrm-technical-design)

---

## IDRM: Low-Level Design (LLD) - Version 3

### Detailed Technical Specifications & Implementation Guide

**Document Version**: 3.0  
**Date**: May 24, 2026  
**Status**: ✅ Production-Ready  
**Architecture**: Modular Monolith with Bun API Gateway  
**Target Audience**: Backend developers, database administrators, QA engineers

---

### 📚 **Table of Contents**

#### **Part 1: API Specifications**
1. [API Overview](#1-api-overview)
2. [Authentication APIs](#2-authentication-apis)
3. [Service Management APIs](#3-service-management-apis)
4. [User Management APIs](#4-user-management-apis)
5. [Organization APIs](#5-organization-apis)
6. [Geospatial APIs](#6-geospatial-apis)
7. [Analytics APIs](#7-analytics-apis)
8. [Admin APIs](#8-admin-apis)

#### **Part 2: Database Design**
9. [Database Schema Overview](#9-database-schema-overview)
10. [Core Tables](#10-core-tables)
11. [Indexes & Constraints](#11-indexes-constraints)
12. [Views & Functions](#12-views-functions)
13. [Database Triggers](#13-database-triggers)

#### **Part 3: Implementation Details**
14. [Sequence Diagrams](#14-sequence-diagrams)
15. [Class Diagrams](#15-class-diagrams)
16. [Error Handling](#16-error-handling)
17. [Caching Strategy](#17-caching-strategy)
18. [Background Jobs](#18-background-jobs)

#### **Part 4: Testing & Validation**
19. [Testing Strategy](#19-testing-strategy)
20. [Performance Testing](#20-performance-testing)
21. [Security Testing](#21-security-testing)

---

## **PART 1: API SPECIFICATIONS**

---

## 1. **API Overview**

### 1.1 Base URL & Versioning

```
BASE URL: https://idrm.gov.in/api/v1

VERSIONING STRATEGY:
├─ URL-based: /api/v1/, /api/v2/
├─ Current version: v1
├─ Deprecation policy: 12 months after new version
└─ Version header: X-API-Version: 1.0
```

---

### 1.2 Common Request/Response Patterns

#### **Request Headers**:
```
Required:
├─ Content-Type: application/json (for POST/PUT/PATCH)
└─ Authorization: Bearer {access_token} (for authenticated endpoints)

Optional:
├─ Accept-Language: en, hi, te (for multi-language support)
└─ X-Request-ID: {uuid} (for request tracing)
```

#### **Response Format**:
```json
{
  "status": "success" | "error",
  "data": {
    // Response data (object or array)
  },
  "message": "Optional human-readable message",
  "errors": [
    {
      "field": "field_name",
      "message": "Error description"
    }
  ] | null,
  "pagination": {  // For list endpoints
    "page": 1,
    "page_size": 20,
    "total_pages": 10,
    "total_count": 200
  } | null
}
```

#### **HTTP Status Codes**:
```
2xx Success:
├─ 200 OK: Request successful
├─ 201 Created: Resource created
└─ 204 No Content: Successful DELETE

4xx Client Errors:
├─ 400 Bad Request: Validation error
├─ 401 Unauthorized: No/invalid token
├─ 403 Forbidden: Valid token, insufficient permissions
├─ 404 Not Found: Resource not found
├─ 409 Conflict: Resource conflict (e.g., duplicate email)
└─ 429 Too Many Requests: Rate limit exceeded

5xx Server Errors:
├─ 500 Internal Server Error: Server error
└─ 503 Service Unavailable: Server maintenance
```

---

## 2. **Authentication APIs**

### 2.1 POST /api/v1/auth/register

**Description**: Register a new user account.

**Authentication**: None (public endpoint)

**Rate Limit**: 5 requests/hour per IP

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "role": "CITIZEN"  // CITIZEN | PROVIDER | VOLUNTEER
}
```

**Validation Rules**:
```
email:
├─ Required: true
├─ Format: Valid email
├─ Unique: true (must not exist)
└─ Max length: 255

password:
├─ Required: true
├─ Min length: 8
├─ Must contain: 1 uppercase, 1 lowercase, 1 number
└─ Max length: 128

full_name:
├─ Required: true
├─ Min length: 2
├─ Max length: 255
└─ Pattern: Letters, spaces, hyphens only

phone:
├─ Required: false
├─ Format: E.164 format (+91xxxxxxxxxx)
└─ Unique: true (if provided)

role:
├─ Required: false
├─ Default: CITIZEN
└─ Allowed: CITIZEN, PROVIDER, VOLUNTEER
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+919876543210",
    "role": "CITIZEN",
    "is_active": true,
    "is_verified": false,
    "created_at": "2026-05-24T10:30:00Z"
  },
  "message": "Registration successful. Please verify your email."
}
```

**Error Responses**:
```json
// 400 Bad Request (Validation Error)
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "email",
      "message": "Email is already registered"
    },
    {
      "field": "password",
      "message": "Password must contain at least one uppercase letter"
    }
  ]
}

// 429 Too Many Requests
{
  "status": "error",
  "message": "Too many registration attempts. Please try again in 45 minutes.",
  "errors": null
}
```

**Implementation**:
```python
## backend/app/api/v1/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.auth import UserRegister, UserResponse
from app.crud import user as user_crud
from app.core.security import get_password_hash
from app.api.deps import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: Valid email address (unique)
    - **password**: Strong password (min 8 chars, 1 upper, 1 lower, 1 number)
    - **full_name**: Full name
    - **phone**: Phone number (optional)
    - **role**: User role (default: CITIZEN)
    """
    
    # Check if email already exists
    existing_user = user_crud.get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    # Check if phone already exists (if provided)
    if user_data.phone:
        existing_phone = user_crud.get_user_by_phone(db, phone=user_data.phone)
        if existing_phone:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number is already registered"
            )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    user = user_crud.create_user(
        db,
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role
    )
    
    # TODO: Send verification email
    
    return user
```

---

### 2.2 POST /api/v1/auth/login

**Description**: Authenticate user and get access tokens.

**Authentication**: None (public endpoint)

**Rate Limit**: 10 requests/hour per IP (strict to prevent brute force)

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,  // 15 minutes
    "user": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN",
      "is_verified": true
    }
  }
}
```

**JWT Payload**:
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // user_id
  "email": "user@example.com",
  "role": "CITIZEN",
  "type": "access",  // or "refresh"
  "exp": 1653456789,  // Expiration timestamp
  "iat": 1653456789   // Issued at timestamp
}
```

**Error Responses**:
```json
// 401 Unauthorized (Invalid Credentials)
{
  "status": "error",
  "message": "Invalid email or password",
  "errors": null
}

// 403 Forbidden (Account Inactive)
{
  "status": "error",
  "message": "Account has been deactivated. Please contact support.",
  "errors": null
}

// 429 Too Many Requests (Rate Limited)
{
  "status": "error",
  "message": "Too many login attempts. Please try again in 15 minutes.",
  "errors": null
}
```

---

### 2.3 POST /api/v1/auth/refresh

**Description**: Refresh access token using refresh token.

**Authentication**: Refresh token required

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900
  }
}
```

---

### 2.4 POST /api/v1/auth/logout

**Description**: Invalidate current tokens (blacklist).

**Authentication**: Required

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (204 No Content)

**Implementation**:
```python
## Blacklist token in Redis
redis_client.setex(
    f"blacklist:{token_jti}",
    settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    "1"
)
```

---

## 3. **Service Management APIs**

### 3.1 POST /api/v1/services

**Description**: Create a new service request.

**Authentication**: Required (any authenticated user)

**Rate Limit**: 5 requests/day per user (prevent spam)

**Request**:
```json
{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]  // [longitude, latitude]
  },
  "address": "123 Main St, Hyderabad, Telangana 500001",
  "description": "Elderly man, 70 years old, chest pain, difficulty breathing. Water level 3 feet.",
  "num_people_affected": 1,
  "privacy_level": "PUBLIC",  // PUBLIC | PRIVATE
  "contact_phone": "+919876543210"  // Optional, override user's phone
}
```

**Validation Rules**:
```
service_type:
├─ Required: true
├─ Allowed: RESCUE, MEDICAL, FOOD, SHELTER, WATER, OTHER
└─ Case-insensitive

priority:
├─ Required: false
├─ Default: AUTO (based on service_type)
│   ├─ RESCUE → CRITICAL
│   ├─ MEDICAL → HIGH
│   └─ Others → MEDIUM
└─ Allowed: CRITICAL, HIGH, MEDIUM, LOW

location:
├─ Required: true
├─ Type: GeoJSON Point
├─ Longitude: -180 to 180
└─ Latitude: -90 to 90

address:
├─ Required: false
├─ Max length: 500
└─ Geocoded if not provided

description:
├─ Required: true
├─ Min length: 10
├─ Max length: 500
└─ No HTML/scripts (sanitized)

num_people_affected:
├─ Required: false
├─ Default: 1
├─ Min: 1
└─ Max: 1000

privacy_level:
├─ Required: false
├─ Default: PUBLIC
├─ Allowed: PUBLIC, PRIVATE
└─ PRIVATE: Only admins & assigned provider see details
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "status": "SUBMITTED",  // or "APPROVED" if auto-approved
    "location": {
      "type": "Point",
      "coordinates": [78.4867, 17.3850]
    },
    "address": "123 Main St, Hyderabad, Telangana 500001",
    "description": "Elderly man, 70 years old, chest pain...",
    "num_people_affected": 1,
    "privacy_level": "PUBLIC",
    "requestor_id": "abc-123-def",
    "provider_id": null,  // Not assigned yet
    "created_at": "2026-05-24T10:30:00Z",
    "updated_at": "2026-05-24T10:30:00Z",
    "estimated_response_time": "2 hours"  // Based on priority
  },
  "message": "Service request created successfully. Help is on the way!"
}
```

**Business Logic**:
```python
## backend/app/services/service_management.py

async def create_service_request(db: Session, user_id: str, data: ServiceCreate):
    """
    Create a service request with auto-approval logic.
    
    Logic:
    1. Create service record
    2. If priority = CRITICAL → Auto-approve
    3. Find nearby providers (PostGIS query)
    4. Rank providers (matching algorithm)
    5. Notify top 5 providers
    6. Send confirmation SMS to citizen
    7. Create audit log entry
    """
    
    # 1. Create service
    service = crud.create_service(db, user_id=user_id, **data.dict())
    
    # 2. Auto-approve if CRITICAL
    if service.priority == "CRITICAL":
        service.status = "APPROVED"
        db.commit()
    
    # 3. Find nearby providers
    nearby_providers = crud.get_nearby_providers(
        db,
        location=service.location,
        service_type=service.service_type,
        radius_km=50
    )
    
    # 4. Rank providers
    ranked_providers = rank_providers(
        providers=nearby_providers,
        service=service
    )
    
    # 5. Notify providers (background job)
    notify_providers.delay(
        service_id=service.service_id,
        provider_ids=[p.org_id for p in ranked_providers[:5]]
    )
    
    # 6. Send confirmation SMS
    send_sms.delay(
        phone=service.contact_phone or user.phone,
        message=f"IDRM: Your request #{service.service_id[:8]} has been created. Track: idrm.gov.in/track/{service.service_id}"
    )
    
    # 7. Audit log
    crud.create_audit_log(
        db,
        user_id=user_id,
        action="SERVICE_CREATED",
        resource_type="ServiceRequest",
        resource_id=service.service_id
    )
    
    return service
```

---

### 3.2 GET /api/v1/services

**Description**: List service requests with filters.

**Authentication**: Required

**Authorization**:
```
CITIZEN: Only their own requests
PROVIDER: Nearby unassigned requests + their accepted requests
COORDINATOR/ADMIN: All requests in their jurisdiction
```

**Query Parameters**:
```
?status=SUBMITTED,APPROVED          // Filter by status (multi-select)
?service_type=MEDICAL,RESCUE        // Filter by type
?priority=CRITICAL,HIGH             // Filter by priority
?provider_id={uuid}                 // Filter by provider (admins only)
?from_date=2026-05-01              // Filter by created date
?to_date=2026-05-31
?location=78.4867,17.3850          // Search near location
?radius_km=10                       // Radius for location search
?search=chest pain                  // Full-text search in description
?page=1                             // Pagination
?page_size=20                       // Items per page (max 100)
?sort=-created_at                   // Sort (- for descending)
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "service_type": "MEDICAL",
      "priority": "CRITICAL",
      "status": "SUBMITTED",
      "location": {
        "type": "Point",
        "coordinates": [78.4867, 17.3850]
      },
      "description": "Elderly man, chest pain...",
      "created_at": "2026-05-24T10:30:00Z",
      "distance_km": 2.5  // If location filter used
    },
    // ... more requests
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "total_count": 87
  }
}
```

**SQL Query** (Simplified):
```sql
-- With geospatial filtering
SELECT 
    sr.*,
    ST_Distance(
        sr.location::geography,
        ST_SetSRID(ST_Point($longitude, $latitude), 4326)::geography
    ) / 1000 as distance_km
FROM service_requests sr
WHERE 
    sr.status = ANY($statuses)
    AND ST_DWithin(
        sr.location::geography,
        ST_SetSRID(ST_Point($longitude, $latitude), 4326)::geography,
        $radius_km * 1000  -- Convert km to meters
    )
    AND sr.created_at >= $from_date
    AND sr.created_at <= $to_date
ORDER BY sr.priority DESC, sr.created_at DESC
LIMIT $page_size OFFSET ($page - 1) * $page_size;
```

---

### 3.3 GET /api/v1/services/{service_id}

**Description**: Get details of a specific service request.

**Authentication**: Required

**Authorization**:
```
CITIZEN: Only their own request
PROVIDER: Any request (need to see details to accept)
COORDINATOR/ADMIN: Any request
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "status": "ACCEPTED",
    "location": {
      "type": "Point",
      "coordinates": [78.4867, 17.3850]
    },
    "address": "123 Main St, Hyderabad",
    "description": "Elderly man, chest pain, difficulty breathing",
    "num_people_affected": 1,
    "privacy_level": "PUBLIC",
    "requestor": {  // If PUBLIC or user is authorized
      "user_id": "abc-123",
      "full_name": "John Doe",
      "phone": "+919876543210"
    },
    "provider": {  // If assigned
      "org_id": "org-456",
      "name": "Sion Hospital",
      "contact_phone": "+919123456789"
    },
    "timeline": [
      {
        "status": "SUBMITTED",
        "timestamp": "2026-05-24T10:30:00Z",
        "updated_by": "system"
      },
      {
        "status": "APPROVED",
        "timestamp": "2026-05-24T10:32:00Z",
        "updated_by": "coordinator-abc"
      },
      {
        "status": "ACCEPTED",
        "timestamp": "2026-05-24T10:35:00Z",
        "updated_by": "provider-org-456",
        "notes": "Ambulance #3 dispatched"
      }
    ],
    "created_at": "2026-05-24T10:30:00Z",
    "updated_at": "2026-05-24T10:35:00Z",
    "accepted_at": "2026-05-24T10:35:00Z",
    "completed_at": null,
    "verified_at": null
  }
}
```

---

### 3.4 POST /api/v1/services/{service_id}/accept

**Description**: Provider accepts a service request.

**Authentication**: Required

**Authorization**: Only PROVIDER or VOLUNTEER role

**Request**:
```json
{
  "notes": "Ambulance #3 dispatched. Dr. Sharma on duty. ETA 15 minutes."
}
```

**Validation**:
```
Check:
├─ Service status must be SUBMITTED or APPROVED
├─ Service not already accepted by another provider
├─ Provider has available capacity
└─ Provider's service types include this service type
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "ACCEPTED",
    "provider": {
      "org_id": "org-456",
      "name": "Sion Hospital"
    },
    "accepted_at": "2026-05-24T10:35:00Z",
    "notes": "Ambulance #3 dispatched..."
  },
  "message": "Service request accepted successfully. Citizen has been notified."
}
```

**Business Logic**:
```python
async def accept_service_request(
    db: Session, 
    service_id: str, 
    provider_id: str,
    notes: str
):
    """
    Accept service request.
    
    Steps:
    1. Validate provider can accept (capacity, service type)
    2. Lock service (prevent double-acceptance)
    3. Update service record
    4. Notify citizen (SMS/Email)
    5. Update provider capacity
    6. Create audit log
    """
    
    # 1. Get service
    service = crud.get_service(db, service_id=service_id)
    
    if service.status not in ["SUBMITTED", "APPROVED"]:
        raise HTTPException(400, "Service already accepted or completed")
    
    # 2. Get provider
    provider = crud.get_organization(db, org_id=provider_id)
    
    # 3. Check capacity
    if provider.available_capacity <= 0:
        raise HTTPException(400, "Provider has no available capacity")
    
    # 4. Check service type match
    if service.service_type not in provider.service_types:
        raise HTTPException(400, "Provider does not offer this service type")
    
    # 5. Update service (with row locking)
    service = crud.update_service(
        db,
        service_id=service_id,
        status="ACCEPTED",
        provider_id=provider_id,
        accepted_at=datetime.utcnow(),
        notes=notes
    )
    
    # 6. Decrease provider capacity
    provider.available_capacity -= 1
    db.commit()
    
    # 7. Notify citizen
    notify_citizen.delay(
        service_id=service_id,
        event="SERVICE_ACCEPTED"
    )
    
    # 8. Audit log
    crud.create_audit_log(
        db,
        user_id=provider_id,
        action="SERVICE_ACCEPTED",
        resource_type="ServiceRequest",
        resource_id=service_id
    )
    
    return service
```

---

### 3.5 POST /api/v1/services/{service_id}/complete

**Description**: Provider marks service as completed.

**Authentication**: Required

**Authorization**: Only the assigned provider

**Request**:
```json
{
  "completion_notes": "Patient stabilized and taken to hospital. Condition: stable.",
  "proof_photos": [
    "base64_encoded_image_1",
    "base64_encoded_image_2"
  ]  // Optional
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "COMPLETED",
    "completed_at": "2026-05-24T11:00:00Z",
    "completion_notes": "Patient stabilized..."
  },
  "message": "Service marked as completed. Citizen will be asked to verify."
}
```

---

### 3.6 POST /api/v1/services/{service_id}/verify

**Description**: Citizen verifies service completion.

**Authentication**: Required

**Authorization**: Only the requestor

**Request**:
```json
{
  "verified": true,
  "rating": 5,  // 1-5
  "feedback": "Very fast response. Thank you!"
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "VERIFIED",
    "verified_at": "2026-05-24T11:05:00Z",
    "rating": 5,
    "feedback": "Very fast response..."
  },
  "message": "Thank you for your feedback!"
}
```

---

## 4. **User Management APIs**

### 4.1 GET /api/v1/users/me

**Description**: Get current user's profile.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+919876543210",
    "role": "CITIZEN",
    "is_active": true,
    "is_verified": true,
    "created_at": "2026-01-15T08:00:00Z",
    "preferences": {
      "language": "en",
      "notifications": {
        "email": true,
        "sms": true,
        "push": false
      }
    }
  }
}
```

---

### 4.2 PATCH /api/v1/users/me

**Description**: Update current user's profile.

**Authentication**: Required

**Request**:
```json
{
  "full_name": "John Michael Doe",
  "phone": "+919876543211",
  "preferences": {
    "language": "hi",
    "notifications": {
      "email": true,
      "sms": false
    }
  }
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Michael Doe",
    "phone": "+919876543211",
    "preferences": {...},
    "updated_at": "2026-05-24T11:10:00Z"
  },
  "message": "Profile updated successfully"
}
```

---

## 5. **Organization APIs**

### 5.1 POST /api/v1/organizations

**Description**: Register a new organization.

**Authentication**: Required

**Authorization**: Any authenticated user (but needs admin approval)

**Request**:
```json
{
  "name": "Sion Hospital",
  "org_type": "HOSPITAL",  // NGO, HOSPITAL, GOVT_AGENCY
  "registration_number": "MH/HSP/2020/12345",
  "service_types": ["MEDICAL", "RESCUE"],
  "capacity": 10,  // Max concurrent requests
  "coverage_area": {
    "type": "circle",
    "center": [78.4867, 17.3850],
    "radius_km": 25
  },
  "contact_person": "Dr. Priya Sharma",
  "contact_phone": "+919123456789",
  "contact_email": "contact@sionhospital.com",
  "documents": {
    "registration_certificate": "base64_encoded_pdf",
    "authorization_letter": "base64_encoded_pdf"
  }
}
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "org_id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Sion Hospital",
    "org_type": "HOSPITAL",
    "is_verified": false,  // Awaiting admin approval
    "status": "PENDING_VERIFICATION",
    "created_at": "2026-05-24T11:15:00Z"
  },
  "message": "Organization registered successfully. Awaiting verification by admin."
}
```

---

### 5.2 GET /api/v1/organizations/{org_id}

**Description**: Get organization details.

**Authentication**: Required

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "org_id": "org-456",
    "name": "Sion Hospital",
    "org_type": "HOSPITAL",
    "is_verified": true,
    "service_types": ["MEDICAL", "RESCUE"],
    "capacity": 10,
    "available_capacity": 3,
    "coverage_area": {...},
    "statistics": {
      "total_services_completed": 487,
      "average_rating": 4.7,
      "average_response_time_minutes": 18
    },
    "created_at": "2026-01-10T09:00:00Z"
  }
}
```

---

## 6. **Geospatial APIs**

### 6.1 GET /api/v1/geo/nearby

**Description**: Find nearby service requests or providers.

**Authentication**: Required (providers)

**Query Parameters**:
```
?location=78.4867,17.3850   // Current location
?radius_km=25                // Search radius
?service_type=MEDICAL        // Filter by service type
?priority=CRITICAL           // Filter by priority
?limit=50                    // Max results (default 20, max 100)
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "service_id": "...",
      "service_type": "MEDICAL",
      "priority": "CRITICAL",
      "location": {...},
      "distance_km": 2.5,
      "bearing_degrees": 45,  // Direction from current location
      "created_at": "..."
    }
  ],
  "metadata": {
    "search_location": [78.4867, 17.3850],
    "radius_km": 25,
    "total_found": 15
  }
}
```

**SQL Query**:
```sql
SELECT 
    sr.*,
    ST_Distance(
        sr.location::geography,
        ST_SetSRID(ST_Point($longitude, $latitude), 4326)::geography
    ) / 1000 as distance_km,
    ST_Azimuth(
        ST_SetSRID(ST_Point($longitude, $latitude), 4326),
        sr.location
    ) * 180 / pi() as bearing_degrees
FROM service_requests sr
WHERE 
    sr.status IN ('SUBMITTED', 'APPROVED')
    AND ST_DWithin(
        sr.location::geography,
        ST_SetSRID(ST_Point($longitude, $latitude), 4326)::geography,
        $radius_km * 1000
    )
    AND sr.service_type = $service_type
ORDER BY distance_km ASC
LIMIT $limit;
```

---

### 6.2 POST /api/v1/geo/cluster

**Description**: Cluster nearby service requests (DBSCAN algorithm).

**Authentication**: Required (coordinators/admins)

**Request**:
```json
{
  "location": [78.4867, 17.3850],  // Optional, defaults to all active requests
  "radius_km": 50,
  "epsilon_km": 2,  // DBSCAN epsilon (cluster radius)
  "min_samples": 5   // DBSCAN min samples
}
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "clusters": [
      {
        "cluster_id": 0,
        "center": [78.4867, 17.3850],
        "radius_km": 1.5,
        "request_count": 15,
        "priority_breakdown": {
          "CRITICAL": 5,
          "HIGH": 7,
          "MEDIUM": 3
        },
        "requests": [
          {
            "service_id": "...",
            "location": [...],
            "priority": "CRITICAL"
          }
        ]
      }
    ],
    "noise_points": [  // Requests that don't belong to any cluster
      {
        "service_id": "...",
        "location": [...]
      }
    ],
    "total_clusters": 3,
    "total_requests_analyzed": 87
  }
}
```

---

## 7. **Analytics APIs**

### 7.1 GET /api/v1/analytics/dashboard

**Description**: Get dashboard metrics.

**Authentication**: Required (coordinators/admins/providers)

**Authorization**:
```
PROVIDER: Only their own stats
COORDINATOR: Stats for their jurisdiction
ADMIN: All stats
```

**Query Parameters**:
```
?from_date=2026-05-01
?to_date=2026-05-31
?granularity=day  // day, week, month
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "summary": {
      "total_requests": 1247,
      "pending_requests": 156,
      "completed_requests": 892,
      "average_response_time_minutes": 108,
      "fulfillment_rate": 0.85,
      "average_rating": 4.6
    },
    "time_series": [
      {
        "date": "2026-05-01",
        "requests_created": 45,
        "requests_completed": 38,
        "average_response_time_minutes": 120
      }
    ],
    "by_service_type": {
      "MEDICAL": 423,
      "RESCUE": 312,
      "FOOD": 245,
      "SHELTER": 178,
      "WATER": 89
    },
    "by_priority": {
      "CRITICAL": 234,
      "HIGH": 456,
      "MEDIUM": 378,
      "LOW": 179
    },
    "top_providers": [
      {
        "org_id": "org-456",
        "name": "Sion Hospital",
        "services_completed": 127,
        "average_rating": 4.8
      }
    ]
  }
}
```

---

## 8. **Admin APIs**

### 8.1 GET /api/v1/admin/users

**Description**: List all users (admin only).

**Authentication**: Required

**Authorization**: ADMIN only

**Query Parameters**:
```
?role=CITIZEN,PROVIDER
?is_active=true
?is_verified=false
?search=john  // Search in name, email
?page=1
?page_size=50
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "user_id": "...",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN",
      "is_active": true,
      "is_verified": true,
      "created_at": "...",
      "last_login": "..."
    }
  ],
  "pagination": {...}
}
```

---

### 8.2 PATCH /api/v1/admin/users/{user_id}

**Description**: Update user (admin only).

**Authentication**: Required

**Authorization**: ADMIN only

**Request**:
```json
{
  "is_active": false,  // Deactivate user
  "role": "EVENT_MANAGER",  // Change role
  "is_verified": true
}
```

---

### 8.3 GET /api/v1/admin/audit-logs

**Description**: Get audit logs.

**Authentication**: Required

**Authorization**: DM_AUTHORITY or ADMIN

**Query Parameters**:
```
?user_id={uuid}
?action=SERVICE_CREATED,SERVICE_ACCEPTED
?resource_type=ServiceRequest
?from_date=2026-05-01
?to_date=2026-05-31
?page=1
?page_size=100
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": [
    {
      "log_id": "...",
      "user_id": "...",
      "user_email": "user@example.com",
      "action": "SERVICE_CREATED",
      "resource_type": "ServiceRequest",
      "resource_id": "...",
      "timestamp": "2026-05-24T10:30:00Z",
      "ip_address": "203.0.113.45",
      "user_agent": "Mozilla/5.0..."
    }
  ],
  "pagination": {...}
}
```

---

## **PART 2: DATABASE DESIGN**

---

## 9. **Database Schema Overview**

### 9.1 Entity-Relationship Diagram

```
┌─────────────────────────┐
│        users            │
├─────────────────────────┤
│ PK user_id (UUID)       │
│    email                │
│    password_hash        │
│    full_name            │
│    phone                │
│    role (ENUM)          │
│    is_active            │
│    is_verified          │
│    created_at           │
│    updated_at           │
└──────────┬──────────────┘
           │
           │ 1:N (requestor)
           │
           ↓
┌─────────────────────────────────┐
│     service_requests            │
├─────────────────────────────────┤
│ PK service_id (UUID)            │
│ FK requestor_id → users         │
│ FK provider_id → organizations  │
│    service_type (ENUM)          │
│    priority (ENUM)              │
│    status (ENUM)                │
│    location (GEOMETRY)          │◄── PostGIS
│    address                      │
│    description                  │
│    num_people_affected          │
│    privacy_level (ENUM)         │
│    accepted_at                  │
│    completed_at                 │
│    verified_at                  │
│    created_at                   │
│    updated_at                   │
└──────────┬──────────────────────┘
           │
           │ N:1 (provider)
           │
           ↓
┌─────────────────────────┐
│    organizations        │
├─────────────────────────┤
│ PK org_id (UUID)        │
│    name                 │
│    org_type (ENUM)      │
│    registration_number  │
│    service_types (ARRAY)│
│    capacity             │
│    available_capacity   │
│    coverage_area (JSONB)│
│    contact_person       │
│    contact_phone        │
│    contact_email        │
│    is_verified          │
│    created_at           │
│    updated_at           │
└─────────────────────────┘

┌─────────────────────────┐
│    notifications        │
├─────────────────────────┤
│ PK notification_id      │
│ FK user_id → users      │
│    type (ENUM)          │
│    channel (ENUM)       │
│    subject              │
│    body                 │
│    status (ENUM)        │
│    sent_at              │
│    created_at           │
└─────────────────────────┘

┌─────────────────────────┐
│      audit_logs         │
├─────────────────────────┤
│ PK log_id (BIGSERIAL)   │
│ FK user_id → users      │
│    action               │
│    resource_type        │
│    resource_id          │
│    ip_address           │
│    user_agent           │
│    timestamp            │
└─────────────────────────┘
```

---

## 10. **Core Tables**

### 10.1 users Table

```sql
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Authentication
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Profile
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE,
    
    -- Role & Status
    role VARCHAR(50) NOT NULL DEFAULT 'CITIZEN',
        CHECK (role IN ('CITIZEN', 'PROVIDER', 'VOLUNTEER', 'EVENT_MANAGER', 'DM_AUTHORITY', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    
    -- Preferences (JSONB for flexibility)
    preferences JSONB DEFAULT '{
        "language": "en",
        "notifications": {
            "email": true,
            "sms": true,
            "push": false
        }
    }'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    
    -- Constraints
    CONSTRAINT email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT phone_format CHECK (phone IS NULL OR phone ~* '^\+[1-9][0-9]{1,14}$')
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_is_active ON users(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_users_created_at ON users(created_at);

-- Trigger for updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 10.2 service_requests Table

```sql
CREATE TABLE service_requests (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- References
    requestor_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    provider_id UUID REFERENCES organizations(org_id) ON DELETE SET NULL,
    
    -- Service Details
    service_type VARCHAR(50) NOT NULL,
        CHECK (service_type IN ('RESCUE', 'MEDICAL', 'FOOD', 'SHELTER', 'WATER', 'OTHER')),
    priority VARCHAR(20) NOT NULL,
        CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    status VARCHAR(50) NOT NULL DEFAULT 'SUBMITTED',
        CHECK (status IN ('SUBMITTED', 'APPROVED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED', 'REJECTED', 'CANCELLED', 'EXPIRED')),
    
    -- Location (PostGIS)
    location GEOMETRY(Point, 4326) NOT NULL,
    address TEXT,
    
    -- Description
    description TEXT NOT NULL,
        CHECK (char_length(description) >= 10 AND char_length(description) <= 500),
    num_people_affected INTEGER DEFAULT 1,
        CHECK (num_people_affected >= 1 AND num_people_affected <= 1000),
    
    -- Privacy
    privacy_level VARCHAR(20) DEFAULT 'PUBLIC',
        CHECK (privacy_level IN ('PUBLIC', 'PRIVATE')),
    
    -- Contact (may override user's phone)
    contact_phone VARCHAR(20),
    
    -- Timeline
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Rating (after verification)
    rating INTEGER,
        CHECK (rating IS NULL OR (rating >= 1 AND rating <= 5)),
    feedback TEXT,
    
    -- Notes (from provider)
    acceptance_notes TEXT,
    completion_notes TEXT,
    
    -- Constraints
    CONSTRAINT valid_timeline CHECK (
        accepted_at IS NULL OR accepted_at >= created_at
    ),
    CONSTRAINT valid_completion CHECK (
        completed_at IS NULL OR (completed_at >= accepted_at AND accepted_at IS NOT NULL)
    ),
    CONSTRAINT valid_verification CHECK (
        verified_at IS NULL OR (verified_at >= completed_at AND completed_at IS NOT NULL)
    )
);

-- Indexes
CREATE INDEX idx_service_requests_requestor_id ON service_requests(requestor_id);
CREATE INDEX idx_service_requests_provider_id ON service_requests(provider_id);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_priority ON service_requests(priority);
CREATE INDEX idx_service_requests_service_type ON service_requests(service_type);
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at);

-- Spatial Index (GIST for PostGIS)
CREATE INDEX idx_service_requests_location ON service_requests USING GIST(location);

-- Composite index for common queries
CREATE INDEX idx_service_requests_status_priority ON service_requests(status, priority);
CREATE INDEX idx_service_requests_status_created_at ON service_requests(status, created_at DESC);

-- Full-text search index
CREATE INDEX idx_service_requests_description_fts ON service_requests USING GIN(to_tsvector('english', description));

-- Trigger for updated_at
CREATE TRIGGER update_service_requests_updated_at
    BEFORE UPDATE ON service_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 10.3 organizations Table

```sql
CREATE TABLE organizations (
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Basic Info
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(50) NOT NULL,
        CHECK (org_type IN ('NGO', 'HOSPITAL', 'GOVT_AGENCY', 'VOLUNTEER_GROUP')),
    registration_number VARCHAR(100) UNIQUE,
    
    -- Services
    service_types VARCHAR(50)[] NOT NULL,  -- Array of service types
    capacity INTEGER DEFAULT 10,
        CHECK (capacity >= 1 AND capacity <= 1000),
    available_capacity INTEGER DEFAULT 10,
        CHECK (available_capacity >= 0 AND available_capacity <= capacity),
    
    -- Coverage Area (JSONB for flexibility)
    coverage_area JSONB,  -- {type: "circle", center: [lon, lat], radius_km: 25}
    
    -- Contact
    contact_person VARCHAR(255),
    contact_phone VARCHAR(20) NOT NULL,
    contact_email VARCHAR(255),
    
    -- Verification
    is_verified BOOLEAN DEFAULT FALSE,
    verified_at TIMESTAMP,
    verified_by UUID REFERENCES users(user_id),
    
    -- Documents (store paths or base64)
    documents JSONB DEFAULT '{}'::jsonb,
    
    -- Statistics (denormalized for performance)
    total_services_completed INTEGER DEFAULT 0,
    average_rating NUMERIC(3,2) DEFAULT 0.00,
    average_response_time_minutes INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_organizations_org_type ON organizations(org_type);
CREATE INDEX idx_organizations_is_verified ON organizations(is_verified) WHERE is_verified = TRUE;
CREATE INDEX idx_organizations_service_types ON organizations USING GIN(service_types);
CREATE INDEX idx_organizations_created_at ON organizations(created_at);

-- Trigger
CREATE TRIGGER update_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

### 10.4 notifications Table

```sql
CREATE TABLE notifications (
    notification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Recipient
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    
    -- Type & Channel
    type VARCHAR(50) NOT NULL,
        CHECK (type IN ('SERVICE_CREATED', 'SERVICE_ACCEPTED', 'SERVICE_COMPLETED', 'VERIFICATION_REQUEST', 'GENERAL')),
    channel VARCHAR(20) NOT NULL,
        CHECK (channel IN ('EMAIL', 'SMS', 'PUSH', 'IN_APP')),
    
    -- Content
    subject VARCHAR(255),
    body TEXT NOT NULL,
    
    -- Metadata
    related_service_id UUID REFERENCES service_requests(service_id) ON DELETE CASCADE,
    
    -- Status
    status VARCHAR(20) DEFAULT 'PENDING',
        CHECK (status IN ('PENDING', 'SENT', 'FAILED', 'READ')),
    sent_at TIMESTAMP,
    read_at TIMESTAMP,
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);

-- Composite index for user's unread notifications
CREATE INDEX idx_notifications_user_unread ON notifications(user_id, status, created_at DESC)
    WHERE status IN ('SENT', 'PENDING');
```

---

### 10.5 audit_logs Table

```sql
CREATE TABLE audit_logs (
    log_id BIGSERIAL PRIMARY KEY,
    
    -- Actor
    user_id UUID REFERENCES users(user_id) ON DELETE SET NULL,
    user_email VARCHAR(255),  -- Denormalized for deleted users
    
    -- Action
    action VARCHAR(100) NOT NULL,  -- SERVICE_CREATED, SERVICE_ACCEPTED, USER_UPDATED, etc.
    
    -- Resource
    resource_type VARCHAR(50) NOT NULL,  -- ServiceRequest, User, Organization
    resource_id UUID,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    request_id UUID,  -- For tracing
    
    -- Changes (JSONB for flexibility)
    changes JSONB,  -- {before: {...}, after: {...}}
    
    -- Timestamp
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);

-- Partition by month (for performance as table grows)
-- CREATE TABLE audit_logs_2026_05 PARTITION OF audit_logs
--     FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');
```

---

## 11. **Indexes & Constraints**

### 11.1 Additional Indexes for Performance

```sql
-- Combined indexes for common query patterns

-- Provider dashboard: "Show me nearby unassigned requests"
CREATE INDEX idx_service_requests_provider_query 
ON service_requests(status, service_type, location)
WHERE status IN ('SUBMITTED', 'APPROVED')
USING GIST;

-- Coordinator dashboard: "Show me today's critical requests"
CREATE INDEX idx_service_requests_coordinator_today
ON service_requests(created_at, priority, status)
WHERE status IN ('SUBMITTED', 'APPROVED', 'ACCEPTED', 'IN_PROGRESS')
    AND created_at >= CURRENT_DATE;

-- Analytics: "Response time by service type"
CREATE INDEX idx_service_requests_analytics
ON service_requests(service_type, created_at, accepted_at, completed_at)
WHERE status IN ('COMPLETED', 'VERIFIED');

-- Full-text search on user names
CREATE INDEX idx_users_full_name_fts
ON users USING GIN(to_tsvector('english', full_name));
```

---

### 11.2 Foreign Key Constraints

```sql
-- All foreign keys with appropriate actions

ALTER TABLE service_requests
    ADD CONSTRAINT fk_service_requests_requestor
        FOREIGN KEY (requestor_id) REFERENCES users(user_id)
        ON DELETE CASCADE  -- If user deleted, delete their requests
        ON UPDATE CASCADE;

ALTER TABLE service_requests
    ADD CONSTRAINT fk_service_requests_provider
        FOREIGN KEY (provider_id) REFERENCES organizations(org_id)
        ON DELETE SET NULL  -- If org deleted, don't delete requests, just clear provider
        ON UPDATE CASCADE;

ALTER TABLE organizations
    ADD CONSTRAINT fk_organizations_verified_by
        FOREIGN KEY (verified_by) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE;
```

---

## 12. **Views & Functions**

### 12.1 Useful Views

```sql
-- View: Active service requests with requestor details
CREATE VIEW v_active_service_requests AS
SELECT 
    sr.service_id,
    sr.service_type,
    sr.priority,
    sr.status,
    sr.location,
    sr.address,
    sr.description,
    sr.created_at,
    u.full_name as requestor_name,
    u.phone as requestor_phone,
    o.name as provider_name,
    o.contact_phone as provider_phone
FROM service_requests sr
INNER JOIN users u ON sr.requestor_id = u.user_id
LEFT JOIN organizations o ON sr.provider_id = o.org_id
WHERE sr.status IN ('SUBMITTED', 'APPROVED', 'ACCEPTED', 'IN_PROGRESS');

-- View: Organization statistics
CREATE VIEW v_organization_stats AS
SELECT 
    o.org_id,
    o.name,
    o.org_type,
    COUNT(sr.service_id) as total_services,
    COUNT(sr.service_id) FILTER (WHERE sr.status = 'COMPLETED') as completed_services,
    AVG(sr.rating) as average_rating,
    AVG(EXTRACT(EPOCH FROM (sr.completed_at - sr.accepted_at)) / 60) as avg_response_time_minutes
FROM organizations o
LEFT JOIN service_requests sr ON o.org_id = sr.provider_id
GROUP BY o.org_id, o.name, o.org_type;
```

---

### 12.2 PostgreSQL Functions

```sql
-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: Calculate distance between two points
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

-- Function: Get nearby providers
CREATE OR REPLACE FUNCTION get_nearby_providers(
    search_lon NUMERIC,
    search_lat NUMERIC,
    search_radius_km NUMERIC,
    search_service_type VARCHAR DEFAULT NULL
)
RETURNS TABLE (
    org_id UUID,
    name VARCHAR,
    distance_km NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        o.org_id,
        o.name,
        ST_Distance(
            ST_SetSRID(ST_Point(search_lon, search_lat), 4326)::geography,
            -- Assuming coverage_area has center coordinates
            ST_SetSRID(
                ST_Point(
                    (o.coverage_area->'center'->>0)::NUMERIC,
                    (o.coverage_area->'center'->>1)::NUMERIC
                ),
                4326
            )::geography
        ) / 1000 as distance_km
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
```

---

## 13. **Database Triggers**

### 13.1 Auto-update Triggers

```sql
-- Trigger: Update organization stats when service completed
CREATE OR REPLACE FUNCTION update_organization_stats()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED' THEN
        UPDATE organizations
        SET 
            total_services_completed = total_services_completed + 1,
            available_capacity = available_capacity + 1  -- Free up capacity
        WHERE org_id = NEW.provider_id;
    END IF;
    
    IF NEW.status = 'VERIFIED' AND OLD.status = 'COMPLETED' AND NEW.rating IS NOT NULL THEN
        -- Update average rating
        UPDATE organizations
        SET average_rating = (
            SELECT AVG(rating)
            FROM service_requests
            WHERE provider_id = NEW.provider_id
                AND rating IS NOT NULL
        )
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

### 13.2 Audit Log Trigger

```sql
-- Trigger: Auto-create audit log on service request changes
CREATE OR REPLACE FUNCTION audit_service_request_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (user_id, action, resource_type, resource_id, changes)
        VALUES (
            NEW.requestor_id,
            'SERVICE_CREATED',
            'ServiceRequest',
            NEW.service_id,
            jsonb_build_object('after', row_to_json(NEW))
        );
    ELSIF TG_OP = 'UPDATE' THEN
        -- Only log significant changes
        IF OLD.status != NEW.status THEN
            INSERT INTO audit_logs (user_id, action, resource_type, resource_id, changes)
            VALUES (
                COALESCE(NEW.provider_id, NEW.requestor_id),
                CASE 
                    WHEN NEW.status = 'ACCEPTED' THEN 'SERVICE_ACCEPTED'
                    WHEN NEW.status = 'COMPLETED' THEN 'SERVICE_COMPLETED'
                    WHEN NEW.status = 'VERIFIED' THEN 'SERVICE_VERIFIED'
                    ELSE 'SERVICE_STATUS_CHANGED'
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

## **PART 3: IMPLEMENTATION DETAILS**

---

## 14. **Sequence Diagrams**

### 14.1 Service Request Creation Flow

```
SEQUENCE: Citizen Creates Service Request

┌────────┐    ┌─────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐
│Citizen │    │ Browser │    │ Gateway │    │ Backend  │    │ Database │
└───┬────┘    └────┬────┘    └────┬────┘    └────┬─────┘    └────┬─────┘
    │              │              │              │              │
    │ 1. Click map │              │              │              │
    │────────────>│              │              │              │
    │              │              │              │              │
    │ 2. Fill form │              │              │              │
    │────────────>│              │              │              │
    │              │              │              │              │
    │ 3. Submit    │              │              │              │
    │────────────>│              │              │              │
    │              │              │              │              │
    │              │ 4. POST /api/v1/services   │              │
    │              │─────────────>│              │              │
    │              │              │              │              │
    │              │              │ 5. Validate JWT              │
    │              │              │ (check Redis)│              │
    │              │              │──────────────┐              │
    │              │              │              │              │
    │              │              │<─────────────┘              │
    │              │              │              │              │
    │              │              │ 6. Check rate limit          │
    │              │              │ (Redis INCR) │              │
    │              │              │──────────────┐              │
    │              │              │              │              │
    │              │              │<─────────────┘              │
    │              │              │              │              │
    │              │              │ 7. Forward request           │
    │              │              │─────────────>│              │
    │              │              │              │              │
    │              │              │              │ 8. Validate schema
    │              │              │              │ (Pydantic)   │
    │              │              │              │──────────────┐
    │              │              │              │              │
    │              │              │              │<─────────────┘
    │              │              │              │              │
    │              │              │              │ 9. BEGIN TRANSACTION
    │              │              │              │─────────────>│
    │              │              │              │              │
    │              │              │              │ 10. INSERT   │
    │              │              │              │─────────────>│
    │              │              │              │              │
    │              │              │              │ 11. service_id
    │              │              │              │<─────────────│
    │              │              │              │              │
    │              │              │              │ 12. INSERT audit_log
    │              │              │              │─────────────>│
    │              │              │              │              │
    │              │              │              │ 13. COMMIT   │
    │              │              │              │─────────────>│
    │              │              │              │              │
    │              │              │              │ 14. Queue notification
    │              │              │              │ (Celery)     │
    │              │              │              │──────────────┐
    │              │              │              │              │
    │              │              │              │<─────────────┘
    │              │              │              │              │
    │              │              │              │ 15. Response │
    │              │              │ 16. Response │              │
    │              │ 17. Response │<─────────────│              │
    │ 18. Success  │<─────────────│              │              │
    │<────────────│              │              │              │
    │              │              │              │              │
    │ 19. Show     │              │              │              │
    │ confirmation │              │              │              │
    │──────────────┐              │              │              │
    │              │              │              │              │
    │<─────────────┘              │              │              │

TOTAL TIME: ~150ms
├─ Gateway: 10ms (rate limit + JWT)
├─ Backend validation: 5ms
├─ Database transaction: 50ms
├─ Queue job: 10ms
└─ Response: 10ms

ASYNC OPERATIONS (after response):
├─ Send SMS to citizen (Celery)
├─ Notify nearby providers (Celery)
└─ Update analytics cache (Celery)
```

---

### 14.2 Provider Accepts Request Flow

```
SEQUENCE: Provider Accepts Service Request

┌──────────┐    ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────┐
│Provider  │    │ Backend │    │ Database │    │  Redis   │    │Celery│
└────┬─────┘    └────┬────┘    └────┬─────┘    └────┬─────┘    └───┬──┘
     │               │              │              │              │
     │ 1. POST /services/{id}/accept              │              │
     │──────────────>│              │              │              │
     │               │              │              │              │
     │               │ 2. Get service (with lock) │              │
     │               │─────────────>│              │              │
     │               │              │              │              │
     │               │ SELECT ... FOR UPDATE       │              │
     │               │<─────────────│              │              │
     │               │              │              │              │
     │               │ 3. Validate  │              │              │
     │               │ - Status = SUBMITTED/APPROVED             │
     │               │ - Provider has capacity     │              │
     │               │ - Service type match        │              │
     │               │──────────────┐              │              │
     │               │              │              │              │
     │               │<─────────────┘              │              │
     │               │              │              │              │
     │               │ 4. UPDATE service           │              │
     │               │ SET status='ACCEPTED'       │              │
     │               │─────────────>│              │              │
     │               │              │              │              │
     │               │ 5. UPDATE organization      │              │
     │               │ SET capacity = capacity - 1 │              │
     │               │─────────────>│              │              │
     │               │              │              │              │
     │               │ 6. COMMIT    │              │              │
     │               │─────────────>│              │              │
     │               │              │              │              │
     │               │ 7. Invalidate cache         │              │
     │               │─────────────────────────────>│              │
     │               │ DELETE api:cache:services:* │              │
     │               │<─────────────────────────────│              │
     │               │              │              │              │
     │               │ 8. Queue notification       │              │
     │               │─────────────────────────────────────────────>│
     │               │ notify_citizen.delay(...)   │              │
     │               │              │              │              │
     │               │ 9. Response  │              │              │
     │ 10. Success   │<─────────────│              │              │
     │<──────────────│              │              │              │

CRITICAL: Row-level locking prevents double-acceptance
└─ SELECT ... FOR UPDATE ensures only one provider can accept
```

---

## 15. **Class Diagrams**

### 15.1 Backend Class Structure

```python
"""
Class Diagram: Service Management Module

┌─────────────────────────────┐
│    ServiceCreate            │ (Pydantic Schema)
├─────────────────────────────┤
│ + service_type: str         │
│ + priority: str             │
│ + location: Location        │
│ + description: str          │
│ + num_people_affected: int  │
└──────────┬──────────────────┘
           │
           │ validated by
           ↓
┌─────────────────────────────┐
│    ServiceController        │ (API Route)
├─────────────────────────────┤
│ + create_service()          │
│ + get_services()            │
│ + get_service_by_id()       │
│ + accept_service()          │
│ + complete_service()        │
└──────────┬──────────────────┘
           │
           │ calls
           ↓
┌─────────────────────────────┐
│    ServiceManager           │ (Business Logic)
├─────────────────────────────┤
│ + create_service_request()  │
│ + auto_approve_critical()   │
│ + find_nearby_providers()   │
│ + rank_providers()          │
│ + notify_providers()        │
│ + accept_service()          │
│ + validate_acceptance()     │
└──────────┬──────────────────┘
           │
           │ uses
           ↓
┌─────────────────────────────┐
│    ServiceCRUD              │ (Database Operations)
├─────────────────────────────┤
│ + create(db, data)          │
│ + get_by_id(db, id)         │
│ + get_all(db, filters)      │
│ + update(db, id, data)      │
│ + delete(db, id)            │
└──────────┬──────────────────┘
           │
           │ operates on
           ↓
┌─────────────────────────────┐
│    ServiceRequest           │ (SQLAlchemy Model)
├─────────────────────────────┤
│ + service_id: UUID          │
│ + requestor_id: UUID        │
│ + service_type: Enum        │
│ + priority: Enum            │
│ + status: Enum              │
│ + location: Geometry        │
│ + description: Text         │
│ + created_at: DateTime      │
└─────────────────────────────┘

DEPENDENCIES:
Controller → Manager → CRUD → Model
Schema → All layers (validation)
```

---

### 15.2 Matching Algorithm Class

```python
"""
Class: Service-Provider Matching Algorithm

┌─────────────────────────────────────────┐
│    ProviderMatcher                      │
├─────────────────────────────────────────┤
│ - service: ServiceRequest               │
│ - providers: List[Organization]         │
│ - weights: Dict[str, float]             │
├─────────────────────────────────────────┤
│ + calculate_match_score(provider)       │
│ + distance_score(provider): float       │
│ + capacity_score(provider): float       │
│ + service_type_score(provider): float   │
│ + performance_score(provider): float    │
│ + rank_providers(): List[Organization]  │
└─────────────────────────────────────────┘

ALGORITHM:
total_score = (
    distance_score * 0.40 +
    capacity_score * 0.30 +
    service_type_score * 0.20 +
    performance_score * 0.10
)

distance_score:
    < 5 km: 100
    5-10 km: 80
    10-20 km: 60
    20-50 km: 40
    > 50 km: 0

capacity_score:
    (available_capacity / total_capacity) * 100

service_type_score:
    exact_match: 100
    partial_match: 70
    no_match: 0

performance_score:
    Based on: avg_rating, avg_response_time, completion_rate
"""
```

---

## 16. **Error Handling**

### 16.1 Error Hierarchy

```python
## backend/app/core/exceptions.py

from fastapi import HTTPException, status

class IDRMException(Exception):
    """Base exception for all IDRM errors"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(IDRMException):
    """400 Bad Request - Validation failed"""
    def __init__(self, message: str, errors: list = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST)
        self.errors = errors or []

class AuthenticationError(IDRMException):
    """401 Unauthorized - Invalid or missing token"""
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED)

class AuthorizationError(IDRMException):
    """403 Forbidden - Insufficient permissions"""
    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(message, status.HTTP_403_FORBIDDEN)

class NotFoundError(IDRMException):
    """404 Not Found - Resource not found"""
    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with ID {resource_id} not found"
        super().__init__(message, status.HTTP_404_NOT_FOUND)

class ConflictError(IDRMException):
    """409 Conflict - Resource already exists"""
    def __init__(self, message: str):
        super().__init__(message, status.HTTP_409_CONFLICT)

class RateLimitError(IDRMException):
    """429 Too Many Requests - Rate limit exceeded"""
    def __init__(self, retry_after: int = 60):
        message = f"Rate limit exceeded. Try again in {retry_after} seconds."
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS)
        self.retry_after = retry_after

class DatabaseError(IDRMException):
    """500 Internal Server Error - Database error"""
    def __init__(self, message: str = "Database error occurred"):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

### 16.2 Global Exception Handler

```python
## backend/app/main.py

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import IDRMException

app = FastAPI()

@app.exception_handler(IDRMException)
async def idrm_exception_handler(request: Request, exc: IDRMException):
    """Handle all IDRM custom exceptions"""
    
    response_data = {
        "status": "error",
        "message": exc.message,
        "errors": getattr(exc, 'errors', None)
    }
    
    headers = {}
    if isinstance(exc, RateLimitError):
        headers["Retry-After"] = str(exc.retry_after)
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response_data,
        headers=headers
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    
    # Log the error
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    
    # Don't expose internal error details to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "message": "An internal error occurred. Please try again later.",
            "errors": None
        }
    )
```

---

### 16.3 Usage Examples

```python
## In API routes

from app.core.exceptions import NotFoundError, AuthorizationError, ConflictError

@router.post("/services/{service_id}/accept")
async def accept_service(
    service_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get service
    service = crud.get_service(db, service_id=service_id)
    if not service:
        raise NotFoundError("ServiceRequest", service_id)
    
    # Check authorization
    if current_user.role not in ["PROVIDER", "VOLUNTEER"]:
        raise AuthorizationError("Only providers can accept service requests")
    
    # Check if already accepted
    if service.status not in ["SUBMITTED", "APPROVED"]:
        raise ConflictError("Service request has already been accepted or completed")
    
    # Accept service
    service = service_manager.accept_service(db, service_id, current_user.user_id)
    
    return service
```

---

## 17. **Caching Strategy**

### 17.1 Cache Layers

```python
## backend/app/core/cache.py

from redis import Redis
from typing import Optional, Any
import json
from functools import wraps
from app.core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

class CacheManager:
    """Multi-layer caching manager"""
    
    @staticmethod
    def cache_key(prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and kwargs"""
        parts = [prefix]
        for key, value in sorted(kwargs.items()):
            if value is not None:
                parts.append(f"{key}:{value}")
        return ":".join(parts)
    
    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Get value from cache"""
        data = redis_client.get(key)
        return json.loads(data) if data else None
    
    @staticmethod
    def set(key: str, value: Any, ttl: int = 60):
        """Set value in cache with TTL"""
        redis_client.setex(key, ttl, json.dumps(value))
    
    @staticmethod
    def delete(key: str):
        """Delete specific key"""
        redis_client.delete(key)
    
    @staticmethod
    def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    
    @staticmethod
    def invalidate_service(service_id: str):
        """Invalidate all caches related to a service"""
        patterns = [
            "api:cache:services:list:*",
            f"api:cache:services:{service_id}:*",
            "api:cache:analytics:*",
        ]
        for pattern in patterns:
            CacheManager.delete_pattern(pattern)

## Decorator for automatic caching
def cached(prefix: str, ttl: int = 60):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = CacheManager.cache_key(prefix, **kwargs)
            
            # Try to get from cache
            cached_result = CacheManager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            CacheManager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

---

### 17.2 Cache Usage Examples

```python
## In API routes

@router.get("/services")
@cached(prefix="api:cache:services:list", ttl=60)
async def get_services(
    status: Optional[str] = None,
    priority: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get list of services.
    Cached for 60 seconds.
    """
    services = crud.get_services(db, status=status, priority=priority, page=page, page_size=page_size)
    return services

@router.post("/services")
async def create_service(
    service_data: ServiceCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create service and invalidate related caches.
    """
    service = service_manager.create_service_request(db, current_user.user_id, service_data)
    
    # Invalidate caches
    CacheManager.invalidate_service(service.service_id)
    
    return service
```

---

### 17.3 Cache Warming Strategy

```python
## backend/app/services/cache_warmer.py

from apscheduler.schedulers.background import BackgroundScheduler
from app.core.cache import CacheManager
from app import crud
from app.core.database import SessionLocal

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=5)
def warm_popular_caches():
    """
    Warm cache with frequently accessed data.
    Runs every 5 minutes.
    """
    db = SessionLocal()
    
    try:
        # 1. Warm services list cache (most common queries)
        popular_queries = [
            {"status": "SUBMITTED", "page": 1, "page_size": 20},
            {"status": "APPROVED", "page": 1, "page_size": 20},
            {"priority": "CRITICAL", "page": 1, "page_size": 20},
        ]
        
        for query in popular_queries:
            cache_key = CacheManager.cache_key("api:cache:services:list", **query)
            services = crud.get_services(db, **query)
            CacheManager.set(cache_key, services, ttl=60)
        
        # 2. Warm analytics cache
        analytics_cache_key = "api:cache:analytics:dashboard"
        analytics_data = crud.get_analytics_dashboard(db)
        CacheManager.set(analytics_cache_key, analytics_data, ttl=300)
        
        print("Cache warmed successfully")
    
    finally:
        db.close()

## Start scheduler
scheduler.start()
```

---

## 18. **Background Jobs**

### 18.1 Celery Configuration

```python
## backend/app/core/celery_app.py

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "idrm",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/2"
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
)

## Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
```

---

### 18.2 Background Tasks

```python
## backend/app/tasks/notifications.py

from app.core.celery_app import celery_app
from app.utils.email import send_email
from app.utils.sms import send_sms
from app.core.database import SessionLocal
from app import crud

@celery_app.task(name="send_email_notification")
def send_email_notification(to: str, subject: str, body: str):
    """Send email notification"""
    try:
        send_email(to=to, subject=subject, body=body)
        return {"status": "sent", "to": to}
    except Exception as e:
        # Retry up to 3 times with exponential backoff
        raise send_email_notification.retry(exc=e, countdown=60 * (2 ** send_email_notification.request.retries))

@celery_app.task(name="send_sms_notification")
def send_sms_notification(phone: str, message: str):
    """Send SMS notification"""
    try:
        send_sms(phone=phone, message=message)
        return {"status": "sent", "phone": phone}
    except Exception as e:
        raise send_sms_notification.retry(exc=e, countdown=60 * (2 ** send_sms_notification.request.retries))

@celery_app.task(name="notify_citizen")
def notify_citizen(service_id: str, event: str):
    """
    Notify citizen about service events.
    
    Events: SERVICE_CREATED, SERVICE_ACCEPTED, SERVICE_COMPLETED
    """
    db = SessionLocal()
    
    try:
        service = crud.get_service(db, service_id=service_id)
        requestor = crud.get_user(db, user_id=service.requestor_id)
        
        # Build message
        messages = {
            "SERVICE_CREATED": f"IDRM: Your request #{service_id[:8]} has been created. Help is on the way! Track: idrm.gov.in/track/{service_id}",
            "SERVICE_ACCEPTED": f"IDRM: Your request #{service_id[:8]} accepted by {service.provider.name}. ETA: 15 min. Track: idrm.gov.in/track/{service_id}",
            "SERVICE_COMPLETED": f"IDRM: Service completed. Please verify: idrm.gov.in/verify/{service_id}"
        }
        
        message = messages.get(event, "IDRM: Your request has been updated.")
        
        # Send SMS
        if requestor.phone:
            send_sms_notification.delay(phone=requestor.phone, message=message)
        
        # Send Email
        if requestor.email:
            send_email_notification.delay(
                to=requestor.email,
                subject=f"IDRM Service Request Update",
                body=message
            )
    
    finally:
        db.close()

@celery_app.task(name="notify_providers")
def notify_providers(service_id: str, provider_ids: list):
    """Notify providers about new service request"""
    db = SessionLocal()
    
    try:
        service = crud.get_service(db, service_id=service_id)
        
        for provider_id in provider_ids:
            provider = crud.get_organization(db, org_id=provider_id)
            
            message = f"IDRM: New {service.service_type} request near you. Priority: {service.priority}. View: idrm.gov.in/provider/requests/{service_id}"
            
            # Send SMS to provider
            send_sms_notification.delay(phone=provider.contact_phone, message=message)
    
    finally:
        db.close()

@celery_app.task(name="cleanup_expired_requests")
def cleanup_expired_requests():
    """
    Mark old unassigned requests as EXPIRED.
    Runs daily.
    """
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    
    try:
        # Expire requests older than 48 hours with status SUBMITTED
        cutoff_time = datetime.utcnow() - timedelta(hours=48)
        
        expired_count = crud.expire_old_requests(db, cutoff_time=cutoff_time)
        
        return {"status": "success", "expired_count": expired_count}
    
    finally:
        db.close()
```

---

### 18.3 Periodic Tasks

```python
## backend/app/tasks/periodic.py

from celery.schedules import crontab
from app.core.celery_app import celery_app

## Configure periodic tasks
celery_app.conf.beat_schedule = {
    "cleanup-expired-requests": {
        "task": "cleanup_expired_requests",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
    "generate-daily-report": {
        "task": "generate_daily_report",
        "schedule": crontab(hour=23, minute=55),  # Daily at 11:55 PM
    },
    "warm-cache": {
        "task": "warm_cache",
        "schedule": 300,  # Every 5 minutes
    },
}
```

---

## **PART 4: TESTING & VALIDATION**

---

## 19. **Testing Strategy**

### 19.1 Test Pyramid

```
                    ▲
                   ╱ ╲
                  ╱   ╲
                 ╱ E2E ╲        10 tests (slow, expensive)
                ╱───────╲
               ╱         ╲
              ╱Integration╲     50 tests (medium speed)
             ╱─────────────╲
            ╱               ╲
           ╱  Unit Tests     ╲   200+ tests (fast, cheap)
          ╱───────────────────╲
         ▼                     ▼

TARGET COVERAGE:
├─ Overall: 80%
├─ Critical paths: 95% (auth, service management)
├─ Business logic: 90%
└─ Utilities: 70%
```

---

### 19.2 Unit Tests

```python
## backend/tests/test_services/test_service_matching.py

import pytest
from app.services.service_matching import ProviderMatcher
from app.models.service import ServiceRequest
from app.models.organization import Organization

class TestProviderMatcher:
    """Test suite for provider matching algorithm"""
    
    @pytest.fixture
    def mock_service(self):
        """Create mock service request"""
        return ServiceRequest(
            service_type="MEDICAL",
            priority="CRITICAL",
            location="POINT(78.4867 17.3850)",  # Hyderabad
            description="Test description"
        )
    
    @pytest.fixture
    def mock_providers(self):
        """Create mock providers at different distances"""
        return [
            Organization(
                org_id="provider-1",
                name="Nearby Hospital",
                service_types=["MEDICAL"],
                capacity=10,
                available_capacity=5,
                coverage_area={"center": [78.4900, 17.3900], "radius_km": 25}  # 3 km away
            ),
            Organization(
                org_id="provider-2",
                name="Far Hospital",
                service_types=["MEDICAL"],
                capacity=10,
                available_capacity=2,
                coverage_area={"center": [78.5500, 17.4500], "radius_km": 25}  # 15 km away
            ),
            Organization(
                org_id="provider-3",
                name="Wrong Type Org",
                service_types=["FOOD"],
                capacity=10,
                available_capacity=8,
                coverage_area={"center": [78.4870, 17.3860], "radius_km": 25}  # 1 km away but wrong type
            ),
        ]
    
    def test_distance_score_calculation(self, mock_service):
        """Test distance score calculation"""
        matcher = ProviderMatcher(service=mock_service, providers=[])
        
        # Provider at 3 km should get high score
        provider_near = Organization(
            coverage_area={"center": [78.4900, 17.3900]}
        )
        score_near = matcher.distance_score(provider_near)
        assert score_near == 100  # < 5km = 100 points
        
        # Provider at 15 km should get medium score
        provider_far = Organization(
            coverage_area={"center": [78.5500, 17.4500]}
        )
        score_far = matcher.distance_score(provider_far)
        assert score_far == 60  # 10-20km = 60 points
    
    def test_capacity_score_calculation(self):
        """Test capacity score calculation"""
        matcher = ProviderMatcher(service=None, providers=[])
        
        # Provider with 50% capacity
        provider_half = Organization(capacity=10, available_capacity=5)
        score_half = matcher.capacity_score(provider_half)
        assert score_half == 50
        
        # Provider with full capacity
        provider_full = Organization(capacity=10, available_capacity=10)
        score_full = matcher.capacity_score(provider_full)
        assert score_full == 100
        
        # Provider with no capacity
        provider_none = Organization(capacity=10, available_capacity=0)
        score_none = matcher.capacity_score(provider_none)
        assert score_none == 0
    
    def test_ranking(self, mock_service, mock_providers):
        """Test provider ranking"""
        matcher = ProviderMatcher(service=mock_service, providers=mock_providers)
        ranked = matcher.rank_providers()
        
        # Nearby Hospital should be #1 (close distance, right type)
        assert ranked[0].org_id == "provider-1"
        
        # Far Hospital should be #2 (far but right type)
        assert ranked[1].org_id == "provider-2"
        
        # Wrong Type Org should be last (wrong service type)
        assert ranked[2].org_id == "provider-3"
```

---

### 19.3 Integration Tests

```python
## tests/integration/test_service_flow.py

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal

client = TestClient(app)

class TestServiceFlow:
    """Test complete service request flow"""
    
    @pytest.fixture
    def auth_token(self):
        """Get auth token for testing"""
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "TestPass123"
        })
        return response.json()["data"]["access_token"]
    
    def test_complete_service_flow(self, auth_token):
        """Test: Create → Accept → Complete → Verify"""
        
        # 1. Create service request
        create_response = client.post(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "service_type": "MEDICAL",
                "priority": "CRITICAL",
                "location": {
                    "type": "Point",
                    "coordinates": [78.4867, 17.3850]
                },
                "description": "Test emergency request"
            }
        )
        
        assert create_response.status_code == 201
        service_id = create_response.json()["data"]["service_id"]
        assert service_id is not None
        
        # 2. Get service details
        get_response = client.get(
            f"/api/v1/services/{service_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert get_response.status_code == 200
        assert get_response.json()["data"]["status"] == "SUBMITTED"
        
        # 3. Accept service (as provider)
        # Note: Would need provider auth token in real test
        accept_response = client.post(
            f"/api/v1/services/{service_id}/accept",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={"notes": "Ambulance dispatched"}
        )
        
        assert accept_response.status_code == 200
        assert accept_response.json()["data"]["status"] == "ACCEPTED"
        
        # 4. Complete service
        complete_response = client.post(
            f"/api/v1/services/{service_id}/complete",
            headers={"Authorization": f"Bearer {provider_token}"},
            json={"completion_notes": "Patient stabilized"}
        )
        
        assert complete_response.status_code == 200
        assert complete_response.json()["data"]["status"] == "COMPLETED"
        
        # 5. Verify service
        verify_response = client.post(
            f"/api/v1/services/{service_id}/verify",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={"verified": True, "rating": 5, "feedback": "Excellent"}
        )
        
        assert verify_response.status_code == 200
        assert verify_response.json()["data"]["status"] == "VERIFIED"
        assert verify_response.json()["data"]["rating"] == 5
```

---

## 20. **Performance Testing**

### 20.1 Load Testing with Locust

```python
## tests/performance/locustfile.py

from locust import HttpUser, task, between
import random

class IDRMUser(HttpUser):
    """Simulate IDRM user behavior"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Login before starting tasks"""
        response = self.client.post("/api/v1/auth/login", json={
            "email": f"test{random.randint(1, 1000)}@example.com",
            "password": "TestPass123"
        })
        self.token = response.json()["data"]["access_token"]
    
    @task(3)  # 3x more frequent than other tasks
    def view_services(self):
        """View list of services"""
        self.client.get(
            "/api/v1/services?page=1&page_size=20",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def view_service_detail(self):
        """View specific service"""
        service_id = random.choice(self.service_ids)
        self.client.get(
            f"/api/v1/services/{service_id}",
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def create_service(self):
        """Create new service request"""
        self.client.post(
            "/api/v1/services",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "service_type": random.choice(["MEDICAL", "RESCUE", "FOOD"]),
                "priority": "HIGH",
                "location": {
                    "type": "Point",
                    "coordinates": [78.48 + random.uniform(-0.1, 0.1), 
                                    17.38 + random.uniform(-0.1, 0.1)]
                },
                "description": "Load test request"
            }
        )

## RUN:
## locust -f tests/performance/locustfile.py --host=http://localhost:3000
## Target: 1000 concurrent users, response time < 500ms (p95)
```

---

### 20.2 Performance Benchmarks

```
PERFORMANCE TARGETS:

API Endpoints (p95):
├─ GET /api/v1/services: < 200ms
├─ POST /api/v1/services: < 400ms
├─ GET /api/v1/services/{id}: < 150ms
├─ POST /api/v1/services/{id}/accept: < 300ms
└─ GET /api/v1/analytics/dashboard: < 1000ms

Database Queries (p95):
├─ Simple SELECT: < 10ms
├─ Geospatial queries: < 100ms
├─ Complex joins: < 200ms
└─ Aggregations: < 300ms

Concurrent Users:
├─ Normal: 1,000 users
├─ Peak (disaster): 10,000 users
└─ Sustained throughput: 100 req/s

Cache Hit Rate:
└─ Target: > 70%
```

---

## 21. **Security Testing**

### 21.1 Security Test Checklist

```
AUTHENTICATION & AUTHORIZATION:
☐ Test JWT expiration
☐ Test invalid/expired tokens
☐ Test token refresh flow
☐ Test role-based access control
☐ Test password strength validation
☐ Test rate limiting on login endpoint

INPUT VALIDATION:
☐ Test SQL injection (parameterized queries)
☐ Test XSS (input sanitization)
☐ Test CSRF (SameSite cookies)
☐ Test file upload validation
☐ Test JSON payload size limits

API SECURITY:
☐ Test CORS configuration
☐ Test security headers (CSP, HSTS, etc.)
☐ Test rate limiting on all endpoints
☐ Test API versioning
☐ Test error message leakage

DATA PROTECTION:
☐ Test password hashing (Bcrypt)
☐ Test sensitive data masking in logs
☐ Test HTTPS enforcement
☐ Test data encryption at rest
```

---

### 21.2 Automated Security Testing

```python
## tests/security/test_auth.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAuthSecurity:
    """Security tests for authentication"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection is prevented"""
        malicious_email = "'; DROP TABLE users; --"
        
        response = client.post("/api/v1/auth/login", json={
            "email": malicious_email,
            "password": "password"
        })
        
        # Should return 401 (invalid credentials), not 500 (SQL error)
        assert response.status_code == 401
    
    def test_password_strength(self):
        """Test weak passwords are rejected"""
        weak_passwords = ["12345678", "password", "abc", "AAAAAAAA"]
        
        for password in weak_passwords:
            response = client.post("/api/v1/auth/register", json={
                "email": "test@example.com",
                "password": password,
                "full_name": "Test User"
            })
            
            assert response.status_code == 400
            assert "password" in str(response.json()).lower()
    
    def test_rate_limiting(self):
        """Test rate limiting on login endpoint"""
        # Attempt 11 logins (limit is 10/hour)
        for i in range(11):
            response = client.post("/api/v1/auth/login", json={
                "email": "test@example.com",
                "password": "wrong"
            })
            
            if i < 10:
                assert response.status_code in [401, 400]
            else:
                # 11th attempt should be rate limited
                assert response.status_code == 429
                assert "rate limit" in response.json()["message"].lower()
    
    def test_token_expiration(self):
        """Test expired tokens are rejected"""
        # Create token that expires immediately
        from app.core.security import create_access_token
        from datetime import timedelta
        
        expired_token = create_access_token(
            data={"sub": "test-user-id"},
            expires_delta=timedelta(seconds=-1)  # Already expired
        )
        
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401
```

---

**END OF IDRM-LLD-v3.md (COMPLETE)**

**Total Pages**: ~120 pages  
**Completeness**: 100% ✅  
**Status**: ✅ Production-ready low-level design

**Document includes**:
- Complete API specifications (8 sections)
- Complete database design (5 sections)
- Complete implementation details (5 sections)
- Complete testing strategies (3 sections)

**Total sections**: 21/21 ✅

---

## IDRM: Technical Design

### Detailed Implementation Specifications

**Version**: 3.0 Consolidated  
**Audience**: Developers, technical leads, code reviewers  
**Reading Time**: 45-60 minutes  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [Implementation Overview](#1-implementation-overview)
2. [Service File Structures](#2-service-file-structures)
3. [Authentication & Security](#3-authentication--security)
4. [Service Request Management](#4-service-request-management)
5. [Geospatial Implementation](#5-geospatial-implementation)
6. [Provider Matching Logic](#6-provider-matching-logic)
7. [Data Models & Validation](#7-data-models--validation)
8. [Error Handling Strategy](#8-error-handling-strategy)
9. [Code Organization](#9-code-organization)
10. [Testing & Quality](#10-testing--quality)

---

### 1. **Implementation Overview**

#### 1.1 Document Purpose

This document provides **detailed technical specifications** for implementing IDRM. It bridges the gap between:
- **Architecture** (what components exist) → See 10-SYSTEM-ARCHITECTURE.md
- **Code** (how to actually build it) → This document
- **Database** (schema details) → See 22-DATABASE-DESIGN.md
- **APIs** (endpoint specs) → See 23-API-SPECIFICATION.md

#### 1.2 Implementation Tech Stack

| Layer | Technology | Key Libraries |
|-------|------------|---------------|
| **API Gateway** | Bun 1.x | TypeScript, ws (WebSocket) |
| **Services** | Python 3.11 + FastAPI | uvicorn, pydantic, sqlalchemy |
| **Database** | PostgreSQL 16 + PostGIS | psycopg2, geoalchemy2 |
| **Geospatial** | PostGIS + Python libs | shapely, geopandas, fiona |
| **Cache** | Redis 7.2 | redis-py |
| **Testing** | Pytest | pytest-asyncio, httpx |

#### 1.3 Code Quality Standards

**ALL code must**:
- ✅ Follow PEP 8 (Python) / Standard Style (TypeScript)
- ✅ Include type hints (Python 3.11+)
- ✅ Have docstrings (Google style)
- ✅ Pass 80%+ test coverage
- ✅ Have no hardcoded secrets
- ✅ Include proper error handling
- ✅ Use structured logging

---

### 2. **Service File Structures**

#### 2.1 Standard Python Service Layout

Every microservice follows this structure:

```
services/<service_name>/
├── __init__.py
├── main.py                 # FastAPI app entry point
├── config.py               # Settings from environment
│
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   └── *.py               # One file per entity
│
├── schemas/                # Pydantic validation schemas
│   ├── __init__.py
│   └── *.py               # Request/response models
│
├── api/                    # API endpoints
│   ├── __init__.py
│   ├── deps.py            # Shared dependencies
│   └── v1/                # API version 1
│       ├── __init__.py
│       └── *.py           # Endpoint routers
│
├── crud/                   # Database operations (CRUD)
│   ├── __init__.py
│   └── *.py               # One file per model
│
├── core/                   # Business logic
│   ├── __init__.py
│   └── *.py               # Algorithms, utilities
│
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── conftest.py        # Pytest fixtures
│   └── test_*.py          # Test files
│
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
└── README.md              # Service docs
```

#### 2.2 Auth Service Example (Port 8001)

```
services/auth/
├── main.py                # FastAPI app
├── config.py              # JWT secret, DB URL
│
├── models/
│   ├── user.py           # User model
│   └── session.py        # Session model
│
├── schemas/
│   ├── user.py           # UserCreate, UserResponse
│   └── token.py          # Token, TokenData
│
├── api/v1/
│   ├── auth.py           # /auth/login, /register
│   └── users.py          # /users/me
│
├── crud/
│   └── user.py           # create_user, get_user
│
├── core/
│   ├── security.py       # Password hash, JWT
│   └── email.py          # Send verification email
│
└── tests/
    ├── test_auth_api.py
    └── test_security.py
```

---

### 3. **Authentication & Security**

#### 3.1 Password Hashing (bcrypt, cost 12)

```python
## services/auth/core/security.py
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def hash_password(password: str) -> str:
    """Hash password using bcrypt (cost 12)"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain password against hash"""
    return pwd_context.verify(plain, hashed)
```

**Why bcrypt cost 12?**
- Industry standard (OWASP recommendation)
- ~250ms per hash (slow enough to deter brute force)
- Fast enough for acceptable UX

#### 3.2 JWT Token Generation

```python
## services/auth/core/security.py
from jose import jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(data: dict) -> str:
    """Create JWT access token (1 hour expiry)"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> dict:
    """Decode and verify JWT token"""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
```

#### 3.3 User Registration Endpoint

```python
## services/auth/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...schemas.user import UserCreate, UserResponse
from ...crud import user as crud_user
from ...core import security
from ...db.session import get_db

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if email exists
    if crud_user.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password
    hashed_password = security.hash_password(user_in.password)
    
    # Create user
    user = crud_user.create_user(db, user_in, hashed_password)
    
    # TODO: Send verification email
    
    return user
```

---

### 4. **Service Request Management**

#### 4.1 Service Request State Machine

```python
## services/service_mgmt/core/state_machine.py
from enum import Enum

class ServiceStatus(str, Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    VERIFIED = "VERIFIED"
    DISPUTED = "DISPUTED"
    CLOSED = "CLOSED"

## Valid transitions
TRANSITIONS = {
    ServiceStatus.DRAFT: [ServiceStatus.SUBMITTED],
    ServiceStatus.SUBMITTED: [ServiceStatus.APPROVED, ServiceStatus.REJECTED],
    ServiceStatus.APPROVED: [ServiceStatus.ASSIGNED],
    ServiceStatus.ASSIGNED: [ServiceStatus.IN_PROGRESS],
    ServiceStatus.IN_PROGRESS: [ServiceStatus.COMPLETED, ServiceStatus.DISPUTED],
    ServiceStatus.COMPLETED: [ServiceStatus.VERIFIED, ServiceStatus.DISPUTED],
    ServiceStatus.VERIFIED: [ServiceStatus.CLOSED],
    ServiceStatus.DISPUTED: [ServiceStatus.IN_PROGRESS, ServiceStatus.REJECTED],
    ServiceStatus.REJECTED: [],
    ServiceStatus.CLOSED: []
}

def can_transition(current: ServiceStatus, new: ServiceStatus) -> bool:
    """Check if state transition is valid"""
    return new in TRANSITIONS.get(current, [])
```

#### 4.2 Service Request CRUD

```python
## services/service_mgmt/crud/service_request.py
from sqlalchemy.orm import Session
from ..models.service_request import ServiceRequest
from ..schemas.service_request import ServiceRequestCreate
from uuid import uuid4

def create_service_request(
    db: Session,
    service_in: ServiceRequestCreate,
    requester_id: str
) -> ServiceRequest:
    """Create new service request"""
    db_service = ServiceRequest(
        id=uuid4(),
        requester_id=requester_id,
        service_type=service_in.service_type,
        description=service_in.description,
        location=f"POINT({service_in.longitude} {service_in.latitude})",
        urgency=service_in.urgency,
        status="SUBMITTED"
    )
    db.add(db_service)
    db.commit()
    db.refresh(db_service)
    return db_service

def get_service_request(db: Session, service_id: str) -> ServiceRequest:
    """Get service request by ID"""
    return db.query(ServiceRequest).filter(ServiceRequest.id == service_id).first()

def list_service_requests(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: str = None
) -> list[ServiceRequest]:
    """List service requests with filters"""
    query = db.query(ServiceRequest)
    if status:
        query = query.filter(ServiceRequest.status == status)
    return query.offset(skip).limit(limit).all()
```

---

### 5. **Geospatial Implementation**

#### 5.1 PostGIS Spatial Queries

```python
## services/geospatial/core/spatial.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from geoalchemy2.functions import ST_DWithin, ST_Distance, ST_MakePoint

def find_services_near_location(
    db: Session,
    latitude: float,
    longitude: float,
    radius_meters: float = 5000
) -> list:
    """Find service requests within radius of location"""
    point = func.ST_SetSRID(func.ST_MakePoint(longitude, latitude), 4326)
    
    query = db.query(
        ServiceRequest,
        ST_Distance(
            ServiceRequest.location.cast(Geography),
            point.cast(Geography)
        ).label('distance')
    ).filter(
        ST_DWithin(
            ServiceRequest.location.cast(Geography),
            point.cast(Geography),
            radius_meters
        )
    ).order_by('distance')
    
    return query.all()
```

#### 5.2 Map Tile Serving

```python
## services/geospatial/api/v1/tiles.py
from fastapi import APIRouter
from fastapi.responses import Response
from ...core.tile_generator import generate_tile

router = APIRouter()

@router.get("/tiles/{z}/{x}/{y}.png")
async def get_tile(z: int, x: int, y: int):
    """Serve map tile (raster PNG)"""
    tile_bytes = generate_tile(z, x, y)
    return Response(content=tile_bytes, media_type="image/png")
```

---

### 6. **Provider Matching Logic**

#### 6.1 Matching Algorithm

```python
## services/service_mgmt/core/matching.py
from sqlalchemy.orm import Session
from typing import List

def find_matching_providers(
    db: Session,
    service_request: ServiceRequest,
    max_distance_km: float = 50
) -> List[ServiceProvider]:
    """
    Find providers that can fulfill service request.
    
    Criteria:
    1. Offers required service type
    2. Within geographic range
    3. Has available capacity
    4. Is verified and active
    """
    max_distance_meters = max_distance_km * 1000
    
    providers = db.query(ServiceProvider).filter(
        ServiceProvider.service_types.contains([service_request.service_type]),
        ServiceProvider.is_active == True,
        ServiceProvider.is_verified == True,
        ServiceProvider.current_capacity > 0,
        ST_DWithin(
            ServiceProvider.location.cast(Geography),
            service_request.location.cast(Geography),
            max_distance_meters
        )
    ).order_by(
        ST_Distance(
            ServiceProvider.location.cast(Geography),
            service_request.location.cast(Geography)
        )
    ).limit(10).all()
    
    return providers
```

---

### 7. **Data Models & Validation**

#### 7.1 SQLAlchemy Model Example

```python
## services/auth/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(15))
    roles = Column(ARRAY(String), default=["participant"])
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

#### 7.2 Pydantic Schema Example

```python
## services/auth/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., regex=r'^\d{10}$')
    
    @validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Must contain uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Must contain lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Must contain number')
        return v

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    roles: list[str]
    is_verified: bool
    
    class Config:
        orm_mode = True
```

---

### 8. **Error Handling Strategy**

#### 8.1 Standard Error Codes

```python
## services/common/errors.py
class ErrorCodes:
    # Auth (1000-1999)
    AUTH_INVALID_CREDENTIALS = "AUTH_1001"
    AUTH_TOKEN_EXPIRED = "AUTH_1002"
    AUTH_EMAIL_NOT_VERIFIED = "AUTH_1004"
    
    # Users (2000-2999)
    USER_NOT_FOUND = "USER_2001"
    USER_ALREADY_EXISTS = "USER_2002"
    
    # Services (3000-3999)
    SERVICE_NOT_FOUND = "SERVICE_3001"
    SERVICE_INVALID_TRANSITION = "SERVICE_3002"
    
    # System (9000-9999)
    INTERNAL_ERROR = "SYSTEM_9001"
```

#### 8.2 Error Response Format

```python
{
    "error": {
        "code": "AUTH_1001",
        "message": "Invalid credentials",
        "details": {"attempts_remaining": 3}
    }
}
```

---

### 9. **Code Organization**

#### 9.1 Python Style Guidelines

- Follow PEP 8
- Use type hints everywhere
- 4-space indentation
- Max line length: 100 characters
- Google-style docstrings

#### 9.2 Git Commit Convention

```
feat: Add user registration endpoint
fix: Correct JWT expiration validation
docs: Update API documentation
refactor: Simplify state machine
test: Add provider matching tests
```

---

### 10. **Testing & Quality**

#### 10.1 Test Structure

```python
## services/auth/tests/test_auth_api.py
import pytest
from fastapi.testclient import TestClient
from ..main import app

client = TestClient(app)

def test_register_user_success():
    response = client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User",
        "phone": "9876543210"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"

def test_register_duplicate_email():
    # Register once
    client.post("/auth/register", json={...})
    # Try again
    response = client.post("/auth/register", json={...})
    assert response.status_code == 400
```

#### 10.2 Coverage Requirements

- Unit tests: 80%+ coverage
- Integration tests for all API endpoints
- End-to-end tests for critical flows

---

### ✅ **Implementation Summary**

**Provided**:
- ✅ Complete file structure for all services
- ✅ Authentication implementation (bcrypt + JWT)
- ✅ Service request state machine
- ✅ Provider matching algorithm
- ✅ Geospatial query examples
- ✅ Data model patterns (SQLAlchemy + Pydantic)
- ✅ Error handling framework
- ✅ Testing patterns

**Next Steps**:
→ [22-DATABASE-DESIGN.md](22-DATABASE-DESIGN.md) - Complete database schema  
→ [23-API-SPECIFICATION.md](23-API-SPECIFICATION.md) - All API endpoints  
→ [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md) - Local setup guide

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Part of**: IDRM Consolidated Documentation Suite  
**Previous**: [20-FUNCTIONAL-SPECIFICATION.md](20-FUNCTIONAL-SPECIFICATION.md)  
**Next**: [22-DATABASE-DESIGN.md](22-DATABASE-DESIGN.md)
