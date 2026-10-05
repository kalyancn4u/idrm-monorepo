# IDRM MVP — API Specification

> *Type: Document (specification) · Audience: developers, testers, integrators · Status: MVP — current*
> *The client↔backend contract. Consolidated from the archived v3 API spec and the `../assets/idrm-api-resource-mapping.xlsx` matrix, standardized to the canonical scheme confirmed 2026-08-12. Endpoints trace to the features in [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) (F1–F11) and the lifecycle in its §4. The machine-readable contract is [`40-api-openapi.yaml`](40-api-openapi.yaml).*

> **API-first:** the contract is a **product**, not an afterthought. The same contract is consumed by the
> MVP's HTML/Tailwind/JS UI **and**, unchanged, by future React/mobile clients. **URIs never change across
> the SDLC** (see [hand-off §12](../../archive/instructions.txt)) — the FFP *adds* endpoints at these same paths; it
> never renames them.

---

## 1. How to read this document

- **§2 Conventions** are frozen rules that apply to *every* endpoint — read them once.
- **§3 Auth** explains the token model at contract level (full security in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md)).
- **§4 Resource catalog** is the canonical URI map (MVP subset + where FFP extends).
- **§5 Endpoints** specify each operation, grouped by resource, tagged with the **Feature** (F1–F11) it serves.
- **§6 Errors** is the shared error catalog.

Vocabulary: the UI term **"help request"** is the API resource **`incident`** — the core record a citizen
(or guest) creates to ask for help at a location.

> **Key terms (expanded once):** **API** = Application Programming Interface — the defined way one program talks
> to another; here, how *any* client (web now, mobile later) talks to IDRM · **URI** = the address of a resource
> (e.g. `/api/v1/incidents`) · **UUID** = Universally Unique Identifier (a random, non-guessable id) · **JSON** =
> the plain-text data format used for request/response bodies · **SDLC** = Software Development Life Cycle
> (build → test → run → evolve — the URIs stay stable across all of it).

---

## 2. API conventions (v1 — frozen)

**Base & versioning**
- All endpoints live under **`/api/v1`**. The version is in the **path**. Breaking changes → `/api/v2`;
  additive changes never bump the version. The FFP keeps `/api/v1`.
- Environment base URLs are configured per deployment (e.g. `https://<host>/api/v1`); the spec uses
  **relative** paths so it is host-independent.

**URIs**
- Resources are **plural, lowercase nouns**, kebab-case when multi-word: `/incidents`, `/organizations`, `/audit-logs`.
- Collection vs item: `GET /incidents` (list) · `GET /incidents/{id}` (one). Sub-resources nest **one** level: `/incidents/{id}/updates`.
- **Lifecycle transitions are dedicated endpoints** (each has its own role, body, and side-effects):
  `POST /incidents/{id}/{accept|start|complete|verify|cancel}` and coordinator `…/{approve|reject}`.

**HTTP methods** — `GET` read · `POST` create & transitions · `PATCH` partial update · `DELETE` reserved
(records are **soft-cancelled**, never hard-deleted).

**Request / response bodies** — JSON, `Content-Type: application/json; charset=utf-8`.
- Field names are **`snake_case`**.
- **Identifiers are UUID strings** (`id`), never guessable sequential integers.
- **Timestamps** are ISO-8601 **UTC**, always suffixed `_at` (`created_at`, `updated_at`).
- **Coordinates**: request inputs use explicit `{"latitude": <num>, "longitude": <num>}`; map-layer
  responses use **GeoJSON**.
- **Enum wire values are lowercase snake_case** (e.g. `service_type: "medical"`, `status: "in_progress"`).
  The UI shows friendly labels; the wire stays machine-stable.
- **Response shape**: a single resource is returned as a **bare object**; a **collection** is wrapped:
  `{ "data": [ … ], "pagination": { … } }`.

**Collections** — `?page=1&limit=20` (default `limit` 20, max 100). Wrapper:
```json
"pagination": { "page": 1, "limit": 20, "total": 137, "total_pages": 7 }
```
- **Filter** by field: `?status=accepted&service_type=medical&priority=critical`.
- **Sort**: `?sort=-created_at` (leading `-` = descending).
- **Search**: `?q=<text>`. **Proximity**: `?latitude=..&longitude=..&radius_km=..`.

