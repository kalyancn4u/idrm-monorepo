# Chapter 10 — The API Contract & Responses

*The frozen conventions every endpoint obeys, and the shapes every response takes.*

**By the end of this chapter you will be able to:** state the `/api/v1` conventions, read
the three response shapes, use the pagination helper, understand the list filters, and say
why the OpenAPI file is the source of contract truth.

Files: [`docs/mvp/40-api-specification.md`](../mvp/40-api-specification.md),
[`40-api-openapi.yaml`](../mvp/40-api-openapi.yaml),
[`app/core/pagination.py`](../../code/app/core/pagination.py),
[`app/core/exceptions.py`](../../code/app/core/exceptions.py).

---

## The frozen conventions (Design Law #2, made concrete)

Every endpoint obeys the same rules, so learning one teaches you all:[1]

- **Base:** everything under **`/api/v1`** (version in the path).
- **URLs:** plural, lowercase nouns (`/incidents`, `/organizations`, `/audit-logs`);
  lifecycle moves are dedicated sub-paths (`/incidents/{id}/accept`).
- **Fields:** `snake_case`; ids are **UUID** strings; timestamps are **ISO-8601 UTC**,
  always `*_at`; enum values are **lowercase snake_case**.
- **Auth:** `Authorization: Bearer <jwt>` (Ch 6); public endpoints are marked.

🧠 **Nuance:** these aren't taste — they're a **compatibility contract**. A client written
today keeps working because none of this shifts under it.[2]

> **Footnotes**
>
> - **[1]** Uniform conventions are ***principle of least astonishment*** at API scale: once you know incidents, you can guess organizations. Consistency is a usability feature for the developers who consume the API.
> - **[2]** The version lives in the *path* (`/api/v1`) so a future breaking change becomes `/api/v2` while `/api/v1` keeps serving old clients. Additive change (a new field, a new endpoint) never bumps the version — it's backward-compatible by construction.

---

## Three response shapes, and only three

Whatever the endpoint, the body is one of:[1]

| Situation | Shape |
|---|---|
| one resource | a **bare object** — `{ "id": "...", "status": "created", ... }` |
| a collection | `{ "data": [ ... ], "pagination": { page, limit, total, total_pages } }` |
| any failure | `{ "error": { "code": "...", "message": "...", "details": [ ... ] } }` |

A client can therefore parse *any* response with three branches — never guesswork.[2]

> **Footnotes**
>
> - **[1]** The error shape is Chapter 4's envelope, produced centrally for your `AppError`s, Pydantic validation, and framework HTTP errors alike. One shape across all three sources is what makes client error-handling simple and reliable.
> - **[2]** Wrapping lists (rather than returning a bare array) leaves room for `pagination` metadata and keeps the top-level type stable (always an object) — a small decision that prevents a lot of client churn later.

---

## One helper builds the list envelope

The `{data, pagination}` shape lived, copy-pasted, in eight endpoints — including the
`total_pages` **ceiling division**. It now lives once, in `core/pagination.py`:[1]

```python
# app/core/pagination.py
def total_pages(total: int, limit: int) -> int:
    if limit <= 0: return 0
    return (total + limit - 1) // limit          # round up

def paginate(data: list, page: int, limit: int, total: int) -> dict:
    return {"data": data, "pagination": {"page": page, "limit": limit,
            "total": total, "total_pages": total_pages(total, limit)}}
```

```python
# any list endpoint now
return paginate([to_response(i).model_dump(mode="json") for i in items], page, limit, total)
```

🧠 **Nuance:** if the pagination shape ever changes, it changes in **one** place — and
the tricky ceiling arithmetic is written (and unit-tested) exactly once.[2]

