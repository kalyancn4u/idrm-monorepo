> *Type: Document (specification) · Audience: Developers, integrators · Status: Archived — v2 historical generation*

# IDRM API - JSON Data Formats Reference
<!-- IDRM-CLEANUP doc=v2-41-jsonformats status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-2 request/response JSON schemas. **Canonical schemas = `docs/mvp/40-api-specification.md` + `40-api-openapi.yaml`**
> (frozen `/api/v1`, `{data,pagination}`, error envelope). *Legend:* ✅ covered · ⚠ superseded · ⊘ FFP.
>
> | Snippet | Section | → Addressed in | Phase | Verdict |
> |---|---|---|---|---|
> | `v2-41§types` | Common Data Types · Error Formats | `docs/mvp/40` (envelope, `PICS-STK-API-01`) | MVP | ✅ |
> | `v2-41§auth` | Authentication Formats | `docs/mvp/40` + `22` | MVP | ⚠ |
> | `v2-41§svc` | Service Request Formats | `docs/mvp/40` (incidents) | MVP | ⚠ |
> | `v2-41§uo` | User & Organization Formats | `docs/mvp/40` (USR/RES) | MVP | ⚠ |
> | `v2-41§geo` | Geospatial Formats | `docs/mvp/40` + `50` (SRID 4326) | MVP | ⚠ |
> | `v2-41§ana` | Analytics Formats | basic → RPT; advanced → FFP | MVP/FFP | ⚠ |
>
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Complete Request/Response Schemas

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Purpose**: Reference for all JSON data formats used in API communication

---

## Table of Contents

