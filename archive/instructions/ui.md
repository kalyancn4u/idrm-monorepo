# IDRM Instructions — UI / Clients

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Phase rule:** MVP is deliberately **React-free**; React/Expo are **FFP**. Same `/api/v1` for all clients.

## MVP (build first) — LOCKED
- Web UI = **HTML + Tailwind CSS v4 + vanilla JS + Leaflet**. **No React, no Bun/Node** (ADR-003/014).
- Server-friendly HTML; progressive enhancement; emergency "lite" path stays fast on low-end Android.
- Accessibility: semantic HTML + ARIA, **WCAG 2.2 AA** (raised from 2.1 in T3, 2026-08-14; both phases now 2.2).

## FFP (next phase)
- Adds a **React web SPA** (rich admin / Common Operational Picture / analytics) and a
  **React Native / Expo** mobile client (offline-first field responder). The MVP HTML app **stays valid**.
- Stack: React + TypeScript (`strict`); Vite *or* Next.js; TailwindCSS (same tokens as MVP); TanStack Query;
  React Hook Form + Zod; Zustand *or* Redux Toolkit (only if state truly needs it); React-Leaflet for maps.
- Accessibility: **WCAG 2.2 AA** (same as MVP since T3); full India localization (react-i18next).
- One design system (tokens/components) spans HTML + React + RN.

## Canonical docs (source of truth)
- FFP design (what): [`../idrm-ffp-docs/60-uidesign-frontend.md`](../idrm-ffp-docs/60-uidesign-frontend.md)
- FFP engineering (how): [`../idrm-ffp-docs/61-frontend-engineering-standards.md`](../idrm-ffp-docs/61-frontend-engineering-standards.md)
- MVP web interaction: [`../idrm-mvp-docs/60-uidesign-web-interaction.md`](../idrm-mvp-docs/60-uidesign-web-interaction.md)

## Trusted external references
- React — react.dev · TypeScript — typescriptlang.org
- TanStack Query — tanstack.com/query · React Hook Form — react-hook-form.com · Zod — zod.dev
- TailwindCSS — tailwindcss.com · Expo (React Native) — docs.expo.dev · React-Leaflet — react-leaflet.js.org
- WCAG 2.2 — w3.org/TR/WCAG22 · WAI-ARIA APG — w3.org/WAI/ARIA/apg
