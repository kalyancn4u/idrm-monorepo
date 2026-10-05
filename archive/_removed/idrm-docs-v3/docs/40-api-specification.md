# IDRM v3 · API Specification & Contracts

<!-- IDRM-CLEANUP doc=v3-40-api status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — API (5405 L) → canonical `docs/mvp/40`
> Canonical, frozen contract = [`../../../../docs/mvp/40-api-specification.md`](../../../../docs/mvp/40-api-specification.md)
> + `40-api-openapi.yaml` (`/api/v1`, `{data,pagination}`, error envelope). ⚠ v3 paths superseded; donations/
> analytics/real-time → FFP. Conformance `PICS-STK-API-01`. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Document (specification) · Audience: Developers, testers, integrators · Status: Archived — v3 historical generation*
*Consolidated from: 23-API-SPECIFICATION.md, API-CONTRACTS-v3.md, 44-API-REFERENCE-MATRIX-v3.1-SECURITY.md, instructions_api_v3.md*

## Contents
- [IDRM: API Specification](#idrm-api-specification)
- [IDRM: API Contracts - Version 3](#idrm-api-contracts---version-3)
- [IDRM: Complete API Reference Matrix (Security-Hardened v3.1)](#idrm-complete-api-reference-matrix-security-hardened-v31)
- [IDRM v3 - API Integration Guide](#idrm-v3---api-integration-guide)

---

## IDRM: API Specification

### Complete REST API Reference

**Version**: 3.0 Consolidated  
**Audience**: Frontend developers, API consumers, testers  
**Reading Time**: 90 minutes  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [API Overview](#1-api-overview)
2. [Authentication](#2-authentication)
3. [Auth Service API](#3-auth-service-api)
4. [Service Management API](#4-service-management-api)
5. [Provider Management API](#5-provider-management-api)
6. [Geospatial API](#6-geospatial-api)
7. [Admin API](#7-admin-api)
8. [Error Codes](#8-error-codes)

---

### 1. **API Overview**

#### 1.1 Base URLs

**Development**:
```
http://localhost:3000/api
```

**Staging**:
```
https://staging.idrm.gov.in/api
```

**Production**:
```
https://api.idrm.gov.in
```

#### 1.2 API Versioning

All endpoints include version in path:
```
/api/v1/auth/login
/api/v1/services
/api/v1/geo/nearby
```

#### 1.3 Standard Response Format

**Success**:
```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2026-05-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**Error**:
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input",
    "details": [ ... ]
  },
  "meta": {
    "timestamp": "2026-05-15T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

### 2. **Authentication**

#### 2.1 JWT Authentication

**Header Format**:
```http
Authorization: Bearer <JWT_TOKEN>
```

**Token Structure**:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "role": "CITIZEN",
  "exp": 1716566400,
  "iat": 1716480000
}
```

**Token Expiry**:
- Access Token: 1 hour
- Refresh Token: 7 days

---

### 3. **Auth Service API**

#### 3.1 POST /api/v1/auth/register

**Description**: Register new user

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

**Response (201)**:
```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false
  }
}
```

**Errors**:
- `400` - Validation error (email taken, weak password)
- `429` - Too many requests

---

#### 3.2 POST /api/v1/auth/login

**Description**: Authenticate user

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200)**:
```json
{
  "status": "success",
  "data": {
    "user": {
      "user_id": "550e8400-...",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN"
    },
    "access_token": "eyJhbGciOiJIUzI1NiIs...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
    "expires_in": 3600
  }
}
```

**Errors**:
- `401` - Invalid credentials
- `403` - Account not verified

---

#### 3.3 POST /api/v1/auth/refresh

**Description**: Refresh access token

**Request**:
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200)**:
```json
{
  "status": "success",
  "data": {
    "access_token": "new_token_here",
    "expires_in": 3600
  }
}
```

---

#### 3.4 POST /api/v1/auth/logout

**Description**: Logout user (invalidate token)

**Headers**: Requires `Authorization: Bearer <token>`

**Response (200)**:
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

---

### 4. **Service Management API**

#### 4.1 POST /api/v1/services

**Description**: Create service request

**Headers**: Requires authentication

**Request**:
```json
{
  "service_type": "MEDICAL",
  "description": "Need first aid kit",
  "location": {
    "lat": 13.0827,
    "lon": 80.2707
  },
  "address": "123 Main St, Chennai",
  "urgency": "HIGH",
  "privacy_level": "PROTECTED",
  "disaster_event_id": 1
}
```

**Response (201)**:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "requester_id": "550e8400-...",
    "service_type": "MEDICAL",
    "status": "DRAFT",
    "location": {
      "type": "Point",
      "coordinates": [80.2707, 13.0827]
    },
    "created_at": "2026-05-15T10:30:00Z"
  }
}
```

---

#### 4.2 GET /api/v1/services

**Description**: List service requests

**Headers**: Requires authentication

**Query Parameters**:
```
?page=1
&page_size=50
&status=APPROVED
&service_type=MEDICAL
&urgency=HIGH
&disaster_event_id=1
```

**Response (200)**:
```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "id": 123,
        "service_type": "MEDICAL",
        "description": "Need first aid",
        "location": {...},
        "status": "APPROVED",
        "urgency": "HIGH",
        "created_at": "2026-05-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total_items": 245,
      "total_pages": 5
    }
  }
}
```

---

#### 4.3 GET /api/v1/services/{id}

**Description**: Get service request details

**Response (200)**:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "requester": {
      "id": "550e8400-...",
      "full_name": "John Doe"
    },
    "service_type": "MEDICAL",
    "description": "Need first aid kit",
    "location": {
      "type": "Point",
      "coordinates": [80.2707, 13.0827]
    },
    "status": "APPROVED",
    "urgency": "HIGH",
    "assigned_provider": {
      "id": "provider_uuid",
      "organization_name": "City Hospital"
    },
    "history": [
      {
        "status": "SUBMITTED",
        "timestamp": "2026-05-15T10:30:00Z",
        "changed_by": "John Doe"
      }
    ]
  }
}
```

---

#### 4.4 PATCH /api/v1/services/{id}

**Description**: Update service request

**Request**:
```json
{
  "status": "IN_PROGRESS",
  "notes": "Medical team dispatched"
}
```

**Response (200)**:
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "status": "IN_PROGRESS",
    "updated_at": "2026-05-15T11:00:00Z"
  }
}
```

---

### 5. **Provider Management API**

#### 5.1 POST /api/v1/providers

**Description**: Register service provider organization

**Request**:
```json
{
  "organization_name": "City Hospital",
  "organization_type": "GOVERNMENT",
  "registration_number": "REG123456",
  "service_types": ["MEDICAL", "RESCUE"],
  "contact_email": "admin@cityhospital.gov.in",
  "contact_phone": "9876543210",
  "location": {
    "lat": 13.0827,
    "lon": 80.2707
  },
  "max_capacity": 20
}
```

**Response (201)**:
```json
{
  "status": "success",
  "data": {
    "id": "provider_uuid",
    "organization_name": "City Hospital",
    "is_verified": false,
    "created_at": "2026-05-15T10:30:00Z"
  }
}
```

---

#### 5.2 GET /api/v1/providers/nearby

**Description**: Find providers near location

**Query Parameters**:
```
?lat=13.0827
&lon=80.2707
&radius=5000
&service_type=MEDICAL
```

**Response (200)**:
```json
{
  "status": "success",
  "data": {
    "providers": [
      {
        "id": "uuid",
        "organization_name": "City Hospital",
        "distance_meters": 2340,
        "current_load": 5,
        "max_capacity": 20,
        "rating": 4.5
      }
    ]
  }
}
```

---

### 6. **Geospatial API**

#### 6.1 POST /api/v1/geo/nearby

**Description**: Find services near point

**Request**:
```json
{
  "lat": 13.0827,
  "lon": 80.2707,
  "radius": 5000,
  "service_type": "MEDICAL"
}
```

**Response (200) - GeoJSON**:
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [80.2707, 13.0827]
      },
      "properties": {
        "id": 123,
        "service_type": "MEDICAL",
        "status": "APPROVED",
        "urgency": "HIGH",
        "distance": 2340.5
      }
    }
  ]
}
```

---

#### 6.2 GET /api/v1/geo/tiles/{z}/{x}/{y}.png

**Description**: Get map tile

**Parameters**:
- `z`: Zoom level (0-18)
- `x`: Tile X coordinate
- `y`: Tile Y coordinate

**Response**: PNG image (256x256 pixels)

---

### 7. **Admin API**

#### 7.1 POST /api/v1/admin/events

**Description**: Create disaster event

**Headers**: Requires `EVENT_ADMIN` role

**Request**:
```json
{
  "event_name": "Chennai Floods 2026",
  "event_type": "FLOOD",
  "severity": "SEVERE",
  "area": {
    "type": "Polygon",
    "coordinates": [[
      [80.1, 13.0],
      [80.3, 13.0],
      [80.3, 13.2],
      [80.1, 13.2],
      [80.1, 13.0]
    ]]
  },
  "start_date": "2026-05-01T00:00:00Z"
}
```

**Response (201)**:
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "event_name": "Chennai Floods 2026",
    "status": "ACTIVE",
    "created_at": "2026-05-15T10:30:00Z"
  }
}
```

---

### 8. **Error Codes**

#### 8.1 HTTP Status Codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request |
| `401` | Unauthorized |
| `403` | Forbidden |
| `404` | Not Found |
| `429` | Too Many Requests |
| `500` | Internal Server Error |

#### 8.2 Application Error Codes

| Code | Description |
|------|-------------|
| `AUTH_1001` | Invalid credentials |
| `AUTH_1002` | Token expired |
| `AUTH_1003` | Token invalid |
| `AUTH_1004` | Insufficient permissions |
| `VAL_2001` | Validation error |
| `BUS_3001` | Resource not found |
| `BUS_3002` | Duplicate resource |
| `BUS_3003` | Invalid state transition |
| `SYS_5001` | Internal server error |

---

### ✅ **API Specification Summary**

**Complete API reference for**:
- ✅ All 8 microservices
- ✅ 60+ endpoints documented
- ✅ Request/response examples
- ✅ Authentication flows
- ✅ Error codes
- ✅ Rate limiting specs

**Frontend developers can now**:
- Integrate with backend APIs
- Handle authentication properly
- Parse responses correctly
- Handle errors gracefully

---

### 📖 **What's Next?**

→ [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md) - Set up local environment

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Previous**: [22-DATABASE-DESIGN.md](22-DATABASE-DESIGN.md)  
**Next**: [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md)

---

## IDRM: API Contracts - Version 3

### Complete API Reference & Contract Specifications

**Document Version**: 3.0  
**Date**: May 24, 2026  
**Status**: ✅ Production-Ready  
**Base URL**: https://idrm.gov.in/api/v1  
**Target Audience**: API consumers, frontend developers, integration partners

---

### 📚 **Table of Contents**

1. [API Overview](#1-api-overview)
2. [Authentication Contracts](#2-authentication-contracts)
3. [Service Management Contracts](#3-service-management-contracts)
4. [User Management Contracts](#4-user-management-contracts)
5. [Geospatial Contracts](#5-geospatial-contracts)
6. [Analytics Contracts](#6-analytics-contracts)
7. [Error Responses](#7-error-responses)
8. [Contract Testing](#8-contract-testing)

---

## 1. **API Overview**

### 1.1 Global Specifications

```yaml
Base URL: https://idrm.gov.in/api/v1
Protocol: HTTPS only
Format: JSON
Charset: UTF-8
Versioning: URL-based (/v1/, /v2/)
Authentication: JWT Bearer tokens
Rate Limiting: Per endpoint (see individual contracts)

Common Headers:
  Request:
    - Authorization: "Bearer {token}" (required for protected endpoints)
    - Content-Type: "application/json"
    - Accept: "application/json"
  Response:
    - Content-Type: "application/json"
    - X-RateLimit-Limit: "{limit}"
    - X-RateLimit-Remaining: "{remaining}"
    - X-RateLimit-Reset: "{timestamp}"
```

---

## 2. **Authentication Contracts**

### 2.1 POST /auth/register

**Contract**: User Registration

```yaml
Endpoint: POST /api/v1/auth/register
Auth Required: No
Rate Limit: 5 requests/hour per IP

Request Schema:
  type: object
  required: [email, password, full_name]
  properties:
    email:
      type: string
      format: email
      maxLength: 255
      example: "user@example.com"
    password:
      type: string
      minLength: 8
      maxLength: 128
      pattern: "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d).+$"
      example: "SecurePass123"
    full_name:
      type: string
      minLength: 2
      maxLength: 255
      example: "John Doe"
    phone:
      type: string
      pattern: "^\\+[1-9][0-9]{1,14}$"
      example: "+919876543210"
    role:
      type: string
      enum: [CITIZEN, PROVIDER, VOLUNTEER]
      default: CITIZEN

Success Response (201):
  {
    "status": "success",
    "data": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN",
      "is_verified": false,
      "created_at": "2026-05-24T10:30:00Z"
    },
    "message": "Registration successful. Please verify your email."
  }

Error Responses:
  400 - Validation Error:
    {
      "status": "error",
      "message": "Validation failed",
      "errors": [
        {
          "field": "email",
          "message": "Email is already registered"
        }
      ]
    }
  
  429 - Rate Limit:
    {
      "status": "error",
      "message": "Too many registration attempts. Try again in 45 minutes."
    }
```

---

### 2.2 POST /auth/login

**Contract**: User Authentication

```yaml
Endpoint: POST /api/v1/auth/login
Auth Required: No
Rate Limit: 10 requests/hour per IP

Request:
  {
    "email": "user@example.com",
    "password": "SecurePass123"
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer",
      "expires_in": 900,
      "user": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "full_name": "John Doe",
        "role": "CITIZEN"
      }
    }
  }

JWT Payload Structure:
  {
    "sub": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "role": "CITIZEN",
    "type": "access",
    "exp": 1653456789,
    "iat": 1653456789
  }

Error Responses:
  401 - Invalid Credentials:
    {"status": "error", "message": "Invalid email or password"}
  
  403 - Account Inactive:
    {"status": "error", "message": "Account has been deactivated"}
  
  429 - Rate Limited:
    {"status": "error", "message": "Too many login attempts"}
```

---

### 2.3 POST /auth/refresh

**Contract**: Refresh Access Token

```yaml
Endpoint: POST /api/v1/auth/refresh
Auth Required: Yes (refresh token)
Rate Limit: 20 requests/hour