1. [Common Data Types](#1-common-data-types)
2. [Authentication Formats](#2-authentication-formats)
3. [Service Request Formats](#3-service-request-formats)
4. [User & Organization Formats](#4-user--organization-formats)
5. [Geospatial Formats](#5-geospatial-formats)
6. [Analytics Formats](#6-analytics-formats)
7. [Error Formats](#7-error-formats)

---

## 1. Common Data Types

### 1.1 UUID Format

All IDs are UUID v4 format:

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210"
}
```

**Pattern**: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$`

---

### 1.2 Timestamp Format

All timestamps in ISO 8601 format (UTC):

```json
{
  "created_at": "2026-05-10T10:45:00Z",
  "updated_at": "2026-05-10T11:30:00.123Z"
}
```

**Pattern**: `YYYY-MM-DDTHH:MM:SS(.mmm)?Z`

---

### 1.3 GeoJSON Point Format

All location coordinates use GeoJSON Point:

```json
{
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  }
}
```

**Format**: `[longitude, latitude]` (note order!)

**Constraints**:
- Longitude: -180 to 180
- Latitude: -90 to 90
- For India: longitude 68-97, latitude 6-35

---

### 1.4 Enum Values

**ServiceType**:
```json
["MEDICAL", "FOOD", "SHELTER", "RESCUE", "SANITATION", 
 "COMMUNICATION", "TRANSPORT", "PSYCHOSOCIAL", "LEGAL", "OTHER"]
```

**PriorityLevel**:
```json
["CRITICAL", "HIGH", "MEDIUM", "LOW"]
```

**ServiceStatus**:
```json
["SUBMITTED", "UNDER_REVIEW", "APPROVED", "REJECTED", 
 "ASSIGNED", "IN_PROGRESS", "COMPLETED", "VERIFIED", 
 "CANCELLED", "DISPUTED"]
```

**PrivacyLevel**:
```json
["PUBLIC", "PROTECTED", "PRIVATE"]
```

**UserRole**:
```json
["SYSTEM_ADMIN", "DM_AUTHORITY", "ORG_ADMIN", 
 "EVENT_MANAGER", "SERVICE_PROVIDER", "VOLUNTEER", 
 "CITIZEN", "AUDITOR"]
```

**OrganizationType**:
```json
["NGO", "GOVERNMENT", "INTERNATIONAL_ORG", "PRIVATE"]
```

---

## 2. Authentication Formats

### 2.1 Registration Request

```json
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "9876543210",
  "role": "CITIZEN"
}
```

**Field Constraints**:
- `email`: Valid email format, max 255 chars, unique
- `password`: Min 8 chars, 1 upper, 1 lower, 1 number
- `full_name`: Max 255 chars
- `phone`: Exactly 10 digits (Indian mobile)
- `role`: Must be 'CITIZEN' or 'SERVICE_PROVIDER' (others admin-only)

**Response (201 Created)**:
```json
{
  "status": "success",
  "message": "Verification email sent to john@example.com",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false,
    "created_at": "2026-05-10T10:30:00Z"
  }
}
```

---

### 2.2 Login Request

```json
{
  "email": "john@example.com",
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
      "email": "john@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN",
      "organization_id": null
    },
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJlbWFpbCI6ImpvaG5AZXhhbXBsZS5jb20iLCJyb2xlIjoiQ0lUSVpFTiIsIm9yZ19pZCI6bnVsbCwiZXhwIjoxNzE1MzQ1NDAwLCJpYXQiOjE3MTUzNDQ1MDAsInR5cGUiOiJhY2Nlc3MifQ.signature",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhMWIyYzNkNC1lNWY2LTc4OTAtYWJjZC1lZjEyMzQ1Njc4OTAiLCJleHAiOjE3MTU5NDkzMDAsImlhdCI6MTcxNTM0NDUwMCwidHlwZSI6InJlZnJlc2gifQ.signature",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

**Token Expiry**:
- `access_token`: 15 minutes (900 seconds)
- `refresh_token`: 7 days

---

### 2.3 Token Refresh Request

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "access_token": "new_access_token_here",
    "refresh_token": "new_refresh_token_here",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

---

## 3. Service Request Formats

### 3.1 Create Service Request

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
  "description": "Urgent medical attention needed for elderly person with chest pain. Patient is 75 years old, experiencing severe chest pain and shortness of breath.",
  "privacy_level": "PROTECTED",
  "disaster_event_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"],
    "medical_history": "diabetes, hypertension"
  }
}
```

**Field Constraints**:
- `service_type`: Required, must be valid enum value
- `priority`: Required, must be valid enum value
- `location`: Required, valid GeoJSON Point within India bounds
- `address`: Required, max 500 chars
- `description`: Required, max 1000 chars
- `privacy_level`: Optional, default 'PROTECTED'
- `disaster_event_id`: Optional, must be valid UUID if provided
- `metadata`: Optional, JSON object for additional data

**Response (201 Created)**:
```json
{
  "status": "success",
  "message": "Service request created successfully",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "APPROVED",
    "created_at": "2026-05-10T10:45:00Z",
    "estimated_response_time": "30 minutes",
    "next_action": "Provider is being assigned automatically"
  }
}
```

---

### 3.2 Service Request (Full Object)

```json
{
  "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "requestor_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad, Telangana 500002",
  "description": "Urgent medical attention needed...",
  "privacy_level": "PROTECTED",
  "status": "IN_PROGRESS",
  "assigned_to": {
    "user_id": "p1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "full_name": "Dr. Rajesh Kumar",
    "organization": {
      "org_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "City Hospital",
      "type": "GOVERNMENT"
    },
    "phone": "9999999999",
    "current_location": {
      "type": "Point",
      "coordinates": [78.4900, 17.3900]
    },
    "estimated_arrival": "2026-05-10T11:15:00Z"
  },
  "disaster_event_id": null,
  "estimated_completion": "2026-05-10T12:00:00Z",
  "completed_at": null,
  "verified_at": null,
  "rating": null,
  "proof_photo_url": null,
  "created_at": "2026-05-10T10:45:00Z",
  "updated_at": "2026-05-10T11:00:00Z",
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"]
  }
}
```

---

### 3.3 Service Request List Response

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
        "status": "IN_PROGRESS",
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
          "full_name": "Dr. Rajesh Kumar",
          "organization": "City Hospital"
        }
      },
      {
        "service_id": "e8d7c6b5-a4b3-2109-fedc-ba9876543211",
        "service_type": "FOOD",
        "priority": "HIGH",
        "status": "APPROVED",
        "location": {
          "type": "Point",
          "coordinates": [78.4900, 17.3900]
        },
        "address": "Mehdipatnam, Hyderabad",
        "description": "Food required for 50 families...",
        "distance_meters": 3250.8,
        "created_at": "2026-05-10T10:30:00Z",
        "assigned_to": null
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

---

### 3.4 Update Service Status Request

```json
{
  "status": "IN_PROGRESS",
  "notes": "En route to location. ETA 15 minutes."
}
```

**Valid Status Transitions**:
- `SUBMITTED` → `UNDER_REVIEW`, `APPROVED`
- `UNDER_REVIEW` → `APPROVED`, `REJECTED`
- `APPROVED` → `ASSIGNED`, `REJECTED`
- `ASSIGNED` → `IN_PROGRESS`, `CANCELLED`
- `IN_PROGRESS` → `COMPLETED`, `CANCELLED`
- `COMPLETED` → `VERIFIED`, `DISPUTED`
- `DISPUTED` → `VERIFIED`, `IN_PROGRESS`
- `CANCELLED` → `APPROVED`

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "Service status updated successfully",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "IN_PROGRESS",
    "updated_at": "2026-05-10T11:00:00Z"
  }
}
```

---

### 3.5 Complete Service Request

```json
{
  "completion_notes": "Patient examined and treatment provided. Vitals stable. Prescribed medication and advised rest.",
  "proof_photo_url": "https://storage.idrm.gov.in/proof/2026-05/abc123-proof.jpg"
}
```

**Constraints**:
- `completion_notes`: Required, min 50 chars, max 1000 chars
- `proof_photo_url`: Required for HIGH/CRITICAL priority

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "Service marked as completed. Awaiting verification.",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "COMPLETED",
    "completed_at": "2026-05-10T12:00:00Z",
    "next_action": "Requestor will verify within 24 hours"
  }
}
```

---

### 3.6 Verify Service Request

```json
{
  "verified": true,
  "rating": 5,
  "feedback": "Excellent service. Doctor was very professional and caring. Arrived quickly and provided thorough treatment."
}
```

**Constraints**:
- `verified`: Required boolean
- `rating`: Optional, 1-5 (integer)
- `feedback`: Optional, max 500 chars

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "Service verified successfully",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "VERIFIED",
    "verified_at": "2026-05-10T12:30:00Z",
    "rating": 5
  }
}
```

---

## 4. User & Organization Formats

### 4.1 User Profile Object

```json
{
  "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "9876543210",
  "role": "CITIZEN",
  "organization_id": null,
  "organization": null,
  "is_active": true,
  "is_verified": true,
  "last_login": "2026-05-10T09:00:00Z",
  "created_at": "2026-05-01T10:30:00Z",
  "updated_at": "2026-05-10T09:00:00Z"
}
```

---

### 4.2 Update Profile Request

```json
{
  "full_name": "John Michael Doe",
  "phone": "9876543211"
}
```

**Note**: Email and role cannot be changed via API

**Response (200 OK)**:
```json
{
  "status": "success",
  "message": "Profile updated successfully",
  "data": {
    "user_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "email": "john@example.com",
    "full_name": "John Michael Doe",
    "phone": "9876543211",
    "role": "CITIZEN",
    "updated_at": "2026-05-10T13:00:00Z"
  }
}
```

---

### 4.3 Organization Registration Request

```json
{
  "name": "Red Cross Hyderabad",
  "type": "NGO",
  "registration_number": "FCRA-2020-0001234",
  "address": "Road No 12, Banjara Hills, Hyderabad, Telangana 500034",
  "location": {
    "type": "Point",
    "coordinates": [78.4500, 17.4200]
  },
  "contact_email": "contact@redcross-hyd.org",
  "contact_phone": "04012345678",
  "description": "Humanitarian organization providing emergency relief and disaster response services across Telangana state.",
  "service_types": ["MEDICAL", "FOOD", "SHELTER"],
  "coverage_area": {
    "type": "Polygon",
    "coordinates": [[
      [78.4000, 17.3000],
      [78.5000, 17.3000],
      [78.5000, 17.5000],
      [78.4000, 17.5000],
      [78.4000, 17.3000]
    ]]
  },
  "capacity": 20
}
```

**Field Constraints**:
- `name`: Required, max 255 chars, unique
- `type`: Required, must be valid enum
- `registration_number`: Required, max 100 chars, unique
- `address`: Required
- `location`: Required, GeoJSON Point
- `service_types`: Required, array of ServiceType enums
- `coverage_area`: Required, GeoJSON Polygon
- `capacity`: Required, 1-100

**Response (201 Created)**:
```json
{
  "status": "success",
  "message": "Organization registered. Pending verification.",
  "data": {
    "organization_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "name": "Red Cross Hyderabad",
    "type": "NGO",
    "is_verified": false,
    "created_at": "2026-05-10T14:00:00Z",
    "next_action": "Await verification from authorities"
  }
}
```

---

### 4.4 Organization Object (Full)

```json
{
  "organization_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Red Cross Hyderabad",
  "type": "NGO",
  "registration_number": "FCRA-2020-0001234",
  "address": "Road No 12, Banjara Hills, Hyderabad",
  "location": {
    "type": "Point",
    "coordinates": [78.4500, 17.4200]
  },
  "contact_email": "contact@redcross-hyd.org",
  "contact_phone": "04012345678",
  "description": "Humanitarian organization...",
  "is_verified": true,
  "verified_by": {
    "user_id": "v1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "full_name": "District Collector",
    "role": "DM_AUTHORITY"
  },
  "verified_at": "2026-05-11T10:00:00Z",
  "service_providers": [
    {
      "provider_id": "p1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "user_id": "u1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "full_name": "Dr. Rajesh Kumar",
      "service_types": ["MEDICAL"],
      "is_available": true,
      "rating": 4.8,
      "total_completed": 145
    }
  ],
  "created_at": "2026-05-10T14:00:00Z",
  "updated_at": "2026-05-11T10:00:00Z"
}
```

---

## 5. Geospatial Formats

### 5.1 GeoJSON Feature Collection

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "properties": {
          "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
          "service_type": "MEDICAL",
          "priority": "CRITICAL",
          "status": "IN_PROGRESS",
          "address": "Charminar, Hyderabad",
          "created_at": "2026-05-10T10:45:00Z",
          "requestor_name": "John Doe",
          "assigned_provider": "Dr. Rajesh Kumar"
        }
      },
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [78.4900, 17.3900]
        },
        "properties": {
          "service_id": "e8d7c6b5-a4b3-2109-fedc-ba9876543211",
          "service_type": "FOOD",
          "priority": "HIGH",
          "status": "APPROVED",
          "address": "Mehdipatnam, Hyderabad",
          "created_at": "2026-05-10T10:30:00Z"
        }
      }
    ]
  }
}
```

---

### 5.2 Clustering Response

**Request**:
```json
{
  "service_ids": [
    "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "e8d7c6b5-a4b3-2109-fedc-ba9876543211",
    "d7c6b5a4-b3a2-1098-fedc-ba9876543212"
  ],
  "k": 3
}
```

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "clusters": [
      {
        "cluster_id": 0,
        "center": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "count": 12,
        "service_types": {
          "MEDICAL": 5,
          "FOOD": 4,
          "SHELTER": 3
        },
        "priorities": {
          "CRITICAL": 2,
          "HIGH": 5,
          "MEDIUM": 3,
          "LOW": 2
        },
        "services": [
          "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
          "e8d7c6b5-a4b3-2109-fedc-ba9876543211"
        ]
      },
      {
        "cluster_id": 1,
        "center": {
          "type": "Point",
          "coordinates": [78.5200, 17.4100]
        },
        "count": 8,
        "service_types": {
          "FOOD": 5,
          "SHELTER": 3
        },
        "priorities": {
          "HIGH": 3,
          "MEDIUM": 4,
          "LOW": 1
        },
        "services": [
          "d7c6b5a4-b3a2-1098-fedc-ba9876543212"
        ]
      }
    ]
  }
}
```

---

## 6. Analytics Formats

### 6.1 Dashboard Data

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "total_requests": 1250,
    "by_status": {
      "SUBMITTED": 45,
      "UNDER_REVIEW": 30,
      "APPROVED": 120,
      "IN_PROGRESS": 85,
      "COMPLETED": 850,
      "VERIFIED": 750,
      "REJECTED": 50,
      "CANCELLED": 20
    },
    "by_priority": {
      "CRITICAL": 12,
      "HIGH": 145,
      "MEDIUM": 680,
      "LOW": 413
    },
    "by_service_type": {
      "MEDICAL": 350,
      "FOOD": 450,
      "SHELTER": 250,
      "RESCUE": 80,
      "SANITATION": 70,
      "COMMUNICATION": 30,
      "TRANSPORT": 20
    },
    "avg_response_time_minutes": 42,
    "completion_rate": 0.85,
    "verification_rate": 0.88,
    "top_providers": [
      {
        "provider_id": "p1",
        "organization": "City Hospital",
        "total_completed": 245,
        "rating": 4.8
      },
      {
        "provider_id": "p2",
        "organization": "Red Cross",
        "total_completed": 198,
        "rating": 4.7
      }
    ],
    "critical_pending": {
      "count": 3,
      "services": [
        {
          "service_id": "f9e8d7c6...",
          "service_type": "MEDICAL",
          "location": "Charminar, Hyderabad",
          "age_minutes": 15
        }
      ]
    }
  }
}
```

