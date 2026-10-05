# IDRM Instructions — APIs, Types & Integrations

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Boundary:** this spoke = the **contract** and API styles. The **gateway** that fronts them =
> [`api-gateway.md`](api-gateway.md).

## The canonical contract — FROZEN (MVP + FFP)
`/api/v1/...` is a **stable contract across the whole SDLC**. FFP only **adds** endpoints at the same paths;
it never renames. Rules:
- Version in path; `snake_case` fields; **UUID** ids; **ISO-8601 UTC** `*_at` timestamps.
- Enum values lowercase `snake_case`.
- Lists wrapped `{ data, pagination }`; a single resource = a **bare object**.
- Error **envelope** with a machine-readable **`code`** (clients branch on `code`, not on messages).
- Terminology: UI "help request" == API resource **`incident`**.
- **OpenAPI-validated** (`openapi-spec-validator`); the spec is the contract.

## API types (phase-scoped)
- **MVP:** REST/JSON only, served by the FastAPI monolith.
- **FFP additions:** gRPC (internal service-to-service) · gRPC-Web / WebSocket / SSE (real-time COP, tasking) ·
  webhooks (external orgs). A **BFF/edge** may compose calls per client without forking the contract.

## Integrations
- External orgs/agencies via versioned REST + webhooks; identity via OIDC/IdP (see [`security.md`](security.md)).
- Geospatial reads are PostGIS-backed (bounding-box + filter queries) — see [`data-modeling.md`](data-modeling.md).
- Real-time backbone — see [`caching-messaging.md`](caching-messaging.md).

## Canonical docs
- [`../idrm-mvp-docs/40-api-specification.md`](../idrm-mvp-docs/40-api-specification.md) (+ `40-api-openapi.yaml`)
- [`../idrm-ffp-docs/40-api-specification.md`](../idrm-ffp-docs/40-api-specification.md)

## Trusted external references
- OpenAPI Spec — spec.openapis.org · REST/JSON conventions — jsonapi.org (reference only)
- gRPC — grpc.io/docs · WebSocket/SSE — developer.mozilla.org (Server-sent events)
- OWASP API Security Top 10 — owasp.org/API-Security
