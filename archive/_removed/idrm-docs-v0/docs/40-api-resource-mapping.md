> *Type: Document (specification) · Audience: Developers, integrators · Status: Archived — v0 historical generation*

# IDRM API Resource Mapping

<!-- IDRM-CLEANUP doc=v0-40-api status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP — where each section is addressed now (annotation pass, 2026-08-16)
>
> Retired v0 API catalogue. **The canonical, frozen contract is `docs/mvp/40-api-specification.md` (+ `40-api-openapi.yaml`)** —
> incident-centric `/api/v1`, snake_case, UUIDs, `{data,pagination}` lists, error envelope with machine `code`.
> The v0 paths/module split here **do not match** and are superseded; use them only to confirm coverage. Naming:
> v0 *"Service"* = **incidents**; *"Organization"* = **providers/resources**; *"System"* = **administration**;
> *"Analytics"* = **reports** (advanced analytics = FFP); *Financial/WebSocket/Rate-Limit = FFP*. *Legend:* ✅ covered ·
> ⚠ superseded · ⊘ dropped. Program: `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
>
> | Snippet | Section | → Addressed in (latest) | Phase | Verdict | PICS |
> |---|---|---|---|---|---|
> | `v0-40§ov` | Project Overview + Endpoints Summary | `docs/mvp/40` | MVP | ⚠ | — |
> | `v0-40§auth` | Auth Module (11 endpoints) | `docs/mvp/40` + `22` | MVP | ⚠ (paths differ) | `PICS-USR-*` |
> | `v0-40§svc` | Service Module (16) = **incidents** | `docs/mvp/40` (incidents) + `11` | MVP | ⚠ | `PICS-INC-*` |
> | `v0-40§dis` | Disaster Module (9) | disaster-type config → ADM; advisories → **ALR**; disaster-event → FFP | MVP / FFP | ⚠ | `PICS-ADM-*`, `PICS-ALR-*` |
> | `v0-40§org` | Organization Module (10) | providers/resources → `docs/mvp/40` | MVP | ⚠ | `PICS-RES-*` |
> | `v0-40§geo` | Geo Module (5) | `docs/mvp/40` + `60` (LOC) | MVP | ⚠ | `PICS-LOC-*` |
> | `v0-40§ntf` | Notification Module (8) | `docs/mvp/40` (NTF) | MVP | ⚠ | `PICS-NTF-*` |
> | `v0-40§fin` | Financial Module (12) | money/donations → FFP | FFP | ⊘ (MVP) | — |
> | `v0-40§ana` | Analytics Module (10) | basic reports → **RPT**; advanced analytics → FFP | MVP / FFP | ⚠ | `PICS-RPT-*` |
> | `v0-40§fil` | Files Module (6) | `docs/mvp/40` + ADR-007 (FIL) | MVP | ⚠ | `PICS-FIL-*` |
> | `v0-40§usr` | User Module (8) | `docs/mvp/40` (profile) (USR) | MVP | ⚠ | `PICS-USR-*` |
> | `v0-40§sys` | System Module (10) | administration/health → `docs/mvp/40`/`80` | MVP | ⚠ | `PICS-ADM-*` |
> | `v0-40§err` | Error Response Reference | `docs/mvp/40` (error envelope + `code`) | MVP | ✅ | `PICS-STK-API-01` |
> | `v0-40§qref` | Quick Reference Tables | `docs/mvp/40` | MVP | ⚠ | — |
> | `v0-40§authg` | Authentication Guide (JWT structure) | `docs/mvp/22` | MVP | ✅ | `PICS-USR-*` |
> | `v0-40§rate` | Rate Limiting Guide | gateway → FFP (`api-gateway` spoke) | FFP | ⊘ (MVP) | `PICS-STK-APISIX-F01` |
> | `v0-40§flows` | Common Workflows | citizen/provider/coordinator → `docs/mvp/11`; donor → FFP | MVP / FFP | ⚠ | — |
> | `v0-40§ws` | WebSocket Events | deep real-time → FFP `81` | FFP | ⊘ (MVP) | `PICS-NTF-F01` |
> | `v0-40§dm` | Data Models Reference (ServiceRequest/DisasterEvent/Org) | `docs/mvp/50`; DisasterEvent → FFP | MVP / FFP | ⚠ | — |
> | `v0-40§resp` | Response Format Standards (success/error/paginated) | `docs/mvp/40` (`{data,pagination}` + envelope) | MVP | ✅ | `PICS-STK-API-01` |
> | `v0-40§sup` | Support & Documentation | boilerplate | — | ⊘ | — |

## Project Overview

| Field | Value |
|-------|-------|
| **Project Name** | IDRM - Integrated Disaster Response Management |
| **API Version** | v1 |
| **Base URL** | https://api.idrm.gov.in/v1 |
| **Owner** | IDRM Development Team |
| **Description** | Complete API suite for disaster management, provider coordination, and relief operations |
| **Last Updated** | 2024-12-23 |
| **Total Endpoints** | 120+ |
| **Authentication** | JWT RS256 with Bearer tokens |
| **Primary Language** | Python (FastAPI) + Node.js (Express) |
| **Database** | PostgreSQL 16 + PostGIS 3.4 |
| **Real-time** | WebSocket (Socket.IO 4.x) |


---

## API Endpoints Summary

**Total Endpoints:** 105 across 12 modules

### Modules Covered:
1. **Authentication & Authorization** (11 endpoints) - User registration, login, JWT tokens, password management
2. **Service Request Management** (16 endpoints) - Create, track, assign, complete service requests
3. **Disaster Event Management** (9 endpoints) - Declare disasters, track events, manage affected areas
4. **Organization/Provider Management** (11 endpoints) - Provider registration, verification, capacity management
5. **Geospatial Operations** (5 endpoints) - Distance calculation, spatial queries, clustering, maps
6. **Notifications** (8 endpoints) - User notifications, preferences, alerts
7. **Financial Operations** (12 endpoints) - Donations, fund allocation, expenditure, transparency reports
8. **Analytics & Reporting** (10 endpoints) - Dashboards, trends, performance metrics, audit reports
9. **File Management** (6 endpoints) - Upload, download, storage management
10. **User Management** (8 endpoints) - User CRUD, role management, activity logs
11. **System/Admin** (10 endpoints) - Health checks, monitoring, system configuration

---

## Complete API Endpoint Reference


### Auth Module (11 endpoints)

#### Register User

**Path:** `POST /auth/register`

**Purpose:** Register new user account

| Property | Value |
|----------|-------|
| **Component** | Registration |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `email, password, name, phone, role` |
| **Response Data** | `user_id, token` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 10/min |
| **Notes** | Email unique, password min 8 chars |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Login

**Path:** `POST /auth/login`

**Purpose:** Authenticate and get JWT tokens

| Property | Value |
|----------|-------|
| **Component** | Login |
| **Resource** | Session |
| **Status** | Active |
| **Request Data** | `email, password` |
| **Response Data** | `access_token, refresh_token` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 5/min |
| **Notes** | 5 attempts then lockout |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Refresh Token

**Path:** `POST /auth/refresh`

**Purpose:** Get new access token

| Property | Value |
|----------|-------|
| **Component** | Token |
| **Resource** | Session |
| **Status** | Active |
| **Request Data** | `refresh_token` |
| **Response Data** | `access_token` |
| **Auth Required** | No |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 10/min |
| **Notes** | Extends session |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Logout

**Path:** `POST /auth/logout`

**Purpose:** End session

| Property | Value |
|----------|-------|
| **Component** | Token |
| **Resource** | Session |
| **Status** | Active |
| **Request Data** | `refresh_token` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 20/min |
| **Notes** | Clears Redis session |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Forgot Password

**Path:** `POST /auth/forgot-password`

**Purpose:** Request reset link

| Property | Value |
|----------|-------|
| **Component** | Password |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `email` |
| **Response Data** | `message` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 3/min |
| **Notes** | Sends email |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Reset Password

**Path:** `POST /auth/reset-password`

**Purpose:** Reset using token

| Property | Value |
|----------|-------|
| **Component** | Password |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `token, new_password` |
| **Response Data** | `success` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 5/min |
| **Notes** | Token expires 1h |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Change Password

**Path:** `POST /auth/change-password`

**Purpose:** Change when logged in

| Property | Value |
|----------|-------|
| **Component** | Password |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `current, new` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 10/min |
| **Notes** | Need current password |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Get Profile

**Path:** `GET /auth/profile`

**Purpose:** Get current user info

| Property | Value |
|----------|-------|
| **Component** | Profile |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `user` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 100/min |
| **Notes** | Returns user details |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Update Profile

**Path:** `PUT /auth/profile`

**Purpose:** Update user details

| Property | Value |
|----------|-------|
| **Component** | Profile |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `name, phone` |
| **Response Data** | `user` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 20/min |
| **Notes** | Cannot change email/role |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Verify Email

**Path:** `POST /auth/verify-email`

**Purpose:** Verify email address

| Property | Value |
|----------|-------|
| **Component** | Verification |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `token` |
| **Response Data** | `success` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 10/min |
| **Notes** | Required for access |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |

#### Resend Verification

**Path:** `POST /auth/resend-verification`

**Purpose:** Resend verification link

| Property | Value |
|----------|-------|
| **Component** | Verification |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `email` |
| **Response Data** | `message` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 3/min |
| **Notes** | Once per hour |
| **Owner Team** | Auth |
| **Doc Reference** | Cat2 |


### Service Module (16 endpoints)

#### Create Request

**Path:** `POST /services/requests`

**Purpose:** Citizens request help

| Property | Value |
|----------|-------|
| **Component** | Form |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `category, title, description, location, priority` |
| **Response Data** | `request_id` |
| **Auth Required** | Yes |
| **Roles Allowed** | Citizen, Coordinator |
| **Rate Limit** | 20/min |
| **Notes** | Location required |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### List Requests

**Path:** `GET /services/requests`

**Purpose:** Get paginated requests

| Property | Value |
|----------|-------|
| **Component** | List |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `page, limit, status, category` |
| **Response Data** | `List<Request>` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | 20 per page default |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Get Request

**Path:** `GET /services/requests/{id}`

**Purpose:** Get request details

| Property | Value |
|----------|-------|
| **Component** | Detail |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | 404 if not found |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Update Request

**Path:** `PUT /services/requests/{id}`

**Purpose:** Update request

| Property | Value |
|----------|-------|
| **Component** | Update |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, title, description` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Citizen (own), Coordinator |
| **Rate Limit** | 20/min |
| **Notes** | Not if assigned |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Update Status

