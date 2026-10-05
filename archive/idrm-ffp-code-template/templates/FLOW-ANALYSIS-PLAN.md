# FLOW-ANALYSIS-PLAN — IDRM Page Templates (Slate + Emerald)

**Created:** 2026-06-07
**Owner:** kalyan.narayana · **Author/agent:** Claude (Opus 4.8)
**Status:** ✅ DONE — R1 templates · R2 CSS validation + fluid type + live maps/charts · R3 beige API notes +
mellowed colors + Chennai→Hyderabad · R4 per-page role indicator (matrix-validated) · R5 encoding fix +
number badges + Lucide SVG icons + hamburger + privacy cards + refined heading scale ·
R6 header auth element (Sign in on public / account icon on auth) replacing the role-pill indicator ·
R7 bugfix: emoji-in-attribute had corrupted the search inputs — search icon moved to a left element; icon script now warns on attribute leaks ·
R8 [ROLE] badge beside the brand ([◆ IDRM] [ROLE]) ·
R9 bugfix: anchor-buttons inherited the global `a:hover` colour → primary button text went emerald-800 on an emerald-800 hover bg (invisible); fixed with per-variant hover/focus colour rules ·
R10 primary-button hover was too subtle (emerald-700→800); deepened to emerald-900 + `shadow-lg` for a clearly visible hover. 2026-06-07.
**Direction chosen by user (2026-06-07): Option A — keep as a static demo.** No backend/mock work for now;
the §12 roadmap (Options B/C/D) stays on file for whenever they decide to go further.

> **📌 CANONICAL SPEC FOR FUTURE EDITS → see §13 (Consolidated Requirements & Specifications).** It lists every
> rule + exact value (colors, fonts, icons, roles, build steps) in novice-friendly language so revisions stay exact.
> The §11 "Round" log is the *history of changes*; §13 is the *current contract* you must keep.
**Location of this file:** `templates/FLOW-ANALYSIS-PLAN.md` (project root: `idrm-mvp/`)

> **Purpose of this file (read me first).** This is the single source of truth for the
> "page templates" deliverable. It records *what we are building*, *why*, *every decision
> taken*, *the full file list*, and a *task checklist updated after each step*. If work is
> interrupted, **a fresh reader (human or Claude) can resume from here alone** — no other
> conversation context required. Update the **Task Checklist** section after completing each task.

---

## 1. The original request (verbatim intent)

The user attached a design-system reference file
(`visual_hierarchy_slate_emerald_mode_light-v3-system_merged_v5.html`) and asked for a complete
set of IDRM page templates built in that visual language. The 10 explicit points:

1. Build different pages (sample templates), each separated by a horizontal line
   `<hr color="skyblue">`, concatenated into a **single standalone, self-contained** document.
2. Line height = **1.75 × font size**.
3. Design inspiration / theme = the attached artifact. **Every page must be responsive.**
4. Requirements come from the `instructions/` folder of the `idrm-mvp` project.
5. Also document, **step-wise**, in a section with a **slightly different (beige) background**, the
   pages and the end-user / user **workflows**, based on different **use-case scenarios**.
6. **Plan → reason → review → validate completeness**, then create the standalone HTML file **and**
   the broken-out html / css / js artifacts in a **`templates/` folder in the project root**.
7. Put the **plan** (summary / outline / pages / workflows) **inside** the standalone artifact, with
   all pages concatenated — a single reference artifact for the future.
8. Ask for clarifications if needed, with novice-friendly recommendations, before proceeding.
9. Detail progress/plan/tasks **first** in this `FLOW-ANALYSIS-PLAN.md`, **update it after each task**,
   and keep enough context here to resume later.
10. Keep a **copy of the attached artifact** in `templates/` under an apt name.

---

## 2. Clarifications resolved (2026-06-07)

Asked 3 questions; user accepted all recommendations:

