# Role-Mastery — Business / Domain Analyst

> *Type: Guide (role-mastery / learning journey) · Audience: BA/Domain Analyst, from novice · Status: MVP — current · Blueprint §25.2*
> *You are the bridge between messy operational reality and precise, buildable requirements. Your craft is turning
> "responders can't find who needs help" into testable rules the team can implement.*

---

## 1. Your mission

Understand the disaster-response domain well enough to **capture, clarify, and specify** what IDRM must do —
unambiguously, traceably, and testably — so engineers and QA build and verify the right behaviour.

## 2. Your mastery map

```mermaid
flowchart LR
    A["Business Fundamentals"] --> B["Disaster Lifecycle"]
    B --> C["Domain Vocabulary"]
    C --> D["Process Mapping"]
    D --> E["Use Cases"]
    E --> F["Business Rules"]
    F --> G["Workflow / State Machines"]
    G --> H["Requirements"]
    H --> I["Traceability"]
    I --> J["Scenario Analysis"]
    J --> K["Mastery"]
```

## 3. Your learning path (rung → what to read)

1. **Disaster lifecycle + domain vocabulary** → [Disaster Management 101](../learn/disaster-management-101.md) ·
   [Incident Management 101](../learn/incident-management-101.md) · the [domain card](../../../archive/instructions/domain.md)
2. **Process mapping + use cases** → the operational flow ([Learning Paths §2](../00-start-learning-paths.md)) ·
   personas in [`10-requirements-prd.md`](../../../docs/mvp/10-requirements-prd.md)
3. **Business rules + workflow/state machines** → the **8-state incident lifecycle**
   ([Incident Management 101](../learn/incident-management-101.md)) — the canonical state machine you'll specify against.
4. **Requirements + traceability** →
   [`11-requirements-scope-and-acceptance.md`](../../../docs/mvp/11-requirements-scope-and-acceptance.md)
   (Feature→Req→Acceptance→Test — the golden thread) · [SDLC 101](../learn/sdlc-101.md) on traceability.
5. **Scenario analysis** → [Disaster Drill / Scenario Testing 101](../learn/disaster-drill-scenario-testing-101.md) ·
   edge cases (who *can't* do what — cross-check with [RBAC/ABAC 101](../learn/rbac-abac-101.md)).

## 4. MVP vs FFP for you

- **MVP:** specify the lean lifecycle, the four roles + guest, and the file-upload/media rules precisely.
- **FFP:** per-request privacy levels, disaster-event entity, multi-agency workflows — you'll model these as the
  triggers arrive, keeping the public API contract stable.

## 5. Mastery test

You can take an **ambiguous operational problem** and produce **precise, testable requirements** — each traceable
to a design, an API operation, a data field, and a test — that engineers and QA can act on without guessing.

---
*Related:* [Product Manager](product-manager.md) · [QA / SDET](qa-sdet.md) · [Solution Architect](solution-architect.md)