**Path:** `PUT /services/requests/{id}/status`

**Purpose:** Change status

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, status, notes` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider, Coordinator |
| **Rate Limit** | 30/min |
| **Notes** | Follow flow |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Accept Request

**Path:** `POST /services/requests/{id}/accept`

**Purpose:** Provider accepts

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, eta` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 50/min |
| **Notes** | Must be matched |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Start Service

**Path:** `POST /services/requests/{id}/start`

**Purpose:** Mark as started

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 50/min |
| **Notes** | Must be assigned |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Complete Service

**Path:** `POST /services/requests/{id}/complete`

**Purpose:** Mark completed

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, notes, photos` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 30/min |
| **Notes** | Needs notes |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Cancel Request

**Path:** `POST /services/requests/{id}/cancel`

**Purpose:** Cancel request

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, reason` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Citizen, Coordinator |
| **Rate Limit** | 20/min |
| **Notes** | Not if completed |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Find Providers

**Path:** `POST /services/requests/{id}/match`

**Purpose:** Find matching providers

| Property | Value |
|----------|-------|
| **Component** | Matching |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, radius` |
| **Response Data** | `List<Provider>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator |
| **Rate Limit** | 50/min |
| **Notes** | Returns top 10 |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Assign Provider

**Path:** `POST /services/requests/{id}/assign`

**Purpose:** Manual assignment

| Property | Value |
|----------|-------|
| **Component** | Assign |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, provider_id` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator |
| **Rate Limit** | 30/min |
| **Notes** | Sends notification |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Search Requests

**Path:** `GET /services/requests/search`

**Purpose:** Search with filters

| Property | Value |
|----------|-------|
| **Component** | Search |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `q, location, date` |
| **Response Data** | `List<Request>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Provider |
| **Rate Limit** | 50/min |
| **Notes** | Fuzzy matching |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Get Nearby

**Path:** `GET /services/requests/nearby`

**Purpose:** Find nearby requests

| Property | Value |
|----------|-------|
| **Component** | Nearby |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `lat, lng, radius, category` |
| **Response Data** | `List<Request>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 100/min |
| **Notes** | PostGIS spatial |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### My Requests

**Path:** `GET /services/requests/my`

**Purpose:** User's own requests

| Property | Value |
|----------|-------|
| **Component** | My |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `status, page` |
| **Response Data** | `List<Request>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Citizen |
| **Rate Limit** | 50/min |
| **Notes** | By user_id |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Assigned to Me

**Path:** `GET /services/requests/assigned`

**Purpose:** Provider's assignments

