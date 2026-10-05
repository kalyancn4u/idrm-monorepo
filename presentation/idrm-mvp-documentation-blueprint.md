---
categories:
- IDRM
- Disaster Management
- Software Architecture
- SDLC
comments: false
date: 2026-08-08
description: A minimum coherent documentation system for Integrated
  Disaster Response Management (IDRM) MVP, covering stakeholders, SDLC,
  architecture, operations, governance, onboarding and role mastery.
pin: true
tags:
- IDRM
- MVP
- documentation
- architecture
- SDLC
- GIS
- security
- DevOps
- SRE
- testing
- onboarding
- mastery
title: IDRM MVP --- Documentation, SDLC & Role-Mastery Blueprint
toc: true
---



# IDRM MVP --- Documentation, SDLC & Role-Mastery Blueprint

> **Integrated Disaster Response Management (IDRM) --- Minimum Viable
> Product**

## Executive Summary

The IDRM MVP should not be documented as a collection of disconnected
architecture notes. It should be documented as a **coherent knowledge
system** that serves four audiences simultaneously:

1.  **Business & operational stakeholders** --- understand what IDRM
    does and why.
2.  **Software delivery teams** --- understand what must be built and
    how.
3.  **Operations, security & governance teams** --- understand how IDRM
    remains secure, reliable, auditable and recoverable.
4.  **New and existing personnel** --- understand how to progress from
    complete novice to independent practitioner and ultimately mastery.

The recommended documentation chain is:

**WHY → WHO → WHAT → WHEN → HOW → DATA → SECURELY → VERIFIED → DEPLOYED
→ OPERATED → OWNED → EVOLVED**

The minimum coherent set is **25 core documents**, supported by
supplementary guides, role-specific learning paths, mastery checklists
and a diagram catalogue.

------------------------------------------------------------------------

## 1. Documentation Philosophy

The central principle is:

> **Every document should have a clear purpose, owner, inputs, outputs
> and downstream dependencies.**

The documentation system should establish traceability from:

**Business Need → Requirement → Use Case → Architecture → Module → API →
Data → Code → Test → Evidence → Release → Operations → Learning**

``` mermaid
flowchart TD
    A["Business Need"] --> B["Requirement"]
    B --> C["Use Case"]
    C --> D["Architecture"]
    D --> E["Module"]
    E --> F["API / Interface"]
    F --> G["Data Model"]
    G --> H["Code"]
    H --> I["Test"]
    I --> J["Evidence"]
    J --> K["Release"]
    K --> L["Operations"]
    L --> M["Learning / AAR"]
    M --> B
```

This closed loop is the foundation for an IDRM documentation system that
remains useful throughout the SDLC and operational lifecycle.

------------------------------------------------------------------------

# 2. Minimum Core Documentation Set

The following **25 documents** form the recommended baseline.

  ------------------------------------------------------------------------
                            \# Document              Purpose
  ---------------------------- --------------------- ---------------------
                            01 **PRD --- Product     Defines problem,
                               Requirements          users, MVP scope,
                               Document**            requirements, NFRs
                                                     and acceptance
                                                     criteria.

                            02 **Vision & Product    Defines why IDRM
                               Strategy**            exists, its strategic
                                                     direction, principles
                                                     and outcomes.

                            03 **Stakeholder &       Defines stakeholders,
                               Persona Catalogue**   personas,
                                                     responsibilities,
                                                     needs, permissions
                                                     and interactions.

                            04 **Business Domain &   Establishes IDRM's
                               Capability Model**    business vocabulary
                                                     and capability
                                                     structure.

                            05 **Disaster Lifecycle  Maps preparedness,
                               & Operating Model**   detection,
                                                     assessment, response,
                                                     stabilization,
                                                     recovery and
                                                     learning.

                            06 **System Architecture Defines architecture
                               & ADR Set**           principles,
                                                     boundaries, quality
                                                     attributes and major
                                                     decisions.

                            07 **Layered /           Defines experience,
                               Deployment            API, domain,
                               Architecture**        integration, data and
                                                     platform layers.

                            08 **Functional          Converts capabilities
                               Architecture &        into functions, use
                               Use-Case Catalogue**  cases and user
                                                     journeys.

                            09 **Module / Component  Defines
                               Specification**       responsibilities,
                                                     interfaces,
                                                     dependencies and
                                                     non-functional
                                                     concerns per module.

                            10 **Data Architecture & Defines entities,
                               Data Dictionary**     relationships,
                                                     ownership, quality,
                                                     classification and
                                                     lifecycle.

                            11 **Data Flow & Event   Defines how commands,
                               Model**               data and events move
                                                     through IDRM.

                            12 **Network / Packet    Defines
                               Flow & API            request/response
                               Specification**       paths, trust
                                                     boundaries, protocols
                                                     and failure behavior.

                            13 **Workflow &          Defines states,
                               State-Machine         transitions,
                               Specification**       approvals,
                                                     escalation,
                                                     exceptions and
                                                     closure.

                            14 **Database Design     Defines
                               Specification**       PostgreSQL/PostGIS
                                                     schema, indexes,
                                                     constraints,
                                                     migrations and
                                                     spatial model.

                            15 **Security & IAM      Defines identity,
                               Architecture**        authentication,
                                                     authorization,
                                                     secrets, audit and
                                                     threat controls.

                            16 **Testing & Quality   Defines unit, API,
                               Engineering           integration, E2E,
                               Strategy**            security,
                                                     accessibility,
                                                     performance and UAT.

                            17 **CI/CD &             Defines source
                               Supply-Chain          control, build, test,
                               Specification**       scan, artifact,
                                                     promotion and
                                                     rollback controls.

                            18 **Deployment &        Defines development
                               Environment           through production
                               Specification**       topology and
                                                     configuration.

                            19 **Observability &     Defines logs,
                               Monitoring            metrics, traces,
                               Specification**       SLOs, alerts and
                                                     domain-health
                                                     indicators.

                            20 **Operations, DR &    Defines failure
                               Business Continuity   handling, backup,
                               Runbook**             restore, DR,
                                                     escalation and
                                                     support.

                            21 **Roles &             Defines explicit and
                               Responsibility        implicit SDLC and
                               Catalogue**           operational roles.

                            22 **Ownership / RACI &  Establishes
                               Governance Matrix**   accountable and
                                                     responsible
                                                     ownership.

                            23 **Enterprise          Defines MVP → scale →
                               Evolution Roadmap**   federation →
                                                     intelligence →
                                                     enterprise evolution.

                            24 **Requirements        Connects
                               Traceability &        requirements, design,
                               Compliance Matrix**   implementation, tests
                                                     and evidence.

                            25 **IDRM Knowledge &    Converts the complete
                               Onboarding Handbook** system into a
                                                     structured learning
                                                     and onboarding path.
  ------------------------------------------------------------------------