---

### 6.2 Time-Series Data

**Response (200 OK)**:
```json
{
  "status": "success",
  "data": {
    "time_series": [
      {
        "date": "2026-05-01",
        "total": 45,
        "by_status": {
          "SUBMITTED": 10,
          "APPROVED": 15,
          "IN_PROGRESS": 12,
          "COMPLETED": 8
        }
      },
      {
        "date": "2026-05-02",
        "total": 52,
        "by_status": {
          "SUBMITTED": 12,
          "APPROVED": 18,
          "IN_PROGRESS": 14,
          "COMPLETED": 8
        }
      }
    ],
    "summary": {
      "total_period": 1250,
      "avg_per_day": 41.7,
      "peak_day": "2026-05-05",
      "peak_count": 78
    }
  }
}
```

---

## 7. Error Formats

### 7.1 Standard Error Response

**All Errors Follow This Format**:
```json
{
  "status": "error",
  "message": "Human-readable error message",
  "code": "ERROR_CODE",
  "details": {},
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

---

### 7.2 Validation Error (400)

```json
{
  "status": "error",
  "message": "Validation failed",
  "code": "VALIDATION_ERROR",
  "details": {
    "errors": [
      {
        "field": "email",
        "message": "Email already registered",
        "value": "john@example.com"
      },
      {
        "field": "password",
        "message": "Password must contain at least one uppercase letter",
        "value": null
      }
    ]
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

---

### 7.3 Unauthorized Error (401)

```json
{
  "status": "error",
  "message": "Authentication required",
  "code": "UNAUTHORIZED",
  "details": {
    "reason": "No token provided"
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

**OR**:
```json
{
  "status": "error",
  "message": "Invalid or expired token",
  "code": "UNAUTHORIZED",
  "details": {
    "reason": "Token expired",
    "expired_at": "2026-05-10T11:45:00Z"
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

---

### 7.4 Forbidden Error (403)

```json
{
  "status": "error",
  "message": "You do not have permission to perform this action",
  "code": "FORBIDDEN",
  "details": {
    "required_role": "DM_AUTHORITY",
    "your_role": "CITIZEN",
    "action": "approve_service_request"
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

---

### 7.5 Not Found Error (404)

```json
{
  "status": "error",
  "message": "Service request not found",
  "code": "NOT_FOUND",
  "details": {
    "resource_type": "service_request",
    "resource_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210"
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

---

### 7.6 Rate Limit Error (429)

```json
{
  "status": "error",
  "message": "Too many requests. Please try again later.",
  "code": "RATE_LIMIT_EXCEEDED",
  "details": {
    "limit": "100 requests per minute",
    "reset_at": "2026-05-10T12:01:00Z",
    "retry_after": 45
  },
  "timestamp": "2026-05-10T12:00:15Z",
  "request_id": "req_abc123"
}
```

---

### 7.7 Server Error (500)

```json
{
  "status": "error",
  "message": "An internal server error occurred",
  "code": "INTERNAL_SERVER_ERROR",
  "details": {
    "error_id": "err_xyz789",
    "message": "The engineering team has been notified"
  },
  "timestamp": "2026-05-10T12:00:00Z",
  "request_id": "req_abc123"
}
```

---

## Appendix: Quick Reference Tables

### HTTP Status Codes

| Code | Name | When Used |
|------|------|-----------|
| 200 | OK | Success (GET, PUT, DELETE) |
| 201 | Created | Success (POST - resource created) |
| 204 | No Content | Success (no response body) |
| 400 | Bad Request | Validation error |
| 401 | Unauthorized | Authentication required/failed |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflict (duplicate) |
| 422 | Unprocessable Entity | Semantic error |
| 429 | Too Many Requests | Rate limited |
| 500 | Server Error | Internal error |
| 503 | Service Unavailable | Temporary outage |

---

### Response Envelope

All successful responses wrapped in:
```json
{
  "status": "success",
  "data": { /* actual data here */ }
}
```

All error responses wrapped in:
```json
{
  "status": "error",
  "message": "...",
  "code": "...",
  "details": {}
}
```

---

**END OF JSON DATA FORMATS REFERENCE**

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**See Also**: 
- instructions_api_v2.md (API Integration Guide)
- IDRM-LLD-v2.md (Low-Level Design with API specs)
