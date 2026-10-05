# FLOW-ANALYSIS-PLAN — IDRM Page Templates **v2** (RBAC-driven · render-split)

**Created:** 2026-06-10
**Owner:** kalyan.narayana · **Author/agent:** Claude (Opus 4.8)
**Status:** ✅ **DONE through R6** (2026-06-11). An RBAC-organised mirror of `templates/` — **24 templates**
(10 role dashboards · 4 service-detail lenses · 2 scoped lists · 2 maps · 1 admin console · 5 shared) plus a
standalone showcase. Every page **and** the showcase carry the **display controls** (Heading/Body font face · size
XS–XL · Light/Dark/System theme · Ctrl/⌘+K search) and a documented **FastAPI-vs-Bun render strategy**. Icons are
inline **Lucide SVG** (no emoji). The post-registration **AAA + security workflows** (§14) and a **bird's-eye
create→update flow diagram** open the showcase.
**Build pipeline (run in this order):** `_apply-icons.ps1` → `_apply-controls.ps1` → `_build-showcase.ps1`.
**Full round-by-round history (R1–R6) is in §15 — Change Log.**
**Direction chosen by user (2026-06-10):** **(1) Strategy doc + mockups only** — keep everything as static,
self-contained HTML (previewable on the Windows authoring box); express the FastAPI-vs-Bun split as a
**rendering matrix + notes**, not as Jinja2/Bun code. **(2) Curated hero pages per role** — build the pages
where roles truly diverge; document the rest.

> **📌 Read me first.** This file is the single source of truth for the **v2** templates deliverable. It is a
> *mirror, not a replica* of `templates/FLOW-ANALYSIS-PLAN.md`: same design system and house rules, but the
> whole thing is **re-pivoted around the RBAC Permission Matrix (FS §3.3)** and adds a first-class
> **rendering-strategy** layer (which screens FastAPI must render vs which Bun can serve/offload). If work is
> interrupted, a fresh reader can resume from here alone — see §10 (checklist) and §11 (how to resume).

**Location:** `templates-v2/FLOW-ANALYSIS-PLAN.md` (project root: `idrm-mvp/`). v1 lives at `templates/`.

---

## 0. What v2 is, and how it differs from v1

| | **v1 (`templates/`)** | **v2 (`templates-v2/`)** |
|---|---|---|
| Organising idea | 15 pages by **feature/screen** (home, login, dashboard, …) | Pages by **role × capability** — the FS §3.3 matrix drives everything |
| Role handling | one `[ROLE]` badge per page (the *default* role) + a beige "Access ·" note | every page declares its **role**, its **data scope** (a visible *scope banner*), and its **render tier** |
| Rendering | static demo, "Option A" | static demo **plus** an explicit **FastAPI-render vs Bun-offload** decision per page (§6) |
| Differentiation | pages are role-aware in prose | pages are **extended per role** — distinct dashboards, distinct service-detail action sets, scoped lists |
| New UI atoms | — | `.render-tier` (F/B/H/WS badge), `.scope-banner`, `.role-strip`, `.role-switcher`, `.perm-matrix` |

**Unchanged from v1 (carried over verbatim):** the Slate + Emerald design system, Inter + 1.75 line-height,
fluid headings, status/priority/service-type/privacy tokens, accessibility rules, the `<hr color="skyblue">`
page separator, the beige "developer note" convention, live Leaflet maps + Chart.js, the build pipeline shape
(`pages/*` → generated showcase). The shared CSS/JS are **mirrored** from v1 and only *extended* (additive) —
see `assets/idrm-design-system.css` (v2 section at the bottom).

---

## 1. Source-of-truth & reconciliation (same contract as v1)

- **`docs/development/IDRM-FS.md` §3.3 Permission Matrix = the single source of truth** for who-can-do-what.
  §3.2 gives each role's CAN/CANNOT; §6 gives the workflows; §4 the functional requirements.
- **`CLAUDE.md`** — API reference, enums, key constraints.
- **Canonical roles** (10 accounts + a Public tier): `CITIZEN, VOLUNTEER, ORGANIZER, PROVIDER, MANAGER,
  EVENT_MANAGER, EXECUTIVE (🔒 Post-MVP), DM_AUTHORITY, AUDITOR, ADMIN` + **Public** (not logged in).
  ⚠️ Never use stale names (`SERVICE_PROVIDER`, `ORG_ADMIN`, `SYSTEM_ADMIN`).
- **Enums UPPERCASE & exact**; **HTTP = GET/POST only** with action sub-endpoints
  (`/approve /accept /complete /verify /cancel /reject`); **statuses** SUBMITTED → APPROVED → ACCEPTED →
  IN_PROGRESS → COMPLETED → VERIFIED (+ REJECTED/CANCELLED/EXPIRED/DISPUTED); emergencies auto-approve.
- **Privacy** PUBLIC / PROTECTED (default) / PRIVATE — *can only be raised*. **Redaction is a server concern**
  (see §6) — PROTECTED hides name/phone from the public; responders get contact **via the system**.
- **Post-MVP** (shown 🔒, never wired): Finance/Donations, AI chatbot, native mobile, `EXECUTIVE` role,
  the two finance permission rows.

---

## 2. The RBAC model, in one place

**11 tiers** (10 accounts + Public). Levels and "held by" per FS §3.1:

| Tier | Role code | Level | Held by | MVP |
|---|---|---|---|---|
| Public | _(anon)_ | — | Anonymous visitors | ✅ view-only |
| Citizen | `CITIZEN` | 2 | Affected individuals | ✅ |
| Volunteer | `VOLUNTEER` | 3 | Community helpers | ✅ |
| Organizer | `ORGANIZER` | 4 | Volunteer team-leads | ✅ |
| Service Provider | `PROVIDER` | 4 | NGOs / hospitals delivering relief | ✅ |
| Manager | `MANAGER` | 5 | Provider-org managers | ✅ |
| Event Manager | `EVENT_MANAGER` | 5 | Runs a disaster-event instance (GO/NGO) | ✅ |
| Executive | `EXECUTIVE` | 6 | Provider-org senior leadership | 🔒 Post-MVP |
| Event Admin | `DM_AUTHORITY` | 7 | Approving authority (GO **or** vetted NGO) | ✅ |
| Auditor | `AUDITOR` | 7 | Accountability / credibility reviewer | ✅ read-only |
| System Admin | `ADMIN` | 8 | Platform IT team | ✅ |

