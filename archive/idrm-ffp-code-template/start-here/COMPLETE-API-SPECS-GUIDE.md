# IDRM Complete API Specs Guide

## All 37 Endpoints with Security, RBAC, and JSON Formats

**Version**: 3.1 Security-Hardened
**Base URL**: `https://idrm.gov.in/api/v1` (production) · `http://localhost:3000/api/v1` (dev)
**Protocol**: HTTPS only · Format: JSON · Auth: JWT Bearer
**Sources**: `44-API-REFERENCE-MATRIX-v3.1-SECURITY.md` + `API-CONTRACTS-v3.md`

---

## Table of Contents

1. [Global Specifications](#1-global-specifications)
2. [Security Requirements](#2-security-requirements)
3. [All Endpoints Quick Reference](#3-all-endpoints-quick-reference)
4. [Authentication Endpoints](#4-authentication-endpoints)
5. [Service Management Endpoints](#5-service-management-endpoints)
6. [User &amp; Organization Endpoints](#6-user--organization-endpoints)
7. [Geospatial Endpoints](#7-geospatial-endpoints)
8. [Analytics Endpoints](#8-analytics-endpoints)
9. [Admin Endpoints](#9-admin-endpoints)
10. [Error Responses](#10-error-responses)
11. [WebSocket Events](#11-websocket-events)
12. [Pre-Deployment Security Checklist](#12-pre-deployment-security-checklist)

---

## 1. Global Specifications

```yaml
Base URL (dev):   http://localhost:3000/api/v1
Base URL (prod):  https://idrm.gov.in/api/v1
Protocol:         HTTPS only (HTTP 301 → HTTPS)
Format:           JSON
Charset:          UTF-8
Versioning:       URL-based (/v1/, /v2/)
Authentication:   JWT Bearer tokens (15-min access, 7-day refresh)

Common Request Headers:
  Authorization: "Bearer {access_token}"
  Content-Type: "application/json"
  Accept: "application/json"

Common Response Headers:
  Content-Type: "application/json"
  X-RateLimit-Limit: "{limit}"
  X-RateLimit-Remaining: "{remaining}"
  X-RateLimit-Reset: "{unix_timestamp}"
```

### HTTP Method Policy

**IDRM uses only GET and POST — no PUT, PATCH, or DELETE.**

| Action          | Method              | Example                        |
| --------------- | ------------------- | ------------------------------ |
| Retrieve data   | GET                 | `GET /services`              |
| Create resource | POST                | `POST /services`             |
| Update resource | POST (with id)      | `POST /services/{id}`        |
| Perform action  | POST (with verb)    | `POST /services/{id}/accept` |
| Cancel/Delete   | POST (with /cancel) | `POST /services/{id}/cancel` |

Rationale: Simplifies CSRF protection and makes workflow actions explicit.

### API Versioning Policy

IDRM uses URL-based versioning (`/api/v1/`, `/api/v2/`). All current endpoints are `/api/v1/`.

**Breaking vs. non-breaking changes:**

| Change type                  | Version impact                             |
| ---------------------------- | ------------------------------------------ |
| Remove or rename a field     | **Breaking** — requires new version |
| Change field type            | **Breaking** — requires new version |
| Change required parameters   | **Breaking** — requires new version |
| Change authentication method | **Breaking** — requires new version |
| Add optional field           | Non-breaking — same version               |
| Add new endpoint             | Non-breaking — same version               |
| Add optional query param     | Non-breaking — same version               |
| Performance improvements     | Non-breaking — same version               |

**Deprecation lifecycle (when v2 is eventually released):**

1. v2 released → v1 marked deprecated in docs
2. After 6 months → v1 responses include warning headers:
   ```
   API-Deprecation: true
   API-Sunset: 2028-05-01
   Link: <https://docs.idrm.gov.in/api/v2>; rel="alternate"
   ```
3. After 12 months → v1 endpoints return `410 Gone`

`/api/v2/` path is reserved but not yet implemented. v1 is supported until at least May 2028.

---

## 2. Security Requirements

### All Endpoints Must

- Use HTTPS (enforced by NGINX)
- Validate all inputs (type, length, format, content)
- Sanitize all outputs (prevent XSS)
- Use parameterized queries (prevent SQL injection)
- Check **authorization** (role), not just authentication (JWT validity)
- Log security events (failed auth, permission denials)

### Authentication Details

```json
{
  "access_token": "eyJ...",   // 15-minute TTL — stored in httpOnly cookie
  "refresh_token": "eyJ..."   // 7-day TTL — stored in httpOnly cookie
}
```

- Access tokens stored in **httpOnly cookies** — not localStorage (prevents XSS theft)
- Failed login rate limit: **5 attempts per 15 min per IP**
- Logout blacklists JTI in Redis with matching TTL

### Rate Limits by Endpoint Type

| Endpoint Type                   | Limit | Window |
| ------------------------------- | ----- | ------ |
| Authentication (login/register) | 5     | 15 min |
| Public GET                      | 60    | 1 min  |
| Authenticated GET               | 300   | 1 min  |
| POST/state-change               | 30    | 1 min  |
| Export/Analytics                | 10    | 1 hour |

### Role Hierarchy

```
ADMIN > DM_AUTHORITY ≈ AUDITOR > EVENT_MANAGER > EXECUTIVE (🔒 Post-MVP) > MANAGER > PROVIDER > ORGANIZER > VOLUNTEER > CITIZEN > Public
(canonical Permission Matrix: docs/development/IDRM-FS.md §3.3)
```

---

## 3. All Endpoints Quick Reference

| #                        | Endpoint                       | Method | Auth | Min Role      | Security | Rate Limit |
| ------------------------ | ------------------------------ | ------ | ---- | ------------- | -------- | ---------- |
| **Authentication** |                                |        |      |               |          |            |
| 1                        | `/auth/register`             | POST   | No   | Public        | Critical | 5/15min    |
| 2                        | `/auth/login`                | POST   | No   | Public        | Critical | 5/15min    |
| 3                        | `/auth/logout`               | POST   | Yes  | Any           | Medium   | 30/min     |
| 4                        | `/auth/refresh`              | POST   | Yes  | Any           | Critical | 10/min     |
| 5                        | `/auth/verify-email`         | POST   | No   | Public        | Medium   | 5/15min    |
| 6                        | `/auth/forgot-password`      | POST   | No   | Public        | Critical | 3/hour     |
| 7                        | `/auth/reset-password`       | POST   | No   | Public        | Critical | 3/hour     |
| **Services**       |                                |        |      |               |          |            |
| 8                        | `/services`                  | GET    | Yes  | Citizen       | Low      | 300/min    |
| 9                        | `/services`                  | POST   | Yes  | Citizen       | Medium   | 30/min     |
| 10                       | `/services/{id}`             | GET    | Yes  | Citizen       | Medium   | 300/min    |
| 11                       | `/services/{id}`             | POST   | Yes  | Requestor     | Medium   | 30/min     |
| 12                       | `/services/{id}/cancel`      | POST   | Yes  | Requestor     | Medium   | 30/min     |
| 13                       | `/services/{id}/accept`      | POST   | Yes  | Provider      | Medium   | 30/min     |
| 14                       | `/services/{id}/complete`    | POST   | Yes  | Provider      | Medium   | 30/min     |
| 15                       | `/services/{id}/verify`      | POST   | Yes  | Requestor     | Medium   | 30/min     |
| 16                       | `/services/{id}/approve`     | POST   | Yes  | DM_Authority  | Critical | 30/min     |
| 17                       | `/services/{id}/reject`      | POST   | Yes  | DM_Authority  | Critical | 30/min     |
| **Users**          |                                |        |      |               |          |            |
| 18                       | `/users/me`                  | GET    | Yes  | Any           | Low      | 300/min    |
| 19                       | `/users/me`                  | POST   | Yes  | Any           | Medium   | 30/min     |
| 20                       | `/users/{id}`                | GET    | Yes  | Admin         | Medium   | 300/min    |
| 21                       | `/users`                     | GET    | Yes  | Admin         | Medium   | 60/min     |
| 22                       | `/users/{id}/role`           | POST   | Yes  | System_Admin  | Critical | 10/min     |
| **Organizations**  |                                |        |      |               |          |            |
| 23                       | `/organizations`             | GET    | Yes  | Any           | Low      | 300/min    |
| 24                       | `/organizations`             | POST   | Yes  | Any           | Medium   | 10/hour    |
| 25                       | `/organizations/{id}`        | GET    | Yes  | Any           | Low      | 300/min    |
| 26                       | `/organizations/{id}`        | POST   | Yes  | Org_Admin     | Medium   | 30/min     |
| 27                       | `/organizations/{id}/verify` | POST   | Yes  | DM_Authority  | Critical | 10/min     |
| **Geospatial**     |                                |        |      |               |          |            |
| 28                       | `/geo/nearby`                | GET    | Yes  | Any           | Low      | 300/min    |
| 29                       | `/geo/cluster`               | POST   | Yes  | Any           | Low      | 60/min     |
| 30                       | `/geo/geojson`               | GET    | Yes  | Any           | Low      | 300/min    |
| 31                       | `/geo/bbox`                  | GET    | Yes  | Any           | Low      | 300/min    |
| **Analytics**      |                                |        |      |               |          |            |
| 32                       | `/analytics/dashboard`       | GET    | Yes  | Volunteer     | Low      | 60/min     |
| 33                       | `/analytics/reports`         | GET    | Yes  | Event_Manager | Medium   | 60/min     |
| 34                       | `/analytics/export`          | POST   | Yes  | DM_Authority  | Critical | 10/hour    |
| **Admin**          |                                |        |      |               |          |            |
| 35                       | `/admin/users`               | GET    | Yes  | System_Admin  | Critical | 60/min     |
| 36                       | `/admin/audit-log`           | GET    | Yes  | Auditor       | Critical | 60/min     |
| 37                       | `/admin/system-health`       | GET    | Yes  | System_Admin  | Critical | 60/min     |

---

## 4. Authentication Endpoints

### POST /auth/register

**Request**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "role": "CITIZEN"
}
```

**Validation rules**:

- Email: RFC 5322 format, unique
- Password: min 8 chars, 1 uppercase + 1 lowercase + 1 digit + 1 special
- Role: only `CITIZEN`, `PROVIDER`, `VOLUNTEER` — admin roles NOT allowed via registration
- Rate: 5 registrations per IP per hour

**Response** (201):

```json
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false,
    "created_at": "2026-05-16T10:00:00Z"
  }
}
```

**Never return**: password, password_hash, verification tokens.

---

### POST /auth/login

**Request**:

```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900,
    "user": {
      "user_id": "550e8400-...",
      "email": "user@example.com",
      "role": "CITIZEN"
    }
  }
}
```

---

### POST /auth/logout

**Request**: `{ "refresh_token": "eyJ..." }`
**Response**: 204 No Content
**Side effect**: Access token JTI blacklisted in Redis; refresh token invalidated.

---

### POST /auth/refresh

**Min role**: Any authenticated | **Security**: Critical | **Rate limit**: 10/min

**Request**:

```json
{ "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." }
```

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 900
  }
}
```

**Security**: Validates refresh token signature and Redis session. Old refresh token is invalidated on reuse (rotation). Returns 401 if refresh token is expired or blacklisted.

---

### POST /auth/verify-email

**Min role**: Public (no auth) | **Security**: Medium | **Rate limit**: 5/15min

**Request**:

```json
{ "token": "verification-token-from-email-link" }
```

**Response** (200):

```json
{
  "status": "success",
  "message": "Email verified successfully. You may now log in."
}
```

**Notes**: Token is single-use and expires in 24 hours. On success, sets `is_verified = true` on the user record.

---

### POST /auth/forgot-password

**Min role**: Public (no auth) | **Security**: Critical | **Rate limit**: 3/hour

**Request**:

```json
{ "email": "user@example.com" }
```

**Response** (200):

```json
{
  "status": "success",
  "message": "If that email exists, a reset link has been sent"
}
```

**Security**: Always returns success regardless of whether the email exists — prevents user enumeration. Reset token is a cryptographically secure random string, stored as a hash in Redis, valid for 15 minutes.

---

### POST /auth/reset-password

**Min role**: Public (no auth) | **Security**: Critical | **Rate limit**: 3/hour

**Request**:

```json
{
  "token": "reset-token-from-email-link",
  "new_password": "NewSecurePass456!"
}
```

**Validation**: Same password strength rules as registration (min 8 chars, 1 uppercase + 1 lowercase + 1 digit + 1 special character).

**Response** (200):

```json
{
  "status": "success",
  "message": "Password reset successfully. Please log in."
}
```

**Security**: Token is single-use and consumed on first use. All existing sessions for this user are purged from Redis after a successful reset.

---

## 5. Service Management Endpoints

### POST /services — Create Request

```json
{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "123 Main St, Hyderabad",
  "description": "Elderly man, 70 years, chest pain, water level 3 feet.",
  "num_people_affected": 1,
  "privacy_level": "PUBLIC",
  "contact_phone": "+919876543210"
}
```

**Service types**: `RESCUE`, `MEDICAL`, `FOOD`, `SHELTER`, `WATER`, `OTHER`
**Priorities**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
**Auto-priority**: RESCUE → CRITICAL, MEDICAL → HIGH, others → MEDIUM
**Rate limit**: 5 requests/day per user (spam prevention)

### GET /services — List (with filters)

```
?status=SUBMITTED,ACCEPTED
?service_type=MEDICAL
?priority=CRITICAL
?lat=17.3850&lon=78.4867&radius_km=10
?page=1&page_size=20
```

### Service Status Workflow

```
SUBMITTED → APPROVED (DM_Authority; auto for emergencies) → ACCEPTED (Provider)
         → IN_PROGRESS → COMPLETED (Provider) → VERIFIED (Requestor)
         → REJECTED (DM_Authority)
         → CANCELLED (Requestor, before acceptance)
         → EXPIRED (system, no action for 48h)
         → DISPUTED (Requestor, from IN_PROGRESS/COMPLETED → reassign or reject)
```

---

### GET /services/ — Get Single Request

**Min role**: Citizen | **Security**: Medium | **Rate limit**: 300/min

**Privacy enforcement**: `PRIVATE` requests are returned in full only to the requestor, assigned provider, and admins. `PROTECTED` requests hide name and phone from public callers.

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "status": "ACCEPTED",
    "location": { "type": "Point", "coordinates": [78.4867, 17.3850] },
    "address": "123 Main St, Hyderabad",
    "description": "Elderly man, chest pain",
    "num_people_affected": 1,
    "privacy_level": "PUBLIC",
    "requestor": { "user_id": "uuid", "full_name": "John Doe" },
    "assigned_to": { "org_id": "uuid", "name": "Red Cross India", "contact_phone": "+911234567890" },
    "created_at": "2026-05-16T10:00:00Z",
    "accepted_at": "2026-05-16T10:15:00Z",
    "completed_at": null,
    "rating": null
  }
}
```

---

### POST /services/ — Update Request

**Min role**: Requestor (own request only) | **Security**: Medium | **Rate limit**: 30/min
**Allowed only when status**: `SUBMITTED` or `APPROVED`

**Request** (include only fields to change):

```json
{
  "priority": "HIGH",
  "description": "Updated: patient condition has stabilised",
  "num_people_affected": 3
}
```

**Forbidden fields** — returning 400 if included: `service_id`, `requestor_id`, `created_at`, `status`, `assigned_to`

---

### POST /services//cancel

**Min role**: Requestor | **Security**: Medium | **Rate limit**: 30/min
**Required status**: `SUBMITTED` or `APPROVED`

**Request**:

```json
{ "reason": "Situation resolved before provider arrived" }
```

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "service_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "CANCELLED",
    "cancelled_at": "2026-05-16T11:00:00Z"
  }
}
```

**Note**: Soft-cancel only — record is preserved for audit trail. If a provider was already assigned, they receive a WebSocket `service.cancelled` event.

---

### POST /services//accept

**Min role**: Provider | **Security**: Medium | **Rate limit**: 30/min
**Required status**: `APPROVED`

**Request**:

```json
{
  "estimated_arrival": "2026-05-16T10:30:00Z",
  "notes": "On my way with medical kit"
}
```

**Backend race condition handling**: Uses `SELECT FOR UPDATE` to prevent two providers accepting simultaneously. Sets `assigned_to`, `status = ACCEPTED`, and notifies the requestor via WebSocket and in-app notification.

---

### POST /services//complete

**Min role**: Provider | **Security**: Medium | **Rate limit**: 30/min
**Required status**: `IN_PROGRESS`

**Request**:

```json
{ "notes": "Treatment administered, patient stable" }
```

Sets `status = COMPLETED`, `completed_at = now()`. Triggers a notification to the requestor asking them to confirm completion.

---

### POST /services//verify

**Min role**: Requestor | **Security**: Medium | **Rate limit**: 30/min
**Required status**: `COMPLETED`

**Request**:

```json
{
  "rating": 5,
  "feedback": "Provider arrived quickly and handled the situation professionally"
}
```

Sets `status = VERIFIED`, stores `rating` (1–5 integer). Rating updates provider and org analytics.

---

### POST /services//approve

**Min role**: DM_Authority | **Security**: Critical | **Rate limit**: 30/min
**Required status**: `SUBMITTED`

**Request**:

```json
{ "notes": "Verified location and priority. Approved for dispatch." }
```

Sets `status = APPROVED`. Broadcasts a WebSocket `service.created` event to providers in the area with matching service types.

---

### POST /services//reject

**Min role**: DM_Authority | **Security**: Critical | **Rate limit**: 30/min
**Required status**: `SUBMITTED`

**Request**:

```json
{ "reason": "Duplicate request — see service #550e8400-e29b-41d4-a716-446655440000" }
```

Sets `status = REJECTED`. Notifies requestor with the rejection reason.

---

## 6. User & Organization Endpoints

### GET /users/me

Returns the authenticated user's profile. No sensitive fields in response.

### POST /users/me — Update Profile

```json
{
  "full_name": "Jane Doe",
  "phone": "+919876543210",
  "preferences": {
    "language": "hi",
    "notifications": { "email": true, "sms": false }
  }
}
```

### POST /organizations — Register Organization

```json
{
  "name": "Red Cross India",
  "org_type": "NGO",
  "service_types": ["MEDICAL", "FOOD"],
  "coverage_area": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "coverage_radius_km": 25,
  "capacity": 50,
  "contact_email": "contact@redcross.in",
  "contact_phone": "+911234567890"
}
```

Org types: `NGO`, `HOSPITAL`, `GOVT_AGENCY`, `VOLUNTEER_GROUP`

---

### GET /users — List All Users (Admin)

**Min role**: Admin | **Security**: Medium | **Rate limit**: 60/min

**Query parameters**:

```
?role=CITIZEN,PROVIDER
?is_active=true
?is_verified=false
?search=john
?page=1&page_size=50
```

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "items": [
      {
        "user_id": "550e8400-...",
        "email": "john@example.com",
        "full_name": "John Doe",
        "role": "CITIZEN",
        "is_active": true,
        "is_verified": true,
        "created_at": "2026-05-01T10:00:00Z"
      }
    ],
    "total": 250,
    "page": 1,
    "page_size": 50,
    "pages": 5
  }
}
```

**Never returned in items**: `password_hash`, reset tokens, session keys.

---

### GET /users/ — Get Any User (Admin)

**Min role**: Admin | **Security**: Medium | **Rate limit**: 300/min

Returns the same structure as `GET /users/me` but for the specified `user_id`. Returns 403 if caller does not have Admin role.

---

### POST /users//role — Change User Role

**Min role**: System_Admin | **Security**: Critical | **Rate limit**: 10/min

**Request**:

```json
{
  "new_role": "EVENT_MANAGER",
  "reason": "Appointed as district coordinator for Chennai flood relief"
}
```

**Guards**:

- Cannot downgrade a `SYSTEM_ADMIN` (returns 400)
- `reason` field is required for audit trail
- Invalidates all existing sessions for the target user after role change

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "user_id": "uuid",
    "old_role": "VOLUNTEER",
    "new_role": "EVENT_MANAGER",
    "changed_by": "admin-uuid",
    "changed_at": "2026-05-16T10:00:00Z"
  }
}
```

---

### GET /organizations — List Organizations

**Min role**: Any authenticated | **Security**: Low | **Rate limit**: 300/min

**Query parameters**:

```
?org_type=NGO,HOSPITAL
?is_verified=true
?service_type=MEDICAL
?lat=17.3850&lon=78.4867&radius_km=20
?page=1&page_size=20
```

---

### GET /organizations/ — Get Organization

**Min role**: Any authenticated | **Security**: Low | **Rate limit**: 300/min

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "org_id": "550e8400-...",
    "name": "Red Cross India",
    "org_type": "NGO",
    "service_types": ["MEDICAL", "FOOD"],
    "is_verified": true,
    "contact_phone": "+911234567890",
    "coverage_area": { "type": "Point", "coordinates": [78.4867, 17.3850] },
    "coverage_radius_km": 25,
    "capacity": 50
  }
}
```

---

### POST /organizations/ — Update Organization

**Min role**: Org_Admin (own org only) | **Security**: Medium | **Rate limit**: 30/min

**Request** (include only fields to change):

```json
{
  "service_types": ["MEDICAL", "FOOD", "SHELTER"],
  "capacity": 75,
  "contact_phone": "+911234567890"
}
```

---

### POST /organizations//verify — Verify Organization

**Min role**: DM_Authority | **Security**: Critical | **Rate limit**: 10/min

**Request**:

```json
{ "notes": "Registration documents verified. License #MH-NGO-2026-001 confirmed." }
```

Sets `is_verified = true` and records verifier's `user_id`. Only verified organisations appear in provider search results for nearby requests.

---

## 7. Geospatial Endpoints

All geospatial queries run in the Python backend using GeoPandas/Shapely — **not GeoServer**.

### GET /geo/nearby

```
?lat=17.3850&lon=78.4867&radius_km=10&service_type=MEDICAL&status=SUBMITTED
```

**Response**: GeoJSON FeatureCollection of service requests within radius.

### POST /geo/cluster

```json
{
  "lat": 17.3850,
  "lon": 78.4867,
  "radius_km": 50,
  "algorithm": "kmeans",
  "max_clusters": 10
}
```

**Response**: Cluster centroids with service counts — used for map heatmap.

### GET /geo/bbox — Bounding Box Query

```
?min_lat=17.0&max_lat=18.0&min_lon=78.0&max_lon=79.0
```

Returns all service requests whose location falls within the rectangle defined by the four coordinates. Useful for map viewport queries when the user pans or zooms.

---

### GET /geo/geojson — Export as GeoJSON

**Min role**: Any authenticated | **Security**: Low | **Rate limit**: 300/min

**Query parameters**:

```
?status=SUBMITTED,ACCEPTED
?service_type=MEDICAL,RESCUE
?bbox=78.0,17.0,79.0,18.0
```

**Response** (200): Standard GeoJSON `FeatureCollection`. Each `Feature` is a service request.

```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": { "type": "Point", "coordinates": [78.4867, 17.3850] },
      "properties": {
        "service_id": "550e8400-...",
        "status": "SUBMITTED",
        "priority": "CRITICAL",
        "service_type": "MEDICAL",
        "created_at": "2026-05-16T10:00:00Z"
      }
    }
  ]
}
```

**⚠️ Coordinate order**: `[longitude, latitude]` — GeoJSON spec, opposite of Leaflet. See [Global Specifications](#1-global-specifications).

Used for importing IDRM service data into external GIS tools (QGIS, ArcGIS, etc.).

---

## 8. Analytics Endpoints

### GET /analytics/dashboard

Returns summary stats for the requesting user's scope:

```json
{
  "status": "success",
  "data": {
    "total_requests": 1250,
    "active_requests": 87,
    "avg_response_time_min": 18.5,
    "completion_rate": 0.89,
    "by_service_type": {
      "MEDICAL": 340, "FOOD": 280, "WATER": 195, "SHELTER": 435
    },
    "by_status": {
      "SUBMITTED": 34, "ACCEPTED": 28, "IN_PROGRESS": 25,
      "COMPLETED": 890, "VERIFIED": 273
    }
  }
}
```

Scope filtering: Volunteer → their area only · Event_Manager → event scope · DM_Authority → district/state · System_Admin → all. Results cached in Redis for 5 minutes.

---

### GET /analytics/reports — Detailed Reports

**Min role**: Event_Manager | **Security**: Medium | **Rate limit**: 60/min

**Query parameters**:

```
?start_date=2026-05-01&end_date=2026-05-31
?service_type=MEDICAL
?region=Chennai
?group_by=day
```

`group_by` accepts: `day`, `week`, `month`

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "period": { "start": "2026-05-01", "end": "2026-05-31" },
    "summary": {
      "total_requests": 320,
      "completed": 285,
      "avg_response_time_min": 22.3,
      "satisfaction_avg": 4.2
    },
    "by_day": [
      { "date": "2026-05-01", "submitted": 12, "completed": 10, "avg_response_min": 19.5 }
    ],
    "by_service_type": { "MEDICAL": 120, "FOOD": 85, "WATER": 65, "SHELTER": 50 }
  }
}
```