------------------------------------------------------------------------

# 3. Master Documentation Flow

The requested order is retained and strengthened with two cross-cutting
documents: **Traceability & Compliance** and **Knowledge & Onboarding**.

``` mermaid
flowchart TD
    A["01 PRD"] --> B["02 Vision"]
    B --> C["03 Stakeholders"]
    C --> D["04 Business Domains"]
    D --> E["05 Disaster Lifecycle"]
    E --> F["06 System Architecture"]
    F --> G["07 Layered View"]
    G --> H["08 Functional View"]
    H --> I["09 Modules"]
    I --> J["10 Data Architecture"]
    J --> K["11 Data Flow"]
    K --> L["12 Packet / API Flow"]
    L --> M["13 Workflow / State Machines"]
    M --> N["14 Database"]
    N --> O["15 Security / IAM"]
    O --> P["16 Testing"]
    P --> Q["17 CI/CD"]
    Q --> R["18 Deployment"]
    R --> S["19 Monitoring"]
    S --> T["20 Operations / DR"]
    T --> U["21 Roles"]
    U --> V["22 Ownership / Governance"]
    V --> W["23 Enterprise Evolution"]

    X["24 Requirements Traceability & Compliance"] -.-> A
    X -.-> F
    X -.-> O
    X -.-> P
    X -.-> R
    X -.-> T

    Y["25 Knowledge & Onboarding"] -.-> C
    Y -.-> D
    Y -.-> F
    Y -.-> U
```

### Why this order works

-   **PRD → Vision** establishes the problem and direction.
-   **Stakeholders → Domains** establishes who needs what.
-   **Lifecycle → Architecture** converts operational reality into
    system structure.
-   **Functional → Modules** turns capabilities into buildable software.
-   **Data → Packet → Workflow** explains what moves, where it moves and
    how state changes.
-   **Database → Security → Testing** makes the implementation
    trustworthy.
-   **CI/CD → Deployment → Monitoring → Operations** makes it releasable
    and survivable.
-   **Roles → Ownership → Evolution** makes the system organizationally
    sustainable.

------------------------------------------------------------------------

# 4. Product & Domain Documentation

## 4.1 PRD

The PRD is the contract for **what is being built**.

Minimum sections:

-   Problem statement
-   Disaster-response problem
-   Vision
-   Goals
-   Non-goals
-   Personas
-   User journeys
-   MVP scope
-   Functional requirements
-   Non-functional requirements
-   Business rules
-   Data requirements
-   Integration requirements
-   Security requirements
-   Accessibility requirements
-   Performance requirements
-   Availability requirements
-   Acceptance criteria
-   Success metrics
-   Risks, assumptions and dependencies

### Essential rule

> **If a requirement cannot eventually be traced to a testable
> acceptance criterion, it is not yet sufficiently specified.**

------------------------------------------------------------------------

## 4.2 Vision & Product Strategy

Answers:

> **Why should IDRM exist?**

Include:

-   Mission
-   Vision
-   Strategic objectives
-   Operating principles
-   MVP philosophy
-   Future-state vision
-   Measurable outcomes
-   Explicit non-goals

The MVP should resist feature inflation.

------------------------------------------------------------------------

## 4.3 Stakeholder & Persona Catalogue

Minimum stakeholder groups:

### Command

-   Incident Commander
-   Operations Lead
-   Planning Lead
-   Logistics Lead
-   Safety Officer

### Response

-   Police
-   Fire
-   EMS
-   Search & Rescue
-   Field Responders

### Administration

-   Government / District Authority
-   Local Administration
-   Emergency Operations Centre

### Support

-   Hospitals
-   Shelters
-   NGOs
-   Utilities
-   Transport
-   Volunteers

### Public

-   Citizens
-   Information contributors

### Technology

-   Product Manager
-   Business Analyst
-   Architect
-   Developers
-   QA / SDET
-   Security
-   DevOps / SRE
-   DBA / Data Engineer
-   GIS Engineer
-   UX / Accessibility
-   Support / Operations

For every persona define:

**Goal → Responsibility → Information → Actions → Permissions → Inputs →
Outputs → Failure scenarios**

------------------------------------------------------------------------

# 5. Business Domain & Disaster Lifecycle

## 5.1 Business Capability Model

Core IDRM capabilities:

1.  Identity & Organization
2.  Incident Management
3.  Situation Awareness
4.  GIS / Common Operational Picture
5.  Tasking & Dispatch
6.  Resource & Logistics
7.  Communications
8.  Evidence & Audit
9.  Reporting & Analytics
10. Administration

``` mermaid
flowchart LR
    A["IDRM"] --> B["Identity & Organization"]
    A --> C["Incident Management"]
    A --> D["Situation Awareness / COP"]
    A --> E["GIS"]
    A --> F["Tasking & Dispatch"]
    A --> G["Resources & Logistics"]
    A --> H["Communications"]
    A --> I["Evidence & Audit"]
    A --> J["Reporting"]
    A --> K["Administration"]
```

------------------------------------------------------------------------

## 5.2 Disaster Lifecycle

