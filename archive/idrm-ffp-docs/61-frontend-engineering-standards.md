# IDRM FFP — Frontend Engineering Specification (React Web + React Native)

> *Type: Document (specification / standards) · Audience: frontend engineers, tech leads, reviewers · Status: FFP — next-phase (planned)*
> *Companion to the frontend design doc [`60-uidesign-frontend.md`](60-uidesign-frontend.md). That doc says **what** the FFP clients are; **this** doc says **how** they MUST be engineered.*

> **This document defines the mandatory engineering, architecture, scalability, security, and reliability
> standards for the IDRM React application(s).** All AI-generated code, human-written code, infrastructure,
> and integrations MUST follow these guidelines.

> **Phase invariant (do not violate):** These standards apply to the **FFP** phase ONLY. The **MVP** web UI stays
> **HTML + Tailwind CSS v4 + vanilla JS + Leaflet** — **no React, no Bun/Node** (MVP locked decision, ADR-003/ADR-014).
> FFP React clients are **additive** and consume the **same `/api/v1` contract** — adding a client requires **no server change**.

> **Conventions:** **MUST / MUST NOT / SHOULD / MAY** follow RFC 2119 (MUST = required; SHOULD = strongly
> recommended, deviations need a recorded reason; MAY = optional). Every `MUST` is a review gate.

> **FFP frontend acronyms (expanded once):** **SPA** = Single-Page Application · **FSD** = Feature-Sliced Design
> (a folder/architecture convention) · **SSR / CSR** = Server-Side / Client-Side Rendering · **PWA** = Progressive
> Web App (installable, offline-capable) · **i18n / a11y** = internationalization / accessibility · **TanStack
> Query** = a data-fetching/caching library · **CI** = Continuous Integration.

---

## 1. Core engineering principles

### 1.1 Mandatory principles
The application MUST follow:

- **SOLID** — five OO design rules (Single-responsibility, Open/closed, Liskov substitution, Interface
  segregation, Dependency inversion). In React terms: one reason to change per component/hook; extend via props
  and composition, not by editing shared internals; depend on typed interfaces, not concrete implementations.