---

### POST /analytics/export — Export Data

**Min role**: DM_Authority | **Security**: Critical | **Rate limit**: 10/hour

**Request**:

```json
{
  "format": "CSV",
  "date_range": { "start": "2026-05-01", "end": "2026-05-31" },
  "filters": {
    "service_types": ["MEDICAL", "FOOD"],
    "priorities": ["CRITICAL", "HIGH"]
  }
}
```

Supported formats: `CSV`, `XLSX`, `JSON`. Maximum date range: 90 days.

**Response** (200):

```json
{
  "status": "success",
  "data": {
    "download_url": "https://exports.idrm.gov.in/secure/a8f3c2d1-export.csv",
    "expires_at": "2026-05-16T12:00:00Z",
    "record_count": 285
  }
}
```

**PII redaction**: `email`, `phone`, and `exact_address` fields are automatically redacted from exports. Export action is recorded in the audit log.

---

## 9. Admin Endpoints

### GET /admin/users

```
?role=CITIZEN,PROVIDER
?is_active=true
?is_verified=false
?search=john
?page=1&page_size=50
```

### GET /admin/audit-log

**Min role**: Auditor or System_Admin | **Security**: Critical | **Rate limit**: 60/min

```
?user_id={uuid}
?action=SERVICE_CREATED,SERVICE_ACCEPTED
?resource_type=ServiceRequest
?from_date=2026-05-01&to_date=2026-05-31
?page=1&page_size=100
```

