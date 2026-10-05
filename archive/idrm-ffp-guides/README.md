# IDRM FFP — Guides

**FFP = Full-Fledged Product** (the later, full-scale enterprise system the MVP evolves into).

This folder holds the **FFP novice-friendly guides** (tutorials & how-tos for the enterprise/full-scale product).
Flat `<prefix>-<category>-<name>.md` naming with the shared legend:
`00` start · `10` setup · `20` build · `30` contribute · `40` reference.

## Approach — DELTA, not duplicate
The full novice→mastery guide library (39 topic **101s** + 12 **role-mastery** journeys) lives **once**, in
[`../idrm-mvp-guides/`](../idrm-mvp-guides/00-start-learning-paths.md), and every guide there is already
**phase-tagged** (MVP vs FFP). To keep **one source of truth** (guardrail: *cross-link, don't duplicate*), the
FFP side does **not** copy those guides — it adds a thin **FFP learning hub** that routes to the shared library
and sequences the FFP-specific path.

## Present
- [`00-start-ffp-learning-paths.md`](00-start-ffp-learning-paths.md) — **FFP learning hub**: the "what FFP adds"
  delta table, the FFP reading path through the shared 101s, per-role FFP deltas, and the FFP spec docs.
  *(Added 2026-08-14.)*
- [`30-contribute-developer-guide.md`](30-contribute-developer-guide.md) — contributing **across services**
  (extends the MVP contributor guide). *(Added 2026-08-12.)*

See [`../INDEX.md`](../INDEX.md) for the full archive map.