### 2.1 Permission Matrix (FS §3.3 — reproduced; the contract v2 renders)

Legend: ✅ full · ❌ none · ⚠️ limited (scope) · 🔒 Post-MVP.

| Permission | Public | Citizen | Volunteer | Organizer | Provider | Manager | Event Mgr | Exec | DM Auth | Auditor | Admin |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| View public map | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🔒 | ✅ | ✅ | ✅ |
| Create service request | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | 🔒 | ✅ | ❌ | ✅ |
| View own requests | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 🔒 | ✅ | ✅ | ✅ |
| View all requests | ❌ | ❌ | ⚠️ Area | ⚠️ Area | ⚠️ Type | ⚠️ Org | ⚠️ Event | 🔒 | ✅ | ✅ | ✅ |
| Accept service request | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | 🔒 | ❌ | ❌ | ✅ |
| Approve service request † | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 🔒 | ✅ | ❌ | ✅ |
| Create & manage disaster events | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | 🔒 | ✅ | ❌ | ✅ |
| Allocate funds | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| View financial data | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 | 🔒 |
| Manage users | ❌ | ❌ | ❌ | ⚠️ Team | ⚠️ Org | ⚠️ Org | ⚠️ Event | 🔒 | ⚠️ Jurisd. | ❌ | ✅ |
| View audit logs | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 🔒 | ⚠️ Limited | ✅ | ✅ |
| System configuration | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | 🔒 | ❌ | ❌ | ✅ |

† Emergency/urgent (CRITICAL/HIGH) requests are **auto-approved by the system**; DM Authority handles
non-urgent approvals + after-the-fact credibility review. **Finance rows** are 🔒 for everyone in the MVP.

### 2.2 The five **scope qualifiers** (the ⚠️ cells) — v2 makes these visible

The matrix's "View all requests" / "Manage users" ⚠️ cells encode a *data boundary*. v2 surfaces each as a
**`.scope-banner`** at the top of the relevant page so the boundary is never implicit:

| Scope | Who | Boundary (server-enforced) | Banner class |
|---|---|---|---|
| **Own** | Citizen | only rows where `requestor_id = me` | `.scope-own` |
| **Area** | Volunteer, Organizer | requests whose location ∈ my assigned area polygon | `.scope-limited` |
| **Type** | Provider | APPROVED requests whose `service_type` ∈ my types **and** location ∈ my service area | `.scope-limited` |
| **Org** | Manager | requests handled by any provider in my organisation | `.scope-limited` |
| **Event** | Event Manager | requests linked to my disaster-event instance | `.scope-limited` |
| **Jurisdiction** | DM Authority | all requests within my jurisdiction polygon | `.scope-jurisdiction` |
| **All (read-only)** | Auditor | every request, but no writes | `.scope-all .scope-readonly` |
| **All** | Admin | everything, everywhere | `.scope-all` |

> **Why this matters for v2:** the scope is exactly what a server-side query `WHERE` clause must enforce — it is
> **not** something the browser can be trusted to filter. That single fact is the spine of the render strategy
> in §6: *scope = a reason to render on FastAPI.*

---

## 3. RBAC-driven plan — **one capability at a time** (the "redo w.r.t. each permission" ask)

For each row of the §3.3 matrix: the roles that hold it, the **page/fragment** in v2 that realises it, the
**render tier** (see §6 for the F/B/H/WS key), and the design nuance.

> Read this as: *"to deliver capability X, build screen Y, rendered by Z, gated like W."*

### C1 · View public map — *Public + everyone* — Tier **B**(+H overlays)
- **Screen:** `pages/map/public.html`. Anonymous base map + **PUBLIC-privacy** markers only (redacted).
- **Nuance:** Public sees aggregate/PUBLIC pins; signed-in roles get richer overlays (their own pins, zone,
  type filters) layered on top. The *base* is identical for all → cache it (Bun); the *overlay* is per-role
  (FastAPI). Geo cluster results cached per zoom+bounds.

### C2 · Create service request — *Citizen, Volunteer, Organizer, DM Authority, Admin* — Tier **F**
- **Screen:** create-request form (mirrored from v1 `06-create-service`; reachable from each eligible dashboard).
- **Nuance:** Volunteer/Organizer get **"create on behalf of"** (requestor ≠ me). PROVIDER/MANAGER/EVENT_MANAGER/
  AUDITOR **must not** see the entry point (conflict-of-interest / role mismatch) — the button is *absent*,
  server-rendered, not merely `display:none`. Privacy defaults PROTECTED; emergencies auto-approve on submit.

### C3 · View own requests — *all signed-in* — Tier **F**
- **Screen:** the "Your/active requests" block on every role dashboard; `pages/service-detail/requestor.html`.
- **Nuance:** identical capability, different surrounding chrome per role (a Citizen's "own" vs a Provider's
  "mine to deliver"). Always `requestor_id = me` (or `assignee = me` for providers).

### C4 · View all requests (scoped) — *Volunteer→Admin, scoped* — Tier **F**
- **Screens:** `pages/requests-list/*` (one per scope) + each dashboard's queue.
  Built: `provider-type.html`, `authority-jurisdiction.html`. Documented: area/org/event variants (§5.3).
- **Nuance:** the **`.scope-banner`** states the boundary; the table columns differ (Provider sees distance +
  accept; Authority sees requestor + approve/priority; Auditor sees audit trail, read-only). Scope filter is a
  server `WHERE` — **never** a client filter.

### C5 · Accept service request — *Provider, Manager, Admin* — Tier **F** + **WS**
- **Screen:** Provider dashboard "Available" list + `pages/service-detail/provider.html` (the Accept action).
- **Nuance:** only **APPROVED** requests are acceptable (BR-SR-007); capacity gate (BR-PM-002) disables Accept
  when full; a provider can't accept own-org requests (BR-PM-005). **Realtime (WS):** if someone else accepts
  first, the card flips to "taken" live. Manager can accept on behalf of an org provider.

### C6 · Approve / reject service request — *DM Authority, Admin* — Tier **F**
- **Screen:** `pages/role-dashboard/dm-authority.html` approval queue + `pages/service-detail/dm-authority.html`.
- **Nuance:** approve / reject(reason) / set-priority / resolve **DISPUTED** (→ IN_PROGRESS or → REJECTED) /
  force-change. Emergencies arrive pre-APPROVED (system) and are flagged "auto-approved — review credibility".

