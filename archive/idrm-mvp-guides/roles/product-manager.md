# Role-Mastery — Product Manager / Product Owner

> *Type: Guide (role-mastery / learning journey) · Audience: PM/PO, from novice · Status: MVP — current · Blueprint §25.1*
> *You own the **why** and the **what**: the problem IDRM solves, for whom, and what to build next. This journey
> sequences the reading that takes you there. You don't need to code — but you must understand the domain deeply.*

---

## 1. Your mission

Make sure IDRM builds the **right thing**: understand disaster-relief needs, translate them into prioritised
requirements, and measure whether they moved the outcome. Your north star is IDRM's success metrics
(response 12h→2h, fulfilment 60%→80%).

## 2. Your mastery map

```mermaid
flowchart LR
    A["Software Basics"] --> B["Disaster Management"]
    B --> C["IDRM Vision"]
    C --> D["Stakeholders"]
    D --> E["Domains"]
    E --> F["Personas / Journeys"]
    F --> G["PRD"]
    G --> H["Prioritisation"]
    H --> I["Acceptance Criteria"]
    I --> J["Metrics"]
    J --> K["Operational Drills"]
    K --> L["Product Strategy"]
    L --> M["Mastery"]
```

## 3. Your learning path (rung → what to read)

1. **Software basics + IDRM orientation** → [SDLC 101](../learn/sdlc-101.md) · [Learning Paths](../00-start-learning-paths.md)
2. **Disaster management** → [Disaster Management 101](../learn/disaster-management-101.md) ·
   [Incident Management 101](../learn/incident-management-101.md) · [Resource Management 101](../learn/resource-management-101.md)
3. **IDRM vision + domains + personas** → [`10-requirements-prd.md`](../../idrm-mvp-docs/10-requirements-prd.md) ·
   the [domain card](../../instructions/domain.md)
4. **PRD + prioritisation + acceptance criteria** →
   [`11-requirements-scope-and-acceptance.md`](../../idrm-mvp-docs/11-requirements-scope-and-acceptance.md)
   (Feature→Req→Acceptance→Test). Remember: **the PRD is tech-free** — needs, not solutions.
5. **Metrics + operational drills** → the success targets (§8 domain card) ·
   [Disaster Drill / Scenario Testing 101](../learn/disaster-drill-scenario-testing-101.md)
6. **Product strategy** → [`../../idrm-ffp-docs/11-requirements-scope-and-roadmap.md`](../../idrm-ffp-docs/11-requirements-scope-and-roadmap.md)
   (the phased FFP evolution + trigger-per-capability).

## 4. MVP vs FFP for you

- **MVP:** the pilot scope, the 8-state incident lifecycle, and the two headline metrics. Keep scope lean —
  every "wouldn't it be nice" tech idea belongs in the FFP backlog with a **trigger**, not the MVP.
- **FFP:** money/donations, national rollout, advanced analytics, multi-channel intake — you own deciding **when**
  a trigger justifies each.

## 5. Mastery test

You can explain, to a stranger, **what problem IDRM solves, for whom, why, what should be built next, and how
success will be measured** — and defend why something is *out* of the MVP.

---
*Related:* [Business Analyst](business-analyst.md) · [Incident/Ops Manager](incident-ops-manager.md) ·
[Learning Paths](../00-start-learning-paths.md)
