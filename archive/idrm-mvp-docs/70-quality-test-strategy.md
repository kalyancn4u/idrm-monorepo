# IDRM MVP — Test Strategy & Test Plan

> *Type: Document (specification) · Audience: QA, developers · Status: MVP — current*
> *How we know IDRM works. The MVP testing pyramid, tools, coverage gates, and the mapping from every acceptance criterion (F1–F11, [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md)) to at least one test. Grounded in the authoritative [`../../docs/06-quality.md`](../../docs/06-quality.md), scoped to the MVP stack (pytest / FastAPI / PostgreSQL+PostGIS).*

> **Principle:** **shift left** — many fast tests low in the pyramid, a few broad ones on top; run them on
> **every change**. A feature is not "done" until its acceptance criteria each have a passing test
> (Definition of Done, doc 11 §7).

---

## 1. The MVP testing pyramid

```
        ┌───────────────┐
        │  E2E  ~5%     │  a few critical journeys (report → claim → verify)
        ├───────────────┤
        │ Integration ~15% │ modules + real PostgreSQL/PostGIS (lifecycle, proximity, single-claim)
        ├───────────────┤
        │  API  ~20%    │ every endpoint's contract (status, body, auth, errors)
        ├───────────────┤
        │  Unit ~60%    │ functions, validators, the state machine, RBAC checks
        ├───────────────┤
        │ Test-data & environment foundation (isolated, repeatable) │
        └───────────────┘
```

The MVP's non-negotiable core is **Unit · API · Integration**; E2E, performance, and deeper security testing
start light and grow (heavier E2E/perf tooling is → FFP).

---

## 2. What each level covers

| Level | Covers (MVP) | Tools |
|---|---|---|
| **Unit** | Pydantic validators, the **lifecycle state machine** (legal/illegal transitions), the **single-claim** rule, RBAC role checks, report metric math, media-rule checks (size/type), enum handling | `pytest` |
| **API** | Each endpoint's **contract**: status codes, request/response shape vs [`40-api-openapi.yaml`](40-api-openapi.yaml), auth (401/403), validation (422), conflicts (409) | `pytest` + FastAPI `TestClient` / `httpx` |
| **Integration** | Flows through **real PostgreSQL + PostGIS**: full lifecycle create→verified, **PostGIS proximity** (`/incidents/nearby`), **concurrent claim** resolves to one winner, audit rows written, MinIO file put/get | `pytest` + a disposable test DB + a test MinIO bucket |
| **DB** | Migrations apply/rollback cleanly; constraints (unique email, FK, CHECK rating 1–5); spatial indexes used | `pytest` + Alembic |
| **E2E** (light) | A few journeys in a browser: citizen report → provider claim → complete → citizen verify; guest emergency submit | Playwright *(kept minimal for MVP)* |
| **Security** | Access-control matrix (deny-by-default), injection resistance, authz on every new endpoint | `pytest` authz suite (+ dependency scanning) |

---

## 3. Coverage & quality gates

Code must clear an automatic bar (mirrors [`../../docs/06-quality.md`](../../docs/06-quality.md) §3):

| Gate | Standard |
|---|---|
| **Format** | Black + isort (auto-applied) |
| **Lint** | Ruff — no errors |
| **Types** | mypy — clean |
| **Tests** | full suite green |
| **Coverage** | **≥ 80% overall** (hard gate ≥ 70%), higher on critical paths (lifecycle, auth, claim) |
| **Security** | no high/critical dependency vulns; authz suite green |

Run locally before a PR; enforced in CI (GitHub Actions) on every push/PR. *(Full DORA metrics, perf SLAs,
and heavy security scanning mature in the FFP.)*

---

## 4. Acceptance-criteria → test coverage (traceability)

Every feature's acceptance criteria (doc 11 §5) map to at least one test type:

| Feature | Key criteria | Test types |
|---|---|---|
| **F1** Accounts & access | unique email; login/logout; guest submit; RBAC denies | Unit (email/role) · API (auth, guest) · Integration (guest→map) |
| **F2** Create request | required fields; valid enums; location stored; confirmation | Unit (validation) · API (201/422) · Integration (queryable) |
| **F3** Map | role-scoped markers; providers layer | API (role-scoped) · Integration (matches DB) |
| **F4** Discover & claim | nearby nearest-first; filter; **single-claim**; type/capacity | Unit (claim rule/filter) · API (list/claim, 409) · **Integration (PostGIS + concurrent claim)** |
| **F5** Update & complete | legal transitions only; assigned-provider-only | Unit (state machine) · API (illegal→409/403) · Integration (full walk) |
| **F6** Notifications | one notification per change; right recipient; outage non-blocking | Unit (recipient) · Integration (enqueue; outage) |
| **F7** Track/verify/rate | track; verify→verified; optional rating | API (verify) · Integration (persisted) |
| **F8** Coordinator | dashboard; approve/reject critical; org verify | API (role-gated) · Integration (approval unblocks claim) |
| **F9** Audit | significant actions recorded; **append-only** | Unit (writer) · Integration (immutable row) |
| **F10** Reports | response-time & fulfilment; export | Unit (metric math) · API (report/export) |
| **F11** Multi-language | second language renders; no hard-coded copy | Unit (catalogue) · manual UI check |

---

## 5. Test data & environment

- **Isolated, repeatable:** each run uses a **disposable PostgreSQL+PostGIS test database** (created,
  migrated with Alembic, torn down) and a **test MinIO bucket** — no shared state, no reliance on prod data.
- **Fixtures/factories** build users per role, organizations, and incidents in known states (e.g. an
  `accepted` incident) so tests are deterministic.
- **Seed personas** from the PRD (Rajesh/Priya/Arjun/Lakshmi) make scenarios readable.
- **Spatial fixtures** use real regional coordinates (Telangana/AP) so PostGIS proximity tests are meaningful.
- Tests never call real SMS/email or external services — those are **stubbed**.

---

## 6. Deferred → FFP

Heavy **E2E** suites & cross-browser grids · **performance/load** testing (k6/Locust) at surge scale ·
**contract testing** across services · automated **DAST** (OWASP ZAP) · full **DORA** delivery metrics.
See the [FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md).

---

*Related:* [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) ·
[`40-api-specification.md`](40-api-specification.md) · [`50-data-model.md`](50-data-model.md) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) · [`26-conformance-pics.md`](26-conformance-pics.md) (tests prove these rows) ·
[`../../docs/06-quality.md`](../../docs/06-quality.md).
Plan: [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).