### C7 · Create & manage disaster events — *Event Manager, DM Authority, Admin* — Tier **F**(+H map draw)
- **Screens:** `pages/role-dashboard/event-manager.html` (event console) and DM Authority dashboard (declare +
  draw zone). Map-draw is a hybrid: Bun-served map shell + FastAPI persistence of the polygon.
- **Nuance:** Event Manager **runs** an event (link requests, assign within it) but **cannot approve/reject**;
  DM Authority **declares** events + defines the affected polygon + approves. Auto-link: requests inside the
  polygon attach to the event.

### C8 · Allocate funds / C9 · View financial data — 🔒 **Post-MVP, all roles**
- **Screen:** none built. Shown only as a **locked** tile on relevant dashboards (DM Authority, Executive,
  Auditor) with a 🔒 "Post-MVP" badge. No endpoints, no data.

### C10 · Manage users (scoped) — *Organizer(Team)→Admin* — Tier **F**
- **Screens:** Admin → `pages/admin-console/admin-system.html` (full CRUD + role assignment). Organizer (team),
  Manager (org), Event Manager (event), DM Authority (jurisdiction) get **scoped** member panels on their
  dashboards. Only **Admin** assigns roles (BR-ROLE-002) and does system-wide user CRUD.
- **Nuance:** the scoped panels can invite/assign *within* their boundary only; the role dropdown they see is
  pruned server-side to roles they're allowed to grant.

### C11 · View audit logs — *Auditor(full), Admin(full), DM Authority(limited)* — Tier **F**
- **Screen:** `pages/role-dashboard/auditor.html` (audit stream + compliance + flag + export). DM Authority gets
  a *limited* slice on their dashboard; Admin has full access via the admin console.
- **Nuance:** logs are **immutable** (no edit/delete in the UI at all — even for Admin); export is allowed.

### C12 · System configuration — *Admin only* — Tier **F**
- **Screen:** `pages/admin-console/admin-system.html` config panel + system-health metrics.
- **Nuance:** the most privileged surface; every action is itself audited (shown as an "all actions logged" note).

---

## 4. Per-role page-extension spec (the "subtle nuances per role" ask)

For each tier: its **landing page**, what it **sees / can do**, its **scope**, the **service-detail actions**
it gets, and the **render tier**. This is the contract each built page honours.

| Role | Landing (built file) | Distinctive content | Scope | Service-detail actions | Tier |
|---|---|---|---|---|---|
| **Public** | `shared/home.html` + `map/public.html` | hero, hotlines (108/112/1070), public stats, **phone+OTP quick-start**; redacted public pins | none | view PUBLIC only (redacted) → prompt to start | **B** |
| **Citizen** | `role-dashboard/citizen.html` | own active requests, **+ Request help**, nearby, recent alerts, mini-map of own pins | Own | track · **cancel** (SUBMITTED/APPROVED) · **verify + rate** · **dispute** | **F** |
| **Volunteer** | `role-dashboard/volunteer.html` | + **area queue**, **create on behalf**, field notes, **verify delivery** | ⚠️ Area | + add field note/photo · mark **Verified Complete** | **F** |
| **Organizer** | `role-dashboard/organizer.html` | + **team roster**, **assign tasks**, team performance, field reports | ⚠️ Area (team) | volunteer actions + **reassign within team** | **F** |
| **Provider** | `role-dashboard/provider.html` | **available** (APPROVED, my type) + **assigned**, **capacity meter**, performance; **no create** | ⚠️ Type+Area | **accept** · **start (IN_PROGRESS)** · **complete** · upload proof · contact-via-system | **F**+WS |
| **Manager** | `role-dashboard/manager.html` | **org overview**, providers list, org metrics, **service-area map**, org reports | ⚠️ Org | accept on behalf · **assign provider** · org notes | **F** |
| **Event Manager** | `role-dashboard/event-manager.html` | **event console**: status/timeline, attached requests, **assignment board**, event report | ⚠️ Event | link/unlink to event · **assign provider/volunteer**; **no approve** | **F** |
| **Executive** 🔒 | `role-dashboard/executive-reserved.html` | **locked** placeholder: strategic analytics + financial summaries (Post-MVP) | 🔒 | — | **F** (later) |
| **DM Authority** | `role-dashboard/dm-authority.html` | **approval queue**, jurisdiction KPIs, **declare event / draw zone**, priority triage, limited audit | Jurisdiction | **approve · reject(reason) · set priority · resolve DISPUTED · cancel any** | **F** |
| **Auditor** | `role-dashboard/auditor.html` | **audit log stream**, compliance snapshot, **flag irregularity**, export; finance 🔒 | All (read-only) | **read-only** + full audit trail + **flag** | **F** |
| **Admin** | `admin-console/admin-system.html` | **users + roles**, orgs, **system health**, **config**, audit access | All | everything + force-change + audit | **F** |

> **Cross-cutting nuances baked into every built page:** (a) the header carries `[◆ IDRM] [ROLE]` + a
> **render-tier badge**; (b) a **scope banner** states the data boundary; (c) the beige developer note lists
> **Access · / Scope · / Render · / API ·**; (d) actions a role lacks are **absent**, not disabled-and-hidden
> — to mirror that the server simply won't render them.

---

## 5. Per-hero-page role variance (how each screen morphs by role)

### 5.1 Dashboard — *the* role-divergent screen
Ten built variants under `pages/role-dashboard/`. Same shell (navbar + sidebar + scope banner + beige note),
**different body**: Citizen=own loop · Volunteer=area+on-behalf · Organizer=team · Provider=capacity/available ·
Manager=org · Event Mgr=event console · DM Authority=approvals · Auditor=audit · Admin=system · Executive=locked.

### 5.2 Service detail — same record, different powers
Four built variants under `pages/service-detail/`: **requestor** (track/cancel/verify/dispute), **provider**
(accept/start/complete/proof + privacy-gated contact), **dm-authority** (approve/reject/priority/dispute),
**auditor** (read-only + audit trail + flag). The **timeline** is shared; the **action bar** + **contact block**
(redaction) differ. Public gets a redacted read-only view (documented; folded into `map/public.html` detail).