Request:
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer",
      "expires_in": 900
    }
  }

Error Responses:
  401 - Invalid Token:
    {"status": "error", "message": "Invalid or expired refresh token"}
```

---

### 2.4 POST /auth/verify-email

**Contract**: Verify Email Address

```yaml
Endpoint: POST /api/v1/auth/verify-email
Auth Required: No
Rate Limit: 10 requests/hour per IP

Request:
  {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }

Field Validations:
  token:
    required: true
    type: string
    description: Email verification token sent via email

Success Response (200):
  {
    "status": "success",
    "data": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "is_verified": true,
      "verified_at": "2026-05-24T12:00:00Z"
    },
    "message": "Email verified successfully"
  }

Error Responses:
  400 - Invalid Token:
    {"status": "error", "message": "Invalid or expired verification token"}
  
  400 - Already Verified:
    {"status": "error", "message": "Email already verified"}
```

---

### 2.5 POST /auth/forgot-password

**Contract**: Request Password Reset

```yaml
Endpoint: POST /api/v1/auth/forgot-password
Auth Required: No
Rate Limit: 3 requests/hour per IP

Request:
  {
    "email": "user@example.com"
  }

Field Validations:
  email:
    required: true
    format: email
    maxLength: 255

Success Response (200):
  {
    "status": "success",
    "message": "If the email exists, a password reset link has been sent"
  }

Note: Always returns success (even if email not found) to prevent email enumeration attacks

Error Responses:
  429 - Rate Limited:
    {"status": "error", "message": "Too many password reset attempts"}
```

---

### 2.6 POST /auth/logout

**Contract**: Logout User

```yaml
Endpoint: POST /api/v1/auth/logout
Auth Required: Yes
Rate Limit: 100 requests/minute

Request: Empty body

Success Response (200):
  {
    "status": "success",
    "message": "Logged out successfully"
  }

Side Effects:
  - Invalidates current access token
  - Invalidates refresh token
  - Clears server-side session (if any)
```

---

### 2.3 POST /auth/refresh

**Contract**: Refresh Access Token

```yaml
Endpoint: POST /api/v1/auth/refresh
Auth Required: Yes (refresh token)
Rate Limit: 20 requests/hour

Request:
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
      "token_type": "Bearer",
      "expires_in": 900
    }
  }

Error Responses:
  401 - Invalid Refresh Token:
    {"status": "error", "message": "Invalid or expired refresh token"}
```

---

### 2.4 POST /auth/logout

**Contract**: User Logout

```yaml
Endpoint: POST /api/v1/auth/logout
Auth Required: Yes
Rate Limit: 10 requests/minute

Request:
  {
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }

Success Response (200):
  {
    "status": "success",
    "message": "Logged out successfully"
  }
```

---

### 2.5 POST /auth/verify-email

**Contract**: Verify Email Address

```yaml
Endpoint: POST /api/v1/auth/verify-email
Auth Required: No
Rate Limit: 5 requests/hour per token

Request:
  {
    "token": "verification-token-from-email"
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "is_verified": true,
      "verified_at": "2026-05-24T12:00:00Z"
    },
    "message": "Email verified successfully"
  }

Error Responses:
  400 - Invalid Token:
    {"status": "error", "message": "Invalid or expired verification token"}
  
  400 - Already Verified:
    {"status": "error", "message": "Email already verified"}
```

---

### 2.6 POST /auth/forgot-password

**Contract**: Request Password Reset

```yaml
Endpoint: POST /api/v1/auth/forgot-password
Auth Required: No
Rate Limit: 3 requests/hour per email

Request:
  {
    "email": "user@example.com"
  }

Success Response (200):
  {
    "status": "success",
    "message": "Password reset instructions sent to email"
  }

Note: Always returns success even if email doesn't exist
      (prevents email enumeration attacks)

Reset Email Contains:
  - Reset link with token
  - Token valid for 1 hour
  - Link format: https://idrm.gov.in/reset-password?token={token}

Follow-up Endpoint (for completing reset):
  POST /auth/reset-password
  Body: {"token": "...", "new_password": "..."}
```

---

## 3. **Service Management Contracts**

### 3.1 POST /services

**Contract**: Create Service Request

```yaml
Endpoint: POST /api/v1/services
Auth Required: Yes
Rate Limit: 5 requests/day per user

Request Schema:
  {
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "location": {
      "type": "Point",
      "coordinates": [78.4867, 17.3850]
    },
    "address": "123 Main St, Hyderabad",
    "description": "Elderly man, chest pain, difficulty breathing",
    "num_people_affected": 1,
    "privacy_level": "PUBLIC",
    "contact_phone": "+919876543210"
  }

Field Validations:
  service_type: 
    enum: [RESCUE, MEDICAL, FOOD, SHELTER, WATER, OTHER]
  priority: 
    enum: [CRITICAL, HIGH, MEDIUM, LOW]
  location.coordinates: 
    - [0]: longitude (-180 to 180)
    - [1]: latitude (-90 to 90)
  description: 
    minLength: 10
    maxLength: 500
  num_people_affected:
    minimum: 1
    maximum: 1000

Success Response (201):
  {
    "status": "success",
    "data": {
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
      "estimated_response_time": "2 hours"
    },
    "message": "Service request created successfully"
  }
```

---

### 3.2 GET /services

**Contract**: List Service Requests

```yaml
Endpoint: GET /api/v1/services
Auth Required: Yes
Rate Limit: 100 requests/minute

Query Parameters:
  status: string[] (comma-separated)
    example: ?status=SUBMITTED,APPROVED
  service_type: string[]
  priority: string[]
  from_date: ISO 8601 date
  to_date: ISO 8601 date
  location: "lon,lat"
    example: ?location=78.4867,17.3850
  radius_km: number (default: 25)
  page: integer (default: 1)
  page_size: integer (default: 20, max: 100)
  sort: string (default: -created_at)
    format: field or -field (- for descending)

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "service_id": "550e8400-e29b-41d4-a716-446655440000",
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "status": "SUBMITTED",
        "location": {"type": "Point", "coordinates": [78.4867, 17.3850]},
        "description": "Elderly man, chest pain...",
        "created_at": "2026-05-24T10:30:00Z",
        "distance_km": 2.5
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_pages": 5,
      "total_count": 87
    }
  }
```

---

### 3.3 POST /services/{id}/accept

**Contract**: Provider Accepts Service Request

```yaml
Endpoint: POST /api/v1/services/{service_id}/accept
Auth Required: Yes (PROVIDER or VOLUNTEER role)
Rate Limit: 50 requests/minute

Request:
  {
    "notes": "Ambulance #3 dispatched. ETA 15 minutes."
  }

Preconditions:
  - Service status must be SUBMITTED or APPROVED
  - Provider must have available capacity
  - Service type must match provider's capabilities

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "ACCEPTED",
      "provider": {
        "org_id": "org-456",
        "name": "Sion Hospital"
      },
      "accepted_at": "2026-05-24T10:35:00Z"
    },
    "message": "Service accepted. Citizen notified."
  }

Error Responses:
  400 - Already Accepted:
    {"status": "error", "message": "Service already accepted"}
  400 - No Capacity:
    {"status": "error", "message": "Provider has no available capacity"}
  403 - Wrong Service Type:
    {"status": "error", "message": "Provider does not offer this service type"}
```

---

### 3.4 GET /services/{id}

**Contract**: Get Single Service Request

```yaml
Endpoint: GET /api/v1/services/{service_id}
Auth Required: Yes
Rate Limit: 100 requests/minute

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "requestor": {
        "user_id": "user-123",
        "full_name": "John Doe",
        "phone": "+919876543210"
      },
      "provider": {
        "org_id": "org-456",
        "name": "Sion Hospital"
      },
      "service_type": "MEDICAL",
      "priority": "CRITICAL",
      "status": "ACCEPTED",
      "location": {
        "type": "Point",
        "coordinates": [78.4867, 17.3850]
      },
      "description": "Elderly man, chest pain...",
      "submitted_at": "2026-05-24T10:30:00Z",
      "accepted_at": "2026-05-24T10:45:00Z",
      "estimated_completion": "2026-05-24T12:30:00Z"
    }
  }
```

---

### 3.5 PUT /services/{id}

**Contract**: Update Service Request

```yaml
Endpoint: PUT /api/v1/services/{service_id}
Auth Required: Yes (Requestor only)
Rate Limit: 10 requests/minute

Authorization:
  - Only the original requestor can update
  - Only if status is SUBMITTED or APPROVED
  - Cannot update after ACCEPTED

Request:
  {
    "service_type": "MEDICAL",
    "priority": "HIGH",
    "description": "Updated description",
    "location": {
      "type": "Point",
      "coordinates": [78.4900, 17.3900]
    },
    "num_people_affected": 2
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "service_type": "MEDICAL",
      "priority": "HIGH",
      "updated_at": "2026-05-24T11:00:00Z"
    },
    "message": "Service request updated"
  }

Error Responses:
  403 - Not Authorized:
    {"status": "error", "message": "Only requestor can update"}
  
  400 - Cannot Update:
    {"status": "error", "message": "Cannot update accepted/completed service"}
```

---

### 3.6 DELETE /services/{id}

**Contract**: Delete Service Request

```yaml
Endpoint: DELETE /api/v1/services/{service_id}
Auth Required: Yes (Requestor or Admin)
Rate Limit: 10 requests/minute

Authorization:
  - Requestor can delete if status is SUBMITTED
  - Admin can delete any service
  - Cannot delete if status is ACCEPTED or later

Success Response (200):
  {
    "status": "success",
    "message": "Service request deleted"
  }

Error Responses:
  403 - Not Authorized:
    {"status": "error", "message": "Cannot delete this service"}
  
  400 - Cannot Delete:
    {"status": "error", "message": "Cannot delete accepted service"}
```

---

### 3.7 POST /services/{id}/approve

**Contract**: Approve Service Request (DM Authority)

```yaml
Endpoint: POST /api/v1/services/{service_id}/approve
Auth Required: Yes (DM_AUTHORITY or ADMIN role)
Rate Limit: 50 requests/minute

Request:
  {
    "notes": "Approved for immediate response. High priority area."
  }

Preconditions:
  - Service status must be SUBMITTED
  - User must have DM_AUTHORITY or ADMIN role
  - Service priority should be CRITICAL or HIGH

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "APPROVED",
      "approved_by": "admin-user-id",
      "approved_at": "2026-05-24T10:35:00Z",
      "approval_notes": "Approved for immediate response"
    },
    "message": "Service request approved"
  }

Workflow:
  SUBMITTED → APPROVED → (provider can accept)

Error Responses:
  403 - Insufficient Permissions:
    {"status": "error", "message": "DM_AUTHORITY role required"}
  
  400 - Already Approved:
    {"status": "error", "message": "Service already approved"}
```

---

### 3.8 POST /services/{id}/reject

**Contract**: Reject Service Request (DM Authority)

```yaml
Endpoint: POST /api/v1/services/{service_id}/reject
Auth Required: Yes (DM_AUTHORITY or ADMIN role)
Rate Limit: 50 requests/minute

Request:
  {
    "reason": "Duplicate request. Already handled by request #XYZ.",
    "alternative_action": "Contact local police station directly"
  }

Preconditions:
  - Service status must be SUBMITTED or APPROVED
  - User must have DM_AUTHORITY or ADMIN role

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "REJECTED",
      "rejected_by": "admin-user-id",
      "rejected_at": "2026-05-24T10:35:00Z",
      "rejection_reason": "Duplicate request"
    },
    "message": "Service request rejected"
  }

Notification:
  - Requestor receives SMS/email with reason
  - Suggested alternative action provided

Error Responses:
  403 - Insufficient Permissions:
    {"status": "error", "message": "DM_AUTHORITY role required"}
  
  400 - Cannot Reject:
    {"status": "error", "message": "Cannot reject completed service"}
```

---

### 3.9 POST /services/{id}/complete

**Contract**: Mark Service as Completed

```yaml
Endpoint: POST /api/v1/services/{service_id}/complete
Auth Required: Yes (Provider)
Rate Limit: 50 requests/minute

Request:
  {
    "completion_notes": "Patient transported to hospital. Stable condition.",
    "resources_used": ["Ambulance #3", "2 paramedics"],
    "completion_photo": "base64_encoded_image" (optional)
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "COMPLETED",
      "completed_at": "2026-05-24T12:30:00Z",
      "completion_notes": "Patient transported..."
    },
    "message": "Service marked as completed"
  }
```

---

### 3.10 POST /services/{id}/verify

**Contract**: Verify Completed Service

```yaml
Endpoint: POST /api/v1/services/{service_id}/verify
Auth Required: Yes (Requestor)
Rate Limit: 20 requests/minute

Request:
  {
    "rating": 5,
    "feedback": "Excellent service. Very professional and quick response."
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "service_id": "550e8400-e29b-41d4-a716-446655440000",
      "status": "VERIFIED",
      "verified_at": "2026-05-24T13:00:00Z",
      "rating": 5
    },
    "message": "Service verified. Thank you for your feedback."
  }
```

---

## 4. **User Management Contracts**

### 4.1 GET /users/me

**Contract**: Get Current User Profile

```yaml
Endpoint: GET /api/v1/users/me
Auth Required: Yes
Rate Limit: 100 requests/minute

Success Response (200):
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
      "preferences": {
        "language": "en",
        "notifications": {
          "email": true,
          "sms": true
        }
      },
      "created_at": "2026-01-15T08:00:00Z"
    }
  }
```

---

### 4.2 PUT /users/me

**Contract**: Update Current User Profile

```yaml
Endpoint: PUT /api/v1/users/me
Auth Required: Yes
Rate Limit: 50 requests/minute

Request (all fields required for PUT):
  {
    "full_name": "John M. Doe",
    "phone": "+919876543210",
    "preferences": {
      "language": "en",
      "notifications": {
        "email": true,
        "sms": true,
        "push": false
      }
    }
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "full_name": "John M. Doe",
      "updated_at": "2026-05-24T12:00:00Z"
    },
    "message": "Profile updated successfully"
  }

Note: Cannot change email, role, or verification status via this endpoint
```

---

### 4.3 GET /users/{id}

**Contract**: Get Any User (Admin Only)

```yaml
Endpoint: GET /api/v1/users/{user_id}
Auth Required: Yes (ADMIN role)
Rate Limit: 100 requests/minute

