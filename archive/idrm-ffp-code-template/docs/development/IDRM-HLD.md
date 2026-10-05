# IDRM: High-Level Design (HLD) - Version 3

## System Architecture & Technical Design

**Document Version**: 3.0
**Date**: May 24, 2026
**Status**: ✅ Approved for Implementation
**Architecture**: Modular Monolith with Bun API Gateway
**Target Audience**: Technical architects, senior developers, DevOps engineers

---

## 📚 **Table of Contents**

### **Part 1: Architecture Overview**

1. [System Architecture](#1-system-architecture)
2. [Architecture Decisions](#2-architecture-decisions)
3. [Component Overview](#3-component-overview)

### **Part 2: Technical Stack**

4. [Technology Stack](#4-technology-stack)
5. [Technology Rationale](#5-technology-rationale)
6. [Development Tools](#6-development-tools)

### **Part 3: System Components**

7. [Frontend Architecture](#7-frontend-architecture)
8. [API Gateway (Bun)](#8-api-gateway-bun)
9. [Backend Architecture](#9-backend-architecture)
10. [Database Design](#10-database-design)
11. [Caching Layer](#11-caching-layer)

### **Part 4: Data & APIs**

12. [Data Flow](#12-data-flow)
13. [API Design](#13-api-design)
14. [Data Models](#14-data-models)

### **Part 5: Infrastructure**

15. [Deployment Architecture](#15-deployment-architecture)
16. [Security Architecture](#16-security-architecture)
17. [Scalability Design](#17-scalability-design)
18. [Monitoring &amp; Observability](#18-monitoring-observability)

### **Part 6: Integration & Future**

19. [Integration Points](#19-integration-points)
20. [Future Evolution](#20-future-evolution)

---

# **PART 1: ARCHITECTURE OVERVIEW**

---

# 1. **System Architecture**

## 1.1 Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         INTERNET / USERS                        │
│  (Citizens, Providers, Coordinators, Admins)                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS (Port 443)
                            │ SSL/TLS Encrypted
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Responsibilities:                                        │  │
│  │ ✓ SSL Termination (HTTPS → HTTP)                       │  │
│  │ ✓ Load Balancing (Round-robin, least-conn)             │  │
│  │ ✓ DDoS Protection (Connection limits)                  │  │
│  │ ✓ Static Asset Caching                                 │  │
│  │ ✓ Gzip Compression                                      │  │
│  │ ✓ Rate Limiting (Connection-level)                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Configuration:                                                 │
│  ├─ Port: 80 (redirect to 443), 443 (SSL)                     │
│  ├─ Max connections: 10,000                                     │
│  ├─ Timeout: 60s                                               │
│  └─ Worker processes: Auto (CPU cores)                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTP (Internal Network)
                            │ Port 3000
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│              BUN API GATEWAY (Application Gateway)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Responsibilities:                                        │  │
│  │ ✓ Rate Limiting (Redis-based, per-user, per-endpoint)  │  │
│  │ ✓ JWT Authentication (Token validation)                │  │
│  │ ✓ Authorization (Role-based access control)            │  │
│  │ ✓ Security Headers (CSP, HSTS, X-Frame-Options)        │  │
│  │ ✓ Static File Serving (HTML, CSS, JS, Images)          │  │
│  │ ✓ Request Routing (API vs Static)                      │  │
│  │ ✓ CORS Handling                                        │  │
│  │ ✓ Request Logging                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Technology: Bun v1.1+ (TypeScript)                            │
│  Port: 3000                                                     │
│  Performance: 50,000 req/s (static), 40,000 req/s (proxy)     │
│                                                                 │
│  Request Flow:                                                  │
│  1. Check rate limit → 429 if exceeded                         │
│  2. Validate JWT (if /api/*) → 401 if invalid                 │
│  3. Check authorization → 403 if unauthorized                   │
│  4. Route:                                                      │
│     ├─ /api/* → Proxy to Backend (Port 8000)                  │
│     └─ /* → Serve static files from /public                   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ For /api/* requests only
                            │ HTTP (Internal)
                            │ Port 8000
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│         MONOLITHIC FASTAPI APPLICATION (Backend)                │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 MODULAR INTERNAL STRUCTURE               │  │
│  │                                                          │  │
│  │  app/                                                    │  │
│  │  ├─ main.py (FastAPI app, single entry point)          │  │
│  │  │                                                       │  │
│  │  ├─ api/ (API Routes - Modular!)                       │  │
│  │  │   ├─ auth.py                                        │  │
│  │  │   │   └─ POST /api/v1/auth/login                    │  │
│  │  │   │   └─ POST /api/v1/auth/register                 │  │
│  │  │   │   └─ POST /api/v1/auth/refresh                  │  │
│  │  │   │                                                  │  │
│  │  │   ├─ services.py                                    │  │
│  │  │   │   └─ GET /api/v1/services (list)               │  │
│  │  │   │   └─ POST /api/v1/services (create)            │  │
│  │  │   │   └─ GET /api/v1/services/{id} (details)       │  │
│  │  │   │   └─ POST /api/v1/services/{id}/accept         │  │
│  │  │   │   └─ POST /api/v1/services/{id}/complete       │  │
│  │  │   │                                                  │  │
│  │  │   ├─ geo.py (Geospatial)                           │  │
│  │  │   │   └─ GET /api/v1/geo/nearby                    │  │
│  │  │   │   └─ POST /api/v1/geo/cluster                  │  │
│  │  │   │                                                  │  │
│  │  │   ├─ analytics.py                                   │  │
│  │  │   ├─ users.py                                       │  │
│  │  │   ├─ organizations.py                               │  │
│  │  │   └─ admin.py                                       │  │
│  │  │                                                      │  │
│  │  ├─ models/ (SQLAlchemy ORM models)                   │  │
│  │  ├─ schemas/ (Pydantic request/response schemas)      │  │
│  │  ├─ crud/ (Database operations)                        │  │
│  │  ├─ services/ (Business logic)                         │  │
│  │  └─ core/ (Config, security, database connection)     │  │
│  │                                                          │  │
│  │  ALL modules run in ONE Python process!                │  │
│  │  Can be run independently for testing.                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  Technology: Python 3.11+, FastAPI 0.109+                      │
│  Port: 8000                                                     │
│  Process: Single uvicorn process (can scale horizontally)     │
│  Performance: 1,000-2,000 req/s                                │
└─────────────┬───────────────────────┬───────────────────────────┘
              │                       │
              │ PostgreSQL            │ Redis
              │ Connection Pool       │ Connection Pool
              ↓                       ↓
┌──────────────────────┐    ┌──────────────────────┐
│   POSTGRESQL 15      │    │      REDIS 7         │
│   + PostGIS 3.3      │    │                      │
│  ┌────────────────┐  │    │  ┌────────────────┐  │
│  │ Data Storage:  │  │    │  │ Use Cases:     │  │
│  │ ✓ Users        │  │    │  │ ✓ Sessions     │  │
│  │ ✓ Services     │  │    │  │ ✓ Cache        │  │
│  │ ✓ Orgs         │  │    │  │ ✓ Rate limits  │  │
│  │ ✓ Locations    │  │    │  │ ✓ Real-time    │  │
│  │ ✓ Audit logs   │  │    │  │ ✓ Job queue    │  │
│  └────────────────┘  │    │  └────────────────┘  │
│                      │    │                      │
│  Port: 5432          │    │  Port: 6379          │
│  Max connections:500 │    │  Max memory: 2GB     │
└──────────────────────┘    └──────────────────────┘
```

---

## 1.2 Request Flow Examples

### **Example 1: Static File Request** (index.html)

```
1. USER REQUEST:
   Browser: https://idrm.gov.in/
   
2. NGINX (Port 443):
   ├─ Receives HTTPS request
   ├─ SSL termination (HTTPS → HTTP)
   ├─ Forwards to: http://bun-gateway:3000/
   └─ Time: ~5ms
   
3. BUN GATEWAY (Port 3000):
   ├─ Receives: GET /
   ├─ Rate limit check: Pass (1000/min allowed for static)
   ├─ No auth needed (public page)
   ├─ Serve static file: /public/index.html
   ├─ Add security headers (CSP, HSTS, etc.)
   └─ Time: ~10ms
   
4. RESPONSE:
   ├─ Status: 200 OK
   ├─ Content-Type: text/html
   ├─ Cache-Control: no-cache
   ├─ Content-Length: 45,678 bytes
   └─ Total time: ~15ms

USER SEES: Homepage loaded ✓
```

---

### **Example 2: API Request** (Create Service Request)

```
1. USER REQUEST:
   POST https://idrm.gov.in/api/v1/services
   Headers:
     Authorization: Bearer eyJhbGc...
     Content-Type: application/json
   Body:
     {
       "service_type": "MEDICAL",
       "priority": "CRITICAL",
       "location": {"type": "Point", "coordinates": [78.4867, 17.3850]},
       "description": "Elderly man, chest pain, flood water rising"
     }

2. NGINX:
   ├─ SSL termination
   ├─ Forward to Bun Gateway
   └─ Time: ~5ms

3. BUN GATEWAY:
   ├─ Check rate limit:
   │   └─ Key: "rate_limit:/api/v1/services:203.0.113.45"
   │   └─ Count: 12/60 → Pass ✓
   │
   ├─ Validate JWT:
   │   └─ Token: eyJhbGc... (valid, expires in 14 min)
   │   └─ User: user_id=abc123, role=CITIZEN ✓
   │
   ├─ Check authorization:
   │   └─ Endpoint: POST /api/v1/services
   │   └─ Required role: CITIZEN or higher ✓
   │
   ├─ Add headers:
   │   └─ X-User-ID: abc123
   │   └─ X-User-Role: CITIZEN
   │
   └─ Proxy to: http://backend:8000/api/v1/services
       Time: ~15ms

4. FASTAPI BACKEND:
   ├─ Route: POST /api/v1/services
   ├─ Handler: services.py → create_service()
   │
   ├─ Validate request (Pydantic):
   │   └─ service_type: MEDICAL ✓
   │   └─ priority: CRITICAL ✓
   │   └─ location: Valid GeoJSON ✓
   │   └─ Time: ~2ms
   │
   ├─ Business logic:
   │   └─ Priority CRITICAL → Auto-approve
   │   └─ Find nearby providers (PostGIS query)
   │   └─ Time: ~50ms
   │
   ├─ Database INSERT:
   │   └─ INSERT INTO service_requests (...)
   │   └─ RETURNING service_id
   │   └─ Time: ~30ms
   │
   ├─ Cache invalidation:
   │   └─ DELETE redis key: "services:list:*"
   │   └─ Time: ~5ms
   │
   ├─ Send notifications:
   │   └─ Queue SMS/Email jobs
   │   └─ Time: ~10ms
   │
   └─ Return response:
       Time: ~100ms total

5. RESPONSE PATH:
   Backend → Bun → NGINX → User
   
6. FINAL RESPONSE:
   Status: 201 Created
   Body:
     {
       "status": "success",
       "data": {
         "service_id": "550e8400-e29b-41d4-a716-446655440000",
         "status": "SUBMITTED",
         "created_at": "2026-05-24T10:30:00Z",
         "estimated_response_time": "2 hours"
       }
     }
   
   Total time: ~125ms

USER SEES: "Service request created successfully" ✓
```

---

# 2. **Architecture Decisions**

## 2.1 Why Modular Monolith?

### **Decision Summary**:

```
CHOSEN: Modular Monolith
INSTEAD OF: Pure Monolith OR Microservices
```

### **Comparison Table**:

| Aspect                      | Pure Monolith         | Modular Monolith ✓   | Microservices    |
| --------------------------- | --------------------- | --------------------- | ---------------- |
| **Deployment**        | Single deploy         | Single deploy         | Multiple deploys |
| **Complexity**        | Low                   | Medium                | High             |
| **Development Speed** | Fast                  | Fast                  | Slow             |
| **Scaling**           | Vertical only         | Vertical + Horizontal | Horizontal       |
| **Testing**           | Simple                | Simple                | Complex          |
| **Debugging**         | Easy                  | Easy                  | Hard             |
| **Team Size**         | 1-3                   | 2-5                   | 10+              |
| **Cost**              | $100/mo | $100-500/mo | $1000+/mo             |                  |
| **Future-Proof**      | No                    | YES ✓                | Yes              |

### **Why Modular Monolith Wins for IDRM**:

```
REASON 1: Government Project Needs
├─ Reliability > Complexity
├─ Easier to audit
├─ Lower operational overhead
└─ Simpler compliance

REASON 2: Team & Budget
├─ Team size: 5-7 developers initially
├─ Budget: Limited (MVP)
├─ Need: Ship fast
└─ Modular monolith = optimal

REASON 3: MVP Requirements
├─ Launch in 4 months
├─ Pilot in 2 districts
├─ Prove value quickly
└─ Iterate based on feedback

REASON 4: Disaster Response Context
├─ Must work during crisis
├─ Fewer moving parts = more reliable
├─ Simple = easier to fix quickly
└─ Lives depend on uptime

REASON 5: Future-Proof
├─ Modular boundaries preserved
├─ Can extract to microservices later
├─ When: After proven, when scale demands
└─ How: Well-documented transition guide
```

---

## 2.2 Why Bun API Gateway?

### **Decision Summary**:

```
CHOSEN: Bun API Gateway + Modular Monolith
INSTEAD OF: NGINX-only OR Node.js Gateway
```

### **Comparison**:

| Feature                  | NGINX Only     | Node.js Gateway | Bun Gateway ✓ |
| ------------------------ | -------------- | --------------- | -------------- |
| **Static Files**   | Excellent      | Good            | Excellent      |
| **Rate Limiting**  | External (Lua) | Built-in        | Built-in       |
| **JWT Validation** | External       | Built-in        | Built-in       |
| **Performance**    | 60k req/s      | 15k req/s       | 50k req/s      |
| **Ease of Dev**    | Hard (Lua)     | Easy (JS)       | Easy (TS)      |
| **Memory**         | 10MB           | 150MB           | 50MB           |

### **Why Bun Gateway**:

```
✓ Centralized Security
  └─ Rate limiting, auth, headers all in one place
  
✓ High Performance
  └─ 3x faster than Node.js
  └─ Nearly as fast as NGINX for proxy
  
✓ Easy to Code
  └─ TypeScript (maintainable)
  └─ Can hire from larger talent pool
  
✓ Full Control
  └─ Custom logic for routing
  └─ Advanced security rules
  └─ Easy to debug
  
✓ Static File Serving
  └─ 50,000 req/s
  └─ Built-in caching
  └─ ETag support
```

---

# 3. **Component Overview**

## 3.1 System Components

```
┌──────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                  │
│  ┌────────────────────────────────────────────────┐  │
│  │ Static Frontend (HTML/CSS/JavaScript)          │  │
│  │ ├─ Landing pages                               │  │
│  │ ├─ Authentication pages                        │  │
│  │ ├─ Dashboard (Citizen, Provider, Coordinator)  │  │
│  │ ├─ Map interface (Leaflet.js)                 │  │
│  │ └─ Admin portal                                │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Technology: HTML5, Tailwind CSS, Vanilla JavaScript│
│  Served by: Bun API Gateway                         │
│  Performance: < 2s page load                        │
└──────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────┐
│                   GATEWAY LAYER                      │
│  ┌────────────────────────────────────────────────┐  │
│  │ Bun API Gateway (TypeScript)                   │  │
│  │                                                │  │
│  │ Middleware Stack:                              │  │
│  │ 1. CORS Handler                                │  │
│  │ 2. Rate Limiter (Redis)                        │  │
│  │ 3. JWT Authenticator                           │  │
│  │ 4. Authorization (RBAC)                        │  │
│  │ 5. Security Headers                            │  │
│  │ 6. Request Logger                              │  │
│  │                                                │  │
│  │ Routes:                                        │  │
│  │ ├─ /api/* → Proxy to Backend                  │  │
│  │ └─ /* → Serve static files                    │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Technology: Bun 1.1+, TypeScript                   │
│  Performance: 40,000 req/s (proxy)                  │
└──────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────┐
│                 APPLICATION LAYER                    │
│  ┌────────────────────────────────────────────────┐  │
│  │ FastAPI Monolith (Python 3.11+)                │  │
│  │                                                │  │
│  │ Modules (Modular Design):                      │  │
│  │                                                │  │
│  │ 1. Authentication Module                       │  │
│  │    ├─ User registration                        │  │
│  │    ├─ Login (JWT generation)                   │  │
│  │    ├─ Password reset                           │  │
│  │    └─ Token refresh                            │  │
│  │                                                │  │
│  │ 2. Service Management Module                   │  │
│  │    ├─ Create service request                   │  │
│  │    ├─ List/search services                     │  │
│  │    ├─ Accept service                           │  │
│  │    ├─ Complete service                         │  │
│  │    └─ Verify service                           │  │
│  │                                                │  │
│  │ 3. Geospatial Module                          │  │
│  │    ├─ Find nearby services                     │  │
│  │    ├─ Cluster analysis                         │  │
│  │    ├─ Route optimization                       │  │
│  │    └─ GeoJSON generation                       │  │
│  │                                                │  │
│  │ 4. User Management Module                      │  │
│  │    ├─ Profile management                       │  │
│  │    ├─ Role management                          │  │
│  │    └─ Preferences                              │  │
│  │                                                │  │
│  │ 5. Organization Module                         │  │
│  │    ├─ Organization registration                │  │
│  │    ├─ Capacity management                      │  │
│  │    └─ Team management                          │  │
│  │                                                │  │
│  │ 6. Analytics Module                            │  │
│  │    ├─ Dashboard metrics                        │  │
│  │    ├─ Report generation                        │  │
│  │    ├─ Performance analytics                    │  │
│  │    └─ Disaster insights                        │  │
│  │                                                │  │
│  │ 7. Admin Module                                │  │
│  │    ├─ User moderation                          │  │
│  │    ├─ System configuration                     │  │
│  │    ├─ Audit logs                               │  │
│  │    └─ Approval workflows                       │  │
│  │                                                │  │
│  │ 8. Notification Module                         │  │
│  │    ├─ Email notifications                      │  │
│  │    ├─ SMS notifications                        │  │
│  │    └─ In-app notifications                     │  │
│  └────────────────────────────────────────────────┘  │
│                                                      │
│  Technology: FastAPI, Uvicorn, Pydantic             │
│  Performance: 1,000-2,000 req/s                      │
└──────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────┐
│                    DATA LAYER                        │
│  ┌──────────────┐          ┌──────────────────────┐  │
│  │ PostgreSQL   │          │       Redis          │  │
│  │ + PostGIS    │          │                      │  │
│  │              │          │                      │  │
│  │ Tables:      │          │ Use Cases:           │  │
│  │ ✓ users      │          │ ✓ Sessions (JWT)     │  │
│  │ ✓ services   │          │ ✓ Rate limits        │  │
│  │ ✓ orgs       │          │ ✓ API cache          │  │
│  │ ✓ audit      │          │ ✓ Job queue          │  │
│  │              │          │ ✓ Real-time pub/sub  │  │
│  └──────────────┘          └──────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

---

## 3.2 Component Responsibilities

### **Frontend (Presentation Layer)**:

```
Responsibilities:
✓ User interface rendering
✓ Form validation (client-side)
✓ Map visualization (Leaflet)
✓ API calls to backend
✓ Local state management
✓ Responsive design

Does NOT:
✗ Business logic
✗ Data persistence
✗ Authentication logic
✗ Complex calculations

Technology Choices:
├─ HTML5: Semantic markup
├─ Tailwind CSS: Utility-first styling
├─ Vanilla JavaScript: No framework overhead
├─ Leaflet.js: Lightweight maps
└─ Axios: HTTP client
```

### **Bun Gateway (Security Layer)**:

```
Responsibilities:
✓ Rate limiting (prevent abuse)
✓ Authentication (JWT validation)
✓ Authorization (role checking)
✓ Security headers (CSP, HSTS)
✓ Static file serving
✓ Request routing
✓ CORS handling
✓ Request logging

Does NOT:
✗ Business logic
✗ Database access
✗ Complex computations

Technology Choices:
├─ Bun: Fast JavaScript runtime
├─ TypeScript: Type safety
├─ ioredis: Redis client
└─ jsonwebtoken: JWT handling
```

### **FastAPI Backend (Business Logic Layer)**:

```
Responsibilities:
✓ Business logic implementation
✓ Data validation (server-side)
✓ Database operations (CRUD)
✓ Complex computations
✓ Service orchestration
✓ Email/SMS sending
✓ Report generation
✓ Background jobs

Does NOT:
✗ UI rendering (frontend's job)
✗ Rate limiting (gateway's job)
✗ Static file serving (gateway's job)

Technology Choices:
├─ FastAPI: Modern Python framework
├─ SQLAlchemy: ORM for database
├─ Pydantic: Data validation
├─ Alembic: Database migrations
└─ Celery: Background tasks
```

### **PostgreSQL (Data Persistence)**:

```
Responsibilities:
✓ Data storage (persistent)
✓ ACID transactions
✓ Complex queries
✓ Geospatial operations (PostGIS)
✓ Full-text search
✓ Data integrity (constraints)

Technology Choices:
├─ PostgreSQL 15: Reliability
├─ PostGIS 3.3: Geospatial
└─ pg_trgm: Full-text search
```

### **Redis (Caching & Sessions)**:

```
Responsibilities:
✓ Session storage (fast)
✓ API response caching
✓ Rate limit counters
✓ Job queue (Celery)
✓ Real-time pub/sub

Technology Choices:
└─ Redis 7: In-memory speed
```

---

# **PART 2: TECHNICAL STACK**

---

# 4. **Technology Stack**

## 4.1 Complete Technology Stack

```
┌─────────────────────────────────────────────────────┐
│                   FRONTEND STACK                    │
├─────────────────────────────────────────────────────┤
│ Core Technologies:                                  │
│ ├─ HTML5                      (Structure)           │
│ ├─ CSS3 + Tailwind CSS 3.4    (Styling)            │
│ └─ JavaScript ES6+             (Interactivity)      │
│                                                     │
│ Libraries:                                          │
│ ├─ Leaflet.js 1.9             (Maps)               │
│ ├─ Chart.js 4.4               (Charts)             │
│ ├─ Axios 1.6                  (HTTP client)        │
│ ├─ DOMPurify 3.0              (XSS prevention)     │
│ └─ Luxon 3.4                  (Date/time)          │
│                                                     │
│ Build Tools (Optional):                             │
│ ├─ Vite (for bundling, if needed later)            │
│ └─ PostCSS (for Tailwind processing)               │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 API GATEWAY STACK                   │
├─────────────────────────────────────────────────────┤
│ Runtime:                                            │
│ └─ Bun 1.1+                    (JavaScript runtime) │
│                                                     │
│ Language:                                           │
│ └─ TypeScript 5.3+             (Type safety)       │
│                                                     │
│ Libraries:                                          │
│ ├─ ioredis 5.3                 (Redis client)      │
│ ├─ jsonwebtoken 9.0            (JWT handling)      │
│ └─ zod 3.22                    (Schema validation) │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                   BACKEND STACK                     │
├─────────────────────────────────────────────────────┤
│ Language & Framework:                               │
│ ├─ Python 3.11+                (Language)          │
│ ├─ FastAPI 0.109+              (Web framework)     │
│ └─ Uvicorn 0.27+               (ASGI server)       │
│                                                     │
│ ORM & Database:                                     │
│ ├─ SQLAlchemy 2.0+             (ORM)               │
│ ├─ Psycopg 3.1+                (PostgreSQL driver) │
│ ├─ Alembic 1.13+               (Migrations)        │
│ └─ GeoAlchemy2 0.14+           (PostGIS support)   │
│                                                     │
│ Data Validation:                                    │
│ └─ Pydantic 2.6+               (Schemas)           │
│                                                     │
│ Authentication:                                     │
│ ├─ python-jose 3.3             (JWT)               │
│ ├─ passlib 1.7                 (Password hashing)  │
│ └─ bcrypt 4.1                  (Hashing backend)   │
│                                                     │
│ Caching & Jobs:                                     │
│ ├─ redis-py 5.0                (Redis client)      │
│ ├─ Celery 5.3                  (Task queue)        │
│ └─ APScheduler 3.10            (Scheduled jobs)    │
│                                                     │
│ Email & Notifications:                              │
│ ├─ python-email 2.0            (Email sending)     │
│ ├─ Jinja2 3.1                  (Templates)         │
│ └─ Twilio SDK 9.0              (SMS - optional)    │
│                                                     │
│ PDF Generation:                                     │
│ └─ WeasyPrint 61.0             (HTML to PDF)       │
│                                                     │
│ Testing:                                            │
│ ├─ pytest 8.0                  (Test framework)    │
│ ├─ pytest-cov 4.1              (Coverage)          │
│ ├─ httpx 0.26                  (Async HTTP client) │
│ └─ faker 22.0                  (Test data)         │
│                                                     │
│ Code Quality:                                       │
│ ├─ black 24.1                  (Formatting)        │
│ ├─ ruff 0.1                    (Linting)           │
│ └─ mypy 1.8                    (Type checking)     │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  DATABASE STACK                     │
├─────────────────────────────────────────────────────┤
│ Primary Database:                                   │
│ ├─ PostgreSQL 15.5             (Relational DB)     │
│ ├─ PostGIS 3.3                 (Geospatial ext)    │
│ └─ pg_trgm                     (Full-text search)  │
│                                                     │
│ Caching & Sessions:                                 │
│ └─ Redis 7.2                   (In-memory store)   │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│               INFRASTRUCTURE STACK                  │
├─────────────────────────────────────────────────────┤
│ Containerization:                                   │
│ ├─ Docker 24.0+                (Containers)        │
│ └─ Docker Compose 2.23+        (Orchestration)     │
│                                                     │
│ Reverse Proxy:                                      │
│ └─ NGINX 1.25+                 (Web server)        │
│                                                     │
│ Monitoring:                                         │
│ ├─ Prometheus 2.48             (Metrics)           │
│ ├─ Grafana 10.2                (Visualization)     │
│ └─ Loki 2.9                    (Log aggregation)   │
│                                                     │
│ CI/CD:                                              │
│ └─ GitHub Actions              (Automation)        │
│                                                     │
│ Cloud (Production):                                 │
│ ├─ DigitalOcean / Linode      (Hosting - MVP)     │
│ └─ AWS / GCP                   (Future scaling)    │
└─────────────────────────────────────────────────────┘
```

---

## 4.2 Version Matrix

| Technology           | Version | Released | EOL      | Why This Version                                |
| -------------------- | ------- | -------- | -------- | ----------------------------------------------- |
| **Python**     | 3.11+   | Oct 2022 | Oct 2027 | Performance improvements, better error messages |
| **FastAPI**    | 0.109+  | Jan 2024 | N/A      | Latest features, async support                  |
| **PostgreSQL** | 15.5    | Nov 2022 | Nov 2027 | Stable, mature, PostGIS 3.3 support             |
| **PostGIS**    | 3.3     | Aug 2023 | N/A      | Latest geospatial features                      |
| **Redis**      | 7.2     | Oct 2023 | N/A      | Better performance, JSON support                |
| **Bun**        | 1.1+    | Jan 2024 | N/A      | Production-ready, fast                          |
| **Node.js**    | 18 LTS  | Oct 2022 | Apr 2025 | Fallback if Bun issues                          |

---

# 5. **Technology Rationale**

## 5.1 Why Python + FastAPI?

```
SELECTED: Python 3.11 + FastAPI 0.109
ALTERNATIVES CONSIDERED: Node.js + Express, Go + Gin, Java + Spring Boot

REASONS:

1. DEVELOPER PRODUCTIVITY ✓
   ├─ Python: Easy to learn, read, write
   ├─ FastAPI: Automatic API docs (Swagger)
   ├─ Pydantic: Automatic data validation
   └─ Result: Ship features faster

2. POSTGIS SUPPORT ✓
   ├─ Python: Excellent PostGIS libraries
   ├─ SQLAlchemy + GeoAlchemy2: Mature
   ├─ Node.js: Sequelize-PostGIS (limited)
   └─ Result: Geospatial queries easier

3. DATA SCIENCE READY ✓
   ├─ Python: NumPy, Pandas, Scikit-learn
   ├─ Future: ML-powered predictions
   ├─ Node.js: Limited ML libraries
   └─ Result: Future-proof for AI features

4. GOVERNMENT PREFERENCE ✓
   ├─ Many govt projects use Python
   ├─ Familiarity with teams
   ├─ Easier hiring in India
   └─ Result: Aligned with ecosystem

5. PERFORMANCE ✓
   ├─ FastAPI: Async support (like Node.js)
   ├─ Uvicorn: 1,000-2,000 req/s
   ├─ Good enough for MVP
   └─ Result: Meets performance targets

TRADE-OFFS:
├─ Node.js: Slightly faster (2-3x)
├─ Go: Much faster (10x), but harder to find developers
├─ Java: Enterprise-grade, but verbose, slower development
└─ VERDICT: Python's developer productivity wins for MVP
```

---

## 5.2 Why Bun > Node.js?

```
SELECTED: Bun 1.1
ALTERNATIVES: Node.js 18 LTS, Deno 1.4

REASONS:

1. PERFORMANCE ✓
   ├─ Bun: 50,000 req/s (static files)
   ├─ Node.js: 15,000 req/s
   ├─ 3x faster!
   └─ Result: Better user experience

2. BUILT-IN FEATURES ✓
   ├─ Bun: Built-in TypeScript support
   ├─ Node.js: Needs ts-node or compilation
   ├─ Bun: Built-in bundler
   └─ Result: Simpler tooling

3. COMPATIBILITY ✓
   ├─ Bun: Runs npm packages
   ├─ All our dependencies work
   └─ Result: No rewriting needed

4. MODERN RUNTIME ✓
   ├─ Written in Zig (faster than C)
   ├─ JavaScriptCore engine (Safari's engine)
   ├─ Better memory management
   └─ Result: More efficient

5. PRODUCTION READY ✓
   ├─ Bun 1.0 released Sept 2023
   ├─ Bun 1.1 (current) = stable
   ├─ Used by: Vercel, Supabase, others
   └─ Result: Battle-tested

FALLBACK PLAN:
├─ If Bun issues arise
├─ Switch to Node.js (same code works)
├─ Performance: Still good (15k req/s)
└─ VERDICT: Low risk, high reward
```

---

## 5.3 Why PostgreSQL + PostGIS?

```
SELECTED: PostgreSQL 15 + PostGIS 3.3
ALTERNATIVES: MySQL + Spatial, MongoDB, Neo4j

REASONS:

1. BEST GEOSPATIAL DB ✓
   ├─ PostGIS: Industry standard
   ├─ ST_Distance, ST_DWithin (find nearby)
   ├─ Spatial indexes (GIST)
   └─ Result: Perfect for our use case

2. ACID COMPLIANCE ✓
   ├─ Transactions: All-or-nothing
   ├─ Consistency: Data integrity
   ├─ Isolation: Concurrent users
   └─ Result: Data correctness guaranteed

3. SCALABILITY ✓
   ├─ Proven: Instagram (1B+ users)
   ├─ Our scale: 1M users (easily handles)
   └─ Result: Won't outgrow it

4. FULL-TEXT SEARCH ✓
   ├─ pg_trgm: Fuzzy search
   ├─ GIN indexes: Fast search
   ├─ No need for Elasticsearch (simpler)
   └─ Result: One less service

5. GOVERNMENT STANDARD ✓
   ├─ Open source (no licensing)
   ├─ Used by many govt projects
   ├─ Strong community
   └─ Result: Aligned with standards

TRADE-OFFS:
├─ MongoDB: Easier schema changes, but weaker geospatial
├─ MySQL: Simpler, but PostGIS better
├─ Elasticsearch: Better search, but complex
└─ VERDICT: PostgreSQL + PostGIS is the gold standard
```

---

## 5.4 Why Redis?

```
SELECTED: Redis 7.2
ALTERNATIVES: Memcached, In-memory SQLite

REASONS:

1. MULTI-PURPOSE ✓
   ├─ Sessions: Fast user state
   ├─ Caching: API responses
   ├─ Rate limiting: Counter operations
   ├─ Job queue: Celery backend
   └─ Result: One tool, many uses

2. PERFORMANCE ✓
   ├─ In-memory: Microsecond latency
   ├─ 100,000+ ops/second
   └─ Result: Fast enough for any load

3. DATA STRUCTURES ✓
   ├─ Strings, Lists, Sets, Hashes
   ├─ Sorted Sets (leaderboards)
   ├─ Pub/Sub (real-time)
   └─ Result: Flexible usage

4. PERSISTENCE OPTIONS ✓
   ├─ RDB: Snapshots
   ├─ AOF: Append-only log
   └─ Result: Data survives restarts

5. SIMPLE ✓
   ├─ Easy to set up
   ├─ Easy to operate
   ├─ Great docs
   └─ Result: Low maintenance

TRADE-OFFS:
├─ Memcached: Simpler, but less features
└─ VERDICT: Redis's versatility wins
```

---

**[Continuing with remaining sections...]**

Due to length, I'll continue with the key remaining sections in the HLD:

---

# **PART 3: SYSTEM COMPONENTS (Continued)**

# 7. **Frontend Architecture**

## 7.1 Frontend Structure

```
frontend/
├── index.html                         # Landing page
├── pages/
│   ├── auth/
│   │   ├── login.html                 # Login page
│   │   ├── register.html              # Registration
│   │   └── forgot-password.html       # Password reset
│   │
│   ├── app/
│   │   ├── dashboard.html             # Main dashboard
│   │   ├── create-service.html        # Create request
│   │   ├── service-detail.html        # View details
│   │   ├── my-services.html           # User's requests
│   │   └── map.html                   # Full map view
│   │
│   ├── provider/
│   │   ├── provider-dashboard.html
│   │   └── available-services.html
│   │
│   └── admin/
│       └── admin-dashboard.html
│
├── assets/
│   ├── css/
│   │   ├── tailwind.min.css          # Tailwind CSS
│   │   └── custom.css                # Custom styles
│   │
│   ├── js/
│   │   ├── app.js                    # Main app logic
│   │   ├── auth.js                   # Authentication
│   │   ├── services.js               # Service operations
│   │   ├── map.js                    # Map handling
│   │   ├── utils.js                  # Utilities
│   │   └── config.js                 # Configuration
│   │
│   ├── images/
│   └── icons/
│
└── templates/                         # Server-rendered (Jinja2)
    ├── email/
    │   ├── welcome.html
    │   └── password-reset.html
    └── pdf/
        └── service-receipt.html
```

## 7.2 Frontend Features

```
KEY FEATURES:

1. Responsive Design
   ├─ Mobile-first approach
   ├─ Works on 320px to 2560px screens
   ├─ Touch-optimized
   └─ Adaptive layouts

2. Progressive Enhancement
   ├─ Works without JavaScript (basic)
   ├─ Enhanced with JavaScript
   ├─ Offline support (service workers - future)
   └─ Graceful degradation

3. Performance Optimizations
   ├─ Lazy loading images
   ├─ Minified CSS/JS
   ├─ CDN for libraries
   ├─ Browser caching
   └─ < 2s page load

4. Accessibility (WCAG 2.1 Level AA)
   ├─ Semantic HTML
   ├─ ARIA labels
   ├─ Keyboard navigation
   ├─ Screen reader support
   └─ Color contrast compliant

5. Multi-Language Support
   ├─ Language switcher
   ├─ i18n JSON files
   ├─ RTL support (future)
   └─ 12+ Indian languages (roadmap)
```

---

# 9. **Backend Architecture**

## 9.1 Backend Module Structure

```python
# Modular Monolith Structure

backend/
├── app/
│   ├── __init__.py
│   ├── main.py                       # FastAPI app
│   │
│   ├── api/                          # API Routes
│   │   ├── __init__.py
│   │   ├── deps.py                   # Shared dependencies
│   │   ├── auth.py                   # Auth endpoints
│   │   ├── services.py               # Service endpoints
│   │   ├── users.py                  # User endpoints
│   │   ├── organizations.py          # Org endpoints
│   │   ├── geo.py                    # Geospatial endpoints
│   │   ├── analytics.py              # Analytics endpoints
│   │   └── admin.py                  # Admin endpoints
│   │
│   ├── models/                       # SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py                   # User model
│   │   ├── service.py                # Service model
│   │   ├── organization.py           # Organization model
│   │   └── audit.py                  # Audit log model
│   │
│   ├── schemas/                      # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── user.py                   # User schemas
│   │   ├── service.py                # Service schemas
│   │   └── auth.py                   # Auth schemas
│   │
│   ├── crud/                         # Database operations
│   │   ├── __init__.py
│   │   ├── user.py                   # User CRUD
│   │   ├── service.py                # Service CRUD
│   │   └── organization.py           # Org CRUD
│   │
│   ├── services/                     # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Auth logic
│   │   ├── service_matching.py       # Matching algorithm
│   │   ├── geospatial.py             # Geo calculations
│   │   └── notifications.py          # Email/SMS sending
│   │
│   ├── core/                         # Core utilities
│   │   ├── __init__.py
│   │   ├── config.py                 # Configuration
│   │   ├── security.py               # Security utils
│   │   ├── database.py               # DB connection
│   │   └── redis.py                  # Redis client
│   │
│   └── tests/                        # Unit tests
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_services.py
│       └── test_geo.py
│
├── tests/                            # Integration tests
│   ├── integration/
│   └── e2e/
│
├── alembic/                          # Migrations
│   ├── versions/
│   └── env.py
│
├── requirements.txt                  # Dependencies
├── pytest.ini                        # Test config
└── main.py                           # Entry point
```

---

# 10. **Database Design**

## 10.1 Core Tables

```sql
-- Users Table
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    role VARCHAR(50) NOT NULL, -- CITIZEN, VOLUNTEER, ORGANIZER, PROVIDER, MANAGER, EVENT_MANAGER, EXECUTIVE (Post-MVP), DM_AUTHORITY, AUDITOR, ADMIN
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Organizations Table
CREATE TABLE organizations (
    org_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(50) NOT NULL, -- NGO, HOSPITAL, GOVT_AGENCY
    registration_number VARCHAR(100),
    capacity INT DEFAULT 0,
    service_types VARCHAR[] NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Service Requests Table (with PostGIS)
CREATE TABLE service_requests (
    service_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    requestor_id UUID REFERENCES users(user_id),
    service_type VARCHAR(50) NOT NULL, -- RESCUE, MEDICAL, FOOD, SHELTER, WATER
    priority VARCHAR(20) NOT NULL, -- CRITICAL, HIGH, MEDIUM, LOW
    status VARCHAR(50) DEFAULT 'SUBMITTED', -- SUBMITTED, APPROVED, ACCEPTED, IN_PROGRESS, COMPLETED, VERIFIED, REJECTED, CANCELLED, EXPIRED, DISPUTED
    location GEOMETRY(Point, 4326) NOT NULL, -- PostGIS point
    address TEXT,
    description TEXT NOT NULL,
    privacy_level VARCHAR(20) DEFAULT 'PROTECTED', -- PUBLIC, PROTECTED, PRIVATE (default PROTECTED)
    provider_id UUID REFERENCES organizations(org_id),
    accepted_at TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial Index
CREATE INDEX idx_service_requests_location ON service_requests USING GIST(location);

-- Other Indexes
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_priority ON service_requests(priority);
CREATE INDEX idx_service_requests_created_at ON service_requests(created_at);
```

---

# 15. **Deployment Architecture**

## 15.1 MVP Deployment (Single Server)

```
┌─────────────────────────────────────────────────────┐
│            DIGITALOCEAN DROPLET                     │
│         (8 vCPU, 16GB RAM, 200GB SSD)              │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │            DOCKER COMPOSE                     │ │
│  │                                               │ │
│  │  ┌─────────────┐  ┌──────────────┐          │ │
│  │  │   NGINX     │  │     BUN      │          │ │
│  │  │  (Port 80)  │  │  (Port 3000) │          │ │
│  │  └─────────────┘  └──────────────┘          │ │
│  │         │                  │                 │ │
│  │         └──────────────────┘                 │ │
│  │                  │                           │ │
│  │         ┌────────▼────────┐                  │ │
│  │         │    FASTAPI      │                  │ │
│  │         │  (Port 8000)    │                  │ │
│  │         └────────┬────────┘                  │ │
│  │                  │                           │ │
│  │     ┌────────────┴───────────┐              │ │
│  │     │                        │              │ │
│  │  ┌──▼──────┐          ┌─────▼────┐         │ │
│  │  │PostgreSQL│          │  Redis   │         │ │
│  │  │(Port 5432)│          │(Port 6379)│         │ │
│  │  └──────────┘          └──────────┘         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Resources:                                         │
│  ├─ NGINX: 512MB RAM, 1 vCPU                       │
│  ├─ Bun: 2GB RAM, 2 vCPU                          │
│  ├─ FastAPI: 4GB RAM, 2 vCPU                      │
│  ├─ PostgreSQL: 6GB RAM, 2 vCPU                   │
│  ├─ Redis: 2GB RAM, 1 vCPU                        │
│  └─ System: 1.5GB RAM                             │
│                                                     │
│  Cost: ~$96/month (DigitalOcean)                   │
└─────────────────────────────────────────────────────┘
```

---

# 16. **Security Architecture**

## 16.1 Security Layers

```
LAYER 1: NETWORK SECURITY
├─ NGINX: SSL/TLS 1.3
├─ Firewall: Only ports 80, 443 open
├─ DDoS protection: Connection limits
└─ IP whitelisting (admin endpoints)

LAYER 2: APPLICATION GATEWAY
├─ Rate limiting: Per-user, per-endpoint
├─ JWT validation: Token signature + expiry
├─ CORS: Restrict origins
└─ Security headers: CSP, HSTS, X-Frame-Options

LAYER 3: APPLICATION SECURITY
├─ Input validation: Pydantic schemas
├─ SQL injection prevention: Parameterized queries
├─ XSS prevention: DOMPurify, CSP
├─ CSRF protection: SameSite cookies
└─ Authentication: JWT (HS256)

LAYER 4: DATA SECURITY
├─ Encryption at rest: Database encryption
├─ Password hashing: Bcrypt (cost=12)
├─ Sensitive data: Encrypted columns
└─ Audit logs: All critical operations

LAYER 5: COMPLIANCE
├─ CERT-In guidelines
├─ Digital Personal Data Protection Act 2023
├─ GDPR-like principles
└─ Regular security audits
```

---

# 6. **Development Tools**

## 6.1 Development Environment

```
REQUIRED TOOLS:

Code Editors:
├─ VS Code (recommended)
│   ├─ Extensions: Python, ESLint, Prettier
│   ├─ Extensions: Tailwind CSS IntelliSense
│   └─ Extensions: Docker, GitLens
├─ PyCharm (alternative for Python)
└─ WebStorm (alternative for TypeScript)

Version Control:
├─ Git 2.40+
├─ GitHub Desktop (optional)
└─ Repository: github.com/idrm-project

Package Managers:
├─ Python: pip, pipenv (or poetry)
├─ Node.js: npm, yarn, or bun
└─ System: apt (Ubuntu), brew (macOS)

Containerization:
├─ Docker Desktop 24.0+
├─ Docker Compose 2.23+
└─ Kubernetes (production only)

Database Tools:
├─ pgAdmin 4 (PostgreSQL GUI)
├─ psql (command line)
├─ Redis Commander (Redis GUI)
└─ DBeaver (multi-database tool)

API Testing:
├─ Postman (API testing)
├─ Thunder Client (VS Code extension)
├─ HTTPie (command line)
└─ curl (command line)

Code Quality:
├─ Black (Python formatting)
├─ Ruff (Python linting)
├─ Prettier (JS/TS formatting)
├─ ESLint (JS/TS linting)
└─ mypy (Python type checking)
```

---

## 6.2 Development Workflow

**LOCAL DEVELOPMENT SETUP:**

1. Clone Repository:

```bash
git clone https://github.com/idrm-project/idrm.git
cd idrm
```

2. Setup Backend:

```bash
cd src/backend/app-python
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head  # Run migrations
python main.py  # Start server (port 8000)
```

3. Setup Bun Gateway:

```bash
cd src/backend/api-gateway
bun install
bun run dev  # Start gateway (port 3000)
```
4. Setup Database (Docker):

```bash
docker-compose up -d postgres redis
```
5. Load Mock Data:

```bash
psql -U idrm_user -d idrm_db -f database/init/mock_data_unittest.sql
```
6. Access Application:

   - Frontend: `http://localhost:3000`
   - API Docs: `http://localhost:8000/docs`
   - pgAdmin:  `http://localhost:5050`

## 6.3 CI/CD Pipeline

**GITHUB ACTIONS WORKFLOW:**

.github/workflows/test.yml:

```Docker
name: Test & Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest --cov=app --cov-fail-under=80

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - run: bun install
      - run: bun test

  deploy-staging:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - run: ssh deploy@staging.idrm.gov.in 'cd /opt/idrm && git pull && docker-compose up -d'

  deploy-production:
    needs: [test-backend, test-frontend]
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - run: ssh deploy@idrm.gov.in 'cd /opt/idrm && git pull && docker-compose up -d'

```

---

# **PART 3: SYSTEM COMPONENTS (Continued)**

---

# 8. **API Gateway (Bun)**

## 8.1 Bun Gateway Architecture

```

BUN API GATEWAY (Port 3000)

RESPONSIBILITIES:
├─ 1. Rate Limiting (Redis-based)
├─ 2. JWT Authentication
├─ 3. Authorization (RBAC)
├─ 4. Security Headers
├─ 5. Static File Serving
├─ 6. Request Routing
├─ 7. CORS Handling
└─ 8. Request Logging

TECHNOLOGY:
├─ Runtime: Bun 1.1+
├─ Language: TypeScript 5.3+
├─ Redis Client: ioredis 5.3
└─ JWT Library: jsonwebtoken 9.0

```

---

## 8.2 Middleware Stack

```typescript
// bun-gateway/src/index.ts

import { serve } from "bun";
import Redis from "ioredis";
import jwt from "jsonwebtoken";

const redis = new Redis({
  host: process.env.REDIS_HOST || "localhost",
  port: parseInt(process.env.REDIS_PORT || "6379"),
});

// Middleware 1: CORS
function corsMiddleware(req: Request): Response | null {
  const origin = req.headers.get("origin");
  const allowedOrigins = ["https://idrm.gov.in", "http://localhost:3000"];
  
  if (origin && !allowedOrigins.includes(origin)) {
    return new Response("CORS not allowed", { status: 403 });
  }
  return null;
}

// Middleware 2: Rate Limiting
async function rateLimitMiddleware(req: Request): Promise<Response | null> {
  const ip = req.headers.get("x-forwarded-for") || "unknown";
  const path = new URL(req.url).pathname;
  const key = `rate_limit:${path}:${ip}`;
  
  const count = await redis.incr(key);
  if (count === 1) {
    await redis.expire(key, 60); // 1 minute window
  }
  
  const limit = path.startsWith("/api/") ? 100 : 1000; // API: 100/min, Static: 1000/min
  
  if (count > limit) {
    return new Response("Rate limit exceeded", {
      status: 429,
      headers: {
        "Retry-After": "60",
        "X-RateLimit-Limit": limit.toString(),
        "X-RateLimit-Remaining": "0",
      },
    });
  }
  
  return null;
}

// Middleware 3: JWT Authentication (for /api/* only)
function authMiddleware(req: Request): Response | null {
  const path = new URL(req.url).pathname;
  
  // Skip auth for public endpoints
  if (!path.startsWith("/api/") || 
      path === "/api/v1/auth/login" || 
      path === "/api/v1/auth/register") {
    return null;
  }
  
  const authHeader = req.headers.get("authorization");
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return new Response("Unauthorized", { status: 401 });
  }
  
  const token = authHeader.substring(7);
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    // Add user info to headers for backend
    // (This is a simplified approach)
    return null;
  } catch (error) {
    return new Response("Invalid token", { status: 401 });
  }
}

// Middleware 4: Security Headers
function securityHeadersMiddleware(): Record<string, string> {
  return {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
  };
}

// Main Server
serve({
  port: 3000,
  async fetch(req) {
    // Apply middleware chain
    let response: Response | null;
  
    response = corsMiddleware(req);
    if (response) return response;
  
    response = await rateLimitMiddleware(req);
    if (response) return response;
  
    response = authMiddleware(req);
    if (response) return response;
  
    const path = new URL(req.url).pathname;
  
    // Route: API requests to backend
    if (path.startsWith("/api/")) {
      const backendUrl = `http://localhost:8000${path}`;
      const backendResponse = await fetch(backendUrl, {
        method: req.method,
        headers: req.headers,
        body: req.body,
      });
  
      // Add security headers to response
      const headers = new Headers(backendResponse.headers);
      Object.entries(securityHeadersMiddleware()).forEach(([key, value]) => {
        headers.set(key, value);
      });
  
      return new Response(backendResponse.body, {
        status: backendResponse.status,
        headers,
      });
    }
  
    // Route: Static files
    const filePath = path === "/" ? "/index.html" : path;
    const file = Bun.file(`./public${filePath}`);
  
    if (await file.exists()) {
      return new Response(file, {
        headers: {
          ...securityHeadersMiddleware(),
          "Cache-Control": "public, max-age=3600",
        },
      });
    }
  
    return new Response("Not Found", { status: 404 });
  },
});

console.log("Bun API Gateway running on http://localhost:3000");
```

---

## 8.3 Rate Limiting Strategy

```
RATE LIMITS:

By Endpoint Type:
├─ Authentication: 5 requests/min (prevent brute force)
├─ API (general): 100 requests/min per IP
├─ Static files: 1000 requests/min per IP
└─ Admin endpoints: 20 requests/min per IP

By User (Authenticated):
├─ Citizen: 50 API requests/min
├─ Provider: 200 API requests/min
├─ Coordinator: 500 API requests/min
└─ Admin: Unlimited

Implementation:
├─ Redis: INCR + EXPIRE
├─ Key format: "rate_limit:{endpoint}:{identifier}"
├─ Window: Sliding window (1 minute)
└─ Response: 429 Too Many Requests + Retry-After header
```

---

## 8.4 Performance Characteristics

```
BUN GATEWAY PERFORMANCE:

Static File Serving:
├─ Throughput: 50,000 req/s
├─ Latency (p50): 5ms
├─ Latency (p95): 15ms
└─ Memory: ~50MB

API Proxying:
├─ Throughput: 40,000 req/s
├─ Latency (p50): 10ms (+ backend time)
├─ Latency (p95): 30ms (+ backend time)
└─ Memory: ~60MB

Rate Limiting:
├─ Overhead: < 2ms per request
└─ Redis operations: < 1ms

Total Gateway Overhead:
└─ < 10ms per request (negligible)
```

---

# 11. **Caching Layer**

## 11.1 Redis Caching Strategy

```
REDIS USE CASES:

1. SESSION STORAGE
   ├─ Key: "session:{user_id}"
   ├─ Value: JWT payload + metadata
   ├─ TTL: 7 days
   └─ Size: ~1KB per session

2. API RESPONSE CACHING
   ├─ Key: "api:cache:{endpoint}:{params_hash}"
   ├─ Value: Serialized JSON response
   ├─ TTL: Varies by endpoint
   │   ├─ Services list: 60 seconds
   │   ├─ Service details: 30 seconds
   │   ├─ Analytics: 5 minutes
   │   └─ Static data: 1 hour
   └─ Invalidation: On data change

3. RATE LIMITING COUNTERS
   ├─ Key: "rate_limit:{endpoint}:{ip}"
   ├─ Value: Request count
   ├─ TTL: 60 seconds
   └─ Operation: INCR + EXPIRE

4. CELERY JOB QUEUE
   ├─ Queue: "celery:tasks"
   ├─ Use: Background jobs (emails, SMS)
   └─ Persistence: RDB snapshot

5. REAL-TIME DATA
   ├─ Pub/Sub: Service status updates
   ├─ Key: "realtime:{service_id}"
   └─ TTL: 5 minutes
```

---

## 11.2 Cache Invalidation

```python
# src/backend/app-python/core/cache.py

from redis import Redis
from typing import Optional
import json

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True,
)

class CacheManager:
    @staticmethod
    def get(key: str) -> Optional[dict]:
        """Get cached value"""
        data = redis_client.get(key)
        return json.loads(data) if data else None
  
    @staticmethod
    def set(key: str, value: dict, ttl: int = 60):
        """Set cached value with TTL"""
        redis_client.setex(key, ttl, json.dumps(value))
  
    @staticmethod
    def delete(key: str):
        """Delete specific key"""
        redis_client.delete(key)
  
    @staticmethod
    def delete_pattern(pattern: str):
        """Delete all keys matching pattern"""
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
  
    @staticmethod
    def invalidate_service(service_id: str):
        """Invalidate all caches related to a service"""
        patterns = [
            f"api:cache:services:list:*",  # List endpoints
            f"api:cache:services:{service_id}:*",  # Specific service
            f"api:cache:analytics:*",  # Analytics (affected by new data)
        ]
        for pattern in patterns:
            CacheManager.delete_pattern(pattern)

# Usage in API endpoint:
@router.post("/api/v1/services")
async def create_service(service: ServiceCreate, db: Session = Depends(get_db)):
    # Create service
    new_service = crud.create_service(db, service)
  
    # Invalidate related caches
    CacheManager.invalidate_service(new_service.service_id)
  
    return new_service
```

---

## 11.3 Cache Warming

```python
# src/backend/app-python/services/cache_warmer.py

from apscheduler.schedulers.background import BackgroundScheduler
from app.core.cache import CacheManager
from app import crud

scheduler = BackgroundScheduler()

@scheduler.scheduled_job('interval', minutes=5)
def warm_popular_caches():
    """Warm cache with frequently accessed data"""
    db = SessionLocal()
  
    try:
        # Warm services list cache (most common queries)
        popular_filters = [
            {"status": "SUBMITTED", "limit": 20},
            {"status": "ACCEPTED", "limit": 20},
            {"priority": "CRITICAL", "limit": 20},
        ]
  
        for filters in popular_filters:
            key = f"api:cache:services:list:{hash(str(filters))}"
            services = crud.get_services(db, **filters)
            CacheManager.set(key, services, ttl=60)
  
        print("Cache warmed successfully")
    finally:
        db.close()

scheduler.start()
```

---

# **PART 4: DATA & APIs**

---

# 12. **Data Flow**

## 12.1 Service Request Creation Flow

```
COMPLETE DATA FLOW: Creating a Service Request

┌─────────────────────────────────────────────────────┐
│ 1. FRONTEND (JavaScript)                            │
│    User clicks map, fills form, submits             │
└────────────┬────────────────────────────────────────┘
             │ POST /api/v1/services
             │ Headers: Authorization: Bearer {token}
             │ Body: {service_type, priority, location, description}
             ↓
┌─────────────────────────────────────────────────────┐
│ 2. BUN GATEWAY                                      │
│    ├─ Check rate limit (Redis)                     │
│    ├─ Validate JWT                                 │
│    ├─ Extract user_id from token                   │
│    └─ Forward to backend with X-User-ID header     │
└────────────┬────────────────────────────────────────┘
             │ POST http://localhost:8000/api/v1/services
             │ Headers: X-User-ID: {user_id}
             ↓
┌─────────────────────────────────────────────────────┐
│ 3. FASTAPI BACKEND (services.py)                    │
│    ├─ Route handler: create_service()              │
│    ├─ Validate request (Pydantic schema)           │
│    ├─ Extract user from X-User-ID                  │
│    └─ Call business logic                          │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 4. BUSINESS LOGIC (services/service_management.py)  │
│    ├─ Priority = CRITICAL? → Auto-approve          │
│    ├─ Find nearby providers (PostGIS query)        │
│    ├─ Rank providers (matching algorithm)          │
│    └─ Prepare notification data                    │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 5. DATABASE (PostgreSQL)                            │
│    ├─ BEGIN TRANSACTION                            │
│    ├─ INSERT INTO service_requests                 │
│    ├─ INSERT INTO audit_log                        │
│    ├─ COMMIT                                        │
│    └─ RETURN service_id                            │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 6. CACHE INVALIDATION (Redis)                       │
│    ├─ DELETE api:cache:services:list:*             │
│    └─ DELETE api:cache:analytics:*                 │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 7. BACKGROUND JOBS (Celery)                         │
│    ├─ Queue: Send SMS to citizen                   │
│    ├─ Queue: Send email to citizen                 │
│    ├─ Queue: Notify nearby providers               │
│    └─ Queue: Update analytics                      │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 8. RESPONSE                                         │
│    Backend → Gateway → Frontend                     │
│    Status: 201 Created                              │
│    Body: {service_id, status, created_at, ...}     │
└─────────────────────────────────────────────────────┘

TOTAL TIME: ~150ms (p95)
├─ Gateway: 10ms
├─ Backend validation: 5ms
├─ Business logic: 30ms
├─ Database insert: 50ms
├─ Cache operations: 5ms
├─ Queue jobs: 10ms
└─ Response serialization: 10ms
```

---

## 12.2 Real-Time Update Flow

```
REAL-TIME STATUS UPDATES

Provider accepts request → Citizen sees update immediately

┌─────────────────────────────────────────────────────┐
│ 1. PROVIDER (Frontend)                              │
│    Clicks "Accept Request" button                   │
└────────────┬────────────────────────────────────────┘
             │ POST /api/v1/services/{id}/accept
             ↓
┌─────────────────────────────────────────────────────┐
│ 2. BACKEND                                          │
│    ├─ Update service status → ACCEPTED             │
│    ├─ Update provider_id, accepted_at              │
│    ├─ Save to database                             │
│    └─ Publish to Redis Pub/Sub                     │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 3. REDIS PUB/SUB                                    │
│    PUBLISH service:updates:{service_id}             │
│    Message: {status: "ACCEPTED", provider: {...}}  │
└────────────┬────────────────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────────────────┐
│ 4. CITIZEN (Frontend - Polling or WebSocket)        │
│    ├─ Option A: Long polling (every 10 seconds)    │
│    │   GET /api/v1/services/{id}                   │
│    │                                                │
│    ├─ Option B: WebSocket (future)                 │
│    │   WS connection receives push notification    │
│    │                                                │
│    └─ Update UI: "Provider XYZ accepted!"          │
└─────────────────────────────────────────────────────┘

ALSO:
├─ SMS sent to citizen (via Celery job)
└─ Email sent to citizen (via Celery job)
```

---

# 13. **API Design**

## 13.1 API Design Principles

```
REST API DESIGN:

1. Resource-Based URLs:
   ✓ Good: /api/v1/services
   ✓ Good: /api/v1/services/{id}
   ✗ Bad: /api/v1/getServices
   ✗ Bad: /api/v1/service_list

2. HTTP Methods:
   ├─ GET: Retrieve resources
   ├─ POST: Create resources
   ├─ PUT: Full update
   ├─ PATCH: Partial update
   └─ DELETE: Remove resources

3. Status Codes:
   ├─ 200: OK (success)
   ├─ 201: Created (POST success)
   ├─ 204: No Content (DELETE success)
   ├─ 400: Bad Request (validation error)
   ├─ 401: Unauthorized (no/invalid token)
   ├─ 403: Forbidden (valid token, insufficient permissions)
   ├─ 404: Not Found
   ├─ 429: Too Many Requests (rate limited)
   └─ 500: Internal Server Error

4. Response Format:
   {
     "status": "success" | "error",
     "data": {...} | null,
     "message": "Optional message",
     "errors": [...] | null
   }

5. Pagination:
   GET /api/v1/services?page=2&page_size=20
   Response includes:
   {
     "data": [...],
     "pagination": {
       "page": 2,
       "page_size": 20,
       "total_pages": 10,
       "total_count": 200
     }
   }

6. Filtering & Sorting:
   GET /api/v1/services?status=SUBMITTED&priority=CRITICAL&sort=-created_at
   ├─ status, priority: Filters
   └─ sort: "-" prefix = descending

7. Field Selection (Sparse Fieldsets):
   GET /api/v1/services?fields=service_id,status,created_at
   └─ Returns only specified fields (reduce payload)
```

---

## 13.2 API Examples

```
AUTHENTICATION:

POST /api/v1/auth/register
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "John Doe",
  "phone": "+919876543210",
  "role": "CITIZEN"
}
Response (201):
{
  "status": "success",
  "data": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "CITIZEN",
    "is_verified": false
  },
  "message": "Registration successful. Please verify your email."
}

---

POST /api/v1/auth/login
Request:
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
Response (200):
{
  "status": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "expires_in": 900,
    "user": {
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "email": "user@example.com",
      "full_name": "John Doe",
      "role": "CITIZEN"
    }
  }
}

---

SERVICE MANAGEMENT:

POST /api/v1/services
Headers:
  Authorization: Bearer {access_token}
Request:
{
  "service_type": "MEDICAL",
  "priority": "CRITICAL",
  "location": {
    "type": "Point",
    "coordinates": [78.4867, 17.3850]
  },
  "address": "123 Main St, Hyderabad",
  "description": "Elderly man, chest pain, difficulty breathing",
  "num_people_affected": 1,
  "privacy_level": "PUBLIC"
}
Response (201):
{
  "status": "success",
  "data": {
    "service_id": "REQ-2024-00001",
    "requestor_id": "550e8400-e29b-41d4-a716-446655440000",
    "service_type": "MEDICAL",
    "priority": "CRITICAL",
    "status": "SUBMITTED",
    "location": {
      "type": "Point",
      "coordinates": [78.4867, 17.3850]
    },
    "description": "Elderly man, chest pain, difficulty breathing",
    "created_at": "2026-05-24T10:30:00Z",
    "updated_at": "2026-05-24T10:30:00Z",
    "estimated_response_time": "2 hours"
  },
  "message": "Service request created successfully"
}

---

GET /api/v1/services?status=SUBMITTED&priority=CRITICAL&page=1&page_size=20
Response (200):
{
  "status": "success",
  "data": [
    {
      "service_id": "REQ-2024-00001",
      "service_type": "MEDICAL",
      "priority": "CRITICAL",
      "status": "SUBMITTED",
      "created_at": "2026-05-24T10:30:00Z",
      "location": {...},
      "distance_km": 2.5
    },
    ...
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total_pages": 5,
    "total_count": 87
  }
}
```

---

## 13.3 Error Handling

```
ERROR RESPONSE FORMAT:

Validation Error (400):
{
  "status": "error",
  "message": "Validation failed",
  "errors": [
    {
      "field": "location",
      "message": "Location coordinates are required"
    },
    {
      "field": "description",
      "message": "Description must be between 10 and 500 characters"
    }
  ]
}

Authentication Error (401):
{
  "status": "error",
  "message": "Authentication required",
  "errors": null
}

Authorization Error (403):
{
  "status": "error",
  "message": "Insufficient permissions. Only EVENT_MANAGER or higher can approve requests.",
  "errors": null
}

Not Found (404):
{
  "status": "error",
  "message": "Service request not found",
  "errors": null
}

Rate Limit (429):
{
  "status": "error",
  "message": "Rate limit exceeded. Please try again in 45 seconds.",
  "errors": null
}
Headers:
  Retry-After: 45
  X-RateLimit-Limit: 100
  X-RateLimit-Remaining: 0
  X-RateLimit-Reset: 1653456789
```

---

# 14. **Data Models**

## 14.1 Core Data Models

```python
# src/backend/app-python/dbmodels/user.py

from sqlalchemy import Column, String, Boolean, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
  
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), index=True)
    role = Column(
        Enum("CITIZEN", "VOLUNTEER", "ORGANIZER", "PROVIDER", "MANAGER",
             "EVENT_MANAGER", "EXECUTIVE", "DM_AUTHORITY", "AUDITOR", "ADMIN",
             name="user_roles"),
        nullable=False,
        default="CITIZEN"
    )
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
    # Relationships
    service_requests = relationship("ServiceRequest", back_populates="requestor")
```

```python
# src/backend/app-python/dbmodels/service.py

from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry
import uuid
from datetime import datetime
from app.core.database import Base

class ServiceRequest(Base):
    __tablename__ = "service_requests"
  
    service_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    requestor_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    service_type = Column(
        Enum("RESCUE", "MEDICAL", "FOOD", "SHELTER", "WATER", "OTHER", 
             name="service_types"),
        nullable=False
    )
    priority = Column(
        Enum("CRITICAL", "HIGH", "MEDIUM", "LOW", name="priority_levels"),
        nullable=False
    )
    status = Column(
        Enum("SUBMITTED", "APPROVED", "ACCEPTED", "IN_PROGRESS", 
             "COMPLETED", "VERIFIED", "REJECTED", "CANCELLED", "EXPIRED", "DISPUTED",
             name="service_statuses"),
        nullable=False,
        default="SUBMITTED"
    )
    location = Column(Geometry("POINT", srid=4326), nullable=False)  # PostGIS
    address = Column(Text)
    description = Column(Text, nullable=False)
    num_people_affected = Column(Integer, default=1)
    privacy_level = Column(
        Enum("PUBLIC", "PROTECTED", "PRIVATE", name="privacy_levels"),
        default="PROTECTED"
    )
    provider_id = Column(UUID(as_uuid=True), ForeignKey("organizations.org_id"))
    accepted_at = Column(DateTime)
    completed_at = Column(DateTime)
    verified_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  
    # Relationships
    requestor = relationship("User", back_populates="service_requests")
    provider = relationship("Organization", back_populates="services_handled")
  
    # Spatial index
    __table_args__ = (
        Index('idx_service_requests_location', location, postgresql_using='gist'),
        Index('idx_service_requests_status', status),
        Index('idx_service_requests_priority', priority),
    )
```

---

## 14.2 Pydantic Schemas

```python
# src/backend/app-python/schemas/service.py

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum

class ServiceType(str, Enum):
    RESCUE = "RESCUE"
    MEDICAL = "MEDICAL"
    FOOD = "FOOD"
    SHELTER = "SHELTER"
    WATER = "WATER"
    OTHER = "OTHER"

class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class Location(BaseModel):
    type: str = "Point"
    coordinates: list[float] = Field(..., min_items=2, max_items=2)
  
    @validator('coordinates')
    def validate_coordinates(cls, v):
        lon, lat = v
        if not (-180 <= lon <= 180):
            raise ValueError("Longitude must be between -180 and 180")
        if not (-90 <= lat <= 90):
            raise ValueError("Latitude must be between -90 and 90")
        return v

class ServiceCreate(BaseModel):
    service_type: ServiceType
    priority: Priority
    location: Location
    address: Optional[str] = None
    description: str = Field(..., min_length=10, max_length=500)
    num_people_affected: Optional[int] = Field(default=1, ge=1, le=1000)
    privacy_level: Optional[str] = "PROTECTED"

class ServiceResponse(BaseModel):
    service_id: str
    requestor_id: str
    service_type: ServiceType
    priority: Priority
    status: str
    location: Location
    address: Optional[str]
    description: str
    created_at: datetime
    updated_at: datetime
    estimated_response_time: Optional[str]
  
    class Config:
        from_attributes = True
```

---

# **PART 5: INFRASTRUCTURE (Continued)**

---

# 17. **Scalability Design**

## 17.1 Horizontal Scaling Strategy

```
SCALING PROGRESSION:

PHASE 1: Single Server (MVP)
├─ 1 server running all services
├─ Handles: 1,000 concurrent users
├─ Cost: $96/month
└─ When to scale: > 800 users sustained

PHASE 2: Small Cluster (Year 1)
├─ 2 web servers (Bun + FastAPI)
├─ 1 database server (PostgreSQL + Redis)
├─ 1 load balancer (NGINX)
├─ Handles: 5,000 concurrent users
├─ Cost: ~$400/month
└─ When to scale: > 4,000 users sustained

PHASE 3: Auto-Scaling (Year 2+)
├─ 2-10 web servers (auto-scale)
├─ Database cluster (primary + replicas)
├─ Redis cluster
├─ CDN (Cloudflare)
├─ Handles: 50,000+ concurrent users
├─ Cost: $1,000-5,000/month
└─ Scales automatically based on load
```

---

## 17.2 Database Scaling

```
DATABASE SCALING STRATEGY:

VERTICAL SCALING (First):
├─ Upgrade server: 8GB → 16GB → 32GB RAM
├─ Add more CPU cores
├─ Faster SSD storage
└─ Cost-effective until ~10M records

HORIZONTAL SCALING (Later):
├─ Read Replicas:
│   ├─ 1 Primary (writes)
│   ├─ 2-3 Replicas (reads)
│   └─ Load balancer: PgBouncer
├─ Sharding (if needed):
│   ├─ By geographic region
│   └─ By date (older data → separate DB)
└─ When: > 50M records or > 10,000 writes/sec

QUERY OPTIMIZATION:
├─ Indexes on all foreign keys
├─ Spatial indexes (GIST) for geospatial
├─ Partial indexes for common filters
├─ Query analysis with EXPLAIN ANALYZE
└─ Connection pooling (100-500 connections)
```

---

## 17.3 Caching at Scale

```
MULTI-LAYER CACHING:

LAYER 1: Browser Cache
├─ Static files (HTML, CSS, JS, images)
├─ Cache-Control: max-age=3600
└─ Handled by Bun Gateway

LAYER 2: CDN Cache (Cloudflare)
├─ Static files globally distributed
├─ Reduces origin server load by 80%
└─ Cost: Free tier sufficient for MVP

LAYER 3: Redis Cache
├─ API responses (60s TTL)
├─ Session data (7 days TTL)
├─ Rate limit counters (60s TTL)
└─ Can scale to Redis Cluster if needed

LAYER 4: Application Cache
├─ In-memory Python cache (lru_cache)
├─ For expensive computations
└─ Limited by server RAM
```

---

# 18. **Monitoring & Observability**

## 18.1 Monitoring Stack

```
METRICS (Prometheus):
├─ System metrics: CPU, RAM, Disk
├─ Application metrics:
│   ├─ Request count (by endpoint)
│   ├─ Response time (p50, p95, p99)
│   ├─ Error rate (5xx errors)
│   └─ Active users
├─ Database metrics:
│   ├─ Query time
│   ├─ Connection pool usage
│   └─ Table sizes
└─ Business metrics:
    ├─ Service requests created/hour
    ├─ Average response time
    └─ Fulfillment rate

LOGS (Loki):
├─ Application logs (FastAPI, Bun)
├─ Access logs (NGINX)
├─ Error logs
└─ Audit logs (user actions)

VISUALIZATION (Grafana):
├─ Real-time dashboards
├─ Alerting (Slack, Email)
└─ Custom queries

UPTIME MONITORING:
├─ UptimeRobot (external)
├─ Checks: Every 5 minutes
├─ Alert: If down > 2 minutes
└─ Status page: status.idrm.gov.in
```

---

## 18.2 Alerting Strategy

```
ALERT LEVELS:

CRITICAL (Immediate Action):
├─ System down (> 2 minutes)
├─ Error rate > 5%
├─ Database connection failures
├─ Disk space < 10%
└─ Notification: SMS + Slack + Email

HIGH (Action within 30 min):
├─ Response time > 2 seconds (p95)
├─ CPU > 80% for 5 minutes
├─ RAM > 90%
└─ Notification: Slack + Email

MEDIUM (Action within 4 hours):
├─ Error rate > 1%
├─ Slow queries (> 1 second)
├─ High request rate (potential DDoS)
└─ Notification: Email

LOW (Review next day):
├─ Cache hit rate < 70%
├─ Unusual traffic patterns
└─ Notification: Email digest
```

---

# **PART 6: INTEGRATION & FUTURE**

---

# 19. **Integration Points**

## 19.1 External Integrations

```
CURRENT INTEGRATIONS (MVP):

1. SMS Gateway (Twilio or SNS):
   ├─ Send SMS notifications
   ├─ Verification codes
   ├─ Status updates
   └─ API: REST

2. Email Service (SMTP or SendGrid):
   ├─ Welcome emails
   ├─ Password resets
   ├─ Reports
   └─ API: SMTP / REST

3. Google Maps API:
   ├─ Geocoding (address → coordinates)
   ├─ Reverse geocoding
   ├─ Directions
   └─ API: REST

4. Payment Gateway (Future):
   ├─ Razorpay or Paytm
   ├─ For donations, subscriptions
   └─ API: REST + Webhooks
```

---

## 19.2 Future Government Integrations

```
PLANNED INTEGRATIONS (Year 2+):

1. Aadhaar eKYC:
   ├─ User verification
   ├─ Reduce fraud
   └─ API: UIDAI API

2. DigiLocker:
   ├─ Document storage
   ├─ Verification certificates
   └─ API: REST

3. UMANG:
   ├─ Single sign-on
   ├─ Wider reach
   └─ API: OAuth 2.0

4. Weather Department:
   ├─ Early warnings
   ├─ Forecast data
   └─ API: REST

5. GIS/ISRO:
   ├─ Satellite imagery
   ├─ Risk maps
   └─ API: WMS/WFS
```

---

# 20. **Future Evolution**

## 20.1 Migration to Microservices

**When to Consider**:

```
TRIGGERS:
├─ Sustained > 5,000 concurrent users
├─ Team size > 10 developers
├─ Need independent scaling
├─ Different tech stacks needed
└─ Organizational boundaries

EXTRACTION ORDER:
1. Authentication Service (first)
2. Geospatial Service (second)
3. Service Management (third)
4. Analytics (fourth)
5. Notifications (fifth)

DETAILED GUIDE:
└─ See MIGRATION-TO-MICROSERVICES-v3.md (20-25 pages)
```

---

**END OF HIGH-LEVEL DESIGN v3.0**

**Total Pages**: ~70 pages
**Completeness**: Production-ready architecture
**Status**: ✅ Ready for implementation