### 5.3 Requests list — same table, different scope + columns
Built: **provider-type** (distance + Accept; APPROVED only) and **authority-jurisdiction** (requestor + Approve/
priority). Documented variants reuse the same template with a different `.scope-banner` + column set:
volunteer-area, organizer-area(team), manager-org, event-event, auditor-all(read-only).

### 5.4 Map — same canvas, different layers
Built: **public** (anonymous, PUBLIC pins, view-only) and **dm-authority-zone** (jurisdiction + draw affected
area + cluster). Provider-nearby (proximity + accept) and event-area are documented reuses.

### 5.5 Admin / event consoles — the management deep-ends
Built: **admin-system** (users/roles/config/health). DM-authority approvals + event declaration live on the
DM Authority dashboard; Auditor's audit console is the Auditor dashboard.

---

## 6. 🚦 Rendering strategy — **FastAPI vs Bun** (efficiently *and* effectively)

> The headline question. IDRM's runtime is **Browsers → Bun API Gateway (3000, +WS 3001) → FastAPI monolith
> (8000) → Postgres/PostGIS + Redis**. "Rendering" can therefore happen at **three** places: the **Bun edge**
> (gateway), the **FastAPI** app (Python/Jinja server-render), or the **client** (React SPA 5174 / vanilla JS
> hydration). v2 assigns every screen a **tier** so the split is explicit.

### 6.1 The decision rule (one sentence each)
- **Render on FastAPI (Tier F)** when the output depends on **who is asking** — role, permissions, *scope*
  (§2.2), or **privacy redaction** (PROTECTED/PRIVATE) — or needs **authoritative DB/PostGIS/Python compute**.
  These are per-user, barely cacheable, and **security-critical**: the RBAC gate and PII redaction must happen
  where the data lives, never in the browser.
- **Offload to Bun (Tier B)** when the output is the **same for everyone** (public/anonymous), **static or
  rarely-changing**, **cacheable** at the edge/CDN, or is a **cross-cutting edge concern** (JWT verify, refresh,
  rate-limit, CORS, security headers, gzip/brotli, routing/proxy) or a **long-lived connection** (WebSocket).
  Bun is the fast, concurrency-friendly front door — ideal for 2G/emergency first paint.
- **Hybrid (Tier H)** when a page is a **cacheable shell + a personalised island**: Bun streams the static shell
  instantly, then stitches in a FastAPI-rendered fragment (htmx partial / edge-side include / streamed SSR).
  Fast first paint **and** authoritative content.
- **Realtime (Tier WS)**: Bun's WebSocket (3001) ↔ **Redis pub/sub** pushes `request_created/updated/deleted`
  to any open page; the DOM patch is client-side, the *event* originates in FastAPI. Bun holds the sockets so
  the Python workers aren't tied up.

### 6.2 The render map (every screen / fragment)

| Screen / fragment | Tier | Why | Cache policy |
|---|:--:|---|---|
| Home / landing, hotlines, public stats | **B** | identical for all; marketing + aggregate numbers | edge cache (long); stats via short-TTL JSON |
| Register / Login / Forgot-password (forms) | **B** | static forms; the POST is proxied to FastAPI `/auth/*` | static, hashed assets |
| Design assets (CSS/JS/fonts/Leaflet/Chart.js) | **B** | immutable | CDN/immutable, content-hashed |
| Public map **base** + PUBLIC pins | **B** | anonymous, redacted, same for all | tiles cached; pins short TTL |
| Geo **cluster** tiles (`/geo/cluster`) | **B over F** | PostGIS computes once (F); Bun/Redis caches per `zoom+bounds` | short keyed TTL |
| **Role dashboards** (all 10) | **F** | role + own data + *which actions exist* | `no-store` (per-user) |
| **Service detail** | **F** | **privacy redaction** + role action set | `no-store` |
| **Requests lists** (scoped) | **F** | server-side `WHERE` scope (Area/Type/Org/Event/Jurisd.) | `no-store` |
| Approval queue / DM console | **F** | authority-only, sensitive writes | `no-store` |
| Audit console | **F** | auditor/admin only; immutable logs | `no-store` |
| Admin users / roles / config / health | **F** | most-privileged; every action audited | `no-store` |
| Analytics dashboard (`/analytics/*`) | **F** | Python aggregation; role-scoped | short **private** cache |
| Profile / notifications | **F** | per-user | `no-store` |
| **Authenticated app shell** (nav/sidebar/footer) | **H** | shell cacheable *per role-class*; data is an island | shell cached by role-class; island `no-store` |
| **Live map** (authenticated overlays / zone) | **H** | Bun base + FastAPI personalised/zone overlay | base cached; overlay `no-store` |
| Realtime status updates | **WS** | push lifecycle changes live | n/a |
| JWT verify/refresh · rate-limit · CORS · headers · compression | **B** | every request, edge concern | n/a |

### 6.3 Why this is efficient *and* effective
- **Efficient:** Bun absorbs the ~80% of traffic that is **public/static/cacheable/real-time** (home, auth
  shells, assets, cluster tiles, WS fan-out, compression) so FastAPI only spends Python cycles on the ~20% that
  is **genuinely per-user**. Result: fewer Python renders, edge cache hits, small payloads → fast on 3G/2G
  (NFR-USE-002), and Python workers stay free for DB/PostGIS work instead of holding sockets.
- **Effective (correct + safe):** every **permission gate** and **privacy redaction** runs in FastAPI, against
  the database, where it **cannot be bypassed** by a crafted client. The browser never receives data a role may
  not see — there is no "hidden div" with PII. One server-side source of truth for RBAC = no drift between the
  three frontends (HTML/Tailwind, React SPA, future mobile).
- **The litmus test (put on a sticky note):** *If the bytes change based on who is logged in, or contain anything
  a less-privileged viewer must not see → **FastAPI (F)**. If the bytes are the same for everyone, or are plumbing
  → **Bun (B)**. If you want a fast shell with a private filling → **Hybrid (H)**. If it must update without a
  reload → **WebSocket (WS)**.*

### 6.4 How v2 mockups encode the tier
Every built page header shows a **render-tier badge** next to `[◆ IDRM] [ROLE]`, and the beige note carries a
`Render ·` line explaining the choice. The showcase groups frames so you can see the **B → F → H** progression.

---

## 7. Deliverable file tree (`templates-v2/`)

