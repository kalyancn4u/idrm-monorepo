# REST API 101

> *Type: Guide (101 / foundational) · Audience: novices → developers · Status: MVP — current · Track: Software Engineering (#11)*
> *An API is how two programs talk. IDRM's whole system — web UI, future mobile app, partner integrations — talks
> to the server through one REST API. This guide explains REST from scratch, then walks IDRM's actual, frozen
> `/api/v1` contract.*

---

## 1. What an API is

**API = Application Programming Interface** — a defined way for one program to ask another to do something or
return data. When the IDRM web page shows a list of help requests, it *called the API* to fetch them. The API is
a **contract**: "send me this, I'll return that."

**REST** is the most common style of web API. It treats everything as **resources** (nouns) that you act on with
standard **HTTP** verbs.

---

## 2. The building blocks: resource, method, status

- **Resource** — a thing, addressed by a URL: `/incidents`, `/incidents/{id}`, `/resources`.
- **HTTP method** — the verb (the action):

| Method | Meaning | IDRM example |
|--------|---------|--------------|
| `GET` | read | `GET /incidents` (list) · `GET /incidents/{id}` (one) |
| `POST` | create | `POST /incidents` (report a help request) |
| `PATCH`/`PUT` | update | `PATCH /incidents/{id}` (change status) |
| `DELETE` | remove | (rare in IDRM — we cancel, not delete) |

- **Status code** — the result, as a number: `200` OK, `201` Created, `400` bad request, `401` not logged in,
  `403` not allowed, `404` not found, `500` server error.
- **JSON** — the text format for the data sent back and forth (keys and values).

---

## 3. A request, end to end

```http
POST /api/v1/incidents          → create a help request
Authorization: Bearer <token>   → who you are (see IAM 101)
Content-Type: application/json

{ "service_type": "rescue", "priority": "high", "description": "3 stranded" }
```

The server validates it, saves it, and replies:

```http
201 Created
{ "id": "3f2a…", "status": "created", "created_at": "2026-08-14T09:00:00Z", ... }
```

---

## 4. IDRM's frozen contract (the rules that never change)

IDRM's API is a **stable contract across the whole life cycle** — FFP only *adds* endpoints at the same paths,
never renames. The conventions (from [`apis.md`](../../../archive/instructions/apis.md)):

- **Version in the path:** everything under `/api/v1/...`.
- **`snake_case`** field names; **UUID** ids; **ISO-8601 UTC** timestamps in `*_at` fields.
- **Enums** are lowercase `snake_case` (e.g. `priority: "critical"`).
- **Lists** come wrapped: `{ "data": [...], "pagination": {...} }`. A **single** resource is a bare object.
- **Errors** use one envelope with a machine-readable **`code`** — clients branch on `code`, never on the
  human message.
- Terminology bridge: the UI's **"help request"** is the API's **`incident`**.
- The contract is described in **OpenAPI** and validated automatically.

> **Why the strict rules?** A predictable, versioned contract means the web app, a future mobile app, and partner
> agencies can all rely on it without breaking — the single most important property of a long-lived API.

---

## 5. How IDRM serves it

The MVP serves this API from a single **FastAPI** (Python) app. Each module exposes its endpoints via its
`router.py`, validates input/output with **Pydantic** schemas, and returns JSON. (FFP adds gRPC/WebSocket/SSE and
a gateway in front — but the public REST contract stays the same.)

---

## 6. Mastery check

You've got REST API 101 when you can:

1. Explain **API**, **resource**, **HTTP method**, and **status code**.
2. Map create/read/update to `POST`/`GET`/`PATCH` with IDRM examples.
3. Recite IDRM's contract rules (versioned path, snake_case, UUID, `{data,pagination}`, error `code`).
4. Explain why the contract is "frozen" and what FFP is allowed to change.
5. Say what **OpenAPI** and **Pydantic** do here.

---

## 7. Go deeper

- IDRM API spec: [`../../idrm-mvp-docs/40-api-specification.md`](../../../docs/mvp/40-api-specification.md) (+ `40-api-openapi.yaml`)
- HTTP status codes — developer.mozilla.org/HTTP/Status · OpenAPI — spec.openapis.org
- FastAPI — fastapi.tiangolo.com · REST (Fielding, reference) · related: [IAM 101](iam-101.md), [API Testing 101](api-testing-101.md)

---
*Next:* [Database 101](database-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