**Response entry format**:

```json
{
  "log_id": 1234,
  "timestamp": "2026-05-16T10:00:00Z",
  "user_id": "uuid",
  "user_email": "john@example.com",
  "action": "SERVICE_CREATED",
  "resource_type": "ServiceRequest",
  "resource_id": "uuid",
  "ip_address": "203.0.113.1",
  "metadata": { "status_before": null, "status_after": "SUBMITTED" }
}
```

Audit logs are immutable — no PUT/DELETE allowed on this table.

---

### GET /admin/system-health

**Min role**: System_Admin | **Security**: Critical | **Rate limit**: 60/min

**Response** (200 — all systems up):

```json
{
  "status": "success",
  "data": {
    "overall": "healthy",
    "services": {
      "api_gateway": { "status": "up", "port": 3000, "latency_ms": 12 },
      "fastapi_monolith": {
        "status": "up", "port": 8000,
        "note": "Single process — all modules (auth, services, geo, analytics, notifications) share port 8000",
        "modules": {
          "auth":          { "status": "up", "route_prefix": "/auth" },
          "services":      { "status": "up", "route_prefix": "/services" },
          "geo":           { "status": "up", "route_prefix": "/geo" },
          "analytics":     { "status": "up", "route_prefix": "/analytics" },
          "notifications": { "status": "up", "route_prefix": "/notifications" }
        }
      }
    },
    "database": {
      "postgres": { "status": "up", "connection_pool": "18/20" },
      "redis": { "status": "up", "memory_used_mb": 142 }
    },
    "uptime_seconds": 86400,
    "checked_at": "2026-05-16T10:00:00Z"
  }
}
```

