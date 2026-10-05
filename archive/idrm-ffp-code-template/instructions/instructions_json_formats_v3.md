# IDRM v3 — JSON Formats & Data Structures
## Complete Reference: Every Request and Response Body

**Source**: backup/40-DATA-FORMATS.md  
**Version**: 3.0  
**Audience**: Frontend developers, backend developers, anyone reading or writing API calls  
**Last Updated**: May 30, 2026

> **How to use this file**: Every API call in IDRM sends and receives JSON. This document shows you the exact shape of each one — what fields go in, what comes back, what each field means, and what values are allowed.

---

## Part 1 — JSON Fundamentals (Quick Reference)

### 1.1 The Six Building Blocks

```json
{
  "text_value":     "any text in quotes",
  "number_value":   42,
  "decimal_value":  3.14,
  "boolean_value":  true,
  "null_value":     null,
  "array_value":    ["item1", "item2"],
  "object_value":   { "nested_key": "nested_value" }
}
```

### 1.2 Field Types Used Across IDRM

| Type | Example | Notes |
|------|---------|-------|
| UUID | `"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` | 8-4-4-4-12 hex pattern. All IDs use this. |
| Timestamp | `"2026-05-16T10:45:00Z"` | ISO 8601, always UTC (Z suffix) |
| GeoJSON Point | `{"type":"Point","coordinates":[lon,lat]}` | **Longitude first**, then latitude |
| Enum string | `"MEDICAL"` | Must match exactly — see allowed values below |
| Pagination | `{"page":1,"limit":20,"total":45}` | All list endpoints return this |

### 1.3 GeoJSON Warning ⚠️

```
WRONG: [latitude, longitude]  →  [17.3850, 78.4867]
RIGHT: [longitude, latitude]  →  [78.4867, 17.3850]
```
GeoJSON standard puts longitude first. This is a common source of map pin errors.

---

## Part 2 — Enumeration Values (Allowed Strings)

### 2.1 ServiceType

```json
"RESCUE"         // Search and rescue operations
"MEDICAL"        // Doctors, ambulances, medicine
"FOOD"           // Meals, water, groceries
"SHELTER"        // Temporary housing, tents
"WATER"          // Clean water supply
"SANITATION"     // Toilets, cleaning, hygiene
"COMMUNICATION"  // Phones, internet, connectivity
"TRANSPORT"      // Vehicles, fuel, logistics
"PSYCHOSOCIAL"   // Counseling, mental health support
"LEGAL"          // Legal aid, documentation
"OTHER"          // Anything else
```

### 2.2 PriorityLevel

```json
"CRITICAL"   // 🔴 Life-threatening — respond immediately
"HIGH"       // 🟠 Urgent — respond within hours
"MEDIUM"     // 🟡 Important — respond within a day
"LOW"        // 🟢 Can wait — respond when resources available
```

### 2.3 ServiceStatus (lifecycle order)

```json
"SUBMITTED"     // Just created, awaiting review"APPROVED"      // Approved, searching for provider
"REJECTED"      // Cannot be fulfilled
"ACCEPTED"      // Provider accepted, not yet started
"IN_PROGRESS"   // Provider en route / actively working
"COMPLETED"     // Service delivered
"VERIFIED"      // Citizen confirmed completion
"CANCELLED"     // Request cancelled before completion
"DISPUTED"      // Problem reported post-completion
"EXPIRED"       // No action taken within 48h
```

State machine: `SUBMITTED → APPROVED → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED` (+ `REJECTED`, `CANCELLED`, `EXPIRED`, `DISPUTED`)

### 2.4 UserRole

```json
"CITIZEN"          // Regular user — creates service requests
"VOLUNTEER"        // Helps coordinate, not a formal provider
"SERVICE_PROVIDER" // Delivers services (attached to an org)
"EVENT_MANAGER"    // Manages a specific disaster event
"DM_AUTHORITY"     // District Magistrate / Government official
"ORG_ADMIN"        // Organization administrator
"SYSTEM_ADMIN"     // Full system access
"AUDITOR"          // Read-only access for compliance
```