**Auth** — `Authorization: Bearer <access_token>` (JWT). Public endpoints are marked. See §3.

**Rate limiting** — per-endpoint budgets (carried from the resource-mapping asset); exceeding returns
**`429`** with a `Retry-After` header (seconds).

**Standard headers** — `Accept-Language: en | te | hi …` selects response language for user-facing
messages (F11, multi-language-ready). `X-Request-Id` is echoed on every response for tracing.

**Enumerations (canonical wire values)**

| Enum | Values |
|---|---|
| `role` | `citizen` · `provider` · `coordinator` · `admin` |
| `service_type` | `medical` · `food` · `rescue` · `water` · `shelter` · `other` |
| `priority` | `low` · `medium` · `high` · `critical` |
| `status` (incident) | `created` · `approved` · `accepted` · `in_progress` · `completed` · `verified` · `cancelled` · `rejected` |

*(FFP adds values/resources — e.g. a `disputed` status, `disaster`/`financial` resources — at the same
paths, never renaming these.)*

---

## 3. Authentication & authorization (contract level)

- **Login** returns a short-lived **`access_token`** and a longer-lived **`refresh_token`**. Clients send
  `Authorization: Bearer <access_token>` on every authenticated call; when it expires they call
  `POST /auth/refresh`. Token lifetimes, signing (JWT RS256), hashing, and lockout policy live in
  [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md).
- **Roles** (`citizen`, `provider`, `coordinator`, `admin`) gate operations. Each endpoint below lists its
  allowed roles; an out-of-role call returns **`403`** (`code: forbidden`). `admin` is the platform
  administrator (superset of `coordinator`).
- **Guest emergency (F1/AC-1.4):** `POST /incidents` accepts an **anonymous** submission for life-safety
  (stricter rate limit); the response returns a **`tracking_token`** the guest can use to follow the one
  request without an account.

---

## 4. Resource catalog (canonical URIs)

| Resource | Path root | MVP | Serves |
|---|---|:--:|---|
| Authentication | `/api/v1/auth` | ✅ | F1 |
| Users | `/api/v1/users` | ✅ | F1 |
| **Incidents** (help requests) | `/api/v1/incidents` | ✅ | F2–F5, F7, F8 |
| Organizations (providers) | `/api/v1/organizations` | ✅ | F3, F4, F8 |
| Resources (provider assets) | `/api/v1/resources` | ✅ | F3 |
| Locations / geo | `/api/v1/locations` | ✅ | F3, F4 |
| Alerts (coordinator broadcasts) | `/api/v1/alerts` | ✅ | F8 |
| Notifications | `/api/v1/notifications` | ✅ | F6 |
| Reports | `/api/v1/reports` | ✅ | F8, F10 |
| Audit logs | `/api/v1/audit-logs` | ✅ | F9 |
| Files (uploads) | `/api/v1/files` | ✅ | F2, F5 |
| System (health) | `/api/v1/health` | ✅ | ops |
| *Disasters* | `/api/v1/disasters` | → FFP | (event entity — deferred) |
| *Financial* | `/api/v1/financial` | → FFP | (donations/funds — deferred) |
| *Realtime* | websocket channel | → FFP | (deep push — deferred) |

---

## 5. Endpoint specifications

> Each row: **Method · Path · Auth/Roles · Purpose · Key request → response · Main errors · Rate**. Bodies
> show *key* fields; the full schemas are in [`40-api-openapi.yaml`](40-api-openapi.yaml). All list endpoints
> honour the pagination/filter/sort rules in §2.

### 5.1 Authentication & users — F1

