# Foundation — Why IDRM Exists

> **Part of:** IDRM Documentation · `01-foundation.md`
> **Answers:** Why are we building IDRM, for whom, and to solve what?
> **Source posters:** Posters 1–8 (Phase 0 Foundation, Phase 1 Business Understanding)
> **Audience:** Everyone · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

This is the "why" of IDRM, in the order a newcomer naturally asks:

1. [Vision & mission](#1-vision--mission) — where we're headed and how.
2. [The problem](#2-the-problem-we-solve) — what's broken today.
3. [Scope](#3-scope-what-the-mvp-does-and-doesnt-do) — what the MVP does and doesn't do.
4. [Goals](#4-goals) — functional and non-functional targets.
5. [Who it serves](#5-who-it-serves--stakeholders--personas) — stakeholders and personas.
6. [Business domains](#6-business-domains) — the areas of work IDRM covers.
7. [Disaster lifecycle](#7-the-disaster-lifecycle) — the phases IDRM supports.
8. [Business workflow](#8-business-workflow-overview) — how a request becomes a response.
9. [How we measure success](#9-how-we-measure-success).
10. [How we deliver it](#10-how-we-deliver-it--sdlc-roadmap) — the SDLC roadmap.

---

## 1. Vision & mission

> **Vision — A disaster-resilient world where communities, institutions, and responders act early,
> respond faster, and recover stronger — saving lives and livelihoods.**

> **Mission — To integrate people, processes, data, and technology on a unified platform that enables
> collaboration, situational awareness, and informed action across the disaster management lifecycle.**

Six **guiding principles** break ties when decisions are hard:

| Principle | In practice |
|---|---|
| **People-Centric** | Prioritise safety, dignity, and inclusion — especially for the vulnerable. |
| **Integrity & Trust** | Be transparent and accountable; protect data and privacy. |
| **Interoperability** | Connect systems and stakeholders using open standards. |
| **Timeliness** | Enable early warnings, rapid response, continuous updates. |
| **Innovation** | Use technology and data for smarter, evidence-based decisions. |
| **Sustainability** | Strengthen long-term resilience, not just quick fixes. |

Six **strategic goals** turn the mission into direction: an **integrated platform**, **situational
awareness**, **effective communication**, **community empowerment**, **data-driven decisions**, and a
**resilient ecosystem**.

---

## 2. The problem we solve

When disasters strike, the biggest failures are rarely a lack of goodwill — they're a lack of *coordination
and shared information*. Today:

- **Siloed systems and fragmented data** across agencies delay situational awareness.
- **Slow information flow and poor coordination** hurt timely decisions and response.
- **Manual processes and duplicate reporting** reduce efficiency and accuracy.
- **Limited visibility of resources** makes allocation and tracking hard.
- **Weak last-mile communication** leaves citizens under-informed during emergencies.
- **Little standardisation or interoperability** across tools and procedures.

IDRM exists to close these gaps with one shared, real-time picture that everyone can act on.

---

## 3. Scope — what the MVP does (and doesn't do)

The MVP is deliberately focused: enough to be genuinely useful, small enough to build and trust.

**In scope (MVP):**

- Situational awareness & dashboard
- Incident reporting & alerts
- Resource management
- Tasking & coordination
- Communication & notifications
- Reports & analytics (basic)
- User & role management
- Mobile & web access
- Data security & audit trails

**Out of scope (MVP — considered for later):**

- Advanced AI/ML predictions
- Complex financial management
- Long-term recovery planning
- Custom hardware solutions
- Deep third-party integrations (beyond essential APIs)

This boundary is a promise: the MVP stays simple, and larger capabilities arrive on the
[evolution roadmap](08-organization.md).

---

## 4. Goals

**Functional goals** — what IDRM must *do*:

- Provide real-time situational awareness with geospatial visualisation.
- Enable rapid incident reporting from field to command.
- Facilitate coordination and collaboration among responders.
- Manage and track resources, assets, and deployments.
- Deliver timely alerts and two-way communication.
- Generate actionable reports and insights for decision-makers.
- Ensure data integrity, traceability, and auditability.

**Non-functional goals** — how well it must do them:

| Quality | Target |
|---|---|
| **Availability** | High availability (≈ 99.5%+) for critical operations. |
| **Performance** | Fast response; able to scale during surge situations. |
| **Security & privacy** | Protect confidentiality, integrity, and privacy by design. |
| **Usability & accessibility** | Intuitive, multilingual, WCAG 2.x AA — usable by all, including PWD. |
| **Interoperability** | Standards-based APIs for seamless exchange. |
| **Reliability & resilience** | Fault-tolerant, with backup and recovery. |
| **Maintainability** | Modular, testable, observable. |

---

## 5. Who it serves — stakeholders & personas

IDRM is built for a broad ecosystem. At a glance:

| Stakeholder group | Role in IDRM |
|---|---|
| **Citizens & communities** | Report incidents, request help, receive alerts, see public info. |
| **Volunteers & NGOs / CBOs** | Register skills, take tasks, coordinate relief. |
| **Field responders** | Police, Fire, Medical, SDRF, NDRF — act on the ground, update status. |
| **District administration & EOCs** | Coordinate response, allocate resources, oversee operations. |
| **State & national agencies** | NDMA/SDMA/DDMA, MHA, NDRF, IMD, ISRO, MoHFW, BRO, Railways — policy, oversight, specialized resources, escalation. |
| **Line departments** | Health, Power, Water, Transport — provide services and data. |
| **Partners & donors** | UN agencies, private partners — support and transparency. |
| **Media & public channels** | Disseminate verified updates. |
| **Technical & operational teams** | System admins, data managers, support. |

**Cross-cutting enablers (for all stakeholders):** Trusted Access · Communication · **Common Operating
Picture** (real-time shared situational awareness) · Data & Interoperability · Mobility · Analytics & Insights ·
Security & Privacy.

**Primary personas (MVP-facing):**

- **Citizen (Web / Mobile)** — reports needs, tracks status, gets alerts. Needs simplicity and language support.
- **Field Officer (Mobile)** — sees assigned tasks, updates from the field, captures location/evidence.
- **Coordinator / Operator (Backoffice)** — triages incidents, assigns resources, monitors the live map.
- **Administrator** — manages users, roles, configuration, and audit oversight.
- **Government official** — views dashboards and reports for decisions and accountability.

Detailed screen-by-screen user guides for these personas come in a later, task-oriented pass.

---

## 6. Business domains

IDRM's work divides into six domains — these become the platform's core modules:

| Domain | What it covers |
|---|---|
| **Incident Management** | Reporting, classification, status tracking, escalation, timeline. |
| **Resource Management** | Inventory, fleet, equipment, shelters, availability. |
| **Volunteer Management** | Registration, skills, assignments, attendance. |
| **GIS & Mapping** | Live map, layers, geofencing, search, routing. |
| **Communication** | Alerts and notifications across email, SMS, and in-app. |
| **Analytics** | Operational reports, KPIs, dashboards, insights. |

---

## 7. The disaster lifecycle

IDRM supports the full lifecycle, not just the emergency itself:

**Preparedness → Mitigation → Response → Recovery → Resilience**

| Phase | What IDRM helps with |
|---|---|
| **Preparedness** | Planning, training, SOPs, awareness. |
| **Mitigation** | Reducing risk before events; hazard awareness. |
| **Response** | Incident handling, field operations, resource mobilisation, communication. |
| **Recovery** | Restoring services, tracking relief, reporting. |
| **Resilience** | Learning from each event to prepare better for the next. |

Designing for the whole lifecycle is what separates IDRM from a simple "emergency ticketing" tool.

---

## 8. Business workflow overview

At its simplest, IDRM turns a **need** into a coordinated **response**, then learns from it:

```
Detect / Sense      → someone (or a sensor) reports an incident or need
   ↓
Assess / Alert      → the system builds situational awareness and notifies the right people
   ↓
Decide / Plan       → coordinators prioritise and plan the response
   ↓
Act / Execute       → responders and volunteers are assigned and act in the field
   ↓
Monitor / Track     → progress is tracked live on the map and dashboards
   ↓
Evaluate / Learn    → reports and insights feed back into preparedness
```

Every module in [`02-architecture.md`](02-architecture.md) exists to serve a step in this flow.

---

## 9. How we measure success

Success is measured by better *response*, not just working software:

| Area | Example measures |
|---|---|
| **Adoption & Reach** | Active users; registered organisations; geographic coverage. |
| **Response Effectiveness** | Alert delivery time; response-time reduction; resolution rate. |
| **Operational Performance** | Uptime; data accuracy; workflow completion rate. |
| **Stakeholder Satisfaction** | Satisfaction score; training completion. |
| **Impact** | Lives saved; people assisted; resource-utilisation efficiency. |
| **Compliance & Trust** | Policy compliance; data-privacy adherence; audit readiness. |

---

## 10. How we deliver it (SDLC roadmap)

IDRM follows a disciplined delivery lifecycle — from idea to continuous improvement — so value is delivered
early and responsibly:

| Stage | What happens | Output |
|---|---|---|
| **1 · Idea** | Problem discovery, stakeholder inputs, feasibility, value proposition | Problem statement & concept note |
| **2 · PRD & Architecture** | Requirements & use cases, FR/NFR, system architecture, data & integration design | PRD, architecture & design specs |
| **3 · Development** | Iterative development, code standards, security by design, version control | Working software (builds) |
| **4 · Testing** | Test planning, functional, performance, security, UAT | Test reports & quality sign-off |
| **5 · Deployment** | Deployment planning, CI/CD automation, data migration, go-live & rollback plan | Live system (production) |
| **6 · Operations** | Monitoring & alerts, incident management, backup & recovery, user support, SLA management | Stable, available, supported system |
| **7 · Continuous Improvement** | Feedback & analytics, post-incident review, performance tuning, roadmap evolution | Improved outcomes & innovation |

**Cross-cutting principles (every stage):** Security & Privacy · User-Centricity · Interoperability · Data
Quality · Compliance · Accessibility · Sustainability.

This lifecycle mirrors the documentation set itself (Foundation → Architecture → Engineering → … → Operations
→ Organization) and the role responsibilities in [`08-organization.md`](08-organization.md).

---

## Standards we hold ourselves to

**WCAG 2.1 / 2.2 AA** (accessibility) · **ISO/IEC 27001** (information security) ·
**ISO 22301** (business continuity) · **DPDP Act, 2023** (India — data protection).

---

## Where this leads

- What IDRM *is*, technically → [`02-architecture.md`](02-architecture.md)
- Who owns it and where it's headed → [`08-organization.md`](08-organization.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"One platform. Every stakeholder. Resilient communities."*