- **DRY** (Don't Repeat Yourself) — one source of truth per rule; extract shared logic into hooks/utilities.
- **KISS** (Keep It Simple) — prefer the simplest solution that meets the requirement; no speculative abstraction.
- **Separation of Concerns** — UI rendering, data fetching, business logic, and routing are distinct layers.
- **High Cohesion, Low Coupling** — a feature's code lives together; features talk through typed APIs, not internals.
- **Composition over Inheritance** — build UIs by composing small components/hooks; never class-inherit UI.
- **Reusable Component Architecture** — a shared, documented component library; features consume it, don't fork it.
- **Type Safety** — TypeScript `strict`; no `any` at boundaries; runtime validation (Zod) where data crosses trust lines.
- **Accessibility-First Development** — WCAG 2.2 AA is a build requirement, not a later pass (see §11).

> **Why this matters for IDRM:** this is disaster-response software. Ambiguity, dead code, and untyped
> boundaries become **outage risk in the field**. The principles above are how we keep a fast-moving codebase
> safe to change under pressure.

### 1.2 IDRM-specific invariants (in addition to 1.1)
- **API contract is law.** Clients consume `/api/v1/...` exactly as specified in
  [`40-api-specification.md`](40-api-specification.md): version-in-path, `snake_case` fields, **UUID** ids,
  **ISO-8601 UTC** `*_at` timestamps, lowercase `snake_case` enum values, list responses wrapped
  `{ data, pagination }`, single resources as a bare object, and a machine-readable **error envelope** with a
  stable `code`. The frontend MUST NOT invent, rename, or reshape fields — map at the edge (§6), never guess.
- **Terminology parity.** The UI term **"help request"** is the API resource **`incident`**. Keep this mapping
  in one place; never leak `incident` into user-facing copy or `help_request` into API calls.
- **Same contract across clients.** React web, React Native, and the MVP HTML app are peers on one API. A
  **BFF/edge** service (Bun/Node/Deno **behind APISIX**) MAY compose or tailor responses per client, but the
  **public contract is never forked**.

---

## 2. Recommended tech stack

### 2.1 Frontend
| Concern | Choice | Notes |
|---|---|---|
| UI library | **React** | Function components + hooks only; no class components. |
| Language | **TypeScript** (`strict`) | Single source of shared types (§7). |
| Build / meta-framework | **Vite** (SPA) *or* **Next.js** (when SSR/SEO/route-level code-split is needed) | Pick once per app; document the choice in an ADR. |
| Styling | **TailwindCSS** | **Same design tokens as the MVP** — one design system across HTML/React/RN. |
| Server state | **TanStack Query** (React Query) | The default for anything from `/api/v1` (§5). |
| Forms | **React Hook Form** | Uncontrolled-first for performance (§8). |
| Validation | **Zod** | One schema → TS type + runtime guard; mirrors server rules (§8). |
| Client state | **Zustand** *or* **Redux Toolkit** | **Only if genuinely needed** (§5). Prefer Zustand for scope; Redux Toolkit for large, audited, time-travel-debuggable state. |
| Maps | **React-Leaflet** (+ Leaflet.markercluster) | The React binding of the MVP's Leaflet; PostGIS-driven (§14). |
| Data viz | Lightweight charting (e.g. visx/Recharts) | For the COP/analytics dashboards. |
| i18n | **react-i18next** (or Next i18n) | India-language localization (§12). |

### 2.2 Mobile (React Native / Expo)
- **React Native + Expo**, TypeScript, sharing the same **types, API client, Zod schemas, and design tokens**
  as web. Field-responder client is **offline-first** (§13) with native GPS/camera/push.

### 2.3 What is out of scope here
Gateway (**APISIX**), edge/BFF runtimes (**Bun/Node/Deno**), brokers, and infra live in
[`20-architecture-system.md`](20-architecture-system.md), [`80-ops-platform-and-deployment.md`](80-ops-platform-and-deployment.md),
and [`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md). This doc covers **client code**.

---

## 3. Project structure (feature-first)

Organize by **feature/domain**, not by file type — cohesion beats convenience. The IDRM domain modules map
directly to feature folders.

```
src/
  app/                 # app shell: providers, router, error boundary, query client
  features/            # ONE folder per IDRM domain module
    incidents/         # (a.k.a. "help requests" in UI copy)
      api/             # typed endpoints + query/mutation hooks for this feature
      components/      # feature-scoped UI
      hooks/           # feature-scoped logic
      schemas.ts       # Zod schemas + inferred types
      routes.tsx       # feature routes (lazy-loaded)
    users/  resources/ locations/ alerts/ notifications/
    reports/ files/ audit/ administration/
  shared/
    ui/                # design-system components (Button, Field, Map, DataTable…)
    api/               # base client (fetch wrapper, auth, error envelope, pagination)
    auth/              # session, RBAC guards, token refresh
    lib/               # pure utilities (dates, geo, formatting)
    types/             # cross-feature shared types
  styles/              # Tailwind config + tokens (shared with MVP design system)
```

Rules:
- A feature **MUST NOT** import another feature's internals. Cross-feature needs go through `shared/` or a
  published feature API (`features/x/api`).
- `shared/ui` is **presentational and domain-agnostic** — no `/api/v1` calls inside it.
- File naming: `PascalCase` for components, `camelCase` for hooks/utils, `kebab-case` for non-component files.

---

## 4. Component architecture & design system

- **Function components + hooks only.** No class components except a top-level **error boundary** (§15).
- **Presentational vs. container split.** `shared/ui` components are pure (props in, UI out, no data fetching).
  Feature "container" components wire data (via hooks) to presentational components.
- **One design system across all clients.** Tokens (color, spacing, type, radius, elevation) are defined once
  and shared by the MVP HTML app, React web, and RN. A component MUST NOT hard-code values that a token exists for.
- **Composition primitives** (`children`, slots, compound components) over boolean-prop explosions.
- **Accessibility baked into primitives:** `Button`, `Field`, `Dialog`, `Menu`, `Map` etc. ship correct roles,
  labels, and keyboard behavior so features get a11y for free (§11).

---

## 5. State management

Classify state before choosing a tool:

| State kind | Example | Owner |
|---|---|---|
| **Server state** | incidents list, a user profile, resource availability | **TanStack Query** (cache, refetch, invalidation) — the default. |
| **URL state** | filters, selected incident id, map bounds, pagination | **The router** (query params) — shareable & back-button safe. |
| **Ephemeral UI state** | modal open, form draft, hover | **local `useState`/`useReducer`** in the component. |
| **Global client state** | auth/session, active role, theme, offline queue | **Zustand/Redux Toolkit** — *only these truly-global concerns*. |

Rules:
- **MUST NOT** copy server data into a global store "to share it" — that creates two sources of truth. Share it
  via the Query cache (`queryKey`) instead.
- Reach for Redux Toolkit/Zustand **only** when global state is real (auth, offline sync). Over-storing is the
  most common IDRM-scale mistake.
- Query keys are **structured and typed** (e.g. `['incidents', { status, district }]`) so invalidation after a
  lifecycle transition is precise.

---

## 6. Data fetching & the API layer

- **One typed client** in `shared/api` wraps `fetch`: base URL `/api/v1`, auth header injection, refresh-on-401
  (§9), timeout, and **error-envelope decoding**. Features never call `fetch` directly.
- **Contract mapping at the edge.** The client validates responses with **Zod** and maps them to internal types
  in exactly one place. `*_at` → `Date`, enums → union types, `{ data, pagination }` → typed page objects.
- **Errors are typed by `code`.** The client turns the server error envelope into a discriminated union
  (`{ code: 'validation_error', fields } | { code: 'forbidden' } | …`) so UI reacts to `code`, never to a
  brittle message string.
- **Pagination is first-class.** List hooks expose cursor/offset + total from `pagination`; infinite lists use
  `useInfiniteQuery`. Never fetch "all rows."
- **Optimistic updates** are allowed for lifecycle actions (e.g. `accept` an incident) but MUST reconcile against
  server-authoritative state and roll back on error.

---

## 7. TypeScript standards

- `strict: true` (implies `noImplicitAny`, `strictNullChecks`, …). CI fails on type errors.
- **No `any` at boundaries.** External/unknown data enters as `unknown` and is narrowed via Zod.
- **Types are derived, not duplicated.** `type Incident = z.infer<typeof incidentSchema>` — one schema, one type.
- Enums as **string-literal unions** matching the API's lowercase `snake_case` values (e.g. incident status
  `'created' | 'approved' | 'accepted' | 'in_progress' | 'completed' | 'verified' | 'cancelled' | 'rejected'`).
- Prefer `type` for data shapes; `readonly`/`as const` for immutable config; exhaustive `switch` on unions
  (with a `never` default) so a new lifecycle state won't compile until it's handled.

---

## 8. Forms & validation

- **React Hook Form** for all forms (uncontrolled inputs → minimal re-renders, important on low-end field devices).
- **Zod resolver**: the same Zod schema validates the form *and* types the payload. **Client validation mirrors
  the server** but is never the only guard — the server remains authoritative.
- Accessible errors: every field has a `<label>`, errors are associated via `aria-describedby`, and the first
  invalid field receives focus on submit.
- **Idempotent submits.** Mutations that create/transition an incident send an idempotency key so a retry
  (flaky field network) never double-creates.

---

## 9. Authentication, session & RBAC

Mirrors [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md):

- **Tokens:** RS256 **JWT** — short-lived **access** (~60 min) + rotating, revocable **refresh** (~7 d). The
  client verifies nothing cryptographically itself; it treats tokens as opaque and trusts the server.
- **Storage:** access token in **memory**; refresh handled via **httpOnly, Secure, SameSite cookie** where the
  platform allows (web). **MUST NOT** persist tokens in `localStorage` (XSS-exfiltration risk). RN uses secure
  device storage (Keychain/Keystore).
- **Silent refresh** on 401 via a single-flight refresh (concurrent 401s await one refresh, then retry).
- **RBAC route guards** for the four roles + guest: `citizen`, `provider`, `coordinator`, `admin`, and the narrow
  **guest** path. A guard checks the role claim before rendering; the server re-checks every request (defense in
  depth). UI hides actions a role can't perform, but **hiding is never the security boundary** — the API is.
- Login lockout (5 attempts / 15 min) is enforced server-side; the client surfaces the `code`, never counts itself.
- FFP-only identity features (OIDC/SSO, MFA, ABAC, full role hierarchy, Auditor role) integrate through the same
  session layer when enabled.

---

## 10. Frontend security

- **XSS:** rely on React's escaping; `dangerouslySetInnerHTML` is **forbidden** unless the HTML is sanitized
  (DOMPurify) with a recorded justification.
- **CSP & headers** are set at the edge/gateway; the client MUST work under a strict CSP (no inline eval, no
  arbitrary remote scripts).
- **No secrets in the bundle.** No API keys, tokens, or credentials in client code or env-exposed vars.
- **No PII in URLs/query strings** (per project privacy rules); use POST bodies or opaque ids.
- **Media privacy (DPDP Act 2023):** before upload the client **strips EXIF/GPS**, compresses, resizes
  (≤1920px, ≥640×480), blur-checks, and runs the **face-DETECTION-only** quality gate (no biometric data is
  computed, stored, or sent — recognition/matching stays a consented FFP feature). Files ≤10 MB (PDF ≤~1.5 MB/pg);
  emergency "lite" path = one ≤~500 KB photo.
- **Consent-gated features** (per-request privacy levels, any future matching) render only after explicit,
  recorded consent.

---

## 11. Accessibility (WCAG 2.2 AA) — a build requirement

- Target **WCAG 2.2 AA** (the shared baseline — the MVP was also raised to 2.2 AA in the T3 alignment).
- **Semantic HTML first**, ARIA only to fill gaps. Landmarks, headings in order, one `<h1>` per view.
- **Full keyboard operability**; visible focus; logical tab order; focus trap + restore for dialogs.
- **Contrast** ≥ 4.5:1 text / 3:1 large text & UI; never rely on color alone (critical for red/amber/green
  incident **priority** and status).
- Forms: programmatic labels, error text, and `aria-live` for async status.
- **Maps need a non-map path:** every map action (find/act on an incident) is also reachable via an accessible
  **list/table** — a screen-reader user must be able to do the job without the map.
- Respect `prefers-reduced-motion`. Accessibility checks run in CI (§16).

---

## 12. Internationalization & localization

- **India-first, multilingual.** All user-facing strings go through **react-i18next** (no hard-coded copy).
- Externalized message catalogs per language; support RTL-readiness in layout even if initial languages are LTR.
- Locale-aware dates/numbers; but **wire/storage timestamps stay ISO-8601 UTC** — localize only at render.
- Keep translations consistent with the domain glossary ("help request" = incident, role names, lifecycle states).

---

## 13. Real-time & offline-first

- **Real-time (COP, tasking, alerts):** WebSocket/SSE **through the edge/BFF** and event backbone
  ([`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md)). The client subscribes per role/scope and
  reconciles pushes into the Query cache — it does not poll aggressively.