| Method · Path | Auth · Roles | Purpose | Key request → response | Errors | Rate |
|---|---|---|---|---|---|
| `POST /auth/register` | Public | Create an account (AC-1.1/1.2) | `email, password, name, phone, role` → `user_id`, verification sent | `409 email_exists`, `422` | 10/min |
| `POST /auth/verify-email` | Public | Activate via emailed token | `token` → `success` | `410 token_expired` | 10/min |
| `POST /auth/resend-verification` | Public | Resend link | `email` → `message` | `429` | 3/min |
| `POST /auth/login` | Public | Authenticate (AC-1.3) | `email, password` → `access_token, refresh_token, user` | `401 invalid_credentials`, `403 account_locked` | 5/min |
| `POST /auth/refresh` | Public* | Exchange refresh for new access | `refresh_token` → `access_token` | `401` | 10/min |
| `POST /auth/logout` | Bearer | End session (AC-1.3) | `refresh_token` → `success` | `401` | 20/min |
| `POST /auth/forgot-password` | Public | Request reset link | `email` → `message` | `429` | 3/min |
| `POST /auth/reset-password` | Public | Reset via token | `token, new_password` → `success` | `410 token_expired`, `422` | 5/min |
| `POST /auth/change-password` | Bearer | Change while logged in | `current_password, new_password` → `success` | `401`, `422` | 10/min |
| `GET /users/me` | Bearer · all | Current user profile | — → `User` | `401` | 100/min |
| `PATCH /users/me` | Bearer · all | Update own profile (not email/role) | `name?, phone?, language?` → `User` | `422` | 20/min |
| `GET /users` | Bearer · coordinator, admin | List/manage users (AC-1.5) | filters → `{data:[User], pagination}` | `403` | 100/min |
| `GET /users/{id}` | Bearer · coordinator, admin | View one user | — → `User` | `403`, `404` | 100/min |
| `PATCH /users/{id}` | Bearer · admin | Change a user's role/status (audited) | `role?, status?` → `User` | `403`, `404` | 20/min |

\* `/auth/refresh` is unauthenticated at the access-token level but requires a valid refresh token.

### 5.2 Incidents (help requests) — F2, F3, F4, F5, F7, F8

**Core CRUD & views**

| Method · Path | Auth · Roles | Purpose | Key request → response | Errors | Rate |
|---|---|---|---|---|---|
| `POST /incidents` | Bearer · citizen, coordinator **or guest** | Create a help request (F2; guest F1/AC-1.4) | `service_type, priority, description, location{latitude,longitude}` → `Incident` (+ `tracking_token` if guest) | `422 validation_error` | 20/min (guest 5/min) |
| `GET /incidents` | Bearer · role-scoped | List/map source, filterable + search (F3) | `?status&service_type&priority&q&sort&page&limit` → `{data:[Incident], pagination}` | `401` | 100/min |
| `GET /incidents/{id}` | Bearer · role-scoped | One request's detail (F3, F7) | — → `Incident` | `403`, `404 not_found` | 100/min |
| `PATCH /incidents/{id}` | Bearer · citizen(own), coordinator | Edit description/priority **before accepted** (AC-5.3) | `description?, priority?` → `Incident` | `403 cannot_modify`, `404` | 20/min |
| `GET /incidents/mine` | Bearer · citizen | Requester's own requests (F7/AC-7.1) | `?status` → `{data:[Incident], pagination}` | `401` | 50/min |
| `GET /incidents/assigned` | Bearer · provider | Provider's claimed requests | `?status` → `{data:[Incident], pagination}` | `401` | 100/min |
| `GET /incidents/nearby` | Bearer · provider, coordinator | Proximity search (F4/AC-4.1) | `?latitude&longitude&radius_km&service_type` → `{data:[Incident]}` nearest-first | `422` | 100/min |
| `GET /incidents/{id}/updates` | Bearer · role-scoped | Status/audit timeline (F5, F7) | — → `{data:[IncidentUpdate]}` | `404` | 100/min |