| Property | Value |
|----------|-------|
| **Component** | Assigned |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `status, page` |
| **Response Data** | `List<Request>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 100/min |
| **Notes** | By provider_id |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |

#### Rate Service

**Path:** `POST /services/requests/{id}/rate`

**Purpose:** Rate completed service

| Property | Value |
|----------|-------|
| **Component** | Rating |
| **Resource** | Request |
| **Status** | Active |
| **Request Data** | `id, rating, review` |
| **Response Data** | `Request` |
| **Auth Required** | Yes |
| **Roles Allowed** | Citizen |
| **Rate Limit** | 10/min |
| **Notes** | Once after completion |
| **Owner Team** | Service |
| **Doc Reference** | Cat3 |


### Disaster Module (9 endpoints)

#### Create Disaster

**Path:** `POST /disasters`

**Purpose:** Declare new disaster

| Property | Value |
|----------|-------|
| **Component** | Form |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `name, type, severity, area, date` |
| **Response Data** | `disaster_id` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 10/min |
| **Notes** | GeoJSON polygon |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### List Disasters

**Path:** `GET /disasters`

**Purpose:** Get all disasters

| Property | Value |
|----------|-------|
| **Component** | List |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `page, type, severity` |
| **Response Data** | `List<Disaster>` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | Paginated |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Get Disaster

**Path:** `GET /disasters/{id}`

**Purpose:** Get details

| Property | Value |
|----------|-------|
| **Component** | Detail |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `Disaster` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | With stats |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Active Disasters

**Path:** `GET /disasters/active`

**Purpose:** Get active only

| Property | Value |
|----------|-------|
| **Component** | Active |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `List<Disaster>` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 200/min |
| **Notes** | For dashboard |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Update Disaster

**Path:** `PUT /disasters/{id}`

**Purpose:** Update details

| Property | Value |
|----------|-------|
| **Component** | Update |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `id, severity, area` |
| **Response Data** | `Disaster` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 20/min |
| **Notes** | Sends alerts |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Close Disaster

**Path:** `POST /disasters/{id}/close`

**Purpose:** Mark resolved

| Property | Value |
|----------|-------|
| **Component** | Close |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `id, notes` |
| **Response Data** | `Disaster` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 10/min |
| **Notes** | Final reports |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Get Stats

**Path:** `GET /disasters/{id}/stats`

**Purpose:** Operational metrics

| Property | Value |
|----------|-------|
| **Component** | Stats |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `stats` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 50/min |
| **Notes** | Real-time |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Map Data

**Path:** `GET /disasters/{id}/map`

**Purpose:** Geographic data

| Property | Value |
|----------|-------|
| **Component** | Map |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `map_data` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | GeoJSON |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |

#### Check Location

**Path:** `POST /disasters/check-location`

**Purpose:** Check if in zone

| Property | Value |
|----------|-------|
| **Component** | Location |
| **Resource** | Event |
| **Status** | Active |
| **Request Data** | `lat, lng` |
| **Response Data** | `List<Disaster>` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 200/min |
| **Notes** | Point-in-polygon |
| **Owner Team** | Disaster |
| **Doc Reference** | Cat3 |


### Organization Module (10 endpoints)

#### Register Org

**Path:** `POST /organizations`

**Purpose:** Provider registration

| Property | Value |
|----------|-------|
| **Component** | Register |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `name, type, services, area, capacity` |
| **Response Data** | `org_id` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 5/min |
| **Notes** | Needs verification |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### List Orgs

**Path:** `GET /organizations`

**Purpose:** Get providers

| Property | Value |
|----------|-------|
| **Component** | List |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `page, service, location` |
| **Response Data** | `List<Org>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Provider |
| **Rate Limit** | 100/min |
| **Notes** | Spatial filter |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Get Org

**Path:** `GET /organizations/{id}`

**Purpose:** Get profile

| Property | Value |
|----------|-------|
| **Component** | Detail |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | Public info |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### My Org

**Path:** `GET /organizations/my`

**Purpose:** Get own org

| Property | Value |
|----------|-------|
| **Component** | My |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider |
| **Rate Limit** | 100/min |
| **Notes** | By user org |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Update Org

**Path:** `PUT /organizations/{id}`

**Purpose:** Update details

| Property | Value |
|----------|-------|
| **Component** | Update |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id, services, capacity` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider (own), Coordinator |
| **Rate Limit** | 20/min |
| **Notes** | Not while assigned |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Verify Org

**Path:** `POST /organizations/{id}/verify`

**Purpose:** Verify documents

| Property | Value |
|----------|-------|
| **Component** | Verify |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id, notes` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 20/min |
| **Notes** | Enables assignments |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Suspend Org

**Path:** `POST /organizations/{id}/suspend`

**Purpose:** Suspend provider

| Property | Value |
|----------|-------|
| **Component** | Suspend |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id, reason` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 10/min |
| **Notes** | Documented reason |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Update Capacity

**Path:** `PUT /organizations/{id}/capacity`

**Purpose:** Update resources

| Property | Value |
|----------|-------|
| **Component** | Capacity |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id, units, type` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider (own) |
| **Rate Limit** | 50/min |
| **Notes** | Affects matching |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Set Availability

**Path:** `PUT /organizations/{id}/availability`

**Purpose:** Set status

| Property | Value |
|----------|-------|
| **Component** | Available |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id, available, until` |
| **Response Data** | `Org` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider (own) |
| **Rate Limit** | 30/min |
| **Notes** | In/out of matching |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |

#### Get Performance

**Path:** `GET /organizations/{id}/performance`

**Purpose:** Performance data

| Property | Value |
|----------|-------|
| **Component** | Performance |
| **Resource** | Org |
| **Status** | Active |
| **Request Data** | `id, period` |
| **Response Data** | `metrics` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 50/min |
| **Notes** | 30 days default |
| **Owner Team** | Org |
| **Doc Reference** | Cat3 |


### Geo Module (5 endpoints)

#### Calculate Distance

**Path:** `POST /geo/distance`

**Purpose:** Haversine distance calc

| Property | Value |
|----------|-------|
| **Component** | Distance |
| **Resource** | Location |
| **Status** | Active |
| **Request Data** | `from{lat,lng}, to{lat,lng}` |
| **Response Data** | `distance_km` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 200/min |
| **Notes** | Returns kilometers |
| **Owner Team** | Geo |
| **Doc Reference** | Cat4 |

#### Find Nearby

**Path:** `POST /geo/nearby`

**Purpose:** PostGIS spatial query

| Property | Value |
|----------|-------|
| **Component** | Nearby |
| **Resource** | Location |
| **Status** | Active |
| **Request Data** | `lat, lng, radius, type` |
| **Response Data** | `List<Entity>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider, Coordinator |
| **Rate Limit** | 100/min |
| **Notes** | ST_DWithin |
| **Owner Team** | Geo |
| **Doc Reference** | Cat4 |

#### Cluster Requests

**Path:** `POST /geo/cluster-requests`

**Purpose:** Identify hotspots

| Property | Value |
|----------|-------|
| **Component** | Cluster |
| **Resource** | Analysis |
| **Status** | Active |
| **Request Data** | `disaster_id, algorithm` |
| **Response Data** | `clusters[]` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator |
| **Rate Limit** | 20/min |
| **Notes** | DBSCAN/K-Means |
| **Owner Team** | Geo |
| **Doc Reference** | Cat4 |

#### Get Map Layer

**Path:** `GET /geo/maps/{layer}`