Returns `503 Service Unavailable` (same body shape but `"overall": "degraded"`) if any critical service is down.

---

## 10. Error Responses

All errors follow a consistent format:

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email address is not valid",
    "field": "email",
    "details": {}
  }
}
```

### HTTP Status Codes

| Code | Meaning               | Common Cause                   |
| ---- | --------------------- | ------------------------------ |
| 200  | OK                    | Successful GET                 |
| 201  | Created               | Successful POST (new resource) |
| 204  | No Content            | Successful logout              |
| 400  | Bad Request           | Validation failed              |
| 401  | Unauthorized          | Missing/expired token          |
| 403  | Forbidden             | Insufficient role              |
| 404  | Not Found             | Resource doesn't exist         |
| 409  | Conflict              | Duplicate email/phone          |
| 422  | Unprocessable Entity  | Schema validation failure      |
| 429  | Too Many Requests     | Rate limit exceeded            |
| 500  | Internal Server Error | Unhandled server error         |

---

## 11. WebSocket Events

WebSocket server runs on `ws://localhost:3001` (dev) via Bun gateway.

### Connection

```javascript
const ws = new WebSocket('ws://localhost:3001/ws');
ws.onopen = () => ws.send(JSON.stringify({ type: 'auth', token: accessToken }));
```

