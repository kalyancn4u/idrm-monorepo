# Common Operational Picture 101

> *Type: Guide (101 / foundational) · Audience: all stakeholders → developers · Status: Domain — phase-neutral · Track: Domain (#4)*
> *When many people respond to a disaster, the deadliest problem is everyone acting on different information. The
> Common Operational Picture solves it. This guide explains the idea and how IDRM's map delivers it.*

---

## 1. What a COP is

A **Common Operational Picture (COP)** is a **single, shared, continuously-updated view** of the situation that
everyone in the response uses. "Common" is the key word: the field team, the coordinator, and the partner agency
all see the *same* incidents, resources, and status — so decisions line up instead of conflicting.

Without a COP you get duplicated effort (two teams to the same site), gaps (a need everyone assumed someone else
had), and confusion. With one, the whole response rows in the same direction.

---

## 2. What makes a picture "operational"

- **Shared** — one source of truth, not many private spreadsheets.
- **Current** — updated in near-real-time as the situation changes.
- **Relevant & role-aware** — each role sees what it needs (a citizen sees their request; a coordinator sees the
  district).
- **Actionable** — you can *act* from it (assign, escalate), not just look.

Usually it's **map-centred**, because disaster information is inherently geographic
([GIS for Emergency Response](gis-for-emergency-response.md)).

---

## 3. How IDRM delivers a COP

IDRM's **map view is a COP in miniature**: incidents and resources drawn on a shared **Leaflet + PostGIS** map,
fed by the `/api/v1` API so everyone sees the same data.

| COP property | In IDRM |
|---|---|
| Shared truth | one PostgreSQL/PostGIS source, one API |
| Map-centred | Leaflet map of incidents & resources |
| Role-aware | RBAC filters what each role sees |
| Actionable | act on an incident from the map (or the list) |
| Accessible | a list/table mirrors the map (never map-only) |

- **MVP:** a functional shared map + list, refreshed on load/refresh.
- **FFP:** a rich, **live** COP — real-time updates via WebSocket/SSE, layered map data, multi-agency views, and
  analytics dashboards. This is the flagship of the future frontend.

---

## 4. Mastery check

1. Define a **COP** and explain why "common" is the crucial word.
2. List the properties that make a picture *operational*.
3. Explain why a COP is usually map-centred.
4. Describe how IDRM's map + list delivers a COP.
5. Contrast the MVP COP with the FFP live COP.

---

## 5. Go deeper

- NATO/FEMA COP concepts (reference) · Related: [Emergency Operations Centre 101](emergency-operations-centre-101.md) ·
  [GIS for Emergency Response](gis-for-emergency-response.md)
- IDRM UI: [`../../idrm-mvp-docs/60-uidesign-web-interaction.md`](../../../docs/mvp/60-uidesign-web-interaction.md) ·
  FFP frontend [`../../idrm-ffp-docs/60-uidesign-frontend.md`](../../../docs/ffp/60-uidesign-frontend.md)

---
*Next:* [Emergency Communications 101](emergency-communications-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
