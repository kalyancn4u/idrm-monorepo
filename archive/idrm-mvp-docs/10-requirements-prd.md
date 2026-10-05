# IDRM MVP — Product Requirements Document (PRD)

> *Type: Document (specification) · Audience: everyone (product, stakeholders, developers, testers) · Status: MVP — current*
> *Consolidated from the archived PRDs (generations v0–v3, primarily v3; those generations are now retired to `../_removed/`). **Needs only — no technology** (the stack lives in [`20-architecture-system.md`](20-architecture-system.md)). Enterprise-scale items are recorded in §13 as **→ FFP**.*

> **What a PRD is:** it describes **what IDRM must do and why, and for whom** — *not how it is built*.
> All technology decisions live in the Architecture document.

> **Two terms you'll meet everywhere — defined once, here:**
> - **MVP = Minimum Viable Product** — the *lean first build*: the **smallest system that still delivers real value**, built as simply as possible. **This document specifies the MVP.**
> - **FFP = Full-Fledged Product** — the *later, full-scale* system the MVP grows into (national scale, mobile apps, AI matching, …). Anything tagged **→ FFP** is deferred **on purpose, not dropped** (the full list is §13).
>
> *Why split them at all? So IDRM can start **saving lives sooner**, without over-building expensive complexity before it is needed. Every MVP choice deliberately favours **simplicity now + a clean path to grow later** (see [`20-architecture-system.md`](20-architecture-system.md)).*

---

## 1. Vision

**IDRM (Integrated Disaster Response Management)** is a **government-endorsed, web-based platform**
that connects people affected by a disaster with the organizations that can help them, through a
simple, **map-based interface** — in real time, during emergencies.

> *In one line: "Uber for disaster relief" — connect people who need help with those who can provide
> it, quickly and transparently, when it matters most.*

The MVP proves this value for an initial region of India with the **essential** capabilities, built
as simply as possible, with a credible path to national scale (that scale is the **FFP**).

---

## 2. The Problem (grounded in India)

During floods, cyclones, and other disasters in India today:

1. **Fragmented communication** — citizens call many separate emergency lines (in India: **100** police, **108** ambulance, **1070/1078** disaster relief); no single place tracks a request, so duplicates waste scarce resources.
2. **Manual coordination** — responders juggle phone calls, WhatsApp groups, and spreadsheets, with no real-time picture.
3. **No transparency** — citizens don't know if help is coming; there's no accountability and no data for future planning.
4. **Unequal coverage** — urban areas get attention, rural areas and non-dominant-language speakers are underserved.

*Real impact cited from 2024 events:* Mumbai floods — ~12-hour average response; Chennai cyclone —
~40% of requests unanswered; Kerala landslides — no centralized tracking.

---

## 3. Objectives

| # | Objective | What success looks like |
|---|---|---|
| O1 | **Save lives** | Faster response to critical requests; fewer preventable deaths |
| O2 | **Improve efficiency** | Less duplication; the right responder reaches the right request faster |
| O3 | **Build trust & transparency** | Citizens can see request status; authorities can see the real picture |

Secondary objectives: give authorities **data for planning**, and reach **underserved groups**
(rural, multiple languages).

---

## 4. Stakeholders

| Stakeholder | Interest in IDRM |
|---|---|
| **Citizens / affected people** | Get help fast; know it's coming |
| **Service providers** (NGOs, hospitals, volunteers) | See real requests; respond by capacity; avoid duplicate effort |
| **Coordinators / Government DM authorities** | Real-time oversight; approve critical actions; accountability & reporting |
| **Platform administrators** | Manage users, organizations, roles, and data integrity |
| **Sponsoring government body** | Public-safety outcomes; measurable impact; endorsement/governance |

---

## 5. Personas (from the archived PRD)

| Persona | Role | Primary need | Key pain today |
|---|---|---|---|
| **Rajesh Kumar** | Affected citizen | Request help and know it's on the way | Calls many numbers, no updates, fear |
| **Dr. Priya Sharma** | Service provider (medical/NGO) | See and respond to real, nearby needs | Uncoordinated calls, duplicate effort |
| **Arjun Reddy** | Volunteer coordinator | Organize volunteers against real requests | No shared, live picture |
| **Lakshmi Iyer (IAS**⁠—senior government officer**)** | Government coordinator | Oversee response; spot gaps; report | Days-old spreadsheets, no ground truth |