```
templates-v2/
├── FLOW-ANALYSIS-PLAN.md             # THIS FILE — RBAC plan + render strategy + checklist + change log (§15)
├── README.md                         # quick orientation (what v2 is, how to view/build)
├── idrm-rbac-showcase.html           # ⭐ GENERATED standalone: controls bar + plan band + role switcher + 24 frames
│   # ----- sources the showcase is assembled from -----
├── _showcase-intro.html              # beige plan/RBAC/render band + bird's-eye diagram (top of the showcase)
├── _showcase-controls.html           # the display-controls bar + Ctrl/⌘+K search modal (font/size/theme/search)
│   # ----- PowerShell helpers (pure-ASCII, UTF-8 no BOM — R2). Pipeline order: icons → controls → build -----
├── _apply-icons.ps1                  # emoji → inline Lucide SVG across pages/* + intro (idempotent)
├── _apply-controls.ps1               # injects the controls bar + css/js links + fonts into every pages/* (idempotent)
├── _build-showcase.ps1               # (re)generates idrm-rbac-showcase.html; strips the per-page controls bar
├── _preview-server.js                # tiny Node static server → http://localhost:4600 (Windows-friendly preview)
├── assets/
│   ├── idrm-design-system.css        # MIRRORED from v1 + v2 RBAC additions (tiers/scope/role-strip/matrix) + mobile fixes
│   ├── idrm-templates.js             # MIRRORED from v1 + data-match (confirm-password) + SVG password toggle
│   ├── showcase-controls.css         # controls bar + the FULL dark-theme remap of the --color-* tokens
│   └── showcase-controls.js          # font/size/theme(System via matchMedia)/search; persists to localStorage
└── pages/                            # 24 standalone templates (each links the assets + carries the controls bar)
    ├── role-dashboard/               # the centrepiece — one per role (subtle per-role nuances)
    │   ├── citizen.html  volunteer.html  organizer.html  provider.html  manager.html
    │   ├── event-manager.html  dm-authority.html  auditor.html  admin.html
    │   └── executive-reserved.html   # 🔒 Post-MVP locked placeholder
    ├── service-detail/               # same record, per-role action set + redaction
    │   ├── requestor.html  provider.html  dm-authority.html  auditor.html
    ├── requests-list/                # scoped "view all requests"
    │   ├── provider-type.html  authority-jurisdiction.html
    ├── map/                          # public vs authority(zone)
    │   ├── public.html  dm-authority-zone.html
    ├── admin-console/
    │   └── admin-system.html         # users/roles/config/health (Admin)
    └── shared/                       # role-agnostic, mirrored from v1
        ├── home.html  login.html  register.html  profile.html  notifications.html
```

---

## 8. Page inventory (built) — what each shows · access · scope · render · API

| # | File | Role | Scope | Tier | Key content | API hooks (documented) |
|---|---|---|---|:--:|---|---|
| D1 | role-dashboard/citizen | CITIZEN | Own | F | own active requests, +Request, nearby, mini-map | `GET /users/me`, `/services?requestor=me`, `/notifications` |
| D2 | role-dashboard/volunteer | VOLUNTEER | Area | F | area queue, create-on-behalf, verify | `GET /services?area=…`, `POST /services`, `/verify` |
| D3 | role-dashboard/organizer | ORGANIZER | Area | F | team roster, assign tasks, team metrics | `GET /services?area=…`, `/users?team=me` |
| D4 | role-dashboard/provider | PROVIDER | Type+Area | F+WS | available/assigned, capacity meter, performance | `GET /geo/nearby`, `/services?provider=me`, `/accept` |
| D5 | role-dashboard/manager | MANAGER | Org | F | org overview, providers, service areas | `GET /services?org=…`, `/users?org=me` |
| D6 | role-dashboard/event-manager | EVENT_MANAGER | Event | F | event console, attached requests, assignment board | `GET /services?event=…`, `/events/{id}` |
| D7 | role-dashboard/dm-authority | DM_AUTHORITY | Jurisdiction | F | approval queue, KPIs, declare event, triage | `GET /analytics/dashboard`, `/approve`, `/reject` |
| D8 | role-dashboard/auditor | AUDITOR | All (RO) | F | audit stream, compliance, flag, export | `GET /audit/*`, `/services` (read-only) |
| D9 | role-dashboard/admin | ADMIN | All | F | users/roles, orgs, health, config | `GET /admin/*`, `POST /users/{id}/role` |
| D10 | role-dashboard/executive-reserved | EXECUTIVE 🔒 | — | F | locked Post-MVP placeholder | none |
| S1 | service-detail/requestor | CITIZEN/VOL/ORG | Own | F | timeline, cancel/verify/dispute, rating | `GET /services/{id}`, `/cancel`, `/verify` |
| S2 | service-detail/provider | PROVIDER/MANAGER | assigned | F+WS | accept/start/complete, proof, privacy-gated contact | `/accept`, `/complete`, WS |
| S3 | service-detail/dm-authority | DM_AUTHORITY | Jurisdiction | F | approve/reject/priority/resolve-dispute | `/approve`, `/reject` |
| S4 | service-detail/auditor | AUDITOR | All (RO) | F | read-only + audit trail + flag | `GET /services/{id}`, `/audit/{id}` |
| L1 | requests-list/provider-type | PROVIDER | Type+Area | F | distance + Accept; APPROVED only | `GET /geo/nearby?type=…` |
| L2 | requests-list/authority-jurisdiction | DM_AUTHORITY | Jurisdiction | F | requestor + Approve/priority | `GET /services?status=SUBMITTED` |
| M1 | map/public | Public | none | B | anonymous, PUBLIC pins, view-only | `GET /geo/cluster` (cached) |
| M2 | map/dm-authority-zone | DM_AUTHORITY | Jurisdiction | H | draw affected zone + cluster | `GET /geo/nearby`, `POST /events/{id}/zone` |
| A1 | admin-console/admin-system | ADMIN | All | F | users/roles, config, health | `GET/POST /admin/*` |
| H1 | shared/home | Public | none | B | hero, hotlines, stats, quick-start | none |
| H2 | shared/login | Public | none | B | email/password, refresh note | `POST /auth/login`, `/auth/refresh` |
| H3 | shared/register | Public | none | B | register (CITIZEN/PROVIDER/VOLUNTEER only) | `POST /auth/register` |
| H4 | shared/profile | any signed-in | Own | F | edit name/phone/lang; password; read-only email/role | `GET/POST /users/me` |
| H5 | shared/notifications | any signed-in | Own | F | list, unread, mark read | `GET /notifications`, `/{id}/read` |