> **Footnotes**
>
> - **[1]** ***DRY*** (Don't Repeat Yourself): eight copies of an arithmetic formula is eight chances for a subtle off-by-one. Centralising it removes that risk and shrinks every list endpoint to one line. (This was finding F3 in the 2026 coherence pass.)
> - **[2]** ***Ceiling division*** `(total + limit - 1) // limit` rounds *up* — 21 items at 20/page is 2 pages, not 1. The pure helper's unit test pins this down; because it needs no database, it runs on any machine.

---

## Filtering and sorting a list — safely

`GET /incidents` accepts `status`, `service_type`, `priority`, `q` (free-text), and
`sort`. Two details matter: `q` uses the **full-text index**, and `sort` is
**whitelisted**.[1]

```python
# app/modules/incidents/service.py + repository.py (trimmed)
if q:  stmt = stmt.where(func.to_tsvector("english", Incident.description)
                         .op("@@")(func.plainto_tsquery("english", q)))   # uses the GIN index
SORTABLE_FIELDS = {"created_at": Incident.created_at, "priority": Incident.priority}
# unknown sort field -> 422 invalid_sort (never an arbitrary column)
```

⚠️ **Pitfall:** letting a client sort by any field name they send invites errors and
injection. A strict allow-list is the safe, KISS choice.[2]

> **Footnotes**
>
> - **[1]** These filters are advertised by the contract *and* backed by real indexes (`priority` b-tree, `to_tsvector(description)` GIN — Ch 5). Contract, code, and schema agree — an index nothing queries is waste, and a filter the contract promises but the code ignores is a broken promise. Keeping the three in lock-step is a recurring theme of this codebase.
> - **[2]** ***SQL injection*** via a column name is a real risk if you interpolate client strings into a query. Mapping an allowed key set to real columns (and `422`-ing anything else) removes the risk without a general-purpose sort engine the MVP doesn't need.

---

## The machine-readable contract: OpenAPI

The prose spec is for humans; **`40-api-openapi.yaml`** is the machine truth — it drives
the interactive `/docs` page and lets clients/tests be generated.[1]

- Add an endpoint in code → **also** document it in the OpenAPI (they must not drift).
- The docs are **mirrored** to the archive copy; a parity check keeps them byte-identical.

🧠 **Nuance:** when code and contract disagreed (a shipped `/notifications/chat` endpoint
missing from the spec; query params that had drifted), the fix was to make the **contract
match the code** and re-freeze — not to quietly change behaviour.[2]

> **Footnotes**
>
> - **[1]** ***OpenAPI*** is a standard schema for describing REST APIs. FastAPI generates a live `/docs` (Swagger UI) from the app, and the committed YAML is the authoritative, reviewable contract. Keeping a hand-maintained YAML in sync is deliberate: it's the artifact clients and the FFP build against.
> - **[2]** This is contract-first discipline in practice. The 2026 coherence pass documented the chat endpoint, reconciled `read`→`unread_only` and the org/audit/nearby filters, and corrected the incidents `q` wording — always moving the *docs* to match the *shipped behaviour*, because clients depend on behaviour.

---

## The error catalog

Because every failure carries a machine `code`, the contract can publish a **catalog** of
them, and clients branch on the code, not the message:[1]

| Code | When |
|---|---|
| `validation_error` | body/query failed Pydantic (`422`) |
| `unauthorized` / `forbidden` | missing/invalid token / wrong role (`401`/`403`) |
| `not_found` | no such resource (`404`) |
| `already_accepted` / `invalid_transition` | lifecycle conflicts (`409`) |
| `rate_limit_exceeded` | too many requests (`429`, with `Retry-After`) |
| `file_too_large` / `invalid_file_type` | upload gates (`413`/`400`) |

> **Footnotes**
>
> - **[1]** A stable code vocabulary is what lets a UI show the right message and a script retry the right cases (e.g. back off on `rate_limit_exceeded`, re-fetch on `already_accepted`). Messages can be reworded or translated freely because clients never parse them.

---

## Recap & what's next

- Everything obeys **frozen `/api/v1` conventions**; responses are one of three shapes —
  **bare object · `{data, pagination}` · error envelope**.
- `core/pagination.py` builds the list envelope **once** (DRY ceiling-division); list
  filters are index-backed and **`sort` is whitelisted**.
- **OpenAPI** is the machine contract; when code and contract drift, the **contract is
  corrected to match shipped behaviour** and re-frozen.

🛠️ **Try it:** open `/docs` on the running app and expand `GET /api/v1/incidents`. Every
parameter you see there is backed by real code and a real index — you've read all of it.

**Next:** [Chapter 11 — Testing & Quality](11-testing-and-quality.md), where we prove the
whole thing works.