### 2.5 PrivacyLevel

```json
"PUBLIC"     // Visible to all logged-in users
"PROTECTED"  // Visible only to authorized responders and admins
"PRIVATE"    // Visible only to the requestor and assigned provider
```

### 2.6 NotificationChannel

```json
"EMAIL"      // Sent via SMTP to user's email
"SMS"        // Sent via SMS gateway (India)
"PUSH"       // Mobile push notification (React Native)
"IN_APP"     // Shown inside the app (all platforms)
"WEBSOCKET"  // Real-time via ws://localhost:3001
```

---

## Part 3 — Authentication JSON

### 3.1 Register — `POST /api/v1/auth/register`

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "role": "CITIZEN"
}
```

**Field rules**:

| Field | Required | Constraints |
|-------|----------|------------|
| `email` | ✅ | Valid email, max 255 chars, unique in system |
| `password` | ✅ | Min 8 chars, ≥1 uppercase, ≥1 lowercase, ≥1 digit |
| `full_name` | ✅ | Letters, spaces, hyphens only, max 255 chars |
| `phone` | ❌ | E.164 format: `+91xxxxxxxxxx` (unique if provided) |
| `role` | ❌ | Default: `CITIZEN`. Only `CITIZEN` and `VOLUNTEER` on self-registration |

**Response** `201 Created`:
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
    "created_at": "2026-05-16T10:30:00Z"
  }
}
```

---

### 3.2 Login — `POST /api/v1/auth/login`

**Request**:
```json
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response** `200 OK`:
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
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

Token rules:
- `access_token`: valid for **15 minutes** (900 seconds). Send in every request: `Authorization: Bearer <token>`
- `refresh_token`: valid for **7 days**. Use it to get a new access token without re-logging in.

---

### 3.3 Token Refresh — `POST /api/v1/auth/refresh`

**Request**:
```json
{ "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Response** `200 OK`:
```json
{
  "status": "success",
  "data": {
    "access_token": "new_access_token...",
    "refresh_token": "new_refresh_token...",
    "expires_in": 900,
    "token_type": "Bearer"
  }
}
```

---

### 3.4 Logout — `POST /api/v1/auth/logout`

**Request**: No body — just the `Authorization: Bearer <token>` header.

**Response** `204 No Content` (empty body on success).

Effect: both the access token JTI and the session are blacklisted in Redis immediately.

---

## Part 4 — Service Request JSON

### 4.1 Create Request — `POST /api/v1/services/requests`

**Request**:
```json
{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "description": "Elderly person with chest pain, 75 years old, needs immediate medical attention.",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad, Telangana 500002",
  "privacy_level": "PROTECTED",
  "contact_phone": "+919876543210",
  "num_people_affected": 1,
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"]
  }
}
```

**Response** `201 Created`:
```json
{
  "status": "success",
  "data": {
    "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
    "status": "SUBMITTED",
    "created_at": "2026-05-16T10:45:00Z",
    "estimated_response_time": "30 minutes",
    "next_action": "Request will be reviewed by coordinator"
  }
}
```

---

### 4.2 Full Service Request Object (from `GET /api/v1/services/requests/{id}`)

```json
{
  "service_id": "f9e8d7c6-b5a4-3210-fedc-ba9876543210",
  "requestor_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "status": "IN_PROGRESS",
  "description": "Elderly person with chest pain...",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "Charminar, Hyderabad",
  "privacy_level": "PROTECTED",
  "num_people_affected": 1,
  "contact_phone": "+919876543210",
  "assigned_to": {
    "user_id": "p1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "full_name": "Dr. Rajesh Kumar",
    "phone": "+919999999999",
    "organization": {
      "org_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "name": "City Hospital",
      "type": "HOSPITAL"
    },
    "current_location": {
      "type": "Point",
      "coordinates": [78.4900, 17.3900]
    },
    "estimated_arrival": "2026-05-16T11:15:00Z"
  },
  "accepted_at": "2026-05-16T11:00:00Z",
  "completed_at": null,
  "verified_at": null,
  "rating": null,
  "feedback": null,
  "created_at": "2026-05-16T10:45:00Z",
  "updated_at": "2026-05-16T11:00:00Z"
}
```

---

### 4.3 List Requests — `GET /api/v1/services/requests`

**Query parameters**:

| Param | Type | Example | Default |
|-------|------|---------|---------|
| `status` | enum | `?status=APPROVED` | all |
| `service_type` | enum | `?service_type=MEDICAL` | all |
| `priority` | enum | `?priority=CRITICAL` | all |
| `page` | integer | `?page=2` | 1 |
| `per_page` | integer | `?per_page=50` | 20 (max 100) |

**Response** `200 OK`:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "service_id": "f9e8d7c6-...",
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "status": "APPROVED",
        "address": "Charminar, Hyderabad",
        "created_at": "2026-05-16T10:45:00Z"
      }
    ],
    "pagination": {
      "total": 45,
      "page": 1,
      "per_page": 20,
      "pages": 3
    }
  }
}
```

---

### 4.4 Update Status — `PUT /api/v1/services/requests/{id}/status`

**Request**:
```json
{
  "status": "IN_PROGRESS",
  "notes": "Provider dispatched — ETA 20 minutes"
}
```

**Response** `200 OK`:
```json
{
  "id": "f9e8d7c6-...",
  "status": "IN_PROGRESS",
  "updated_at": "2026-05-16T11:05:00Z"
}
```

---

## Part 5 — User & Organization JSON

### 5.1 User Profile — `GET /api/v1/users/me`

**Response** `200 OK`:
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "email": "john@example.com",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "role": "CITIZEN",
  "language_preference": "en",
  "is_active": true,
  "is_verified": true,
  "organization_id": null,
  "created_at": "2026-05-01T10:30:00Z",
  "last_login": "2026-05-16T09:00:00Z"
}
```