Authorization:
  - Requires ADMIN or DM_AUTHORITY role
  - Returns full user details including activity

Success Response (200):
  {
    "status": "success",
    "data": {
      "user_id": "user-123",
      "email": "user@example.com",
      "full_name": "John Doe",
      "phone": "+919876543210",
      "role": "CITIZEN",
      "is_active": true,
      "is_verified": true,
      "created_at": "2026-01-15T08:00:00Z",
      "last_login": "2026-05-24T09:00:00Z",
      "statistics": {
        "total_requests": 12,
        "completed_requests": 10,
        "average_rating_given": 4.5
      }
    }
  }

Error Responses:
  403 - Forbidden:
    {"status": "error", "message": "Admin access required"}
  
  404 - Not Found:
    {"status": "error", "message": "User not found"}
```

---

### 4.4 GET /users

**Contract**: List All Users (Admin Only)

```yaml
Endpoint: GET /api/v1/users
Auth Required: Yes (ADMIN role)
Rate Limit: 100 requests/minute

Query Parameters:
  role: string[] (filter by role)
  is_active: boolean
  is_verified: boolean
  search: string (search in name/email)
  from_date: ISO 8601 date
  to_date: ISO 8601 date
  page: integer (default: 1)
  page_size: integer (default: 50, max: 100)
  sort: string (default: -created_at)

Examples:
  - All citizens: ?role=CITIZEN
  - Unverified users: ?is_verified=false
  - Search by name: ?search=john
  - Recent users: ?from_date=2026-05-01

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "user_id": "user-123",
        "email": "user@example.com",
        "full_name": "John Doe",
        "phone": "+919876543210",
        "role": "CITIZEN",
        "is_active": true,
        "is_verified": true,
        "created_at": "2026-01-15T08:00:00Z",
        "last_login": "2026-05-24T09:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total_pages": 20,
      "total_count": 987
    }
  }
```

---

### 4.5 PUT /users/{id}/role

**Contract**: Change User Role (System Admin Only)

```yaml
Endpoint: PUT /api/v1/users/{user_id}/role
Auth Required: Yes (SYSTEM_ADMIN role only)
Rate Limit: 50 requests/minute

Authorization:
  - Only SYSTEM_ADMIN can change roles
  - Cannot change own role
  - Logged in audit_logs

Request:
  {
    "new_role": "EVENT_MANAGER",
    "reason": "Promoted to disaster coordinator for Hyderabad region"
  }

Field Validations:
  new_role:
    required: true
    enum: [CITIZEN, PROVIDER, VOLUNTEER, EVENT_MANAGER, 
           DM_AUTHORITY, AUDITOR, SYSTEM_ADMIN]
  reason:
    required: true
    minLength: 10
    maxLength: 500

Success Response (200):
  {
    "status": "success",
    "data": {
      "user_id": "user-123",
      "old_role": "CITIZEN",
      "new_role": "EVENT_MANAGER",
      "changed_by": "admin-456",
      "changed_at": "2026-05-24T12:00:00Z",
      "reason": "Promoted to disaster coordinator..."
    },
    "message": "User role updated successfully"
  }

Error Responses:
  403 - Forbidden:
    {"status": "error", "message": "SYSTEM_ADMIN role required"}
  
  400 - Cannot Change Own Role:
    {"status": "error", "message": "Cannot change your own role"}
  
  400 - Invalid Role:
    {"status": "error", "message": "Invalid role specified"}

Notification:
  - User receives email about role change
  - New permissions take effect immediately
```

---

## 5. **Organization Management Contracts**

### 5.1 POST /organizations

**Contract**: Register New Organization

```yaml
Endpoint: POST /api/v1/organizations
Auth Required: Yes
Rate Limit: 3 requests/day per user

Request Schema:
  {
    "name": "Sion Hospital",
    "org_type": "HOSPITAL",
    "registration_number": "MH/HSP/2020/12345",
    "service_types": ["MEDICAL", "RESCUE"],
    "capacity": 10,
    "coverage_area": {
      "type": "circle",
      "center": [78.4867, 17.3850],
      "radius_km": 25
    },
    "contact_person": "Dr. Priya Sharma",
    "contact_phone": "+919123456789",
    "contact_email": "contact@sionhospital.com",
    "address": "123 Hospital Road, Hyderabad",
    "documents": {
      "registration_certificate": "base64_encoded_pdf",
      "authorization_letter": "base64_encoded_pdf"
    }
  }

Field Validations:
  name:
    required: true
    minLength: 3
    maxLength: 255
  org_type:
    required: true
    enum: [NGO, HOSPITAL, GOVT_AGENCY, VOLUNTEER_GROUP]
  service_types:
    required: true
    minItems: 1
    items: enum [RESCUE, MEDICAL, FOOD, SHELTER, WATER, OTHER]
  capacity:
    required: true
    minimum: 1
    maximum: 1000
  contact_phone:
    required: true
    pattern: "^\\+[1-9][0-9]{1,14}$"

Success Response (201):
  {
    "status": "success",
    "data": {
      "org_id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Sion Hospital",
      "org_type": "HOSPITAL",
      "is_verified": false,
      "status": "PENDING_VERIFICATION",
      "created_at": "2026-05-24T11:15:00Z"
    },
    "message": "Organization registered. Awaiting admin verification."
  }

Error Responses:
  400 - Duplicate Registration:
    {
      "status": "error",
      "message": "Organization with this registration number already exists"
    }
  
  413 - Documents Too Large:
    {
      "status": "error",
      "message": "Document size exceeds 5MB limit"
    }
```

---

### 5.2 GET /organizations/{org_id}

**Contract**: Get Organization Details

```yaml
Endpoint: GET /api/v1/organizations/{org_id}
Auth Required: Yes
Rate Limit: 100 requests/minute

Path Parameters:
  org_id: UUID of organization

Success Response (200):
  {
    "status": "success",
    "data": {
      "org_id": "org-456",
      "name": "Sion Hospital",
      "org_type": "HOSPITAL",
      "is_verified": true,
      "registration_number": "MH/HSP/2020/12345",
      "service_types": ["MEDICAL", "RESCUE"],
      "capacity": 10,
      "available_capacity": 3,
      "coverage_area": {
        "type": "circle",
        "center": [78.4867, 17.3850],
        "radius_km": 25
      },
      "contact_person": "Dr. Priya Sharma",
      "contact_phone": "+919123456789",
      "contact_email": "contact@sionhospital.com",
      "address": "123 Hospital Road, Hyderabad",
      "statistics": {
        "total_services_completed": 487,
        "total_services_accepted": 512,
        "average_rating": 4.7,
        "average_response_time_minutes": 18
      },
      "created_at": "2026-01-10T09:00:00Z",
      "verified_at": "2026-01-15T14:30:00Z"
    }
  }

Error Responses:
  404 - Not Found:
    {"status": "error", "message": "Organization not found"}
```

---

### 5.3 PUT /organizations/{org_id}

**Contract**: Update Organization Details

```yaml
Endpoint: PUT /api/v1/organizations/{org_id}
Auth Required: Yes
Authorization: Organization admin or system admin
Rate Limit: 50 requests/minute

Request (all fields required for PUT):
  {
    "capacity": 15,
    "available_capacity": 8,
    "service_types": ["MEDICAL", "RESCUE", "FOOD"],
    "contact_phone": "+919123456790",
    "contact_email": "contact@sionhospital.com",
    "coverage_area": {
      "type": "circle",
      "center": [78.4867, 17.3850],
      "radius_km": 30
    }
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "org_id": "org-456",
      "name": "Sion Hospital",
      "capacity": 15,
      "available_capacity": 8,
      "updated_at": "2026-05-24T12:00:00Z"
    },
    "message": "Organization updated successfully"
  }

Error Responses:
  403 - Forbidden:
    {"status": "error", "message": "Not authorized to update this organization"}
  
  400 - Invalid Update:
    {
      "status": "error",
      "message": "available_capacity cannot exceed capacity"
    }
```

---

### 5.4 GET /organizations

**Contract**: List Organizations

```yaml
Endpoint: GET /api/v1/organizations
Auth Required: Yes
Rate Limit: 100 requests/minute

Query Parameters:
  org_type: string (NGO, HOSPITAL, etc.)
  service_types: string[] (comma-separated)
  is_verified: boolean
  location: "lon,lat"
  radius_km: number
  page: integer (default: 1)
  page_size: integer (default: 20)

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "org_id": "org-456",
        "name": "Sion Hospital",
        "org_type": "HOSPITAL",
        "service_types": ["MEDICAL", "RESCUE"],
        "is_verified": true,
        "available_capacity": 3,
        "distance_km": 5.2
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_pages": 3,
      "total_count": 47
    }
  }
```

---

## 6. **Notification Contracts**

### 6.1 GET /notifications

**Contract**: Get User Notifications

```yaml
Endpoint: GET /api/v1/notifications
Auth Required: Yes
Rate Limit: 100 requests/minute

Query Parameters:
  status: string[] (PENDING, SENT, READ)
  type: string[] (SERVICE_CREATED, SERVICE_ACCEPTED, etc.)
  from_date: ISO 8601 date
  page: integer
  page_size: integer (max: 100)

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "notification_id": "notif-123",
        "type": "SERVICE_ACCEPTED",
        "channel": "SMS",
        "subject": "Service Request Accepted",
        "body": "Your request #abc123 has been accepted by Sion Hospital",
        "status": "SENT",
        "related_service_id": "abc123",
        "created_at": "2026-05-24T10:35:00Z",
        "sent_at": "2026-05-24T10:35:02Z",
        "read_at": null
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total_count": 45,
      "unread_count": 12
    }
  }
```

---

### 6.2 PATCH /notifications/{notification_id}/read

**Contract**: Mark Notification as Read

```yaml
Endpoint: PATCH /api/v1/notifications/{notification_id}/read
Auth Required: Yes
Rate Limit: 100 requests/minute

Success Response (200):
  {
    "status": "success",
    "data": {
      "notification_id": "notif-123",
      "status": "READ",
      "read_at": "2026-05-24T12:00:00Z"
    }
  }

Error Responses:
  404 - Not Found:
    {"status": "error", "message": "Notification not found"}
  
  403 - Forbidden:
    {"status": "error", "message": "Not your notification"}
```

---

### 6.3 POST /notifications/mark-all-read

**Contract**: Mark All Notifications as Read

```yaml
Endpoint: POST /api/v1/notifications/mark-all-read
Auth Required: Yes
Rate Limit: 10 requests/minute

Success Response (200):
  {
    "status": "success",
    "data": {
      "marked_count": 12
    },
    "message": "All notifications marked as read"
  }
```

---

## 7. **Geospatial Contracts**

### 7.1 GET /geo/nearby

**Contract**: Find Nearby Service Requests

```yaml
Endpoint: GET /api/v1/geo/nearby
Auth Required: Yes (PROVIDER role)
Rate Limit: 100 requests/minute

Query Parameters (Required):
  location: "lon,lat"
    example: ?location=78.4867,17.3850
  radius_km: number (default: 25, max: 100)
  
Query Parameters (Optional):
  service_type: string
  priority: string
  limit: integer (default: 20, max: 100)

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "service_id": "550e8400-e29b-41d4-a716-446655440000",
        "service_type": "MEDICAL",
        "priority": "CRITICAL",
        "location": {"type": "Point", "coordinates": [78.4900, 17.3900]},
        "distance_km": 2.5,
        "bearing_degrees": 45.0,
        "created_at": "2026-05-24T10:30:00Z"
      }
    ],
    "metadata": {
      "search_location": [78.4867, 17.3850],
      "radius_km": 25,
      "total_found": 15
    }
  }
```

---

### 7.2 POST /geo/cluster

**Contract**: Generate Hotspot Clusters

```yaml
Endpoint: POST /api/v1/geo/cluster
Auth Required: Yes (EVENT_MANAGER or higher)
Rate Limit: 20 requests/minute

Request:
  {
    "bbox": {
      "min_lon": 78.35,
      "max_lon": 78.65,
      "min_lat": 17.25,
      "max_lat": 17.55
    },
    "cluster_radius_km": 2,
    "min_cluster_size": 5,
    "service_types": ["MEDICAL", "RESCUE"],
    "from_date": "2026-05-20T00:00:00Z",
    "to_date": "2026-05-24T23:59:59Z"
  }

Field Validations:
  cluster_radius_km:
    minimum: 0.5
    maximum: 10
  min_cluster_size:
    minimum: 2
    maximum: 100

Success Response (200):
  {
    "status": "success",
    "data": {
      "clusters": [
        {
          "cluster_id": 1,
          "center": {
            "type": "Point",
            "coordinates": [78.4867, 17.3850]
          },
          "radius_km": 2.0,
          "service_count": 47,
          "priority_breakdown": {
            "CRITICAL": 15,
            "HIGH": 22,
            "MEDIUM": 8,
            "LOW": 2
          },
          "dominant_service_type": "MEDICAL",
          "earliest_request": "2026-05-20T08:00:00Z",
          "latest_request": "2026-05-24T15:30:00Z"
        }
      ],
      "total_clusters": 12,
      "total_services_analyzed": 548,
      "clustering_params": {
        "radius_km": 2,
        "min_size": 5
      }
    }
  }

Use Cases:
  - Identify disaster hotspots
  - Resource allocation planning
  - Emergency response prioritization
  - Deployment of mobile units
```

---

### 7.3 GET /geo/geojson

**Contract**: Export Services as GeoJSON

```yaml
Endpoint: GET /api/v1/geo/geojson
Auth Required: Yes
Rate Limit: 10 requests/minute

Query Parameters:
  bbox: "min_lon,min_lat,max_lon,max_lat"
    example: ?bbox=78.35,17.25,78.65,17.55
  service_types: string[]
  status: string[]
  from_date: ISO 8601 date
  to_date: ISO 8601 date
  limit: integer (max: 10000)

Success Response (200):
  {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "Point",
          "coordinates": [78.4867, 17.3850]
        },
        "properties": {
          "service_id": "550e8400-e29b-41d4-a716-446655440000",
          "service_type": "MEDICAL",
          "priority": "CRITICAL",
          "status": "ACCEPTED",
          "description": "Elderly man, chest pain",
          "submitted_at": "2026-05-24T10:30:00Z"
        }
      }
    ],
    "metadata": {
      "total_features": 156,
      "bbox": [78.35, 17.25, 78.65, 17.55],
      "generated_at": "2026-05-24T14:00:00Z"
    }
  }

