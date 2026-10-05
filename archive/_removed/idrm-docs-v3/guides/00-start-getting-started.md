# IDRM v3 · Getting Started

<!-- IDRM-CLEANUP doc=v3-g00-getting-started status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — onboarding → current guides
> → [`../../../../guides/mvp/00-start-learning-paths.md`](../../../../guides/mvp/00-start-learning-paths.md) + the
> [`learn/`](../../../../guides/mvp/learn/README.md) library + [`roles/`](../../../../guides/mvp/roles/README.md).
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: Complete novices · Status: Archived — v3 historical generation*
*Consolidated from: 00-GETTING-STARTED.md, QUICK-REFERENCE-V3.md*

## Contents
- [IDRM: Getting Started Guide](#idrm-getting-started-guide)
- [IDRM v3 Monolith: Quick Reference Guide](#idrm-v3-monolith-quick-reference-guide)

---

## IDRM: Getting Started Guide

### Your Complete Introduction to the Platform

**Version**: 3.0 Consolidated  
**Audience**: Everyone (especially beginners)  
**Reading Time**: 30-45 minutes  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [What is IDRM?](#1-what-is-idrm)
2. [Who Should Use This Guide?](#2-who-should-use-this-guide)
3. [Quick Overview](#3-quick-overview)
4. [Understanding the Problem](#4-understanding-the-problem)
5. [How IDRM Solves It](#5-how-idrm-solves-it)
6. [Key Concepts (For Beginners)](#6-key-concepts-for-beginners)
7. [System Capabilities](#7-system-capabilities)
8. [User Roles Explained](#8-user-roles-explained)
9. [Choosing Your Path](#9-choosing-your-path)
10. [Your First Steps](#10-your-first-steps)
11. [Common Questions](#11-common-questions)
12. [What's Next?](#12-whats-next)

---

### 1. **What is IDRM?**

#### 1.1 The Simple Answer

**IDRM** stands for **Integrated Disaster Response Management Platform**.

Think of it as:
- **"Uber for disaster response"** - Connects people who need help with people who can help
- **"Google Maps for emergencies"** - Shows everything on a map in real-time
- **"Transparent donation tracker"** - See where every rupee goes

#### 1.2 The Real-World Example

**Scenario**: A flood hits a district in India.

**Without IDRM**:
- Victims call multiple numbers, repeat their story many times
- Relief organizations don't know who needs what
- Duplicate efforts (3 organizations send food to same area, nobody sends medicine)
- Donors don't know if their money was used properly
- Government can't see the full picture

**With IDRM**:
- Victim makes ONE request on a map
- All authorized responders see it instantly
- Responders coordinate (one sends food, another medicine)
- Donors see exactly where their money went
- Government dashboard shows real-time status

#### 1.3 Why It Matters

India faces **multiple disasters** every year:
- Floods, cyclones, earthquakes
- Heat waves, landslides
- Industrial accidents

Currently, **coordination is manual and slow**. IDRM makes it **digital and instant**.

**Impact**: Faster response = More lives saved

---

### 2. **Who Should Use This Guide?**

#### 2.1 You're in the Right Place If...

✅ **You're completely new** to IDRM and want to understand it  
✅ **You're a developer** starting to work on IDRM  
✅ **You're a project manager** planning IDRM implementation  
✅ **You're a decision maker** evaluating whether to use IDRM  
✅ **You're a student** learning about disaster response systems  

#### 2.2 After Reading This, You'll Understand...

- What IDRM is and why it exists
- What problems it solves
- Who uses it and how
- Whether it's right for your needs
- Where to go next based on your role

#### 2.3 Prerequisites

**To understand this guide**: None! Written for complete beginners.

**To implement IDRM**: See [01-PREREQUISITES.md](01-PREREQUISITES.md) for technical requirements.

---

### 3. **Quick Overview**

#### 3.1 IDRM in 60 Seconds

```
┌─────────────────────────────────────────────┐
│            What IDRM Does                   │
├─────────────────────────────────────────────┤
│                                             │
│  1. CONNECT                                 │
│     Citizens ↔ Service Providers            │
│     ↔ Coordinators ↔ Donors                 │
│                                             │
│  2. VISUALIZE                               │
│     Everything on an interactive map        │
│     Real-time updates                       │
│                                             │
│  3. COORDINATE                              │
│     Prevent duplication                     │
│     Track progress                          │
│     Ensure accountability                   │
│                                             │
│  4. TRACK                                   │
│     Money flows                             │
│     Service delivery                        │
│     Response times                          │
│                                             │
└─────────────────────────────────────────────┘
```

#### 3.2 Key Numbers (Target Scale)

| Metric | Value |
|--------|-------|
| **Concurrent Users** | 10,000 |
| **Monthly Active Users** | 100,000 |
| **Uptime** | 99.5% |
| **Response Time** | <2 seconds |
| **Service Providers** | 1,000+ organizations |
| **Coverage** | Pan-India |

---

### 4. **Understanding the Problem**

#### 4.1 Current State of Disaster Response

**Today's Challenges**:

1. **Fragmented Information**
   - Multiple agencies maintain separate databases
   - No single source of truth
   - Information silos

2. **Slow Coordination**
   - Manual phone calls and emails
   - Hours/days to coordinate response
   - Missed opportunities

3. **Resource Wastage**
   - Duplicate efforts (same area served twice)
   - Gaps (some areas not served at all)
   - Inefficient allocation

4. **Limited Transparency**
   - Donors don't know where money went
   - Citizens can't track their requests
   - Difficult to audit

5. **Privacy Concerns**
   - Sensitive victim data shared widely
   - No granular access control
   - Security risks

#### 4.2 The Cost of These Problems

- **Lives lost** due to delayed response
- **Money wasted** on duplicate efforts
- **Trust eroded** due to lack of transparency
- **Coordination failures** leading to chaos

#### 4.3 Why Existing Solutions Don't Work

**WhatsApp Groups**: Unstructured, not searchable, no audit trail  
**Excel Spreadsheets**: Not real-time, prone to errors, no map visualization  
**Custom Apps**: Expensive, not interoperable, vendor lock-in  

**What's Needed**: A **unified digital platform** built specifically for disaster response.

---

### 5. **How IDRM Solves It**

#### 5.1 Core Solution Components

##### **Component 1: Unified Map Interface**

All disaster response activity visualized on **one interactive map**:
- Red markers = Urgent requests
- Yellow markers = In-progress
- Green markers = Completed
- Blue areas = Disaster zones

**Benefit**: Everyone sees the same picture, in real-time.

##### **Component 2: Service Request System**

**Citizens submit requests** with:
- Type of help needed (medical, food, shelter, rescue)
- Location (GPS or address)
- Urgency level
- Contact details (with privacy controls)

**Providers see requests** and can:
- Accept responsibility
- Update status
- Mark as complete
- Add notes

**Benefit**: No duplicate efforts, clear accountability.

##### **Component 3: Role-Based Access**

**8 Different User Roles**:
1. **Individual** - General citizen (view only)
2. **Participant** - Affected person (can request help)
3. **Volunteer** - Helper on the ground
4. **Organizer** - Coordinates volunteers
5. **Manager** - Manages service providers
6. **Executive** - Organizational leadership
7. **Event Admin** - Manages disaster events
8. **System Admin** - Platform administrator

**Each role sees only what they need**. Privacy protected.

**Benefit**: Security + appropriate information access.

##### **Component 4: Financial Transparency**

**Donation tracking**:
- Who donated how much
- When it was received
- How it was allocated
- Which services were funded
- Proof of delivery

**Benefit**: Builds donor trust, enables auditing.

##### **Component 5: Audit & Reporting**

**Everything is logged**:
- Who did what, when
- All changes tracked
- Reports generated automatically
- Compliance with regulations

**Benefit**: Accountability, compliance, learning.

#### 5.2 The Complete Flow (Example)

**Step 1**: Flood declared in District X  
→ *Event Admin creates disaster event*

**Step 2**: Citizen Ramesh's house is flooded  
→ *Ramesh submits request for food via mobile*

**Step 3**: Request appears on map  
→ *All food providers in 50km see it*

**Step 4**: NGO ABC accepts request  
→ *Status changes to "In Progress"*

**Step 5**: Volunteer delivers food packets  
→ *Updates status, uploads photo proof*

**Step 6**: Ramesh confirms delivery  
→ *Status changes to "Completed"*

**Step 7**: Transaction logged  
→ *Donor sees their ₹500 funded this delivery*

**Total Time**: 2-4 hours (vs 2-4 days manually)

---

### 6. **Key Concepts (For Beginners)**

#### 6.1 What is a "Platform"?

A **platform** is like a marketplace that connects different groups:
- **Amazon** connects buyers ↔ sellers
- **Uber** connects riders ↔ drivers
- **IDRM** connects victims ↔ service providers

#### 6.2 What is "Map-Driven"?

Everything in IDRM is tied to a **location on a map**:
- Service requests have GPS coordinates
- Providers have service areas
- Disaster zones are drawn as polygons
- Resources are tracked by location

**Why maps?**: Disasters are **geographical**. Visualization helps coordination.

#### 6.3 What is "Privacy-First"?

**Privacy-first** means:
- Victim data is **protected by default**
- Access granted on **need-to-know basis**
- Three privacy levels:
  - **Public** (anyone can see)
  - **Protected** (authorized responders only)
  - **Private** (only the person and admins)

**Why?**: Vulnerable disaster victims need protection from exploitation.

#### 6.4 What is "Role-Based Access"?

Different users see different things based on their **role**:
- **Citizen** sees public information
- **Volunteer** sees requests they can help with
- **Admin** sees everything for oversight

**Why?**: Security + appropriate information for each person.

#### 6.5 What is "Real-Time"?

**Real-time** means updates happen **instantly**:
- Request submitted → Appears on map immediately
- Status updated → Everyone sees it now
- No delays, no manual syncing

**Why?**: In disasters, every minute counts.

#### 6.6 Technology Terms (Simple Explanations)

| Term | What It Means | Why It Matters |
|------|---------------|----------------|
| **API** | A way for computers to talk to each other | Allows different systems to connect |
| **Database** | Organized storage for all data | Remembers everything reliably |
| **Frontend** | What users see and click on | The user interface (web/mobile) |
| **Backend** | Behind-the-scenes logic | Processes requests, enforces rules |
| **Map Server** | Provides map tiles and geospatial features | Powers the map interface |
| **Authentication** | Verifying who you are (login) | Security - only authorized users |
| **Authorization** | Checking what you can do | Permissions - role-based access |

---

### 7. **System Capabilities**

#### 7.1 What Users Can Do

##### **For Affected Citizens (Participants)**

✅ **Submit service requests**  
- Choose type: Medical, Food, Shelter, Rescue, Other  
- Mark location on map or enter address  
- Set urgency: Critical, High, Medium, Low  
- Attach photos if needed  

✅ **Track request status**  
- See who accepted it  
- Get real-time updates  
- Communicate with provider  
- Confirm completion  

✅ **Protect privacy**  
- Choose who sees your request  
- Control contact information visibility  
- Request deletion after disaster  

##### **For Service Providers (Volunteers, Organizers)**

✅ **View requests on map**  
- Filter by type, urgency, distance  
- See only requests in service area  
- Get notifications for matches  

✅ **Accept and manage requests**  
- Claim responsibility  
- Update progress  
- Upload proof of delivery  
- Mark as complete  

✅ **Coordinate with team**  
- Assign tasks to volunteers  
- Track team performance  
- Communicate internally  

##### **For Coordinators (Managers, Executives)**

✅ **Monitor operations**  
- Real-time dashboard  
- Performance metrics  
- Resource allocation status  

✅ **Generate reports**  
- Services delivered  
- Response times  
- Geographic coverage  
- Financial summaries  

✅ **Manage resources**  
- Track inventory  
- Allocate funds  
- Deploy teams  

##### **For Administrators (Event Admins, System Admins)**

✅ **Create disaster events**  
- Define affected areas  
- Set severity levels  
- Coordinate overall response  

✅ **Manage users and organizations**  
- Approve registrations  
- Assign roles  
- Handle whitelisting/blacklisting  

✅ **System configuration**  
- Modify settings  
- Generate audit reports  
- Ensure compliance  

#### 7.2 What the System Provides

**Real-Time Visualization**  
- Interactive map with all activity  
- Color-coded markers by status  
- Heat maps showing demand  

**Smart Matching**  
- Automatically suggests providers near requests  
- Considers capacity, specialization  
- Prevents overburdening  

**Communication**  
- In-app messaging  
- Email notifications  
- SMS alerts (future)  
- Push notifications (mobile app)  

**Transparency**  
- Public feed of completed services  
- Financial transaction logs  
- Audit trails for all actions  

**Analytics**  
- Response time tracking  
- Success rate metrics  
- Geographic coverage analysis  
- Impact assessment  

**Security**  
- Encrypted data  
- Secure authentication (JWT tokens)  
- Role-based access control  
- Audit logging  

---

### 8. **User Roles Explained**

#### 8.1 Complete Role Hierarchy

```
┌──────────────────────────────────────┐
│         System Admin                 │
│    (Full platform control)           │
└──────────────┬───────────────────────┘
               │
      ┌────────┴────────┐
      │                 │
┌─────▼──────┐   ┌──────▼──────┐
│Event Admin │   │  Auditor    │
│ (Disaster  │   │ (Oversight) │
│  events)   │   │             │
└─────┬──────┘   └─────────────┘
      │
      ├──────────┬──────────┬──────────┐
      │          │          │          │
  ┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌──▼────┐
  │Manager│  │Exec  │  │Organ- │  │Volun- │
  │       │  │utive │  │izer   │  │teer   │
  └───┬───┘  └──────┘  └───┬───┘  └───────┘
      │                    │
      │                    │
  ┌───▼──────────────┬─────▼──┐
  │   Participant    │Individual│
  │ (Request help)   │(View only)│
  └──────────────────┴──────────┘
```

#### 8.2 Role Details

##### **Individual** (Tier 1 - General Public)
- **Who**: Any citizen
- **Access**: Public information only
- **Can**: Browse map, view public statistics
- **Cannot**: Submit requests or access detailed data

##### **Participant** (Tier 2 - Affected Person)
- **Who**: Someone affected by disaster
- **Access**: Can submit and track own requests
- **Can**: Request help, update requests, confirm delivery
- **Cannot**: See other people's private requests

##### **Volunteer** (Tier 3 - Helper)
- **Who**: Individual wanting to help
- **Access**: Sees requests in their area/skill
- **Can**: Accept requests, update status, deliver services
- **Cannot**: Access financial data or admin functions

##### **Organizer** (Tier 4 - Team Lead)
- **Who**: Leads a group of volunteers
- **Access**: Sees team members and their assignments
- **Can**: Assign tasks, track team performance
- **Cannot**: Manage other organizations

##### **Manager** (Tier 5 - Organization Manager)
- **Who**: Manages service provider organization
- **Access**: Full view of organization operations
- **Can**: Manage providers, allocate resources, generate reports
- **Cannot**: Create disaster events or access other orgs

##### **Executive** (Tier 6 - Leadership)
- **Who**: Organization leadership/directors
- **Access**: Strategic overview, financial data
- **Can**: View high-level analytics, approve major decisions
- **Cannot**: Day-to-day operational control

##### **Event Admin** (Tier 7 - Disaster Coordinator)
- **Who**: Coordinates specific disaster response
- **Access**: Full view of disaster event
- **Can**: Create events, approve providers, coordinate response
- **Cannot**: System-wide configuration

##### **System Admin** (Tier 8 - Platform Administrator)
- **Who**: Technical platform administrator
- **Access**: Everything
- **Can**: Full system control, user management, configuration
- **Responsibility**: Platform integrity and security

---

### 9. **Choosing Your Path**

#### 9.1 Quick Decision Tree

```
What do you want to do with IDRM?
│
├─ "I want to UNDERSTAND it"
│  └─ ✅ You're reading the right document!
│     Next: Browse other docs in README.md
│
├─ "I want to BUILD it (developer)"
│  └─ Next Steps:
│     1. Read: 01-PREREQUISITES.md
│     2. Read: 30-DEVELOPMENT-SETUP.md
│     3. Start: Week 1 implementation
│
├─ "I want to DEPLOY it (DevOps)"
│  └─ Next Steps:
│     1. Read: 01-PREREQUISITES.md
│     2. Choose: 31-STAGING or 32-PRODUCTION
│     3. Follow: Setup guide
│
├─ "I want to USE it (end user)"
│  └─ Next Steps:
│     1. Wait for deployment
│     2. Register on platform
│     3. Access user guides (in platform)
│
└─ "I want to EVALUATE it (decision maker)"
   └─ Next Steps:
      1. Read: 10-SYSTEM-ARCHITECTURE.md
      2. Read: 20-FUNCTIONAL-SPECIFICATION.md
      3. Review: Cost and timeline estimates
```

#### 9.2 By Role: Where to Go Next

| Your Role | Read This Next | Then This | Finally |
|-----------|----------------|-----------|---------|
| **Decision Maker** | 10-SYSTEM-ARCHITECTURE | 20-FUNCTIONAL-SPEC | 11-ARCHITECTURE-DECISIONS |
| **Project Manager** | 20-FUNCTIONAL-SPEC | 42-CHECKLISTS | Implementation docs |
| **Developer (Frontend)** | 01-PREREQUISITES | 24-FRONTEND-IMPL | 12-DESIGN-SYSTEM |
| **Developer (Backend)** | 01-PREREQUISITES | 25-BACKEND-IMPL | 22-DATABASE-DESIGN |
| **DevOps Engineer** | 01-PREREQUISITES | 30/31/32-SETUP | 33-CI-CD |
| **QA Engineer** | 20-FUNCTIONAL-SPEC | 42-CHECKLISTS | Test environment setup |

---

### 10. **Your First Steps**

#### 10.1 If You're a Complete Beginner

**This Week**:
1. ✅ Finish reading this document
2. ✅ Read the [README.md](README.md) navigation guide
3. ✅ Browse [10-SYSTEM-ARCHITECTURE.md](10-SYSTEM-ARCHITECTURE.md) (skim, don't deep dive)
4. ✅ Decide if you want to build, deploy, or just learn

**Next Week**:
- If building → Read [01-PREREQUISITES.md](01-PREREQUISITES.md)
- If deploying → Read deployment guides
- If learning → Read functional & technical specs

#### 10.2 If You're a Developer

**Today**:
1. ✅ Read [01-PREREQUISITES.md](01-PREREQUISITES.md)
2. ✅ Check your hardware (8GB+ RAM, Ubuntu 22/24)
3. ✅ Decide: Development or Staging setup?

**This Week**:
1. ✅ Install prerequisites (Bun, Python/Miniconda, PostgreSQL, Redis)
2. ✅ Follow [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md)
3. ✅ Get all services running
4. ✅ Test the basic flow

**Next Week**:
1. ✅ Read [20-FUNCTIONAL-SPECIFICATION.md](20-FUNCTIONAL-SPECIFICATION.md)
2. ✅ Start Week 1 implementation
3. ✅ Build your first feature

#### 10.3 If You're a DevOps Engineer

**Today**:
1. ✅ Read [01-PREREQUISITES.md](01-PREREQUISITES.md)
2. ✅ Check server requirements
3. ✅ Decide: Staging or Production first?

**This Week**:
1. ✅ Set up server (Ubuntu 22/24, 16-32GB RAM)
2. ✅ Follow [31-STAGING-SETUP.md](31-STAGING-SETUP.md) or [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)
3. ✅ Test deployment

**Next Week**:
1. ✅ Set up [33-CI-CD-PIPELINES.md](33-CI-CD-PIPELINES.md)
2. ✅ Configure monitoring
3. ✅ Document your setup

---

### 11. **Common Questions**

#### 11.1 About the Project

**Q: Is IDRM only for India?**  
A: Designed for India initially, but architecture is global-ready. Can be adapted for any country.

**Q: Is it only for natural disasters?**  
A: No! Works for any coordinated response: pandemics, industrial accidents, refugee situations.

**Q: Can it work offline?**  
A: Core features require internet. Offline mode is planned for future (Progressive Web App).

**Q: Is data secure?**  
A: Yes. Encryption, role-based access, audit logging, compliance with data protection laws.

#### 11.2 About Technology

**Q: Why not use WhatsApp or existing tools?**  
A: Existing tools lack: map visualization, structured data, audit trails, proper access control, analytics.

**Q: Why Bun instead of Node.js?**  
A: Bun is 3-4x faster, has better built-in features, and is the modern choice for new projects.

**Q: Why PostgreSQL instead of MongoDB?**  
A: Geospatial queries are 4-5x faster in PostgreSQL with PostGIS. ACID compliance ensures data integrity.

**Q: Can it scale to millions of users?**  
A: Yes. Architecture supports horizontal scaling. Current MVP targets 100K users; can scale beyond that.

#### 11.3 About Implementation

**Q: How long to build the MVP?**  
A: For an experienced developer: 8-12 weeks. For a beginner: 16-20 weeks with learning.

**Q: What's the minimum hardware?**  
A: Development: 8GB RAM laptop. Production: 32GB RAM server.

**Q: Do I need to know Docker?**  
A: Not for development setup. Yes for staging/production deployments.

**Q: Can I use this for my NGO?**  
A: Absolutely! That's the goal. See deployment guides.

#### 11.4 About Contribution

**Q: Is this open source?**  
A: Yes! MIT License. See [43-CONTRIBUTION-GUIDE.md](43-CONTRIBUTION-GUIDE.md)

**Q: Can I modify it for my needs?**  
A: Yes! Fork it, customize it, deploy it.

**Q: How can I contribute?**  
A: Code, documentation, testing, translations, feedback - all welcome!

---

### 12. **What's Next?**

#### 12.1 Immediate Next Steps

Choose **ONE** of these based on your goal:

**If you want to understand the architecture**:  
→ Read [10-SYSTEM-ARCHITECTURE.md](10-SYSTEM-ARCHITECTURE.md)

**If you want to start building**:  
→ Read [01-PREREQUISITES.md](01-PREREQUISITES.md)  
→ Then [30-DEVELOPMENT-SETUP.md](30-DEVELOPMENT-SETUP.md)

**If you want to deploy**:  
→ Read [01-PREREQUISITES.md](01-PREREQUISITES.md)  
→ Then [31-STAGING-SETUP.md](31-STAGING-SETUP.md) or [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)

**If you want to understand requirements**:  
→ Read [20-FUNCTIONAL-SPECIFICATION.md](20-FUNCTIONAL-SPECIFICATION.md)

**If you're evaluating IDRM**:  
→ Read [11-ARCHITECTURE-DECISIONS.md](11-ARCHITECTURE-DECISIONS.md)

#### 12.2 Complete Learning Path

**Beginner → Intermediate → Advanced**

```
LEVEL 1: Understanding
├─ ✅ 00-GETTING-STARTED.md (you are here)
├─ □ README.md (navigation)
└─ □ 10-SYSTEM-ARCHITECTURE.md (overview)

LEVEL 2: Planning
├─ □ 20-FUNCTIONAL-SPECIFICATION.md (requirements)
├─ □ 11-ARCHITECTURE-DECISIONS.md (rationale)
└─ □ 42-VERIFICATION-CHECKLISTS.md (tracking)

LEVEL 3: Building
├─ □ 01-PREREQUISITES.md (setup)
├─ □ 30-DEVELOPMENT-SETUP.md (environment)
├─ □ 24-FRONTEND-IMPLEMENTATION.md (UI)
├─ □ 25-BACKEND-IMPLEMENTATION.md (API)
└─ □ 22-DATABASE-DESIGN.md (data)

LEVEL 4: Deploying
├─ □ 31-STAGING-SETUP.md (testing env)
├─ □ 32-PRODUCTION-DEPLOYMENT.md (live)
└─ □ 33-CI-CD-PIPELINES.md (automation)

LEVEL 5: Mastering
├─ □ 21-TECHNICAL-DESIGN.md (deep dive)
├─ □ 23-API-SPECIFICATION.md (API details)
├─ □ 40-DATA-FORMATS.md (data schemas)
└─ □ 41-CODE-STANDARDS.md (best practices)
```

#### 12.3 Getting Help

**Stuck? Confused? Questions?**

1. **Check documentation**: Use README.md navigation to find relevant docs
2. **Search existing issues**: GitHub Issues for known problems
3. **Ask the community**: Discussion forum
4. **Report bugs**: GitHub Issues with reproduction steps

**Remember**: Everyone starts as a beginner. Take it step by step!

---

### ✅ **Quick Checklist: Did You Understand?**

After reading this document, you should be able to answer:

- [ ] What is IDRM in one sentence?
- [ ] What problem does it solve?
- [ ] Who are the main users?
- [ ] What are the key capabilities?
- [ ] What is "map-driven" and why does it matter?
- [ ] What are the 8 user roles?
- [ ] Which document should I read next for my role?

**If you can answer these**, you're ready to move forward! 🎉

---

### 🎯 **Summary: IDRM in 3 Minutes**

**What**: Digital platform for disaster response coordination  
**Why**: Current response is fragmented and slow  
**How**: Map-based, real-time, privacy-first, role-based access  
**Who**: Citizens, providers, coordinators, donors, admins  
**Where**: Pan-India (MVP), globally adaptable  
**When**: MVP implementation: 8-16 weeks  

**Core Value**: **Faster response → More lives saved**

**Your Next Step**: Pick from [Section 12.1](#121-immediate-next-steps) above based on your goal.

---

**Welcome to IDRM! Let's build a better disaster response system together.** 🚀

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Part of**: IDRM Consolidated Documentation Suite (18 documents)  
**Related**: README.md → All other docs  
**Feedback**: Open an issue or submit a PR on GitHub

---

## IDRM v3 Monolith: Quick Reference Guide

### Everything You Need at Your Fingertips - Multi-Platform Edition

**Version**: 3.0  
**Platforms**: HTML/Tailwind + React SPA + React Native  
**Stack**: Bun + Python (Miniconda) + PostgreSQL + Redis

---

### 🎯 v3 Quick Facts

**Three Frontend Platforms**:
- HTML/Tailwind (Port 5173) - Primary web
- React SPA (Port 5174) - Admin dashboards
- React Native (Expo) - iOS + Android mobile

**Key Changes from v2**:
- ❌ Removed: Java/GeoServer, Node.js, npm, venv
- ✅ Added: Python geospatial, Bun, Miniconda, React Native

---

### 🚀 Installation (v3 Stack)

```bash
## Download v3 setup script
wget https://raw.githubusercontent.com/your-repo/idrm-mvp/v3/setup-idrm-v3.sh
chmod +x setup-idrm-v3.sh
./setup-idrm-v3.sh

## What it installs:
## - PostgreSQL 16 + PostGIS 3.4
## - Redis 7.2+
## - Miniconda (Python 3.11)
## - Bun (JavaScript runtime) - NOT Node.js!
## - Expo CLI (for React Native)
## - VSCodium/VSCode
## - DBeaver, Android Studio (optional)

## Time: 20-25 minutes
```

---

### 📁 Daily Workflow (v3 - Three Platforms)

#### Full Stack Development (5 Terminals)

```bash
## Terminal 1: Backend
cd ~/projects/idrm-mvp/backend
conda activate idrm-mvp
uvicorn app.main:app --reload --port 8000

## Terminal 2: API Gateway
cd ~/projects/idrm-mvp/api-gateway
bun run dev

## Terminal 3: HTML/Tailwind Frontend
cd ~/projects/idrm-mvp/frontend/html-tailwind
bun run dev    # NOT npm run dev!

## Terminal 4: React SPA (Admin)
cd ~/projects/idrm-mvp/frontend/react-spa
bun run dev

## Terminal 5: React Native (Mobile)
cd ~/projects/idrm-mvp/mobile
npx expo start
```

#### Single Platform Focus

```bash
## Working on mobile app only? Just run:

## Terminal 1: Backend
cd backend && conda activate idrm-mvp && uvicorn app.main:app --reload

## Terminal 2: Mobile
cd mobile && npx expo start
```

#### URLs (v3)

- **Backend API**: http://localhost:8000
- **API Gateway**: http://localhost:3000
- **HTML/Tailwind**: http://localhost:5173
- **React SPA**: http://localhost:5174
- **API Docs**: http://localhost:8000/docs
- **React Native**: Expo Dev Tools (auto-opens)

---

### 🗄️ Database Commands (Same as v2)

```bash
## Connect
psql -U idrm_user -d idrm_db

## Quick status
sudo systemctl status postgresql
sudo systemctl status redis

## Backup
pg_dump -U idrm_user -d idrm_db > backup.sql
```

---

### 🐍 Python (Miniconda) Commands

**v3 uses Miniconda, NOT venv!**

```bash
## Activate environment
conda activate idrm-mvp

## Install packages (IMPORTANT: use --break-system-packages)
pip install package-name --break-system-packages

## Update environment
conda env update -f environment.yml

## Deactivate
conda deactivate

## List environments
conda env list

## Create new environment
conda create -n idrm-mvp python=3.11
```

**Common mistake**: Don't use `python -m venv` - we use Miniconda!

---

### 🟨 JavaScript (Bun) Commands

**v3 uses Bun, NOT npm or node!**

```bash
## Install dependencies
bun install              # NOT npm install

## Run dev server
bun run dev              # NOT npm run dev

## Build for production
bun run build            # NOT npm run build

## Run script
bun run script.ts        # NOT node script.js

## Execute file directly
bun script.ts

## Install package
bun add package-name     # NOT npm install package-name

## Remove package
bun remove package-name  # NOT npm uninstall
```

**Common mistake**: Using `npm` or `node` commands - use `bun` instead!

---

### 📱 React Native (Expo) Commands

```bash
## Start development server
npx expo start

## Run on iOS simulator
npx expo start --ios

## Run on Android emulator
npx expo start --android

## Clear cache
npx expo start -c

## Build for production
eas build --platform ios
eas build --platform android

## Over-the-air update
eas update --branch production

## Check project
npx expo doctor
```

---

### 🔧 Frontend Commands (Three Platforms)

#### HTML/Tailwind

```bash
cd frontend/html-tailwind
bun install              # Install dependencies
bun run dev              # Start dev server (port 5173)
bun run build            # Build for production
bun run preview          # Preview production build
```

#### React SPA

```bash
cd frontend/react-spa
bun install              # Install dependencies
bun run dev              # Start dev server (port 5174)
bun run build            # Build for production
bun run preview          # Preview production build
bun run test             # Run tests
```

#### React Native

```bash
cd mobile
bun install              # Install dependencies
npx expo start           # Start Expo dev server
npx expo start --ios     # Open iOS simulator
npx expo start --android # Open Android emulator
bun run test             # Run tests
```

---

### 🔌 API Gateway Commands

```bash
cd api-gateway
bun install              # Install dependencies
bun run dev              # Start dev server (port 3000)
bun run start            # Start production server
bun test                 # Run tests
```

---

### 🧪 Testing Commands (v3)

```bash
## Backend tests
cd backend
pytest tests/ -v
pytest tests/test_api.py::test_create_user -v

## HTML/Tailwind tests
cd frontend/html-tailwind
bun test

## React SPA tests
cd frontend/react-spa
bun test
bun test:watch

## React Native tests
cd mobile
bun test
bun test --watch

## Integration tests (all platforms)
cd tests/integration
pytest test_multi_platform.py -v
```

---

### 🚨 Troubleshooting (v3)

#### Port Already in Use

```bash
## Check what's using a port
sudo lsof -i :8000    # Backend
sudo lsof -i :3000    # API Gateway
sudo lsof -i :5173    # HTML/Tailwind
sudo lsof -i :5174    # React SPA

## Kill process
kill -9 <PID>
```

#### Frontend Won't Connect

```bash
## Check CORS in backend (backend/app/main.py)
allow_origins=[
    "http://localhost:5173",  # HTML/Tailwind
    "http://localhost:5174",  # React SPA
    "exp://*",                # React Native
]

## Check API Gateway is running
curl http://localhost:3000/health
```

#### React Native Can't Connect

```bash
## Use your computer's IP, not localhost
## In mobile/src/config.ts:
export const API_URL = "http://192.168.1.100:3000/api/v1";
## Replace 192.168.1.100 with YOUR local IP

## Find your IP:
ip addr show | grep inet
## Or on macOS: ifconfig | grep inet
```

#### Python Geospatial Service Issues

```bash
## Install geospatial packages
conda activate idrm-mvp
pip install geopandas shapely gdal fiona pyproj --break-system-packages

## Test geospatial service
curl http://localhost:8002/health
```

---

### 📦 Package Management (v3)

#### Python (Miniconda)

```bash
## Add package
pip install package-name --break-system-packages

## Add to requirements
echo "package-name==1.0.0" >> requirements.txt

## Update all
pip install -r requirements.txt --break-system-packages
```

#### JavaScript (Bun)

```bash
## Add package
bun add package-name

## Add dev dependency
bun add -d package-name

## Update all
bun update

## Remove package
bun remove package-name
```

---

### 🎨 Quick Code Snippets (v3)

#### Start All Services Script

```bash
#!/bin/bash
## scripts/dev-all-v3.sh

## Start backend
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/backend && conda activate idrm-mvp && uvicorn app.main:app --reload; exec bash"

## Start API Gateway
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/api-gateway && bun run dev; exec bash"

## Start HTML/Tailwind
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/frontend/html-tailwind && bun run dev; exec bash"

## Start React SPA
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/frontend/react-spa && bun run dev; exec bash"

## Start React Native
gnome-terminal -- bash -c "cd ~/projects/idrm-mvp/mobile && npx expo start; exec bash"

echo "✅ All v3 services started!"
```

#### Health Check All Services

```bash
#!/bin/bash
## scripts/health-check-v3.sh

echo "Checking Backend (8000)..."
curl -s http://localhost:8000/health | jq

echo "Checking API Gateway (3000)..."
curl -s http://localhost:3000/health | jq

echo "Checking HTML/Tailwind (5173)..."
curl -s http://localhost:5173 > /dev/null && echo "✅ Running"

echo "Checking React SPA (5174)..."
curl -s http://localhost:5174 > /dev/null && echo "✅ Running"

echo "Checking PostgreSQL..."
sudo systemctl status postgresql --no-pager

echo "Checking Redis..."
sudo systemctl status redis --no-pager
```

---

### 🔐 Environment Variables (v3)

```bash
## backend/.env
DATABASE_URL=postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,exp://*

## api-gateway/.env
BACKEND_URL=http://localhost:8000
FRONTEND_HTML_URL=http://localhost:5173
FRONTEND_SPA_URL=http://localhost:5174

## mobile/.env
API_URL=http://192.168.1.100:3000/api/v1  # Use your local IP
```

---

### 📊 Monitoring Commands

```bash
## View logs
journalctl -u idrm-backend -f        # Backend logs
journalctl -u idrm-api-gateway -f    # API Gateway logs
tail -f /var/log/postgresql/*.log    # PostgreSQL logs

## System resources
htop                                  # CPU/RAM usage
df -h                                 # Disk usage
free -h                               # Memory usage

## Database performance
psql -U idrm_user -d idrm_db -c "SELECT * FROM pg_stat_activity;"
```

---

### 🚀 Production Deployment (v3)

```bash
## Build all frontends
cd frontend/html-tailwind && bun run build
cd frontend/react-spa && bun run build

## Build mobile apps
cd mobile
eas build --platform all

## Deploy to server
rsync -avz frontend/html-tailwind/dist/ user@server:/var/www/idrm/
rsync -avz frontend/react-spa/dist/ user@server:/var/www/idrm-admin/

## Restart services
ssh user@server "sudo systemctl restart idrm-backend idrm-api-gateway nginx"
```

---

### 📚 Documentation Links

- **PRD**: IDRM-MVP-PRD-v2.md (v3 review pending)
- **Architecture**: monolith-architecture-v3.md
- **Design System**: design-system-v3.md
- **Contributor Guide**: contributor-guide-v3.md
- **API Docs**: http://localhost:8000/docs

---

### 🎯 Common Commands Summary

**Python (Miniconda)**:
```bash
conda activate idrm-mvp
pip install package --break-system-packages
```

**JavaScript (Bun)**:
```bash
bun install
bun run dev
bun add package
```

**React Native (Expo)**:
```bash
npx expo start
eas build --platform ios
```

**Database**:
```bash
psql -U idrm_user -d idrm_db
sudo systemctl status postgresql
```

---

**IDRM v3 Quick Reference - Multi-Platform Development Made Easy!** 🚀
