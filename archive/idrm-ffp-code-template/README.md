# IDRM v3.0 — Integrated Disaster Response Management
## Multi-Platform Emergency Response System for India 🇮🇳

**Version**: 3.0  
**Last Updated**: May 30, 2026  
**Status**: ✅ Documentation Complete | 🏗️ Code 20% | 📱 Multi-Platform Ready  
**Architecture**: Modular Monolith · 3 Frontend Platforms  
**Tech Stack**: Bun · Python/FastAPI · PostgreSQL 16 + PostGIS 3.4 · Redis 7.2

[![Setup Guide](https://img.shields.io/badge/setup-COMPLETE--SETUP--GUIDE-brightgreen)](./start-here/COMPLETE-SETUP-GUIDE.md)
[![API Specs](https://img.shields.io/badge/api-37%20endpoints-blue)](./start-here/COMPLETE-API-SPECS-GUIDE.md)
[![License](https://img.shields.io/badge/license-Open%20Source-green)]()

---

## 📋 Table of Contents

1. [What is IDRM?](#-what-is-idrm)
2. [Quick Start](#-quick-start-choose-your-path)
3. [Project Structure](#-project-structure)
4. [Technology Stack](#️-technology-stack-v30)
5. [Documentation Map](#-documentation-map)
6. [Development Workflow](#-development-workflow)
7. [Deployment Options](#-deployment-options)
8. [Current Status](#-current-status)
9. [Roadmap](#️-roadmap)
10. [Contributing](#-contributing)

---

## 🎯 What is IDRM?

### The Problem

When disasters strike India (earthquakes, floods, cyclones, pandemics):
- 🚨 **Citizens need help** but don't know where to request it
- 📍 **Responders can't see** where help is needed
- 🔄 **No coordination** between NGOs, government, and volunteers
- 📊 **No tracking** of response effectiveness

### The Solution: Think "Uber for Disaster Relief"

```
┌──────────────────────────────────────────────────────┐
│                  IDRM v3 Platform                    │
│                                                      │
│  Citizen requests help → Shows on map → Coordinator  │
│  approves → Provider accepts → Delivers → Verified   │
│                                                      │
│  🗺️ Real-time map    📱 Mobile app    📊 Analytics   │
│  ⚡ <5 min response  🔐 Secure        💰 Transparent │
└──────────────────────────────────────────────────────┘
```

### How It Works

1. **Citizen** (web/mobile): "Need food at T Nagar, Chennai" → Creates request
2. **DM Authority**: Reviews on map → Approves request
3. **System**: Notifies nearby providers via push/SMS/email
4. **Provider**: Accepts → Delivers → Marks complete
5. **Citizen**: Verifies completion → Rates provider
6. **Everyone**: Tracks in real-time → Full transparency

---

## ✨ Key Features v3.0

### 🌐 Three Platforms, One Backend

| Platform | Technology | Port | Users | Purpose |
|----------|-----------|------|-------|---------|
| **Web Interface** | HTML + Tailwind CSS | 5173 | Citizens | Request help, view map |
| **Admin Dashboard** | React SPA + TypeScript | 5174 | Coordinators | Manage requests, analytics |
| **Mobile App** _(Post-MVP)_ | React Native + Expo | Expo | Field Workers | GPS, camera, offline |

### 🗺️ Core Features

**For Citizens**:
- ✅ Interactive map (real-time request locations)
- ✅ One-click emergency request
- ✅ Track request status through full lifecycle
- ✅ Privacy controls (PUBLIC / PROTECTED / PRIVATE — default PROTECTED)

**For Coordinators (DM_AUTHORITY)**:
- ✅ Dashboard with live analytics
- ✅ Approve or reject incoming requests
- ✅ Real-time notifications via WebSocket
- ✅ Heatmaps and performance charts

**For Field Workers (Providers)**:
- ✅ Mobile app (iOS + Android)
- ✅ GPS location tracking
- ✅ Offline-first support
- ✅ Push notifications on new assignments

**Technical Features**:
- ✅ Role-based access (10 account roles + a Public tier; canonical Permission Matrix in `docs/development/IDRM-FS.md` §3.3)
- ✅ Geospatial queries (find requests within N km using PostGIS)
- ✅ Map clustering (group nearby requests at zoom-out)
- ✅ Real-time WebSocket updates (port 3001)
- ✅ Multi-language support (English, Hindi, Telugu)
- ✅ JWT authentication with 15-min access tokens + 7-day refresh

---

## 🚀 Quick Start (Choose Your Path)

### 🟢 Path A: Complete Beginner

**Prerequisites**: New to software development? Start here.

```bash
# Step 1: Read the beginner guide first
# → start-here/COMPLETE-BEGINNERS-GUIDE.md

# Step 2: Install all prerequisites
./scripts/setup-prerequisites.sh

# Step 3: Set up your development environment
./scripts/setup-development-monolith.sh

# Step 4: Start all 5 services
# → See "Development Workflow" section below
```

**Recommended reading order**:
1. [`start-here/COMPLETE-BEGINNERS-GUIDE.md`](./start-here/COMPLETE-BEGINNERS-GUIDE.md) — Start absolutely here
2. [`start-here/COMPLETE-SETUP-GUIDE.md`](./start-here/COMPLETE-SETUP-GUIDE.md) — Install and run
3. [`CONTRIBUTING.md`](./CONTRIBUTING.md) — How to write code for this project

---

### 🟡 Path B: Some Experience

**Prerequisites**: Know HTML/CSS/JavaScript or Python basics.

```bash
# Day 1: Understand the system
# → docs/IDRM-ARCHITECTURE-GUIDE.md      (architecture — 45 min)
# → CLAUDE.md                             (API quick reference — 20 min)

# Day 2-3: Setup and run
./scripts/setup-prerequisites.sh
./scripts/setup-development-monolith.sh

# Day 4+: Start building
# → start-here/COMPLETE-API-SPECS-GUIDE.md  (all 37 endpoints)
# → schedules/IDRM-MVP-ANALYSIS-ROADMAP.md  (what to build next)
```

**Recommended reading order**:
1. [`docs/IDRM-ARCHITECTURE-GUIDE.md`](./docs/IDRM-ARCHITECTURE-GUIDE.md)
2. [`start-here/COMPLETE-SETUP-GUIDE.md`](./start-here/COMPLETE-SETUP-GUIDE.md)
3. [`start-here/COMPLETE-API-SPECS-GUIDE.md`](./start-here/COMPLETE-API-SPECS-GUIDE.md)
4. [`schedules/IDRM-MVP-ANALYSIS-ROADMAP.md`](./schedules/IDRM-MVP-ANALYSIS-ROADMAP.md)

---

### 🔴 Path C: Experienced Developer

**Prerequisites**: Experienced with web development and APIs.

```bash
# Hour 1: Skim the essentials
# → CLAUDE.md                (architecture constraints + API reference)
# → docs/development/IDRM-LLD.md  (complete DB schema + API specs)

# Hour 2: One-command setup
./scripts/setup-prerequisites.sh && ./scripts/setup-development-monolith.sh

# Hour 3+: Start coding
# Terminal 1: cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000
# Terminal 2: cd src/backend/api-gateway && bun run dev
# Terminal 3: cd src/frontend/web-html && bun run dev
# Terminal 4: cd src/frontend/web-react && bun run dev
# Terminal 5: cd src/frontend/mobile-expo && npx expo start
```

**Recommended reading order**:
1. [`CLAUDE.md`](./CLAUDE.md) — Architecture decisions + API cheat sheet
2. [`docs/development/IDRM-LLD.md`](./docs/development/IDRM-LLD.md) — Complete technical spec
3. [`start-here/QUICK-CMD-REFERENCE.md`](./start-here/QUICK-CMD-REFERENCE.md) — Daily commands

---

## 📁 Project Structure

### High-Level Overview

```
idrm-mvp/
├── src/                          # All source code
│   ├── backend/
│   │   ├── app-python/           # FastAPI Modular Monolith (port 8000)
│   │   │   ├── api/              # Route handlers
│   │   │   ├── core/             # Config, DB session, security
│   │   │   ├── dbmodels/         # SQLAlchemy ORM models
│   │   │   ├── schemas/          # Pydantic request/response schemas
│   │   │   └── services/         # Business logic layer
│   │   └── api-gateway/          # Bun gateway (port 3000 HTTP · 3001 WS)
│   └── frontend/
│       ├── web-html/             # HTML/Tailwind — citizens (port 5173)
│       ├── web-react/            # React SPA — admins (port 5174)
│       └── mobile-expo/          # React Native — field workers (Expo)
│
├── database/
│   └── init/
│       ├── 01-extensions.sql     # Enable PostGIS, uuid-ossp, pg_trgm
│       ├── 02-schema.sql         # All tables, indexes, views, functions, triggers
│       └── 03-seed-data.sql      # disaster_types reference table + 9 seed rows
│
├── infra/
│   └── docker/
│       └── full-stack.yml        # Full-stack Docker Compose
│
├── scripts/
│   ├── setup-prerequisites.sh         # Verify + install prerequisites
│   ├── setup-development-monolith.sh  # Local dev setup
│   ├── setup-development-modular.sh   # Modular dev setup
│   ├── setup-staging.sh               # Staging environment setup
│   └── setup-production.sh            # Production setup
│
├── start-here/                   # 📖 Start reading here — entry-point guides
├── docs/                         # 📖 Deep-dive technical documentation
│   ├── development/              # PRD, HLD, LLD, FS
│   └── diagrams/                 # 13 Mermaid architecture diagrams
├── instructions/                 # Platform-specific developer guides
├── schedules/                    # Gap analysis, roadmap, implementation plan
├── tests/                        # All tests (backend, frontend, e2e)
│
├── CLAUDE.md                     # AI context + API quick reference
├── CONTRIBUTING.md               # Contributor guide + coding standards
└── README.md                     # This file
```

### Backend Detail

```
src/backend/app-python/           # Single FastAPI process — all modules on port 8000
├── api/                          # Route handlers grouped by domain
│   └── v1/
│       ├── auth.py               # /auth/* — login, register, JWT, refresh
│       ├── services.py           # /services/* — requests, accept, complete, verify
│       ├── geo.py                # /geo/* — nearby, cluster, bbox, GeoJSON
│       ├── analytics.py          # /analytics/* — dashboard, reports, export
│       └── notifications.py      # /notifications/* — list, mark-read
├── core/
│   ├── config.py                 # Settings from .env
│   ├── database.py               # SQLAlchemy async session
│   └── security.py               # JWT creation/validation, bcrypt hashing
├── dbmodels/                     # SQLAlchemy table definitions
├── schemas/                      # Pydantic request + response models
└── services/                     # Business logic (auth, matching, geo, notifications)
```

### API Gateway Detail

```
src/backend/api-gateway/          # Bun — the front door for all traffic
├── routes/                       # Forward to FastAPI at localhost:8000
├── middleware/
│   ├── auth.ts                   # JWT verification — strips token, injects X-User-ID header
│   ├── cors.ts                   # CORS — restricts allowed origins
│   ├── rateLimit.ts              # Rate limiting via Redis
│   └── logger.ts                 # Request logging
└── utils/
    ├── redis.ts                  # Redis client (sessions, rate-limit counters)
    └── errors.ts                 # Standardised error responses
```

### Frontend Detail

```
src/frontend/web-html/            # Primary citizen-facing web (port 5173)
├── src/
│   ├── pages/                    # HTML pages (login, register, map-view, dashboard)
│   ├── components/               # Reusable HTML components (navbar, modal, map-container)
│   ├── layouts/                  # Page shells (auth-layout, dashboard-layout, main-layout)
│   ├── js/
│   │   ├── api/                  # Fetch-based API client — talks to port 3000
│   │   ├── modules/maps/         # Leaflet map integration
│   │   ├── ui/                   # DOM helpers
│   │   └── utils/                # Shared utilities
│   └── styles/                   # Tailwind CSS + theme overrides
└── public/                       # Static assets (favicon, icons, manifest)

src/frontend/web-react/           # Admin dashboard (port 5174)
├── src/
│   ├── pages/                    # Dashboard, RequestManagement, UserManagement, Analytics
│   ├── components/               # UI components, charts, map view
│   ├── hooks/                    # useAuth, useServiceRequests, useAnalytics
│   └── lib/                      # API client (TypeScript), utilities

src/frontend/mobile-expo/         # React Native field-worker app (Expo)
├── App.tsx                       # Root component
├── screens/                      # Home, Map, CreateRequest, MyRequests, Profile
├── components/                   # RequestCard, MapMarker, CameraButton
└── navigation/                   # AppNavigator, AuthNavigator
```

---

## 🛠️ Technology Stack v3.0

### Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **API Gateway** | Bun | 1.x | HTTP routing (3000), WebSocket (3001), rate limiting |
| **Backend** | Python + FastAPI | 3.11 / 0.109+ | Modular Monolith — all business logic |
| **Python Env** | Miniconda | Latest | Manages GDAL/GEOS geospatial binaries |
| **Geospatial** | GeoPandas + PostGIS | Custom | Replaces Java/GeoServer |

### Data Layer

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Database** | PostgreSQL | 16 | Primary data store |
| **Spatial Extension** | PostGIS | 3.4 | GPS coordinates, distance queries |
| **Cache / Sessions** | Redis | 7.2+ | JWT sessions, rate limits, pub/sub |
| **ORM** | SQLAlchemy | 2.0+ | Database access layer |
| **Migrations** | Alembic | 1.13+ | Schema versioning |

### Frontend Platforms

| Platform | Technology | Version | Build Tool | Port |
|----------|-----------|---------|------------|------|
| **Web** | HTML + Tailwind CSS | 3.4+ | Vite (Bun) | 5173 |
| **Admin** | React + TypeScript | 18.2+ | Vite (Bun) | 5174 |
| **Mobile** | React Native + Expo | 49+ | Expo CLI | Expo |

### DevOps & Infrastructure

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **CI/CD** | GitHub Actions | Automated test + deploy on push |
| **Containers** | Docker + Compose | Staging and production containerisation |
| **Reverse Proxy** | NGINX | SSL termination, load balancing |
| **Monitoring** | Prometheus + Grafana | Metrics and dashboards |

### What We DON'T Use (Replaced in v3)

- ❌ **Java / GeoServer** — Replaced by Python GeoPandas module inside FastAPI
- ❌ **Node.js** — Replaced by Bun (3–4× faster)
- ❌ **Python venv / pip** — Replaced by Miniconda (manages binary geospatial deps)
- ❌ **Microservices** — Single FastAPI process on port 8000 (modular monolith)

---

## 📚 Documentation Map

All **43 documents** that exist in this repository, grouped by purpose.

---

### 🚪 Entry Points — Start Here (`start-here/`)

| Document | Purpose | Who |
|----------|---------|-----|
| [`COMPLETE-SETUP-GUIDE.md`](./start-here/COMPLETE-SETUP-GUIDE.md) | Zero to fully running — dev, staging, production | Everyone |
| [`COMPLETE-API-SPECS-GUIDE.md`](./start-here/COMPLETE-API-SPECS-GUIDE.md) | All 37 endpoints with security, RBAC, JSON examples | Backend / API devs |
| [`COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md`](./start-here/COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md) | Design tokens, component library, UX patterns | Frontend devs / designers |
| [`COMPLETE-DATABASE-GUIDE.md`](./start-here/COMPLETE-DATABASE-GUIDE.md) | Database operations, migrations, query patterns | Backend / DB devs |
| [`COMPLETE-BEGINNERS-GUIDE.md`](./start-here/COMPLETE-BEGINNERS-GUIDE.md) | Step-by-step for first-time contributors | Complete beginners |
| [`COMPLETE-DevSecOps-GUIDE.md`](./start-here/COMPLETE-DevSecOps-GUIDE.md) | CI/CD pipeline, security hardening, DevOps | DevOps engineers |
| [`COMPLETE-MONITORING-GUIDE.md`](./start-here/COMPLETE-MONITORING-GUIDE.md) | Prometheus, Grafana, alerting, observability | Ops / SRE |
| [`QUICK-CMD-REFERENCE.md`](./start-here/QUICK-CMD-REFERENCE.md) | One-page cheat sheet of daily commands | Everyone |

---

### 📖 Technical Deep-Dives (`docs/`)

| Document | Purpose | Who |
|----------|---------|-----|
| [`IDRM-ARCHITECTURE-GUIDE.md`](./docs/IDRM-ARCHITECTURE-GUIDE.md) | Full system architecture — decisions, trade-offs, diagrams | Architects / tech leads |
| [`IDRM-DEVELOPMENT-GUIDE.md`](./docs/IDRM-DEVELOPMENT-GUIDE.md) | Development workflow, environment, hot-reload | All developers |
| [`IDRM-DEPLOYMENT-GUIDE.md`](./docs/IDRM-DEPLOYMENT-GUIDE.md) | Staging + production deployment step-by-step | DevOps |
| [`IDRM-Bun-Gateway-Guide.md`](./docs/IDRM-Bun-Gateway-Guide.md) | Bun API Gateway internals — routing, middleware, WS | Backend devs |
| [`IDRM-Database-Query-Reference.md`](./docs/IDRM-Database-Query-Reference.md) | Optimised SQL patterns, PostGIS recipes | Backend / DB devs |
| [`IDRM-Redis-Operations.md`](./docs/IDRM-Redis-Operations.md) | Redis key patterns, caching strategy, pub/sub | Backend devs |
| [`IDRM-Testing-Strategy.md`](./docs/IDRM-Testing-Strategy.md) | Testing philosophy, coverage goals, test patterns | QA / all devs |
| [`IDRM-Mock-Data-Guide.md`](./docs/IDRM-Mock-Data-Guide.md) | Generating realistic test data | QA / backend devs |

---

### 📐 Formal Engineering Docs (`docs/development/`)

| Document | Purpose | Who |
|----------|---------|-----|
| [`IDRM-PRD.md`](./docs/development/IDRM-PRD.md) | Product Requirements — what we're building and why | PMs / architects |
| [`IDRM-HLD.md`](./docs/development/IDRM-HLD.md) | High-Level Design — system-wide technical decisions | Architects |
| [`IDRM-LLD.md`](./docs/development/IDRM-LLD.md) | Low-Level Design — complete DB schema, API specs, triggers, tests | All backend devs |
| [`IDRM-FS.md`](./docs/development/IDRM-FS.md) | Functional Specification — feature behaviour definitions | PMs / QA |

> **`IDRM-LLD.md` is the single source of truth** for database schema and API contract details.

---

### 🗺️ Diagrams (`docs/diagrams/`)

All diagrams are written in Mermaid — renderable in GitHub, VS Code, and Notion.

| Document | What it shows |
|----------|--------------|
| [`IDRM-System-Architecture.md`](./docs/diagrams/IDRM-System-Architecture.md) | Three-platform monolith — full system overview |
| [`IDRM-Database-Schema.md`](./docs/diagrams/IDRM-Database-Schema.md) | Entity-relationship diagram |
| [`IDRM-Entity-Classes.md`](./docs/diagrams/IDRM-Entity-Classes.md) | Class diagram for all domain entities |
| [`IDRM-Service-Management.md`](./docs/diagrams/IDRM-Service-Management.md) | Service request lifecycle state machine |
| [`IDRM-Session-Management.md`](./docs/diagrams/IDRM-Session-Management.md) | JWT auth + Redis session flow |
| [`IDRM-User-Registration.md`](./docs/diagrams/IDRM-User-Registration.md) | User registration and email verification flow |
| [`IDRM-Components.md`](./docs/diagrams/IDRM-Components.md) | Component breakdown across all three platforms |
| [`IDRM-DFD.md`](./docs/diagrams/IDRM-DFD.md) | Data flow diagram (current) |
| [`IDRM-DFD-Original.md`](./docs/diagrams/IDRM-DFD-Original.md) | Data flow diagram (original reference) |
| [`IDRM-CICD-Workflow.md`](./docs/diagrams/IDRM-CICD-Workflow.md) | GitHub Actions CI/CD pipeline |
| [`IDRM-Deployment-Pipeline.md`](./docs/diagrams/IDRM-Deployment-Pipeline.md) | Blue/green deployment flow |
| [`IDRM-Frontend-Deployment.md`](./docs/diagrams/IDRM-Frontend-Deployment.md) | Frontend build + deploy |
| [`IDRM-MAD-Management.md`](./docs/diagrams/IDRM-MAD-Management.md) | Mobile app distribution management |

---

### 📝 Platform-Specific Guides (`instructions/`)

| Document | Purpose |
|----------|---------|
| [`instructions_ui_v3.md`](./instructions/instructions_ui_v3.md) | UI/UX rulebook — Slate+Emerald design tokens + Tailwind component recipes |
| [`instructions_web_v3.md`](./instructions/instructions_web_v3.md) | HTML/Tailwind platform — detailed guide |
| [`instructions_pages_v3.md`](./instructions/instructions_pages_v3.md) | Page-by-page reference for all three platforms |
| [`instructions_json_formats_v3.md`](./instructions/instructions_json_formats_v3.md) | All JSON request/response formats |

> `instructions_ui_v3.md` is the canonical UI/UX rulebook (Slate + Emerald tokens, Tailwind component recipes).

---

### 🗓️ Schedules & Planning (`schedules/`)

| Document | Purpose |
|----------|---------|
| [`IDRM-MVP-ANALYSIS-ROADMAP.md`](./schedules/IDRM-MVP-ANALYSIS-ROADMAP.md) | What's built, what's missing, priority order |
| [`IDRM-IMPLEMENTATION-GUIDE.md`](./schedules/IDRM-IMPLEMENTATION-GUIDE.md) | Week-by-week implementation timeline |

---

### 🤝 Contributor & Project Docs (root)

| Document | Purpose |
|----------|---------|
| [`CLAUDE.md`](./CLAUDE.md) | AI context file — architecture constraints, API quick reference, enum values |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | How to contribute — coding standards, PR process, code review checklist |
| [`RELEASE-NOTES.md`](./RELEASE-NOTES.md) | Release history and changelogs |
| [`archive/MIGRATION-TO-MICROSERVICES-v3.md`](./archive/MIGRATION-TO-MICROSERVICES-v3.md) | Year 2–3 migration plan (future reference only) |

---

## 💻 Development Workflow

### Starting All Services (5 Terminals Required)

> All 5 must run simultaneously. The Bun API Gateway (Terminal 2) is the **front door** —
> all browser traffic goes through it. Skipping it makes the app unreachable.

```bash
# Terminal 1 — FastAPI Modular Monolith (ALL backend modules on port 8000)
cd src/backend/app-python
conda activate idrm-mvp
uvicorn main:app --reload --port 8000

# Terminal 2 — Bun API Gateway (routes, JWT validation, rate limiting)
cd src/backend/api-gateway
bun run dev                    # HTTP: port 3000 · WebSocket: port 3001

# Terminal 3 — HTML/Tailwind (citizen-facing web)
cd src/frontend/web-html
bun run dev                    # Port 5173

# Terminal 4 — React SPA (admin dashboards)
cd src/frontend/web-react
bun run dev                    # Port 5174

# Terminal 5 — React Native (field-worker mobile app — optional during early dev)
cd src/frontend/mobile-expo
npx expo start
```

### Access Points

| Service | URL | Notes |
|---------|-----|-------|
| **Citizen Web** | http://localhost:5173 | Primary web interface |
| **Admin Dashboard** | http://localhost:5174 | Admin / coordinator dashboard |
| **API Gateway** | http://localhost:3000 | All API calls go here |
| **FastAPI Swagger UI** | http://localhost:8000/docs | Backend-only API exploration |
| **Mobile** | Expo Dev Tools | Scan QR with Expo Go app |

### Database Setup

```bash
# One-time database initialisation (after PostgreSQL is installed and running)
psql -U idrm_user -d idrm_db -f database/init/01-extensions.sql
psql -U idrm_user -d idrm_db -f database/init/02-schema.sql
psql -U idrm_user -d idrm_db -f database/init/03-seed-data.sql
```

### Running Tests

```bash
# Backend (from src/backend/app-python/)
conda activate idrm-mvp
pytest --cov=. --cov-report=html

# API Gateway (from src/backend/api-gateway/)
bun test

# Frontend React (from src/frontend/web-react/)
bun test
```

### Verify Installation

```bash
./scripts/setup-prerequisites.sh

# Should report:
# ✅ Bun 1.x
# ✅ Python 3.11 (Miniconda — idrm-mvp env)
# ✅ PostgreSQL 16
# ✅ PostGIS 3.4
# ✅ Redis 7.2+
```

---

## 🚀 Deployment Options

### Development (Local — 5 Terminals)

```bash
# Native — no Docker, hot-reload on all platforms
# Resource usage: ~1.5–2.5 GB RAM
# → See "Starting All Services" above
```

**Best for**: Daily development, fast iteration (<100 ms reload)

---

### Staging (Docker)

```bash
cp .env.staging.example .env.staging
# Edit .env.staging with staging credentials
docker-compose -f infra/docker/full-stack.yml up -d
docker-compose -f infra/docker/full-stack.yml exec backend alembic upgrade head

# Verify
curl https://staging.idrm.example.com/health
```

Full details: [`docs/IDRM-DEPLOYMENT-GUIDE.md`](./docs/IDRM-DEPLOYMENT-GUIDE.md)

---

### Production (Cloud)

```bash
./scripts/setup-production.sh
```

Architecture: Load Balancer (NGINX) → Blue/Green Docker deployments → Prometheus + Grafana monitoring → Automated PostgreSQL backups to S3.

Full details: [`start-here/COMPLETE-DevSecOps-GUIDE.md`](./start-here/COMPLETE-DevSecOps-GUIDE.md)

---

## 📊 Current Status

### Code Implementation

```
Database schema:    ██████████████████░░  90% (schema written; Alembic migrations pending)
Backend APIs:       ████░░░░░░░░░░░░░░░░  20%
API Gateway:        ███░░░░░░░░░░░░░░░░░  15%
Web Frontend:       ███░░░░░░░░░░░░░░░░░  15%
Admin Dashboard:    █░░░░░░░░░░░░░░░░░░░   5%
Mobile App:         █░░░░░░░░░░░░░░░░░░░   5%
Testing:            ██░░░░░░░░░░░░░░░░░░  10%
──────────────────────────────────────────
Overall code:       ████░░░░░░░░░░░░░░░░  20% 🏗️
```

### What's Complete ✅

- ✅ Full system architecture design (Modular Monolith + 3 frontends)
- ✅ Complete database schema — tables, indexes, views, functions, triggers
- ✅ Full API specification (37 endpoints with RBAC, security, examples)
- ✅ Design system (colours, typography, components)
- ✅ CI/CD pipeline design
- ✅ Deployment scripts (dev, staging, production)
- ✅ 43 documentation files covering every aspect of the system

### What's Next 🏗️

- 🏗️ Complete backend API implementations
- 🏗️ All three frontend platforms
- 🏗️ Unit + integration + E2E tests
- 🏗️ Staging deployment
- 🏗️ Production go-live

---

## 🗓️ Roadmap

### Phase 1: Foundation (Weeks 1–2)

- [x] Database schema design
- [ ] Run `database/init/` scripts → initialise PostgreSQL + PostGIS
- [ ] User authentication (register, login, JWT)
- [ ] Basic service request CRUD
- [ ] HTML/Tailwind skeleton

**Goal**: Can register, log in, and create a service request

---

### Phase 2: Core Features (Weeks 3–6)

- [ ] Geospatial queries (nearby requests via PostGIS)
- [ ] Map view (Leaflet)
- [ ] Full service request lifecycle (approve → accept → complete → verify)
- [ ] Role-based access control

**Goal**: Citizens can create requests; providers can accept and complete them

---

### Phase 3: Multi-Platform (Weeks 7–10)

- [ ] React SPA admin dashboard + analytics
- [ ] React Native mobile app
- [ ] GPS and camera integration (mobile)
- [ ] Real-time WebSocket events

**Goal**: All three platforms working end-to-end

---

### Phase 4: Polish & Test (Weeks 11–13)

- [ ] Full test coverage (unit, integration, E2E)
- [ ] Notifications (email, SMS, push)
- [ ] Error handling and loading states
- [ ] Performance optimisation

**Goal**: Production-ready quality

---

### Phase 5: Deploy (Weeks 14–16)

- [ ] Staging deployment + team testing
- [ ] Production deployment
- [ ] Monitoring setup (Prometheus + Grafana)
- [ ] Mobile app store submission (iOS + Android)

**Goal**: Live and serving users

---

### Which Frontend Should I Build First?

| Build first if... | HTML/Tailwind | React SPA | React Native |
|-------------------|:---:|:---:|:---:|
| Need MVP fastest | ✅ Best | — | — |
| Target general public | ✅ Best | — | — |
| Team knows React well | — | ✅ Best | — |
| Admin tools are priority | — | ✅ Best | — |
| Field workers are primary users | — | — | ✅ Best |
| Must work offline | — | — | ✅ Best |

**Recommended order**: HTML/Tailwind → React SPA → React Native

---

### Timeline Estimates

| Team Size | Full-Time | Part-Time | Hobby |
|-----------|-----------|-----------|-------|
| **Solo** | 3–4 months | 6–8 months | 12+ months |
| **2–3 people** | 2–3 months | 4–6 months | 8–12 months |
| **4+ people** | 1.5–2 months | 3–4 months | 6–8 months |

Full breakdown: [`schedules/IDRM-MVP-ANALYSIS-ROADMAP.md`](./schedules/IDRM-MVP-ANALYSIS-ROADMAP.md)

---

## 🤝 Contributing

### How to Contribute

1. **Read the guide**: [`CONTRIBUTING.md`](./CONTRIBUTING.md) — coding standards, PR process, review checklist
2. **Find an issue**: GitHub Issues
3. **Fork** and clone your fork
4. **Branch**: `git checkout -b feature/my-feature`
5. **Code** following the standards in `CONTRIBUTING.md`
6. **Test**: All tests must pass
7. **Commit**: `git commit -m "feat(api): add search endpoint for services"`
8. **PR**: Create Pull Request with the template from `CONTRIBUTING.md`

### Areas We Need Help

| Area | Skills Needed | Difficulty |
|------|---------------|------------|
| **Backend APIs** | Python, FastAPI, SQLAlchemy | 🟡 Medium |
| **Web Frontend** | HTML, CSS, JavaScript, Tailwind | 🟢 Easy |
| **Admin Dashboard** | React, TypeScript | 🟡 Medium |
| **Mobile App** | React Native, Expo | 🟡 Medium |
| **Geospatial** | Python, GeoPandas, PostGIS | 🔴 Hard |
| **Testing** | pytest, Vitest | 🟢 Easy |
| **Documentation** | Technical writing | 🟢 Easy |
| **Translation** | Hindi, Telugu | 🟢 Easy |
| **DevOps** | Docker, GitHub Actions | 🔴 Hard |

---

## 🗺️ Quick Navigation

### New to the Project?

| What you want | Go to |
|--------------|-------|
| Complete beginner guide | [`start-here/COMPLETE-BEGINNERS-GUIDE.md`](./start-here/COMPLETE-BEGINNERS-GUIDE.md) |
| Install and run the project | [`start-here/COMPLETE-SETUP-GUIDE.md`](./start-here/COMPLETE-SETUP-GUIDE.md) |
| Understand the architecture | [`docs/IDRM-ARCHITECTURE-GUIDE.md`](./docs/IDRM-ARCHITECTURE-GUIDE.md) |
| See a diagram of the system | [`docs/diagrams/IDRM-System-Architecture.md`](./docs/diagrams/IDRM-System-Architecture.md) |

### Ready to Code?

| What you want | Go to |
|--------------|-------|
| All API endpoints (37) | [`start-here/COMPLETE-API-SPECS-GUIDE.md`](./start-here/COMPLETE-API-SPECS-GUIDE.md) |
| Database schema + SQL | [`docs/development/IDRM-LLD.md`](./docs/development/IDRM-LLD.md) |
| Daily commands cheat sheet | [`start-here/QUICK-CMD-REFERENCE.md`](./start-here/QUICK-CMD-REFERENCE.md) |
| Coding standards | [`CONTRIBUTING.md`](./CONTRIBUTING.md) |
| Design system (UI) | [`start-here/COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md`](./start-here/COMPLETE-UI-UX-DESIGN-SYSTEM-GUIDE.md) |
| Architecture decisions | [`CLAUDE.md`](./CLAUDE.md) |

### Ready to Deploy?

| What you want | Go to |
|--------------|-------|
| Staging + production setup | [`docs/IDRM-DEPLOYMENT-GUIDE.md`](./docs/IDRM-DEPLOYMENT-GUIDE.md) |
| CI/CD and security | [`start-here/COMPLETE-DevSecOps-GUIDE.md`](./start-here/COMPLETE-DevSecOps-GUIDE.md) |
| Monitoring setup | [`start-here/COMPLETE-MONITORING-GUIDE.md`](./start-here/COMPLETE-MONITORING-GUIDE.md) |

### Looking for Something Specific?

| What you want | Go to |
|--------------|-------|
| Gap analysis (what to build) | [`schedules/IDRM-MVP-ANALYSIS-ROADMAP.md`](./schedules/IDRM-MVP-ANALYSIS-ROADMAP.md) |
| Redis caching patterns | [`docs/IDRM-Redis-Operations.md`](./docs/IDRM-Redis-Operations.md) |
| Bun Gateway internals | [`docs/IDRM-Bun-Gateway-Guide.md`](./docs/IDRM-Bun-Gateway-Guide.md) |
| Test data generation | [`docs/IDRM-Mock-Data-Guide.md`](./docs/IDRM-Mock-Data-Guide.md) |
| Future microservices plan | [`archive/MIGRATION-TO-MICROSERVICES-v3.md`](./archive/MIGRATION-TO-MICROSERVICES-v3.md) |

---

## 📄 License

Open Source — built for the public good, designed to save lives during disasters.

---

## 🙏 Acknowledgments

Built with **FastAPI · PostgreSQL + PostGIS · Bun · React · React Native · Tailwind CSS · Expo**.  
Inspired by disaster response needs across India and open-source emergency management systems.

---

## 📞 Getting Help

- **Setup problems**: [`start-here/COMPLETE-SETUP-GUIDE.md`](./start-here/COMPLETE-SETUP-GUIDE.md) § Common Troubleshooting
- **API questions**: [`start-here/COMPLETE-API-SPECS-GUIDE.md`](./start-here/COMPLETE-API-SPECS-GUIDE.md)
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and ideas

---

## 📊 Quick Stats

```
Documents:            43 markdown files across 8 folders
API Endpoints:        37 (fully documented with security annotations)
Database Tables:      6 (users, service_requests, organizations, notifications, audit_logs, disaster_types)
Backend Modules:      5 (auth, services, geo, analytics, notifications — all on port 8000)
Frontend Platforms:   3 (HTML/Tailwind · React SPA · React Native)
Languages:            Python · TypeScript · JavaScript · SQL
Lines of Docs:        15,000+ (current)
Lines of Code:        ~50,000+ (target)
Time to Deploy:       1.5–4 months depending on team size
```

---

**Built with ❤️ for India | Version 3.0 | Modular Monolith · 3 Platforms · Open Source**

**Join us in building technology that saves lives.** 🚀