**Purpose:** Map visualization

| Property | Value |
|----------|-------|
| **Component** | Map |
| **Resource** | Tiles |
| **Status** | Active |
| **Request Data** | `layer, bbox, zoom` |
| **Response Data** | `GeoJSON` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 200/min |
| **Notes** | CDN cached |
| **Owner Team** | Geo |
| **Doc Reference** | Cat4 |

#### Reverse Geocode

**Path:** `GET /geo/reverse-geocode`

**Purpose:** Coords to address

| Property | Value |
|----------|-------|
| **Component** | Geocode |
| **Resource** | Location |
| **Status** | Active |
| **Request Data** | `lat, lng` |
| **Response Data** | `address` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 100/min |
| **Notes** | External API |
| **Owner Team** | Geo |
| **Doc Reference** | Cat4 |


### Notification Module (8 endpoints)

#### Get Notifications

**Path:** `GET /notifications`

**Purpose:** User's notifications

| Property | Value |
|----------|-------|
| **Component** | List |
| **Resource** | Alert |
| **Status** | Active |
| **Request Data** | `page, read, type` |
| **Response Data** | `List<Notification>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 100/min |
| **Notes** | Paginated |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Get Notification

**Path:** `GET /notifications/{id}`

**Purpose:** Single notification

| Property | Value |
|----------|-------|
| **Component** | Detail |
| **Resource** | Alert |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `Notification` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 100/min |
| **Notes** | Mark as read |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Mark as Read

**Path:** `POST /notifications/{id}/read`

**Purpose:** Mark notification read

| Property | Value |
|----------|-------|
| **Component** | Mark |
| **Resource** | Alert |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 50/min |
| **Notes** | Updates status |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Mark All Read

**Path:** `POST /notifications/read-all`

**Purpose:** Mark all as read

| Property | Value |
|----------|-------|
| **Component** | Mark |
| **Resource** | Alert |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 20/min |
| **Notes** | Bulk update |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Get Preferences

**Path:** `GET /notifications/preferences`

**Purpose:** Get notification settings

| Property | Value |
|----------|-------|
| **Component** | Preferences |
| **Resource** | Settings |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `preferences` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 50/min |
| **Notes** | Channel preferences |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Update Preferences

**Path:** `PUT /notifications/preferences`

**Purpose:** Set notification channels

| Property | Value |
|----------|-------|
| **Component** | Preferences |
| **Resource** | Settings |
| **Status** | Active |
| **Request Data** | `email, sms, push, in_app` |
| **Response Data** | `preferences` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 20/min |
| **Notes** | Enable/disable channels |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Unread Count

**Path:** `GET /notifications/unread-count`

**Purpose:** Get unread count

| Property | Value |
|----------|-------|
| **Component** | Unread |
| **Resource** | Alert |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `count` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 200/min |
| **Notes** | For badge display |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |

#### Delete Notification

**Path:** `DELETE /notifications/{id}`

**Purpose:** Remove notification

| Property | Value |
|----------|-------|
| **Component** | Delete |
| **Resource** | Alert |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 30/min |
| **Notes** | Soft delete |
| **Owner Team** | Notif |
| **Doc Reference** | Cat8 |


### Financial Module (12 endpoints)

#### Create Donation

**Path:** `POST /financial/donations`

**Purpose:** Process donation

| Property | Value |
|----------|-------|
| **Component** | Donation |
| **Resource** | Payment |
| **Status** | Active |
| **Request Data** | `amount, disaster_id, donor_info, pan` |
| **Response Data** | `payment_link` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 10/min |
| **Notes** | Min ₹10, Max ₹10L |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Payment Callback

**Path:** `POST /financial/donations/callback`

**Purpose:** Payment gateway callback

| Property | Value |
|----------|-------|
| **Component** | Donation |
| **Resource** | Payment |
| **Status** | Active |
| **Request Data** | `payment_id, order_id, signature` |
| **Response Data** | `status` |
| **Auth Required** | No |
| **Roles Allowed** | System |
| **Rate Limit** | 100/min |
| **Notes** | Razorpay webhook |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Get Donation Stats

**Path:** `GET /financial/donations/stats`

**Purpose:** Donation statistics

| Property | Value |
|----------|-------|
| **Component** | Donation |
| **Resource** | Payment |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `stats` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 50/min |
| **Notes** | Total, count, average |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Allocate Funds

**Path:** `POST /financial/allocations`

**Purpose:** Allocate budget

| Property | Value |
|----------|-------|
| **Component** | Allocation |
| **Resource** | Fund |
| **Status** | Active |
| **Request Data** | `disaster_id, amount, category, org_id, purpose` |
| **Response Data** | `allocation_id` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 20/min |
| **Notes** | Check available funds |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Get Allocations

**Path:** `GET /financial/allocations`

**Purpose:** Get fund allocations

| Property | Value |
|----------|-------|
| **Component** | Allocation |
| **Resource** | Fund |
| **Status** | Active |
| **Request Data** | `disaster_id, page` |
| **Response Data** | `List<Allocation>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 50/min |
| **Notes** | By disaster |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Allocation Summary

**Path:** `GET /financial/allocations/{disaster_id}/summary`

**Purpose:** Allocation overview

| Property | Value |
|----------|-------|
| **Component** | Allocation |
| **Resource** | Fund |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `summary` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 50/min |
| **Notes** | Total allocated, spent |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Record Expenditure

**Path:** `POST /financial/expenditures`

**Purpose:** Record spending

| Property | Value |
|----------|-------|
| **Component** | Expenditure |
| **Resource** | Tracking |
| **Status** | Active |
| **Request Data** | `allocation_id, amount, description, invoice` |
| **Response Data** | `expenditure_id` |
| **Auth Required** | Yes |
| **Roles Allowed** | Provider, Coordinator |
| **Rate Limit** | 30/min |
| **Notes** | Against allocation |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Get Expenditures

**Path:** `GET /financial/expenditures`

**Purpose:** Get spending records

