# IDRM UI/UX Instructions — Slate + Emerald (Tailwind CSS)

**Version**: 3.0 · **Created (reconciled)**: 2026-05-30
**Design language**: Slate (neutrals) + Emerald (primary), Light Mode
**Styling**: Tailwind CSS · **Applies to**: HTML/Tailwind (primary web), React SPA (admin). React Native (mobile) reuses the same hex tokens — 🔒 Post-MVP.

> **Purpose**: A practical, copy-paste rulebook so any contributor (human or AI) builds **responsive, consistent, accessible** IDRM pages without re-deciding design. This is the *application* guide; the full token reference lives in `start-here/COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md` (being updated to this Slate+Emerald palette — this file is canonical for color/component decisions).
>
> **Golden rule**: Don't invent colors, spacings, or radii. Use the tokens below. If a value isn't here, pick the nearest token rather than a new hex.

---

## 1. Setup — the only config you need

The palette equals Tailwind's built-in `slate` + `emerald` + `amber`/`red`/`blue`/`violet`. So **use Tailwind's default classes directly** (e.g. `bg-emerald-600`, `text-slate-700`). The one thing to configure is the **Inter** font:

```js
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{html,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'] },
      // OPTIONAL semantic aliases (lets you write bg-primary; also eases a future dark mode)
      colors: {
        primary: { DEFAULT: '#059669', hover: '#047857', light: '#d1fae5', dark: '#065f46' },
      },
    },
  },
};
```

```html
<!-- load Inter once, in <head> -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
```

Set `font-sans antialiased bg-slate-50 text-slate-700` on `<body>`.

---

## 2. Token → Tailwind reference (use these, nothing else)

### Colors
| Role | Tailwind class | Hex |
|---|---|---|
| Page background | `bg-slate-50` | `#f8fafc` |
| Surface (card) | `bg-white` | `#ffffff` |
| Surface elevated | `bg-slate-100` | `#f1f5f9` |
| Heading text | `text-slate-900` | `#0f172a` |
| Body text | `text-slate-700` | `#334155` |
| Muted text | `text-slate-500` (AAA: `slate-600`) | `#64748b` |
| Disabled text | `text-slate-400` | `#94a3b8` |
| Primary | `bg-emerald-600` / `text-emerald-600` | `#059669` |
| Primary hover | `hover:bg-emerald-700` | `#047857` |
| Primary tint | `bg-emerald-100` | `#d1fae5` |
| Border (default) | `border-slate-200` | `#e2e8f0` |
| Border (input) | `border-slate-300` | `#cbd5e1` |

### Radius (⚠️ mapped by value, not name)
| Use | Tailwind |
|---|---|
| Buttons, inputs, badges-sm | `rounded-md` (0.375rem) |
| Inputs/buttons default | `rounded-lg` (0.5rem) |
| Cards | `rounded-2xl` (1rem) |
| Pills / badges | `rounded-full` |

### Type scale (matches Tailwind defaults)
`text-xs` 12 · `text-sm` 14 · `text-base` 16 · `text-lg` 18 · `text-xl` 20 · `text-2xl` 24 · `text-3xl` 30 · `text-4xl` 36.
Weights: `font-normal/medium/semibold/bold/extrabold`.

### Elevation & motion
Shadows: `shadow-sm` → `shadow-md` → `shadow-lg` → `shadow-xl`. Transitions: `transition` + `duration-150/200/300`.

---

## 3. Typography hierarchy

| Element | Classes |
|---|---|
| H1 | `text-4xl font-extrabold tracking-tight text-slate-900 leading-tight` |
| H2 | `text-3xl font-bold tracking-tight text-slate-900 border-b-2 border-slate-200 pb-2` |
| H3 | `text-2xl font-semibold text-slate-900` |
| H4 | `text-xl font-semibold text-slate-900` |
| Body | `text-base text-slate-700 leading-normal` |
| Muted | `text-sm text-slate-500` |
| Small/caption | `text-xs text-slate-500` |
| Link | `text-emerald-600 hover:text-emerald-700 hover:underline` |

**Rule:** one `h1` per page; never skip heading levels; use spacing utilities (`mt-8 mb-4`) for rhythm rather than `<br>`.

---

## 4. IDRM semantic color mapping (canonical — match `IDRM-FS.md` §3.3)

### Feedback intents
| Intent | Badge / Alert classes |
|---|---|
| Success | `bg-emerald-50 text-emerald-700 border-emerald-500` |
| Warning | `bg-amber-50 text-amber-700 border-amber-500` |
| Error | `bg-red-50 text-red-700 border-red-500` |
| Info | `bg-blue-50 text-blue-700 border-blue-500` |
| Review | `bg-violet-50 text-violet-700 border-violet-500` |

### Priority (badge color)
| Priority | Color | Badge classes |
|---|---|---|
| `CRITICAL` | red | `bg-red-50 text-red-700 ring-1 ring-red-500/40` |
| `HIGH` | orange | `bg-orange-50 text-orange-700 ring-1 ring-orange-500/40` |
| `MEDIUM` | amber | `bg-amber-50 text-amber-700 ring-1 ring-amber-500/40` |
| `LOW` | emerald | `bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500/40` |