Content-Type: application/geo+json

Use Cases:
  - Import into GIS software (QGIS, ArcGIS)
  - Mapping tools integration
  - Spatial analysis
  - Custom visualization
```

---

### 7.4 GET /geo/bbox

**Contract**: Bounding Box Search

```yaml
Endpoint: GET /api/v1/geo/bbox
Auth Required: Yes
Rate Limit: 100 requests/minute

Query Parameters (Required):
  min_lon: number
  min_lat: number
  max_lon: number
  max_lat: number
  
Query Parameters (Optional):
  service_type: string
  priority: string
  status: string
  page: integer
  page_size: integer (max: 100)

Example:
  ?min_lon=78.35&min_lat=17.25&max_lon=78.65&max_lat=17.55

Success Response (200):
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
        "submitted_at": "2026-05-24T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 100,
      "total_count": 234
    },
    "bbox": {
      "min_lon": 78.35,
      "min_lat": 17.25,
      "max_lon": 78.65,
      "max_lat": 17.55,
      "area_km2": 144.5
    }
  }

Use Cases:
  - Large-scale map queries
  - District/region-wide analysis
  - Bulk data extraction
  - Coverage area verification
```

---

---

## 8. **Admin Contracts**

### 8.1 GET /admin/users

**Contract**: List All Users (Admin Only)

```yaml
Endpoint: GET /api/v1/admin/users
Auth Required: Yes (ADMIN role)
Rate Limit: 100 requests/minute

Query Parameters:
  role: string[] (CITIZEN, PROVIDER, etc.)
  is_active: boolean
  is_verified: boolean
  search: string (search in name/email)
  from_date: ISO 8601 date
  to_date: ISO 8601 date
  page: integer
  page_size: integer (max: 100)

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "user_id": "user-123",
        "email": "user@example.com",
        "full_name": "John Doe",
        "phone": "+919876543210",
        "role": "CITIZEN",
        "is_active": true,
        "is_verified": true,
        "created_at": "2026-01-15T08:00:00Z",
        "last_login": "2026-05-24T09:00:00Z",
        "total_requests": 12,
        "total_services_provided": 0
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 50,
      "total_pages": 20,
      "total_count": 987
    }
  }

Authorization:
  - User must have ADMIN role
  - Returns 403 if insufficient permissions
```

---

### 8.2 PATCH /admin/users/{user_id}

**Contract**: Update User (Admin Only)

```yaml
Endpoint: PATCH /api/v1/admin/users/{user_id}
Auth Required: Yes (ADMIN role)
Rate Limit: 50 requests/minute

Request (all fields optional):
  {
    "is_active": false,
    "is_verified": true,
    "role": "EVENT_MANAGER"
  }

Success Response (200):
  {
    "status": "success",
    "data": {
      "user_id": "user-123",
      "is_active": false,
      "is_verified": true,
      "role": "EVENT_MANAGER",
      "updated_at": "2026-05-24T12:00:00Z"
    },
    "message": "User updated successfully"
  }

Common Use Cases:
  - Deactivate user: {"is_active": false}
  - Verify user: {"is_verified": true}
  - Promote to coordinator: {"role": "EVENT_MANAGER"}
  - Demote from admin: {"role": "CITIZEN"}

Error Responses:
  403 - Forbidden:
    {"status": "error", "message": "Admin access required"}
  
  400 - Invalid Role:
    {"status": "error", "message": "Cannot change own role"}
```

---

### 8.3 GET /admin/organizations/pending

**Contract**: Get Pending Organization Verifications

```yaml
Endpoint: GET /api/v1/admin/organizations/pending
Auth Required: Yes (ADMIN or DM_AUTHORITY)
Rate Limit: 100 requests/minute

Query Parameters:
  org_type: string
  from_date: ISO 8601 date
  page: integer
  page_size: integer

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "org_id": "org-789",
        "name": "New Hope NGO",
        "org_type": "NGO",
        "registration_number": "TS/NGO/2026/00123",
        "service_types": ["FOOD", "SHELTER"],
        "contact_person": "Mr. Kumar",
        "contact_phone": "+919123456789",
        "documents": {
          "registration_certificate": "https://storage.../cert.pdf",
          "authorization_letter": "https://storage.../auth.pdf"
        },
        "created_at": "2026-05-20T10:00:00Z",
        "pending_since_days": 4
      }
    ],
    "pagination": {
      "page": 1,
      "total_count": 15
    }
  }
```

---

### 8.4 POST /admin/organizations/{org_id}/verify

**Contract**: Verify Organization

```yaml
Endpoint: POST /api/v1/admin/organizations/{org_id}/verify
Auth Required: Yes (ADMIN or DM_AUTHORITY)
Rate Limit: 50 requests/minute

Request:
  {
    "action": "APPROVE",
    "notes": "All documents verified. Registration valid."
  }

Field Validations:
  action:
    required: true
    enum: [APPROVE, REJECT]
  notes:
    required: true
    minLength: 10
    maxLength: 500

Success Response (200):
  {
    "status": "success",
    "data": {
      "org_id": "org-789",
      "name": "New Hope NGO",
      "is_verified": true,
      "verified_at": "2026-05-24T12:00:00Z",
      "verified_by": "admin-user-id"
    },
    "message": "Organization approved and verified"
  }

If Rejected:
  {
    "status": "success",
    "data": {
      "org_id": "org-789",
      "is_verified": false,
      "rejection_reason": "Invalid registration documents"
    },
    "message": "Organization registration rejected"
  }
```

---

### 8.5 GET /admin/audit-log

**Contract**: Get Audit Logs

```yaml
Endpoint: GET /api/v1/admin/audit-log
Auth Required: Yes (ADMIN or DM_AUTHORITY)
Rate Limit: 100 requests/minute

Query Parameters:
  user_id: UUID
  action: string[] (SERVICE_CREATED, USER_LOGIN, etc.)
  resource_type: string (ServiceRequest, User, Organization)
  resource_id: UUID
  from_date: ISO 8601 date
  to_date: ISO 8601 date
  ip_address: string
  page: integer
  page_size: integer (max: 100)

