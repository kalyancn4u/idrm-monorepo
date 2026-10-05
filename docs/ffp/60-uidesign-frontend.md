# IDRM FFP — Frontend (React Web + React Native/Expo)

> *Type: Document (specification) · Audience: frontend devs, designers · Status: FFP — next-phase (planned)*
> *Extends the MVP web UI [`../idrm-mvp-docs/60-uidesign-web-interaction.md`](../mvp/60-uidesign-web-interaction.md). Adds rich **React** web and **native mobile** clients — **on the same `/api/v1` contract**. Consolidates `v3/32-design-frontend.md`, `60-uidesign-design-system.md`, `v2/60,61,62-uidesign-*`.*

> **Invariant:** the MVP's **HTML + Tailwind + JS** app stays valid and keeps working. FFP clients are
> **additive** and consume the **same endpoints** (MVP ADR-003) — no server change to add a client.

---

## 1. The client family

| Client | Role | When | Tech |
|---|---|---|---|
| **HTML + Tailwind + JS** (MVP) | fast, universal, emergency | always | server-friendly HTML |
| **React SPA** | rich admin dashboards, COP, analytics | Phase 2+ | React + Tailwind, same design tokens |
| **React Native / Expo** | field responder, **offline-first**, GPS/camera | Phase 2+ | RN/Expo, shared component patterns |

All three call the **same API**; a **BFF edge service** (Bun/Node/Deno behind APISIX) may compose calls per
client without changing the public contract.

## 2. React web SPA
For information-dense workflows the plain UI struggles with: live **Common Operational Picture**, rich maps,
data-viz dashboards, complex tasking. Reuses the MVP's interaction model (screens → API calls) and design
system; adds client-side state, real-time updates (websocket/SSE via the edge), and role-aware admin tools.

## 3. React Native / Expo mobile
For field responders: **offline-first** capture (queue + sync when connectivity returns), native GPS/camera,
push notifications, and a streamlined tasking flow. Consumes the same API; offline writes reconcile via
idempotent requests + events.

## 4. Shared design system & accessibility
One design system (tokens, components) spans web + mobile; **WCAG 2.2 AA** accessibility; multilingual
(full localization, FFP-FR-6); consistent terminology with the PRD/domain model.

## 5. Real-time & offline
- **Real-time:** live COP/tasking/chat via websocket/SSE through the edge + event backbone
  ([`81-ops-messaging-and-async.md`](81-ops-messaging-and-async.md)).
- **Offline:** local store + background sync; conflict handling via server-authoritative state + idempotency.

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · **Engineering standards (how to build it): [`61-frontend-engineering-standards.md`](61-frontend-engineering-standards.md)** ·
[`20-architecture-system.md`](20-architecture-system.md) · [`40-api-specification.md`](40-api-specification.md) ·
MVP UI [`../idrm-mvp-docs/60-uidesign-web-interaction.md`](../mvp/60-uidesign-web-interaction.md).
