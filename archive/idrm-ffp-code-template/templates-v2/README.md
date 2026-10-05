# IDRM Templates **v2** — RBAC-driven, with a FastAPI/Bun render split

A **mirror (not a replica)** of [`../templates/`](../templates/), re-pivoted around the **FS §3.3 Permission
Matrix**. Where v1 organised pages by *screen*, v2 organises them by **role × capability**, and adds a
first-class answer to *"which screens must FastAPI render, and which can Bun serve/offload?"*

> **Full reasoning lives in [`FLOW-ANALYSIS-PLAN.md`](FLOW-ANALYSIS-PLAN.md)** — the RBAC plan, the per-role
> page-extension spec, and the render-strategy matrix. Read that first; this README is just orientation.

## What's here

| | |
|---|---|
| **`idrm-rbac-showcase.html`** | ⭐ One standalone file: the plan band + permission matrix + render legend + a **role switcher**, then all 24 templates concatenated (`<hr color="skyblue">` between each). Open it in any browser. |
| **`FLOW-ANALYSIS-PLAN.md`** | The brain: RBAC matrix, scope qualifiers, per-role nuances, the FastAPI/Bun render map, file tree, checklist. |
| **`pages/`** | 24 standalone templates, grouped by `role-dashboard/`, `service-detail/`, `requests-list/`, `map/`, `admin-console/`, `shared/`. |
| **`assets/`** | The v1 design system **mirrored** + a v2 RBAC section (render-tier badge, scope banner, role strips, permission-matrix styling). |
| `_showcase-intro.html`, `_build-showcase.ps1` | Source + generator for the showcase. |

## The three ideas v2 adds (visible on every page)

1. **`[ROLE]` badge** by the brand — whose page this is.
2. **Scope banner** — the exact data boundary the role sees (Own / Area / Type / Org / Event / Jurisdiction /
   All) — i.e. the server-side `WHERE` clause, made visible.
3. **Render-tier badge** — who renders it:
   - 🟢 **FastAPI (F)** — per-user, RBAC-gated, privacy-redacted (dashboards, service detail, lists, admin).
   - 🔵 **Bun (B)** — public / static / cacheable + edge plumbing + WebSocket (home, auth, public map, assets).
   - 🟣 **Hybrid (H)** — Bun-cached shell + a streamed FastAPI island (e.g. the declare-event zone map).

   **Litmus test:** bytes differ by who's logged in (or hide anything a lesser role mustn't see) → **F**.
   Same for everyone, or plumbing → **B**. Fast shell + private filling → **H**. Live without reload → **WS**.

## View it

- **Easiest:** open `idrm-rbac-showcase.html` directly in a browser (self-contained; only the Inter font, Leaflet
  and Chart.js load from CDNs, all with graceful fallbacks).
- **Individual pages:** open any file under `pages/…`. They link the shared `assets/` so keep the folder intact.
- This is a **static demo** — no backend needed (and none runs on the Windows authoring box; see `../CLAUDE.md`).

## Rebuild the showcase (after editing any page / asset / intro)

```powershell
# 1) (only if you added/changed emoji) convert UI icons -> inline Lucide SVG
powershell -ExecutionPolicy Bypass -File templates-v2/_apply-icons.ps1
# 2) (re)apply the display controls (font / size / theme / search) to every page in pages/
powershell -ExecutionPolicy Bypass -File templates-v2/_apply-controls.ps1
# 3) regenerate the standalone showcase
powershell -ExecutionPolicy Bypass -File templates-v2/_build-showcase.ps1
```

Every page under `pages/` **and** the showcase carry the same control bar — font face (Inter / DM Sans / Work Sans /
Source Sans Pro / Lato / Lexend / System Default), size XS–XL, Light/Dark/System theme, and Ctrl/⌘+K search.

All icons are **inline Lucide SVG** (`<svg class="ic">`), never emoji — `_apply-icons.ps1` enforces this (only
typographic glyphs `●` `→` `★` `✓` are kept). Step 2 regenerates `idrm-rbac-showcase.html` from `pages/*`, the shared CSS/JS, and `_showcase-intro.html`.
The script is **pure ASCII** and writes **UTF-8 (no BOM)** — see `FLOW-ANALYSIS-PLAN.md` §12 (R2) for why.

## Relationship to v1

v1 (`templates/`) stays as-is — the feature-organised static demo. v2 reuses its design system verbatim and
layers the RBAC view on top. Nothing in v1 is changed.