*Each persona maps to a role in the system (§7 use cases, and RBAC in [`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md)).*

---

## 6. What IDRM Does (MVP capabilities)

The MVP is **one responsive web platform** (works on ordinary smartphones) that serves three views by role:

- **Citizen view** — create a help request on a map, choose a **service type** (e.g. RESCUE, FOOD, MEDICAL), set **priority**, track status, confirm completion, and rate the service.
- **Provider view** — see nearby requests on a map, filter by type/priority, **accept** (claim) a request, update its status, and mark it complete.
- **Coordinator/Admin view** — a live overview of all requests, approve/reject **critical** ones, monitor response times, manage organizations, and generate basic reports.

> *(Separate native mobile apps and a richer single-page web client are **→ FFP**, §13. The MVP is one
> web app with role-based views.)*

---

## 7. Use Cases (essential MVP flows)

- **UC-1 Report a request:** a citizen opens IDRM, marks a map location, selects service type + priority, describes the need, and submits. Emergency/guest submission is allowed for life-safety.
- **UC-2 Match & accept:** a nearby provider sees the request, accepts it (so no one else duplicates), and is guided to the location.
- **UC-3 Track & update:** the provider updates status; the citizen sees progress in near-real-time and receives notifications.
- **UC-4 Complete & verify:** the provider marks the request complete; the citizen confirms and rates it.
- **UC-5 Oversee:** a coordinator watches the live picture, approves/rejects critical requests, and spots gaps.
- **UC-6 Report:** a coordinator generates a basic report (response times, fulfillment) and exports it.

---

## 8. Functional Requirements (MVP)

| ID | Requirement |
|---|---|
| **FR-1** | Users can register and authenticate; citizens may submit an emergency request as a guest. |
| **FR-2** | A citizen can create a request with a **map location**, **service type**, **priority**, and description. |
| **FR-3** | Users can view requests and available providers/resources on an **interactive map**. |
| **FR-4** | A provider can see nearby requests, **filter** them, and **accept/claim** one (preventing duplicates). |
| **FR-5** | A provider can **update status** and **mark a request complete**; status is tracked end-to-end. |
| **FR-6** | The system sends **notifications** (e.g. SMS/email) on key status changes. |
| **FR-7** | A citizen can **track** their request in near-real-time and **verify/rate** completion. |
| **FR-8** | A coordinator/admin has a **dashboard**: overview, approve/reject **critical** requests, monitor response times, manage organizations. |
| **FR-9** | The system enforces **role-based access** (citizen, provider, coordinator, admin). |
| **FR-10** | The system keeps an **audit log** of significant actions. |
| **FR-11** | The system produces **basic reports** (response time, fulfillment) with export. |
| **FR-12** | The interface is **multi-language ready** (English + at least one regional language at MVP; broader localization → FFP). |

---

## 9. Non-Functional Requirements (MVP)

| ID | Requirement | Target/intent |
|---|---|---|
| **NFR-1 Availability** | The platform must be dependable **when disasters strike** (surge load). | High availability during events |
| **NFR-2 Performance** | Fast and usable on **basic smartphones and low bandwidth**. | Quick map & request actions under load |
| **NFR-3 Security & privacy** | Protect personal and location data; enforce access control; audit actions. | See security doc |
| **NFR-4 Usability** | A stressed, non-technical citizen can file a request in **minimal steps**. | Map-first, simple flows |
| **NFR-5 Accessibility** | Accessible to people with disabilities and low digital literacy. | **WCAG 2.2 AA**-aligned (WCAG = Web Content Accessibility Guidelines, the international standard for accessible web design; "2.2 AA" is the target level) |
| **NFR-6 Reliability & integrity** | Requests are tracked accurately from creation to completion. | No lost/duplicated requests |
| **NFR-7 Scalability path** | MVP serves the initial region but is designed to grow. | Grow toward FFP without rewrite |

---

## 10. Business Rules

- A **critical** request may require **coordinator approval**.
- A request is **claimed by one provider** at a time (no duplicate fulfillment).
- Every request has a lifecycle: **created → accepted → in-progress → completed → verified**. *(This is the everyday "happy path". The **full, authoritative lifecycle is 8 states** — it adds **`approved`** for critical requests and the exits **`cancelled`**/**`rejected`** — defined precisely in [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md). Same idea; that doc is the source of truth.)*
- **Emergency/guest** citizen requests are allowed (life-safety over friction).
- Providers respond **by capacity and service type**.
- All significant actions are **auditable**.

---

## 11. Constraints, Assumptions, Dependencies

**Constraints**
- India-focused; **government-endorsed** and governed.
- Must work on **ordinary smartphones and degraded/low-bandwidth** connectivity.
- **MVP simplicity** — essential features only; initial coverage is a limited region (e.g. Telangana & Andhra Pradesh).

**Assumptions**
- Citizens have basic phone/internet access (with SMS as a fallback channel).
- Partner organizations (providers) are onboarded; authorities provide oversight.
- Connectivity may be **degraded** during a disaster and the design must tolerate it.

**Dependencies**
- Onboarding of **partner provider organizations**.
- **Government endorsement** and any official data/authority.
- A **messaging channel** (SMS/email) for notifications.
- **Base map data** for the served region.

---

## 12. Success Criteria (MVP — target Q4 2026)

| Measure | Baseline (today) | MVP target |
|---|---|---|
| Coverage | — | **2 states, 50+ districts** |
| Registered users | — | **10,000+** |
| Partner organizations | — | **50+** |
| Average response time | ~12 hours | **~2 hours** |
| Request fulfillment rate | ~60% | **~80%** |
| Lives saved (annual, est.) | — | **500+** |
| User satisfaction | — | High (tracked) |

*The MVP is "complete" when these essential capabilities work end-to-end for the initial region; the
precise pass/fail checks live in [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md).*

---

## 13. Out of Scope for the MVP — Deferred to FFP

*Recorded here (per decision) so nothing is lost; these are addressed in the
[FFP charter](../idrm-ffp-docs/prompts/instructions_idrm_ffp_docs.md).*

- **AI-powered automated matching/routing** (MVP uses straightforward, rule-based matching).
- **Native mobile apps** and a **rich single-page web client** (MVP is one responsive web app with role-based views).
- **National-scale rollout** (all states/UTs), and **market/competitive positioning & monetization**.
- **Advanced/predictive analytics & insights** (MVP = basic reports).
- **Full localization** in 12+ Indian languages (MVP = core languages, multi-language-*ready*).
- **Multi-channel intake** (WhatsApp / voice / IVR integration).
- **Deep real-time push infrastructure** (MVP = near-real-time updates are acceptable).

---

*Related MVP documents:* [`11-requirements-scope-and-acceptance.md`](11-requirements-scope-and-acceptance.md) ·
[`20-architecture-system.md`](20-architecture-system.md) ·
[`22-architecture-security-and-iam.md`](22-architecture-security-and-iam.md) ·
[`40-api-specification.md`](40-api-specification.md) · [`50-data-model.md`](50-data-model.md).
Plan: [`prompts/instructions_idrm_mvp_docs.md`](prompts/instructions_idrm_mvp_docs.md).