``` mermaid
flowchart LR
    A["PREPARE"] --> B["DETECT"]
    B --> C["REPORT"]
    C --> D["ASSESS"]
    D --> E["ACTIVATE"]
    E --> F["RESPOND"]
    F --> G["COORDINATE"]
    G --> H["STABILIZE"]
    H --> I["RECOVER"]
    I --> J["REVIEW"]
    J --> K["LEARN"]
    K --> A
```

The MVP should have its deepest operational support in:

**Detect → Assess → Respond → Coordinate → Stabilize**

while preserving enough structure for recovery and after-action
learning.

------------------------------------------------------------------------

# 6. Architecture Documentation

## 6.1 System Architecture

The architecture document should contain:

-   Context diagram
-   Container diagram
-   Component diagram
-   Integration diagram
-   Trust-boundary diagram
-   Security boundaries
-   Failure boundaries
-   Ownership boundaries
-   Architecture principles
-   Quality attributes
-   Architecture Decision Records
-   Technology decisions
-   Failure modes

A modular monolith or small service set is sufficient for an MVP unless
scale, team autonomy, reliability or regulatory boundaries justify
further decomposition.

------------------------------------------------------------------------

## 6.2 Layered Architecture

``` mermaid
flowchart TB
    A["Experience / UI<br/>Command Dashboard • Field UI • Public Interface"]
    B["API / Gateway<br/>REST • BFF • Validation • Rate Limits"]
    C["Domain<br/>Incident • Task • Resource • GIS • Communications"]
    D["Integration<br/>Events • Notifications • External Systems"]
    E["Data<br/>PostgreSQL/PostGIS • Object Storage • Cache"]
    F["Platform<br/>Containers • CI/CD • Secrets • Observability • DR"]

    A --> B --> C --> D
    C --> E
    D --> E
    E --> F
```

------------------------------------------------------------------------

# 7. Functional Architecture

The functional chain should be:

**Capability → Function → Use Case → Actor → API → Module → Data →
Test**

``` mermaid
flowchart TD
    A["Business Capability"] --> B["Function"]
    B --> C["Use Case"]
    C --> D["Actor / Persona"]
    C --> E["API / Interface"]
    E --> F["Module"]
    F --> G["Data"]
    C --> H["Acceptance Test"]
```

This becomes a powerful bridge between business analysis and software
engineering.

------------------------------------------------------------------------

# 8. Module Documentation

Every module should use one standard template:

``` text
Purpose
Responsibilities
Actors
Inputs
Outputs
APIs
Events
Database Entities
Business Rules
Security Rules
Failure Modes
Dependencies
Tests
Metrics
Owner
```

Recommended MVP modules:

-   IAM & Organizations
-   Incident & Case
-   GIS / COP
-   Tasking & Dispatch
-   Resources & Logistics
-   Communications & Notifications
-   Evidence & Audit
-   Reports & Analytics
-   Administration

------------------------------------------------------------------------

# 9. Data Architecture

## 9.1 Minimum Domain Model

``` mermaid
erDiagram
    ORGANIZATION ||--o{ USER : contains
    USER }o--o{ ROLE : has
    ORGANIZATION ||--o{ INCIDENT : owns
    INCIDENT ||--o{ INCIDENT_LOCATION : occurs_at
    INCIDENT ||--o{ TASK : generates
    TASK }o--o{ RESOURCE : uses
    RESOURCE ||--o{ ALLOCATION : receives
    INCIDENT ||--o{ MESSAGE : generates
    INCIDENT ||--o{ ATTACHMENT : contains
    INCIDENT ||--o{ AUDIT_EVENT : produces
```

Core entities:

-   Organization
-   User
-   Role
-   Incident
-   IncidentLocation
-   Task
-   Resource
-   Allocation
-   Message
-   Attachment
-   AuditEvent
-   Plan
-   Template

------------------------------------------------------------------------

# 10. Data Flow

The canonical IDRM data path is:

``` mermaid
flowchart LR
    A["Source"] --> B["Ingest"]
    B --> C["Validate"]
    C --> D["Authenticate"]
    D --> E["Authorize"]
    E --> F["Persist"]
    F --> G["Publish Event"]
    G --> H["Project / Notify / Analyze"]
    F --> I["Audit"]
```

Important cross-cutting mechanisms:

-   Correlation IDs
-   Request IDs
-   Idempotency keys
-   Event versioning
-   Retry policy
-   Dead-letter handling
-   Data freshness
-   Provenance

------------------------------------------------------------------------

# 11. Packet / API Flow

``` mermaid
sequenceDiagram
    participant U as User / Field UI
    participant G as Gateway / WAF
    participant A as API / BFF
    participant D as Domain
    participant DB as PostgreSQL/PostGIS
    participant E as Event Bus
    participant N as Notification / GIS

    U->>G: HTTPS request
    G->>A: Authenticated request
    A->>D: Authorized command
    D->>DB: Transaction
    DB-->>D: Result
    D->>E: Domain event
    E->>N: Notification / projection
    D-->>A: Response
    A-->>U: Result + correlation ID
```

Every critical request should define:

-   Protocol
-   Endpoint
-   Authentication
-   Authorization
-   Request schema
-   Response schema
-   Errors
-   Timeout
-   Retry
-   Idempotency
-   Logging
-   Tracing
-   Rate limiting

------------------------------------------------------------------------

# 12. Workflow & State Machines

State transitions are **business rules**, not merely UI behavior.

## Incident

``` mermaid
stateDiagram-v2
    [*] --> NEW
    NEW --> TRIAGED
    TRIAGED --> ACTIVE
    ACTIVE --> STABILIZING
    STABILIZING --> RESOLVED
    RESOLVED --> CLOSED
    TRIAGED --> ACTIVE
    ACTIVE --> RESOLVED
```

## Task