---

### 5.2 Update Profile — `PUT /api/v1/users/me`

**Request**:
```json
{
  "full_name": "John A. Doe",
  "phone": "+919876543211",
  "language_preference": "hi"
}
```

Language options: `"en"` (English), `"hi"` (Hindi), `"te"` (Telugu)

---

### 5.3 Organization Object

```json
{
  "org_id": "o1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "Red Cross Hyderabad",
  "org_type": "NGO",
  "registration_number": "FCRA-2020-0001234",
  "service_types": ["MEDICAL", "FOOD", "SHELTER"],
  "contact_person": "Priya Sharma",
  "contact_phone": "+914012345678",
  "contact_email": "contact@redcross-hyd.org",
  "is_verified": true,
  "verified_at": "2026-04-01T09:00:00Z",
  "created_at": "2026-03-15T10:30:00Z"
}
```

`org_type` values: `"NGO"`, `"HOSPITAL"`, `"GOVT_AGENCY"`, `"VOLUNTEER_GROUP"`

---

## Part 6 — Geospatial JSON

### 6.1 Nearby Search — `GET /api/v1/geo/nearby`

**Query parameters**:

| Param | Required | Example |
|-------|----------|---------|
| `latitude` | ✅ | `13.0827` |
| `longitude` | ✅ | `80.2707` |
| `radius` | ❌ | `10` (km, default 5, max 50) |
| `service_type` | ❌ | `MEDICAL` |

**Response** `200 OK`:
```json
{
  "center": { "latitude": 13.0827, "longitude": 80.2707 },
  "radius_km": 10,
  "total": 3,
  "results": [
    {
      "service_id": "f9e8d7c6-...",
      "service_type": "MEDICAL",
      "priority": "CRITICAL",
      "distance_km": 1.2,
      "location": { "type": "Point", "coordinates": [80.2750, 13.0850] },
      "address": "Anna Nagar, Chennai"
    }
  ]
}
```

