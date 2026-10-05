# Role-Mastery — Solution / Software Architect

> *Type: Guide (role-mastery / learning journey) · Audience: architect, from strong-dev → mastery · Status: MVP — current · Blueprint §25.3*
> *You own the **shape** of the system and the **decisions** behind it — and the discipline of writing down *why*.
> For IDRM that means defending the modular-monolith-now, microservices-later strategy against real trade-offs.*

---

## 1. Your mission

Design a structure that meets IDRM's **quality attributes** (reliability, security, scalability, maintainability)
at each phase, keep the module/API boundaries clean so the MVP can evolve into the FFP **without a rewrite**, and
record every significant choice as an **ADR** with its trigger.

## 2. Your mastery map

```mermaid
flowchart LR
    A["Software Fundamentals"] --> B["IDRM Domain"]
    B --> C["Requirements"]
    C --> D["Quality Attributes"]
    D --> E["Architecture Principles"]
    E --> F["Context / Container"]
    F --> G["Component Design"]
    G --> H["Data / Events"]
    H --> I["Security"]
    I --> J["Failure Architecture"]
    J --> K["ADR"]
    K --> L["Architecture Review"]
    L --> M["Mastery"]
```

## 3. Your learning path (rung → what to read)

1. **IDRM domain + requirements** → [Disaster Management 101](../learn/disaster-management-101.md) ·
   [`10-requirements-prd.md`](../../../docs/mvp/10-requirements-prd.md) · [domain card](../../../archive/instructions/domain.md)
2. **Architecture principles + context/container/component** →
   [`20-architecture-system.md`](../../../docs/mvp/20-architecture-system.md) (the modular monolith) ·
   [backend-services spoke](../../../archive/instructions/backend-services.md)
3. **Data / events** → [`50-data-model.md`](../../../docs/mvp/50-data-model.md) ·
   [Database 101](../learn/database-101.md) · [Event-Driven Architecture 101](../learn/event-driven-architecture-101.md) (FFP)
4. **Security** → [`22-architecture-security-and-iam.md`](../../../docs/mvp/22-architecture-security-and-iam.md) ·
   [security spoke](../../../archive/instructions/security.md) · [Threat Modeling 101](../learn/threat-modeling-101.md)
5. **Failure architecture** → [Disaster Recovery 101](../learn/disaster-recovery-101.md) ·
   [SRE 101](../learn/sre-101.md) · [Disaster Drill Testing 101](../learn/disaster-drill-scenario-testing-101.md)
6. **ADRs + review** → [`21-architecture-decisions.md`](../../../docs/mvp/21-architecture-decisions.md) (MVP, 14 ADRs)
   and [`../../idrm-ffp-docs/21-architecture-decisions.md`](../../../docs/ffp/21-architecture-decisions.md)
   (FFP, trigger-gated) — study how each decision names its trigger.

## 4. The IDRM architectural through-line (know this cold)

The **API contract and module boundaries are the invariant**: the MVP is a modular monolith; the FFP extracts
services **one at a time, least-coupled first (auth), on a concrete trigger** (Strangler Fig), with the public
`/api/v1` contract preserved. Gateway = **APISIX** (Kong evaluated, not chosen for the free build —
[api-gateway spoke](../../../archive/instructions/api-gateway.md)). Advanced tech (React, Redis, brokers, Docker/K8s) is
**deferred, not dropped**.

## 5. Mastery test

You can **justify IDRM's structure against its quality attributes and failure modes**, write a sound **ADR** with
an explicit trigger, and lead an architecture review — including defending why something is *not* in the MVP.

---
*Related:* [Backend Engineer](backend-engineer.md) · [Security Engineer](security-engineer.md) ·
[DevOps / SRE](devops-sre.md) · [Business Analyst](business-analyst.md)