---

## 9. Workflows, by role (mirrors FS §6; maps to the built pages)

1. **Citizen core loop** — home → quick-start/login → **citizen dashboard** → create → **requestor detail**
   (track) → verify + rate. *SUBMITTED → (auto-APPROVED if emergency) → ACCEPTED → IN_PROGRESS → COMPLETED →
   VERIFIED.*
2. **Volunteer survey** — **volunteer dashboard** → create-on-behalf (×N) → area queue → field notes → verify.
3. **Organizer coordinate** — **organizer dashboard** → assign tasks to team → track team queue.
4. **Provider deliver** — **provider dashboard** → available (`provider-type` list) → **accept** → **provider
   detail** (start → complete + proof) → requestor verifies. (WS flips a card to "taken" if beaten to it.)
5. **Manager org-run** — **manager dashboard** → org queue → assign provider → org performance.
6. **Event Manager run-event** — **event-manager dashboard** → link requests → assignment board → event report.
7. **DM Authority approve & coordinate** — **dm-authority dashboard** / `authority-jurisdiction` list →
   approve/reject/priority → declare event + **draw zone** (`dm-authority-zone`) → resolve DISPUTED.
8. **Auditor oversee** — **auditor dashboard** → audit stream → verify delivery records → flag → export.
9. **Admin operate** — **admin-system** → users/roles → orgs → health → config (all audited).
10. **Public** — home + `map/public` (view-only) → prompted to quick-start to act.

---

## 10. Task checklist (UPDATE AFTER EACH TASK)

Legend: ⬜ todo · 🟡 in progress · ✅ done

- ✅ T0. Read v1 (`templates/`) + FS §3.3; lock direction (mockups+doc; curated hero pages).
- ✅ T1. Scaffold `templates-v2/` tree; **mirror** CSS/JS from v1; append v2 RBAC CSS (tiers/scope/role-strip/matrix).
- ✅ T2. Write this RBAC-driven `FLOW-ANALYSIS-PLAN.md` (matrix · per-role spec · render strategy).
- ✅ T3. Build 10 role dashboards (`pages/role-dashboard/*`).
- ✅ T4. Build 4 service-detail variants (`pages/service-detail/*`).
- ✅ T5. Build scoped lists (`requests-list/*`), maps (`map/*`), admin console (`admin-console/*`).
- ✅ T6. Build shared pages (`shared/*`) — mirrored from v1.
- ✅ T7. Write `_showcase-intro.html` (beige plan + matrix + render band + role switcher).
- ✅ T8. Write `_build-showcase.ps1`; generate `idrm-rbac-showcase.html`; verify counts/encoding (24 frames; 0 mojibake; 0 svg-in-attr; no BOM).
- ✅ T9. Write `README.md`; final validation pass (§13); Status flipped to ✅.

---

## 11. How to resume (if interrupted)
1. Read §2 (RBAC model + scopes), §3 (capability→screen→tier), §4 (per-role spec), §6 (render strategy).
2. Check §10 for the first non-✅ item; continue there.
3. Honour the contract: enums UPPERCASE; canonical roles; GET/POST + action endpoints; privacy redaction is a
   *server* concern; actions a role lacks are **absent** in the markup (not disabled).
4. Shared CSS/JS are mirrored from v1 + the additive v2 block. Keep `pages/*` and the generated showcase in sync
   (rebuild with `_build-showcase.ps1`). Update §10 after each task.

---

## 12. Design rules carried over from v1 (must stay true)
The full R1–R14 ruleset in `templates/FLOW-ANALYSIS-PLAN.md` §13 still governs v2. Highlights that bite:
- **R2 encoding:** `.ps1` scripts are **pure ASCII**; emit non-ASCII as HTML entities or from code points; write
  files UTF-8 **no BOM**. (Why the build script below avoids raw —/·/©/emoji.)
- **R4 type:** Inter, body line-height **1.75**, fluid headings, one `<h1>`/page.
- **R5 colour:** Slate+Emerald; mellow service-type hexes; beige = metadata.
- **R8 header:** `[◆ IDRM] [ROLE]` left; auth element right (Sign in on public / account icon on auth). v2 adds
  the **render-tier badge** beside the role.
- **R13 a11y/responsive:** 360/768/1280; ≥44px targets; focus rings; colour never the only signal; buttons keep
  readable text in all states.
- **v2 deltas:** add `.scope-banner` (state the data boundary), `.render-tier` (state who renders), and keep
  role-absent actions out of the DOM.
- **R6 icons (enforced in v2):** all UI/nav/scope/workflow icons are **inline Lucide SVG** (`<svg class="ic">`),
  never emoji — run `_apply-icons.ps1` (pure ASCII; builds the emoji match-keys from code points) before
  `_build-showcase.ps1`. Only typographic glyphs stay (`●` status, `→` flow, `★` rating, `✓` matrix). Never put an
  SVG in an attribute (R7); emoji that can't be SVG (e.g. inside `<option>`) become plain text.
- **Display controls — shared, NOT sticky:** `_showcase-controls.*` give Heading/Body font, size XS–XL (default
  **M = 15px**), Light/Dark/System theme (System resolved via `matchMedia` → `[data-theme]`) and Ctrl/⌘+K search; they
  sit on the showcase **and** every page (injected by `_apply-controls.ps1`, wrapped in `<!-- SC-CONTROLS-START/END -->`
  so the build strips them from the frames → one bar in the showcase). The bar is **`position: relative` (not sticky)**
  so the page's own navbar/sidebar stay the sticky layer; it's compacted on phones (labels hidden, selects capped).
  Dark mode is a full remap of the `--color-*` tokens + fix-ups for the few hard-coded-hex chips.
- **Mobile display — no horizontal overflow:** the app `column` layout MUST `align-items: stretch` + `.app-main
  { width:100% }` (else it shrink-wraps a long API URL and overflows); `code { overflow-wrap: anywhere }` wraps long
  endpoints; `.bottom-nav a { flex:1 1 0; min-width:0 }` + `.bottom-nav { max-width:100vw }` keep the tab bar in the
  viewport. Verify `scrollWidth == clientWidth` at 360/375.