**Lifecycle transitions** *(dedicated endpoints; enforce the [§4 lifecycle](11-requirements-scope-and-acceptance.md#4-the-request-lifecycle-authoritative-for-the-mvp); illegal transition → `409 invalid_transition`)*

| Method · Path | Auth · Roles | From → To | Key request | Errors |
|---|---|---|---|---|
| `POST /incidents/{id}/approve` | coordinator | created → approved *(critical)* | `note?` (F8/AC-8.2) | `409 invalid_transition` |
| `POST /incidents/{id}/reject` | coordinator | created/approved → rejected | `reason` (required) (F8/AC-8.3) | `422`, `409` |
| `POST /incidents/{id}/accept` | provider | created/approved → accepted | `eta?` (F4/AC-4.3) | `409 already_accepted` |
| `POST /incidents/{id}/assign` | coordinator | created/approved → accepted | `organization_id` (manual assign, F8) | `409`, `404` |
| `POST /incidents/{id}/start` | provider (assigned) | accepted → in_progress | — (F5/AC-5.1) | `403`, `409` |
| `POST /incidents/{id}/complete` | provider (assigned) | in_progress → completed | `notes, photos?` (F5/AC-5.2) | `403`, `409` |
| `POST /incidents/{id}/verify` | citizen (owner) | completed → verified | `rating?` (1–5), `review?` (F7/AC-7.2, AC-7.3 — rating optional) | `403`, `409` |
| `POST /incidents/{id}/cancel` | citizen(own)/coordinator | pre-delivery → cancelled | `reason` (F cancel) | `409` (not if completed) |

> **Single-claim guarantee (AC-4.4):** `accept`/`assign` are atomic — the first succeeds and binds the one
> provider; any concurrent second attempt gets **`409 already_accepted`**. Only the assigned provider may
> `start`/`complete` (AC-5.4) → otherwise `403`.

### 5.3 Organizations (providers) & resources — F3, F4, F8

| Method · Path | Auth · Roles | Purpose | Errors | Rate |
|---|---|---|---|---|
| `POST /organizations` | Bearer · provider | Register a provider org (pending verification) | `409`, `422` | 5/min |
| `GET /organizations` | Bearer · coordinator, provider | List providers (spatial/type filters) | `401` | 100/min |
| `GET /organizations/{id}` | Bearer · all | Org profile (public fields) | `404` | 100/min |
| `GET /organizations/mine` | Bearer · provider | Own org | `404` | 100/min |
| `PATCH /organizations/{id}` | Bearer · provider(own), coordinator | Update services/details | `403`, `404` | 20/min |
| `POST /organizations/{id}/verify` | Bearer · coordinator, admin | Approve org (enables claiming) (F8/AC-8.4) | `403`, `404` | 20/min |
| `PATCH /organizations/{id}/capacity` | Bearer · provider(own) | Set concurrent-request capacity (F4/AC-4.5) | `403` | 50/min |
| `PATCH /organizations/{id}/availability` | Bearer · provider(own) | Toggle in/out of matching | `403` | 30/min |
| `GET /resources` | Bearer · role-scoped | Provider assets on the map (F3) | `401` | 100/min |
| `POST /resources` · `PATCH /resources/{id}` | Bearer · provider(own) | Declare/update assets | `403`, `422` | 20/min |

### 5.4 Locations / geo — F3, F4

| Method · Path | Auth · Roles | Purpose | Errors | Rate |
|---|---|---|---|---|
| `GET /locations/nearby` | Bearer · provider, coordinator | Generic PostGIS proximity (incidents+providers) | `422 invalid_coordinates` | 100/min |
| `POST /locations/distance` | Bearer · all | Distance between two points (km) | `422` | 200/min |
| `GET /locations/reverse-geocode` | Bearer · all | Coordinates → address | `422` | 100/min |
| `GET /locations/map/{layer}` | Bearer · role-scoped | GeoJSON map layer (incidents/providers) | `404` | 200/min |

### 5.5 Alerts & notifications — F6, F8

| Method · Path | Auth · Roles | Purpose | Errors | Rate |
|---|---|---|---|---|
| `POST /alerts` | Bearer · coordinator, admin | Broadcast an area alert (F8) | `422` | 20/min |
| `GET /alerts` | Bearer · all | List active alerts for the user's area | `401` | 100/min |
| `GET /notifications` | Bearer · authenticated | User's notifications (F6) | `401` | 100/min |
| `GET /notifications/unread-count` | Bearer · authenticated | Badge count | `401` | 200/min |
| `POST /notifications/{id}/read` | Bearer · authenticated | Mark one read | `404` | 50/min |
| `POST /notifications/read-all` | Bearer · authenticated | Mark all read | `401` | 20/min |
| `GET /notifications/preferences` · `PATCH /notifications/preferences` | Bearer · authenticated | View/set channels (email, sms, in_app) | `422` | 50/min |
| `DELETE /notifications/{id}` | Bearer · authenticated | Soft-delete a notification | `404` | 30/min |
| `POST /notifications/chat` | Bearer · authenticated | FAQ chatbot **stub** — fixed acknowledgement (Task L; real NLP → FFP) | `422` | 30/min |

> **Delivery (F6/AC-6.3):** a status change enqueues **one** notification to the right recipient; if the
> SMS/email channel is down the state change still succeeds and the send is retried (near-real-time is
> acceptable; deep push → FFP).

> **FAQ chatbot (Task L / PICS-NTF-004):** `POST /notifications/chat` accepts `{ "message": "…" }`
> (1–2000 characters) and **always** returns the same acknowledgement —
> `{ "reply": "Your input is noted, we'll try to get back to you shortly, if possible." }`. It is a
> deliberate **non-intelligent stub** in the MVP (no ML); genuine natural-language help is an FFP
> intelligence engine (white paper #1, [`21`](21-architecture-decisions.md)).

### 5.6 Reports & audit — F9, F10

| Method · Path | Auth · Roles | Purpose | Errors | Rate |
|---|---|---|---|---|
| `GET /reports/dashboard` | Bearer · coordinator, admin | Live overview metrics (F8/AC-8.1) | `403` | 50/min |
| `GET /reports/response-times` | Bearer · coordinator, admin | Avg/median response time (F10/AC-10.1) | `403` | 50/min |
| `GET /reports/fulfillment` | Bearer · coordinator, admin | Fulfilment rate by period/area (F10/AC-10.1) | `403` | 50/min |
| `GET /reports/{name}/export` | Bearer · coordinator, admin | Same figures as a file (`?format=csv`) (F10/AC-10.2) | `403`, `422` | 20/min |
| `GET /audit-logs` | Bearer · coordinator, admin | Read-only audit trail, filterable (F9/AC-9.1) | `403` | 50/min |

> **Audit (F9/AC-9.2):** audit entries are **append-only** — there is deliberately **no** create/update/
> delete endpoint. They are written by the system as a side-effect of the operations above. Retention is in
> the security doc.

### 5.7 Files & system — F2, F5, ops

| Method · Path | Auth · Roles | Purpose | Errors | Rate |
|---|---|---|---|---|
| `POST /files` | Bearer · authenticated | Upload a photo/document; returns a `url` an incident references (F2/AC-2.1, F5/AC-5.2) | `400 invalid_file_type`, `413 file_too_large`, `422` | 20/min |
| `GET /files/{id}` | Bearer · role-scoped | File metadata | `404` | 100/min |
| `GET /health` | Public | Liveness/readiness probe (also exposed unversioned by the host) | `503` | — |

> **Uploads (MVP):** `multipart/form-data`, allowed types **image/jpeg, image/png, application/pdf**, **≤ 10 MB**
> per file. Incidents carry `photos: [url]` pointing at uploaded files — the emergency create flow (F2) and
> completion proof (F5) both use this. Heavy media (video, large attachments) is **→ FFP**.
>
> **Storage:** files are stored in **MinIO** (on-prem, **S3-compatible** object storage), not in the
> database — PostgreSQL keeps only the object key/URL + metadata. The returned `url` may be a time-limited
> pre-signed link. Because the code speaks the **S3 API**, the same contract survives into the FFP
> (distributed MinIO or cloud S3) unchanged. See [`20-architecture-system.md`](20-architecture-system.md) §7.

#### Media handling & quality rules

*Why these exist (plain terms):* during a disaster the network is weak and congested. Big or blurry
uploads either fail to send or arrive useless. So the app **shrinks and checks** every file **on the
device first**, and the server **re-checks** on `POST /files` (never trust the client). Failures return a
clear message — `413 file_too_large`, `400`/`422 invalid_file_type` — telling the user what to fix.

**File size & compression**
- Every file is **compressed on-device before upload** and must be **≤ 10 MB** (hard cap).
- **Photos:** max **5 per incident**, each compressed to a target **≤ 2 MB**.
- **Documents (PDF):** **≤ 10 MB** total, target **≤ ~1.5 MB per page** (scanned pages ~150 dpi) — the
  per-page budget keeps multi-page docs light and lets a weak link upload **page by page**.
- **Emergency "lite" mode:** on a slow connection (or an *Emergency* submit), capture **one** photo shrunk
  to **≤ ~500 KB** so it sends in seconds.

**Photo resolution & clarity**
- Formats **JPEG / PNG** (WebP accepted); auto-resized to **long edge ≤ 1920 px**, saved at **~80% JPEG
  quality** — plenty to see an injury, damage, or a face without wasting bandwidth.
- **Minimum ≥ 640×480** — smaller images are rejected as too small to be useful evidence.
- **Sharpness gate:** a blur score (variance-of-Laplacian) rejects out-of-focus photos and asks the user to
  **retake**, so responders never get a useless smear.
- **Privacy:** hidden photo metadata (**EXIF, embedded GPS**) is stripped on upload; a request's location
  comes only from the **map pin the user chose**.

**Face check on person photos (MVP = detection only)**
- For person-type photos (rescue / missing-person), a **lightweight, client-side face *detection*** checks
  that a **clear, decently-sized, sharp face** is present — a **quality gate** that returns *"good"* or
  *"please retake"*. It creates and stores **no biometric data**.
- Full **FaceNet face *recognition* / matching** (biometric identity, re-identifying people across photos)
  is **→ FFP** — it is heavier ML **and** biometric data about vulnerable people, so it needs explicit
  consent and India **DPDP Act 2023** safeguards. See the
  [FFP charter](../ffp/prompts/instructions_idrm_ffp_docs.md).

---

## 6. Error catalog (shared)

Every error uses the same envelope:
```json
{ "error": { "code": "already_accepted", "message": "This request was already accepted by another provider.", "details": [] } }
```
`details` carries per-field validation issues: `[{ "field": "location.latitude", "issue": "must be between -90 and 90" }]`.

| HTTP | Typical `code`(s) | When |
|---|---|---|
| **400** | `bad_request` | Malformed JSON / bad query params |
| **401** | `unauthorized`, `invalid_credentials` | Missing/expired token; wrong login |
| **403** | `forbidden`, `account_locked`, `cannot_modify`, `not_verified` | Role/permission denied; locked; editing an accepted request |
| **404** | `not_found` | No such resource |
| **409** | `email_exists`, `already_accepted`, `invalid_transition`, `org_exists` | State/uniqueness conflict |
| **410** | `token_expired` | Reset/verification token expired |
| **413** | `file_too_large` | Uploaded file exceeds the 10 MB limit (`/files`) |
| **422** | `validation_error`, `invalid_coordinates`, `invalid_file_type` | Semantic validation failed |
| **429** | `rate_limit_exceeded` | Over budget (includes `Retry-After`) |
| **500 / 503** | `internal_error`, `service_unavailable` | Server fault / maintenance |

*(FFP-only families — `/financial/*` `402 payment_required`, websocket close codes — are documented in the
FFP API doc when those resources are added.)*

---

## 7. Traceability & next steps

- Every endpoint above maps to a **Feature (F1–F11)** and its acceptance criteria in
  [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md); tests in
  [`70-quality-test-strategy.md`](70-quality-test-strategy.md) assert these contracts.
- Request/response **schemas** (fields, types, constraints) are defined once in
  [`40-api-openapi.yaml`](40-api-openapi.yaml) and detailed in [`50-data-model.md`](50-data-model.md).
- **Asset reconciled (2026-08-12 ✅):** `../assets/idrm-api-resource-mapping.xlsx` now uses these canonical
  `/api/v1` URIs with a **`Phase (MVP/FFP)`** column (disaster/financial/websocket rows tagged FFP, kept).
  See the changelog.

*Related:* [`10-requirements-prd.md`](10-requirements-prd.md) · [`20-architecture-system.md`](20-architecture-system.md) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) · [`50-data-model.md`](50-data-model.md) ·
[`26-conformance-pics.md`](26-conformance-pics.md) (API conformance rows) · [`40-api-openapi.yaml`](40-api-openapi.yaml).
Plan: [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).
