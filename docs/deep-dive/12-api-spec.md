# API Specification (MVP)

> **Part of:** IDRM Documentation · `deep-dive/12-api-spec.md`
> **Answers:** What are the API conventions, and where is the machine-readable contract?
> **Source posters:** MVP execution poster *Modular Packet/Workflow* (Key HTTP Request Examples); conforms to
> the data model in [`13-data-model.md`](13-data-model.md) (Poster 22). Deepens
> [`../02-architecture.md`](../02-architecture.md), [`../03-engineering.md`](../03-engineering.md).
> **Standards:** **OpenAPI 3.1** · URL versioning · JWT bearer auth
> **Audience:** Developers · **Depth:** Deep
> **Status:** Draft

---

## 1. Overview

IDRM exposes a single **REST API** served by **FastAPI** inside the modular monolith. The machine-readable
contract is **[`openapi.yaml`](openapi.yaml)** (OpenAPI 3.1); this document explains the conventions and how to
use it. FastAPI also serves a live, interactive version at **`/docs`** (Swagger UI) and **`/redoc`** (ReDoc).

---

## 2. Base URL & versioning

- **Base path:** `/api/v1` (URL versioning; a breaking change would introduce `/api/v2` with a deprecation
  window — see ADR-009 in [`../99-decisions-and-history.md`](../99-decisions-and-history.md)).
- **Example:** `GET https://<host>/api/v1/incidents`

---

## 3. Authentication & authorization

- **Authentication:** JWT **bearer** tokens. Clients obtain a token from `POST /api/v1/auth/login`, then send
  `Authorization: Bearer <token>` on subsequent requests. Tokens are refreshed via `POST /api/v1/auth/refresh`.
- **Authorization:** **RBAC** — the caller's role (from the `users.role_id` → `roles` relationship) governs
  which operations and records are permitted (see [`../05-security.md`](../05-security.md)).
- Endpoints are authenticated by default; only `auth/login` and explicitly public read endpoints are open.

---

## 4. Request & response format

- **Format:** JSON (`Content-Type: application/json`), UTF-8.
- **Validation:** every request body/query is validated by **Pydantic**; invalid input is rejected with `422`.
- **IDs:** resource identifiers are UUIDs (`*_id`), matching [`13-data-model.md`](13-data-model.md).
- **Timestamps:** ISO 8601 / RFC 3339 (`2026-08-09T10:15:00Z`).
- **Geography:** coordinates as GeoJSON-style `[longitude, latitude]`; areas/features as GeoJSON geometry.

---

## 5. Errors

A consistent error envelope (aligned with RFC 9457 "problem details" thinking):

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "description must be between 10 and 500 characters",
    "details": [ { "field": "description", "issue": "too_short" } ],
    "request_id": "b1f2…"
  }
}
```

| Status | Meaning |
|---|---|
| `200 / 201` | Success / created. |
| `204` | Success, no content (e.g. delete). |
| `400` | Malformed request. |
| `401` | Missing/invalid token. |
| `403` | Authenticated but not permitted (RBAC). |
| `404` | Resource not found. |
| `409` | Conflict (e.g. duplicate, illegal state transition). |
| `422` | Validation failed. |
| `429` | Rate limit exceeded. |
| `500` | Unexpected error (with `request_id` for tracing). |

Every response carries a `request_id` that ties it to the audit/observability trail
([`../07-operations.md`](../07-operations.md)).

---

## 6. Collections: pagination, filtering, sorting

List endpoints share conventions (confirmed by the MVP request examples, e.g.
`GET /api/v1/incidents?status=active&page=1&size=20`):

| Concern | Convention |
|---|---|
| **Pagination** | `?page=` (1-based) and `?size=` (default 20, max 100). Responses include `total`, `page`, `size`. |
| **Filtering** | Resource-specific query params (e.g. `status`, `severity_level`, `incident_type_id`). |
| **Sorting** | `?sort=field` / `?sort=-field` (prefix `-` for descending). |
| **Spatial** | `?bbox=minLon,minLat,maxLon,maxLat` and/or `?near=lon,lat&radius_km=` for geo queries. |

---

## 7. Cross-cutting

- **Rate limiting:** applied per client (`429` with `Retry-After`) — see [`../05-security.md`](../05-security.md).
- **Compression:** GZip for responses.
- **CORS & security headers:** applied globally.
- **Idempotency:** `PUT`/`DELETE` are idempotent; `POST` creates.

---

## 8. Resource catalog

Every resource maps to an entity in [`13-data-model.md`](13-data-model.md) (Poster 22). Standard operations:
**L**ist · **C**reate · **R**ead · **U**pdate · **D**elete (subject to RBAC). Reference tables are read-mostly.

| Resource path | Entity | Ops | Notes |
|---|---|---|---|
| `/auth/login`, `/auth/refresh`, `/auth/logout` | (session) | — | Obtain/refresh/revoke JWT. |
| `/users`, `/users/me` | `users` | L C R U | Admin-managed; `me` is self-profile. |
| `/roles` | `roles` | L R | Reference (RBAC roles). |
| `/organizations` | `organizations` | L C R U | Hierarchy via `parent_org_id`. |
| `/locations` | `locations` | L C R U | Hierarchy; `boundary` geometry. |
| `/incidents` | `incidents` | L C R U D | Core resource. |
| `/incidents/{id}/updates` | `incident_updates` | L C | Timeline entries. |
| `/incidents/{id}/alerts` · `/alerts` | `alerts` | L C R | Alerts/notifications for an incident. |
| `/incidents/{id}/tasks` · `/tasks` | `tasks` | L C R U | Assignable tasks. |
| `/incidents/{id}/deployments` · `/deployments` | `deployments` | L C R U | Resource↔incident link. |
| `/incidents/{id}/documents` · `/documents` | `documents` | L C R D | File references. |
| `/incidents/{id}/media` · `/media` | `media` | L C R D | Photos/videos. |
| `/incident-types` | `incident_types` | L R | Reference. |
| `/responders` | `responders` | L C R U | Users acting for orgs. |
| `/resources` | `resources` | L C R U | Inventory/assets. |
| `/resource-types` | `resource_types` | L R | Reference. |
| `/map/layers` | `geospatial_data` | L R | Map layers; supports `?bbox=`. |
| `/communication-logs` | `communication_logs` | L C R | Comms trail. |
| `/audit-logs` | `audit_logs` | L R | Admin, read-only. |

---

## 9. Viewing & validating the contract

- **View:** run the app and open `/docs` (Swagger UI) or `/redoc`; or load [`openapi.yaml`](openapi.yaml) into
  any OpenAPI viewer.
- **Validate/lint:** the `openapi.yaml` is linted (e.g. Spectral) as part of the deep-dive workflow before
  emission (see [`00-plan.md`](00-plan.md) §5).

---

## 10. Traceability

Each operation traces back to a data entity (Poster 22) and a requirement in `10-srs.md`, consolidated in
`14-traceability-matrix.md`.

---

*Conforms to the MVP request examples and the Poster 22 data model; expressed as OpenAPI 3.1.*