- **Forms — confirm + match:** sensitive changes use a **double-entry** field validated with `data-match="<id>"` (live
  + on submit) so typos are caught before save — see profile *Change password* (Current · New + strength · Confirm).
  `idrm-templates.js` resolves the error element via `closest('.form-group')`.

---

## 13. Validation checklist (run before flipping Status to ✅)
- [ ] 10 role dashboards exist; each has `[ROLE]` badge, a **scope banner**, a **render-tier badge**, and a beige
      `Access · / Scope · / Render · / API ·` note.
- [ ] Service-detail variants differ only in the **action bar** + **contact/redaction** block (shared timeline).
- [ ] Lists carry the correct `.scope-banner`; no client-side scope filtering implied.
- [ ] Render tiers match §6.2 (public/auth/static = B; per-user/sensitive = F; shell+island = H; live = WS).
- [ ] Roles canonical; enums UPPERCASE; HTTP GET/POST + action endpoints; Finance/Exec shown 🔒 only.
- [ ] Body line-height 28px (1.75×); `<hr color="skyblue">` between frames; **no console errors**; no mojibake.
- [ ] Responsive at 360/768/1280; account/Sign-in element correct per public-vs-auth.
- [ ] **No horizontal overflow** at 360/375 (`scrollWidth == clientWidth`; the `.bottom-nav` 100vw value in the
      preview is a fixed-CB emulation artifact, not a real-device overflow).
- [ ] **Controls bar** on the showcase + every page; **non-sticky**; font/size/theme/search work; Light/Dark/System
      all render (dark = full token remap, no white boxes); prefs persist (localStorage).
- [ ] **Change password** = Current + New (strength) + **Confirm**; mismatch shows the error + red border live and
      clears on match.
- [ ] **Footer** organised (brand + tagline · **helplines 108/112/1070** · links) on `home.html` + the showcase.

---

## 14. Post-registration workflows — AAA + Security / Confidentiality / Integrity / Authenticity

> **Added 2026-06-11 (v2 · R2).** After a user registers (or quick-starts with phone + OTP), every interaction
> runs through six concerns. Each is listed, **elucidated**, and broken into **sub-workflows** mapped to the
> IDRM pages, endpoints, render tier (§6) and FS requirements. The **bird's-eye flow diagram** + per-dimension
> **sub-workflow ribbons** are depicted at the **start of the showcase** (anchors `#overview` and `#workflows`).

**The one-line mental model:**
`Register → Authentication → Authorization (role + scope) → Create / Update an entity → { Confidentiality · Integrity · Authenticity } guard every byte → Accounting records it.`

### 14.1 Authentication (AuthN) — "prove who you are" — Tier **B** edge + **F** credential check
*Establish identity and hand back short-lived, signed tokens.* Sub-workflows:
- **Email + password login** → `POST /auth/login` → 15-min access token + 7-day refresh token (FR-UM-003, NFR-SEC-002).
- **Phone + OTP quick-start** → anonymous visitor becomes `CITIZEN` instantly, no long form (FS §3.2).
- **Silent refresh** → `POST /auth/refresh` before the 15-min access token expires (handled at the Bun edge).
- **Logout** → `POST /auth/logout` → token invalidated immediately (204).
- **Forgot / reset** → `forgot-password` → emailed link (valid 1h) → `reset-password`; old sessions invalidated (FR-UM-004).
- **Email verification** → account inactive until verified (24h link) (FR-UM-002).
- **Brute-force lockout** → 5 failed attempts → 15-min lockout (FR-UM-003).
- *Render:* Bun mints/refreshes + rate-limits at the edge; FastAPI verifies the bcrypt(12) hash.

### 14.2 Authorization (AuthZ) — "what you're allowed to do" — Tier **F**
*Map identity → permissions, then enforce scope and gate actions.* Sub-workflows:
- **Role resolution** → the JWT's role(s) → permission set per **FS §3.3** (default `CITIZEN`, BR-ROLE-004).
- **Scope enforcement** → the ⚠️ cells become a server `WHERE`: Own / Area / Type / Org / Event / Jurisdiction (PostGIS for area/type). §2.2.
- **Action gating** → only permitted actions are *rendered* (approve = DM_AUTHORITY/ADMIN; accept = PROVIDER/MANAGER/ADMIN; create ≠ PROVIDER). Absent, not disabled.
- **Role elevation** → elevated roles can't be self-assigned; **ADMIN** grants via `POST /users/{id}/role` (BR-ROLE-002, audited); a vetted NGO may also hold `DM_AUTHORITY` (BR-ROLE-003).
- **Privacy-level authorization** → who may see PROTECTED/PRIVATE contact (responders via relay, authority full, public none).
- *Render:* FastAPI — gating + scope run where the data lives; the browser cannot widen them.

### 14.3 Accounting (the third A) — "record what happened" — Tier **F** (+ **WS**, + **B** cache)
*Account for every action, notify stakeholders, and aggregate metrics.* Sub-workflows:
- **Audit logging** → every sensitive action → immutable entry: timestamp (UTC), user, IP, action, resource, old → new (FR-SEC-002).
- **Notification trail** → in-app + email per status change; per-user feed (`SERVICE_*`, `VERIFICATION_REQUEST`, `GENERAL`, `SYSTEM`).
- **Metrics accounting** → response time, completion rate, provider performance → analytics dashboards (FR-REP-001).
- **Retention** → audit logs retained 7 years; notifications auto-delete after 30 days.
- **Financial ledger** → 🔒 Post-MVP (donations / allocations).
- *Render:* FastAPI writes the audit row; Bun WebSocket pushes notifications; Bun caches the public/aggregate analytics.

### 14.4 Security & Confidentiality — "keep secrets secret" — Tier **F** redaction + **B** edge
*Least-privilege data, server-side redaction, encryption everywhere.* Sub-workflows:
- **Privacy levels** → PUBLIC / PROTECTED (default) / PRIVATE; **raise-only** (BR-SR-003, FR-SEC-001).
- **PII redaction** → PROTECTED hides name/phone from public *and* responders (contact via system relay); **redaction is server-side** — hidden PII never reaches the browser.
- **Encryption** → TLS 1.3 in transit, bcrypt(12) passwords, AES-256 PII at rest, encrypted backups (FR-SEC-003, NFR-SEC-001/006).
- **Rate limiting / abuse** → 100 req/user/min at the Bun edge (NFR-SEC-004); disaster-surge mode.
- **Least-privilege delivery** → responses carry only the fields the caller's role + scope permit.
- *Render:* FastAPI redacts before serialising; Bun terminates TLS, applies rate-limit + security headers.

