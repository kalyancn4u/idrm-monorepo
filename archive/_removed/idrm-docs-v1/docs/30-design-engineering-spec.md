> *Type: Document (specification) · Audience: Developers, architects · Status: Archived — v1 historical generation*

# IDRM Platform Engineering Specification

> This document defines the mandatory engineering, architecture, scalability, security, and reliability standards for the Integrated Disaster Response Management (IDRM) Platform.

> All AI-generated code, human-written code, infrastructure, and integrations MUST follow these guidelines.

<!-- IDRM-CLEANUP doc=v1-30-engspec status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ SECTION MAP (annotation pass, 2026-08-16)
> Gen-1 engineering spec. **Key split:** the **FSD (Feature-Sliced Design) + TypeScript + Zod + component
> architecture** here is **FFP frontend** — now `docs/ffp/61-frontend-engineering-standards.md` (the MVP UI is
> plain HTML+Tailwind+**vanilla JS**+Leaflet, ADR-004). Vanilla-JS/Leaflet/PostGIS parts are MVP. *Legend:* ✅
> covered · ⚠ superseded · ⊘ dropped/FFP.
>
> | Snippet | Section group | → Addressed in | Phase | Verdict |
> |---|---|---|---|---|
> | `v1-30§prin` | Project Context · Mandatory Principles (1.1) | eng principles in `instructions.txt` + `docs/mvp/20` | MVP | ✅ |
> | `v1-30§arch` | System Architecture (2.1: FE/BE/DB/caching/geo/proxy/deploy) | `docs/mvp/20`; caching(Redis)+proxy(gateway) → FFP | MVP/FFP | ⚠ |
> | `v1-30§ms` | Microservices (2.2) | `docs/ffp/20` | FFP | ⊘ |
> | `v1-30§fsd` | FSD overview · project structure · import rules (3.x) | `docs/ffp/61` (FFP frontend) | FFP | ⊘ |
> | `v1-30§ts` | Type Safety · Zod Validation (4.x) | `docs/ffp/61` (TypeScript/Zod = FFP) | FFP | ⊘ |
> | `v1-30§js` | Vanilla-JS patterns: module/component/state/API-client/form (5.x) | `docs/mvp/60` (MVP web UI) | MVP | ⚠ |
> | `v1-30§geo` | Leaflet init · geospatial handling · real-time map (6.x) | `docs/mvp/60` (Leaflet); real-time → FFP | MVP/FFP | ⚠ |
> | `v1-30§gw` | Express.js + Bun gateway · auth middleware · WebSocket (7.x) | edge/gateway → FFP (`api-gateway`/`backend-services`) | FFP | ⊘ |
> | `v1-30§pg` | PostGIS Database Schema (9.1) | `docs/mvp/50` | MVP | ⚠ |
>
> *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Project Context: IDRM Platform

The Integrated Disaster Response Management Platform (IDRM) is a unified, map-driven, privacy-first digital platform designed to enable timely, coordinated, transparent disaster response in India. The system serves as a national-scale digital coordination system connecting information flow, logistics, people, and accountability mechanisms.

**Core Capabilities:**
- Real-time geospatial mapping and visualization
- Service request and provider coordination
- Privacy-first architecture with ReVV (Request Verification and Validation)
- Role-based access control (RBAC)
- Financial transparency for donations and allocations
- Comprehensive audit trails
- Real-time communication and notifications

---

# 1. Core Engineering Principles

## 1.1 Mandatory Principles

The application MUST follow:

- **SOLID Principles**
- **DRY (Don't Repeat Yourself)**
- **KISS (Keep It Simple)**
- **Separation of Concerns**
- **High Cohesion, Low Coupling**
- **Composition over Inheritance**
- **Reusable Component Architecture**
- **Type Safety**
- **Accessibility First Development**

---

# 2. IDRM Technology Stack

## 2.1 System Architecture Overview

```
┌─────────────────────────────────────────┐
│     Presentation Layer (Web Client)     │
│    Leaflet Maps | HTML/CSS/JS/React     │
└─────────────────────────────────────────┘
                  ↓ HTTPS
┌─────────────────────────────────────────┐
│    NGINX (Reverse Proxy, WAF, Cache)    │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│    API Gateway (Bun 1.x/Express.js)     │
│   Authentication | Routing | WebSocket  │
└─────────────────────────────────────────┘
        ↓                    ↓
┌───────────────┐    ┌──────────────────┐
│  Redis 7.2    │    │  GeoServer 2.24  │
└───────────────┘    └──────────────────┘
        ↓                    ↓
┌─────────────────────────────────────────┐
│ Business Logic (Python 3.11/FastAPI)    │
│  Service Mgmt | Analytics | Geospatial  │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│  PostgreSQL 16 + PostGIS 3.4            │
│   User | Service | Geo | Audit Data     │
└─────────────────────────────────────────┘
```

## Frontend

### Primary Web Interface (Default - Enabled)
**Pure HTML/CSS/JavaScript Stack:**
- **HTML5** (semantic markup)
- **CSS3** with **TailwindCSS** (utility-first styling)
- **Vanilla JavaScript** (ES6+)
- **Leaflet 1.9** (interactive maps - MANDATORY for IDRM)
- **Leaflet Plugins** (MarkerCluster, Draw, Routing)
- **Bun** (build tool and module bundler)
- **Vite** (dev server and bundler)
- **Axios** or **Fetch API** (HTTP requests)
- **Socket.io Client** (real-time updates)
- **Alpine.js** (optional, for reactive components)

### Secondary Web Interface (React-based)
**React Application Stack:**
- **React** (with TypeScript)
- **Bun** (package manager and runtime)
- **Vite** (build tool)
- **TailwindCSS** (styling)
- **React Leaflet** (React components for Leaflet maps)
- **React Query / TanStack Query** (data fetching)
- **React Hook Form** (form management)
- **Zod** (schema validation)
- **Zustand** or **Redux Toolkit** (state management, only if needed)
- **Socket.io Client** (real-time communication)

### Mobile
- **React Native** with **Expo**
- **TypeScript**
- **React Navigation** (routing)
- **React Native Maps** (geospatial visualization)
- **React Query** (data fetching)
- **Zustand** (state management)

## Backend

### API Gateway & Real-time Services (Bun)
**Bun 1.x Runtime Stack:**
- **Bun 1.x** - Fast all-in-one JavaScript runtime (drop-in Node.js replacement)
- **Express.js 4.x** - Web application framework for REST APIs
- **Socket.io 4.x** - Real-time bidirectional communication (MANDATORY)
- **Passport.js** - Authentication middleware supporting JWT
- **Helmet.js** - Security middleware for HTTP headers
- **Express-validator** - Input validation and sanitization
- **Winston** - Logging framework
- **Morgan** - HTTP request logger
- **Joi** - Schema validation
- **pg (node-postgres)** - PostgreSQL client
- **ioredis** - Redis client

**Why Bun for API Gateway:**
- **Performance**: 3-4x faster than Node.js for HTTP requests
- **Built-in TypeScript**: Native TypeScript support without transpilation
- **Compatibility**: Drop-in replacement for Node.js APIs
- **Built-in bundler**: No need for separate build tools
- **Better memory usage**: More efficient than Node.js
- **Native WebSocket**: Built-in WebSocket support alongside Socket.io

### Data Processing & Analytics (Python)
**Python 3.11 Stack:**
- **FastAPI 0.104+** - Modern, fast web framework for building APIs
- **SQLAlchemy 2.0** - ORM for database operations
- **GeoAlchemy2** - Spatial extension for SQLAlchemy (MANDATORY)
- **Alembic** - Database migrations
- **Pandas** - Data manipulation and analysis
- **Celery 5.x** - Distributed task queue for async processing
- **Pydantic** - Data validation using Python type annotations
- **Shapely** - Geometric operations
- **Psycopg2** or **asyncpg** - PostgreSQL adapter

## Database & Caching

### PostgreSQL 16 + PostGIS 3.4 (MANDATORY)
**Primary relational database with geospatial capabilities:**
- PostGIS extension for geospatial data types and operations
- Supports point, line, polygon geometries with spatial indexing
- R-tree indexes for efficient spatial queries
- Over 1000 geospatial operations
- Spatial functions: ST_Distance, ST_Contains, ST_Intersects, ST_Buffer
- ACID compliance for transactional integrity

### Redis 7.2 (MANDATORY)
**In-memory data store:**
- Session management and JWT token blacklisting
- Real-time data caching
- Message queue for pub/sub patterns
- Rate limiting implementation
- Sub-millisecond latency

## Geospatial Services (MANDATORY for IDRM)

### GeoServer 2.24
**OGC-compliant map server:**
- Web Map Service (WMS) for map rendering
- Web Feature Service (WFS) for vector data
- Web Coverage Service (WCS) for raster data
- Connects to PostGIS for spatial data
- Supports SLD (Styled Layer Descriptor) for map visualization
- REST API for programmatic control

### Leaflet 1.9
**Frontend mapping library:**
- Lightweight and mobile-friendly
- Plugin ecosystem for extended functionality
- WMS/WFS integration with GeoServer
- Custom markers, popups, and overlays
- Geolocation support
- Drawing and editing tools

## Web Server & Proxy

### NGINX 1.24 (MANDATORY)
**Reverse proxy and web server:**
- Reverse proxy for Node.js and Python services
- Web Application Firewall (WAF) capabilities
- SSL/TLS termination
- Static file serving and caching
- Load balancing across service instances
- Rate limiting and DDoS protection

## Development & Deployment

### Docker 24.x & Docker Compose (MANDATORY)
- Container orchestration
- Service isolation
- Development-production parity
- Multi-container applications

### Git
- Version control system
- Branch strategy: GitFlow or trunk-based development

---

## 2.2 IDRM Microservices Architecture

The IDRM platform implements a microservices pattern with clear separation of concerns:

### Core Microservices

**1. Authentication Service** (Bun/Express.js)
- **Responsibilities:**
  - JWT token generation and validation
  - OAuth 2.0 integration capability
  - Session management with Redis
  - Token blacklisting on logout
  - Password hashing and verification
  - Multi-factor authentication (MFA)
- **Technology:** Bun 1.x, Express.js, Passport.js, Redis, bcrypt

**2. Service Management Service** (Python/FastAPI)
- **Responsibilities:**
  - CRUD operations for service requests
  - Provider matching algorithms
  - Status tracking and updates
  - Task assignment logic
  - Service request validation
- **Technology:** Python, FastAPI, SQLAlchemy, GeoAlchemy2

**3. Geospatial Service** (Python/FastAPI)
- **Responsibilities:**
  - Spatial queries and analysis
  - Location-based service matching
  - Distance calculations (ST_Distance)
  - Proximity search
  - Clustering algorithms
  - Geocoding and reverse geocoding
- **Technology:** Python, FastAPI, GeoAlchemy2, Shapely, PostGIS

**4. Communication Service** (Bun/Socket.io)
- **Responsibilities:**
  - Real-time notifications
  - WebSocket connections
  - Broadcast mechanisms
  - Message queuing
  - Push notifications
- **Technology:** Bun 1.x, Socket.io, Redis (pub/sub)

**5. Analytics Service** (Python/FastAPI)
- **Responsibilities:**
  - Data aggregation
  - Report generation
  - Dashboard metrics
  - Audit log processing
  - Statistical analysis
  - Performance metrics
- **Technology:** Python, FastAPI, Pandas, SQLAlchemy

**6. Financial Service** (Python/FastAPI)
- **Responsibilities:**
  - Donation tracking
  - Allocation management
  - Transparent accounting
  - Fund flow auditing
  - Financial reporting
- **Technology:** Python, FastAPI, SQLAlchemy, Pydantic

**7. Privacy Service** (Python/FastAPI)
- **Responsibilities:**
  - ReVV (Request Verification and Validation) implementation
  - Data anonymization
  - Privacy controls enforcement
  - Consent management
  - Data access logging
- **Technology:** Python, FastAPI, SQLAlchemy

### Service Communication Patterns

**Synchronous Communication:**
- HTTP/REST API calls between services
- API Gateway routes requests to appropriate services
- Request/Response pattern for CRUD operations

**Asynchronous Communication:**
- Redis pub/sub for event broadcasting
- Celery for background task processing
- WebSocket for real-time updates

**Data Consistency:**
- Each service owns its data
- Eventual consistency for cross-service operations
- Event-driven updates for data synchronization

---

# 3. Feature-Sliced Design (FSD) Architecture

## 3.1 FSD Overview

The application MUST follow **Feature-Sliced Design** methodology for predictable, scalable, and maintainable architecture.

### FSD Layers (from top to bottom):

1. **app** - Application initialization, global providers, routing
2. **processes** - Complex business processes spanning multiple pages/features
3. **pages** - Full page components, route-level composition
4. **widgets** - Complex UI blocks composed of features and entities
5. **features** - User interactions, business features (add to cart, auth, etc.)
6. **entities** - Business entities (user, product, order, etc.)
7. **shared** - Reusable infrastructure, UI kit, utilities

### FSD Slices:

Each layer (except `app` and `shared`) is divided into **slices** representing business domains.

### FSD Segments (inside each slice):

- **ui/** - React components, styles
- **model/** - Business logic, state management, stores
- **api/** - API requests, data fetching
- **lib/** - Infrastructure logic, utilities
- **config/** - Configuration, constants
- **types/** - TypeScript types/interfaces

---

## 3.2 IDRM Project Structure

```
project-root/
├── apps/
│   ├── web/                    # Primary Web (DEFAULT - ENABLED)
│   │   │                       # Pure HTML/CSS/JS + Tailwind + Leaflet
│   │   ├── src/
│   │   │   ├── index.html     # Entry point
│   │   │   ├── js/            # JavaScript modules
│   │   │   │   ├── main.js
│   │   │   │   ├── map/       # Leaflet map components (IDRM-specific)
│   │   │   │   │   ├── map-init.js
│   │   │   │   │   ├── layers.js
│   │   │   │   │   ├── markers.js
│   │   │   │   │   └── geolocation.js
│   │   │   │   ├── api/       # API client
│   │   │   │   │   ├── client.js
│   │   │   │   │   ├── services.js
│   │   │   │   │   ├── auth.js
│   │   │   │   │   └── websocket.js
│   │   │   │   ├── components/ # Reusable JS components
│   │   │   │   │   ├── navbar.js
│   │   │   │   │   ├── service-card.js
│   │   │   │   │   ├── donation-form.js
│   │   │   │   │   └── modal.js
│   │   │   │   ├── pages/     # Page-specific logic
│   │   │   │   │   ├── home.js
│   │   │   │   │   ├── map-view.js
│   │   │   │   │   ├── service-request.js
│   │   │   │   │   └── donations.js
│   │   │   │   └── utils/     # Utilities
│   │   │   │       ├── dom.js
│   │   │   │       ├── validation.js
│   │   │   │       └── storage.js
│   │   │   ├── css/           # Stylesheets
│   │   │   │   ├── main.css   # Main entry (imports Tailwind)
│   │   │   │   ├── components/
│   │   │   │   └── pages/
│   │   │   ├── pages/         # HTML pages
│   │   │   │   ├── index.html
│   │   │   │   ├── map.html
│   │   │   │   ├── services.html
│   │   │   │   └── donations.html
│   │   │   └── assets/        # Images, fonts, etc.
│   │   ├── public/
│   │   ├── package.json
│   │   ├── tailwind.config.js
│   │   └── vite.config.js
│   │
│   ├── web-react/              # Secondary Web (React-based Admin/Dashboard)
│   │   ├── src/
│   │   │   ├── app/           # App layer
│   │   │   ├── processes/
│   │   │   ├── pages/         # IDRM-specific pages
│   │   │   │   ├── dashboard/
│   │   │   │   ├── disaster-management/
│   │   │   │   ├── service-coordination/
│   │   │   │   ├── analytics/
│   │   │   │   └── financial-tracking/
│   │   │   ├── widgets/
│   │   │   │   ├── map-widget/
│   │   │   │   ├── stats-panel/
│   │   │   │   └── audit-log/
│   │   │   ├── features/      # IDRM features
│   │   │   │   ├── auth/
│   │   │   │   ├── service-request/
│   │   │   │   ├── provider-matching/
│   │   │   │   ├── real-time-notifications/
│   │   │   │   └── donation-management/
│   │   │   ├── entities/      # Business entities
│   │   │   │   ├── user/
│   │   │   │   ├── service/
│   │   │   │   ├── provider/
│   │   │   │   ├── disaster-event/
│   │   │   │   └── donation/
│   │   │   └── shared/
│   │   │       ├── ui/
│   │   │       ├── api/
│   │   │       ├── lib/
│   │   │       │   ├── websocket.ts
│   │   │       │   └── geo-utils.ts
│   │   │       └── config/
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   └── vite.config.ts
│   │
│   └── mobile/                 # React Native mobile app
│       ├── src/
│       │   ├── app/
│       │   ├── features/
│       │   │   ├── service-request/
│       │   │   ├── map-view/
│       │   │   └── notifications/
│       │   ├── entities/
│       │   └── shared/
│       ├── package.json
│       └── app.json
│
├── services/                   # Backend Microservices
│   ├── api-gateway/           # Bun API Gateway (MANDATORY)
│   │   ├── src/
│   │   │   ├── index.js
│   │   │   ├── config/
│   │   │   │   ├── database.js
│   │   │   │   ├── redis.js
│   │   │   │   └── env.js
│   │   │   ├── routes/
│   │   │   │   ├── auth.routes.js
│   │   │   │   ├── services.routes.js
│   │   │   │   └── proxy.routes.js
│   │   │   ├── middleware/
│   │   │   │   ├── auth.middleware.js
│   │   │   │   ├── validation.middleware.js
│   │   │   │   ├── error-handler.js
│   │   │   │   └── rate-limiter.js
│   │   │   ├── websocket/
│   │   │   │   ├── socket-server.js
│   │   │   │   └── handlers/
│   │   │   └── utils/
│   │   ├── tests/
│   │   ├── package.json
│   │   └── .env.example
│   │
│   ├── auth-service/          # Authentication Service (Bun)
│   │   ├── src/
│   │   │   ├── controllers/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── utils/
│   │   ├── tests/
│   │   └── package.json
│   │
│   ├── service-management/    # Service Management (Python/FastAPI)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   │       ├── endpoints/
│   │   │   │       │   ├── services.py
│   │   │   │       │   └── providers.py
│   │   │   │       └── api.py
│   │   │   ├── core/
│   │   │   │   ├── config.py
│   │   │   │   ├── security.py
│   │   │   │   └── database.py
│   │   │   ├── models/
│   │   │   │   ├── service.py
│   │   │   │   └── provider.py
│   │   │   ├── schemas/
│   │   │   ├── services/
│   │   │   │   ├── matching.py
│   │   │   │   └── assignment.py
│   │   │   └── repositories/
│   │   ├── tests/
│   │   ├── alembic/
│   │   ├── pyproject.toml
│   │   └── requirements.txt
│   │
│   ├── geospatial-service/    # Geospatial Service (Python/FastAPI)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   │   └── v1/
│   │   │   │       ├── endpoints/
│   │   │   │       │   ├── spatial.py
│   │   │   │       │   └── geocoding.py
│   │   │   ├── core/
│   │   │   ├── services/
│   │   │   │   ├── spatial_analysis.py
│   │   │   │   └── clustering.py
│   │   │   └── utils/
│   │   │       └── geo_utils.py
│   │   ├── tests/
│   │   └── pyproject.toml
│   │
│   ├── communication-service/ # Communication (Bun/Socket.io)
│   │   ├── src/
│   │   │   ├── index.js
│   │   │   ├── socket/
│   │   │   ├── notifications/
│   │   │   └── pubsub/
│   │   └── package.json
│   │
│   ├── analytics-service/     # Analytics (Python/FastAPI)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   │   ├── aggregation.py
│   │   │   │   └── reporting.py
│   │   │   └── models/
│   │   └── pyproject.toml
│   │
│   ├── financial-service/     # Financial Tracking (Python/FastAPI)
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/
│   │   │   ├── services/
│   │   │   │   ├── donations.py
│   │   │   │   └── allocations.py
│   │   │   └── models/
│   │   └── pyproject.toml
│   │
│   └── privacy-service/       # Privacy/ReVV (Python/FastAPI)
│       ├── app/
│       │   ├── main.py
│       │   ├── api/
│       │   ├── services/
│       │   │   ├── revv.py
│       │   │   ├── anonymization.py
│       │   │   └── consent.py
│       │   └── models/
│       └── pyproject.toml
│
├── packages/                   # Shared packages
│   ├── shared-types/          # Shared TypeScript/Python types
│   ├── shared-utils/          # Shared utilities
│   └── api-client/            # Shared API client
│
├── infrastructure/
│   ├── nginx/
│   │   ├── nginx.conf
│   │   ├── sites-available/
│   │   └── ssl/
│   ├── geoserver/
│   │   ├── data_dir/
│   │   ├── styles/
│   │   └── workspaces/
│   ├── redis/
│   │   └── redis.conf
│   └── postgres/
│       ├── init.sql
│       └── postgis-setup.sql
│
├── docker/
│   ├── Dockerfile.web
│   ├── Dockerfile.web-react
│   ├── Dockerfile.api-gateway
│   ├── Dockerfile.python-service
│   └── Dockerfile.geoserver
│
├── docker-compose.yml
├── docker-compose.prod.yml
├── package.json               # Root package.json (workspaces)
└── README.md
```
├── packages/                   # Shared packages (monorepo)
│   ├── shared-types/          # Shared TypeScript types
│   ├── shared-utils/          # Shared utilities
│   └── api-client/            # Shared API client
│
├── backend/                    # Python backend
│   ├── app/
│   │   ├── main.py            # FastAPI app entry
│   │   ├── api/               # API routes
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── auth.py
│   │   │   │   │   ├── users.py
│   │   │   │   │   └── products.py
│   │   │   │   └── api.py
│   │   ├── core/              # Core functionality
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/            # Database models
│   │   │   ├── user.py
│   │   │   └── product.py
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── user.py
│   │   │   └── product.py
│   │   ├── services/          # Business logic
│   │   │   ├── auth.py
│   │   │   └── product.py
│   │   ├── repositories/      # Data access layer
│   │   │   ├── user.py
│   │   │   └── product.py
│   │   └── utils/             # Utilities
│   ├── alembic/               # Database migrations
│   ├── tests/
│   ├── pyproject.toml
│   └── poetry.lock
│
├── docker/
│   ├── Dockerfile.web
│   ├── Dockerfile.mobile
│   └── Dockerfile.backend
│
├── docker-compose.yml
├── package.json               # Root package.json (workspaces)
└── README.md
```

---

## 3.3 Web Interfaces Overview

### Primary Web Interface (apps/web)
**Status:** DEFAULT - ALWAYS ENABLED  
**Technology:** Pure HTML/CSS/JavaScript + Tailwind CSS

**Purpose:**
- Main customer-facing website
- Public-facing web pages
- E-commerce storefront or content site
- Optimized for SEO and performance
- Fast initial page load
- Progressive enhancement approach

**Why Vanilla JS:**
- ⚡ **Performance**: No framework overhead, faster initial load
- 🎯 **SEO**: Server-rendered HTML, better search engine indexing
- 📦 **Lightweight**: Smaller bundle size
- 🔧 **Simple**: Easier to maintain for content-heavy sites
- 💰 **Cost-effective**: Better hosting options, CDN-friendly

**Use Cases:**
- Marketing website / landing pages
- E-commerce product catalog
- Blog / content platform
- Public documentation
- Customer-facing features

**Technology Stack:**
- HTML5 (semantic markup)
- CSS3 + TailwindCSS (utility-first styling)
- Vanilla JavaScript ES6+ (modular architecture)
- Vite (dev server and bundler)
- Axios/Fetch (API communication)
- Alpine.js (optional, for reactive components)

**Architecture Pattern:**
```
src/
├── js/
│   ├── api/          # API client modules
│   ├── components/   # Reusable components
│   ├── pages/        # Page-specific logic
│   └── utils/        # Shared utilities
├── css/              # Stylesheets
├── pages/            # HTML pages
└── assets/           # Static assets
```

---

### Secondary Web Interface (apps/web-react)
**Status:** OPTIONAL - React-based Application  
**Technology:** React + TypeScript + FSD Architecture

**Purpose:**
- Admin panel / dashboard
- Complex interactive features
- Data visualization and analytics
- Internal tools for staff
- Content Management System (CMS)
- Advanced user workflows

**Why React:**
- 🎨 **Complex UI**: Rich, interactive interfaces
- 🔄 **State Management**: Handle complex application state
- 🧩 **Component Reusability**: Sophisticated component patterns
- 📊 **Data Visualization**: Charts, graphs, real-time updates
- 🛠️ **Developer Experience**: Modern tooling, TypeScript support

**Use Cases:**
- Admin dashboard
- Analytics and reporting interface
- Content management system
- Staff tools and internal applications
- Advanced customer portals

**Technology Stack:**
- React + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- React Query (data fetching)
- Zustand (state management)
- React Router (routing)
- Full FSD (Feature-Sliced Design) architecture

**Architecture Pattern:**
Follows complete FSD structure with 7 layers:
- app → processes → pages → widgets → features → entities → shared

**Configuration:**
```json
// package.json - workspace scripts
{
  "scripts": {
    "dev:web": "bun --cwd apps/web run dev",
    "dev:react": "bun --cwd apps/web-react run dev",
    "dev:all": "bun run dev:web & bun run dev:react & bun run dev:mobile",
    "build:web": "bun --cwd apps/web run build",
    "build:react": "bun --cwd apps/web-react run build"
  }
}
```

### Routing Configuration

**Primary Web Interface (apps/web) - Multi-Page Application:**
```javascript
// apps/web/src/js/router.js
// Simple client-side routing for SPA behavior (optional)
class Router {
  constructor() {
    this.routes = new Map();
    this.currentPath = window.location.pathname;
  }

  register(path, handler) {
    this.routes.set(path, handler);
  }

  navigate(path) {
    window.history.pushState({}, '', path);
    this.handleRoute(path);
  }

  handleRoute(path) {
    const handler = this.routes.get(path);
    if (handler) {
      handler();
    }
  }

  init() {
    window.addEventListener('popstate', () => {
      this.handleRoute(window.location.pathname);
    });
    
    // Handle link clicks
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-link]')) {
        e.preventDefault();
        this.navigate(e.target.getAttribute('href'));
      }
    });
  }
}

// Usage
const router = new Router();
router.register('/', () => import('./pages/home.js'));
router.register('/products', () => import('./pages/products.js'));
router.init();
```

**Or Traditional Multi-Page Approach:**
```html
<!-- apps/web/src/pages/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Home</title>
  <link rel="stylesheet" href="/css/main.css">
</head>
<body>
  <nav>
    <a href="/">Home</a>
    <a href="/products.html">Products</a>
    <a href="/cart.html">Cart</a>
  </nav>
  <main id="app"></main>
  <script type="module" src="/js/main.js"></script>
</body>
</html>
```

**Secondary Web Interface (apps/web-react) - Single Page Application:**
```typescript
// apps/web-react/src/app/routes/index.tsx
import { createBrowserRouter } from 'react-router-dom';
import { DashboardPage } from '@/pages/dashboard';
import { UsersManagementPage } from '@/pages/users-management';
import { AnalyticsPage } from '@/pages/analytics';
import { ProtectedRoute } from '@/features/auth';

export const router = createBrowserRouter([
  {
    path: '/admin',
    element: <ProtectedRoute requiredRole="admin" />,
    children: [
      {
        path: 'dashboard',
        element: <DashboardPage />,
      },
      {
        path: 'users',
        element: <UsersManagementPage />,
      },
      {
        path: 'analytics',
        element: <AnalyticsPage />,
      },
    ],
  },
]);
```

### Shared Packages Configuration

Both web interfaces can share common code through the monorepo's `packages/` directory:

```typescript
// packages/shared-types/src/user.ts
export interface User {
  id: string;
  email: string;
  role: 'admin' | 'user' | 'guest';
}

// packages/api-client/src/index.ts
export { apiClient } from './client';
export { productApi } from './product-api';
```

**Import from shared packages:**
```javascript
// In apps/web (vanilla JS)
import { apiClient } from '@repo/api-client';
import { productApi } from '@repo/api-client';

// In apps/web-react (TypeScript)
import { User } from '@repo/shared-types';
import { apiClient } from '@repo/api-client';
```

---

## 3.4 FSD Import Rules (Public API)

**CRITICAL**: Follow strict import rules to maintain architecture boundaries.

### Allowed Imports:

- Lower layers can be imported by upper layers
- Slices on the same layer CANNOT import each other directly
- Each slice MUST export a public API through `index.ts`

### Example Public API:

```typescript
// entities/user/index.ts
export { UserCard } from './ui/user-card';
export { useUser } from './model/use-user';
export { userApi } from './api/user-api';
export type { User, UserRole } from './types';
```

### Import Examples:

✅ **CORRECT:**
```typescript
// features/add-to-cart/ui/add-button.tsx
import { Product } from '@/entities/product';
import { Button } from '@/shared/ui/button';
```

❌ **WRONG:**
```typescript
// features/add-to-cart/ui/add-button.tsx
import { ProductFilter } from '@/features/product-filter'; // Same layer!
import { ProductCard } from '@/entities/product/ui/product-card'; // Not public API!
```

---

# 4. TypeScript Standards

## 4.1 Type Safety

- **MUST** use TypeScript strict mode
- **MUST** define explicit return types for functions
- **MUST** use interfaces for object shapes
- **MUST** use type guards for runtime type checking
- **AVOID** using `any` - use `unknown` instead
- **USE** branded types for domain-specific values

```typescript
// Good
interface User {
  id: string;
  email: string;
  role: UserRole;
}

function getUser(id: string): Promise<User> {
  // implementation
}

// Bad
function getUser(id: any): any {
  // implementation
}
```

## 4.2 Zod Validation

Use Zod for runtime validation:

```typescript
import { z } from 'zod';

export const userSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  name: z.string().min(2).max(100),
  role: z.enum(['admin', 'user', 'guest']),
});

export type User = z.infer<typeof userSchema>;
```

---

# 5. Vanilla JavaScript Standards (Primary Web Interface)

## 5.1 Modern JavaScript (ES6+)

**MUST** use modern JavaScript features:
- ES6 modules (`import`/`export`)
- Arrow functions
- Template literals
- Destructuring
- Async/await for asynchronous code
- Classes for component-like structures
- Optional chaining (`?.`)
- Nullish coalescing (`??`)

```javascript
// Good: Modern ES6+ JavaScript
export class ProductCard {
  constructor(product) {
    this.product = product;
    this.element = null;
  }

  render() {
    const { name, price, image } = this.product;
    
    this.element = document.createElement('div');
    this.element.className = 'product-card p-4 border rounded-lg';
    this.element.innerHTML = `
      <img src="${image}" alt="${name}" class="w-full h-48 object-cover rounded">
      <h3 class="text-lg font-semibold mt-2">${name}</h3>
      <p class="text-gray-600">$${price.toFixed(2)}</p>
      <button class="btn-primary mt-2" data-product-id="${this.product.id}">
        Add to Cart
      </button>
    `;
    
    return this.element;
  }

  attachEventListeners() {
    const button = this.element.querySelector('button');
    button?.addEventListener('click', () => this.handleAddToCart());
  }

  async handleAddToCart() {
    try {
      await addToCart(this.product.id);
      showNotification('Added to cart!');
    } catch (error) {
      console.error('Failed to add to cart:', error);
      showNotification('Failed to add to cart', 'error');
    }
  }
}

// Bad: Old JavaScript
var ProductCard = function(product) {
  this.product = product;
  this.element = null;
}
```

## 5.2 Module Pattern

```javascript
// apps/web/src/js/api/products.js
import { apiClient } from './client.js';

export async function getAllProducts() {
  try {
    const response = await apiClient.get('/api/v1/products');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch products:', error);
    throw error;
  }
}

export async function getProductById(id) {
  const response = await apiClient.get(`/api/v1/products/${id}`);
  return response.data;
}

export async function createProduct(productData) {
  const response = await apiClient.post('/api/v1/products', productData);
  return response.data;
}
```

## 5.3 Component Pattern

Create reusable components using classes or factory functions:

```javascript
// apps/web/src/js/components/navbar.js
export class Navbar {
  constructor(containerId) {
    this.container = document.getElementById(containerId);
    this.cartCount = 0;
  }

  render() {
    this.container.innerHTML = `
      <nav class="bg-white shadow-lg">
        <div class="container mx-auto px-4">
          <div class="flex justify-between items-center py-4">
            <a href="/" class="text-2xl font-bold">MyStore</a>
            <div class="flex gap-4">
              <a href="/products.html" class="hover:text-blue-600">Products</a>
              <a href="/cart.html" class="hover:text-blue-600">
                Cart <span class="cart-count">(${this.cartCount})</span>
              </a>
            </div>
          </div>
        </div>
      </nav>
    `;
  }

  updateCartCount(count) {
    this.cartCount = count;
    const countElement = this.container.querySelector('.cart-count');
    if (countElement) {
      countElement.textContent = `(${count})`;
    }
  }
}

// Usage
import { Navbar } from './components/navbar.js';

const navbar = new Navbar('navbar-container');
navbar.render();
```

## 5.4 State Management (Vanilla JS)

Use a simple store pattern for state management:

```javascript
// apps/web/src/js/utils/store.js
class Store {
  constructor(initialState = {}) {
    this.state = initialState;
    this.listeners = [];
  }

  getState() {
    return { ...this.state };
  }

  setState(newState) {
    this.state = { ...this.state, ...newState };
    this.notify();
  }

  subscribe(listener) {
    this.listeners.push(listener);
    return () => {
      this.listeners = this.listeners.filter(l => l !== listener);
    };
  }

  notify() {
    this.listeners.forEach(listener => listener(this.state));
  }
}

// Create stores
export const cartStore = new Store({
  items: [],
  total: 0,
});

export const userStore = new Store({
  user: null,
  isAuthenticated: false,
});

// Usage
import { cartStore } from './utils/store.js';

// Subscribe to changes
cartStore.subscribe((state) => {
  console.log('Cart updated:', state);
  updateCartUI(state);
});

// Update state
cartStore.setState({ 
  items: [...cartStore.getState().items, newItem],
  total: calculateTotal()
});
```

## 5.5 API Client (Vanilla JS)

```javascript
// apps/web/src/js/api/client.js
class ApiClient {
  constructor(baseURL) {
    this.baseURL = baseURL;
    this.token = localStorage.getItem('auth-token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Handle unauthorized
          this.handleUnauthorized();
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('auth-token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('auth-token');
  }

  handleUnauthorized() {
    this.clearToken();
    window.location.href = '/login.html';
  }
}

export const apiClient = new ApiClient(import.meta.env.VITE_API_URL);
```

## 5.6 Form Handling

```javascript
// apps/web/src/js/utils/form-handler.js
export class FormHandler {
  constructor(formElement) {
    this.form = formElement;
    this.errors = {};
  }

  getData() {
    const formData = new FormData(this.form);
    return Object.fromEntries(formData.entries());
  }

  validate(rules) {
    this.errors = {};
    const data = this.getData();

    for (const [field, rule] of Object.entries(rules)) {
      const value = data[field];
      
      if (rule.required && !value) {
        this.errors[field] = `${field} is required`;
      }
      
      if (rule.minLength && value.length < rule.minLength) {
        this.errors[field] = `${field} must be at least ${rule.minLength} characters`;
      }
      
      if (rule.pattern && !rule.pattern.test(value)) {
        this.errors[field] = rule.message || `${field} is invalid`;
      }
    }

    return Object.keys(this.errors).length === 0;
  }

  showErrors() {
    // Clear previous errors
    this.form.querySelectorAll('.error-message').forEach(el => el.remove());
    
    // Show new errors
    for (const [field, message] of Object.entries(this.errors)) {
      const input = this.form.querySelector(`[name="${field}"]`);
      if (input) {
        const error = document.createElement('div');
        error.className = 'error-message text-red-500 text-sm mt-1';
        error.textContent = message;
        input.parentElement.appendChild(error);
      }
    }
  }

  async submit(handler) {
    const data = this.getData();
    try {
      await handler(data);
      this.form.reset();
    } catch (error) {
      console.error('Form submission failed:', error);
      throw error;
    }
  }
}

// Usage
import { FormHandler } from './utils/form-handler.js';

const loginForm = document.getElementById('login-form');
const formHandler = new FormHandler(loginForm);

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const isValid = formHandler.validate({
    email: { 
      required: true, 
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
      message: 'Invalid email address'
    },
    password: { 
      required: true, 
      minLength: 8 
    },
  });

  if (!isValid) {
    formHandler.showErrors();
    return;
  }

  await formHandler.submit(async (data) => {
    const response = await apiClient.post('/api/v1/auth/login', data);
    apiClient.setToken(response.token);
    window.location.href = '/dashboard.html';
  });
});
```

---

# 6. Leaflet & Geospatial Standards (MANDATORY for IDRM)

## 6.1 Leaflet Map Initialization

**MUST** use Leaflet 1.9 for all mapping functionality in the primary web interface.

```javascript
// apps/web/src/js/map/map-init.js
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

export class IDRMMap {
  constructor(containerId, options = {}) {
    this.container = containerId;
    this.map = null;
    this.layers = new Map();
    this.markers = new Map();
    
    // Default center: India
    this.defaultCenter = options.center || [20.5937, 78.9629];
    this.defaultZoom = options.zoom || 5;
  }

  init() {
    // Initialize map
    this.map = L.map(this.container, {
      center: this.defaultCenter,
      zoom: this.defaultZoom,
      zoomControl: true,
      attributionControl: true,
    });

    // Add base layer (OpenStreetMap)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(this.map);

    // Add GeoServer WMS layer
    this.addGeoServerLayer('idrm:disaster_zones', 'Disaster Zones');
    this.addGeoServerLayer('idrm:service_requests', 'Service Requests');

    return this;
  }

  addGeoServerLayer(layerName, displayName) {
    const wmsLayer = L.tileLayer.wms(
      `${import.meta.env.VITE_GEOSERVER_URL}/wms`,
      {
        layers: layerName,
        format: 'image/png',
        transparent: true,
        version: '1.1.0',
        attribution: 'IDRM Platform',
      }
    );

    this.layers.set(displayName, wmsLayer);
    wmsLayer.addTo(this.map);
  }

  addMarker(lat, lng, options = {}) {
    const marker = L.marker([lat, lng], {
      icon: this.getCustomIcon(options.type),
      title: options.title,
    });

    if (options.popup) {
      marker.bindPopup(options.popup);
    }

    marker.addTo(this.map);
    this.markers.set(options.id, marker);
    
    return marker;
  }

  getCustomIcon(type) {
    const iconMap = {
      'service-request': L.icon({
        iconUrl: '/assets/icons/service-marker.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
      }),
      'provider': L.icon({
        iconUrl: '/assets/icons/provider-marker.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32],
      }),
      'disaster-zone': L.icon({
        iconUrl: '/assets/icons/disaster-marker.png',
        iconSize: [40, 40],
        iconAnchor: [20, 40],
        popupAnchor: [0, -40],
      }),
    };

    return iconMap[type] || L.Icon.Default;
  }

  enableGeolocation() {
    this.map.locate({ setView: true, maxZoom: 16 });
    
    this.map.on('locationfound', (e) => {
      const radius = e.accuracy / 2;
      L.marker(e.latlng).addTo(this.map)
        .bindPopup(`You are within ${radius} meters from this point`);
      L.circle(e.latlng, radius).addTo(this.map);
    });

    this.map.on('locationerror', (e) => {
      console.error('Location error:', e.message);
    });
  }

  clearMarkers() {
    this.markers.forEach(marker => this.map.removeLayer(marker));
    this.markers.clear();
  }

  fitBounds(bounds) {
    this.map.fitBounds(bounds);
  }
}

// Usage
const idrm Map = new IDRMMap('map-container', {
  center: [28.6139, 77.2090], // Delhi
  zoom: 10,
});

idrmMap.init();
idrmMap.enableGeolocation();
```

## 6.2 Geospatial Data Handling

```javascript
// apps/web/src/js/map/layers.js
export class GeoDataManager {
  constructor(map) {
    this.map = map;
    this.geoJsonLayers = new Map();
  }

  async loadGeoJSON(url, layerName, style = {}) {
    try {
      const response = await fetch(url);
      const geoJsonData = await response.json();

      const layer = L.geoJSON(geoJsonData, {
        style: style.style || this.defaultStyle,
        onEachFeature: (feature, layer) => {
          if (feature.properties) {
            layer.bindPopup(this.createPopupContent(feature.properties));
          }
        },
        pointToLayer: (feature, latlng) => {
          return L.circleMarker(latlng, style.point || {
            radius: 8,
            fillColor: '#ff7800',
            color: '#000',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8,
          });
        },
      });

      layer.addTo(this.map.map);
      this.geoJsonLayers.set(layerName, layer);

      return layer;
    } catch (error) {
      console.error(`Failed to load GeoJSON layer ${layerName}:`, error);
      throw error;
    }
  }

  defaultStyle(feature) {
    return {
      color: '#3388ff',
      weight: 2,
      opacity: 0.6,
      fillOpacity: 0.3,
    };
  }

  createPopupContent(properties) {
    let content = '<div class="popup-content">';
    for (const [key, value] of Object.entries(properties)) {
      content += `<p><strong>${key}:</strong> ${value}</p>`;
    }
    content += '</div>';
    return content;
  }

  toggleLayer(layerName) {
    const layer = this.geoJsonLayers.get(layerName);
    if (layer) {
      if (this.map.map.hasLayer(layer)) {
        this.map.map.removeLayer(layer);
      } else {
        this.map.map.addLayer(layer);
      }
    }
  }
}
```

## 6.3 Real-time Map Updates

```javascript
// apps/web/src/js/map/real-time-updates.js
import { io } from 'socket.io-client';

export class RealTimeMapUpdates {
  constructor(map, socketUrl) {
    this.map = map;
    this.socket = io(socketUrl);
    this.setupListeners();
  }

  setupListeners() {
    // Listen for new service requests
    this.socket.on('service:created', (data) => {
      this.addServiceMarker(data);
    });

    // Listen for service updates
    this.socket.on('service:updated', (data) => {
      this.updateServiceMarker(data);
    });

    // Listen for provider location updates
    this.socket.on('provider:location', (data) => {
      this.updateProviderLocation(data);
    });
  }

  addServiceMarker(service) {
    const { id, location, type, description } = service;
    
    this.map.addMarker(
      location.latitude,
      location.longitude,
      {
        id: `service-${id}`,
        type: 'service-request',
        title: description,
        popup: this.createServicePopup(service),
      }
    );
  }

  updateServiceMarker(service) {
    const markerId = `service-${service.id}`;
    const marker = this.map.markers.get(markerId);
    
    if (marker) {
      marker.setPopupContent(this.createServicePopup(service));
      
      // Update marker icon based on status
      const icon = this.getStatusIcon(service.status);
      marker.setIcon(icon);
    }
  }

  updateProviderLocation(provider) {
    const markerId = `provider-${provider.id}`;
    let marker = this.map.markers.get(markerId);

    if (!marker) {
      marker = this.map.addMarker(
        provider.location.latitude,
        provider.location.longitude,
        {
          id: markerId,
          type: 'provider',
          title: provider.name,
          popup: this.createProviderPopup(provider),
        }
      );
    } else {
      // Animate marker movement
      marker.setLatLng([
        provider.location.latitude,
        provider.location.longitude,
      ]);
    }
  }

  createServicePopup(service) {
    return `
      <div class="service-popup p-2">
        <h3 class="font-bold text-lg">${service.type}</h3>
        <p class="text-sm">${service.description}</p>
        <p class="text-xs text-gray-600">Status: ${service.status}</p>
        <p class="text-xs text-gray-600">Priority: ${service.priority}</p>
        <button 
          onclick="handleServiceAction('${service.id}')"
          class="mt-2 px-3 py-1 bg-blue-600 text-white rounded text-sm"
        >
          View Details
        </button>
      </div>
    `;
  }

  createProviderPopup(provider) {
    return `
      <div class="provider-popup p-2">
        <h3 class="font-bold text-lg">${provider.name}</h3>
        <p class="text-sm">${provider.organization}</p>
        <p class="text-xs text-gray-600">Type: ${provider.type}</p>
        <p class="text-xs text-gray-600">Available: ${provider.available ? 'Yes' : 'No'}</p>
      </div>
    `;
  }

  getStatusIcon(status) {
    const statusIcons = {
      'pending': '/assets/icons/pending-marker.png',
      'in-progress': '/assets/icons/active-marker.png',
      'completed': '/assets/icons/completed-marker.png',
      'cancelled': '/assets/icons/cancelled-marker.png',
    };

    return L.icon({
      iconUrl: statusIcons[status] || statusIcons['pending'],
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32],
    });
  }

  disconnect() {
    this.socket.disconnect();
  }
}
```

---

# 7. Bun API Gateway Standards (MANDATORY for IDRM)

## 7.1 Express.js API Gateway Structure with Bun

**MUST** use Bun 1.x runtime for the API Gateway for superior performance.

```javascript
// services/api-gateway/src/index.js
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import morgan from 'morgan';
import { createServer } from 'http';
import { Server } from 'socket.io';
import rateLimit from 'express-rate-limit';
import { redisClient } from './config/redis.js';
import { authMiddleware } from './middleware/auth.middleware.js';
import authRoutes from './routes/auth.routes.js';
import serviceRoutes from './routes/services.routes.js';
import { errorHandler } from './middleware/error-handler.js';
import { logger } from './utils/logger.js';

const app = express();
const httpServer = createServer(app);
const io = new Server(httpServer, {
  cors: {
    origin: process.env.ALLOWED_ORIGINS.split(','),
    credentials: true,
  },
});

// Security middleware
app.use(helmet());
app.use(cors({
  origin: process.env.ALLOWED_ORIGINS.split(','),
  credentials: true,
}));

// Rate limiting with Redis
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // Limit each IP to 100 requests per windowMs
  standardHeaders: true,
  legacyHeaders: false,
  store: new RedisStore({
    client: redisClient,
    prefix: 'rate-limit:',
  }),
});

app.use('/api/', limiter);

// Logging
app.use(morgan('combined', {
  stream: { write: (message) => logger.info(message.trim()) },
}));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    runtime: 'bun',
    version: Bun.version,
    timestamp: new Date().toISOString() 
  });
});

// Routes
app.use('/api/v1/auth', authRoutes);
app.use('/api/v1/services', authMiddleware, serviceRoutes);

// WebSocket setup
import { setupWebSocket } from './websocket/socket-server.js';
setupWebSocket(io);

// Error handling
app.use(errorHandler);

// Start server with Bun
const PORT = process.env.PORT || 3000;
httpServer.listen(PORT, () => {
  logger.info(`API Gateway running on Bun ${Bun.version} - Port ${PORT}`);
});

export { app, io };
```

**Running with Bun:**
```bash
# Development
bun run --watch src/index.js

# Production
bun run src/index.js

# With environment variables
bun --env-file=.env run src/index.js
```

## 7.2 Authentication Middleware

```javascript
// services/api-gateway/src/middleware/auth.middleware.js
import jwt from 'jsonwebtoken';
import { redisClient } from '../config/redis.js';

export const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];

    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    // Check if token is blacklisted
    const isBlacklisted = await redisClient.get(`blacklist:${token}`);
    if (isBlacklisted) {
      return res.status(401).json({ error: 'Token has been revoked' });
    }

    // Verify token
    const decoded = jwt.verify(token, process.env.JWT_SECRET);

    // Attach user to request
    req.user = decoded;

    next();
  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      return res.status(401).json({ error: 'Invalid token' });
    }
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({ error: 'Token expired' });
    }
    return res.status(500).json({ error: 'Authentication failed' });
  }
};

export const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};
```

## 7.3 WebSocket Server (Real-time Communication)

```javascript
// services/api-gateway/src/websocket/socket-server.js
import jwt from 'jsonwebtoken';
import { redisClient } from '../config/redis.js';
import { logger } from '../utils/logger.js';

export function setupWebSocket(io) {
  // Authentication middleware for WebSocket
  io.use(async (socket, next) => {
    try {
      const token = socket.handshake.auth.token;
      
      if (!token) {
        return next(new Error('Authentication error'));
      }

      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      socket.user = decoded;
      
      next();
    } catch (error) {
      next(new Error('Authentication error'));
    }
  });

  io.on('connection', (socket) => {
    logger.info(`Client connected: ${socket.user.userId}`);

    // Join user-specific room
    socket.join(`user:${socket.user.userId}`);

    // Join role-specific room
    socket.join(`role:${socket.user.role}`);

    // Handle location updates (for providers)
    socket.on('location:update', async (data) => {
      try {
        // Validate and store location
        await handleLocationUpdate(socket.user.userId, data);
        
        // Broadcast to relevant rooms
        io.to('role:coordinator').emit('provider:location', {
          providerId: socket.user.userId,
          location: data,
          timestamp: new Date(),
        });
      } catch (error) {
        logger.error('Location update error:', error);
        socket.emit('error', { message: 'Failed to update location' });
      }
    });

    // Handle service request updates
    socket.on('service:subscribe', (serviceId) => {
      socket.join(`service:${serviceId}`);
      logger.info(`User ${socket.user.userId} subscribed to service ${serviceId}`);
    });

    socket.on('service:unsubscribe', (serviceId) => {
      socket.leave(`service:${serviceId}`);
    });

    socket.on('disconnect', () => {
      logger.info(`Client disconnected: ${socket.user.userId}`);
    });
  });

  // Function to emit to specific users
  io.emitToUser = (userId, event, data) => {
    io.to(`user:${userId}`).emit(event, data);
  };

  // Function to emit to specific roles
  io.emitToRole = (role, event, data) => {
    io.to(`role:${role}`).emit(event, data);
  };

  // Function to emit service updates
  io.emitServiceUpdate = (serviceId, event, data) => {
    io.to(`service:${serviceId}`).emit(event, data);
  };

  return io;
}

async function handleLocationUpdate(userId, locationData) {
  // Store location in Redis with expiry
  await redisClient.setEx(
    `location:${userId}`,
    300, // 5 minutes TTL
    JSON.stringify(locationData)
  );
}
```

---

# 8. React Component Standards (Secondary Web Interface)

```typescript
// features/add-to-cart/ui/add-button.tsx
import { FC } from 'react';
import { Product } from '@/entities/product';
import { Button } from '@/shared/ui/button';
import { useAddToCart } from '../model/use-add-to-cart';

interface AddToCartButtonProps {
  product: Product;
  variant?: 'primary' | 'secondary';
  className?: string;
}

export const AddToCartButton: FC<AddToCartButtonProps> = ({
  product,
  variant = 'primary',
  className,
}) => {
  const { addToCart, isLoading } = useAddToCart();

  const handleClick = () => {
    addToCart(product.id);
  };

  return (
    <Button
      onClick={handleClick}
      disabled={isLoading}
      variant={variant}
      className={className}
    >
      {isLoading ? 'Adding...' : 'Add to Cart'}
    </Button>
  );
};
```

## 6.2 Component Best Practices

- **USE** functional components with hooks
- **AVOID** class components
- **USE** named exports for better refactoring
- **EXTRACT** complex logic into custom hooks
- **MEMOIZE** expensive computations with `useMemo`
- **MEMOIZE** callbacks with `useCallback`
- **USE** `React.memo` for expensive components

---

# 9. PostGIS & Python Microservices Standards (MANDATORY for IDRM)

## 9.1 PostGIS Database Schema

**MUST** use PostGIS 3.4 for all geospatial data operations.

```python
# services/geospatial-service/app/models/spatial.py
from sqlalchemy import Column, String, Integer, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()

class ServiceRequest(Base):
    __tablename__ = 'service_requests'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    type = Column(String, nullable=False)  # medical, food, shelter, rescue
    description = Column(String)
    priority = Column(String)  # low, medium, high, critical
    status = Column(String, default='pending', index=True)
    
    # PostGIS geometry column - MANDATORY
    location = Column(
        Geometry(geometry_type='POINT', srid=4326),
        nullable=False,
        index=True  # Spatial index
    )
    
    address = Column(String)
    is_anonymous = Column(Boolean, default=False)
    revv_id = Column(String)  # Privacy verification ID
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
```

**See full PostGIS examples in the Backend Standards section below.**

## 9.2 GeoAlchemy2 Spatial Queries

**MUST** use spatial queries for all location-based matching and analysis.

Key functions to use:
- `ST_Distance`: Calculate distance between geometries
- `ST_DWithin`: Find geometries within a distance
- `ST_Contains`: Check if geometry contains another
- `ST_Intersects`: Check if geometries intersect
- `ST_Buffer`: Create buffer around geometry
- `ST_AsGeoJSON`: Convert to GeoJSON format

---

# 10. RBAC & Privacy Standards (MANDATORY for IDRM)

## 10.1 Role-Based Access Control (RBAC)

**MUST** implement role-based access control for all API endpoints.

```python
# services/api-gateway/src/middleware/rbac.middleware.js
import { redisClient } from '../config/redis.js';

export const ROLES = {
  SUPER_ADMIN: 'super_admin',
  ADMIN: 'admin',
  COORDINATOR: 'coordinator',
  PROVIDER: 'provider',
  CITIZEN: 'citizen',
  GUEST: 'guest',
};

export const PERMISSIONS = {
  // Disaster Event Management
  'disaster:create': [ROLES.SUPER_ADMIN, ROLES.ADMIN],
  'disaster:update': [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.COORDINATOR],
  'disaster:view': [ROLES.SUPER_ADMIN, ROLES.ADMIN, ROLES.COORDINATOR, ROLES.PROVIDER, ROLES.CITIZEN],
  
  // Service Request Management
  'service:create': [ROLES.CITIZEN, ROLES.COORDINATOR, ROLES.ADMIN],
  'service:assign': [ROLES.COORDINATOR, ROLES.ADMIN],
  'service:update': [ROLES.PROVIDER, ROLES.COORDINATOR, ROLES.ADMIN],
  'service:view': [ROLES.CITIZEN, ROLES.PROVIDER, ROLES.COORDINATOR, ROLES.ADMIN],
  
  // Provider Management
  'provider:register': [ROLES.ADMIN],
  'provider:update': [ROLES.PROVIDER, ROLES.COORDINATOR, ROLES.ADMIN],
  'provider:view': [ROLES.COORDINATOR, ROLES.ADMIN],
  
  // Financial Operations
  'donation:create': [ROLES.CITIZEN, ROLES.ADMIN],
  'donation:allocate': [ROLES.ADMIN, ROLES.COORDINATOR],
  'donation:view': [ROLES.CITIZEN, ROLES.ADMIN],  // Citizens can only view their own
  'donation:report': [ROLES.ADMIN],
  
  // Analytics & Reporting
  'analytics:view': [ROLES.ADMIN, ROLES.COORDINATOR],
  'report:generate': [ROLES.ADMIN, ROLES.COORDINATOR],
  
  // User Management
  'user:create': [ROLES.ADMIN],
  'user:update': [ROLES.ADMIN],
  'user:delete': [ROLES.SUPER_ADMIN],
  'user:view': [ROLES.ADMIN],
};

export const checkPermission = (permission) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }

    const allowedRoles = PERMISSIONS[permission];
    
    if (!allowedRoles) {
      return res.status(403).json({ error: 'Invalid permission' });
    }

    if (!allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ 
        error: 'Insufficient permissions',
        required: permission,
        userRole: req.user.role
      });
    }

    next();
  };
};
```

## 10.2 ReVV (Request Verification and Validation) - Privacy System

**MUST** implement ReVV for privacy-sensitive service requests.

```python
# services/privacy-service/app/services/revv.py
from sqlalchemy.orm import Session
import hashlib
import secrets
from datetime import datetime, timedelta
from app.models.revv import ReVVRecord, VerificationCode

class ReVVService:
    """
    ReVV (Request Verification and Validation) System
    
    Enables anonymous service requests while maintaining accountability.
    Users can request services without revealing personal identity.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def create_anonymous_request(
        self,
        user_id: str,
        service_data: dict
    ):
        """
        Create an anonymous service request with ReVV protection.
        
        Returns:
        - revv_id: Anonymous identifier for the request
        - verification_code: Code for the user to verify ownership
        """
        # Generate ReVV ID (one-way hash of user_id + timestamp + salt)
        salt = secrets.token_hex(16)
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{user_id}:{timestamp}:{salt}"
        revv_id = hashlib.sha256(hash_input.encode()).hexdigest()[:16]
        
        # Generate verification code for user to prove ownership
        verification_code = secrets.token_hex(8).upper()
        
        # Store ReVV record (mapping is encrypted and only accessible by authorized admins)
        revv_record = ReVVRecord(
            revv_id=revv_id,
            user_id_hash=hashlib.sha256(user_id.encode()).hexdigest(),
            verification_code_hash=hashlib.sha256(verification_code.encode()).hexdigest(),
            service_type=service_data.get('type'),
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        self.db.add(revv_record)
        self.db.commit()
        
        return {
            'revv_id': revv_id,
            'verification_code': verification_code,
            'message': 'Keep this verification code safe. You will need it to update or verify this request.'
        }

    def verify_request_ownership(
        self,
        revv_id: str,
        verification_code: str
    ):
        """
        Verify that a user owns a specific anonymous request.
        """
        revv_record = self.db.query(ReVVRecord).filter_by(
            revv_id=revv_id
        ).first()
        
        if not revv_record:
            return False
        
        # Check if expired
        if revv_record.expires_at < datetime.utcnow():
            return False
        
        # Verify code
        code_hash = hashlib.sha256(verification_code.encode()).hexdigest()
        return code_hash == revv_record.verification_code_hash

    def anonymize_user_data(self, user_data: dict):
        """
        Anonymize user data for privacy-sensitive contexts.
        """
        return {
            'id': hashlib.sha256(user_data['id'].encode()).hexdigest()[:12],
            'role': user_data.get('role'),
            'location_approximate': self.fuzzy_location(
                user_data.get('location')
            ),
            # Remove all PII
            # 'name': REMOVED
            # 'email': REMOVED
            # 'phone': REMOVED
        }

    def fuzzy_location(self, location: dict):
        """
        Reduce location precision for privacy.
        Round to nearest 0.01 degrees (~1km)
        """
        if not location:
            return None
            
        return {
            'latitude': round(location['latitude'], 2),
            'longitude': round(location['longitude'], 2)
        }
```

## 10.3 Data Access Logging (Audit Trail)

**MUST** log all access to sensitive data for audit purposes.

```python
# services/privacy-service/app/models/audit.py
from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)  # create, read, update, delete
    resource_type = Column(String, nullable=False)  # service, user, donation, etc.
    resource_id = Column(String, nullable=False)
    details = Column(JSON)  # Additional context
    ip_address = Column(String)
    user_agent = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)


# Middleware to log all data access
async def audit_middleware(request, call_next):
    # Log the request
    audit_log = AuditLog(
        id=generate_id(),
        user_id=request.user.id if hasattr(request, 'user') else 'anonymous',
        action=request.method,
        resource_type=extract_resource_type(request.url.path),
        resource_id=extract_resource_id(request.url.path),
        details={'path': request.url.path, 'query': str(request.query_params)},
        ip_address=request.client.host,
        user_agent=request.headers.get('user-agent'),
        timestamp=datetime.utcnow()
    )
    
    # Save to database (async)
    await save_audit_log(audit_log)
    
    response = await call_next(request)
    return response
```

---

# 11. State Management

## 6.1 State Guidelines

- **LOCAL STATE**: `useState` for component-specific state
- **SERVER STATE**: React Query for data fetching
- **GLOBAL STATE**: Zustand for cross-cutting concerns (theme, auth)
- **AVOID** prop drilling - use composition or context
- **AVOID** Redux unless absolutely necessary

## 6.2 Zustand Store Example

```typescript
// features/auth/model/auth-store.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User } from '@/entities/user';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      login: (user, token) => 
        set({ user, token, isAuthenticated: true }),
      logout: () => 
        set({ user: null, token: null, isAuthenticated: false }),
    }),
    {
      name: 'auth-storage',
    }
  )
);
```

## 6.3 React Query Usage

```typescript
// entities/product/api/use-products.ts
import { useQuery } from '@tanstack/react-query';
import { productApi } from './product-api';

export const useProducts = () => {
  return useQuery({
    queryKey: ['products'],
    queryFn: productApi.getAll,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useProduct = (id: string) => {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => productApi.getById(id),
    enabled: !!id,
  });
};
```

---

# 7. API Integration

## 7.1 API Client (shared/api)

```typescript
// shared/api/client.ts
import axios, { AxiosError } from 'axios';

const API_URL = import.meta.env.VITE_API_URL;

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth-token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth-token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 7.2 API Layer Pattern

```typescript
// entities/product/api/product-api.ts
import { apiClient } from '@/shared/api/client';
import { productSchema } from '../types';
import type { Product } from '../types';

export const productApi = {
  getAll: async (): Promise<Product[]> => {
    const { data } = await apiClient.get('/api/v1/products');
    return data.map((item: unknown) => productSchema.parse(item));
  },

  getById: async (id: string): Promise<Product> => {
    const { data } = await apiClient.get(`/api/v1/products/${id}`);
    return productSchema.parse(data);
  },

  create: async (product: Omit<Product, 'id'>): Promise<Product> => {
    const { data } = await apiClient.post('/api/v1/products', product);
    return productSchema.parse(data);
  },

  update: async (id: string, product: Partial<Product>): Promise<Product> => {
    const { data } = await apiClient.patch(`/api/v1/products/${id}`, product);
    return productSchema.parse(data);
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/products/${id}`);
  },
};
```

---

# 8. Styling Standards

## 8.1 TailwindCSS Usage

- **USE** Tailwind utility classes for styling
- **EXTRACT** repeated patterns into components
- **USE** `@apply` sparingly in CSS files
- **CONFIGURE** custom theme in `tailwind.config.js`
- **USE** CSS variables for dynamic theming

```typescript
// Good: Utility classes
<button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
  Click me
</button>

// Better: Extracted component
// shared/ui/button/button.tsx
import { FC, ButtonHTMLAttributes } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/shared/lib/utils';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-lg font-medium transition-colors',
  {
    variants: {
      variant: {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-200 text-gray-900 hover:bg-gray-300',
        outline: 'border border-gray-300 hover:bg-gray-50',
      },
      size: {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
);

interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button: FC<ButtonProps> = ({
  className,
  variant,
  size,
  ...props
}) => {
  return (
    <button
      className={cn(buttonVariants({ variant, size, className }))}
      {...props}
    />
  );
};
```

---

# 9. Testing Standards

## 9.1 Test Coverage

- **MUST** write unit tests for business logic
- **MUST** write integration tests for API endpoints
- **SHOULD** write E2E tests for critical user flows
- **TARGET** 80%+ code coverage

## 9.2 Testing Tools

- **Vitest** (unit tests)
- **React Testing Library** (component tests)
- **Playwright** or **Cypress** (E2E tests)
- **MSW** (API mocking)

## 9.3 Test Example

```typescript
// features/add-to-cart/model/use-add-to-cart.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useAddToCart } from './use-add-to-cart';

describe('useAddToCart', () => {
  it('should add product to cart', async () => {
    const { result } = renderHook(() => useAddToCart());

    result.current.addToCart('product-123');

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.isSuccess).toBe(true);
    });
  });
});
```

---

# 10. Backend Standards (Python/FastAPI)

## 10.1 Project Structure

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
```

## 10.2 Layered Architecture

```python
# backend/app/api/v1/endpoints/products.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.product import Product, ProductCreate
from app.services.product import ProductService

router = APIRouter()

@router.get("/products", response_model=list[Product])
async def get_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
):
    service = ProductService(db)
    return await service.get_all(skip=skip, limit=limit)

@router.post("/products", response_model=Product)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
):
    service = ProductService(db)
    return await service.create(product)
```

```python
# backend/app/services/product.py
from sqlalchemy.orm import Session
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate

class ProductService:
    def __init__(self, db: Session):
        self.repository = ProductRepository(db)

    async def get_all(self, skip: int = 0, limit: int = 100):
        return await self.repository.get_all(skip, limit)

    async def create(self, product: ProductCreate):
        return await self.repository.create(product)
```

```python
# backend/app/repositories/product.py
from sqlalchemy.orm import Session
from app.models.product import Product as ProductModel
from app.schemas.product import ProductCreate

class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    async def get_all(self, skip: int = 0, limit: int = 100):
        return self.db.query(ProductModel).offset(skip).limit(limit).all()

    async def create(self, product: ProductCreate):
        db_product = ProductModel(**product.dict())
        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)
        return db_product
```

## 10.3 Database Models

```python
# backend/app/models/product.py
from sqlalchemy import Column, String, Float, Text, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

## 10.4 Pydantic Schemas

```python
# backend/app/schemas/product.py
from datetime import datetime
from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = None
    price: float = Field(..., gt=0)

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: str
    created_at: datetime
    updated_at: datetime | None

    class Config:
        from_attributes = True
```

---

# 11. Database Standards (PostgreSQL)

## 11.1 Migration Strategy

- **USE** Alembic for database migrations
- **NEVER** modify migrations after they've been applied
- **ALWAYS** create new migrations for changes
- **TEST** migrations in development before production

```bash
# Create migration
alembic revision --autogenerate -m "Add products table"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 11.2 Database Best Practices

- **USE** indexes on frequently queried columns
- **USE** foreign keys with proper constraints
- **USE** transactions for multi-step operations
- **AVOID** N+1 queries - use eager loading
- **USE** connection pooling
- **IMPLEMENT** soft deletes for important data

---

# 12. Bun Usage

## 12.1 Package Management

```json
// package.json (root)
{
  "name": "idrm-platform",
  "workspaces": [
    "apps/*",
    "services/*",
    "packages/*"
  ],
  "scripts": {
    "dev:web": "bun --cwd apps/web run dev",
    "dev:react": "bun --cwd apps/web-react run dev",
    "dev:mobile": "bun --cwd apps/mobile run start",
    "dev:api-gateway": "bun --cwd services/api-gateway run --watch src/index.js",
    "dev:backend": "cd backend && poetry run uvicorn app.main:app --reload",
    "dev:all": "concurrently \"bun run dev:web\" \"bun run dev:react\" \"bun run dev:api-gateway\"",
    
    "build:web": "bun --cwd apps/web run build",
    "build:react": "bun --cwd apps/web-react run build",
    "build:mobile": "bun --cwd apps/mobile run build",
    "build:all": "bun run build:web && bun run build:react",
    
    "test": "bun test",
    "test:web": "bun --cwd apps/web run test",
    "test:react": "bun --cwd apps/web-react run test",
    "test:api-gateway": "bun --cwd services/api-gateway test",
    "test:backend": "cd backend && poetry run pytest",
    
    "lint": "bun run eslint .",
    "typecheck": "bun run tsc --noEmit",
    
    "docker:up": "docker-compose up",
    "docker:up:react": "docker-compose --profile react up",
    "docker:down": "docker-compose down"
  },
  "devDependencies": {
    "concurrently": "^8.2.0",
    "eslint": "^8.0.0",
    "typescript": "^5.0.0"
  }
}
```

## 12.2 Bun for API Gateway Development

```javascript
// services/api-gateway/package.json
{
  "name": "idrm-api-gateway",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "bun run --watch src/index.js",
    "start": "bun run src/index.js",
    "test": "bun test",
    "lint": "eslint src"
  },
  "dependencies": {
    "express": "^4.18.0",
    "socket.io": "^4.6.0",
    "passport": "^0.7.0",
    "passport-jwt": "^4.0.0",
    "helmet": "^7.0.0",
    "cors": "^2.8.5",
    "express-rate-limit": "^7.0.0",
    "express-validator": "^7.0.0",
    "joi": "^17.11.0",
    "winston": "^3.11.0",
    "morgan": "^1.10.0",
    "pg": "^8.11.0",
    "ioredis": "^5.3.0",
    "bcrypt": "^5.1.0",
    "jsonwebtoken": "^9.0.2"
  },
  "devDependencies": {
    "@types/express": "^4.17.0",
    "@types/node": "^20.0.0",
    "bun-types": "^1.0.0"
  }
}
```

**Development Commands:**
```bash
# Install dependencies with Bun (much faster than npm)
bun install

# Run API Gateway in watch mode (auto-restart on changes)
bun run --watch src/index.js

# Run with environment file
bun --env-file=.env run src/index.js

# Run tests with Bun's built-in test runner
bun test

# Type check (Bun has built-in TypeScript support)
bun run tsc --noEmit

# Production mode
NODE_ENV=production bun run src/index.js
```

## 12.3 Bun Runtime Features & Best Practices

**Built-in TypeScript Support:**
```typescript
// You can use .ts files directly without transpilation
// services/api-gateway/src/index.ts
import express, { Express, Request, Response } from 'express';
import { Server } from 'socket.io';

const app: Express = express();

// Bun natively understands TypeScript
app.get('/health', (req: Request, res: Response) => {
  res.json({ 
    runtime: 'bun',
    version: Bun.version,
    uptime: process.uptime()
  });
});
```

**Environment Variables:**
```typescript
// Bun provides built-in env support
const config = {
  port: Bun.env.PORT || 3000,
  dbUrl: Bun.env.DATABASE_URL,
  jwtSecret: Bun.env.JWT_SECRET,
  redisUrl: Bun.env.REDIS_URL,
};

// Or use process.env (Node.js compatible)
const port = process.env.PORT || 3000;
```

**Native HTTP Server (alternative to Express):**
```typescript
// For even better performance, use Bun's native server
import { serve } from 'bun';

const server = serve({
  port: 3000,
  fetch(req) {
    const url = new URL(req.url);
    
    if (url.pathname === '/health') {
      return Response.json({ 
        status: 'healthy',
        runtime: 'bun'
      });
    }
    
    return new Response('Not Found', { status: 404 });
  },
});

console.log(`Server running on http://localhost:${server.port}`);
```

**File System Operations:**
```typescript
// Bun provides fast file operations
const file = Bun.file('./config.json');
const config = await file.json();

// Write files
await Bun.write('./output.txt', 'Hello from Bun!');

// Read files
const content = await Bun.file('./data.txt').text();
```

**SQLite Support (for local development):**
```typescript
import { Database } from 'bun:sqlite';

const db = new Database('mydb.sqlite');
const query = db.query('SELECT * FROM users WHERE id = ?');
const user = query.get(1);
```

## 12.4 Performance Advantages

**Bun vs Node.js Performance:**
- **HTTP Requests**: 3-4x faster
- **Package Installation**: 10-20x faster than npm
- **TypeScript Execution**: No transpilation needed
- **Memory Usage**: ~30% less memory than Node.js
- **Startup Time**: 4x faster cold starts

**Benchmarks (approximate):**
```
HTTP Requests/sec:
- Bun:    45,000 req/s
- Node.js: 12,000 req/s

Package Install Time:
- bun install:  2-3 seconds
- npm install: 30-45 seconds

Memory Usage:
- Bun:    ~80 MB
- Node.js: ~120 MB
```

---

# 13. Docker & DevOps

## 13.1 Docker Compose (IDRM Platform)

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Database
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=en_US.UTF-8"
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./infrastructure/postgres/init.sql:/docker-entrypoint-initdb.d/01-init.sql
      - ./infrastructure/postgres/postgis-setup.sql:/docker-entrypoint-initdb.d/02-postgis.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Cache & Message Queue
  redis:
    image: redis:7.2-alpine
    container_name: idrm-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./infrastructure/redis/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # GeoServer for Map Services
  geoserver:
    image: kartoza/geoserver:2.24.0
    container_name: idrm-geoserver
    ports:
      - "8080:8080"
    environment:
      - GEOSERVER_ADMIN_USER=admin
      - GEOSERVER_ADMIN_PASSWORD=${GEOSERVER_ADMIN_PASSWORD}
      - INITIAL_MEMORY=2G
      - MAXIMUM_MEMORY=4G
    volumes:
      - geoserver_data:/opt/geoserver/data_dir
      - ./infrastructure/geoserver/styles:/opt/geoserver/styles
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/geoserver/web/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # API Gateway (Bun Runtime)
  api-gateway:
    build:
      context: .
      dockerfile: docker/Dockerfile.api-gateway
    container_name: idrm-api-gateway
    ports:
      - "3000:3000"
    environment:
      NODE_ENV: production
      PORT: 3000
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      JWT_SECRET: ${JWT_SECRET}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "bun", "run", "healthcheck.js"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Service Management Microservice (Python/FastAPI)
  service-management:
    build:
      context: ./services/service-management
      dockerfile: ../../docker/Dockerfile.python-service
    container_name: idrm-service-mgmt
    ports:
      - "8001:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Geospatial Service (Python/FastAPI)
  geospatial-service:
    build:
      context: ./services/geospatial-service
      dockerfile: ../../docker/Dockerfile.python-service
    container_name: idrm-geospatial
    ports:
      - "8002:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      GEOSERVER_URL: http://geoserver:8080/geoserver
    depends_on:
      postgres:
        condition: service_healthy
      geoserver:
        condition: service_healthy

  # Communication Service (Bun/Socket.io)
  communication-service:
    build:
      context: ./services/communication-service
      dockerfile: ../../docker/Dockerfile.bun-service
    container_name: idrm-communication
    ports:
      - "3002:3000"
    environment:
      NODE_ENV: production
      REDIS_HOST: redis
      REDIS_PORT: 6379
    depends_on:
      redis:
        condition: service_healthy

  # Analytics Service (Python/FastAPI)
  analytics-service:
    build:
      context: ./services/analytics-service
      dockerfile: ../../docker/Dockerfile.python-service
    container_name: idrm-analytics
    ports:
      - "8003:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy

  # Financial Service (Python/FastAPI)
  financial-service:
    build:
      context: ./services/financial-service
      dockerfile: ../../docker/Dockerfile.python-service
    container_name: idrm-financial
    ports:
      - "8004:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
    depends_on:
      postgres:
        condition: service_healthy

  # Privacy/ReVV Service (Python/FastAPI)
  privacy-service:
    build:
      context: ./services/privacy-service
      dockerfile: ../../docker/Dockerfile.python-service
    container_name: idrm-privacy
    ports:
      - "8005:8000"
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      ENCRYPTION_KEY: ${ENCRYPTION_KEY}
    depends_on:
      postgres:
        condition: service_healthy

  # Celery Worker for Background Tasks
  celery-worker:
    build:
      context: ./services/service-management
      dockerfile: ../../docker/Dockerfile.python-service
    container_name: idrm-celery-worker
    command: celery -A app.celery worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Primary Web Interface (HTML/CSS/JS + Leaflet)
  web:
    build:
      context: .
      dockerfile: docker/Dockerfile.web
    container_name: idrm-web
    ports:
      - "3100:3000"
    environment:
      VITE_API_URL: http://api-gateway:3000/api/v1
      VITE_GEOSERVER_URL: http://geoserver:8080/geoserver
      VITE_WS_URL: ws://api-gateway:3000
    depends_on:
      - api-gateway

  # Secondary Web Interface (React Admin Dashboard)
  web-react:
    build:
      context: .
      dockerfile: docker/Dockerfile.web-react
    container_name: idrm-web-react
    ports:
      - "3101:3001"
    environment:
      VITE_API_URL: http://api-gateway:3000/api/v1
      VITE_WS_URL: ws://api-gateway:3000
    depends_on:
      - api-gateway
    profiles:
      - react

  # NGINX Reverse Proxy
  nginx:
    image: nginx:1.24-alpine
    container_name: idrm-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./infrastructure/nginx/sites-available:/etc/nginx/sites-available
      - ./infrastructure/nginx/ssl:/etc/nginx/ssl
      - ./apps/web/dist:/usr/share/nginx/html
    depends_on:
      - api-gateway
      - web
      - geoserver

volumes:
  postgres_data:
  redis_data:
  geoserver_data:

networks:
  default:
    name: idrm-network
```

**Running IDRM Platform:**
```bash
# Start core services (database, cache, API gateway, geospatial)
docker-compose up postgres redis api-gateway geospatial-service geoserver

# Start all microservices
docker-compose up

# Start with React admin dashboard
docker-compose --profile react up

# Production deployment with NGINX
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Scale specific services
docker-compose up --scale service-management=3

# View logs
docker-compose logs -f api-gateway

# Health check all services
docker-compose ps
```

## 13.2 Dockerfile Examples

```dockerfile
# docker/Dockerfile.web
FROM oven/bun:1 as builder

WORKDIR /app

COPY package.json bun.lockb ./
COPY apps/web/package.json ./apps/web/
RUN bun install --frozen-lockfile

COPY apps/web ./apps/web
RUN bun --cwd apps/web run build

FROM oven/bun:1-slim

WORKDIR /app

COPY --from=builder /app/apps/web/dist ./dist
COPY --from=builder /app/apps/web/package.json .

EXPOSE 3000

CMD ["bun", "run", "preview"]
```

```dockerfile
# docker/Dockerfile.web-react
FROM oven/bun:1 as builder

WORKDIR /app

COPY package.json bun.lockb ./
COPY apps/web-react/package.json ./apps/web-react/
RUN bun install --frozen-lockfile

COPY apps/web-react ./apps/web-react
RUN bun --cwd apps/web-react run build

FROM oven/bun:1-slim

WORKDIR /app

COPY --from=builder /app/apps/web-react/dist ./dist
COPY --from=builder /app/apps/web-react/package.json .

EXPOSE 3001

CMD ["bun", "run", "preview", "--port", "3001"]
```

```dockerfile
# docker/Dockerfile.api-gateway (Bun Runtime)
FROM oven/bun:1 as builder

WORKDIR /app

# Copy package files
COPY services/api-gateway/package.json services/api-gateway/bun.lockb* ./

# Install dependencies
RUN bun install --frozen-lockfile --production

# Copy source code
COPY services/api-gateway/src ./src

# Production image
FROM oven/bun:1-slim

WORKDIR /app

# Copy from builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/package.json ./

# Create healthcheck script
RUN echo 'const res = await fetch("http://localhost:3000/health"); process.exit(res.ok ? 0 : 1);' > healthcheck.js

EXPOSE 3000

# Run with Bun
CMD ["bun", "run", "src/index.js"]
```

```dockerfile
# docker/Dockerfile.bun-service (Generic Bun Service)
FROM oven/bun:1 as builder

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --frozen-lockfile --production

COPY src ./src

FROM oven/bun:1-slim

WORKDIR /app

COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/src ./src
COPY --from=builder /app/package.json ./

EXPOSE 3000

CMD ["bun", "run", "src/index.js"]
```

```dockerfile
# docker/Dockerfile.backend (Python Service)
FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# 14. Security Standards

## 14.1 Authentication & Authorization

- **USE** JWT tokens for authentication
- **IMPLEMENT** refresh token rotation
- **USE** HTTP-only cookies for token storage (mobile: secure storage)
- **IMPLEMENT** RBAC (Role-Based Access Control)
- **USE** bcrypt or argon2 for password hashing

## 14.2 API Security

- **IMPLEMENT** rate limiting
- **USE** CORS properly
- **VALIDATE** all inputs with Zod/Pydantic
- **SANITIZE** user inputs
- **USE** HTTPS in production
- **IMPLEMENT** CSRF protection

## 14.3 Environment Variables

```bash
# .env.example
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# API
API_URL=http://localhost:8000
API_SECRET_KEY=your-secret-key-here

# JWT
JWT_SECRET=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# Frontend
VITE_API_URL=http://localhost:8000/api/v1
```

**NEVER** commit `.env` files to version control!

---

# 15. Performance Optimization

## 15.1 Frontend Optimization

- **USE** code splitting and lazy loading
- **OPTIMIZE** images (WebP, lazy loading)
- **IMPLEMENT** virtual scrolling for long lists
- **USE** React.memo for expensive components
- **DEBOUNCE** expensive operations
- **IMPLEMENT** request caching with React Query

```typescript
// Lazy loading
const ProductDetail = lazy(() => import('@/pages/product-detail'));

// Virtual scrolling
import { useVirtualizer } from '@tanstack/react-virtual';

// Debouncing
import { debounce } from '@/shared/lib/debounce';

const handleSearch = debounce((query: string) => {
  // Search logic
}, 300);
```

## 15.2 Backend Optimization

- **USE** database indexes
- **IMPLEMENT** caching with Redis
- **USE** pagination for large datasets
- **OPTIMIZE** database queries
- **USE** background tasks for heavy operations (Celery)
- **IMPLEMENT** connection pooling

---

# 16. Error Handling

## 16.1 Frontend Error Handling

```typescript
// shared/lib/error-handler.ts
import { AxiosError } from 'axios';
import { toast } from 'sonner';

export function handleApiError(error: unknown) {
  if (error instanceof AxiosError) {
    const message = error.response?.data?.message || 'An error occurred';
    toast.error(message);
    
    if (error.response?.status === 401) {
      // Handle unauthorized
      window.location.href = '/login';
    }
  } else {
    toast.error('An unexpected error occurred');
  }
}
```

## 16.2 Backend Error Handling

```python
# backend/app/core/errors.py
from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )
```

---

# 17. Accessibility (a11y)

- **USE** semantic HTML
- **IMPLEMENT** keyboard navigation
- **PROVIDE** ARIA labels
- **ENSURE** proper color contrast
- **TEST** with screen readers
- **IMPLEMENT** focus management

```typescript
// Good accessibility
<button
  aria-label="Add to cart"
  onClick={handleClick}
  disabled={isLoading}
>
  <ShoppingCartIcon aria-hidden="true" />
  Add to Cart
</button>
```

---

# 18. Documentation

## 18.1 Code Documentation

- **WRITE** JSDoc comments for public APIs
- **DOCUMENT** complex logic
- **MAINTAIN** README files
- **KEEP** ADRs (Architecture Decision Records)

```typescript
/**
 * Adds a product to the shopping cart
 * @param productId - The unique identifier of the product
 * @returns Promise that resolves when the product is added
 * @throws {Error} If the product is out of stock
 */
export async function addToCart(productId: string): Promise<void> {
  // implementation
}
```

## 18.2 API Documentation

- **USE** OpenAPI/Swagger for REST APIs
- **GENERATE** API docs automatically
- **PROVIDE** example requests/responses

---

# 19. CI/CD Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
      
      - name: Install dependencies
        run: bun install
      
      - name: Lint
        run: bun run lint
      
      - name: Type check
        run: bun run typecheck
      
      - name: Test
        run: bun test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build
        run: bun run build
      
      - name: Deploy
        if: github.ref == 'refs/heads/main'
        run: echo "Deploy to production"
```

---

# 20. Mobile-Specific Considerations

## 20.1 React Native Best Practices

- **USE** Expo for easier development
- **IMPLEMENT** offline support
- **OPTIMIZE** for different screen sizes
- **USE** platform-specific code when needed
- **IMPLEMENT** proper error boundaries
- **USE** async storage for persistence

```typescript
// Platform-specific code
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  container: {
    paddingTop: Platform.OS === 'ios' ? 20 : 0,
  },
});
```

---

# IDRM Platform Implementation Checklist

## Architecture & Infrastructure (MANDATORY)
- ✅ Implement microservices architecture (Bun API Gateway + Python services)
- ✅ Deploy PostgreSQL 16 + PostGIS 3.4 (geospatial database)
- ✅ Deploy Redis 7.2 (caching, session management, message queue)
- ✅ Deploy GeoServer 2.24 (OGC-compliant map server)
- ✅ Deploy NGINX 1.24 (reverse proxy, WAF, SSL termination)
- ✅ Implement Docker containerization for all services
- ✅ Configure service health checks and monitoring
- ✅ Set up development-production parity

## Frontend Implementation
### Primary Web Interface (HTML/CSS/JS + Leaflet)
- ✅ Implement Leaflet 1.9 for interactive maps (MANDATORY)
- ✅ Integrate with GeoServer WMS/WFS layers
- ✅ Implement real-time map updates via Socket.io
- ✅ Create custom map markers for service types
- ✅ Implement geolocation support
- ✅ Use TailwindCSS for styling
- ✅ Implement Socket.io client for WebSocket communication
- ✅ Optimize for SEO and performance
- ✅ Implement progressive enhancement

### Secondary Web Interface (React Admin)
- ✅ Follow Feature-Sliced Design architecture
- ✅ Implement React Leaflet for map components
- ✅ Use React Query for data fetching
- ✅ Integrate Socket.io for real-time updates
- ✅ Implement analytics dashboard
- ✅ Create admin management interfaces

### Mobile Application (React Native)
- ✅ Implement React Native Maps for geospatial features
- ✅ Follow FSD architecture
- ✅ Enable real-time notifications
- ✅ Implement offline support

## Backend - Bun API Gateway (MANDATORY)
- ✅ Use Bun 1.x runtime for superior performance
- ✅ Implement Express.js 4.x for REST APIs
- ✅ Implement Socket.io 4.x for real-time communication
- ✅ Configure Passport.js for JWT authentication
- ✅ Implement Helmet.js security middleware
- ✅ Set up rate limiting with Redis
- ✅ Implement request validation with Joi/Express-validator
- ✅ Configure Winston logging
- ✅ Implement WebSocket authentication
- ✅ Create room-based broadcasting (user, role, service-specific)
- ✅ Leverage Bun's built-in TypeScript support
- ✅ Utilize Bun's native performance benefits (3-4x faster than Node.js)

## Backend - Python Microservices (MANDATORY)
### Service Management Service
- ✅ Implement CRUD for service requests
- ✅ Implement provider matching algorithms
- ✅ Create task assignment logic
- ✅ Implement status tracking

### Geospatial Service
- ✅ Configure GeoAlchemy2 for PostGIS operations
- ✅ Implement spatial queries (ST_Distance, ST_DWithin, ST_Contains, ST_Intersects)
- ✅ Create proximity search functionality
- ✅ Implement service density calculations
- ✅ Create GeoJSON endpoints for map visualization
- ✅ Implement clustering algorithms

### Communication Service
- ✅ Implement real-time notifications via Socket.io
- ✅ Configure Redis pub/sub for event broadcasting
- ✅ Create broadcast mechanisms for different user types
- ✅ Implement message queuing

### Analytics Service
- ✅ Implement data aggregation with Pandas
- ✅ Create report generation functionality
- ✅ Build dashboard metrics endpoints
- ✅ Implement audit log processing

### Financial Service
- ✅ Implement donation tracking
- ✅ Create allocation management
- ✅ Build transparent accounting system
- ✅ Implement fund flow auditing

### Privacy Service (ReVV)
- ✅ Implement ReVV (Request Verification and Validation) system
- ✅ Create anonymous request functionality
- ✅ Implement verification code system
- ✅ Build data anonymization utilities
- ✅ Implement consent management
- ✅ Create fuzzy location (privacy-preserving geolocation)

## Database & Geospatial (MANDATORY)
- ✅ Install PostGIS extension on PostgreSQL
- ✅ Create spatial indexes on geometry columns
- ✅ Implement SRID 4326 (WGS 84) for all geometries
- ✅ Use POINT geometry for service requests and providers
- ✅ Use POLYGON/MULTIPOLYGON for disaster zones
- ✅ Implement proper spatial indexes (R-tree)
- ✅ Create database migration scripts with Alembic
- ✅ Implement soft deletes for critical data

## Security & Privacy (MANDATORY)
### Authentication & Authorization
- ✅ Implement JWT-based authentication
- ✅ Configure Redis for JWT blacklisting
- ✅ Implement refresh token rotation
- ✅ Add OAuth 2.0 integration capability
- ✅ Use bcrypt for password hashing

### RBAC (Role-Based Access Control)
- ✅ Define roles: super_admin, admin, coordinator, provider, citizen, guest
- ✅ Implement permission-based middleware
- ✅ Create role-specific access controls
- ✅ Implement resource-level permissions
- ✅ Add audit logging for all privileged operations

### Privacy Controls
- ✅ Implement ReVV system for anonymous requests
- ✅ Create data anonymization for PII
- ✅ Implement location fuzzing for privacy
- ✅ Add consent management system
- ✅ Create audit trail for data access

### API Security
- ✅ Implement rate limiting (100 requests/15min per IP)
- ✅ Configure CORS properly
- ✅ Add input validation with Pydantic/Joi
- ✅ Implement request sanitization
- ✅ Enable HTTPS in production
- ✅ Add CSRF protection
- ✅ Configure WAF in NGINX

## Real-time Communication (MANDATORY)
- ✅ Implement WebSocket server with Socket.io
- ✅ Add WebSocket authentication
- ✅ Create user-specific rooms
- ✅ Create role-specific rooms
- ✅ Create service-specific rooms
- ✅ Implement location update broadcasting
- ✅ Add service status update notifications
- ✅ Implement provider availability updates

## GeoServer Configuration (MANDATORY)
- ✅ Connect GeoServer to PostGIS database
- ✅ Create workspaces for IDRM data layers
- ✅ Publish service request layer (WMS/WFS)
- ✅ Publish disaster zone layer (WMS)
- ✅ Publish provider location layer (WMS)
- ✅ Configure SLD styling for different service types
- ✅ Enable REST API access
- ✅ Optimize layer caching

## Audit & Compliance
- ✅ Implement comprehensive audit logging
- ✅ Log all data access operations
- ✅ Log all privileged operations
- ✅ Store IP address and user agent
- ✅ Create audit log retention policy
- ✅ Implement audit log search and reporting
- ✅ Add data access monitoring dashboard

## Testing & Quality Assurance
- ✅ Write unit tests for all business logic
- ✅ Write integration tests for API endpoints
- ✅ Write E2E tests for critical user flows
- ✅ Perform load testing (1000+ concurrent users)
- ✅ Conduct security penetration testing
- ✅ Test geospatial query performance
- ✅ Validate WebSocket scalability
- ✅ Test disaster scenario simulations
- ✅ Achieve 80%+ code coverage

## Monitoring & Observability
- ✅ Implement health check endpoints
- ✅ Configure service monitoring
- ✅ Set up error tracking
- ✅ Implement performance monitoring
- ✅ Create dashboard for system metrics
- ✅ Configure alerting for critical failures
- ✅ Monitor database performance
- ✅ Track API response times

## Documentation (MANDATORY)
- ✅ Create API documentation (OpenAPI/Swagger)
- ✅ Document database schema
- ✅ Create deployment guides
- ✅ Write user manuals (end users, providers, admins)
- ✅ Document RBAC permissions
- ✅ Create troubleshooting guides
- ✅ Document ReVV system usage
- ✅ Create developer onboarding guide

## Deployment & Operations
- ✅ Configure production environment variables
- ✅ Set up SSL certificates
- ✅ Configure automated backups
- ✅ Implement database replication
- ✅ Set up log rotation
- ✅ Configure monitoring alerts
- ✅ Create rollback procedures
- ✅ Document disaster recovery plan
- ✅ Set up CI/CD pipeline
- ✅ Configure auto-scaling policies (if cloud-deployed)

## IDRM-Specific Features
- ✅ Implement service request lifecycle management
- ✅ Create provider-service matching algorithm
- ✅ Build disaster zone management system
- ✅ Implement donation tracking and allocation
- ✅ Create financial transparency reports
- ✅ Build analytics dashboard for coordinators
- ✅ Implement priority-based service routing
- ✅ Create capacity management for providers
- ✅ Build service density heatmaps
- ✅ Implement emergency broadcast system

---

**This is the authoritative specification for the IDRM Platform. All development MUST adhere to these guidelines to ensure a secure, scalable, privacy-first disaster response system for India.**

**Document Version**: 2.0 (Integrated with IDRM PRD)  
**Last Updated**: December 2024  
**Status**: Production Specification  
**Classification**: Internal Use - IDRM Project