---

### 6.2 Cluster — `GET /api/v1/geo/cluster`

**Query parameters**: `zoom` (1–20, required), `bounds` (optional: `south,west,north,east`)

**Response** `200 OK`:
```json
{
  "clusters": [
    {
      "latitude": 13.05,
      "longitude": 80.25,
      "count": 15,
      "priority_breakdown": {
        "CRITICAL": 3,
        "HIGH": 7,
        "MEDIUM": 5,
        "LOW": 0
      }
    }
  ]
}
```

---

## Part 7 — Notifications JSON

### 7.1 List Notifications — `GET /api/v1/notifications`

**Response** `200 OK`:
```json
{
  "items": [
    {
      "id": "n1b2c3d4-...",
      "type": "request_assigned",
      "title": "Provider Assigned",
      "message": "Dr. Rajesh Kumar has been assigned to your medical request.",
      "read": false,
      "related_service_id": "f9e8d7c6-...",
      "created_at": "2026-05-16T11:00:00Z"
    }
  ],
  "unread_count": 2
}
```

`type` values: `"request_created"`, `"request_assigned"`, `"request_updated"`, `"request_completed"`, `"system_alert"`

---

## Part 8 — Analytics JSON

### 8.1 Dashboard — `GET /api/v1/analytics/dashboard`

**Response** `200 OK`:
```json
{
  "total_requests": 1250,
  "pending_requests": 45,
  "active_providers": 120,
  "requests_by_type": {
    "MEDICAL": 450,
    "FOOD": 380,
    "WATER": 220,
    "SHELTER": 200
  },
  "requests_by_status": {
    "SUBMITTED": 10,
    "APPROVED": 20,
    "ACCEPTED": 15,
    "IN_PROGRESS": 30,
    "COMPLETED": 1150,
    "CANCELLED": 25
  },
  "requests_by_priority": {
    "CRITICAL": 85,
    "HIGH": 320,
    "MEDIUM": 560,
    "LOW": 285
  },
  "avg_response_time_minutes": 28,
  "generated_at": "2026-05-16T12:00:00Z"
}
```

---

## Part 9 — Error Response Format

**All errors use this structure**:

```json
{
  "status": "error",
  "detail": "Human-readable error message",
  "code": "ERROR_CODE",
  "field": "field_name_if_validation_error",
  "errors": [
    {
      "field": "email",
      "message": "Email is already registered"
    }
  ]
}
```

**HTTP status codes**:

| Code | Meaning | When |
|------|---------|------|
| `400` | Bad Request | Invalid JSON, missing required field, failed validation |
| `401` | Unauthorized | No token, expired token, invalid token |
| `403` | Forbidden | Valid token but not allowed (wrong role) |
| `404` | Not Found | The resource ID doesn't exist |
| `409` | Conflict | Duplicate (e.g., email already registered) |
| `422` | Unprocessable | Malformed request body that passed JSON parsing |
| `429` | Rate Limited | Too many requests — see `Retry-After` header |
| `500` | Server Error | Something broke internally |

---

## Part 10 — WebSocket Events

**Connect**: `ws://localhost:3001` (dev) or `wss://api.idrm.gov.in/ws` (prod)

**Subscribe message** (send after connecting):
```json
{ "type": "subscribe", "channel": "service_requests" }
```

**Events received**:

```json
// New request created
{ "type": "request_created", "request": { "service_id": "...", "service_type": "MEDICAL", ... } }

// Request status changed
{ "type": "request_updated", "request": { "service_id": "...", "status": "ACCEPTED", ... } }

// Request removed
{ "type": "request_deleted", "request": { "id": "..." } }
```

---

## Quick Reference — Request Headers

```http
# Authenticated request
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json
Accept-Language: en
X-Request-ID: a1b2c3d4-uuid-for-tracing

# Public request (no auth needed)
Content-Type: application/json
```
