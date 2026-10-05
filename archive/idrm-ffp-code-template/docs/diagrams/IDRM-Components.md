# IDRM Components Diagram

## Entity Classes Organized by Domain

**Source**: DRM_components.png
**Type**: Domain Subgraph Diagram (SOLID design with Separation of Concerns)
**Version**: 3.0
**Purpose**: Shows all entity classes organized by functional domain

---

> ⚠️ **Full-system component map (MVP vs Post-MVP).** This shows the complete planned class landscape. Several domains are **🔒 Post-MVP** — Content & Communication (ChatBot, Blog, Article), the finance pieces of Team & Visibility (Charity, Pooling, Grants, SevaCard), and the MAD\* classes (Misuse/Abuse/Discrepancy). The **MVP core**: Auth & IAM, Roles & Permissions, Service requests/providers, Geo/Search, Session Management, Notifications. Canonical roles: `docs/development/IDRM-FS.md` §3.3.

```mermaid
graph TD

    subgraph SG1["Core System"]
        DrmWiz --> Dashboards
        Dashboards --- OpsMode
        OpsMode --- PoliceD
        PoliceD --- MADAlerts
        MADAlerts --- MADHandling
        MADHandling --- MADBlacklists
        MADBlacklists --- MADWhitelists
        MADWhitelists --- DrmNotes
    end

    subgraph SG2["Annotation & Validation"]
        DRDAnnotator --> Services
        Services --- Validators
        Validators --- Providers
        Providers --- Requestors
        Requestors --- ReVV
        ReVV --- AnnotatorNotes
        AnnotatorNotes --- MLOps
        MLOps --- HealthMon
        HealthMon --- DevSecOps
        DevSecOps --- ConfigNotes
    end

    subgraph SG3["Team & Visibility"]
        TeamVis --> LocationAlerts
        LocationAlerts --- LiveTracking
        LiveTracking --- TeamNotify
        TeamNotify --- Charity
        Charity --- Pooling
        Pooling --- Grants
        Grants --- SevaCard
        SevaCard --- eServing
        eServing --- CharityNotes
    end

    subgraph SG4["Search & Discovery"]
        Search --> Filters
        Filters --- ServiceType
        ServiceType --- ServiceID
        ServiceID --- LocationSvc["Location"]
        LocationSvc --- Contextual
        Contextual --- Tagging
        Tagging --- Trending
        Trending --- Carousel
        Carousel --- Bookmarks
        Bookmarks --- SearchNotes
    end

    subgraph SG5["Content & Communication"]
        ChatBot --> Blog
        Blog --- Article
        Article --- Feedback
        Feedback --- IIntegrations
        IIntegrations --- MDValidator
        MDValidator --- MDEditor
        MDEditor --- InfoNotes
    end

    subgraph SG6["Scheduling & Tasks"]
        Scheduler --> EvtSch["Event"]
        EvtSch --- TaskNode["Task"]
        TaskNode --- SubTask
        SubTask --- CollabNotes
        CollabNotes --- Notifications
        Notifications --- Escalations
        Escalations --- Grievances
        Grievances --- Pending
        Pending --- ActNotes
    end

    subgraph SG7["Authentication & IAM"]
        IAMAA --> SignUp
        SignUp --- SignIn
        SignIn --- PrivacyPP
        PrivacyPP --- MFA
        MFA --- OAuthNode["OAuth"]
        OAuthNode --- JWT
        JWT --- OTP
        OTP --- Biometric
        Biometric --- EPA
        EPA --- IAMAANotes
    end

    subgraph SG8["Roles & Permissions"]
        Roles --> Public
        Public --- Citizen
        Citizen --- Volunteer
        Volunteer --- Organizer
        Organizer --- Provider
        Provider --- Manager
        Manager --- EventManager
        EventManager --- Executive
        Executive --- DMAuthority
        DMAuthority --- Auditor
        Auditor --- SysAdmin
        SysAdmin --- RolesNotes
    end

    subgraph SG9["Session Management"]
        SessionMgmt --> CookieMgmt
        CookieMgmt --- SessionMapping
        SessionMapping --- Blacklisting
        Blacklisting --- SessionSuspend
        SessionSuspend --- SessionNotes
        SessionNotes --- Ratings
        Ratings --- Credibility
        Credibility --- Transparency
        Transparency --- RatingNotes
    end
```

> `-->` = representative relationship within domain · `---` = domain membership (structural grouping only)
> Node aliases used for parser safety: `Location` → `LocationSvc`, `Event` → `EvtSch`, `Task` → `TaskNode`, `OAuth` → `OAuthNode`
> Full class descriptions: see Domain Summary table below.

---

## Domain Summary

| Domain                  | Classes                                             | Purpose                              |
| ----------------------- | --------------------------------------------------- | ------------------------------------ |
| Core System             | DrmWiz, Dashboards, OpsMode, PoliceD, MAD*          | Operations center, alert management  |
| Annotation & Validation | DRDAnnotator, Services, Validators, Providers       | Data quality, service routing        |
| Team & Visibility       | TeamVis, LocationAlerts, LiveTracking, Charity      | Field coordination, resource pooling |
| Search & Discovery      | Search, Filters, ServiceType, Location, Trending    | Finding services and providers       |
| Content & Communication | ChatBot, Blog, Article, Feedback                    | Information and engagement           |
| Scheduling & Tasks      | Scheduler, Event, Task, Notifications, Escalations  | Workflow and alerting                |
| Authentication & IAM    | IAMAA, SignUp, SignIn, MFA, OAuth, JWT              | Identity and access                  |
| Roles & Permissions     | Public, Citizen, Volunteer, Organizer, Provider, Manager, EventManager, Executive (🔒), DM Authority, Auditor, SysAdmin | RBAC (canonical: FS §3.3) |
| Session Management      | SessionMgmt, CookieMgmt, Blacklisting, Credibility  | Session lifecycle                    |

**Design principles**: SOLID, Separation of Concerns (SoC), domain-driven class grouping.