| Property | Value |
|----------|-------|
| **Component** | Expenditure |
| **Resource** | Tracking |
| **Status** | Active |
| **Request Data** | `disaster_id, allocation_id, page` |
| **Response Data** | `List<Expenditure>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 50/min |
| **Notes** | Filtered query |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Transparency Report

**Path:** `GET /financial/reports/transparency/{disaster_id}`

**Purpose:** Generate report

| Property | Value |
|----------|-------|
| **Component** | Report |
| **Resource** | Document |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `PDF` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 10/min |
| **Notes** | Public transparency |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### 80G Certificate

**Path:** `GET /financial/reports/80g/{transaction_id}`

**Purpose:** Tax certificate

| Property | Value |
|----------|-------|
| **Component** | Report |
| **Resource** | Document |
| **Status** | Active |
| **Request Data** | `transaction_id` |
| **Response Data** | `PDF` |
| **Auth Required** | Yes |
| **Roles Allowed** | Donor |
| **Rate Limit** | 20/min |
| **Notes** | PAN required |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Financial Overview

**Path:** `GET /financial/dashboard/{disaster_id}`

**Purpose:** Financial metrics

| Property | Value |
|----------|-------|
| **Component** | Dashboard |
| **Resource** | Analytics |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `dashboard_data` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 50/min |
| **Notes** | KPIs + charts |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |

#### Public Dashboard

**Path:** `GET /financial/public/{disaster_id}`

**Purpose:** Public financial info

| Property | Value |
|----------|-------|
| **Component** | Transparency |
| **Resource** | Public |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `public_data` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 100/min |
| **Notes** | Cached, no auth |
| **Owner Team** | Finance |
| **Doc Reference** | Cat12 |


### Analytics Module (10 endpoints)

#### Overview Metrics

**Path:** `GET /analytics/dashboard/overview`

**Purpose:** System-wide KPIs

| Property | Value |
|----------|-------|
| **Component** | Dashboard |
| **Resource** | Metrics |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `metrics` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 50/min |
| **Notes** | Real-time data |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Disaster Metrics

**Path:** `GET /analytics/dashboard/disaster/{id}`

**Purpose:** Disaster-specific KPIs

| Property | Value |
|----------|-------|
| **Component** | Dashboard |
| **Resource** | Metrics |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `metrics` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 50/min |
| **Notes** | Per disaster |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Service Trends

**Path:** `GET /analytics/trends/services`

**Purpose:** Daily service trends

| Property | Value |
|----------|-------|
| **Component** | Trends |
| **Resource** | Analysis |
| **Status** | Active |
| **Request Data** | `disaster_id, days` |
| **Response Data** | `trend_data` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator |
| **Rate Limit** | 30/min |
| **Notes** | Time series |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Provider Performance

**Path:** `GET /analytics/providers/performance`

**Purpose:** Top provider rankings

| Property | Value |
|----------|-------|
| **Component** | Performance |
| **Resource** | Provider |
| **Status** | Active |
| **Request Data** | `top_n, period` |
| **Response Data** | `List<ProviderMetrics>` |
| **Auth Required** | Yes |
| **Roles Allowed** | All |
| **Rate Limit** | 50/min |
| **Notes** | Sorted by rating |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Category Distribution

**Path:** `GET /analytics/distribution/category`

**Purpose:** Request breakdown

| Property | Value |
|----------|-------|
| **Component** | Distribution |
| **Resource** | Category |
| **Status** | Active |
| **Request Data** | `disaster_id` |
| **Response Data** | `distribution` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator |
| **Rate Limit** | 50/min |
| **Notes** | Pie chart data |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Generate Chart

**Path:** `GET /analytics/charts/trends`

**Purpose:** Plotly chart data

| Property | Value |
|----------|-------|
| **Component** | Charts |
| **Resource** | Visualization |
| **Status** | Active |
| **Request Data** | `type, disaster_id, days` |
| **Response Data** | `chart_json` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator |
| **Rate Limit** | 30/min |
| **Notes** | Interactive charts |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Generate Report

**Path:** `GET /analytics/reports/disaster/{id}`

**Purpose:** Disaster report

| Property | Value |
|----------|-------|
| **Component** | Reports |
| **Resource** | Document |
| **Status** | Active |
| **Request Data** | `id, format (pdf/excel)` |
| **Response Data** | `file` |
| **Auth Required** | Yes |
| **Roles Allowed** | Coordinator, Admin |
| **Rate Limit** | 10/min |
| **Notes** | PDF or Excel |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### User Activity Report

**Path:** `GET /analytics/audit/user-activity`

**Purpose:** Audit trail

| Property | Value |
|----------|-------|
| **Component** | Audit |
| **Resource** | Compliance |
| **Status** | Active |
| **Request Data** | `user_id, period` |
| **Response Data** | `activity_data` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | Compliance report |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Security Report

**Path:** `GET /analytics/audit/security`

**Purpose:** Security incidents

| Property | Value |
|----------|-------|
| **Component** | Audit |
| **Resource** | Compliance |
| **Status** | Active |
| **Request Data** | `period` |
| **Response Data** | `security_events` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | Failed logins, etc |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |

#### Export Data

**Path:** `GET /analytics/export`

**Purpose:** Data export

| Property | Value |
|----------|-------|
| **Component** | Export |
| **Resource** | Data |
| **Status** | Active |
| **Request Data** | `disaster_id, entity, format` |
| **Response Data** | `file` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 5/min |
| **Notes** | CSV/Excel export |
| **Owner Team** | Analytics |
| **Doc Reference** | Cat11 |


### Files Module (6 endpoints)

#### Upload File

**Path:** `POST /files/upload`

**Purpose:** Upload to S3/MinIO

| Property | Value |
|----------|-------|
| **Component** | Upload |
| **Resource** | Storage |
| **Status** | Active |
| **Request Data** | `file, entity_type, entity_id` |
| **Response Data** | `file_url` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 20/min |
| **Notes** | Max 100MB |
| **Owner Team** | Files |
| **Doc Reference** | Cat8 |

#### Download File

**Path:** `GET /files/{file_id}`

**Purpose:** Get file

| Property | Value |
|----------|-------|
| **Component** | Download |
| **Resource** | Storage |
| **Status** | Active |
| **Request Data** | `file_id` |
| **Response Data** | `file` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 100/min |
| **Notes** | Presigned URL |
| **Owner Team** | Files |
| **Doc Reference** | Cat8 |

#### List Files

**Path:** `GET /files`

**Purpose:** Get files for entity

| Property | Value |
|----------|-------|
| **Component** | List |
| **Resource** | Storage |
| **Status** | Active |
| **Request Data** | `entity_type, entity_id, page` |
| **Response Data** | `List<File>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 50/min |
| **Notes** | By entity |
| **Owner Team** | Files |
| **Doc Reference** | Cat8 |

#### Delete File

**Path:** `DELETE /files/{file_id}`

**Purpose:** Remove file

| Property | Value |
|----------|-------|
| **Component** | Delete |
| **Resource** | Storage |
| **Status** | Active |
| **Request Data** | `file_id` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Owner, Admin |
| **Rate Limit** | 20/min |
| **Notes** | Soft delete |
| **Owner Team** | Files |
| **Doc Reference** | Cat8 |

#### Get Presigned URL

**Path:** `GET /files/{file_id}/url`

**Purpose:** Temporary download link

| Property | Value |
|----------|-------|
| **Component** | URL |
| **Resource** | Storage |
| **Status** | Active |
| **Request Data** | `file_id, expires` |
| **Response Data** | `url` |
| **Auth Required** | Yes |
| **Roles Allowed** | Authenticated |
| **Rate Limit** | 100/min |
| **Notes** | Expires in 1h |
| **Owner Team** | Files |
| **Doc Reference** | Cat8 |