*(Matches the FS map-marker convention — red / orange / amber / green.)*

### Status (badge color) — the 10 canonical states
| Status | Hue | Badge classes |
|---|---|---|
| `SUBMITTED` | violet (awaiting review) | `bg-violet-50 text-violet-700` |
| `APPROVED` | blue | `bg-blue-50 text-blue-700` |
| `ACCEPTED` | sky/blue | `bg-sky-50 text-sky-700` |
| `IN_PROGRESS` | amber | `bg-amber-50 text-amber-700` |
| `COMPLETED` | emerald (light) | `bg-emerald-50 text-emerald-700` |
| `VERIFIED` | emerald (strong) | `bg-emerald-100 text-emerald-800` |
| `REJECTED` | red | `bg-red-50 text-red-700` |
| `DISPUTED` | red (outline) | `bg-white text-red-700 ring-1 ring-red-500` |
| `CANCELLED` | slate | `bg-slate-100 text-slate-600` |
| `EXPIRED` | slate | `bg-slate-100 text-slate-500` |

### Service type (icon dot / accent)
`RESCUE` red-600 · `MEDICAL` rose-500 · `FOOD` amber-500 · `SHELTER` violet-500 · `WATER` blue-500 · `OTHER` slate-500.

### Privacy badge
`PUBLIC` slate · `PROTECTED` (default) blue · `PRIVATE` violet — always pair with a lock icon for `PROTECTED`/`PRIVATE`.

---

## 5. Component recipes (copy-paste)

### Buttons
```html
<!-- Primary (emerald-700 bg for AA contrast on small text) -->
<button class="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-800 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2 active:scale-[.98] disabled:opacity-50 disabled:pointer-events-none">Primary</button>

<!-- Secondary --> <button class="… bg-slate-500 text-white hover:bg-slate-600 …">Secondary</button>
<!-- Outline --> <button class="… border border-emerald-600 text-emerald-700 hover:bg-emerald-50 …">Outline</button>
<!-- Ghost --> <button class="… text-slate-500 hover:bg-slate-100 hover:text-slate-900 …">Ghost</button>
<!-- Danger --> <button class="… bg-red-600 text-white hover:bg-red-700 …">Danger</button>
```
Shared base for every button: `inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2 text-sm font-semibold transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none`. **Minimum tap target 44×44px** on mobile (use `py-2.5`/`min-h-11` for primary actions).

### Card
```html
<div class="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-lg">…</div>
<!-- Elevated: bg-slate-100 shadow-md (no hover lift for static panels) -->
```

### Form field
```html
<div class="mb-5">
  <label class="mb-2 block text-sm font-medium text-slate-900">
    Full name <span class="text-red-500">*</span>
  </label>
  <input type="text" placeholder="Enter your full name"
    class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm text-slate-700 transition placeholder:text-slate-400 focus:border-emerald-600 focus:outline-none focus:ring-2 focus:ring-emerald-600/30 disabled:bg-slate-100 disabled:text-slate-400 disabled:cursor-not-allowed" />
  <p class="mt-1 text-xs text-slate-500">Helper text goes here.</p>
  <!-- error state: add `border-red-500 focus:ring-red-500/30` to input and: -->
  <p class="mt-1 text-xs text-red-600">This field is required.</p>
</div>
```
Checkboxes/radios: `h-4 w-4 accent-emerald-600`. Always wire `<label for>`.

### Badge
```html
<span class="inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold bg-emerald-50 text-emerald-700 ring-1 ring-emerald-500/30">✓ Verified</span>
```

### Alert
```html
<div role="alert" class="mb-4 flex items-start gap-3 rounded-lg border-l-4 border-emerald-500 bg-emerald-50 p-4 shadow-sm">
  <span class="text-lg leading-none text-emerald-600" aria-hidden="true">✓</span>
  <div class="flex-1">
    <p class="text-sm font-semibold text-emerald-800">Success</p>
    <p class="text-sm text-emerald-700/90">Your action was completed.</p>
  </div>
</div>
```
Swap the color family for `warning`/`error`/`info`/`review`. Error/critical alerts: also set `aria-live="assertive"`.

### Data table
```html
<div class="overflow-x-auto rounded-lg border border-slate-200">
  <table class="w-full border-collapse text-sm">
    <thead><tr>
      <th class="bg-slate-100 px-4 py-3 text-left font-semibold text-slate-900 border-b border-slate-200">Name</th>
    </tr></thead>
    <tbody>
      <tr class="hover:bg-slate-50"><td class="px-4 py-3 text-slate-700 border-b border-slate-200">…</td></tr>
    </tbody>
  </table>
</div>
```
On mobile, prefer **stacked cards** over wide tables (or keep `overflow-x-auto`).

