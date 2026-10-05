# Orientation — Start Here & How to Read

> **Part of:** IDRM Documentation · `00-orientation.md`
> **Answers:** What is IDRM, where do I begin, and how is this documentation organised?
> **Source posters:** Big Picture (35)
> **Audience:** Everyone · **Depth:** Overview
> **Status:** Draft

---

## What is IDRM, in one line?

**IDRM (Integrated Disaster Response Management)** is a single, people-centric platform that helps
communities and agencies **prepare for, respond to, and recover from disasters** — by putting incidents,
resources, volunteers, maps, communication, and analytics in one place.

## The three things to remember

1. **The posters are the authoritative design.** Every document is written to match `posters/`.
2. **IDRM is a modular monolith** — one Python application. Simple on purpose, with room to grow.
3. **Read by role, not front-to-back.** Use the map below and jump to what you need.

---

## The documentation set

This is a **lean set**: one substantial document per phase, numbered in reading order. The number *is* the
order.

| # | Document | Answers | For whom |
|---|---|---|---|
| 00 | **This file** | Where do I start? | Everyone |
| 01 | [`01-foundation.md`](01-foundation.md) | *Why* does IDRM exist? | Leaders, stakeholders, everyone |
| 02 | [`02-architecture.md`](02-architecture.md) | *What* is IDRM? | Architects, developers |
| 03 | [`03-engineering.md`](03-engineering.md) | *How* is it built? | Developers |
| 04 | [`04-data.md`](04-data.md) | The data & maps | Data / GIS engineers |
| 05 | [`05-security.md`](05-security.md) | How is it kept safe? | Security engineers |
| 06 | [`06-quality.md`](06-quality.md) | How do we know it works? | Testers, developers |
| 07 | [`07-operations.md`](07-operations.md) | How do we run it? | Operators, DevOps/SRE |
| 08 | [`08-organization.md`](08-organization.md) | Who owns it, where's it going? | Leaders, teams |
| 90 | [`90-glossary.md`](90-glossary.md) | What does this term mean? | Everyone (lookup) |
| 99 | [`99-decisions-and-history.md`](99-decisions-and-history.md) | Decisions & rationale (owner reference) | Owner / maintainers |

Not sure where to begin? Read **01 → 02**, then follow your role:

| If you are… | After 01–02, read… |
|---|---|
| Leader / sponsor | 08 (roadmap & big picture) |
| Architect | 02, 03, then 04–05 |
| Developer (backend/frontend) | 03, then 04 / 06 |
| Data / GIS engineer | 04 |
| Security engineer | 05 |
| Tester | 06 |
| Operator (DevOps/SRE) | 07 |

---

## How each document is built

Every document opens with a fixed **header** so you always know what you're reading and whether to trust it:

```
> Part of:        the file's place in the set
> Answers:        the one question this document answers
> Source posters: which poster(s) this content comes from
> Audience:       who it's written for
> Depth:          Overview (plain) or Deep (technical detail)
> Status:         Draft / Reviewed / Final
```

Inside, documents use short sections, tables, and plain language. **Overview depth** comes first; deeper
technical detail is added in a later pass and marked **Depth: Deep**.

## Golden rules

1. **The posters are the authoritative design** — every document matches `posters/`.
2. **One phase per file** — if you can't find a topic, it's a section inside its phase document.
3. **Read by role** — you are not expected to read everything.
4. Decisions and their rationale are recorded in
   [`99-decisions-and-history.md`](99-decisions-and-history.md) (owner reference).