### Event Types

| Event                      | Payload                                    | Who Receives              |
| -------------------------- | ------------------------------------------ | ------------------------- |
| `service.created`        | `{ service_id, service_type, location }` | Providers in area         |
| `service.accepted`       | `{ service_id, provider_id, eta }`       | Requestor                 |
| `service.status_changed` | `{ service_id, old_status, new_status }` | Requestor + Provider      |
| `service.completed`      | `{ service_id, completed_at }`           | Requestor                 |
| `notification`           | `{ message, type, link }`                | Target user               |
| `location.update`        | `{ service_id, lat, lon }`               | Requestor (live tracking) |

---

## 12. Pre-Deployment Security Checklist

Run through every item before shipping to staging or production.

**Authentication & Authorization**

- [ ] All passwords hashed with bcrypt (cost ≥ 12)
- [ ] JWT access tokens expire in 15 min; refresh tokens in 7 days
- [ ] Every endpoint checks **authorization** (role), not just authentication (JWT valid)
- [ ] Ownership verified for user-scoped resources (user can only touch own data)
- [ ] Failed logins rate-limited: 5 per 15 min per IP

**Input Validation**

- [ ] All inputs validated — type, length, format, content
- [ ] Enum values checked against whitelist (service_type, priority, status, role)
- [ ] Coordinates validated (lat −90..90, lon −180..180, radius ≤ 50 km)
- [ ] SQL injection prevented (parameterised queries — no string concatenation)
- [ ] JSON structure validated before use