``` mermaid
stateDiagram-v2
    [*] --> CREATED
    CREATED --> ASSIGNED
    ASSIGNED --> ACKNOWLEDGED
    ACKNOWLEDGED --> IN_PROGRESS
    IN_PROGRESS --> VERIFIED
    VERIFIED --> CLOSED

    ASSIGNED --> CANCELLED
    ACKNOWLEDGED --> EXPIRED
```

For every transition document:

**Who → condition → data change → event → notification → audit record**

------------------------------------------------------------------------

# 13. Database Design

For PostgreSQL/PostGIS:

-   ERD
-   Schema
-   Constraints
-   Indexes
-   Spatial indexes
-   Transactions
-   Locking / concurrency
-   Migration strategy
-   Seed data
-   Backup
-   Restore
-   Retention
-   Spatial reference system
-   Data quality

Attachments should normally be stored in object storage, with metadata,
hashes, classification and retention information in the database.

------------------------------------------------------------------------

# 14. Security & IAM

Security must be a standalone architecture concern.

``` mermaid
flowchart TD
    A["Identity"] --> B["Authentication"]
    B --> C["Session / Token"]
    C --> D["Authorization"]
    D --> E["Policy Evaluation"]
    E --> F["Action"]
    F --> G["Audit"]
```

Minimum controls:

-   OIDC
-   OAuth 2.1 + PKCE
-   MFA
-   RBAC
-   Contextual authorization
-   Organization boundaries
-   Secrets management
-   Encryption
-   Key management
-   Audit
-   Threat modelling
-   Abuse cases
-   Secure SDLC
-   Vulnerability management

Current identity guidance should be based on NIST SP 800-63-4 and SP
800-63B-4 rather than older editions.

------------------------------------------------------------------------

# 15. Testing & Quality Engineering

The testing pyramid:

``` mermaid
flowchart TB
    A["UAT / Operational Drill"]
    B["End-to-End"]
    C["Integration"]
    D["API / Contract"]
    E["Unit"]

    E --> D --> C --> B --> A

    S["Security"]
    P["Performance"]
    R["Resilience"]
    AC["Accessibility"]
    DQ["Data Quality"]

    S -.-> A
    P -.-> A
    R -.-> A
    AC -.-> A
    DQ -.-> A
```

The governing principle is:

> **Test operational scenarios, not merely individual functions.**

Example:

**Flood report → triage → commander → task → responder acknowledgement →
resource allocation → field update → resolution → audit → report.**

------------------------------------------------------------------------

# 16. CI/CD

``` mermaid
flowchart LR
    A["Commit"] --> B["Lint / Unit Test"]
    B --> C["SAST / SCA"]
    C --> D["Build"]
    D --> E["SBOM / Artifact Scan"]
    E --> F["Integration Tests"]
    F --> G["Staging"]
    G --> H["E2E / UAT"]
    H --> I["Approval"]
    I --> J["Production"]
```

Controls should include:

-   Protected main branch
-   Dependency pinning
-   SAST
-   SCA
-   SBOM
-   Container scanning
-   Artifact provenance
-   Secrets protection
-   Migration testing
-   Rollback strategy

------------------------------------------------------------------------

# 17. Deployment

Minimum environments:

``` mermaid
flowchart LR
    A["LOCAL"] --> B["DEV"]
    B --> C["TEST"]
    C --> D["STAGING"]
    D --> E["PRODUCTION"]
```

Each environment needs documented:

-   Network
-   DNS
-   TLS
-   Secrets
-   Database
-   Storage
-   Containers
-   Scaling
-   Configuration
-   Deployment strategy
-   Rollback

------------------------------------------------------------------------

# 18. Observability & Monitoring

Technical observability:

**Logs + Metrics + Traces**

IDRM domain observability should additionally measure:

-   Active incidents
-   Critical incidents
-   Unacknowledged tasks
-   Overdue tasks
-   Responder availability
-   Resource shortages
-   Notification failures
-   GIS freshness
-   Integration failures
-   Resolution time

``` mermaid
flowchart TD
    A["Telemetry"] --> B["Logs"]
    A --> C["Metrics"]
    A --> D["Traces"]
    A --> E["Domain Events"]

    B --> F["Observability Platform"]
    C --> F
    D --> F
    E --> F

    F --> G["Dashboard"]
    F --> H["Alert"]
    H --> I["Incident Response"]
```

------------------------------------------------------------------------

# 19. Operations, DR & Business Continuity

IDRM must be able to survive disruption to itself.

Minimum runbooks:

1.  Application outage
2.  Database outage
3.  GIS outage
4.  Notification outage
5.  Authentication outage
6.  Integration outage
7.  Data corruption
8.  Cybersecurity incident
9.  Backup failure
10. Disaster recovery
11. Credential compromise
12. Major incident escalation

Define:

**RTO + RPO + backup policy + restore procedure + DR test procedure**

------------------------------------------------------------------------

# 20. Roles & Responsibilities

The role catalogue should cover:

### Product

-   Product Manager
-   Product Owner
-   Business Analyst

### Architecture

-   Solution Architect
-   Application Architect
-   Data Architect
-   Security Architect
-   Integration Architect

### Engineering

-   Backend Developer
-   Frontend Developer
-   Full-Stack Developer
-   GIS Engineer
-   Data Engineer
-   Integration Engineer

### Quality

-   QA Engineer
-   SDET
-   Performance Engineer
-   Security Tester
-   Accessibility Tester

### Platform

-   DevOps Engineer
-   SRE
-   Cloud Engineer
-   DBA

### Operations

-   Incident Manager
-   Service Manager
-   Support Engineer
-   DR Coordinator

### Governance

-   Security Officer
-   Privacy / Data Governance
-   Compliance
-   Risk
-   Audit

### Domain

-   Incident Commander
-   Operations
-   Planning
-   Logistics
-   Field Responder

------------------------------------------------------------------------

# 21. Ownership & Governance

The rule should be:

> **Every critical capability has exactly one Accountable owner.**