| # | Decision | Chosen |
|---|----------|--------|
| 1 | **Page scope** | **Full citizen web + provider/admin** (~15 templates) = the MVP primary web surface. |
| 2 | **Styling** | **Self-contained CSS design tokens** (extend the attached file). Zero external deps; opens offline; fast on 2G (IDRM emergency principle). Tailwind equivalents noted in comments. |
| 3 | **Behavior** | **Visual mockups + documented API hooks** — realistic sample data + endpoint/JSON in comments + light vanilla JS. No live backend (Ubuntu backend can't run from Windows). |

---

## 3. Project context (so this file stands alone)

- **IDRM** = Integrated Disaster Response Management — government-backed, map-driven platform
  connecting citizens in crisis with NGOs/hospitals/volunteers ("Uber for Disaster Relief").
- **MVP web surface** = the HTML/Tailwind citizen platform (port 5173) + provider pages; a thin
  admin dashboard (full admin is the React SPA on 5174, secondary). Mobile (Expo) is Post-MVP.
- **Authoring box is Windows (this machine) — build/run happens on an Ubuntu laptop.** So these
  templates are static/self-contained and do NOT require any backend to view.

### Source-of-truth docs used
- `instructions/instructions_pages_v3.md` — page-by-page inventory (citizen/provider/admin/mobile).
- `instructions/instructions_ui_v3.md` — **canonical** Slate+Emerald tokens, component recipes, a11y.
- `instructions/instructions_web_v3.md` — API client, Leaflet, WebSocket, validation, toasts.
- `instructions/instructions_json_formats_v3.md` — request/response JSON shapes.
- `docs/development/IDRM-FS.md` — §3.1 role hierarchy, **§3.3 Permission Matrix (source of truth)**,
  §6 business workflows (service-request lifecycle, provider onboarding, disaster-event lifecycle),
  §5 user stories.
- `CLAUDE.md` — API reference + key constraints/enums.

### Reconciliation decisions (where docs disagree, this wins)
- **Enums are UPPERCASE**, exact spelling (DB CHECK constraints). e.g. `MEDICAL`, not `medical`.
- **Canonical roles** (FS §3.3 / CLAUDE.md): `CITIZEN, VOLUNTEER, ORGANIZER, PROVIDER, MANAGER,
  EVENT_MANAGER, EXECUTIVE (🔒 Post-MVP), DM_AUTHORITY, AUDITOR, ADMIN` + a Public tier.
  ⚠️ Ignore stale names in older guides (`SERVICE_PROVIDER`, `ORG_ADMIN`, `SYSTEM_ADMIN`).
- **HTTP = GET/POST only** (CLAUDE.md). Status changes via action sub-endpoints:
  `/approve, /accept, /complete, /verify, /cancel, /reject`. ⚠️ Ignore `PUT/PATCH` in older guides.
- **Statuses (lifecycle):** SUBMITTED → APPROVED → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED;
  terminal: REJECTED, CANCELLED, EXPIRED; plus DISPUTED. Emergency/urgent = auto-approved.
- **Service types:** RESCUE, MEDICAL, FOOD, SHELTER, WATER, OTHER.
- **Priority:** CRITICAL, HIGH, MEDIUM, LOW.
- **Privacy:** PUBLIC, PROTECTED (default), PRIVATE (can only be raised).
- **Finance/Donations, AI Chatbot, native mobile = Post-MVP** (shown as 🔒 where referenced).

---

## 4. Design system rules applied

- **Palette:** Slate (neutrals) + Emerald (primary), Light Mode, WCAG AA/AAA targets.
- **Font:** Inter (Google Fonts), `font-sans antialiased`, page bg `#f8fafc` (slate-50).
- **Line-height = 1.75** on `body` (request #2) — relaxed reading rhythm.
- **Tokens:** reuse the attached file's CSS custom properties (`--color-*`, `--space-*`, `--radius-*`,
  `--shadow-*`), extended with IDRM semantic tokens (status/priority/service-type/privacy).
- **Responsive:** mobile-first; verified breakpoints 360 / 768 / 1280; tap targets ≥ 44px;
  no hover-only affordances; sidebars collapse `flex-col → md:flex-row`; tables scroll / stack.
- **A11y:** semantic HTML, one `h1`/page, focus-visible rings, `role="alert"`, `aria-current`,
  color never the only signal (status/priority always have text + icon), labels on every field.
- **Separator between pages:** `<hr color="skyblue">` (request #1).

---

## 5. Deliverable file tree (under `templates/`)

```
templates/
├── FLOW-ANALYSIS-PLAN.md                 # THIS FILE — plan + checklist (update after each task)
├── idrm-templates-showcase.html          # ⭐ standalone, self-contained: plan + workflows + all 15 pages
├── visual_hierarchy_slate_emerald_REFERENCE.html   # copy of the attached design-system artifact (#10)
├── assets/
│   ├── idrm-design-system.css            # shared tokens + components (linked by pages/*.html)
│   └── idrm-templates.js                 # shared interactions (nav, tabs, toast, validation, rating…)
└── pages/                                # individual page artifacts (each links ../assets/*)
    ├── 01-home.html                      # Public landing
    ├── 02-register.html                  # Create account
    ├── 03-login.html                     # Sign in
    ├── 04-forgot-password.html           # Reset password
    ├── 05-dashboard.html                 # Citizen dashboard
    ├── 06-create-service.html            # Request help (form + map pin)
    ├── 07-service-detail.html            # Track a request (timeline, provider, rating)
    ├── 08-my-services.html               # All my requests (filters, table/cards)
    ├── 09-map.html                       # Live map (markers, clusters, filters)
    ├── 10-notifications.html             # Alerts & updates
    ├── 11-profile.html                   # Settings (profile + password + language)
    ├── 12-provider-dashboard.html        # Provider control panel
    ├── 13-available-services.html        # Open requests to accept
    ├── 14-active-services.html           # Assigned/active work
    └── 15-admin-dashboard.html           # Admin overview (stats, approvals, audit)
```

**Self-contained vs linked:** `idrm-templates-showcase.html` inlines all CSS/JS (true standalone).
`pages/*.html` are full HTML docs that **link** `../assets/idrm-design-system.css` +
`../assets/idrm-templates.js` (separation of concerns / DRY for the dev team). Page *markup* is shared.

---

## 6. Page inventory — what each shows + API hooks (mockup data; calls documented in comments)

| # | Page | Who | Key content | Documented API hooks |
|---|------|-----|-------------|----------------------|
| 01 | Home | Public | Hero, "Request Help"/"Register as Provider" CTAs, hotlines, how-it-works, live stats | none (redirect to dashboard if token) |
| 02 | Register | Public | email/password/full_name/phone/role(CITIZEN default), strength meter | `POST /auth/register` |
| 03 | Login | Public | email/password, generic error, auto-refresh note | `POST /auth/login`, `POST /auth/refresh` |
| 04 | Forgot password | Public | request link → set new password (token in URL) | `POST /auth/forgot-password`, `/reset-password` |
| 05 | Dashboard | Auth (role-aware) | welcome, active-count, quick actions, recent notifications, mini-map | `GET /users/me`, `/services`, `/notifications`, `/analytics/dashboard` |
| 06 | Create service | Citizen/Volunteer | service_type, priority, description, map pin + "use my location", privacy, people, phone | `GET /users/me`, `POST /services` |
| 07 | Service detail | Requestor/Provider/Auth | status badge, timeline, provider card+ETA, role actions, rating form | `GET /services/{id}`, action endpoints, WS `service_requests` |
| 08 | My services | Auth | filters (status/type/date), paginated list (table desktop / cards mobile) | `GET /services` |
| 09 | Map | Auth | live Leaflet map, priority markers, filter chips, detail drawer (see §13 R11) | `GET /geo/nearby`, `/geo/cluster`, WS |
| 10 | Notifications | Auth | list newest-first, unread highlight, mark read / mark all | `GET /notifications`, `/notifications/{id}/read` |
| 11 | Profile | Auth | edit full_name/phone/language; password change; read-only email/role | `GET/POST /users/me`, `POST /auth/change-password` |
| 12 | Provider dashboard | PROVIDER | assigned/available counts, capacity, active list, performance | `GET /users/me`, `/services?provider=me` |
| 13 | Available services | PROVIDER | open APPROVED requests near me, accept action, type filter | `GET /geo/nearby`, `POST /services/{id}/accept` |
| 14 | Active services | PROVIDER | ACCEPTED/IN_PROGRESS assignments, mark in-progress/complete | `GET /services?status=…&provider=me`, action endpoints |
| 15 | Admin dashboard | DM_AUTHORITY/ADMIN | KPI stats, approval queue (approve/reject), by-type/status, audit snippet, users | `GET /analytics/dashboard`, approve/reject, `/admin/*` |

---

## 7. Workflow / use-case scenarios to document (beige "Plan & Workflows" section, #5)

Step-wise, novice-friendly, mapped to the FS §6 workflows and the pages above:

1. **Citizen requests help (the core loop)** — Home → Register/Login → Dashboard → Create Service
   (pin location) → Service Detail (track) → Confirm completion + rate.
   *Lifecycle:* SUBMITTED → (auto-APPROVED if emergency) → ACCEPTED → IN_PROGRESS → COMPLETED → VERIFIED.
2. **Citizen tracks & manages** — My Services (filter) → Service Detail → Cancel (if SUBMITTED/APPROVED).
3. **Provider delivers relief** — Provider Dashboard → Available Services (accept) → Active Services
   (mark in-progress → complete) → requestor verifies.
4. **DM Authority approves & coordinates** — Admin Dashboard approval queue → approve/reject;
   handle DISPUTED (reassign → IN_PROGRESS, or → REJECTED).
5. **Admin oversees** — Admin Dashboard KPIs, users, audit snapshot.
6. **Public (not logged in)** — Home + public map (view-only); prompted to register to act.

Each scenario lists: actor (role), goal, numbered steps, the pages touched, and the resulting status.

---

## 8. Task Checklist (UPDATE AFTER EACH TASK)

Legend: ⬜ todo · 🟡 in progress · ✅ done

- ✅ T0. Explore project; read instruction files + FS; confirm empty layout placeholders.
- ✅ T1. Ask clarifications (scope / styling / behavior). All recommendations accepted.
- ✅ T2. Create `templates/` + write this `FLOW-ANALYSIS-PLAN.md` (initial).
- ✅ T3. Copy attached artifact → `templates/visual_hierarchy_slate_emerald_REFERENCE.html` (#10).
- ✅ T4. Build `templates/assets/idrm-design-system.css` (tokens + components + IDRM semantics + 1.75 lh).
- ✅ T5. Build `templates/assets/idrm-templates.js` (nav/tabs/toast/validation/rating/map-stub/TOC).
- ✅ T6. Build `pages/01..04` (home, register, login, forgot-password).
- ✅ T7. Build `pages/05..08` (dashboard, create-service, service-detail, my-services).
- ✅ T8. Build `pages/09..11` (map, notifications, profile).
- ✅ T9. Build `pages/12..15` (provider dashboard, available, active, admin dashboard).
- ✅ T10. Build `idrm-templates-showcase.html` — inline CSS/JS + beige plan/workflows + all 15 pages
        concatenated with `<hr color="skyblue">` (#1, #5, #7). Assembled via `_build-showcase.ps1`.
- ✅ T11. Validated in a local Node preview (see §11): 15 frames + 15 TOC anchors; body line-height
        measured **28px/16px = 1.75×**; in-frame navbars neutralized to `static` (no overlap);
        desktop + mobile (375px) render correctly (burger nav, bottom tab-bar, stacked layout);
        nav toggle works; **no console errors**.

### Helper files (kept for re-generation / preview / resuming)
- `_showcase-intro.html` — the header + TOC + beige plan/workflows band injected at the top of the showcase.
- `_build-showcase.ps1` — re-assembles `idrm-templates-showcase.html` from the parts. Run:
  `powershell -ExecutionPolicy Bypass -File templates/_build-showcase.ps1`
- `_apply-icons.ps1` — replaces UI/nav emoji with inline Lucide SVGs + circled numbers with `.num-badge`
  across `pages/*.html` + `_showcase-intro.html`. Pure-ASCII (matches emoji by code point). Re-run any time
  (idempotent), then re-run `_build-showcase.ps1`. Run:
  `powershell -ExecutionPolicy Bypass -File templates/_apply-icons.ps1`
- `_apply-brand-role.ps1` — wraps each page's header brand as `[◆ IDRM] [ROLE]` (role badge beside the logo).
  Idempotent (skips pages already wrapped); touches only the header brand. One-time applier; re-running is a no-op.
- `_preview-server.js` + `.claude/launch.json` (`idrm-templates`) — tiny Node static server on port 4599
  to preview locally (`node templates/_preview-server.js` → http://localhost:4599).

---

## 9. How to resume (if interrupted)

1. Read §3 (context), §4 (design rules), §5 (file tree), §6 (page specs), §7 (workflows).
2. Check §8 checklist for the first non-✅ item; continue there.
3. Shared CSS/JS live in `templates/assets/`. Page markup is mirrored between `pages/*.html`
   (linked) and `idrm-templates-showcase.html` (inlined) — keep them consistent.
4. Honor the reconciliation decisions in §3 (UPPERCASE enums, canonical roles, GET/POST + action
   endpoints). When in doubt, FS §3.3 + CLAUDE.md win over the older instruction guides.
5. Update §8 after each task; flip the header **Status** to ✅ DONE when T11 passes.

---

## 10. Validation checklist (run at T11) — ✅ all passed

- [x] Body `line-height: 1.75` — measured 28px/16px = 1.75× in the preview.
- [x] Pages separated by `<hr color="skyblue">` in the showcase (15 separators; renders as a sky line).
- [x] Beige section present with plan + step-wise workflows + 6 use-case scenarios.
- [x] Showcase is truly standalone (CSS/JS inlined; only Inter font is external, with system fallback).
- [x] Responsive at 360 / 768 / 1280 (mobile-first; nav collapses to burger; bottom tab-bar; tables scroll).
- [x] Status/priority/service-type/privacy use canonical UPPERCASE + correct colors + text/icon.
- [x] Roles canonical (no SERVICE_PROVIDER/ORG_ADMIN/SYSTEM_ADMIN).
- [x] API hooks documented in `.api-note` blocks + comments; methods are GET/POST with action endpoints.
- [x] Focus rings present; alerts have roles; labels wired; one h1 per page.
- [x] Copy of original artifact present in `templates/` (`visual_hierarchy_slate_emerald_REFERENCE.html`).
- [x] No browser console errors; in-frame sticky/fixed chrome neutralized so frames don't overlap.

---

## 11. Round 2 (2026-06-07) — CSS validation, responsive type, live maps + charts

**A. CSS validated against the original** `visual_hierarchy_slate_emerald_*` artifact. Faithful on all
tokens/components; 3 deviations corrected, 2 kept on purpose:
- ✅ Restored the **`h2` underline** (`border-bottom: 2px` + `padding-bottom`) — it was dropped.
- ✅ Re-aligned **radii to the source**: buttons/inputs → `0.5rem`, cards/modal → `1rem` (were rounder).
- ✅ Kept (intentional, accessibility): muted text `slate-600` (AAA), primary button `emerald-700` (AA on small text).

**B. Cleaner, responsive typography (the "font-size vs display size" ask):**
- Headings are now **fluid via `clamp()`** — H1 30→40px, H2 24→30px, H3 20→24px, H4 18→20px across phone→desktop.
- Body prose nudges 16→17px on large screens; **body line-height stays 1.75×**; table line-height tightened to 1.5.

**C. External functionality made real (per your choices):**
- 🗺️ **Live maps** — Leaflet 1.9.4 + OpenStreetMap tiles on pages 05/06/07/09 and in the showcase.
  Priority-colored markers, popups, zoom. Loads from CDN; **graceful fallback** to the styled placeholder
  if offline. Lazy-initialized on scroll (IntersectionObserver). GeoJSON `[lng,lat]` → Leaflet `[lat,lng]`.
- 📊 **Real charts** — Chart.js doughnut (by service type) + bar (by status) on the admin dashboard, with
  the CSS-bar version kept as a graceful fallback.
- GPS "use my location" already worked (browser Geolocation). Skipped (not requested now): Nominatim
  reverse-geocoding, marker-clustering plugin. WebSocket + REST stay as documented stubs (need the backend).
- New external dependencies (only where used): `unpkg.com/leaflet`, `cdn.jsdelivr.net/chart.js`. The showcase
  is therefore "self-contained for layout/behavior" but uses these CDNs (and map tiles) for the live map/charts;
  everything degrades gracefully without a network.

**Verified in a local Node preview:** maps render real tiles+markers; both charts draw; H1=40px at desktop;
body line-height=28px (1.75×); `h2` underline present; **no console errors**.

### Round 3 (2026-06-07) — metadata styling, mellow colors, content review
- 🟫 **`.api-note` → beige** (`#faf6ed`, beige dashed border) + an uppercase label "ⓘ Developer reference —
  metadata, not part of the page", so the developer "API ·" footers read clearly as meta, matching the
  showcase's beige plan band. Text = slate-600 on beige (AAA contrast).
- 🎨 **Mellowed service-type palette** (muted-professional, user-chosen): RESCUE `#c2554f`, MEDICAL `#c16b83`,
  FOOD `#b07f30`, WATER `#4f86b3`, SHELTER `#8174ad`, OTHER `#6b7280`. Updated the CSS tokens, the doughnut
  chart's literal colors, and added white separators (`borderWidth:2`) to the doughnut. Dots stay paired with
  text → color is never the only signal (WCAG 1.4.1).
- 🗺️ **Content fix — relocated the flagship sample** from "Anna Nagar, Chennai" to "Kukatpally, Hyderabad"
  (coords 13.08,80.27 → 17.49,78.40) across pages 05/07/08/09/12/13/14, matching the stated Hyderabad +
  Vijayawada pilot and fixing the dashboard map-vs-text mismatch.
- 🔎 **Content review:** no placeholder names / encoding artifacts / lorem / TODO found; enums, roles and
  endpoints already canonical. Note (no change): icons are emoji (fine for templates; a production build would
  swap to SVG). Verified all changes in the preview — **no console errors**.

### Round 4 (2026-06-07) — per-page login-role indicator (matrix-validated)
- 🔑 Added a **role indicator in every page header (top-right)** — an "ACCESS" label + role pill(s) with the
  **default/expected role first** (emerald), additional roles as secondary (grey) pills. On mobile only the
  default pill shows (label + extras hidden) to keep the header compact (single row); `.navbar-inner` got
  `flex-wrap` as a safety net.
- 🟫 Mirrored the **full access list (default first) in the beige API note** on every page (`<strong>Access ·</strong> …`),
  so the metadata section documents who can reach the page — exactly per the **Permission Matrix (FS §3.3)**.
- 🧹 Removed the old brand-adjacent "Provider"/"Authority" badges on pages 12–15 (role now lives consistently
  in the top-right indicator). Unified the brand to "◆ IDRM" everywhere.
- **Matrix-validated access mapping** (default first):
  - 01–04 home/register/login/forgot → **Public** (no login).
  - 05 dashboard, 08 my-requests, 10 alerts, 11 profile → **CITIZEN** + all signed-in (role-aware).
  - 06 create → **CITIZEN**, VOLUNTEER, ORGANIZER (+ DM_AUTHORITY, ADMIN per matrix; PROVIDER/MANAGER/EVENT_MANAGER/AUDITOR cannot).
  - 07 detail → **CITIZEN** (requestor), PROVIDER/MANAGER, DM_AUTHORITY, AUDITOR (read-only), ADMIN.
  - 09 map → **CITIZEN** + Public (view-only public map).
  - 12–14 provider → **PROVIDER** + MANAGER (ADMIN all).
  - 15 admin → **DM_AUTHORITY** + ADMIN (+ EVENT_MANAGER events, AUDITOR read-only).
- **Verified** in preview: 15 role indicators + 15 beige "Access ·" notes; desktop shows full list, mobile shows
  only the default pill (single-row 60px header); 0 brand badges remain; **no console errors**.

### Round 5 (2026-06-07) — encoding fix, number badges, Lucide SVG icons, hamburger, privacy cards, heading scale
- 🔤 **Fixed footer text mojibake** ("IDRM â€" Page Templates…"). Root cause: Windows PowerShell 5.1 executes
  `_build-showcase.ps1` reading it as ANSI, so literal non-ASCII in the script's here-strings (— · × ©) corrupt.
  Fix: those became HTML entities (`&mdash; &middot; &times; &copy;`) in the script. (See R2 for the rule.)
- 🔢 **Number display** — replaced circled-digit unicode (①–⑥, which fall back to a mismatched system font) with
  on-brand `.num-badge` (small emerald circle + digit) in the showcase Contents list and section headings.
- 🎨 **Icons → inline Lucide SVG** (user chose **Lucide** + **"UI & navigation icons"** scope). Brand mark,
  hamburger, sidebar + bottom-nav, key action buttons, privacy lock, KPI/stat icons and avatars now render as
  `<svg class="ic">` (Lucide, ISC-licensed, currentColor). **Kept as emoji** (deliberate): status/alert glyphs
  (✓ ✗ ⚠ ℹ 💡), wave/celebration, empty-state, password show/hide, priority dots, and the service-type emoji
  inside `<select><option>` (HTML cannot embed SVG in an option). Applied by `_apply-icons.ps1`.
- ☰ **Hamburger de-cluttered** — the congested ☰ glyph is now a clean Lucide "menu" SVG; `.nav-toggle` recentred.
- 🔒 **"Contact & privacy" (page 06)** — the cramped inline radios are now `.privacy-option` cards
  (radio + badge + description, with a selected-state highlight); PROTECTED is marked **Default**.
- 🔠 **Refined heading scale** (calmer maxes for a cleaner hierarchy): H1 28→36, H2 22→26, H3 19→22, H4 17→19px.
- New helper `_apply-icons.ps1`. **Verified** in preview: footer encoding clean (no `â€`/`Â`), **122** inline
  SVG icons render, 12 number badges, 15 role tags, status emoji preserved, **no console errors**.

### Round 6 (2026-06-07) — header auth element (Sign in / account icon); role-pill indicator removed
- **User clarified** the top-right nav element should be the **standard auth state**, not a role or privacy display:
  **public pages → a "Sign in" button**; **login-required pages → a user/account icon button** (→ profile).
  And **PUBLIC/PROTECTED/PRIVATE are data attributes → NOT shown in the nav** (they remain on request cards /
  the create-service form). This supersedes the Round-4 `ACCESS · role` pill.
- Removed the `.role-tag` / `.role-pill` indicator + its CSS from all 15 pages. Public 02/03/04 → single "Sign in"
  (login page → "Create account"); home → "Sign in" + "Get started" (moved out of the menu into the header).
  Auth pages → account icon (Lucide `user`) linking to profile; existing actions (+ Request, back links, Sign out)
  kept; provider/admin org avatars (building/landmark) unified to the same account icon.
- **Access roles are still documented in the beige *developer* note** (kept on purpose — metadata, not UI; see R8/R9).
- **Verified** in preview: home = "Sign in" + "Get started"; dashboard = "+ Request help" + account icon;
  **0 role pills** remain; **no console errors**.

### Round 7 (2026-06-07) — bugfix: emoji-in-attribute corrupted the search inputs
- **Symptom (user-reported):** stray text such as `<svg class= Search description or address…">` on pages 08 &
  15 (and the showcase) — the search box markup was broken.
- **Cause:** `_apply-icons.ps1` (Round 5) replaced the 🔍 emoji that was sitting **inside an HTML attribute**
  (`placeholder="🔍 Search…"`). An inline `<svg>` contains `"` and `<`, which prematurely close/break the
  attribute value. This is the general hazard of "replace emoji blindly."
- **Fix:** the search icon is now a real element — `<span class="input-icon-left"><svg…/></span>` inside
  `<div class="input-group has-icon-left">` — with a **plain** `placeholder` and a small CSS rule
  (`.input-group .input-icon-left` + `.input-group.has-icon-left input{padding-left:2.25rem}`). No emoji remains
  in any attribute.
- **Hardened `_apply-icons.ps1`:** after replacing, it scans each file for `="[^"]*<svg` and **prints a warning**
  if an icon ever leaks into an attribute again. Codified the rule in **R6** and added a grep check to **R14**.
- **Verified:** `grep '="[^"]*<svg'` = **0** across all HTML (incl. rebuilt showcase); both search boxes show a
  left icon + clean placeholder; no stray `<svg>` / `class=` text on the page; **no console errors**.

### Round 8 (2026-06-07) — [ROLE] badge beside the brand
- **Request:** show the page's role right beside the logo — `[◆ IDRM] [ROLE]` — in addition to the right-side auth
  element (Round 6). The badge = the page's **default/expected role**.
- Added `.brand-group` (wraps the brand link) + `.brand-role` badge in the CSS. Per page: **01–04 Public** (muted
  `.brand-role.public`); **05–11 CITIZEN**; **12–14 PROVIDER**; **15 DM_AUTHORITY**. Applied by the idempotent
  `_apply-brand-role.ps1` (wraps only the header brand; the home footer brand is left alone).
- The right-side auth element (Sign in / account icon) and the beige access note (dev) are unchanged. Now the header
  consistently reads **`[◆ IDRM] [ROLE] … [auth element]`**.
- **Verified:** 15 brand-role badges in the showcase (distinct: Public / CITIZEN / PROVIDER / DM_AUTHORITY); home =
  `[◆ IDRM][PUBLIC]` + Sign in/Get started; admin = `[◆ IDRM][DM_AUTHORITY]` + account icon; **no console errors**.

### Round 9 (2026-06-07) — bugfix: button text invisible on hover (global `a:hover` colour leak)
- **Symptom (user-reported):** some buttons' text disappeared on hover — "font colour and background colour become
  one and the same."
- **Root cause:** the global `a:hover { color: var(--color-primary-strong) /* emerald-800 #065f46 */;
  text-decoration: underline }` (specificity **0,1,1**, inherited from the original design system) overrode a
  button variant's *base* text colour (**0,1,0**) on hover. An `<a class="btn btn-primary">` **without** an inline
  `color` therefore got **emerald-800 text**, while `.btn-primary:hover` background is **also emerald-800** →
  identical → invisible. `<button>` elements (no `a:hover`) and links with inline `style="color:#fff"` were
  unaffected — which is why only *some* buttons broke. It's a pre-existing architecture issue that surfaced as more
  anchor-buttons (Sign in, + New request, account, etc.) were added across rounds.
- **Fix (one CSS block, no page edits):** per-variant hover/focus colour rules at specificity **0,2,0** so each
  button keeps its own text colour — `.btn-primary/.btn-secondary/.btn-danger → white`, `.btn-outline → emerald-700`,
  `.btn-ghost → slate-900` — plus `.btn:hover{text-decoration:none}` so button links don't underline.
- **Verified (deterministic cascade check):** for `a.btn.btn-primary` the winning hover colour rule is
  `.btn-primary:hover → --color-text-on-primary` (white, specificity 20) beating `a:hover → emerald-800` (11);
  rest colour = white, distinct from the emerald hover background; **no console errors**.
- The inline `style="color:#fff"` on the header CTA links is now redundant (kept — harmless; could be cleaned up).

### Round 10 (2026-06-07) — primary button hover was barely visible
- **Symptom (user-reported):** primary buttons "don't show a hover effect."
- **Cause:** `.btn-primary` rest background is **emerald-700** (`--color-primary-hover` #047857 — chosen in Round 1
  so the white label clears WCAG AA), and the hover only stepped to **emerald-800** (`--color-primary-strong`
  #065f46). Two adjacent dark greens = a barely-perceptible darken; and with OS *reduced-motion* the `-1px` lift is
  suppressed too, so the hover looked like almost nothing. (Not a regression — Round 9 only touched the text colour;
  the AA-driven dark rest from Round 1 had compressed the hover range all along.)
- **Fix:** added token `--color-primary-darker: #064e3b` (emerald-900); `.btn-primary:hover` now darkens
  **700 → 900** (green channel 120 → 78, a clear step) with `--shadow-lg`. White label kept (AAA on emerald-900);
  rest stays emerald-700 (AA preserved). One CSS change → fixes every primary button on every page.
- **Verified (CSSOM):** rest bg `rgb(4,120,87)` (emerald-700) vs hover bg `rgb(6,78,59)` (emerald-900) — clearly
  distinct — with `shadow-lg`; **no console errors**.

---

## 12. TODO — Roadmap from "templates" to a full-stack IDRM app

> **Read this first (plain English).** Right now we have the **front of the shop** — every screen, beautifully
> styled, with *pretend* data and *live* maps/charts. To make it a **real application** we still need the
> **back of the shop**: a *server* that stores data and enforces rules, a *database* to keep that data, and the
> *plumbing* that connects screens to the server. This section lists that pending work as tasks, then offers
> **paths** (how far to go), **autonomy levels** (how self-running it is), and rough **cost/effort + risk-reward**
> so you can pick. Estimates assume **one developer** (AI-assisted can compress them); they are indicative, not quotes.
> **Effort key:** S ≈ 1–2 days · M ≈ 3–5 days · L ≈ 1–2 weeks · XL ≈ 3+ weeks.

### 12.0 Jargon, in one line each
- **Frontend** = the screens in the browser (what we built). **Backend** = the server program that holds the
  logic. **Database** = where data is permanently stored. **API** = the messenger format the frontend uses to
  ask the backend for things. **Gateway** = a guard in front of the backend (checks identity, limits abuse).
- **Mock backend** = a fake server that returns canned data, so the frontend "works" without the real thing.
- **JWT** = a signed digital wristband proving who you are. **RBAC** = "role-based access control" = who is
  allowed to do what. **WebSocket** = a always-open phone line for live updates. **CI/CD** = robots that test
  and deploy your code automatically. **Container (Docker)** = a sealed box that runs the app the same everywhere.

### 12.1 Current state vs. the goal
- **Have:** 15 responsive page templates + standalone showcase; design system; live maps & charts; documented
  API contracts; FS/role matrix. **No** real data persistence, **no** auth, **no** server logic yet.
- **Goal ("as far as feasible"):** a working IDRM that a real citizen/provider/authority can use end-to-end,
  runnable on the **Ubuntu** target (this Windows box is authoring-only).

### 12.2 Pending work as phased TODO tasks
> Each is a checkbox so progress can be tracked here. Do them roughly top-to-bottom.

**Phase P1 — Make the frontend "real-data-ready" (Frontend)** · effort **M**
- [ ] P1.1 Extract shared partials (navbar/sidebar/footer/bottom-nav) so they aren't copy-pasted per page.
- [ ] P1.2 Add a tiny API client layer (`fetch`/Axios) with the endpoints already documented in each page's
      `.api-note` — but pointed at a **mock** first (P2). *Why: screens stop using hard-coded data.*
- [ ] P1.3 Wire auth guard + token storage + 15-min refresh loop (already specced in `instructions_web_v3.md`).
- [ ] P1.4 Replace mock toasts/handlers with real submit→response flows; loading/empty/error states everywhere.

**Phase P2 — Self-contained mock backend (so it "works" with no real stack)** · effort **S–M**
- [ ] P2.1 Stand up a mock API (e.g. **Mock Service Worker** in-browser, or `json-server`/a tiny Bun server)
      returning the documented JSON. *Why: full clickable demo, still laptop-only, no DB.*
- [ ] P2.2 Seed realistic sample data (the records already shown in the templates).
- [ ] P2.3 Fake auth (accept any login, issue a dummy token) so role-based views can be demoed.

**Phase P3 — Real database (Data)** · effort **M** · *Ubuntu only*
- [ ] P3.1 PostgreSQL 16 + **PostGIS** (for map/geo queries) + Redis 7 (cache/sessions/pub-sub).
- [ ] P3.2 Schema + migrations + seed (the repo already has `database/init/*.sql` to build on).
- [ ] P3.3 Confirm geo queries (`/geo/nearby`, `/geo/cluster`) with PostGIS.

**Phase P4 — Real backend (FastAPI modular monolith, port 8000)** · effort **L–XL** · *Ubuntu only*
- [ ] P4.1 Auth module: register/login/refresh/logout, password reset, hashing, JWT.
- [ ] P4.2 Services module: full request lifecycle + action endpoints (`/approve,/accept,/complete,/verify,/cancel,/reject`).
- [ ] P4.3 Geo, Notifications, Analytics modules.
- [ ] P4.4 **RBAC** enforced server-side per **FS §3.3** + privacy levels (PUBLIC/PROTECTED/PRIVATE).
- [ ] P4.5 Input validation, error format, pagination — match the documented contracts.

**Phase P5 — API Gateway (Bun, port 3000) + real-time** · effort **M**
- [ ] P5.1 Routing/proxy to FastAPI, JWT check, CORS, rate limiting, security headers.
- [ ] P5.2 **WebSocket** (port 3001) ↔ Redis pub/sub for `request_created/updated/deleted` live updates.

**Phase P6 — Wire frontend → real gateway** · effort **S–M**
- [ ] P6.1 Point the API client at the gateway; remove the mock. Verify all 6 workflows (see §7) end-to-end.

**Phase P7 — Quality & access** · effort **M–L**
- [ ] P7.1 Tests: unit + integration + a few end-to-end (the repo has CI workflow stubs).
- [ ] P7.2 Accessibility audit (axe), keyboard pass, contrast check on any custom pairings.
- [ ] P7.3 i18n for **en/hi/te** (Telugu pilot region).

**Phase P8 — Run & ship (DevOps)** · effort **M–L** · *Ubuntu only*
- [ ] P8.1 Dockerize everything; `docker compose` for one-command local bring-up (repo has `infra/docker/`).
- [ ] P8.2 Env config for dev/staging/prod (see `docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`).
- [ ] P8.3 CI/CD (GitHub Actions stubs exist) → automated test + deploy.
- [ ] P8.4 NGINX + TLS, backups, monitoring/logging, basic hardening.

**Phase P9 — Post-MVP / "autonomous" extras** · effort **L+**
- [ ] P9.1 Native mobile (Expo), Finance/Donations, AI chatbot (all Post-MVP per `CLAUDE.md`).
- [ ] P9.2 Optional **agentic ops** (auto-triage requests, auto-scale, self-healing) — see autonomy L4 below.

### 12.3 Feasibility options (pick the destination)
| Option | What you get | Runs where | Autonomy | Effort | Infra $/mo | Risk → Reward |
|---|---|---|---|---|---|---|
| **A. Static demo** *(current)* | Clickable styled screens, live maps/charts, pretend data | Any browser, offline | L0–L1 | **done** | $0 | Very low risk / Low reward — great for look-and-feel sign-off only |
| **B. Self-contained demo + mock API** *(Recommended next)* | Full clickable flows, fake login & data, no DB | Laptop (also Windows) | L1 | **S–M** (P1–P2) | $0 | Low risk / **High reward** — convincing demos & usability tests, cheap, fast |
| **C. Real full-stack MVP** | True app: DB, auth, RBAC, live updates | **Ubuntu** dev→staging→prod | L2–L3 | **XL** (P3–P8) | ~$20–80 (1 small VPS + managed PG/Redis optional) | Medium risk / **High reward** — the actual product; needs ops discipline |
| **D. AI-assisted autonomous build & ops** | Option C, but scaffolded/maintained by agents + optional AI features | Ubuntu + CI + agents | L3–L4 | **XL+** ongoing | C + agent/LLM usage | Higher risk / High reward — fastest build, but needs guardrails, review & cost control |

*Plain English:* **B** is the cheap, fast, low-risk way to get a "working" app for demos. **C** is the real thing
(the documented architecture) and is the right MVP target — but only on Ubuntu, with real effort. **D** uses AI to
go faster and to add smart/auto features, trading some predictability for speed.

### 12.4 Levels of autonomy (how self-running it is)
| Level | Meaning | Needs | Effort to reach | Risk–reward |
|---|---|---|---|---|
| **L0 Static** | Hand-opened HTML, no data | nothing | done | safe / demo-only |
| **L1 Mock-data app** | Works end-to-end on fake data/login | mock API (P2) | S–M | low / high (demos) |
| **L2 Real backend, manual ops** | Real data/auth; you start/stop it | P3–P6 | XL | medium / high |
| **L3 Automated delivery** | Tests + deploys run themselves (CI/CD); monitored | P7–P8 | +M–L | medium / high |
| **L4 Agentic/self-healing + AI** | Auto-triage, auto-scale, self-recovery, AI assist | P9.2 + guardrails | +L+ | higher / high — **needs human-in-loop, budgets, audit** |

> "Autonomous self-contained" realistically means **L1 today** (self-contained demo) and **L3 later** (a real app
> that builds/deploys/monitors itself). **L4** (an app that operates itself with AI) is feasible but should always
> keep a human approving high-impact actions — apt for disaster-response safety.

### 12.5 Cost & effort summary (indicative, one developer)
- **Path B (mock):** ~**1 week**, **$0** infra. **Path C (real MVP):** ~**4–8 weeks**, **$20–80/mo** infra
  (a single Ubuntu VPS can host dev/staging; managed Postgres/Redis optional). **Path D:** C + ongoing
  agent/LLM spend (control with budgets, caching, batch jobs).
- Biggest effort sinks: **P4 backend** and **P8 DevOps**. Biggest *value-per-effort*: **P2 mock** (tiny effort,
  unlocks a full demo).

### 12.6 Risk–reward notes per phase
- **P1/P2 (frontend+mock):** risk **low**, reward **high** — do first.
- **P3/P4 (DB+backend):** risk **medium** (security, data modeling), reward **high** — the core.
- **P5 (gateway/WS):** risk **medium** (real-time edge cases), reward **high** (the "live" feel).
- **P7 (tests/a11y/i18n):** risk **low**, reward **high** — pays back by preventing regressions; non-negotiable
  for a government/accessibility-first product.
- **P8 (DevOps):** risk **medium** (config drift, secrets), reward **high** (repeatable, safe releases).
- **P9 (AI/agentic):** risk **higher** (cost, correctness, safety), reward **high** — gate behind human approval.

### 12.7 Recommended path & immediate next steps
1. **Recommended:** do **Path B now** (self-contained demo + mock API — Phases **P1 → P2**), then decide on
   **Path C** for the real MVP on Ubuntu. Rationale: maximum value for least cost/risk, keeps everything runnable
   on this Windows box, and turns the templates into a convincing, testable product immediately.
2. **First three TODOs to start with:** P1.1 (shared partials) → P1.2 (API client) → P2.1 (mock API + seed).
3. **Confirm before I build:** which **Option (A/B/C/D)** and **autonomy level** do you want to target, and should
   I begin Phase **P1–P2** now? (See chat for the same options with recommendations.)

> **✅ Decision (2026-06-07): Option A — keep as a static demo.** No P1+ work begins now. To resume later,
> pick a path here and start at §12.7 step 2 (P1.1 → P1.2 → P2.1 for Path B).

---

## 13. Consolidated Requirements & Specifications (CANONICAL — read before any edit)

> **What this section is, in plain words.** Everything the user has asked for across all rounds, written as
> *requirements* with *exact values*. Two audiences: a **complete novice** (each item starts with a plain-English
> "what & why") and **Claude / a developer on a future iteration** (each item gives the precise spec + the file to
> change). **Golden rule:** if you revise the templates, keep every requirement below true, or update this section
> in the same change. Where a number/colour/name is given, use it *exactly*.

### R1 — Deliverable shape & how to rebuild  *(novice: "what files exist and how to regenerate them")*
- **Two layers.** (a) `pages/01..15-*.html` = individual pages that **link** the shared `assets/idrm-design-system.css`
  + `assets/idrm-templates.js`. (b) `idrm-templates-showcase.html` = **one standalone file** with all CSS/JS
  **inlined** + the beige plan/workflows intro + all 15 pages concatenated, each in a `.tpl-frame` separated by
  `<hr color="skyblue">`. The page **markup must stay identical** between the two layers.
- **The showcase is generated, never hand-edited.** Build pipeline:
  1. Edit `pages/*.html`, `_showcase-intro.html`, `assets/*.css|js` as needed.
  2. If you changed icons/emoji/circled-numbers → run `_apply-icons.ps1` (idempotent).
  3. Always finish with `_build-showcase.ps1` to regenerate `idrm-templates-showcase.html`.
  4. Preview with the `idrm-templates` launch config / `node templates/_preview-server.js` → `http://localhost:4599`.
- **Files:** see §5 tree + §8 helper list (`_showcase-intro.html`, `_build-showcase.ps1`, `_apply-icons.ps1`,
  `_preview-server.js`, `.claude/launch.json`). A renamed copy of the original artifact lives at
  `templates/visual_hierarchy_slate_emerald_REFERENCE.html` (do **not** edit it — it's the reference).

### R2 — Text encoding (CRITICAL — caused the footer "â€" bug)  *(novice: "why weird characters appear and how to avoid them")*
- All deliverable files are **UTF-8**. Editing HTML/CSS/JS/MD via the normal editor is safe.
- **The trap:** Windows PowerShell 5.1 runs a `.ps1` **as ANSI (Windows-1252)**. Any literal non-ASCII character
  written *inside a script's string literals* (— em-dash, · middot, × times, © copyright, or emoji) is corrupted on
  output → mojibake like `â€"`. This produced the showcase footer glitch.
- **The rule for ALL `.ps1` scripts here:** keep the script **pure ASCII**. Emit non-ASCII either as **HTML
  entities** (`&mdash; &middot; &times; &copy; &amp;`) — used in `_build-showcase.ps1` — or build it **from code
  points** at runtime (`[char]::ConvertFromUtf32(0x1F3E0)`) — used in `_apply-icons.ps1`. Never paste raw emoji or
  dashes into a `.ps1`. Files are written with `UTF8Encoding($false)` (UTF-8, no BOM).

### R3 — Layout & page separators  *(request #1)*
- Showcase: every page wrapped in `<section class="tpl-frame" id="tpl-NN-name">` with a dark label bar
  (number + filename + "Open standalone ↗") and preceded by `<hr color="skyblue">` (renders as a 2px sky line via
  `hr[color]` CSS). **Exactly 15 separators / 15 frames.**
- Inside frames, page-level `position:sticky/fixed` chrome is neutralised to `static` (navbar, sidebar, bottom-nav)
  so stacked pages don't overlap.

### R4 — Typography  *(request #2 + "improve heading sizes")*  — exact values, file: `assets/idrm-design-system.css`
- Font **Inter** (Google Fonts) + system fallback. Body `line-height: 1.75` (= **28px** at the 16px base — this is
  request #2 and must not change). Body prose (`p`, `.text-body`) is fluid **16→17px** `clamp(1rem,0.97rem+0.16vw,1.0625rem)`.
- **Fluid heading scale (current, keep exact):**
  - `h1` `clamp(1.75rem, 1.45rem + 1.5vw, 2.25rem)` → **28→36px**, extrabold.
  - `h2` `clamp(1.375rem, 1.20rem + 0.9vw, 1.625rem)` → **22→26px**, bold, **+ `border-bottom:2px` + `padding-bottom`** (the underline — restored in R2; the original design had it).
  - `h3` `clamp(1.1875rem, 1.09rem + 0.5vw, 1.375rem)` → **19→22px**.
  - `h4` `clamp(1.0625rem, 1.01rem + 0.28vw, 1.1875rem)` → **17→19px**.
- One `<h1>` per page; never skip levels.

### R5 — Colour tokens  *(incl. the "mellow the service-type colours" request)*  — file: `assets/idrm-design-system.css` `:root`
- Base palette = **Slate (neutrals) + Emerald (primary)**, Light mode. Page bg `#f8fafc`, surface `#fff`,
  headings `#0f172a`, body `#334155`. **Intentional a11y choices (keep):** muted text = `slate-600 #475569` (AAA);
  primary **button** rest = `emerald-700 #047857` (`--color-primary-hover`, AA white label; brand primary is
  `emerald-600 #059669`), and primary button **hover** = `emerald-900 #064e3b` (`--color-primary-darker`) +
  `shadow-lg` — a clearly-visible darken, since a single 700→800 step was too subtle (Round 10).
- **Service-type accents — MELLOWED (muted-professional), use these EXACT hexes:** RESCUE `#c2554f`,
  MEDICAL `#c16b83`, FOOD `#b07f30`, WATER `#4f86b3`, SHELTER `#8174ad`, OTHER `#6b7280`. Used by `.svc-dot`,
  the admin breakdown bars, **and** the doughnut chart's literal `backgroundColor` in `pages/15-*.html`
  (order there is MEDICAL,FOOD,WATER,SHELTER,RESCUE,OTHER) — **keep CSS tokens and chart colours in sync.**
- **Beige "metadata" tokens:** `--color-bg-beige #faf6ed`, `--color-bg-beige-soft #fdfbf6`, `--color-border-beige #e8dfc9`.
- Status (10), priority (4), privacy (3) palettes already defined in CSS — match FS §3.3 hues. Status/priority must
  **always pair colour with text** (WCAG 1.4.1 — colour is never the only signal).

### R6 — Iconography (Lucide inline SVG)  *(the "replace flag-post unicode icons with SVG" request)*
- **What & why:** wayfinding/UI icons were emoji (inconsistent across fonts). They are now **inline SVG** from
  **Lucide** (https://lucide.dev, ISC-licensed) — chosen by the user. Inline = no icon-font, no extra request,
  colour follows text.
- **Mechanism:** markup is `<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">…paths…</svg>`. The `.ic` CSS
  class supplies `stroke:currentColor; fill:none; stroke-width:2; size 1.15em`, with context size overrides
  (`.nav-toggle .ic`, `.brand-mark .ic`, `.avatar .ic`, `.stat-icon .ic`, `.ico .ic`, `.bottom-nav .ico .ic`,
  `.alert-icon .ic`, `.privacy/.chip/.status .ic`).
- **Scope = "UI & navigation icons".** Mapping applied (emoji → Lucide): ◆ brand→`life-buoy`, ☰→`menu`,
  🏠→`home`, 🆘→`circle-plus`, 📋→`clipboard-list`, 🗺️→`map`, 📍→`map-pin`, 🔔→`bell`, ⚙️→`user`, 🔒→`lock`,
  🔍→`search`, 📞→`phone`, 📊→`layout-dashboard`, 🆕→`inbox`, 🚐→`truck`, 👥→`users`, 📈→`bar-chart`,
  ✅→`circle-check`, 🧾→`file-text`, 📨→`mail`, ⚡→`zap`, ⏱️→`clock`, 🏥→`building-2`, 🏛️→`landmark`,
  📝→`square-pen`, 🛡️→`shield`.
- **Deliberately KEPT as emoji** (do not convert): status/alert glyphs **✓ ✗ ⚠️ ℹ️ 💡**; wave 👋; celebration 🎉;
  empty-state 📭; password show/hide **👁 / 🙈** (toggled by JS via `textContent`); **priority dots 🔴🟠🟡🟢** and
  **service-type emoji 🛟🚑🍲💧🏚️❓ inside `<select><option>`** — because **HTML cannot embed an SVG inside an
  `<option>`**.
- **To add/replace an icon later:** add the Lucide path to `$paths` in `_apply-icons.ps1`, add the emoji code-point
  → name to `$map`, re-run `_apply-icons.ps1`, then `_build-showcase.ps1`. (Get path data from lucide.dev; the
  script is pure-ASCII per R2.)
- **⚠️ NEVER put a mapped emoji inside an HTML attribute** (`placeholder`, `title`, `value`, `aria-label`, `alt`).
  The icon script replaces emoji blindly, and an `<svg>` (with `"` and `<`) inside an attribute **breaks the
  markup** — this caused the Round-7 search-box corruption (`placeholder="🔍 Search…"`). Put the icon in a
  **separate element** instead, e.g. a search field:
  `<div class="input-group has-icon-left"><span class="input-icon-left"><svg…/></span><input placeholder="Search…"></div>`.
  `_apply-icons.ps1` now warns if a leak is detected; R14 has the grep check.

### R7 — Section number badges  *(the "number display can be improved" request)*
- Circled-digit unicode (①–⑥) → `<span class="num-badge">N</span>` (small emerald circle, white digit). Appears in
  the showcase **Contents** list and the 6 beige section headings. Applied by `_apply-icons.ps1`.

### R8 — Header [ROLE] badge + auth element + access (developer) note  *(Round-6/8)*
- **Left, beside the brand = a `[ROLE]` badge** — markup
  `<div class="brand-group"><a class="brand">◆ IDRM</a><span class="brand-role">ROLE</span></div>` — showing the
  page's **default/expected role**: **01–04 → Public** (muted `.brand-role.public`); **05–11 → CITIZEN**;
  **12–14 → PROVIDER**; **15 → DM_AUTHORITY**. Applied by `_apply-brand-role.ps1` (idempotent; header brand only).
  Every header therefore reads **`[◆ IDRM] [ROLE] … [auth element]`**.
- **Top-right of every page = standard AUTH STATE (the "auth element"), separate from the role badge:**
  - **Public pages (01–04):** a **"Sign in"** button (`.btn.btn-outline.btn-sm` → `03-login.html`). The **login**
    page shows **"Create account"** instead; **home** shows **"Sign in" + "Get started"** (primary).
  - **Login-required pages (05–15):** an **account icon button** =
    `<a href="11-profile.html" class="avatar" title="Account" aria-label="Account">` wrapping the Lucide **user** SVG.
    Page actions ("+ Request", "← Back", "Sign out") sit to its left; on profile the icon is `aria-current="page"`.
- **Privacy levels (PUBLIC/PROTECTED/PRIVATE) are DATA attributes — NEVER shown in the nav.** They appear only on
  request cards and the create-service form as `.privacy-*` badges.
- **Access roles live ONLY in the beige developer note** (R9): first line `<strong>Access ·</strong> {roles,
  default first}` — metadata for developers, not user-facing UI.
- **Matrix-validated access (FS §3.3) — drives the beige note + the public/auth split (keep exact):**
  | Pages | Header auth element | Access roles (documented in the beige note) |
  |---|---|---|
  | 01–04 home/register/login/forgot | "Sign in" (login → "Create account"; home adds "Get started") | Public (no login) |
  | 05 dashboard · 08 my-requests · 10 alerts · 11 profile | account icon → profile | any signed-in role (role-aware), default CITIZEN |
  | 06 create request | account icon | CITIZEN(default), VOLUNTEER, ORGANIZER, DM_AUTHORITY, ADMIN may create; PROVIDER/MANAGER/EVENT_MANAGER/AUDITOR cannot |
  | 07 service detail | account icon | requestor (CITIZEN/VOLUNTEER/ORGANIZER), assigned PROVIDER/MANAGER, DM_AUTHORITY, AUDITOR (read-only), ADMIN |
  | 09 live map | account icon | any signed-in role; Public may view the public map |
  | 12–14 provider | account icon | PROVIDER(default), MANAGER, ADMIN |
  | 15 admin | account icon | DM_AUTHORITY(default), ADMIN; EVENT_MANAGER (events), AUDITOR (read-only) |
- Brand mark = Lucide **life-buoy** (`.brand-mark`); the brand is wrapped in `.brand-group` with the `[ROLE]` badge
  beside it (see top bullet). The old top-right `.role-tag/.role-pill` pill (Round 4) was removed; the account
  button reuses `.avatar` styled as a link (see R6).

### R9 — Developer "API ·" meta note  *(the "make the API footer beige = metadata" request)*
- `.api-note` = **beige** (`#faf6ed`) with a dashed beige border and a `::before` label
  **"ⓘ Developer reference — metadata, not part of the page"**. It holds the Access line (R8) + the documented API
  calls. It is reference-only chrome, visually distinct from real page UI (matches the beige plan band).

### R10 — "Contact & privacy" options (page 06)  *(the "improve the PROTECTED display" request)*
- Rendered as a vertical stack of `.privacy-option` **cards** (each a `<label>` wrapping the radio +
  `.privacy-option-body` = badge row + description). Selected card highlights via `:has(input:checked)`.
  **PROTECTED is the default** and shows a "Default" badge. Privacy can only be raised, never lowered (note kept).

### R11 — Live maps & charts  *(self-contained-with-graceful-fallback)*
- **Maps:** Leaflet **1.9.4** + OpenStreetMap tiles via CDN on pages **05, 06, 07, 09**. Container is
  `.map-canvas[data-map]` with `data-lat/-lng/-zoom` and `data-markers='[…JSON…]'`; `idrm-templates.js` lazy-inits
  (IntersectionObserver). **Graceful fallback:** if Leaflet/CDN is unavailable the static placeholder remains.
  Remember GeoJSON is `[lng,lat]` but Leaflet wants `[lat,lng]`.
- **Charts:** Chart.js **4.4.1** via CDN on page **15**: `<canvas data-chart='{…config…}'>` with a `.chart-fallback`
  (CSS bars) that is hidden once the chart draws. Doughnut colours must equal the R5 service-type hexes.

### R12 — Content rules  *(appropriateness)*
- **Region:** Hyderabad + Vijayawada **pilot only**. Flagship sample request lives at **"Kukatpally, Hyderabad"**
  (coords **17.4948, 78.3996**). **No Chennai.** Emergency numbers: **108** ambulance, **112** all-emergency,
  **1070** disaster cell. Sample people/orgs use Indian / Telugu-region names.
- **Enums are UPPERCASE & exact** (see §3). **Canonical roles** only (no `SERVICE_PROVIDER/ORG_ADMIN/SYSTEM_ADMIN`).
  **HTTP = GET/POST only** with action sub-endpoints (`/approve /accept /complete /verify /cancel /reject`).
  Finance/Donations, AI chatbot, native mobile = **Post-MVP**.

### R13 — Responsiveness & accessibility  *(request #3 + a11y-first)*
- Mobile-first; verify **360 / 768 / 1280px**. Top nav collapses to the hamburger ≤860px; the citizen bottom
  tab-bar appears ≤640px; tap targets ≥44px; no hover-only affordances.
- Semantic HTML; one `h1`; visible `focus-visible` rings (never removed); `role="alert"` (+ `aria-live` for errors);
  `aria-current="page"`; every input has a real `<label>`; colour never the sole signal; honour
  `prefers-reduced-motion`. Decorative SVGs/emoji are `aria-hidden`.
- **Interaction-state contrast (Round 9):** every button keeps readable text in *all* states. **An `<a>` used as a
  button must override the global `a` / `a:hover` colour** — otherwise its text gets re-tinted on hover (emerald-800
  text on an emerald-800 hover background = invisible). Each `.btn-*` variant sets an explicit `:hover`/`:focus`
  colour (specificity 0,2,0 > the `a:hover` 0,1,1); button links also get `text-decoration:none` on hover.
  Hover states must also be **clearly visible** (Round 10): the primary button darkens emerald-700 → **emerald-900**
  (`--color-primary-darker`) + `shadow-lg` — don't let rest & hover be two adjacent dark greens (the old 700→800 step
  was nearly imperceptible, worse under `prefers-reduced-motion` which drops the lift).

### R14 — Definition of Done  *(run this before calling any revision finished)*
1. If icons/emoji/numbers changed → `_apply-icons.ps1`; then **always** `_build-showcase.ps1`.
2. Preview (`idrm-templates`) and confirm:
   - **No mojibake** — page text has no `â€` / `Â`; footer reads "IDRM — Page Templates & Workflows".
   - **No icon leaked into an attribute** — `grep '="[^"]*<svg'` returns **0** across all HTML (the icon script
     also warns). No stray `<svg` / `class=` text visible on any page.
   - Icons render (no broken glyphs); kept-emoji set per R6 still present; **no console errors**.
   - **Buttons:** hover every variant — text stays visible (anchor-buttons keep their own colour, never the
     `a:hover` colour) and button links don't underline (Round 9).
   - Header correct (R8): the **`[ROLE]` badge** sits beside the brand (Public/CITIZEN/PROVIDER/DM_AUTHORITY);
     public pages show "Sign in" (login → "Create account"); login-required pages show the account icon;
     **no `.role-tag` / `.role-pill` remain** (15 `.brand-role` badges in the showcase).
   - Body line-height = **28px** (1.75×); H1 ≈ 36px at desktop; `h2` underline present.
   - Showcase: **15** `<hr color="skyblue">`, **15** `.tpl-frame`, **15** beige "Access ·" notes; TOC anchors resolve.
   - Responsive at 360 / 768 / 1280 (burger nav, bottom tab-bar, stacked layout).
3. Update **§11** (add a Round entry) and **§13** (if a rule changed). Keep `pages/*.html` and the showcase in sync.