### System states (always provide all three)
```html
<!-- Loading --> <div class="rounded-2xl border border-slate-200 bg-white p-12 text-center">
  <div class="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-[3px] border-slate-200 border-t-emerald-600"></div>
  <p class="text-xl font-semibold text-slate-900">Loading…</p></div>
<!-- Empty --> icon + title + description + a primary action ("Create request").
<!-- Error --> icon + "Something went wrong" + Retry button.
```

### Sidebar nav link / Tabs
```html
<a class="block rounded-lg px-4 py-2 text-slate-700 transition hover:bg-slate-100 hover:text-emerald-700">Item</a>
<a aria-current="page" class="block rounded-lg px-4 py-2 bg-emerald-100 text-emerald-800 font-medium">Active</a>

<button class="border-b-2 border-transparent px-4 py-2 text-sm font-medium text-slate-500 hover:text-emerald-700 aria-selected:border-emerald-600 aria-selected:text-emerald-700">Tab</button>
```

### Responsive grid
```html
<div class="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">…</div>
```

---

## 6. Layout & responsiveness (mobile-first — IDRM is used in emergencies)

- **Page shell**: `mx-auto max-w-7xl px-4 py-6 md:px-6 md:py-8` (`max-w-7xl` = 1280px).
- **Mobile-first always**: base styles target the phone; add `sm:` (640) `md:` (768) `lg:` (1024) upward. Never start desktop-first.
- **Sidebar layouts collapse**: `flex flex-col md:flex-row`; sidebar `w-full md:w-64`, border moves from right → bottom on mobile.
- **Touch targets ≥ 44px**, generous spacing, no hover-only affordances (mobile has no hover).
- **Works on 2G / cheap phones**: keep DOM light, lazy-load below the fold, avoid heavy JS for core flows (citizen request must work with minimal JS).
- **≤ 3 clicks** to create a service request; primary CTA always visible without scrolling on mobile.
- **Same tokens across platforms**: HTML/Tailwind (citizen) and React SPA (admin) share these classes; React Native (Post-MVP) reuses the same hex values in StyleSheet.

---

## 7. Accessibility (non-negotiable — "Accessibility First")

- **Contrast floor = WCAG AA (4.5:1 normal, 3:1 large/UI)**; aim AAA for body content (already met by `slate-900`/`slate-700`). Use `slate-600` for small muted text where AAA is required; use `emerald-700` (not `-600`) for primary button backgrounds.
- **Focus visible** on every interactive element: `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600 focus-visible:ring-offset-2`. Never remove focus rings.
- **Semantic HTML**: real `<button>`, `<a>`, `<nav>`, `<table>`, `<label for>`; headings in order.
- **ARIA**: alerts `role="alert"` (errors `aria-live="assertive"`); modals `role="dialog" aria-modal="true"` + focus trap; active nav `aria-current="page"`; icon-only buttons need `aria-label`.
- **Don't rely on color alone** — pair status/priority color with text and/or an icon (color-blind users, and IDRM map markers).
- **Motion**: respect `motion-reduce:` — gate transforms/animations (`motion-reduce:transition-none motion-reduce:hover:translate-y-0`).
- **Forms**: every input has a visible label; errors are text (not just red border) and linked via `aria-describedby`.

---

## 8. Interaction states (apply consistently)
| State | Convention |
|---|---|
| Hover | color deepen + optional `hover:-translate-y-1`/`hover:shadow-lg` (cards), `hover:bg-…` (buttons) |
| Focus | emerald ring (above) — always |
| Active | `active:scale-[.98]` |
| Disabled | `disabled:opacity-50 disabled:pointer-events-none` (+ `cursor-not-allowed` on inputs) |
| Loading | spinner + `pointer-events-none opacity-70`; disable the triggering button |

---

## 9. Do / Don't

**Do**: use the token classes; keep one consistent radius family (`rounded-lg`/`rounded-2xl`); give every list/table a loading + empty + error state; write mobile-first; label every form field; keep the primary CTA emerald.
**Don't**: introduce new hex values or arbitrary spacings; use `emerald-600` text on white for small text (fails AA — use `emerald-700`); rely on color alone for status; nest cards more than one level; remove focus outlines; use the old sky-blue brand or stale enums (`assigned`, `clothing`, `transport`).

---

## 10. Page-build checklist
1. Shell: `mx-auto max-w-7xl px-4 py-6 md:px-6 md:py-8`, `bg-slate-50`, Inter loaded.
2. One `h1`; headings in order; body `text-slate-700`.
3. Components from §5 only; status/priority colors from §4.
4. Mobile-first; verify at 360px, 768px, 1280px; tap targets ≥44px.
5. Every interactive element has a focus ring; color never the only signal.
6. Lists/tables have loading + empty + error states.
7. Forms: labels, hints, text errors, `required` marked.
8. Run an AA contrast check on any custom pairing.

---

*Canonical roles/permissions, statuses, and enums: `docs/development/IDRM-FS.md` §3.3. Full design-token reference: `start-here/COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md` (update pending to this Slate+Emerald palette).*