### 14.5 Integrity — "data is correct & untampered" — Tier **F** + DB constraints
*Validated input, lawful transitions, append-only history.* Sub-workflows:
- **Immutable audit log** → append-only; no edit/delete in the UI even for ADMIN.
- **Lifecycle integrity** → no skipping states (SUBMITTED→…→VERIFIED); emergencies auto-approve by system; DM Authority force-change is logged (FR-SR-006).
- **Input validation** → server-side: enums UPPERCASE, GeoJSON `[lng,lat]`, Indian phone, password complexity; invalid → rejected (DB CHECK constraints).
- **Single-writer rules** → exactly one requester (BR-SR-001), ≤ one provider (BR-SR-002), capacity gate (BR-PM-002).
- **Provenance** → every change records who + when + old → new.
- *Render:* FastAPI validates and enforces transitions; the database CHECK constraints are the last line.

### 14.6 Authenticity — "the actor & the data are genuine" — Tier **B** verify + **F** bind
*Signed tokens, non-repudiation, proof of genuineness.* Sub-workflows:
- **JWT signing + edge verification** → signed access tokens; Bun verifies signature + expiry on **every** request before proxying to FastAPI.
- **Non-repudiation** → each audited action is bound to the authenticated identity (can't be denied later).
- **Credibility review** → auto-approved emergencies are reviewed for genuineness by DM Authority; Auditor flags irregularities.
- **Proof of delivery** → provider uploads photos/receipts → requestor verifies completion + rating → authentic outcome (FR-SR-006).
- **Event provenance** → only DM Authority declares events; requests inside the geofence auto-link (FR-GEO-004).
- *Render:* Bun authenticates the token at the edge; FastAPI binds the action to the identity and records proof.

### 14.7 Create vs Update — what the start-of-showcase diagram depicts
- **CREATE** entities: account (`register`), **service request** (`POST /services` → `SUBMITTED`), disaster event (DM Authority), profile.
- **UPDATE** flows: the request lifecycle via action endpoints (`/approve /accept /complete /verify /cancel /reject`), profile (`POST /users/me`), role grant (`POST /users/{id}/role`), event status.
- Each create/update is **one guarded transaction**: `AuthN → AuthZ → (Confidentiality · Integrity · Authenticity) → Accounting`. The diagram shows the navigation map, the create→update lifecycle ribbon, and that guard band.

### 14.8 Checklist (R2)
- ✅ T10. Append flow CSS; add §14; build the bird's-eye diagram + 6 sub-workflow ribbons into `_showcase-intro.html` at the start; rebuild + verify.

---

## 15. Change Log (R1–R6) — consolidated history

> Round-by-round record of *what changed and why*. The header **Status** is the current state; this is the trail.
> All rounds dated 2026-06-10/11. Pipeline throughout: `_apply-icons.ps1` → `_apply-controls.ps1` → `_build-showcase.ps1`.

### R1 — Initial build
RBAC-organised mirror of `templates/`: 24 static templates (10 role dashboards, 4 service-detail lenses, 2 scoped
lists, 2 maps, 1 admin console, 5 shared) + the generated showcase. Documented FastAPI-vs-Bun render strategy (§6),
per-role nuance spec (§4), the §3.3 matrix. Validated: 24 frames, 0 mojibake, 0 attribute-leaked SVGs, UTF-8 no BOM.

### R2 — Post-registration AAA + security workflows
Added §14 (Authentication · Authorization · Accounting · Confidentiality · Integrity · Authenticity — each with
sub-workflows + endpoints + tier) and, at the **start of the showcase**, a bird's-eye **navigation map + create→update
lifecycle ribbon + security-gate band** (`#overview`) plus six sub-workflow ribbons (`#workflows`). New CSS atoms:
`.flow*`, `.sec-band/.sec-chip`, `.nav-map/.nav-col`, `.wf-card`, `.dim-*`.

### R3 — Lucide icons, no emoji
`_apply-icons.ps1` replaced every UI/nav/scope/workflow emoji with inline Lucide SVG (228 `.ic`; 0 astral emoji).
Kept only typographic glyphs (`●` `→` `★` `✓`). `<option>` priority dots → plain text (SVG can't live in `<option>`);
the password show/hide toggle swaps Lucide eye/eye-off in JS; copyCode labels de-emoji'd.

### R4 — Display controls on the showcase
A control bar in `idrm-rbac-showcase.html`: Heading + Body **font face** (Inter / DM Sans / Work Sans / Source Sans
Pro / Lato / Lexend / System Default), **size XS–XL** (default **M = 15px**), **theme Light/Dark/System** (cycle
button; System via `matchMedia` → `[data-theme]`), **Ctrl/⌘+K search**. New: `_showcase-controls.html`,
`assets/showcase-controls.css` (full dark remap of `--color-*`), `assets/showcase-controls.js`. Expanded the
Google-Fonts link; prefs persist to localStorage.

### R5 — Controls on every page
`_apply-controls.ps1` injected the same bar + the css/js links + fonts into all 24 `pages/*` (idempotent; bar wrapped
in `<!-- SC-CONTROLS-START/END -->` markers so the build strips it from the showcase frames → the showcase keeps one bar).

### R6 — Display fixes, confirm-password, footer
- **Mobile overflow fixed** (user-reported "display not apt"): the app `column` layout now `align-items: stretch` +
  `.app-main { width:100% }` (it was shrink-wrapping a long API URL); `code { overflow-wrap:anywhere }` wraps long
  endpoints; `.bottom-nav` items `flex:1 1 0` + `max-width:100vw`. Verified: provider page mobile = 0 overflow.
- **Control bar → `position: relative` (non-sticky)** + compacted on phones, so it no longer crowds the app navbar/
  sidebar (the page's own chrome stays the sticky layer). Removed the `--sc-bar-h` navbar/sidebar offsets.
- **Change password** rebuilt as a **double-entry** form: Current + New (strength meter) + **Confirm new password**,
  validated with `data-match` (live as you type + on submit) to catch typos; all three fields have show/hide toggles.
- **Footer reorganised** into 3 columns — brand + tagline, **Emergency helplines (108 / 112 / 1070, `tel:` links)**,
  quick links / reference — on `home.html` and the showcase.
