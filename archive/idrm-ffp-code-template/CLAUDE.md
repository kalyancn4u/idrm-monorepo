# IDRM v3 - Claude AI Context File

## Integrated Disaster Response Management

**Version**: 3.0
**Last Updated**: May 24, 2026
**Architecture**: Monolith with 3 Frontend Platforms
**Tech Stack**: Bun + Python/FastAPI + PostgreSQL + PostGIS + Redis

---

> ## 🚩🚩 Authoring vs. target environment — READ FIRST
> This repository is **written/generated on a Windows machine**, but that box is **for authoring code only**. It has **no Python/conda, no PostgreSQL/PostGIS, no Redis**, and Bun-on-Windows misbehaves (stray processes, localhost hangs). **Do not build, run, migrate, or verify on the Windows box.**
>
> The **development/target platform is an Ubuntu laptop** — **all building, running, database/migrations, and verification happen there.** Treat every shell command in this file and the guides as an **Ubuntu** command. Full ports/firewall + dev/staging/prod walkthrough: **`docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`**.

---

## 🎯 Project Overview

**IDRM** (Integrated Disaster Response Management) is a government-backed, map-driven platform that connects citizens in crisis with NGOs, hospitals, and volunteers — think "Uber for Disaster Relief". It is built as a monolith that serves three frontend platforms from a single unified backend.

### Three Frontend Platforms

| Platform      | Port | Purpose                                                                        |
| ------------- | ---- | ------------------------------------------------------------------------------ |
| HTML/Tailwind | 5173 | Primary citizen-facing web interface (fast, lightweight, works in emergencies) |
| React SPA     | 5174 | Admin dashboards with rich data visualizations                                 |
| React Native  | Expo | iOS + Android native apps for field workers — **🔒 Post-MVP** (MVP ships responsive web) |

### Key Architecture Decisions

- **Bun** (not Node.js) — JavaScript runtime for API Gateway
- **Miniconda** (not venv/pip) — Python environment management
- **Python geospatial module** (not Java/GeoServer) — embedded inside the FastAPI monolith on port 8000
- **PostGIS** — PostgreSQL extension for geospatial queries
- **Redis** — Caching, sessions, rate limiting, pub/sub

---