Example:

  ---------------------------------------------------------------------------
  Capability     Accountable    Responsible     Consulted      Evidence
  -------------- -------------- --------------- -------------- --------------
  Incident       Product /      Engineering +   Security + Ops PRD + tests +
  lifecycle      Domain         QA                             audit

  IAM            Security       Platform        Product +      Access reviews
                                                Domain         

  GIS / COP      Domain         GIS / Data      Ops + UX       Layer
                                                               catalogue +
                                                               freshness

  Tasking        Domain         Engineering     QA + Ops       Workflow tests

  Deployment     SRE            DevOps          Security + QA  Pipeline +
                                                               artifact

  DR             SRE            Platform        Security +     Restore drill
                                                Product        
  ---------------------------------------------------------------------------

------------------------------------------------------------------------

# 22. Requirements Traceability & Compliance

This is the **audit spine** of the project.

``` mermaid
flowchart LR
    A["Business Need"] --> B["Requirement"]
    B --> C["Design"]
    C --> D["Implementation"]
    D --> E["Test"]
    E --> F["Evidence"]
    F --> G["Release"]
    G --> H["Operational Evidence"]
```

Maintain links between:

-   Requirement IDs
-   Architecture decisions
-   Design elements
-   Source modules
-   API contracts
-   Database entities
-   Test cases
-   Security controls
-   Release versions
-   Evidence

------------------------------------------------------------------------

# 23. Enterprise Evolution

``` mermaid
flowchart LR
    A["MVP"] --> B["Scale"]
    B --> C["Multi-Agency"]
    C --> D["Federated Ecosystem"]
    D --> E["Decision Support"]
    E --> F["Predictive / Optimization"]
    F --> G["Enterprise Resilience Platform"]
```

Evolution principle:

> **Do not build the enterprise platform inside the MVP. Build the seams
> that allow the enterprise platform to emerge.**

------------------------------------------------------------------------

# 24. Role-Mastery Framework

Every role should follow the same maturity pattern:

``` mermaid
flowchart TD
    A["Complete Novice"] --> B["IDRM Orientation"]
    B --> C["Domain Literacy"]
    C --> D["Role Fundamentals"]
    D --> E["Tools & Technology"]
    E --> F["Guided Tasks"]
    F --> G["Independent Tasks"]
    G --> H["Cross-Functional Work"]
    H --> I["Production Responsibility"]
    I --> J["Failure / Incident Handling"]
    J --> K["Design / Review"]
    K --> L["Mentor Others"]
    L --> M["Mastery"]
```

**Mastery is demonstrated by capability, not by course completion.**

------------------------------------------------------------------------

# 25. Role-Specific Mastery Maps

## 25.1 Product Manager / Product Owner

``` mermaid
flowchart LR
    A["Software Basics"] --> B["Disaster Management"]
    B --> C["IDRM Vision"]
    C --> D["Stakeholders"]
    D --> E["Domains"]
    E --> F["Personas / Journeys"]
    F --> G["PRD"]
    G --> H["Prioritization"]
    H --> I["Acceptance Criteria"]
    I --> J["Metrics"]
    J --> K["Operational Drills"]
    K --> L["Product Strategy"]
    L --> M["Mastery"]
```

**Mastery test:** Can explain what problem IDRM solves, for whom, why,
what should be built next and how success will be measured.

------------------------------------------------------------------------

## 25.2 Business Analyst / Domain Analyst

``` mermaid
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

**Mastery test:** Converts ambiguous operational problems into precise,
testable requirements.

------------------------------------------------------------------------

## 25.3 Solution / Software Architect

``` mermaid
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

------------------------------------------------------------------------

## 25.4 Backend Engineer

``` mermaid
flowchart LR
    A["Programming"] --> B["HTTP / REST"]
    B --> C["API Design"]
    C --> D["IDRM Domain"]
    D --> E["Domain Model"]
    E --> F["Database"]
    F --> G["Transactions"]
    G --> H["AuthN / AuthZ"]
    H --> I["Events"]
    I --> J["Testing"]
    J --> K["Observability"]
    K --> L["Production Debugging"]
    L --> M["Mastery"]
```

------------------------------------------------------------------------

## 25.5 Frontend Engineer

``` mermaid
flowchart LR
    A["HTML / CSS"] --> B["JavaScript"]
    B --> C["TypeScript"]
    C --> D["React"]
    D --> E["API Integration"]
    E --> F["Authentication"]
    F --> G["GIS / COP"]
    G --> H["Accessibility"]
    H --> I["State / Error Handling"]
    I --> J["Offline UX"]
    J --> K["E2E Testing"]
    K --> L["Mastery"]
```

------------------------------------------------------------------------

## 25.6 GIS / Geospatial Engineer

``` mermaid
flowchart LR
    A["Maps"] --> B["Coordinates / CRS"]
    B --> C["GeoJSON"]
    C --> D["Spatial Data"]
    D --> E["PostGIS"]
    E --> F["Spatial Queries"]
    F --> G["GeoServer"]
    G --> H["Map Layers"]
    H --> I["Incident Geolocation"]
    I --> J["Spatial Analysis"]
    J --> K["COP"]
    K --> L["Mastery"]
```

------------------------------------------------------------------------

## 25.7 QA / SDET

``` mermaid
flowchart LR
    A["Testing Fundamentals"] --> B["IDRM Requirements"]
    B --> C["Use Cases"]
    C --> D["Test Design"]
    D --> E["API Testing"]
    E --> F["Database Testing"]
    F --> G["Automation"]
    G --> H["Integration"]
    H --> I["E2E"]
    I --> J["Security"]
    J --> K["Performance"]
    K --> L["Resilience"]
    L --> M["Disaster Drills"]
    M --> N["Mastery"]
```

------------------------------------------------------------------------

## 25.8 Security Engineer