#### Update Metadata

**Path:** `PUT /files/{file_id}/metadata`

**Purpose:** Update file info

| Property | Value |
|----------|-------|
| **Component** | Metadata |
| **Resource** | Storage |
| **Status** | Active |
| **Request Data** | `file_id, title, description` |
| **Response Data** | `file` |
| **Auth Required** | Yes |
| **Roles Allowed** | Owner, Admin |
| **Rate Limit** | 30/min |
| **Notes** | Metadata only |
| **Owner Team** | Files |
| **Doc Reference** | Cat8 |


### User Module (8 endpoints)

#### List Users

**Path:** `GET /users`

**Purpose:** Get all users

| Property | Value |
|----------|-------|
| **Component** | List |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `page, role, status` |
| **Response Data** | `List<User>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin, Coordinator |
| **Rate Limit** | 50/min |
| **Notes** | Admin panel |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### Get User

**Path:** `GET /users/{id}`

**Purpose:** Get user details

| Property | Value |
|----------|-------|
| **Component** | Detail |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `User` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin, Coordinator |
| **Rate Limit** | 100/min |
| **Notes** | User profile |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### Update User

**Path:** `PUT /users/{id}`

**Purpose:** Update user

| Property | Value |
|----------|-------|
| **Component** | Update |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `id, name, phone, status` |
| **Response Data** | `User` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | Admin only |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### Change Role

**Path:** `PUT /users/{id}/role`

**Purpose:** Update user role

| Property | Value |
|----------|-------|
| **Component** | Role |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `id, role` |
| **Response Data** | `User` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 10/min |
| **Notes** | RBAC change |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### Activate User

**Path:** `POST /users/{id}/activate`

**Purpose:** Activate account

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `User` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | Enable access |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### Deactivate User

**Path:** `POST /users/{id}/deactivate`

**Purpose:** Disable account

| Property | Value |
|----------|-------|
| **Component** | Status |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `id` |
| **Response Data** | `User` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | Suspend access |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### Search Users

**Path:** `GET /users/search`

**Purpose:** Find users

| Property | Value |
|----------|-------|
| **Component** | Search |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `q, role, status` |
| **Response Data** | `List<User>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin, Coordinator |
| **Rate Limit** | 50/min |
| **Notes** | Full-text search |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |

#### User Activity Log

**Path:** `GET /users/{id}/activity`

**Purpose:** Audit trail

| Property | Value |
|----------|-------|
| **Component** | Activity |
| **Resource** | User |
| **Status** | Active |
| **Request Data** | `id, period` |
| **Response Data** | `activity_log` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 30/min |
| **Notes** | User actions |
| **Owner Team** | User |
| **Doc Reference** | Cat2 |


### System Module (10 endpoints)

#### Health Check

**Path:** `GET /health`

**Purpose:** System health

| Property | Value |
|----------|-------|
| **Component** | Health |
| **Resource** | Monitor |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `status` |
| **Auth Required** | No |
| **Roles Allowed** | Public |
| **Rate Limit** | 500/min |
| **Notes** | For monitoring |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Liveness Probe

**Path:** `GET /health/live`

**Purpose:** Is service alive

| Property | Value |
|----------|-------|
| **Component** | Health |
| **Resource** | Monitor |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `status` |
| **Auth Required** | No |
| **Roles Allowed** | K8s |
| **Rate Limit** | 1000/min |
| **Notes** | Kubernetes probe |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Readiness Probe

**Path:** `GET /health/ready`

**Purpose:** Ready for traffic

| Property | Value |
|----------|-------|
| **Component** | Health |
| **Resource** | Monitor |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `status` |
| **Auth Required** | No |
| **Roles Allowed** | K8s |
| **Rate Limit** | 1000/min |
| **Notes** | Kubernetes probe |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Prometheus Metrics

**Path:** `GET /metrics`

**Purpose:** Scrape endpoint

| Property | Value |
|----------|-------|
| **Component** | Metrics |
| **Resource** | Monitor |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `metrics` |
| **Auth Required** | No |
| **Roles Allowed** | Prometheus |
| **Rate Limit** | 200/min |
| **Notes** | Time series data |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Get System Config

**Path:** `GET /admin/config`

**Purpose:** System settings

| Property | Value |
|----------|-------|
| **Component** | Config |
| **Resource** | Admin |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `config` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | App configuration |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Update Config

**Path:** `PUT /admin/config`

**Purpose:** Update setting

| Property | Value |
|----------|-------|
| **Component** | Config |
| **Resource** | Admin |
| **Status** | Active |
| **Request Data** | `key, value` |
| **Response Data** | `config` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 10/min |
| **Notes** | Hot reload |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Clear Cache

**Path:** `POST /admin/cache/clear`

**Purpose:** Invalidate cache

| Property | Value |
|----------|-------|
| **Component** | Cache |
| **Resource** | Admin |
| **Status** | Active |
| **Request Data** | `pattern` |
| **Response Data** | `success` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 10/min |
| **Notes** | Redis pattern |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### View Logs

**Path:** `GET /admin/logs`

**Purpose:** Recent logs

| Property | Value |
|----------|-------|
| **Component** | Logs |
| **Resource** | Admin |
| **Status** | Active |
| **Request Data** | `level, service, limit` |
| **Response Data** | `logs[]` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 20/min |
| **Notes** | Last 100 default |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### List Celery Tasks

**Path:** `GET /admin/tasks`

**Purpose:** Async tasks

| Property | Value |
|----------|-------|
| **Component** | Tasks |
| **Resource** | Admin |
| **Status** | Active |
| **Request Data** | `status, page` |
| **Response Data** | `List<Task>` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 30/min |
| **Notes** | Background jobs |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |

#### Database Stats

**Path:** `GET /admin/database/stats`

**Purpose:** DB metrics

| Property | Value |
|----------|-------|
| **Component** | Database |
| **Resource** | Admin |
| **Status** | Active |
| **Request Data** | `nan` |
| **Response Data** | `stats` |
| **Auth Required** | Yes |
| **Roles Allowed** | Admin |
| **Rate Limit** | 10/min |
| **Notes** | Connections, queries |
| **Owner Team** | System |
| **Doc Reference** | Cat10 |


---

## Error Response Reference

### HTTP Status Codes

#### 400 - Bad Request

**Applies to:** All Endpoints

**When it happens:** Invalid input data, missing required fields, malformed JSON

**Example Response:**
```json
{"error": "Bad Request", "details": "Field 'email' is required"}
```

---

#### 401 - Unauthorized

**Applies to:** All Endpoints

**When it happens:** Missing or invalid authentication token

**Example Response:**
```json
{"error": "Unauthorized", "message": "Invalid or expired token"}
```

---

#### 403 - Forbidden

**Applies to:** All Endpoints

**When it happens:** User lacks permission for this action

**Example Response:**
```json
{"error": "Forbidden", "message": "Admin role required"}
```