**Output Security**

- [ ] All outputs sanitised (prevent XSS — escape HTML in any string field)
- [ ] `password_hash`, reset tokens, session keys **never** in responses
- [ ] PII redacted in exports (`email`, `phone`, `exact_address`)
- [ ] Error messages don't leak internal details or stack traces

**Transport Security**

- [ ] HTTPS enforced — HTTP 301-redirects to HTTPS
- [ ] TLS 1.2+ required
- [ ] HSTS header set (`Strict-Transport-Security`)
- [ ] Cookies flagged `HttpOnly; Secure; SameSite=Strict`

**Rate Limiting** (verify Bun gateway config matches these)

- [ ] Auth endpoints: 5 attempts / 15 min
- [ ] Public GET: 60 / min
- [ ] Authenticated GET: 300 / min
- [ ] POST / state-change: 30 / min
- [ ] Export / Analytics: 10 / hour

**Security Headers** (verify NGINX/Bun adds these)

- [ ] `Content-Security-Policy`
- [ ] `X-Frame-Options: DENY`
- [ ] `X-Content-Type-Options: nosniff`
- [ ] `X-XSS-Protection: 1; mode=block`

**Logging & Monitoring**

- [ ] All auth failures logged to `audit_logs`
- [ ] All admin actions logged (role changes, org verification, exports)
- [ ] Data exports logged with actor and record count
- [ ] Alerts configured for repeated 401/403 bursts

**CSRF Protection**

- [ ] CSRF tokens on all POST requests from browser clients
- [ ] `SameSite=Strict` on auth cookies
- [ ] `Origin` header validated against allowlist

---

**Reference**:

- Live API docs (dev): [http://localhost:8000/docs](http://localhost:8000/docs)
- Database schema: [../docs/development/IDRM-LLD.md](../docs/development/IDRM-LLD.md) §9–11
- Architecture overview: [../docs/diagrams/IDRM-System-Architecture.md](../docs/diagrams/IDRM-System-Architecture.md)