``` mermaid
flowchart LR
    A["Networking"] --> B["Web Security"]
    B --> C["Cryptography"]
    C --> D["IAM"]
    D --> E["OIDC"]
    E --> F["OAuth 2.1 + PKCE"]
    F --> G["MFA"]
    G --> H["RBAC / ABAC"]
    H --> I["Threat Modeling"]
    I --> J["Secure SDLC"]
    J --> K["Application Security"]
    K --> L["Cloud Security"]
    L --> M["Response"]
    M --> N["Mastery"]
```

------------------------------------------------------------------------

## 25.9 DevOps / SRE

``` mermaid
flowchart LR
    A["Linux"] --> B["Git"]
    B --> C["Networking"]
    C --> D["Containers"]
    D --> E["CI/CD"]
    E --> F["Infrastructure"]
    F --> G["Secrets"]
    G --> H["Deployment"]
    H --> I["Logging / Metrics / Traces"]
    I --> J["SLOs"]
    J --> K["Incident Response"]
    K --> L["Backup / Restore"]
    L --> M["DR"]
    M --> N["Reliability"]
    N --> O["Mastery"]
```

------------------------------------------------------------------------

## 25.10 Data Engineer

``` mermaid
flowchart LR
    A["SQL"] --> B["Relational Modeling"]
    B --> C["PostgreSQL"]
    C --> D["Data Quality"]
    D --> E["ETL / ELT"]
    E --> F["GIS Data"]
    F --> G["Events"]
    G --> H["Lineage"]
    H --> I["Governance"]
    I --> J["Analytics"]
    J --> K["Operational Data"]
    K --> L["Data Platform"]
    L --> M["Mastery"]
```

------------------------------------------------------------------------

## 25.11 Incident / Operations Manager

``` mermaid
flowchart LR
    A["Disaster Management"] --> B["Incident Lifecycle"]
    B --> C["IDRM"]
    C --> D["Incident Roles"]
    D --> E["COP"]
    E --> F["Assessment"]
    F --> G["Command"]
    G --> H["Tasking"]
    H --> I["Resource Allocation"]
    I --> J["Communication"]
    J --> K["Escalation"]
    K --> L["Closure"]
    L --> M["After-Action Review"]
    M --> N["Leadership"]
    N --> O["Mastery"]
```

------------------------------------------------------------------------

## 25.12 Technical / Application Support

``` mermaid
flowchart LR
    A["IDRM Orientation"] --> B["Architecture"]
    B --> C["IAM"]
    C --> D["Logs"]
    D --> E["Dashboards"]
    E --> F["Common Failures"]
    F --> G["Runbooks"]
    G --> H["Incident Triage"]
    H --> I["Escalation"]
    I --> J["Recovery"]
    J --> K["RCA"]
    K --> L["Problem Management"]
    L --> M["Mastery"]
```

------------------------------------------------------------------------

# 26. The Universal IDRM Operational Flow

Regardless of job role, every IDRM professional should eventually
understand the following end-to-end journey:

``` mermaid
flowchart TD
    A["Citizen / Source"] --> B["Report"]
    B --> C["Incident"]
    C --> D["Command"]
    D --> E["Task"]
    D --> F["Resource"]
    E --> G["Responder"]
    F --> G
    G --> H["Field Update"]
    H --> I["Resolution"]
    I --> J["Audit"]
    J --> K["After-Action Review"]
    K --> L["Learning"]
    L --> A
```

This is the **common mental model** across the organization.

Specialists then descend into their own branch.

------------------------------------------------------------------------

# 27. Supplementary Guide Library

The core documents should be supported by concise **101 / intermediate /
advanced guides**.

## IDRM Domain Guides

1.  Disaster Management 101
2.  Incident Management 101
3.  Emergency Operations Centre 101
4.  Common Operational Picture 101
5.  GIS for Emergency Response
6.  Resource Management 101
7.  Emergency Communications 101
8.  Incident Command 101

## Software Engineering Guides

9.  SDLC 101
10. Git / GitHub 101
11. REST API 101
12. Database 101
13. PostgreSQL / PostGIS 101
14. Event-Driven Architecture 101
15. Docker 101
16. CI/CD 101
17. Observability 101

## Security Guides

18. IAM 101
19. OIDC 101
20. OAuth 2.1 + PKCE 101
21. MFA 101
22. RBAC / ABAC 101
23. Threat Modeling 101
24. Secure Coding 101

## Quality Guides

25. Testing 101
26. API Testing 101
27. E2E Testing 101
28. Performance Testing 101
29. Security Testing 101
30. Accessibility Testing 101
31. Disaster Drill / Scenario Testing 101

## Operations Guides

32. Linux 101
33. Networking 101
34. Cloud 101
35. Monitoring 101
36. Incident Response 101
37. Backup & Restore 101
38. Disaster Recovery 101
39. SRE 101

------------------------------------------------------------------------

# 28. New-Joinee Reading Path

Do not hand a new employee all 25 documents simultaneously.

Use progressive disclosure:

``` mermaid
flowchart TD
    A["IDRM Orientation"] --> B["Vision"]
    B --> C["Stakeholders"]
    C --> D["Disaster Lifecycle"]
    D --> E["Business Domains"]
    E --> F["Operational Flow"]
    F --> G["Architecture Overview"]
    G --> H["Security Overview"]
    H --> I["My Role"]
    I --> J["My Responsibilities"]
    J --> K["My Tools"]
    K --> L["My Module"]
    L --> M["My Workflows"]
    M --> N["My APIs / Data"]
    N --> O["My Tests"]
    O --> P["My Deployment"]
    P --> Q["My Runbooks"]
    Q --> R["Shadow"]
    R --> S["Guided Work"]
    S --> T["Independent Work"]
    T --> U["Production Responsibility"]
    U --> V["Mentor"]
    V --> W["Mastery"]
```

------------------------------------------------------------------------

# 29. Reading Pyramid

``` mermaid
flowchart TD
    A["Fundamentals"] --> B["Role Skills"]
    B --> C["IDRM Domain Knowledge"]
    C --> D["Professional Practice"]
    D --> E["Architecture / Standards / Design"]
    E --> F["Mastery"]
```