---

#### 404 - Not Found

**Applies to:** All Endpoints

**When it happens:** Resource doesn't exist at specified ID

**Example Response:**
```json
{"error": "Not Found", "message": "Service request not found"}
```

---

#### 409 - Conflict

**Applies to:** All Endpoints

**When it happens:** Resource already exists or state conflict

**Example Response:**
```json
{"error": "Conflict", "message": "Email already registered"}
```

---

#### 422 - Unprocessable Entity

**Applies to:** All Endpoints

**When it happens:** Validation failed, semantic errors

**Example Response:**
```json
{"error": "Validation Error", "fields": {"lat": "Invalid latitude"}}
```

---

#### 429 - Too Many Requests

**Applies to:** All Endpoints

**When it happens:** Rate limit exceeded

**Example Response:**
```json
{"error": "Rate Limit Exceeded", "retry_after": 60}
```

---

#### 500 - Internal Server Error

**Applies to:** All Endpoints

**When it happens:** Unexpected server error, bugs

**Example Response:**
```json
{"error": "Internal Server Error", "message": "Something went wrong"}
```

---

#### 502 - Bad Gateway

**Applies to:** All Endpoints

**When it happens:** Upstream service unavailable

**Example Response:**
```json
{"error": "Bad Gateway", "message": "Payment gateway timeout"}
```

---

#### 503 - Service Unavailable

**Applies to:** All Endpoints

**When it happens:** System maintenance or overload

**Example Response:**
```json
{"error": "Service Unavailable", "message": "System under maintenance"}
```

---

#### 504 - Gateway Timeout

**Applies to:** All Endpoints

**When it happens:** Request timeout, long operation

**Example Response:**
```json
{"error": "Gateway Timeout", "message": "Operation took too long"}
```

---

#### 401 - Invalid Credentials

