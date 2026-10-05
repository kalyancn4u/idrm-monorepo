# Disaster Drill / Scenario Testing 101

> *Type: Guide (101 / foundational) · Audience: all stakeholders → developers/ops · Status: **FFP** — next-phase · Track: Quality (#31)*
> *IDRM's whole purpose is to work during a disaster. This unique guide is about rehearsing exactly that — testing
> the **people, process, and system together** against realistic emergencies before a real one arrives.*

---

## 1. Why drills, not just tests

Ordinary tests check the software. But in a real disaster, success depends on **software + people + process**
under stress. A **disaster drill** (or scenario test) rehearses a whole realistic emergency end-to-end — like a
fire drill for the entire response, IDRM included. It's the ultimate validation that the system helps rather than
hinders when it counts.

This mirrors the disaster lifecycle's **Preparedness** phase from [Disaster Management 101](disaster-management-101.md).

---

## 2. What a scenario test exercises

A scenario ("a cyclone hits a coastal district; 500 incidents in an hour; two agencies responding") stresses:

- **The workflow** — can citizens report, coordinators approve/assign, providers complete, all at volume?
- **The people** — do the roles know what to do? Is the UI usable under pressure?
- **The system** — does it stay fast and correct under a realistic surge? (overlaps
  [Performance Testing 101](performance-testing-101.md))
- **The failure modes** — what happens when connectivity drops, a node fails, or data is stale?

---

## 3. Resilience & chaos (the engineering side)

Beyond rehearsing the happy path, mature teams **deliberately inject failure** to prove the system degrades
gracefully — **chaos engineering**: kill a service, throttle the network, fail the database's replica, and watch.
The goal is to discover weaknesses in a controlled drill, not during a real cyclone.

Key ideas: **graceful degradation** (partial service beats total outage), **offline resilience** (the FFP field
app queues and syncs — [caching/messaging spoke](../../../archive/instructions/caching-messaging.md)), and validated
**backup/restore** ([Backup & Restore 101](backup-restore-101.md)).

---

## 4. IDRM context

- **MVP:** run **tabletop + seeded-scenario** drills — load realistic incident data, walk the full lifecycle with
  people in each role, confirm the pilot targets (response 12h→2h, fulfilment 60%→80%) are achievable, and capture
  an **After-Action Review**.
- **FFP:** formal, repeatable scenario suites + chaos experiments across the distributed system, tied to SLOs and
  DR plans ([Disaster Recovery 101](disaster-recovery-101.md)).

> The After-Action Review closes the loop back to the disaster lifecycle: every drill feeds learning into the
> next improvement.

---

## 5. Mastery check

1. Explain why a **drill** tests more than the software.
2. Describe what a realistic IDRM scenario exercises.
3. Explain **chaos engineering** and **graceful degradation**.
4. Distinguish a tabletop drill from a seeded-scenario drill.
5. Connect drills to the disaster lifecycle's Preparedness and After-Action phases.

---

## 6. Go deeper

- Principles of Chaos Engineering — principlesofchaos.org · Google SRE (DiRT drills) — sre.google/books
- Related: [Disaster Management 101](disaster-management-101.md) · [Performance Testing 101](performance-testing-101.md) · [Backup & Restore 101](backup-restore-101.md)

---
*Next:* Networking 101 (Operations track) · *Up:* [Learning Paths](../00-start-learning-paths.md)