This avoids a common failure mode: asking a beginner to read advanced
architecture documents before understanding the operational problem.

------------------------------------------------------------------------

# 30. Authoritative Reading Directions

The reading list should be curated by topic rather than becoming an
uncontrolled library.

### Disaster Management / Incident Management

Use **ISO 22320:2018** as an important reference for incident-management
processes, structures, roles/responsibilities, resource management and
cooperation. Confirm jurisdiction-specific applicability before treating
it as a compliance requirement.

Use **NIMS** as a useful reference model for shared terminology, systems
and processes across participating organizations.

### Cybersecurity

Use **NIST CSF 2.0** for cybersecurity risk management and
communication.

### Digital Identity

Use the current **NIST SP 800-63-4** family, including **SP 800-63B-4**
for authentication.

### Accessibility

Use **W3C WCAG 2.2** as the primary accessibility reference.

The documentation should distinguish:

**reference → alignment → implementation requirement → verification →
formal certification**, because merely citing a standard does not
establish compliance.

------------------------------------------------------------------------

# 31. Recommended Repository Structure

``` text
docs/
├── 01-product/
├── 02-domain/
├── 03-architecture/
│   └── adr/
├── 04-data/
├── 05-integration/
├── 06-workflows/
├── 07-security/
├── 08-quality/
├── 09-devops/
├── 10-operations/
├── 11-governance/
├── 12-onboarding/
│   ├── role-maps/
│   ├── learning-paths/
│   └── mastery-checklists/
└── 13-evolution/
```

A useful convention is to keep document identifiers aligned with this
structure:

``` text
01-PRD
02-VISION
03-STAKEHOLDERS
04-DOMAINS
...
24-TRACEABILITY
25-ONBOARDING
```

------------------------------------------------------------------------

# 32. Definition of Documentation Done

A document should not be considered complete merely because it exists.

A document is **Done** when:

-   Purpose is explicit.
-   Scope is explicit.
-   Owner is identified.
-   Inputs are identified.
-   Outputs are identified.
-   Dependencies are identified.
-   Terminology is consistent.
-   Diagrams agree with text.
-   Requirements are traceable.
-   Security implications are addressed.
-   Accessibility implications are addressed where relevant.
-   Operational consequences are documented.
-   Test implications are identified.
-   Version/history is maintained.
-   Relevant stakeholders have reviewed it.

------------------------------------------------------------------------

# Appendix A --- IDRM Diagram Catalogue

The diagram numbering convention is:

> **`XX-YY-ZZ` = Chapter → Section → Sub-section**

For example:

**`06-02-01`** = Architecture chapter → Layered Architecture section →
Layer diagram.