**Applies to:** /auth/*

**When it happens:** Wrong email or password

**Example Response:**
```json
{"error": "Invalid Credentials"}
```

---

#### 403 - Account Locked

**Applies to:** /auth/*

**When it happens:** Too many failed login attempts

**Example Response:**
```json
{"error": "Account Locked", "unlock_at": "2024-12-23T10:30:00Z"}
```

---

#### 409 - Email Already Exists

**Applies to:** /auth/*

**When it happens:** Email already registered

**Example Response:**
```json
{"error": "Email already in use"}
```

---

#### 410 - Token Expired

**Applies to:** /auth/*

**When it happens:** Reset token or verification token expired

**Example Response:**
```json
{"error": "Token Expired"}
```

---

#### 400 - Invalid Location

**Applies to:** /services/*

**When it happens:** Lat/lng outside valid range

**Example Response:**
```json
{"error": "Invalid location", "details": "Latitude must be -90 to 90"}
```

---

#### 403 - Cannot Modify

**Applies to:** /services/*

**When it happens:** Cannot update assigned or completed request

**Example Response:**
```json
{"error": "Request is already assigned"}
```

---

#### 404 - Request Not Found

**Applies to:** /services/*

**When it happens:** Service request ID doesn't exist

**Example Response:**
```json
{"error": "Service request not found"}
```

---

#### 409 - Already Accepted

**Applies to:** /services/*

**When it happens:** Provider already accepted this request

**Example Response:**
```json
{"error": "Request already accepted by another provider"}
```

---

#### 400 - Invalid Service Area

**Applies to:** /organizations/*

**When it happens:** Service area polygon malformed

**Example Response:**
```json
{"error": "Invalid GeoJSON polygon"}
```

---

#### 403 - Not Verified

**Applies to:** /organizations/*

**When it happens:** Organization not yet verified

**Example Response:**
```json
{"error": "Organization pending verification"}
```

---

#### 409 - Org Already Exists

**Applies to:** /organizations/*

**When it happens:** Organization name already registered

**Example Response:**
```json
{"error": "Organization name already exists"}
```

---

#### 400 - Invalid Amount

**Applies to:** /financial/*

**When it happens:** Amount below minimum or above maximum

**Example Response:**
```json
{"error": "Amount must be between ₹10 and ₹10,00,000"}
```

---

#### 402 - Payment Required

**Applies to:** /financial/*

**When it happens:** Payment verification failed

**Example Response:**
```json
{"error": "Payment verification failed"}
```

---

#### 403 - Insufficient Funds

**Applies to:** /financial/*

**When it happens:** Allocation exceeds available funds

**Example Response:**
```json
{"error": "Insufficient funds", "available": 50000}
```

---

#### 400 - Invalid Coordinates

**Applies to:** /geo/*

**When it happens:** Lat/lng format incorrect

**Example Response:**
```json
{"error": "Invalid coordinate format"}
```

---

#### 422 - Clustering Failed

**Applies to:** /geo/*

**When it happens:** Not enough data points for clustering

**Example Response:**
```json
{"error": "Minimum 10 requests required for clustering"}
```

---

#### 400 - Invalid File Type

**Applies to:** /files/*

**When it happens:** File type not allowed

**Example Response:**
```json
{"error": "Only PDF, JPG, PNG allowed"}
```

---

#### 413 - File Too Large

**Applies to:** /files/*

**When it happens:** File exceeds size limit

**Example Response:**
```json
{"error": "File size must be under 100MB"}
```

---

#### 404 - File Not Found

**Applies to:** /files/*

**When it happens:** File ID doesn't exist

**Example Response:**
```json
{"error": "File not found"}
```

---

#### 1000 - Normal Closure

**Applies to:** WebSocket

**When it happens:** Client closed connection normally

---

#### 1001 - Going Away

**Applies to:** WebSocket

**When it happens:** Server shutting down

---

#### 1002 - Protocol Error

**Applies to:** WebSocket

**When it happens:** WebSocket protocol violation

---

#### 1003 - Unsupported Data

**Applies to:** WebSocket

**When it happens:** Data type not accepted

---

#### 1008 - Policy Violation

**Applies to:** WebSocket

**When it happens:** Message violates policy (too large, rate limit)

---

#### 1011 - Internal Error

**Applies to:** WebSocket

**When it happens:** Server error in WebSocket handler

---


## Quick Reference Tables

### By Module

| Module | Endpoints | Key Features |
|--------|-----------|-------------|
| Auth | 11 | Registration, Login, JWT, Password Management |
| Service Request | 16 | Create, Track, Assign, Complete, Rate Services |
| Disaster | 9 | Declare, Track, Close Disasters |
| Organization | 11 | Provider Registration, Verification, Capacity |
| Geospatial | 5 | Distance, Proximity, Clustering, Maps |
| Notification | 8 | Alerts, Preferences, Unread Count |
| Financial | 12 | Donations, Allocations, Expenditure, Reports |
| Analytics | 10 | Dashboards, Trends, Performance, Audit |
| Files | 6 | Upload, Download, Storage Management |
| User | 8 | User CRUD, Roles, Activity Logs |
| System | 10 | Health, Monitoring, Configuration |

### By HTTP Method

| Method | Count | Purpose |
|--------|-------|---------|
| GET | 52 | Retrieve data, list resources, view details |
| POST | 35 | Create resources, submit actions, process requests |
| PUT | 14 | Update existing resources, modify state |
| DELETE | 3 | Remove resources (soft delete) |
| Other | 1 | WebSocket connections |

### By Authentication Requirement

| Auth Type | Count | Description |
|-----------|-------|-------------|
| Yes - Authenticated | 88 | Requires valid JWT token |
| No - Public | 13 | Open access (register, login, health checks) |
| System Only | 4 | Internal system calls (webhooks, K8s probes) |

### By Role Access

| Role | Accessible Endpoints | Description |
|------|---------------------|-------------|
| **Admin** | 105 (all) | Full system access |
| **Coordinator** | 75+ | Disaster management, resource allocation |
| **Provider** | 50+ | Service requests, organization management |
| **Citizen** | 40+ | Create requests, track status, rate services |
| **Public** | 13 | Registration, login, health checks |

---

## Authentication Guide

### Getting Started

1. **Register:** `POST /auth/register`
2. **Login:** `POST /auth/login` - Returns `access_token` and `refresh_token`
3. **Use Token:** Add header `Authorization: Bearer {access_token}` to all authenticated requests
4. **Refresh:** When access token expires (1 hour), use `POST /auth/refresh` with refresh token
5. **Logout:** `POST /auth/logout` to invalidate tokens

### JWT Token Structure

```
Header: Bearer <token>

Token contains:
- user_id
- email
- role
- permissions
- exp (expiry timestamp)
```

---

## Rate Limiting Guide

### Rate Limit Tiers

| Tier | Limit | Applies To |
|------|-------|------------|
| Very High | 500-1000/min | Health checks, system probes |
| High | 100-200/min | Read operations (GET), public dashboards |
| Medium | 30-100/min | Authenticated reads, searches |
| Low | 10-30/min | Write operations, assignments |
| Very Low | 3-10/min | Sensitive operations (password reset, admin actions) |

### Rate Limit Headers

Every response includes:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000 (Unix timestamp)
```

---

## Common Workflows

### Citizen Requesting Help

1. **Register/Login** → `POST /auth/register` or `POST /auth/login`
2. **Create Request** → `POST /services/requests` with location, category, description
3. **Track Status** → `GET /services/requests/{id}` or via WebSocket updates
4. **Rate Service** → `POST /services/requests/{id}/rate` after completion

### Provider Responding

1. **Register Organization** → `POST /organizations`
2. **Wait for Verification** → Coordinator calls `POST /organizations/{id}/verify`
3. **View Nearby Requests** → `GET /services/requests/nearby?lat=...&lng=...`
4. **Accept Request** → `POST /services/requests/{id}/accept`
5. **Update Status** → `POST /services/requests/{id}/start`, then `/complete`

### Coordinator Managing Disaster

1. **Declare Disaster** → `POST /disasters` with affected area polygon
2. **View Dashboard** → `GET /analytics/dashboard/disaster/{id}`
3. **Monitor Requests** → `GET /services/requests?disaster_id={id}`
4. **Manual Assignment** → `POST /services/requests/{id}/assign`
5. **Generate Reports** → `GET /analytics/reports/disaster/{id}`

### Donor Contributing

1. **Create Donation** → `POST /financial/donations` → Receive payment link
2. **Complete Payment** → External (Razorpay)
3. **Payment Callback** → System calls `POST /financial/donations/callback`
4. **Get Receipt** → `GET /financial/reports/80g/{transaction_id}`
5. **Track Impact** → `GET /financial/public/{disaster_id}`

---

## WebSocket Events

### Connection

```javascript
const socket = io('wss://api.idrm.gov.in', {
  auth: {
    token: 'your_jwt_token'
  }
});
```

### Event Channels

| Channel | Events | Purpose |
|---------|--------|---------|
| `service` | request_created, request_assigned, status_changed | Service request updates |
| `disaster` | disaster_declared, disaster_updated, disaster_closed | Disaster alerts |
| `notification` | new_notification, alert | Real-time notifications |
| `chat` | message | In-app messaging |
| `system` | maintenance, announcement | System-wide messages |

### Subscribe to Events

```javascript
// Join disaster-specific room
socket.emit('join_disaster', {disaster_id: '123'});

// Listen for events
socket.on('request_assigned', (data) => {
  console.log('Provider assigned:', data);
});
```

---

## Data Models Reference

### ServiceRequest

```typescript
{
  id: string (UUID)
  category: 'food' | 'water' | 'medical' | 'shelter' | 'evacuation' | 'search_rescue' | 'relief_supplies' | 'other'
  title: string
  description: string
  location: { lat: number, lng: number }
  address: string
  priority: 1 | 2 | 3 | 4 | 5
  urgency: 'low' | 'medium' | 'high' | 'critical'
  status: 'pending' | 'assigned' | 'in_progress' | 'completed' | 'cancelled'
  beneficiaries: number
  contact_phone: string
  created_by: string (user_id)
  assigned_to: string | null (organization_id)
  disaster_event_id: string | null
  created_at: datetime
  updated_at: datetime
}
```

### DisasterEvent

```typescript
{
  id: string (UUID)
  name: string
  type: 'earthquake' | 'flood' | 'cyclone' | 'fire' | 'other'
  severity: 'low' | 'medium' | 'high' | 'extreme'
  affected_area: GeoJSON Polygon
  start_date: datetime
  end_date: datetime | null
  status: 'active' | 'resolved' | 'closed'
  estimated_affected: number
  description: string
}
```

### Organization

```typescript
{
  id: string (UUID)
  name: string
  type: 'ngo' | 'government' | 'corporate' | 'volunteer'
  service_categories: string[]
  service_area: { lat: number, lng: number }
  service_radius_km: number
  capacity: number
  available_capacity: number
  is_available: boolean
  is_verified: boolean
  rating: number (0-5)
  total_requests_completed: number
}
```

---

## Response Format Standards

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "message": "Operation successful"
}
```

### Error Response

```json
{
  "error": "Error Type",
  "message": "Human-readable message",
  "details": { ... },
  "timestamp": "2024-12-23T10:30:00Z",
  "path": "/api/endpoint"
}
```

### Paginated Response

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total_pages": 5,
    "total_items": 95
  }
}
```

---

## Support & Documentation

- **Primary Documentation:** Category-wise LLD documents (Categories 1-12)
- **API Testing:** Use Postman collection or Swagger UI at `/docs`
- **Issue Reporting:** Contact IDRM Development Team
- **Rate Limit Issues:** Contact admin for increased limits

---

**Document Version:** 1.0  
**Last Updated:** December 23, 2024  
**Total Endpoints:** 105  
**Status:** ✅ Complete - Production Ready
