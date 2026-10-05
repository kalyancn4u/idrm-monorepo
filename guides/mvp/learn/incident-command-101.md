# Incident Command 101

> *Type: Guide (101 / foundational) · Audience: all stakeholders → developers · Status: Domain — phase-neutral · Track: Domain (#8)*
> *When many teams converge on a disaster, who's in charge? The Incident Command System answers that. This guide
> explains the structure everyone in emergency response shares — and how IDRM's roles reflect it.*

---

## 1. The problem: coordination at scale

A single ambulance needs no org chart. A city-wide flood with dozens of agencies, hundreds of responders, and
thousands of needs will collapse into chaos without a clear, agreed structure. The **Incident Command System
(ICS)** is that structure — a standard way to organise a response so authority, roles, and communication are
unambiguous, whatever the disaster's size.

ICS is used worldwide precisely because it's **standard**: people from different agencies can plug into the same
structure instantly.

---

## 2. The key ideas

- **Incident Commander (IC)** — the single person ultimately in charge of a response. Unity of command: everyone
  reports up one clear chain (no one takes orders from two bosses).
- **Functional sections** — the work is split into standard areas:
  - **Operations** — does the tactical work (rescue, medical).
  - **Planning** — tracks the situation and plans ahead.
  - **Logistics** — supplies people, equipment, resources.
  - **Finance/Admin** — costs and records.
- **Span of control** — one leader supervises a manageable number of people/teams (roughly 3–7), so no one is
  overwhelmed. Big responses grow by adding layers, not by overloading one person.
- **Scalability** — the same structure expands or contracts with the incident.

---

## 3. How it maps to IDRM

IDRM doesn't replace ICS — it **supports** it in software:

| ICS concept | In IDRM |
|---|---|
| Incident Commander / command | **coordinator/admin** role (approve, assign, verify) |
| Operations | **provider** role working incidents/tasks |
| Logistics | the **resources** module |
| Situation/Planning | the **COP**/map + reports |
| One clear record & chain | **audit** trail; RBAC enforces who can do what |

The government chain from Disaster Management 101 (NDMA → SDMA → DDMA) is a real-world command hierarchy; IDRM's
coordinator/admin permissions mirror that authority. Full role hierarchies and an Auditor role arrive in **FFP**.

---

## 4. Mastery check

1. Explain what ICS is and the problem it solves.
2. Define **Incident Commander**, **unity of command**, and **span of control**.
3. Name the functional sections and what each does.
4. Explain how ICS **scales** with incident size.
5. Map ICS roles onto IDRM's roles and modules.

---

## 5. Go deeper

- FEMA ICS resources — training.fema.gov/is/courseoverview (ICS-100) · ISO 22320 (incident coordination)
- Related: [Incident Management 101](incident-management-101.md) · [Emergency Operations Centre 101](emergency-operations-centre-101.md) · [RBAC/ABAC 101](rbac-abac-101.md)

---
*Next:* Event-Driven Architecture 101 (Software-Engineering track) · *Up:* [Learning Paths](../00-start-learning-paths.md)