## 🏗️ System Architecture

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
        │  FastAPI Modular Monolith        │
        │  Port 8000 · Single Process      │
        │  ├─ /auth/*          module      │
        │  ├─ /services/*      module      │
        │  ├─ /geo/*           module      │
        │  ├─ /analytics/*     module      │
        │  └─ /notifications/* module      │
        └──────────┬───────────────────────┘
                   ↓
        ┌──────────────────────┐
        │  Data Layer          │
        │  ├─ PostgreSQL 16    │
        │  │  + PostGIS 3.4    │
        │  └─ Redis 7.2+       │
        └──────────────────────┘
```

### Base URLs

| Environment | API Gateway                            | WebSocket                        |
| ----------- | -------------------------------------- | -------------------------------- |
| Development | `http://localhost:3000/api/v1`       | `ws://localhost:3001`          |
| Staging     | `https://staging.idrm.gov.in/api/v1` | `wss://staging.idrm.gov.in/ws` |
| Production  | `https://api.idrm.gov.in/api/v1`     | `wss://api.idrm.gov.in/ws`     |

---

## 🔌 API Reference

### Authentication APIs

#### POST /auth/register

```json
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "full_name": "John Doe",
    "phone": "+919876543210",
    "role": "CITIZEN",
    "language_preference": "en"
}
```

> **Allowed role values on registration**: `CITIZEN`, `PROVIDER`, `VOLUNTEER` only.
> All elevated roles (`ORGANIZER`, `MANAGER`, `EVENT_MANAGER`, `EXECUTIVE`, `DM_AUTHORITY`, `AUDITOR`, `ADMIN`)
> cannot be self-assigned — they must be granted by an `ADMIN` via `POST /users/{id}/role`.
> `EXECUTIVE` is reserved for Post-MVP. `DM_AUTHORITY` ("Event Admin") may be a Government Org **or** a vetted NGO.

Response (201): `{ "id": "uuid", "email": "...", "full_name": "...", "role": "CITIZEN" }`

#### POST /auth/login

```json
{ "email": "user@example.com", "password": "SecurePass123!" }
```

Response (200): `{ "access_token": "...", "refresh_token": "...", "token_type": "Bearer", "expires_in": 900, "user": {...} }`

> **Note**: `expires_in` is **900 seconds = 15 minutes**. Access tokens are short-lived for security. Use `POST /auth/refresh` with the refresh token before they expire.

#### POST /auth/refresh

```json
{ "refresh_token": "..." }
```

Response (200): `{ "access_token": "...", "token_type": "Bearer", "expires_in": 900 }`

#### POST /auth/logout

Header: `Authorization: Bearer <access_token>`
Response: 204 No Content

---

### Service Request APIs

> **Important — enum values are UPPERCASE**: The database uses exact UPPERCASE strings for all fixed-choice
> fields. Sending `"medical"` instead of `"MEDICAL"` is treated as an invalid value and the request is
> rejected. Think of them like a dropdown that only accepts the exact option text.

> **Important — HTTP method**: IDRM uses only GET and POST. There are no PUT, PATCH, or DELETE
> endpoints. Status changes happen through specific action sub-endpoints (e.g. `/approve`, `/accept`).

#### POST /services

```json
{
    "service_type": "MEDICAL",
    "description": "Need ambulance urgently",
    "priority": "CRITICAL",
    "location": { "type": "Point", "coordinates": [80.2707, 13.0827] },
    "address": "Anna Nagar, Chennai",
    "num_people_affected": 3,
    "privacy_level": "PUBLIC",
    "contact_phone": "+919876543210"
}
```

> **Coordinate order**: GeoJSON always puts `[longitude, latitude]` — note this is the **opposite** of
> how most maps display it (latitude first). Longitude is the east-west value, latitude is north-south.

Response (201): Full request object with `service_id`, `status: "SUBMITTED"`, timestamps.

#### GET /services

Query params: `status`, `service_type`, `priority`, `page` (default 1), `per_page` (default 20, max 100)
Example: `GET /services?status=SUBMITTED&service_type=MEDICAL&page=1`
Response (200): `{ "status": "success", "data": { "items": [...], "total": 45, "page": 1, "per_page": 20, "pages": 3 } }`

#### GET /services/

Response (200): Full request object including `requestor` user details.

#### POST /services//approve — DM Authority approves a SUBMITTED request

```json
{ "notes": "Verified location and priority. Approved for dispatch." }
```

#### POST /services//accept — Provider accepts an APPROVED request

```json
{ "estimated_arrival": "2026-05-24T10:30:00Z", "notes": "On my way with medical kit" }
```

#### POST /services//start — Provider starts work (ACCEPTED → IN_PROGRESS)

No body required. (Documented in the contract: see `docs/rfc/RFC-PROTOCOL.md` §3 transition T4.)

#### POST /services//complete — Provider marks the service as done

```json
{ "notes": "Treatment administered, patient stable" }
```

#### POST /services//verify — Requestor confirms completion (with optional rating 1–5)

```json
{ "rating": 5, "feedback": "Provider arrived quickly and handled the situation well" }
```

#### POST /services//cancel — Requestor cancels (only while SUBMITTED or APPROVED)

```json
{ "reason": "Situation resolved before provider arrived" }
```

#### POST /services//reject — DM Authority rejects a SUBMITTED request

```json
{ "reason": "Duplicate request — see service #abc123" }
```

---

### Geospatial APIs

#### GET /geo/nearby

Query params: `latitude` (required), `longitude` (required), `radius` (km, default 5, max 50), `service_type` (optional)
Example: `GET /geo/nearby?latitude=13.0827&longitude=80.2707&radius=10`
Response (200): `{ "center": {...}, "radius_km": 10, "results": [...], "total": 12 }`

#### GET /geo/cluster

Query params: `zoom` (required, 1–20), `bounds` (optional: south,west,north,east)
Response (200): `{ "clusters": [{ "latitude": ..., "longitude": ..., "count": 15, "priority_breakdown": {...} }] }`

---

### User & Organization APIs

#### GET /users/me

Response (200): `{ "id": "uuid", "email": "...", "full_name": "...", "phone": "...", "role": "CITIZEN", "preferences": { "language": "en" }, "created_at": "..." }`

#### POST /users/me

```json
{ "full_name": "...", "phone": "...", "preferences": { "language": "hi" } }
```

> **Why POST and not PUT?** IDRM uses only GET and POST throughout — no PUT, PATCH, or DELETE.
> POST handles all creates, updates, and actions. See `start-here/COMPLETE-API-SPECS-GUIDE.md` § HTTP Method Policy.

---

### Analytics APIs

#### GET /analytics/dashboard

Response (200):

```json
{
    "status": "success",
    "data": {
        "total_requests": 1250,
        "active_requests": 87,
        "avg_response_time_min": 18.5,
        "completion_rate": 0.89,
        "by_service_type": {
            "RESCUE": 180, "MEDICAL": 450, "FOOD": 380,
            "WATER": 220, "SHELTER": 200, "OTHER": 20
        },
        "by_status": {
            "SUBMITTED": 34, "APPROVED": 11, "ACCEPTED": 28,
            "IN_PROGRESS": 25, "COMPLETED": 890, "VERIFIED": 262
        }
    }
}
```

---

### Notification APIs

#### GET /notifications

Response (200): `{ "status": "success", "data": { "items": [{ "id": "...", "type": "SERVICE_ACCEPTED", "title": "...", "message": "...", "read": false, "created_at": "..." }], "unread_count": 5 } }`

> Notification `type` values: `SERVICE_CREATED`, `SERVICE_ACCEPTED`, `SERVICE_COMPLETED`, `VERIFICATION_REQUEST`, `GENERAL`, `SYSTEM`

#### POST /notifications//read

Response: 200 OK

---

### WebSocket Real-time

**URL**: `ws://localhost:3001` (dev) / `wss://api.idrm.gov.in/ws` (prod)

**Subscribe message**:

```json
{ "type": "subscribe", "channel": "service_requests" }
```

**Event types received**:

- `request_created` — new request with full `request` object
- `request_updated` — status change with updated `request` object
- `request_deleted` — removal with `{ "request": { "id": "..." } }`

---

### Error Handling

Standard error format:

```json
{ "detail": "Error message", "code": "ERROR_CODE", "field": "field_name" }
```

HTTP status codes: 200 OK, 201 Created, 204 No Content, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable Entity, 429 Rate Limited, 500 Server Error.

---

## 💻 Common Development Commands

> 🚩 Run these on the **Ubuntu dev laptop** (the target) — not the Windows authoring box.

```bash
# Start all services (5-terminal approach)
# Terminal 1: Backend (FastAPI — Modular Monolith)
cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000

# Terminal 2: API Gateway
cd src/backend/api-gateway && bun run dev

# Terminal 3: HTML/Tailwind frontend
cd src/frontend/web-html && bun run dev  # Port 5173

# Terminal 4: React SPA
cd src/frontend/web-react && bun run dev  # Port 5174

# Terminal 5: React Native
cd src/frontend/mobile-expo && bun install && npx expo start

# Tests
pytest tests/
bun test src/backend/api-gateway/

# Database
psql -U idrm_user -d idrm_db
redis-cli ping
```

---

## 📁 Platform-Specific File Locations

| File                                  | Purpose                                   |
| ------------------------------------- | ----------------------------------------- |
| `src/frontend/web-html/src/js/api/` | HTML/Tailwind API client                  |
| `src/frontend/web-react/src/`       | React TypeScript source                   |
| `src/frontend/mobile-expo/`         | React Native (Expo) source                |
| `src/backend/app-python/api/`       | FastAPI route handlers                    |
| `src/backend/api-gateway/`          | Bun gateway (routing, rate limiting, JWT) |

---

## 📋 Instruction Files Status

| File                                | Status                  | Purpose                                                                              |
| ----------------------------------- | ----------------------- | ------------------------------------------------------------------------------------ |
| `instructions_api_v3.md`          | ✅ Complete (see above) | API integration guide for all 3 platforms                                            |
| `instructions_ui_v3.md`           | ✅ Complete             | UI/UX rulebook — Slate+Emerald tokens + Tailwind component recipes                    |
| `instructions_web_v3.md`          | ✅ Complete             | HTML/Tailwind detailed guide —`instructions/instructions_web_v3.md`               |
| `instructions_pages_v3.md`        | ✅ Complete             | Page-by-page reference for all platforms —`instructions/instructions_pages_v3.md` |
| `instructions_json_formats_v3.md` | ✅ Complete             | All JSON request/response formats —`instructions/instructions_json_formats_v3.md` |

> ✅ **Note for Claude**: `instructions_ui_v3.md` now exists in `instructions/` — the canonical UI/UX
> rulebook (Slate + Emerald palette, Tailwind component recipes). For the full design-token reference,
> also see `start-here/COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md` (pending update to the Slate+Emerald palette).

---

## 🏛️ Core Engineering Principles

### 1. Mandatory Principles

The application MUST follow:

- SOLID Principles
- DRY (Don't Repeat Yourself)
- KISS (Keep It Simple)
- Separation of Concerns
- High Cohesion, Low Coupling
- Composition over Inheritance
- Reusable Component Architecture
- Type Safety
- Accessibility First Development

---

## 🔑 Key Constraints & Decisions

- **No Java/GeoServer** — Replaced by a Python geospatial module inside the FastAPI monolith (port 8000)
- **No Node.js** — Replaced by Bun
- **No venv** — Use Miniconda (`conda activate idrm-mvp`)
- **Three frontends** — Each has its own `bun run dev` command
- **Role types** (10 account roles + a Public tier): `CITIZEN`, `VOLUNTEER`, `ORGANIZER`, `PROVIDER`, `MANAGER`, `EVENT_MANAGER`, `EXECUTIVE` (🔒 Post-MVP), `DM_AUTHORITY`, `AUDITOR`, `ADMIN` — plus a non-account **Public** (not-logged-in, view-only) tier. "Event Admin" = `DM_AUTHORITY` (GO or NGO). Canonical matrix: `docs/development/IDRM-FS.md` §3.3.
- **Service types**: `RESCUE`, `MEDICAL`, `FOOD`, `SHELTER`, `WATER`, `OTHER`
- **Priority levels**: `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`
- **Request statuses** (lifecycle order): `SUBMITTED` → `APPROVED` → `ACCEPTED` → `IN_PROGRESS` → `COMPLETED` → `VERIFIED` (terminal states: `REJECTED`, `CANCELLED`, `EXPIRED`; plus `DISPUTED` — raised from `IN_PROGRESS`/`COMPLETED`, resolves to `IN_PROGRESS` or `REJECTED`). Emergency/urgent requests are auto-approved by the system.
- **Privacy levels**: `PUBLIC`, `PROTECTED`, `PRIVATE` (default `PROTECTED`; can only be raised). `PROTECTED` hides name/phone from the public; responders get contact via the system.
- **Language preferences**: `en`, `hi`, `te` (English, Hindi, Telugu — the pilot region is Telugu-speaking)
- **Out of MVP (Post-MVP)**: Finance/Donations module, AI Chatbot, native mobile app (React Native/Expo). **MVP scope** = 2-district pilot (Hyderabad + Vijayawada); pan-India / 100k users are growth targets.

> **Case rule**: All enum values above are UPPERCASE strings. The database's CHECK constraints enforce exact spelling — `"medical"` is rejected; `"MEDICAL"` is accepted. Always send them as shown here.

---

*For deep-dive architecture, see `docs/IDRM-ARCHITECTURE-GUIDE.md` and `docs/development/IDRM-HLD.md`.*
*For development setup, see `docs/IDRM-DEVELOPMENT-GUIDE.md`.*
*🚩 For Ubuntu **ports** (open/check/free + `ufw` firewall) and running **dev / staging / production** on one host, see `docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`.*
*For API contracts, see `start-here/COMPLETE-API-SPECS-GUIDE.md`.*