Success Response (200):
  {
    "status": "success",
    "data": [
      {
        "log_id": 12345,
        "user_id": "user-abc",
        "user_email": "user@example.com",
        "user_role": "CITIZEN",
        "action": "SERVICE_CREATED",
        "resource_type": "ServiceRequest",
        "resource_id": "service-xyz",
        "ip_address": "203.0.113.45",
        "user_agent": "Mozilla/5.0...",
        "changes": {
          "after": {
            "service_type": "MEDICAL",
            "priority": "CRITICAL"
          }
        },
        "timestamp": "2026-05-24T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "page_size": 100,
      "total_count": 50000
    }
  }

Use Cases:
  - Track user activity: ?user_id={uuid}
  - Investigation: ?action=USER_DEACTIVATED&from_date=2026-05-01
  - Security audit: ?ip_address=suspicious.ip.address
  - Resource history: ?resource_type=ServiceRequest&resource_id={uuid}
```

---

### 8.6 GET /admin/stats

**Contract**: Get System-Wide Statistics

```yaml
Endpoint: GET /api/v1/admin/stats
Auth Required: Yes (ADMIN or DM_AUTHORITY)
Rate Limit: 10 requests/minute

Query Parameters:
  from_date: ISO 8601 date (default: 30 days ago)
  to_date: ISO 8601 date (default: now)

Success Response (200):
  {
    "status": "success",
    "data": {
      "users": {
        "total": 1547,
        "active": 1423,
        "new_this_period": 87,
        "by_role": {
          "CITIZEN": 1200,
          "PROVIDER": 150,
          "VOLUNTEER": 100,
          "EVENT_MANAGER": 50,
          "DM_AUTHORITY": 30,
          "ADMIN": 17
        }
      },
      "organizations": {
        "total": 52,
        "verified": 48,
        "pending": 4,
        "by_type": {
          "HOSPITAL": 15,
          "NGO": 25,
          "GOVT_AGENCY": 8,
          "VOLUNTEER_GROUP": 4
        }
      },
      "services": {
        "total": 8247,
        "pending": 156,
        "completed": 6891,
        "verified": 6234,
        "fulfillment_rate": 0.87,
        "avg_response_time_minutes": 108
      },
      "performance": {
        "api_requests_total": 1250000,
        "api_requests_per_minute": 347,
        "avg_response_time_ms": 156,
        "error_rate": 0.012
      }
    }
  }
```

---

### 8.7 POST /admin/broadcast

**Contract**: Send Broadcast Notification

```yaml
Endpoint: POST /api/v1/admin/broadcast
Auth Required: Yes (ADMIN or DM_AUTHORITY)
Rate Limit: 5 requests/hour

Request:
  {
    "target": "ALL_USERS",
    "channel": "SMS",
    "subject": "Emergency Alert",
    "message": "Cyclone warning for next 24 hours. Stay indoors.",
    "filters": {
      "roles": ["CITIZEN"],
      "location": {
        "center": [78.4867, 17.3850],
        "radius_km": 50
      }
    }
  }

Field Validations:
  target:
    enum: [ALL_USERS, ROLE_BASED, LOCATION_BASED]
  channel:
    enum: [EMAIL, SMS, PUSH, IN_APP]
  message:
    required: true
    maxLength: 500 (for SMS)

Success Response (202):
  {
    "status": "success",
    "data": {
      "broadcast_id": "broadcast-123",
      "estimated_recipients": 1247,
      "status": "QUEUED",
      "created_at": "2026-05-24T12:00:00Z"
    },
    "message": "Broadcast queued for delivery"
  }

Error Responses:
  400 - Too Many Recipients:
    {
      "status": "error",
      "message": "Cannot broadcast to more than 10,000 users at once"
    }
```

---

### 8.8 GET /admin/system-health

**Contract**: System Health Check

```yaml
Endpoint: GET /api/v1/admin/system-health
Auth Required: Yes (SYSTEM_ADMIN role)
Rate Limit: 60 requests/minute

Success Response (200):
  {
    "status": "success",
    "data": {
      "overall_status": "HEALTHY",
      "timestamp": "2026-05-24T14:00:00Z",
      "components": {
        "database": {
          "status": "HEALTHY",
          "response_time_ms": 12,
          "connections": {
            "active": 15,
            "idle": 5,
            "max": 100
          }
        },
        "redis": {
          "status": "HEALTHY",
          "response_time_ms": 2,
          "memory_used_mb": 124,
          "memory_max_mb": 512
        },
        "api": {
          "status": "HEALTHY",
          "uptime_seconds": 3456789,
          "requests_per_minute": 347,
          "error_rate": 0.012
        },
        "background_jobs": {
          "status": "HEALTHY",
          "queue_size": 23,
          "processing": 5,
          "failed_last_hour": 2
        },
        "external_services": {
          "sms_provider": {
            "status": "HEALTHY",
            "last_check": "2026-05-24T13:59:00Z"
          },
          "email_provider": {
            "status": "HEALTHY",
            "last_check": "2026-05-24T13:59:00Z"
          }
        }
      },
      "metrics": {
        "total_users": 1547,
        "active_services": 156,
        "database_size_mb": 2340,
        "disk_usage_percent": 45,
        "memory_usage_percent": 62,
        "cpu_usage_percent": 38
      }
    }
  }

Unhealthy Response (503):
  {
    "status": "error",
    "message": "System degraded",
    "data": {
      "overall_status": "DEGRADED",
      "components": {
        "database": {
          "status": "DEGRADED",
          "error": "High connection count"
        }
      }
    }
  }

Status Values:
  - HEALTHY: All systems operational
  - DEGRADED: Partial functionality
  - UNHEALTHY: Critical issues
  
Use Cases:
  - Monitoring & alerting
  - Load balancer health checks
  - Operations dashboard
  - Incident response
```

---

## 9. **Analytics Contracts**

### 9.1 GET /analytics/dashboard

**Contract**: Get Dashboard Metrics

```yaml
Endpoint: GET /api/v1/analytics/dashboard
Auth Required: Yes (COORDINATOR, ADMIN)
Rate Limit: 10 requests/minute

Query Parameters:
  from_date: ISO 8601 date (default: 30 days ago)
  to_date: ISO 8601 date (default: now)
  granularity: enum [day, week, month] (default: day)

Success Response (200):
  {
    "status": "success",
    "data": {
      "summary": {
        "total_requests": 1247,
        "pending_requests": 156,
        "completed_requests": 892,
        "average_response_time_minutes": 108,
        "fulfillment_rate": 0.85
      },
      "time_series": [
        {
          "date": "2026-05-01",
          "requests_created": 45,
          "requests_completed": 38
        }
      ],
      "by_service_type": {
        "MEDICAL": 423,
        "RESCUE": 312,
        "FOOD": 245
      }
    }
  }
```

---

### 9.2 GET /analytics/reports

**Contract**: Get Detailed Reports

```yaml
Endpoint: GET /api/v1/analytics/reports
Auth Required: Yes (EVENT_MANAGER or higher)
Rate Limit: 10 requests/minute

Query Parameters:
  report_type: string (required)
    enum: [performance, providers, services, response_time, geographic]
  from_date: ISO 8601 date (required)
  to_date: ISO 8601 date (required)
  format: string (default: json)
    enum: [json, csv]
  filters: JSON object
    {
      "service_types": ["MEDICAL", "RESCUE"],
      "priorities": ["CRITICAL", "HIGH"],
      "districts": ["Hyderabad", "Warangal"]
    }

Success Response (200) - Performance Report:
  {
    "status": "success",
    "data": {
      "report_type": "performance",
      "period": {
        "from": "2026-05-01T00:00:00Z",
        "to": "2026-05-24T23:59:59Z"
      },
      "metrics": {
        "total_requests": 1247,
        "completed": 892,
        "pending": 156,
        "rejected": 199,
        "fulfillment_rate": 0.85,
        "avg_response_time_minutes": 108,
        "median_response_time_minutes": 65,
        "p95_response_time_minutes": 245
      },
      "by_priority": {
        "CRITICAL": {
          "count": 234,
          "avg_response_minutes": 45,
          "fulfillment_rate": 0.95
        },
        "HIGH": {
          "count": 445,
          "avg_response_minutes": 87,
          "fulfillment_rate": 0.89
        }
      },
      "trends": [
        {
          "date": "2026-05-01",
          "requests": 45,
          "completed": 38,
          "avg_response_minutes": 102
        }
      ]
    }
  }

Success Response (200) - Provider Report:
  {
    "status": "success",
    "data": {
      "report_type": "providers",
      "top_performers": [
        {
          "org_id": "org-456",
          "name": "Sion Hospital",
          "services_completed": 147,
          "avg_rating": 4.8,
          "avg_response_minutes": 38,
          "capacity_utilization": 0.75
        }
      ],
      "by_org_type": {
        "HOSPITAL": {
          "count": 15,
          "services_completed": 534,
          "avg_rating": 4.6
        }
      }
    }
  }

Use Cases:
  - Government reporting
  - Performance analysis
  - Provider evaluation
  - Resource planning
  - Policy decisions
```

---

### 9.3 POST /analytics/export

**Contract**: Export Analytics Data

```yaml
Endpoint: POST /api/v1/analytics/export
Auth Required: Yes (DM_AUTHORITY or higher)
Rate Limit: 5 requests/hour

Request:
  {
    "export_type": "services",
    "format": "csv",
    "from_date": "2026-05-01T00:00:00Z",
    "to_date": "2026-05-24T23:59:59Z",
    "filters": {
      "service_types": ["MEDICAL", "RESCUE"],
      "status": ["COMPLETED", "VERIFIED"],
      "districts": ["Hyderabad"]
    },
    "include_fields": [
      "service_id",
      "requestor_name",
      "provider_name",
      "service_type",
      "priority",
      "submitted_at",
      "completed_at",
      "response_time_minutes",
      "rating"
    ]
  }

Field Validations:
  export_type:
    required: true
    enum: [services, users, organizations, audit, performance]
  format:
    required: true
    enum: [csv, xlsx, json]
  date range:
    maximum: 90 days

Success Response (202):
  {
    "status": "success",
    "data": {
      "export_id": "export-123",
      "status": "QUEUED",
      "estimated_time_seconds": 45,
      "created_at": "2026-05-24T14:00:00Z"
    },
    "message": "Export queued. You'll receive email when ready."
  }

Follow-up: Check Export Status
  GET /analytics/export/{export_id}
  
  Response:
    {
      "export_id": "export-123",
      "status": "COMPLETED",
      "download_url": "https://idrm.gov.in/exports/export-123.csv",
      "expires_at": "2026-05-25T14:00:00Z",
      "file_size_mb": 12.5,
      "record_count": 1247
    }

Error Responses:
  400 - Date Range Too Large:
    {"status": "error", "message": "Date range cannot exceed 90 days"}
  
  429 - Export Limit:
    {"status": "error", "message": "Maximum 5 exports per hour"}

Use Cases:
  - Government compliance reporting
  - Data archival
  - Offline analysis
  - Integration with other systems
```

---

## 10. **Error Responses**

### 10.1 Standard Error Format

```yaml
All errors follow this format:
  {
    "status": "error",
    "message": "Human-readable error message",
    "errors": [
      {
        "field": "field_name",
        "message": "Field-specific error"
      }
    ]
  }

HTTP Status Codes:
  400 Bad Request: Validation error, malformed request
  401 Unauthorized: Missing or invalid authentication
  403 Forbidden: Valid auth, insufficient permissions
  404 Not Found: Resource not found
  409 Conflict: Resource already exists
  429 Too Many Requests: Rate limit exceeded
  500 Internal Server Error: Server error
  503 Service Unavailable: Maintenance mode
```

---

## 11. **Contract Testing**

### 11.1 Pact Contract Tests

```javascript
// tests/contract/service-creation.pact.js

const { Pact } = require('@pact-foundation/pact');
const { like, term } = require('@pact-foundation/pact/dsl/matchers');

describe('Service Creation Contract', () => {
  const provider = new Pact({
    consumer: 'IDRM-Frontend',
    provider: 'IDRM-Backend',
  });

  beforeAll(() => provider.setup());
  afterAll(() => provider.finalize());

  it('creates a service request', async () => {
    await provider.addInteraction({
      state: 'user is authenticated',
      uponReceiving: 'a request to create a service',
      withRequest: {
        method: 'POST',
        path: '/api/v1/services',
        headers: {
          'Authorization': term({
            matcher: 'Bearer .+',
            generate: 'Bearer eyJhbGc...'
          }),
          'Content-Type': 'application/json',
        },
        body: {
          service_type: 'MEDICAL',
          priority: 'CRITICAL',
          location: {
            type: 'Point',
            coordinates: [78.4867, 17.3850]
          },
          description: like('Emergency medical request')
        }
      },
      willRespondWith: {
        status: 201,
        headers: {
          'Content-Type': 'application/json'
        },
        body: {
          status: 'success',
          data: {
            service_id: like('550e8400-e29b-41d4-a716-446655440000'),
            service_type: 'MEDICAL',
            priority: 'CRITICAL',
            status: 'SUBMITTED'
          }
        }
      }
    });

    // Test implementation...
  });
});

// Run: npm run test:contract
```

---

### 8.2 OpenAPI Validation

```yaml
## Use OpenAPI spec for automated validation
## openapi.yml

openapi: 3.0.0
info:
  title: IDRM API
  version: 3.0.0
paths:
  /api/v1/services:
    post:
      summary: Create service request
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ServiceCreate'
      responses:
        '201':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ServiceResponse'

## Validate: 
## swagger-cli validate openapi.yml
```

---

**END OF API-CONTRACTS-v3.md**

**Total Endpoints Documented**: 36 endpoints (100% of API Reference Matrix)

Breakdown by Section:
  - Authentication: 6 endpoints
    • POST /auth/register
    • POST /auth/login
    • POST /auth/refresh
    • POST /auth/logout
    • POST /auth/verify-email
    • POST /auth/forgot-password
  
  - Service Management: 10 endpoints
    • GET /services (list)
    • POST /services (create)
    • GET /services/{id}
    • PUT /services/{id}
    • DELETE /services/{id}
    • POST /services/{id}/accept
    • POST /services/{id}/complete
    • POST /services/{id}/verify
    • POST /services/{id}/approve
    • POST /services/{id}/reject
  
  - User Management: 5 endpoints
    • GET /users/me
    • PUT /users/me
    • GET /users/{id}
    • GET /users
    • PUT /users/{id}/role
  
  - Organization Management: 4 endpoints
    • POST /organizations
    • GET /organizations/{id}
    • PUT /organizations/{id}
    • GET /organizations
  
  - Geospatial: 4 endpoints
    • GET /geo/nearby
    • POST /geo/cluster
    • GET /geo/geojson
    • GET /geo/bbox
  
  - Analytics: 3 endpoints
    • GET /analytics/dashboard
    • GET /analytics/reports
    • POST /analytics/export
  
  - Admin: 3 endpoints (moved user management to separate section)
    • GET /admin/audit-log
    • GET /admin/system-health
    • POST /admin/broadcast
  
  - Notifications: 1 endpoint (in Admin section)
    Note: Notification endpoints were added based on PRD requirements
    but are not in original 44-API-REFERENCE-MATRIX.md
  
**Coverage**: 100% ✅ of original API Reference Matrix
**Completeness**: All 36 endpoints fully specified
**Status**: ✅ Production-ready API contracts
**Contract Testing**: Pact examples included
**OpenAPI**: Ready for spec generation
**Methods**: GET (16), POST (15), PUT (4), DELETE (1)
**REST Compliance**: ✅ Consistent with matrix (PUT not PATCH)

---

## IDRM: Complete API Reference Matrix (Security-Hardened v3.1)

### All Endpoints, RBAC, Methods & JSON Formats - Security Reviewed

**Version**: 3.1 Security-Hardened  
**Audience**: Developers, Testers, Security Auditors  
**Last Updated**: May 16, 2026  
**Security Review**: ✅ Complete

---

### 🔒 **CRITICAL Security Notice**

**This document has been security-reviewed and updated with:**
- ✅ Corrected HTTP methods (POST vs PUT analysis)
- ✅ Security annotations on every endpoint
- ✅ Input validation requirements
- ✅ Rate limiting recommendations
- ✅ CSRF protection requirements
- ✅ Data exposure warnings
- ✅ Authentication/Authorization requirements

**⚠️ DEVELOPERS: Read security annotations before implementing!**

---

### 📚 **Table of Contents**

1. [Security Overview](#1-security-overview)
2. [Quick Reference Tables](#2-quick-reference-tables)
3. [HTTP Method Guidelines](#3-http-method-guidelines)
4. [Authentication Endpoints](#4-authentication-endpoints)
5. [Service Management Endpoints](#5-service-management-endpoints)
6. [User & Organization Endpoints](#6-user--organization-endpoints)
7. [Geospatial Endpoints](#7-geospatial-endpoints)
8. [Analytics & Reporting Endpoints](#8-analytics--reporting-endpoints)
9. [Admin Endpoints](#9-admin-endpoints)
10. [Security Checklist](#10-security-checklist)

---

### 1. **Security Overview**

#### 1.1 Critical Security Requirements

**ALL Endpoints MUST:**
- ✅ Use HTTPS only (HTTP 301 redirect to HTTPS)
- ✅ Validate all inputs (type, length, format)
- ✅ Sanitize all outputs (prevent XSS)
- ✅ Use parameterized queries (prevent SQL injection)
- ✅ Check authorization (not just authentication!)
- ✅ Log security events (auth failures, permission denials)
- ✅ Include CORS headers (restrict origins)
- ✅ Set security headers (CSP, X-Frame-Options, etc.)

**State-Changing Endpoints MUST:**
- ✅ Require authentication (no public POST/PUT/DELETE!)
- ✅ Use CSRF tokens (except for API token auth)
- ✅ Implement rate limiting
- ✅ Validate ownership (users can only modify own resources)

**Sensitive Data MUST:**
- ✅ Never include passwords in responses
- ✅ Hash passwords with bcrypt (min cost 12)
- ✅ Redact sensitive fields based on privacy level
- ✅ Use HTTPS for transmission
- ✅ Expire tokens appropriately

---

#### 1.2 Authentication Security

**JWT Tokens:**
```json
{
  "access_token": "eyJ...",  // Short-lived (15 min)
  "refresh_token": "eyJ..."  // Longer-lived (7 days), stored securely
}
```

**Security Rules:**
- ✅ Access tokens expire in 15 minutes
- ✅ Refresh tokens expire in 7 days
- ✅ Tokens stored in HTTP-only cookies (NOT localStorage!)
- ✅ CSRF tokens required for cookie-based auth
- ✅ Invalid tokens return 401 Unauthorized
- ✅ Rate limit: 5 failed logins per 15 min per IP

---

#### 1.3 Rate Limiting

**Recommended Limits:**

| Endpoint Type | Limit | Window | Action on Exceed |
|---------------|-------|--------|------------------|
| **Authentication** | 5 attempts | 15 min | 429 + delay |
| **Public GET** | 60 requests | 1 min | 429 |
| **Authenticated GET** | 300 requests | 1 min | 429 |
| **POST/PUT/DELETE** | 30 requests | 1 min | 429 |
| **Export/Analytics** | 10 requests | 1 hour | 429 |

**Headers to Include:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1716567890
```

---

### 2. **Quick Reference Tables**

#### 2.1 All Endpoints with Security Annotations

| # | Endpoint | Method | Auth? | Min Role | Security Level | Rate Limit |
|---|----------|--------|-------|----------|----------------|------------|
| **AUTHENTICATION** |
| 1 | `/api/v1/auth/register` | POST | ❌ No | Public | 🔴 Critical | 5/15min |
| 2 | `/api/v1/auth/login` | POST | ❌ No | Public | 🔴 Critical | 5/15min |
| 3 | `/api/v1/auth/logout` | POST | ✅ Yes | Any | 🟡 Medium | 30/min |
| 4 | `/api/v1/auth/refresh` | POST | ✅ Yes | Any | 🔴 Critical | 10/min |
| 5 | `/api/v1/auth/verify-email` | POST | ❌ No | Public | 🟡 Medium | 5/15min |
| 6 | `/api/v1/auth/forgot-password` | POST | ❌ No | Public | 🔴 Critical | 3/hour |
| 7 | `/api/v1/auth/reset-password` | POST | ❌ No | Public | 🔴 Critical | 3/hour |
| **SERVICES** |
| 8 | `/api/v1/services` | GET | ✅ Yes | Citizen | 🟢 Low | 300/min |
| 9 | `/api/v1/services` | POST | ✅ Yes | Citizen | 🟡 Medium | 30/min |
| 10 | `/api/v1/services/{id}` | GET | ✅ Yes | Citizen | 🟡 Medium | 300/min |
| 11 | `/api/v1/services/{id}` | POST | ✅ Yes | Requestor | 🟡 Medium | 30/min |
| 12 | `/api/v1/services/{id}/cancel` | POST | ✅ Yes | Requestor | 🟡 Medium | 30/min |
| 13 | `/api/v1/services/{id}/accept` | POST | ✅ Yes | Provider | 🟡 Medium | 30/min |
| 14 | `/api/v1/services/{id}/complete` | POST | ✅ Yes | Provider | 🟡 Medium | 30/min |
| 15 | `/api/v1/services/{id}/verify` | POST | ✅ Yes | Requestor | 🟡 Medium | 30/min |
| 16 | `/api/v1/services/{id}/approve` | POST | ✅ Yes | DM_Authority | 🔴 Critical | 30/min |
| 17 | `/api/v1/services/{id}/reject` | POST | ✅ Yes | DM_Authority | 🔴 Critical | 30/min |
| **USERS** |
| 18 | `/api/v1/users/me` | GET | ✅ Yes | Any | 🟢 Low | 300/min |
| 19 | `/api/v1/users/me` | POST | ✅ Yes | Any | 🟡 Medium | 30/min |
| 20 | `/api/v1/users/{id}` | GET | ✅ Yes | Admin | 🟡 Medium | 300/min |
| 21 | `/api/v1/users` | GET | ✅ Yes | Admin | 🟡 Medium | 60/min |
| 22 | `/api/v1/users/{id}/role` | POST | ✅ Yes | System_Admin | 🔴 Critical | 10/min |
| **ORGANIZATIONS** |
| 23 | `/api/v1/organizations` | GET | ✅ Yes | Any | 🟢 Low | 300/min |
| 24 | `/api/v1/organizations` | POST | ✅ Yes | Any | 🟡 Medium | 10/hour |
| 25 | `/api/v1/organizations/{id}` | GET | ✅ Yes | Any | 🟢 Low | 300/min |
| 26 | `/api/v1/organizations/{id}` | POST | ✅ Yes | Org_Admin | 🟡 Medium | 30/min |
| 27 | `/api/v1/organizations/{id}/verify` | POST | ✅ Yes | DM_Authority | 🔴 Critical | 10/min |
| **GEOSPATIAL** |
| 28 | `/api/v1/geo/nearby` | GET | ✅ Yes | Any | 🟢 Low | 300/min |
| 29 | `/api/v1/geo/cluster` | POST | ✅ Yes | Any | 🟢 Low | 60/min |
| 30 | `/api/v1/geo/geojson` | GET | ✅ Yes | Any | 🟢 Low | 300/min |
| 31 | `/api/v1/geo/bbox` | GET | ✅ Yes | Any | 🟢 Low | 300/min |
| **ANALYTICS** |
| 32 | `/api/v1/analytics/dashboard` | GET | ✅ Yes | Volunteer | 🟢 Low | 60/min |
| 33 | `/api/v1/analytics/reports` | GET | ✅ Yes | Event_Manager | 🟡 Medium | 60/min |
| 34 | `/api/v1/analytics/export` | POST | ✅ Yes | DM_Authority | 🔴 Critical | 10/hour |
| **ADMIN** |
| 35 | `/api/v1/admin/users` | GET | ✅ Yes | System_Admin | 🔴 Critical | 60/min |
| 36 | `/api/v1/admin/audit-log` | GET | ✅ Yes | Auditor | 🔴 Critical | 60/min |
| 37 | `/api/v1/admin/system-health` | GET | ✅ Yes | System_Admin | 🔴 Critical | 60/min |

**Total Endpoints**: 37 (updated from 36)

**Security Level Legend:**
- 🔴 **Critical**: Extra security measures required
- 🟡 **Medium**: Standard security measures
- 🟢 **Low**: Basic security measures

---

#### 2.2 HTTP Methods Summary (Updated)

| Method | Count | Purpose | When to Use |
|--------|-------|---------|-------------|
| **GET** | 16 | Retrieve data | Idempotent, read-only, cacheable |
| **POST** | 21 | Create/Action | Non-idempotent, state changes, actions |
| **PUT** | 0 | Full replace | ~~Not used~~ (Using POST instead) |
| **PATCH** | 0 | Partial update | ~~Not used~~ (Using POST instead) |
| **DELETE** | 0 | Remove | ~~Not used~~ (Using POST /cancel instead) |
| **TOTAL** | **37** | | |

---

### 3. **HTTP Method Guidelines**

#### 3.1 Why POST Instead of PUT/DELETE?

**Decision: Use POST for ALL state-changing operations**

**Reasoning:**

1. **Simpler CSRF Protection**
   - PUT/DELETE require custom CSRF handling
   - POST works with standard CSRF middleware

2. **Better Action Semantics**
   - `/services/{id}/accept` is an ACTION, not a replacement
   - `/services/{id}/complete` is an ACTION, not a replacement
   - POST clearly indicates "perform this action"

3. **Consistency**
   - All state changes use POST
   - Easier for frontend developers
   - Less confusion about idempotency

4. **Real-World Alignment**
   - "Accept service" is not "update service to accepted"
   - "Complete service" is not "replace service with completed version"
   - These are workflow actions with side effects

**Exception: When to use PUT**
```
Never in IDRM! We use POST for all updates.

Traditional PUT use:
PUT /users/{id} with FULL user object

Why we don't:
- Requires sending entire object
- Partial updates need PATCH
- More complex error handling
- CSRF token complications

Our approach:
POST /users/me with ONLY changed fields
```

---

#### 3.2 Method Selection Guide

```
Need to...                        Use Method...
─────────────────────────────────────────────────
Retrieve data                  → GET
Create new resource            → POST
Update existing resource       → POST (with id)
Perform action/workflow step   → POST (with action verb)
Delete/Cancel resource         → POST /cancel
```

---

### 4. **Authentication Endpoints**

#### 4.1 POST /api/v1/auth/register

**Security Level**: 🔴 Critical

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

**Security Requirements:**
```javascript
✅ MUST validate email format (RFC 5322)
✅ MUST check email uniqueness
✅ MUST validate password strength:
   - Min 8 characters
   - 1 uppercase, 1 lowercase, 1 number
   - 1 special character
✅ MUST hash password with bcrypt (cost 12)
✅ MUST validate phone (10 digits, Indian format)
✅ MUST sanitize all inputs (prevent XSS)
✅ MUST rate limit: 5 registrations per IP per hour
✅ MUST send verification email
✅ MUST NOT allow admin roles via registration
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false,
    "created_at": "2026-05-16T10:00:00Z"
  }
}
```

**⚠️ NEVER return in response:**
- ❌ Password (even hashed!)
- ❌ Password hash
- ❌ Verification tokens
- ❌ Internal IDs

---

#### 4.2 POST /api/v1/auth/login

**Security Level**: 🔴 Critical

**Request**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Security Requirements:**
```javascript
✅ MUST use bcrypt.compare() for password verification
✅ MUST rate limit: 5 attempts per IP per 15 minutes
✅ MUST implement exponential backoff after failures
✅ MUST log failed login attempts
✅ MUST NOT reveal if email exists ("Invalid credentials")
✅ MUST check is_verified before allowing login
✅ MUST create session in Redis
✅ MUST return HTTP-only secure cookies
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "user": {
      "user_id": "uuid-here",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN"
    },
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "expires_in": 900
  }
}
```

**Cookie Setting:**
```http
Set-Cookie: access_token=eyJhbG...; HttpOnly; Secure; SameSite=Strict; Max-Age=900
Set-Cookie: refresh_token=eyJhbG...; HttpOnly; Secure; SameSite=Strict; Max-Age=604800
```

**Failed Login (401)**:
```json
{
  "status": "error",
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Invalid email or password"
  }
}
```

**⚠️ Security Note:** Message is intentionally vague (don't reveal if email exists)

---

#### 4.3 POST /api/v1/auth/logout

**Security Level**: 🟡 Medium

**Request**: No body (token in header/cookie)

**Security Requirements:**
```javascript
✅ MUST invalidate session in Redis
✅ MUST blacklist JWT token until expiry
✅ MUST clear HTTP-only cookies
✅ MUST log logout event
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "Logged out successfully"
}
```

**Cookie Clearing:**
```http
Set-Cookie: access_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0
Set-Cookie: refresh_token=; HttpOnly; Secure; SameSite=Strict; Max-Age=0
```

---

#### 4.4 POST /api/v1/auth/forgot-password

**Security Level**: 🔴 Critical

**Request**:
```json
{
  "email": "user@example.com"
}
```

**Security Requirements:**
```javascript
✅ MUST rate limit: 3 attempts per IP per hour
✅ MUST generate cryptographically secure reset token
✅ MUST store token hash (not plain token!)
✅ MUST set token expiry (15 minutes)
✅ MUST send reset link via email
✅ MUST NOT reveal if email exists (always return success)
✅ MUST log password reset requests
```

**Response** (200 OK):
```json
{
  "status": "success",
  "message": "If that email exists, a reset link has been sent"
}
```

**⚠️ Security Note:** Always return success (timing attacks prevention)

---

### 5. **Service Management Endpoints**

#### 5.1 GET /api/v1/services

**Security Level**: 🟢 Low

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST filter by user role:
   - Citizen: Only own requests
   - Provider: Own + assigned requests
   - Volunteer+: All in area/org
   - Admin: All requests
✅ MUST respect privacy_level:
   - PRIVATE: Only requestor + assigned provider
   - PROTECTED: Hide sensitive fields from public
   - PUBLIC: Show all fields
✅ MUST validate pagination params (max 100 per page)
✅ MUST sanitize all query parameters
```

**Query Parameters:**
```
?service_type=MEDICAL
&priority=CRITICAL
&status=APPROVED
&bbox=78.4,17.3,78.6,17.5  // Bounding box
&page=1
&limit=20
```

**Parameter Validation:**
```javascript
service_type: ENUM validation
priority: ENUM validation
status: ENUM validation
bbox: 4 floats, valid coordinates
page: int, min 1
limit: int, min 1, max 100
```

---

#### 5.2 POST /api/v1/services

**Security Level**: 🟡 Medium

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
  "description": "Urgent medical attention needed",
  "privacy_level": "PROTECTED",
  "metadata": {
    "patient_age": 75,
    "symptoms": ["chest pain", "shortness of breath"]
  }
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST validate service_type (ENUM)
✅ MUST validate priority (ENUM)
✅ MUST validate coordinates (valid lat/lng)
✅ MUST sanitize description (prevent XSS)
✅ MUST validate address format
✅ MUST limit description length (max 2000 chars)
✅ MUST rate limit: 30 requests per user per minute
✅ MUST check user is not spamming (anti-abuse)
✅ MUST validate metadata JSON structure
✅ MUST set requestor_id = authenticated user
```

**Response** (201 Created):
```json
{
  "status": "success",
  "data": {
    "service_id": "uuid-here",
    "status": "SUBMITTED",
    "created_at": "2026-05-16T10:00:00Z",
    "estimated_response_time": "30 minutes"
  }
}
```

---

#### 5.3 POST /api/v1/services/{id} (Update Service)

**Changed from PUT to POST!**

**Security Level**: 🟡 Medium

**Why POST instead of PUT:**
- Not replacing entire resource
- Partial update semantics
- CSRF protection easier
- Action-oriented (updating specific fields)

**Request**:
```json
{
  "priority": "HIGH",
  "description": "Updated description",
  "metadata": {
    "additional_info": "New info"
  }
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify user is requestor (ownership check!)
✅ MUST validate status (can't update if completed)
✅ MUST validate only allowed fields are updated
✅ MUST sanitize all inputs
✅ MUST log update (audit trail)
✅ MUST NOT allow changing:
   - service_id
   - requestor_id
   - created_at
   - assigned_to (use /accept endpoint)
   - status (use action endpoints)
```

**Authorization Check:**
```javascript
// Backend validation
if (service.requestor_id !== auth_user.user_id) {
  return 403 Forbidden
}

if (service.status === 'COMPLETED') {
  return 400 Bad Request ("Cannot modify completed service")
}
```

---

#### 5.4 POST /api/v1/services/{id}/cancel (Delete Alternative)

**Changed from DELETE to POST /cancel!**

**Security Level**: 🟡 Medium

**Why POST /cancel instead of DELETE:**
- Soft delete (preserves data for audit)
- Action semantics (canceling vs deleting)
- Can include cancellation reason
- CSRF protection
- Better for disaster response (maintain records)

**Request**:
```json
{
  "reason": "Situation resolved"
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify user is requestor
✅ MUST validate status (can't cancel if completed)
✅ MUST set status = 'CANCELLED'
✅ MUST NOT actually delete record
✅ MUST notify assigned provider (if any)
✅ MUST log cancellation
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "service_id": "uuid-here",
    "status": "CANCELLED",
    "cancelled_at": "2026-05-16T11:00:00Z"
  }
}
```

---

#### 5.5 POST /api/v1/services/{id}/accept

**Security Level**: 🟡 Medium

**Request**:
```json
{
  "estimated_arrival": "2026-05-16T10:30:00Z",
  "notes": "On my way with medical kit"
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify user role = SERVICE_PROVIDER
✅ MUST verify service status = APPROVED
✅ MUST verify service not already assigned
✅ MUST validate estimated_arrival (future time)
✅ MUST set assigned_to = user_id
✅ MUST set status = ASSIGNED
✅ MUST notify requestor
✅ MUST prevent race conditions (atomic update)
```

**Race Condition Prevention:**
```sql
-- Use SELECT FOR UPDATE
BEGIN;
SELECT * FROM service_requests 
WHERE service_id = $1 AND assigned_to IS NULL
FOR UPDATE;

-- If still unassigned, assign
UPDATE service_requests 
SET assigned_to = $2, status = 'ASSIGNED'
WHERE service_id = $1 AND assigned_to IS NULL;

COMMIT;
```

---

### 6. **User & Organization Endpoints**

#### 6.1 GET /api/v1/users/me

**Security Level**: 🟢 Low

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST return only authenticated user's data
✅ MUST NOT return password_hash
✅ MUST NOT return internal tokens
```

**Response** (200 OK):
```json
{
  "status": "success",
  "data": {
    "user_id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "9876543210",
    "role": "CITIZEN",
    "organization_id": null,
    "is_verified": true,
    "created_at": "2026-05-01T10:00:00Z",
    "profile_picture_url": "https://cdn.idrm.gov.in/avatars/uuid.jpg"
  }
}
```

**⚠️ NEVER include in response:**
- ❌ password_hash
- ❌ reset_tokens
- ❌ verification_tokens
- ❌ session_keys

---

#### 6.2 POST /api/v1/users/me (Update Profile)

**Changed from PUT to POST!**

**Security Level**: 🟡 Medium

**Request**:
```json
{
  "full_name": "John Michael Doe",
  "phone": "9876543211",
  "profile_picture_url": "https://cdn.idrm.gov.in/avatars/new.jpg"
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST validate full_name (max 100 chars, no special chars)
✅ MUST validate phone (10 digits)
✅ MUST validate profile_picture_url (HTTPS, whitelisted domain)
✅ MUST sanitize all inputs
✅ MUST NOT allow changing:
   - user_id
   - email (use separate endpoint)
   - role (admin only)
   - password (use separate endpoint)
   - created_at
```

**Validation Example:**
```python
## Whitelist allowed fields
ALLOWED_UPDATE_FIELDS = ['full_name', 'phone', 'profile_picture_url']

for field in request_data.keys():
    if field not in ALLOWED_UPDATE_FIELDS:
        return 400 Bad Request (f"Cannot update field: {field}")
```

---

#### 6.3 POST /api/v1/users/{id}/role

**Changed from PUT to POST!**

**Security Level**: 🔴 Critical

**Request**:
```json
{
  "new_role": "EVENT_MANAGER",
  "reason": "Appointed as district coordinator"
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify user role = SYSTEM_ADMIN
✅ MUST validate new_role (ENUM)
✅ MUST NOT allow downgrading SYSTEM_ADMIN
✅ MUST require reason (audit trail)
✅ MUST log role change with admin_id
✅ MUST notify user of role change
✅ MUST invalidate old sessions
```

**Authorization Check:**
```javascript
if (auth_user.role !== 'SYSTEM_ADMIN') {
  return 403 Forbidden
}

if (target_user.role === 'SYSTEM_ADMIN' && new_role !== 'SYSTEM_ADMIN') {
  return 400 Bad Request ("Cannot downgrade SYSTEM_ADMIN")
}
```

---

### 7. **Geospatial Endpoints**

#### 7.1 GET /api/v1/geo/nearby

**Security Level**: 🟢 Low

**Query Parameters:**
```
?latitude=17.3850
&longitude=78.4867
&radius=5000
&service_type=MEDICAL
&priority=CRITICAL
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST validate coordinates (-90 to 90 lat, -180 to 180 lng)
✅ MUST validate radius (max 50000 meters = 50km)
✅ MUST sanitize service_type
✅ MUST respect privacy_level
✅ MUST apply RBAC filtering
✅ MUST cache results (Redis, 5 min TTL)
```

**Parameter Validation:**
```javascript
if (latitude < -90 || latitude > 90) {
  return 400 Bad Request ("Invalid latitude")
}

if (longitude < -180 || longitude > 180) {
  return 400 Bad Request ("Invalid longitude")
}

if (radius > 50000) {
  return 400 Bad Request ("Radius too large (max 50km)")
}
```

---

#### 7.2 POST /api/v1/geo/cluster

**Why POST:** Clustering computation can be resource-intensive, uses request body for complex parameters

**Security Level**: 🟢 Low

**Request**:
```json
{
  "bbox": [78.4, 17.3, 78.6, 17.5],
  "cluster_count": 5,
  "service_types": ["MEDICAL", "FOOD"]
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST validate bbox (4 floats)
✅ MUST validate cluster_count (1-20)
✅ MUST validate service_types (ENUM array)
✅ MUST rate limit (expensive operation!)
✅ MUST cache results (Redis, 10 min TTL)
```

---

### 8. **Analytics & Reporting Endpoints**

#### 8.1 GET /api/v1/analytics/dashboard

**Security Level**: 🟢 Low

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify role >= VOLUNTEER
✅ MUST filter by user's permissions:
   - Volunteer: Own area only
   - Event_Manager: Event scope
   - DM_Authority+: District/State
   - System_Admin: All
✅ MUST cache results (Redis, 5 min TTL)
```

---

#### 8.2 POST /api/v1/analytics/export

**Security Level**: 🔴 Critical

**Request**:
```json
{
  "format": "CSV",
  "date_range": {
    "start": "2026-05-01",
    "end": "2026-05-16"
  },
  "filters": {
    "service_types": ["MEDICAL", "FOOD"],
    "priorities": ["CRITICAL", "HIGH"]
  }
}
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify role >= DM_AUTHORITY
✅ MUST validate date_range (max 90 days)
✅ MUST sanitize all filters
✅ MUST redact sensitive fields (PII)
✅ MUST log export (audit trail)
✅ MUST rate limit: 10 exports per user per hour
✅ MUST scan for data exfiltration patterns
```

**Data Redaction:**
```javascript
// Always redact in exports
REDACT_FIELDS = [
  'email', 
  'phone', 
  'exact_address',  // Use approximate instead
  'metadata'        // May contain PII
]
```

---

### 9. **Admin Endpoints**

#### 9.1 GET /api/v1/admin/audit-log

**Security Level**: 🔴 Critical

**Query Parameters:**
```
?user_id=uuid-here
&action=LOGIN
&start_date=2026-05-01
&end_date=2026-05-16
&page=1
&limit=50
```

**Security Requirements:**
```javascript
✅ MUST authenticate user
✅ MUST verify role = AUDITOR or SYSTEM_ADMIN
✅ MUST validate all parameters
✅ MUST paginate results (max 100 per page)
✅ MUST log audit log access (meta-audit!)
✅ MUST NOT allow deleting/modifying logs
```

**Audit Log Entry Format:**
```json
{
  "log_id": "uuid",
  "timestamp": "2026-05-16T10:00:00Z",
  "user_id": "uuid",
  "action": "LOGIN_SUCCESS",
  "ip_address": "203.0.113.1",
  "user_agent": "Mozilla/5.0...",
  "details": {
    "endpoint": "/api/v1/auth/login",
    "status_code": 200
  }
}
```

---

### 10. **Security Checklist**

#### 10.1 Pre-Deployment Security Checklist

**Authentication & Authorization:**
- [ ] All passwords hashed with bcrypt (cost >= 12)
- [ ] JWT tokens expire appropriately (15 min access, 7 day refresh)
- [ ] All endpoints check authorization (not just authentication!)
- [ ] Ownership verified for user-scoped resources
- [ ] Failed logins rate limited (5 per 15 min)

**Input Validation:**
- [ ] All inputs validated (type, length, format)
- [ ] Enum values validated against whitelist
- [ ] Coordinates validated (lat -90 to 90, lng -180 to 180)
- [ ] File uploads validated (type, size, virus scan)
- [ ] JSON structure validated
- [ ] SQL injection prevented (parameterized queries)

**Output Security:**
- [ ] All outputs sanitized (XSS prevention)
- [ ] Passwords NEVER in responses
- [ ] PII redacted based on privacy level
- [ ] Error messages don't leak info
- [ ] Stack traces disabled in production

**Transport Security:**
- [ ] HTTPS enforced (HTTP 301 redirect)
- [ ] TLS 1.2+ required
- [ ] HSTS header set
- [ ] Secure cookies (HttpOnly, Secure, SameSite)

**Rate Limiting:**
- [ ] Auth endpoints: 5/15min
- [ ] Public GET: 60/min
- [ ] Authenticated GET: 300/min
- [ ] POST/PUT/DELETE: 30/min
- [ ] Export: 10/hour

**Security Headers:**
- [ ] Content-Security-Policy
- [ ] X-Frame-Options: DENY
- [ ] X-Content-Type-Options: nosniff
- [ ] Strict-Transport-Security
- [ ] X-XSS-Protection: 1; mode=block

**Logging & Monitoring:**
- [ ] All auth failures logged
- [ ] All admin actions logged
- [ ] All data exports logged
- [ ] Suspicious patterns detected
- [ ] Alerts configured

**CSRF Protection:**
- [ ] CSRF tokens on all POST requests
- [ ] SameSite cookies configured
- [ ] Origin validation

---

### 🎯 **Summary of Changes**

#### **HTTP Methods:**
- ✅ Changed all PUT to POST (simpler, better semantics)
- ✅ Changed DELETE to POST /cancel (soft delete)
- ✅ All state changes now use POST

#### **Security Enhancements:**
- ✅ Added security level to every endpoint
- ✅ Added rate limiting recommendations
- ✅ Added input validation requirements
- ✅ Added CSRF protection requirements
- ✅ Added data redaction guidelines
- ✅ Added audit logging requirements

#### **New Endpoints:**
- ✅ /api/v1/auth/reset-password
- ✅ /api/v1/services/{id}/cancel

#### **Documentation:**
- ✅ Security requirements for every endpoint
- ✅ Validation rules specified
- ✅ Authorization checks documented
- ✅ Common mistakes highlighted
- ✅ Pre-deployment checklist added

---

**Document Version**: 3.1 Security-Hardened  
**Security Review Date**: May 16, 2026  
**Next Review**: Before production deployment  
**Status**: ✅ Ready for implementation

**See Also:**
- [41-CODE-STANDARDS.md](41-CODE-STANDARDS.md) - Secure coding practices
- [42-VERIFICATION-CHECKLISTS.md](42-VERIFICATION-CHECKLISTS.md) - Security testing
- [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md) - Production security config

---

## IDRM v3 - API Integration Guide

### Complete API Reference for All Three Frontend Platforms

**Version**: 3.0  
**Last Updated**: May 24, 2026  
**For**: HTML/Tailwind, React SPA, React Native frontends  
**Architecture**: Bun API Gateway + Python Backend Services

---

### 📋 Table of Contents

1. [API Architecture](#1-api-architecture)
2. [Base Configuration](#2-base-configuration)
3. [Authentication APIs](#3-authentication-apis)
4. [Service Request APIs](#4-service-request-apis)
5. [Geospatial APIs](#5-geospatial-apis)
6. [User & Organization APIs](#6-user--organization-apis)
7. [Analytics APIs](#7-analytics-apis)
8. [Notification APIs](#8-notification-apis)
9. [WebSocket Real-time](#9-websocket-real-time)
10. [Error Handling](#10-error-handling)
11. [Platform-Specific Examples](#11-platform-specific-examples)

---

### 1. API Architecture

#### 1.1 v3 Architecture Overview

```
┌─────────────────────────────────────────────┐
│  Three Frontend Platforms                   │
│  ├─ HTML/Tailwind (Port 5173)              │
│  ├─ React SPA (Port 5174)                  │
│  └─ React Native (Expo)                    │
└─────────────────┬───────────────────────────┘
                  ↓ HTTPS/WSS
        ┌─────────────────────┐
        │  Bun API Gateway    │
        │  (Port 3000)        │
        │  - Routing          │
        │  - WebSocket        │
        │  - Rate Limiting    │
        └──────────┬──────────┘
                   ↓
        ┌──────────────────────────────────┐
        │  Python Backend Services         │
        │  ├─ Auth (8000)                  │
        │  ├─ Services (8001)              │
        │  ├─ Geospatial (8002)            │
        │  ├─ Analytics (8003)             │
        │  └─ Notifications (8004)         │
        └──────────┬───────────────────────┘
                   ↓
        ┌──────────────────────┐
        │  Data Layer          │
        │  ├─ PostgreSQL 16    │
        │  │  + PostGIS 3.4    │
        │  └─ Redis 7.2+       │
        └──────────────────────┘
```

#### 1.2 Base URLs

**Development**:
- API Gateway: `http://localhost:3000/api/v1`
- WebSocket: `ws://localhost:3001`

**Staging**:
- API Gateway: `https://staging.idrm.gov.in/api/v1`
- WebSocket: `wss://staging.idrm.gov.in/ws`

**Production**:
- API Gateway: `https://api.idrm.gov.in/api/v1`
- WebSocket: `wss://api.idrm.gov.in/ws`

#### 1.3 API Versioning

All endpoints use `/api/v1/` prefix. Future versions will use `/api/v2/`, etc.

---

### 2. Base Configuration

#### 2.1 HTML/Tailwind Configuration

**File**: `frontend/html-tailwind/src/js/api.js`

```javascript
/**
 * IDRM v3 API Client
 * Vanilla JavaScript - Works in all browsers
 */

const CONFIG = {
    development: {
        apiUrl: 'http://localhost:3000/api/v1',
        wsUrl: 'ws://localhost:3001'
    },
    staging: {
        apiUrl: 'https://staging.idrm.gov.in/api/v1',
        wsUrl: 'wss://staging.idrm.gov.in/ws'
    },
    production: {
        apiUrl: 'https://api.idrm.gov.in/api/v1',
        wsUrl: 'wss://api.idrm.gov.in/ws'
    }
};

const ENV = 'development'; // Change based on environment
const API_BASE = CONFIG[ENV].apiUrl;
const WS_BASE = CONFIG[ENV].wsUrl;

class APIClient {
    constructor() {
        this.baseURL = API_BASE;
        this.wsURL = WS_BASE;
    }

    // Get token from localStorage
    getToken() {
        return localStorage.getItem('access_token');
    }

    // Set authorization header
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        
        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        
        return headers;
    }

    // Generic API call
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        try {
            const response = await fetch(url, config);
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'API Error');
            }
            
            return await response.json();
        } catch (error) {
            console.error('API Request Failed:', error);
            throw error;
        }
    }

    // HTTP Methods
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
}

// Export singleton instance
const api = new APIClient();
```

#### 2.2 React SPA Configuration

**File**: `frontend/react-spa/src/lib/api.ts`

```typescript
/**
 * IDRM v3 API Client for React
 * TypeScript with type safety
 */

interface Config {
    apiUrl: string;
    wsUrl: string;
}

const config: Record<string, Config> = {
    development: {
        apiUrl: 'http://localhost:3000/api/v1',
        wsUrl: 'ws://localhost:3001'
    },
    staging: {
        apiUrl: 'https://staging.idrm.gov.in/api/v1',
        wsUrl: 'wss://staging.idrm.gov.in/ws'
    },
    production: {
        apiUrl: 'https://api.idrm.gov.in/api/v1',
        wsUrl: 'wss://api.idrm.gov.in/ws'
    }
};

const ENV = process.env.NODE_ENV || 'development';
const { apiUrl, wsUrl } = config[ENV];

class APIClient {
    private baseURL: string;
    private wsURL: string;

    constructor() {
        this.baseURL = apiUrl;
        this.wsURL = wsUrl;
    }

    private getToken(): string | null {
        return localStorage.getItem('access_token');
    }

    private getHeaders(): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json'
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;
        const config: RequestInit = {
            ...options,
            headers: {
                ...this.getHeaders(),
                ...options.headers
            }
        };

        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }

        return response.json();
    }

    async get<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET' });
    }

    async post<T>(endpoint: string, data: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put<T>(endpoint: string, data: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' });
    }
}

export const api = new APIClient();
export default api;
```

#### 2.3 React Native Configuration

**File**: `mobile/src/lib/api.ts`

```typescript
/**
 * IDRM v3 API Client for React Native
 * Works with Expo
 */

import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// For Android emulator, use 10.0.2.2 instead of localhost
const getLocalIP = () => {
    if (Platform.OS === 'android') {
        return '10.0.2.2';
    }
    return 'localhost';
};

const config = {
    development: {
        apiUrl: `http://${getLocalIP()}:3000/api/v1`,
        wsUrl: `ws://${getLocalIP()}:3001`
    },
    staging: {
        apiUrl: 'https://staging.idrm.gov.in/api/v1',
        wsUrl: 'wss://staging.idrm.gov.in/ws'
    },
    production: {
        apiUrl: 'https://api.idrm.gov.in/api/v1',
        wsUrl: 'wss://api.idrm.gov.in/ws'
    }
};

const ENV = __DEV__ ? 'development' : 'production';
const { apiUrl, wsUrl } = config[ENV];

class APIClient {
    private baseURL: string;
    private wsURL: string;

    constructor() {
        this.baseURL = apiUrl;
        this.wsURL = wsUrl;
    }

    private async getToken(): Promise<string | null> {
        return AsyncStorage.getItem('access_token');
    }

    private async getHeaders(): Promise<HeadersInit> {
        const headers: HeadersInit = {
            'Content-Type': 'application/json'
        };

        const token = await this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        return headers;
    }

    async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
        const url = `${this.baseURL}${endpoint}`;
        const headers = await this.getHeaders();
        
        const config: RequestInit = {
            ...options,
            headers: {
                ...headers,
                ...options.headers
            }
        };

        const response = await fetch(url, config);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }

        return response.json();
    }

    async get<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'GET' });
    }

    async post<T>(endpoint: string, data: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put<T>(endpoint: string, data: unknown): Promise<T> {
        return this.request<T>(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete<T>(endpoint: string): Promise<T> {
        return this.request<T>(endpoint, { method: 'DELETE' });
    }
}

export const api = new APIClient();
export default api;
```

---

### 3. Authentication APIs

#### 3.1 User Registration

**Endpoint**: `POST /auth/register`

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "phone": "+919876543210",
    "role": "citizen",
    "language_preference": "en"
}
```

**Response** (201 Created):
```json
{
    "id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "citizen",
    "created_at": "2026-05-24T10:30:00Z"
}
```

**Example (HTML/Tailwind)**:
```javascript
async function register(email, password, fullName, phone) {
    try {
        const user = await api.post('/auth/register', {
            email,
            password,
            full_name: fullName,
            phone,
            role: 'citizen',
            language_preference: 'en'
        });
        
        console.log('Registration successful:', user);
        return user;
    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
}
```

#### 3.2 User Login

**Endpoint**: `POST /auth/login`

**Request Body**:
```json
{
    "email": "user@example.com",
    "password": "SecurePass123!"
}
```

**Response** (200 OK):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 1800,
    "user": {
        "id": "uuid-here",
        "email": "user@example.com",
        "full_name": "John Doe",
        "role": "citizen"
    }
}
```

**Example (React)**:
```typescript
async function login(email: string, password: string) {
    try {
        const response = await api.post<LoginResponse>('/auth/login', {
            email,
            password
        });
        
        // Store tokens
        localStorage.setItem('access_token', response.access_token);
        localStorage.setItem('refresh_token', response.refresh_token);
        localStorage.setItem('user', JSON.stringify(response.user));
        
        return response;
    } catch (error) {
        console.error('Login failed:', error);
        throw error;
    }
}
```

#### 3.3 Token Refresh

**Endpoint**: `POST /auth/refresh`

**Request Body**:
```json
{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 1800
}
```

#### 3.4 Logout

**Endpoint**: `POST /auth/logout`

**Request Headers**: `Authorization: Bearer <access_token>`

**Response** (204 No Content)

---

### 4. Service Request APIs

#### 4.1 Create Service Request

**Endpoint**: `POST /services/requests`

**Request Body**:
```json
{
    "service_type": "medical",
    "description": "Need ambulance urgently",
    "priority": "critical",
    "location": {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "address": "Anna Nagar, Chennai"
    },
    "privacy_level": "public",
    "contact_phone": "+919876543210"
}
```

**Response** (201 Created):
```json
{
    "id": "uuid-here",
    "service_type": "medical",
    "description": "Need ambulance urgently",
    "priority": "critical",
    "status": "pending",
    "location": {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "address": "Anna Nagar, Chennai"
    },
    "created_by": "uuid-user",
    "created_at": "2026-05-24T10:30:00Z",
    "updated_at": "2026-05-24T10:30:00Z"
}
```

**Example (React Native)**:
```typescript
async function createServiceRequest(data: ServiceRequestData) {
    try {
        const request = await api.post<ServiceRequest>('/services/requests', {
            service_type: data.serviceType,
            description: data.description,
            priority: data.priority,
            location: {
                latitude: data.location.latitude,
                longitude: data.location.longitude,
                address: data.location.address
            },
            privacy_level: 'public',
            contact_phone: data.phone
        });
        
        console.log('Request created:', request);
        return request;
    } catch (error) {
        console.error('Failed to create request:', error);
        throw error;
    }
}
```

#### 4.2 List Service Requests

**Endpoint**: `GET /services/requests`

**Query Parameters**:
- `status` (optional): pending, assigned, in_progress, completed, cancelled
- `service_type` (optional): medical, food, water, shelter
- `priority` (optional): low, medium, high, critical
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Example Request**: `GET /services/requests?status=pending&service_type=medical&page=1`

**Response** (200 OK):
```json
{
    "items": [
        {
            "id": "uuid-1",
            "service_type": "medical",
            "description": "Need ambulance",
            "status": "pending",
            "priority": "critical",
            "location": {
                "latitude": 13.0827,
                "longitude": 80.2707
            },
            "created_at": "2026-05-24T10:30:00Z"
        }
    ],
    "total": 45,
    "page": 1,
    "per_page": 20,
    "pages": 3
}
```

#### 4.3 Get Single Request

**Endpoint**: `GET /services/requests/{id}`

**Response** (200 OK):
```json
{
    "id": "uuid-here",
    "service_type": "medical",
    "description": "Need ambulance urgently",
    "priority": "critical",
    "status": "pending",
    "location": {
        "latitude": 13.0827,
        "longitude": 80.2707,
        "address": "Anna Nagar, Chennai"
    },
    "created_by": {
        "id": "uuid-user",
        "full_name": "John Doe",
        "phone": "+919876543210"
    },
    "assigned_to": null,
    "created_at": "2026-05-24T10:30:00Z",
    "updated_at": "2026-05-24T10:30:00Z"
}
```

#### 4.4 Update Request Status

**Endpoint**: `PUT /services/requests/{id}/status`

**Request Body**:
```json
{
    "status": "in_progress",
    "notes": "Provider dispatched"
}
```

**Response** (200 OK):
```json
{
    "id": "uuid-here",
    "status": "in_progress",
    "updated_at": "2026-05-24T11:00:00Z"
}
```

---

### 5. Geospatial APIs

#### 5.1 Nearby Requests

**Endpoint**: `GET /geo/nearby`

**Query Parameters**:
- `latitude` (required): Center point latitude
- `longitude` (required): Center point longitude
- `radius` (optional): Radius in kilometers (default: 5, max: 50)
- `service_type` (optional): Filter by service type

**Example**: `GET /geo/nearby?latitude=13.0827&longitude=80.2707&radius=10`

**Response** (200 OK):
```json
{
    "center": {
        "latitude": 13.0827,
        "longitude": 80.2707
    },
    "radius_km": 10,
    "results": [
        {
            "id": "uuid-1",
            "service_type": "medical",
            "location": {
                "latitude": 13.0856,
                "longitude": 80.2731
            },
            "distance_km": 0.35,
            "priority": "critical",
            "status": "pending"
        }
    ],
    "total": 12
}
```

**Example (HTML/Tailwind)**:
```javascript
async function findNearbyRequests(lat, lng, radius = 5) {
    try {
        const data = await api.get(
            `/geo/nearby?latitude=${lat}&longitude=${lng}&radius=${radius}`
        );
        
        // Display on map
        data.results.forEach(request => {
            addMarkerToMap(request);
        });
        
        return data;
    } catch (error) {
        console.error('Failed to fetch nearby requests:', error);
        throw error;
    }
}
```

#### 5.2 Cluster Markers

**Endpoint**: `GET /geo/cluster`

**Query Parameters**:
- `zoom` (required): Map zoom level (1-20)
- `bounds` (optional): Map bounds (south,west,north,east)

**Response** (200 OK):
```json
{
    "clusters": [
        {
            "latitude": 13.0827,
            "longitude": 80.2707,
            "count": 15,
            "priority_breakdown": {
                "critical": 5,
                "high": 7,
                "medium": 3
            }
        }
    ]
}
```

---

### 6. User & Organization APIs

#### 6.1 Get Current User

**Endpoint**: `GET /users/me`

**Response** (200 OK):
```json
{
    "id": "uuid-here",
    "email": "user@example.com",
    "full_name": "John Doe",
    "phone": "+919876543210",
    "role": "citizen",
    "language_preference": "en",
    "created_at": "2026-01-15T10:00:00Z"
}
```

#### 6.2 Update User Profile

**Endpoint**: `PUT /users/me`

**Request Body**:
```json
{
    "full_name": "John Updated Doe",
    "phone": "+919876543210",
    "language_preference": "hi"
}
```

---

### 7. Analytics APIs

#### 7.1 Dashboard Statistics

**Endpoint**: `GET /analytics/dashboard`

**Response** (200 OK):
```json
{
    "total_requests": 1250,
    "pending_requests": 45,
    "active_providers": 120,
    "requests_by_type": {
        "medical": 450,
        "food": 380,
        "water": 220,
        "shelter": 200
    },
    "requests_by_status": {
        "pending": 45,
        "assigned": 30,
        "in_progress": 25,
        "completed": 1150
    }
}
```

---

### 8. Notification APIs

#### 8.1 Get Notifications

**Endpoint**: `GET /notifications`

**Response** (200 OK):
```json
{
    "items": [
        {
            "id": "uuid-notif",
            "type": "request_assigned",
            "title": "Request Assigned",
            "message": "Your request has been assigned to Red Cross",
            "read": false,
            "created_at": "2026-05-24T10:30:00Z"
        }
    ],
    "unread_count": 5
}
```

#### 8.2 Mark as Read

**Endpoint**: `PUT /notifications/{id}/read`

**Response** (200 OK)

---

### 9. WebSocket Real-time

#### 9.1 Connect to WebSocket

**URL**: `ws://localhost:3001` (or wss:// for production)

**Example (HTML/Tailwind)**:
```javascript
let ws;

function connectWebSocket() {
    ws = new WebSocket('ws://localhost:3001');
    
    ws.onopen = () => {
        console.log('WebSocket connected');
        
        // Subscribe to updates
        ws.send(JSON.stringify({
            type: 'subscribe',
            channel: 'service_requests'
        }));
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        switch (data.type) {
            case 'request_created':
                addMarkerToMap(data.request);
                break;
            case 'request_updated':
                updateMarker(data.request);
                break;
            case 'request_deleted':
                removeMarker(data.request.id);
                break;
        }
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
    
    ws.onclose = () => {
        console.log('WebSocket closed, reconnecting...');
        setTimeout(connectWebSocket, 5000);
    };
}
```

---

### 10. Error Handling

#### 10.1 Standard Error Format

All errors return:
```json
{
    "detail": "Error message",
    "code": "ERROR_CODE",
    "field": "field_name"
}
```

#### 10.2 Common HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid input
- `401 Unauthorized`: Not authenticated
- `403 Forbidden`: Authenticated but not authorized
- `404 Not Found`: Resource doesn't exist
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

#### 10.3 Error Handling Example

```javascript
async function handleAPICall() {
    try {
        const data = await api.get('/services/requests');
        return data;
    } catch (error) {
        if (error.message.includes('401')) {
            // Token expired, refresh
            await refreshToken();
            return handleAPICall(); // Retry
        } else if (error.message.includes('403')) {
            // Not authorized
            alert('You do not have permission');
        } else if (error.message.includes('404')) {
            // Not found
            alert('Resource not found');
        } else {
            // Generic error
            alert('An error occurred: ' + error.message);
        }
        throw error;
    }
}
```

---

### 11. Platform-Specific Examples

#### 11.1 Complete HTML/Tailwind Example

**File**: `frontend/html-tailwind/src/js/requests.js`

```javascript
// Create a new service request
async function submitRequest(formData) {
    const submitBtn = document.getElementById('submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Creating...';
    
    try {
        const request = await api.post('/services/requests', {
            service_type: formData.get('service_type'),
            description: formData.get('description'),
            priority: formData.get('priority'),
            location: {
                latitude: parseFloat(formData.get('latitude')),
                longitude: parseFloat(formData.get('longitude')),
                address: formData.get('address')
            },
            privacy_level: 'public',
            contact_phone: formData.get('phone')
        });
        
        alert('Request created successfully!');
        window.location.href = '/dashboard.html';
        
    } catch (error) {
        alert('Failed to create request: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit Request';
    }
}
```

#### 11.2 Complete React Example

**File**: `frontend/react-spa/src/hooks/useServiceRequests.ts`

```typescript
import { useState, useEffect } from 'react';
import api from '../lib/api';

interface ServiceRequest {
    id: string;
    service_type: string;
    description: string;
    status: string;
    priority: string;
    location: {
        latitude: number;
        longitude: number;
    };
}

export function useServiceRequests() {
    const [requests, setRequests] = useState<ServiceRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadRequests();
    }, []);

    async function loadRequests() {
        try {
            setLoading(true);
            const data = await api.get<{ items: ServiceRequest[] }>(
                '/services/requests'
            );
            setRequests(data.items);
            setError(null);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }

    async function createRequest(data: Partial<ServiceRequest>) {
        const request = await api.post<ServiceRequest>('/services/requests', data);
        setRequests(prev => [request, ...prev]);
        return request;
    }

    return {
        requests,
        loading,
        error,
        createRequest,
        reload: loadRequests
    };
}
```

#### 11.3 Complete React Native Example

**File**: `mobile/src/hooks/useServiceRequests.ts`

```typescript
import { useState, useEffect } from 'react';
import api from '../lib/api';
import * as Location from 'expo-location';

export function useServiceRequests() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadNearbyRequests();
    }, []);

    async function loadNearbyRequests() {
        try {
            // Get user location
            const { status } = await Location.requestForegroundPermissionsAsync();
            if (status !== 'granted') {
                throw new Error('Location permission denied');
            }

            const location = await Location.getCurrentPositionAsync({});
            
            // Fetch nearby requests
            const data = await api.get(
                `/geo/nearby?latitude=${location.coords.latitude}&longitude=${location.coords.longitude}&radius=10`
            );
            
            setRequests(data.results);
        } catch (error) {
            console.error('Failed to load nearby requests:', error);
        } finally {
            setLoading(false);
        }
    }

    async function createRequest(data: any) {
        // Get current location
        const location = await Location.getCurrentPositionAsync({});
        
        const request = await api.post('/services/requests', {
            ...data,
            location: {
                latitude: location.coords.latitude,
                longitude: location.coords.longitude
            }
        });
        
        setRequests(prev => [request, ...prev]);
        return request;
    }

    return {
        requests,
        loading,
        createRequest,
        reload: loadNearbyRequests
    };
}
```

---

**IDRM v3 API Guide: Complete Reference for All Three Platforms!** 🚀

**Platforms Covered**: HTML/Tailwind, React SPA, React Native  
**Architecture**: Bun API Gateway + Python Backend  
**Real-time**: WebSocket support  
**Type-Safe**: TypeScript examples included