The numbering is deliberately semantic rather than sequential so
diagrams remain stable when new diagrams are inserted.

  -----------------------------------------------------------------------
  Diagram ID              Diagram                 Brief elucidation
  ----------------------- ----------------------- -----------------------
  **00-01-01**            IDRM Documentation      Shows how business
                          Knowledge Graph         needs become
                                                  requirements,
                                                  implementation,
                                                  evidence and learning.

  **01-01-01**            PRD Requirement Chain   Requirement → use case
                                                  → acceptance criterion
                                                  → evidence.

  **02-01-01**            IDRM Strategic North    Vision → outcomes → MVP
                          Star                    → enterprise evolution.

  **03-01-01**            Stakeholder Ecosystem   Command, responders,
                                                  government, support,
                                                  public and technology
                                                  participants.

  **04-01-01**            Business Capability Map Major IDRM business
                                                  capabilities.

  **04-02-01**            Core Domain Model       Incident, location,
                                                  task, resource,
                                                  communication and
                                                  evidence relationships.

  **05-01-01**            Disaster Lifecycle      Prepare → detect →
                                                  assess → respond →
                                                  stabilize → recover →
                                                  learn.

  **06-01-01**            System Context          IDRM and its external
                                                  actors/systems.

  **06-02-01**            Layered Architecture    Experience → API →
                                                  domain → integration →
                                                  data → platform.

  **06-03-01**            Trust Boundaries        Public, edge,
                                                  application and
                                                  data/security
                                                  boundaries.

  **07-01-01**            Functional              Capability → function →
                          Decomposition           use case → actor → API
                                                  → module.

  **08-01-01**            Module Dependency View  Relationships and
                                                  boundaries between MVP
                                                  modules.

  **09-01-01**            Data Architecture       Canonical entities and
                                                  ownership.

  **10-01-01**            Data Flow               Source → ingest →
                                                  validate → authorize →
                                                  persist → publish →
                                                  consume.

  **10-02-01**            Event Flow              Domain event
                                                  propagation to
                                                  projections,
                                                  notifications and
                                                  analytics.

  **11-01-01**            Packet / Request Flow   UI → gateway → API →
                                                  domain → database →
                                                  event → downstream
                                                  systems.

  **11-02-01**            API Sequence            Request/response and
                                                  downstream interaction
                                                  sequence.

  **12-01-01**            Incident State Machine  NEW → TRIAGED → ACTIVE
                                                  → STABILIZING →
                                                  RESOLVED → CLOSED.

  **12-02-01**            Task State Machine      CREATED → ASSIGNED →
                                                  ACKNOWLEDGED →
                                                  IN_PROGRESS → VERIFIED
                                                  → CLOSED.

  **12-03-01**            Resource Allocation     Need → identify
                          Flow                    resource → allocate →
                                                  move → arrive →
                                                  release.

  **13-01-01**            IDRM ERD                Core PostgreSQL/PostGIS
                                                  entity relationships.

  **14-01-01**            IAM Flow                Identity →
                                                  authentication →
                                                  token/session →
                                                  authorization → policy
                                                  → action → audit.

  **14-02-01**            Security Boundary Map   Public, edge,
                                                  application, data and
                                                  operations trust zones.

  **15-01-01**            Testing Pyramid         Unit → contract/API →
                                                  integration → E2E →
                                                  UAT/drill.

  **15-02-01**            Quality Cross-Cutting   Security, performance,
                          Model                   accessibility,
                                                  resilience and data
                                                  quality.

  **16-01-01**            CI/CD Pipeline          Commit → test → scan →
                                                  build → artifact →
                                                  staging → UAT →
                                                  production.

  **17-01-01**            Environment Promotion   Local → Dev → Test →
                                                  Staging → Production.

  **18-01-01**            Observability Model     Logs + metrics +
                                                  traces + domain events
                                                  → dashboards/alerts.

  **19-01-01**            Operations Lifecycle    Detect → triage →
                                                  mitigate → recover →
                                                  review → improve.

  **19-02-01**            DR Architecture         Primary → backup →
                                                  restore → alternate
                                                  failure domain →
                                                  recovery.

  **20-01-01**            SDLC Role Map           Product → analysis →
                                                  architecture →
                                                  engineering → quality →
                                                  operations.

  **21-01-01**            RACI Model              Accountable,
                                                  responsible, consulted
                                                  and informed ownership.

  **22-01-01**            Enterprise Evolution    MVP → scale →
                                                  multi-agency →
                                                  federation → decision
                                                  support → enterprise.

  **23-01-01**            Requirements            Need → requirement →
                          Traceability            design → code → test →
                                                  evidence → release.

  **24-01-01**            New-Joinee Learning     Orientation → domain →
                          Path                    role → guided work →
                                                  independent work →
                                                  mastery.

  **24-02-01**            Universal Role-Mastery  Novice → fundamentals →
                          Model                   guided → independent →
                                                  production → mentor →
                                                  master.

  **24-03-01**            Product Mastery Map     Product-specific
                                                  learning progression.

  **24-03-02**            BA / Domain Mastery Map Requirements and
                                                  process-analysis
                                                  progression.

  **24-03-03**            Architect Mastery Map   Architecture and
                                                  decision-making
                                                  progression.

  **24-03-04**            Backend Mastery Map     Programming → APIs →
                                                  data → security →
                                                  production.

  **24-03-05**            Frontend Mastery Map    Web → React → API → GIS
                                                  → accessibility →
                                                  operational UX.

  **24-03-06**            GIS Mastery Map         Maps → CRS → GeoJSON →
                                                  PostGIS → GeoServer →
                                                  COP.

  **24-03-07**            QA/SDET Mastery Map     Test design →
                                                  automation → E2E →
                                                  security → resilience →
                                                  drills.

  **24-03-08**            Security Mastery Map    Networking → IAM →
                                                  identity →
                                                  authorization → threat
                                                  modelling → response.

  **24-03-09**            DevOps/SRE Mastery Map  Linux → Git →
                                                  containers → CI/CD →
                                                  observability → DR →
                                                  reliability.

  **24-03-10**            Data Engineer Mastery   SQL → PostgreSQL → GIS
                          Map                     → pipelines →
                                                  governance → data
                                                  platform.

  **24-03-11**            Incident Manager        Disaster management →
                          Mastery Map             command → coordination
                                                  → closure → AAR.

  **24-03-12**            Support Mastery Map     Architecture →
                                                  diagnostics → runbooks
                                                  → incident response →
                                                  RCA.

  **25-01-01**            Universal IDRM          Report → incident →
                          Operational Flow        command → task/resource
                                                  → responder →
                                                  resolution → audit →
                                                  learning.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# Appendix B --- Diagram Design Rules

Every IDRM diagram should follow these rules:

1.  **One diagram = one primary idea.**
2.  Direction of flow must be visually obvious.
3.  Avoid decorative arrows.
4.  Avoid crossing connectors wherever possible.
5.  Use the same terminology as the PRD and domain model.
6.  Use consistent identifiers such as `06-02-01`.
7.  Never communicate meaning through color alone.
8.  Include a legend when symbols have specialized meaning.
9.  Keep diagrams readable at normal presentation/document zoom.
10. Prefer Mermaid source for architecture and workflow diagrams so they
    remain version-controlled.
11. Keep source diagrams alongside their rendered versions where
    practical.
12. Validate every diagram against the corresponding text and
    implementation.

------------------------------------------------------------------------

# Appendix C --- The Ultimate IDRM Mental Model

The entire IDRM MVP can ultimately be reduced to:

``` mermaid
flowchart TD
    A["SENSE"] --> B["UNDERSTAND"]
    B --> C["DECIDE"]
    C --> D["COORDINATE"]
    D --> E["ACT"]
    E --> F["VERIFY"]
    F --> G["RECORD"]
    G --> H["LEARN"]
    H --> A
```

Or, operationally:

> **Sense → Decide → Coordinate → Act → Verify → Record → Learn**

That is the conceptual spine connecting the **PRD, architecture,
workflows, data, security, testing, operations, roles and enterprise
evolution** of IDRM.

------------------------------------------------------------------------

## Appendix D --- Recommended Reading Sequence

For a complete novice:

1.  **IDRM 101**
2.  **Disaster Management 101**
3.  **Incident Lifecycle**
4.  **Stakeholders & Roles**
5.  **IDRM Business Domains**
6.  **System Architecture 101**
7.  **Security & IAM 101**
8.  **Role-specific fundamentals**
9.  **Role-specific tools**
10. **IDRM module documentation**
11. **Operational workflows**
12. **Testing / deployment / monitoring**
13. **Runbooks**
14. **Standards and advanced design**
15. **Scenario drills**
16. **Mentoring and design reviews**

The objective is not to make everyone a generalist.

The objective is:

> **Broad IDRM literacy + deep role expertise + enough cross-functional
> understanding to operate safely as one system.**

------------------------------------------------------------------------

## Closing Principle

> **IDRM documentation is successful when a new person can enter the
> organization, understand the mission, understand the system,
> understand their role, perform useful work safely, respond to failure,
> and eventually improve and teach the system --- without depending on
> tribal knowledge.**