- **Offline-first (RN field client):** local store + **background sync queue**; writes are **idempotent** and
  reconcile against **server-authoritative state** on reconnect. Conflicts resolve server-side; the client shows
  clear pending/synced/failed states. Assume **flaky, low-bandwidth** networks — this is disaster response.

---

## 14. Maps & geospatial

- **React-Leaflet** (React binding of the MVP's Leaflet) with **marker clustering** for dense incident/resource
  layers. Map data is **PostGIS-driven** via `/api/v1` (bounding-box + filter queries) — the client requests only
  what's in view.
- Debounce map-move refetches; cap rendered markers (cluster beyond a threshold) to protect low-end devices.
- Coordinates follow the API contract; never place lat/long in URLs as user-identifying data.
- Provide the accessible list alternative (§11) for every map interaction.

---

## 15. Error handling & resilience

- **Error boundaries** at app and major-route level render a recoverable fallback (retry / go back) — never a
  white screen in the field.
- **Query/mutation errors** map from the typed `code` to specific UX (validation → inline; `forbidden` → explain;
  network → retry with backoff; `server_error` → safe fallback + report id).
- **Loading/empty/error/success** are designed states for every data view — no bare spinners for critical flows.
- **Retries with backoff** for idempotent reads; **no silent auto-retry** for state-changing writes (surface it).

---

## 16. Testing & quality gates

| Layer | Tooling | What it covers |
|---|---|---|
| Unit | **Vitest** | pure logic, hooks, mappers, Zod schemas |
| Component | **React Testing Library** | behavior & accessibility (query by role/label) |
| Integration | RTL + **MSW** (mock `/api/v1`) | feature flows against the real contract shape |
| E2E | **Playwright** | critical journeys (report a help request, accept, complete, verify) |
| Accessibility | **axe** (jest-axe / Playwright-axe) | automated a11y checks per component & page |

- **Test behavior, not implementation** (query by role/label, not test-ids-as-crutch).
- **MSW handlers are generated/validated against the OpenAPI contract** so tests can't drift from the API.
- **Coverage:** meaningful coverage on logic and critical journeys (a threshold in CI); coverage is a floor, not a goal.
- CI gates (all MUST pass to merge): **type-check → lint → unit/component → a11y → build**; E2E on the critical set.

---

## 17. Performance & scalability

- **Code-split by route/feature** (lazy + Suspense); keep the initial bundle within a documented budget.
- **Core Web Vitals** targets (LCP/CLS/INP) tracked in CI/RUM; regressions block release.
- **Virtualize** long lists/tables (incidents, audit); never render thousands of DOM nodes.
- Memoize deliberately (`useMemo`/`useCallback`/`React.memo`) where profiling shows benefit — not by reflex.
- Optimize images/media (already compressed client-side, §10); lazy-load below the fold.
- Assume **low-end Android + poor connectivity** as a primary target, not an edge case.

---

## 18. Observability (frontend)

- **Structured client logging** (levels, no PII) and **error tracking** (e.g. Sentry-class) with source maps and a
  correlation/report id surfaced to users for support.
- **RUM** for Core Web Vitals and key funnels (report→accept→complete→verify).
- Logs/metrics flow to the same platform observability stack; never log tokens or personal data.

---

## 19. Tooling & code quality

- **ESLint** (TS + react-hooks + jsx-a11y) and **Prettier**; lint/format run in **pre-commit** (Husky + lint-staged)
  and in CI.
- **TypeScript `strict`** everywhere; no `// @ts-ignore` without a justification comment.
- **Conventional Commits**; small, reviewable PRs; every PR passes §16 gates and this doc's `MUST` rules.
- **ADRs** record any deviation from a `SHOULD` and any stack choice (Vite vs Next, Zustand vs Redux).

---

## 20. Definition of Done (frontend feature)

A feature is done when it: meets the requirement; consumes `/api/v1` per contract (Zod-validated, typed);
handles loading/empty/error/success; is RBAC-guarded for the right roles; passes **WCAG 2.2 AA** checks; is
keyboard- and screen-reader-operable including a non-map path; is localized (no hard-coded copy); has unit +
component + relevant integration tests and E2E if it's a critical journey; meets performance budgets; strips
EXIF/PII on any upload; logs without PII; and updates docs/ADRs where decisions changed.

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`60-uidesign-frontend.md`](60-uidesign-frontend.md) (design/what) ·
[`40-api-specification.md`](40-api-specification.md) (the contract) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) (auth/RBAC) ·
[`20-architecture-system.md`](20-architecture-system.md) (edge/gateway) ·
[`70-quality-test-strategy.md`](70-quality-test-strategy.md) (test strategy) ·
[`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md) (real-time backbone) ·
MVP UI [`../idrm-mvp-docs/60-uidesign-web-interaction.md`](../idrm-mvp-docs/60-uidesign-web-interaction.md).
