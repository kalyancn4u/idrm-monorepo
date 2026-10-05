> *Type: Document (specification) · Audience: Architects, developers · Status: Archived — v2 historical generation*

# IDRM MVP - High-Level Design (HLD)

<!-- IDRM-CLEANUP doc=v2-23-hld status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — HLD → `docs/mvp/20` + `30`
> Gen-2 HLD (detailed design). Current source of truth = [`../../../../docs/mvp/20-architecture-system.md`](../../../../docs/mvp/20-architecture-system.md)
> + [`../../../../docs/mvp/30-design-data-flow-and-modules.md`](../../../../docs/mvp/30-design-data-flow-and-modules.md);
> module detail → `docs/mvp/25`. MVP-aligned; microservices/scaling parts → FFP. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Integrated Disaster Response Management Platform

**Document Type**: High-Level Design  
**Version**: 2.0  
**Date**: May 10, 2026  
**Status**: Final  
**Classification**: Internal Use

---

## Document Control

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | Dec 2, 2024 | Technical Team | Initial design with Java GeoServer, Node.js |
| 2.0 | May 10, 2026 | Technical Team | **Updated for v2.0**: Bun (not Node.js), Python geospatial (not Java GeoServer), Miniconda (not venv) |

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture Overview](#2-system-architecture-overview)
3. [Technology Stack](#3-technology-stack)
4. [Component Design](#4-component-design)
5. [Data Architecture](#5-data-architecture)
6. [Security Architecture](#6-security-architecture)
7. [Deployment Architecture](#7-deployment-architecture)
8. [Integration Architecture](#8-integration-architecture)
9. [Scalability & Performance](#9-scalability--performance)
10. [High Availability & Disaster Recovery](#10-high-availability--disaster-recovery)

---

## 1. Executive Summary

### 1.1 Purpose

This High-Level Design (HLD) document describes **HOW** the IDRM platform is built from an architectural perspective. It defines the system components, their interactions, technology choices, and design decisions without diving into implementation code details.

### 1.2 Audience

This document is for:
- **Solution Architects**: Understand overall system design
- **Technical Leads**: Make implementation decisions
- **DevOps Engineers**: Plan infrastructure and deployment
- **Security Architects**: Review security design
- **Developers**: Understand component responsibilities before coding

### 1.3 Design Principles

The IDRM architecture follows these core principles:

1. **Microservices Architecture**: Independent, loosely-coupled services
2. **API-First Design**: All functionality exposed via RESTful APIs
3. **Stateless Services**: Enable horizontal scaling
4. **Event-Driven**: Real-time updates via WebSocket and pub/sub
5. **Security by Design**: Multi-layer security (defense in depth)
6. **Cloud-Native Patterns**: Container-based, orchestrated deployment
7. **Open Source First**: Prefer open-source technologies
8. **Performance Optimized**: Caching, indexing, and efficient queries

---

## 2. System Architecture Overview

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                             │
│  Web Clients (HTML/Tailwind, React SPA) | Mobile (React Native) │
└─────────────────────────────────────────────────────────────────┘
                               ↓ HTTPS
┌─────────────────────────────────────────────────────────────────┐
│                    EDGE LAYER (NGINX)                           │
│  Reverse Proxy | SSL Termination | WAF | Rate Limiting | Cache │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                  API GATEWAY LAYER (Bun)                        │
│   Request Routing | Authentication | WebSocket | Aggregation   │
└─────────────────────────────────────────────────────────────────┘
            ↓                  ↓                    ↓
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  SERVICE LAYER   │  │  SERVICE LAYER   │  │  SERVICE LAYER   │
│  (Python/FastAPI)│  │  (Python/FastAPI)│  │  (Python/FastAPI)│
│                  │  │                  │  │                  │
│ Auth Service     │  │ Service Mgmt     │  │ Geospatial       │
│ Port 8000        │  │ Port 8001        │  │ Port 8002        │
└──────────────────┘  └──────────────────┘  └──────────────────┘
            ↓                  ↓                    ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DATA ACCESS LAYER                             │
│              ORM (SQLAlchemy) + GeoAlchemy2                    │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                    DATA LAYER                                   │
│  PostgreSQL 16 + PostGIS 3.4  |  Redis 7.2 (Cache + Sessions) │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 High-Level Component Diagram

```
                    ┌─────────────────┐
                    │   Web Clients   │
                    │  (HTTP/HTTPS)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │     NGINX       │
                    │  (Reverse Proxy)│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼────────┐    │    ┌────────▼────────┐
     │   Bun Gateway   │    │    │   Geospatial    │
     │   (Port 3000)   │    │    │   Tiles/WMS     │
     └────────┬────────┘    │    └────────┬────────┘
              │             │              │
     ┌────────┴────────┐    │     ┌───────┴────────┐
     │     Redis       │    │     │   PostgreSQL   │
     │   (Sessions)    │    │     │   + PostGIS    │
     └─────────────────┘    │     └────────────────┘
              │             │
     ┌────────▼────────────────────────────┐
     │      Python Microservices           │
     │                                     │
     │  ┌──────────────────────────────┐  │
     │  │ Auth (8000)                  │  │
     │  │ - Registration, Login        │  │
     │  │ - JWT generation             │  │
     │  └──────────────────────────────┘  │
     │                                     │
     │  ┌──────────────────────────────┐  │
     │  │ Service Mgmt (8001)          │  │
     │  │ - CRUD operations            │  │
     │  │ - Provider matching          │  │
     │  │ - Status tracking            │  │
     │  └──────────────────────────────┘  │
     │                                     │
     │  ┌──────────────────────────────┐  │
     │  │ Geospatial (8002)            │  │
     │  │ - Tile generation            │  │
     │  │ - Spatial queries            │  │
     │  │ - GeoJSON serving            │  │
     │  └──────────────────────────────┘  │
     │                                     │
     │  ┌──────────────────────────────┐  │
     │  │ Analytics (8003)             │  │
     │  │ - Dashboard data             │  │
     │  │ - Report generation          │  │
     │  └──────────────────────────────┘  │
     │                                     │
     │  ┌──────────────────────────────┐  │
     │  │ Notifications (8004)         │  │
     │  │ - Email, SMS sending         │  │
     │  └──────────────────────────────┘  │
     └─────────────────────────────────────┘
```

### 2.3 Request Flow Example

**Scenario**: User creates a service request

```
1. User (Browser) → HTTPS POST to /api/services
   ↓
2. NGINX → SSL termination, rate limiting check
   ↓
3. NGINX → Forward to Bun API Gateway (port 3000)
   ↓
4. Bun Gateway → Validate JWT token (check Redis blacklist)
   ↓
5. Bun Gateway → Check RBAC permissions (Casbin)
   ↓
6. Bun Gateway → Forward to Service Mgmt Service (port 8001)
   ↓
7. Service Mgmt → Validate request schema (Pydantic)
   ↓
8. Service Mgmt → Insert into PostgreSQL (via SQLAlchemy)
   ↓
9. Service Mgmt → Trigger geospatial indexing
   ↓
10. Service Mgmt → Publish event to Redis (for notifications)
   ↓
11. Notifications Service → Send email/SMS
   ↓
12. Service Mgmt → Return response to Bun
   ↓
13. Bun → Return JSON response to client
   ↓
14. NGINX → Return to user browser
   ↓
15. WebSocket → Push real-time update to connected users
```

---

## 3. Technology Stack

### 3.1 Technology Selection Matrix

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Reverse Proxy** | NGINX | 1.24+ | SSL termination, load balancing, caching, WAF |
| **API Gateway** | Bun | 1.x | Fast JavaScript runtime, WebSocket, request routing |
| **Backend Language** | Python | 3.11 | Microservices, data processing, geospatial analysis |
| **Environment Mgmt** | Miniconda | Latest | Python environment isolation |
| **Backend Framework** | FastAPI | 0.104+ | Modern async Python web framework |
| **ORM** | SQLAlchemy | 2.0 | Database abstraction |
| **Spatial ORM** | GeoAlchemy2 | Latest | PostGIS integration |
| **Database** | PostgreSQL | 16 | Primary relational database |
| **Spatial Extension** | PostGIS | 3.4 | Geospatial data types and operations |
| **Cache/Session** | Redis | 7.2+ | In-memory caching, session storage |
| **Geospatial Server** | Python FastAPI | Custom | Tile generation, spatial queries |
| **Frontend (Primary)** | HTML/Tailwind | Pure | Lightweight web interface |
| **Frontend (Admin)** | React | 18.x | Rich admin dashboards |
| **Frontend (Mobile)** | React Native | 0.72+ | Cross-platform mobile app |
| **Map Library** | Leaflet | 1.9 | Interactive maps |
| **Containerization** | Docker | 24.x | Service isolation |
| **Orchestration** | Docker Compose | 2.x | Multi-container deployment |

### 3.2 Technology Rationale

#### 3.2.1 Bun vs Node.js (API Gateway)

**Selected**: **Bun 1.x**

**Rationale**:
- **Performance**: 3-4x faster than Node.js for API serving
- **Memory**: 30% less memory usage
- **Native TypeScript**: No transpilation needed
- **Built-in Features**: WebSocket, SQLite, testing built-in
- **Compatibility**: Drop-in replacement for Node.js APIs
- **Startup Time**: 4x faster cold start

**Comparison**:
```
Benchmark: 10,000 requests

Node.js 20:
- Requests/sec: 25,000
- Memory: 250MB
- Cold start: 800ms

Bun 1.x:
- Requests/sec: 90,000 (3.6x faster)
- Memory: 175MB (30% less)
- Cold start: 200ms (4x faster)
```

---

#### 3.2.2 Python FastAPI vs Node.js Express (Backend Services)

**Selected**: **Python 3.11 + FastAPI**

**Rationale**:
- **Geospatial Libraries**: Superior ecosystem (GDAL, Shapely, GeoPandas, Rasterio)
- **Data Processing**: pandas, numpy for analytics
- **Type Safety**: Native type hints + Pydantic validation
- **Performance**: Async support with uvicorn ASGI server
- **Documentation**: Auto-generated OpenAPI/Swagger docs
- **Scientific Computing**: Extensive libraries for future ML/AI

**Comparison**:
```
Geospatial Operations (1000 points):

Node.js + Turf.js:
- 1000 point-in-polygon checks: 450ms
- Limited spatial functions

Python + Shapely:
- 1000 point-in-polygon checks: 120ms (3.7x faster)
- 1000+ spatial functions available
```

---

#### 3.2.3 PostgreSQL + PostGIS vs MongoDB

**Selected**: **PostgreSQL 16 + PostGIS 3.4**

**Rationale**:
- **Spatial Performance**: 4-5x faster for spatial queries
- **Spatial Functions**: 1000+ functions vs 34 in MongoDB
- **ACID Compliance**: Strong transactional integrity
- **Spatial Indexing**: R-tree and GiST indexes
- **Data Integrity**: Foreign keys, constraints
- **Mature Ecosystem**: 30+ years of development

**Comparison**:
```
Query: Find services within 5km (10,000 records)

MongoDB (geospatial):
- Query time: 850ms
- Functions: 34 spatial operators

PostgreSQL + PostGIS:
- Query time: 180ms (4.7x faster)
- Functions: 1000+ spatial functions
- Spatial indexes: GIST, BRIN, SP-GIST
```

---

#### 3.2.4 Python Geospatial vs Java GeoServer

**Selected**: **Python FastAPI Custom Geospatial Service**

**Rationale**:
- **Language Consistency**: Same language as backend (Python)
- **Memory Footprint**: 500MB vs 1.5GB for GeoServer
- **Customization**: Direct control over tile rendering
- **Integration**: Native integration with PostgreSQL/PostGIS
- **Dependencies**: No Java runtime required
- **Performance**: Comparable for MVP scale

**Comparison**:
```
Resource Usage (Idle):

Java GeoServer:
- Memory: 1.5GB
- JVM overhead: 800MB
- Startup time: 45 seconds

Python Geospatial Service:
- Memory: 500MB
- No JVM overhead
- Startup time: 3 seconds
```

**Why Not GeoServer**:
- Requires Java runtime (adds complexity)
- Higher resource usage
- Overkill for MVP (most features unused)
- Can migrate to GeoServer later if needed

---

#### 3.2.5 Miniconda vs venv

**Selected**: **Miniconda**

**Rationale**:
- **Dependency Management**: Better handling of system libraries (GDAL, proj)
- **Binary Packages**: Pre-compiled geospatial libraries
- **Environment Isolation**: Complete isolation including system packages
- **Cross-Platform**: Consistent across dev/staging/prod
- **Reproducibility**: conda-lock for exact environment reproduction

---

### 3.3 Technology Dependencies

**Core Dependencies**:

**Bun API Gateway**:
```json
{
  "dependencies": {
    "hono": "^4.0.0",
    "ioredis": "^5.3.0",
    "jsonwebtoken": "^9.0.0",
    "bcrypt": "^5.1.0"
  }
}
```

**Python Services**:
```
# Core web framework
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0

# Database
sqlalchemy==2.0.23
geoalchemy2==0.14.2
alembic==1.12.1
psycopg2-binary==2.9.9

# Geospatial
gdal==3.7.0
shapely==2.0.2
geopandas==0.14.1
rasterio==1.3.9

# Data processing
pandas==2.1.3
numpy==1.26.2

# Caching
redis==5.0.1

# Authentication
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# Utilities
python-dotenv==1.0.0
```

---

## 4. Component Design

### 4.1 NGINX (Edge Layer)

**Purpose**: Reverse proxy, SSL termination, load balancing, security

**Responsibilities**:
- SSL/TLS termination (Let's Encrypt certificates)
- HTTP to HTTPS redirect
- Request routing to backend services
- Static file serving
- Rate limiting (100 req/min per user)
- Web Application Firewall (WAF)
- Response caching
- Compression (gzip)
- Load balancing (if multiple instances)

**Configuration Highlights**:
```nginx
# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

# Upstream services
upstream api_gateway {
    least_conn;
    server api-gateway:3000;
}

# SSL configuration
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers HIGH:!aNULL:!MD5;
ssl_prefer_server_ciphers on;

# Security headers
add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";
add_header X-XSS-Protection "1; mode=block";
```

**Performance**:
- Worker processes: auto (matches CPU cores)
- Worker connections: 4096
- Keepalive timeout: 65s
- Client max body size: 20MB

---

### 4.2 Bun API Gateway

**Purpose**: Single entry point for all client requests

**Port**: 3000

**Responsibilities**:
- Request routing to appropriate microservices
- JWT token validation
- RBAC authorization (Casbin)
- Request/response logging
- WebSocket connection management
- API rate limiting (additional layer)
- Request aggregation (GraphQL-style)
- Circuit breaker pattern

**Key Features**:

**Authentication Middleware**:
```typescript
async function authMiddleware(c: Context, next: Next) {
  const token = c.req.header('Authorization')?.replace('Bearer ', '');
  
  if (!token) {
    return c.json({ error: 'Unauthorized' }, 401);
  }
  
  // Check Redis blacklist
  const blacklisted = await redis.get(`blacklist:${token}`);
  if (blacklisted) {
    return c.json({ error: 'Token revoked' }, 401);
  }
  
  // Verify JWT
  const decoded = jwt.verify(token, JWT_SECRET);
  c.set('user', decoded);
  
  await next();
}
```

**WebSocket Support**:
- Real-time service status updates
- Live map marker updates
- Notification push
- Connection pooling

**Service Proxy**:
```typescript
// Route to appropriate service
app.post('/api/services', authMiddleware, rbacMiddleware, async (c) => {
  const body = await c.req.json();
  const response = await fetch('http://service-mgmt:8001/services', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  return c.json(await response.json());
});
```

---

### 4.3 Auth Service (Python/FastAPI)

**Purpose**: User authentication and authorization

**Port**: 8000

**Responsibilities**:
- User registration
- Login (JWT generation)
- Password reset
- Email verification
- Token refresh
- Token blacklisting (logout)
- User profile management
- Role assignment

**Key Endpoints**:
```python
POST /auth/register
POST /auth/login
POST /auth/logout
POST /auth/refresh
POST /auth/verify-email
POST /auth/forgot-password
POST /auth/reset-password
GET  /users/me
PUT  /users/me
```

**JWT Structure**:
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "SERVICE_PROVIDER",
  "org_id": "org-uuid",
  "exp": 1234567890,
  "iat": 1234567000
}
```

**Password Security**:
- Bcrypt hashing (cost factor 12)
- Minimum 8 characters
- Must include: uppercase, lowercase, number
- Password history (last 3 passwords blocked)

---

### 4.4 Service Management Service (Python/FastAPI)

**Purpose**: Core service request CRUD and lifecycle management

**Port**: 8001

**Responsibilities**:
- Service request creation
- CRUD operations on requests
- Status updates
- Provider matching algorithm
- Assignment logic
- Completion verification
- Service history

**Key Endpoints**:
```python
POST   /services
GET    /services
GET    /services/{id}
PUT    /services/{id}
DELETE /services/{id}
POST   /services/{id}/assign
PUT    /services/{id}/status
POST   /services/{id}/verify
GET    /services/nearby?lat=X&lng=Y&radius=R
```

**Provider Matching Algorithm**:
```python
def match_providers(request: ServiceRequest) -> List[Provider]:
    """
    Match providers based on:
    1. Distance (nearest first)
    2. Service type
    3. Availability
    4. Capacity
    5. Performance rating
    """
    radius = get_radius_by_priority(request.priority)
    # CRITICAL: 10km, HIGH: 25km, MEDIUM/LOW: 50km
    
    providers = db.query(Provider).filter(
        ST_DWithin(
            Provider.location,
            request.location,
            radius
        ),
        Provider.service_types.contains([request.service_type]),
        Provider.is_available == True,
        Provider.current_load < Provider.capacity
    ).order_by(
        ST_Distance(Provider.location, request.location),
        Provider.rating.desc(),
        Provider.current_load.asc()
    ).limit(20).all()
    
    return providers
```

---

### 4.5 Geospatial Service (Python/FastAPI)

**Purpose**: Map tile generation and spatial queries

**Port**: 8002

**Responsibilities**:
- Generate map tiles (PNG, 256x256)
- Serve GeoJSON features
- Perform spatial queries
- Clustering (K-means)
- Distance calculations
- Coverage area computations

**Key Endpoints**:
```python
GET  /tiles/{z}/{x}/{y}.png
GET  /geojson/services?bounds=...
GET  /spatial/nearby?lat=X&lng=Y&radius=R
POST /spatial/cluster
GET  /spatial/coverage/{provider_id}
```

**Tile Generation**:
```python
def generate_tile(z: int, x: int, y: int) -> bytes:
    """
    Generate map tile for zoom level z, tile coordinates x, y
    Returns PNG image bytes
    """
    # Check Redis cache first
    cache_key = f"tile:{z}:{x}:{y}"
    cached = redis.get(cache_key)
    if cached:
        return cached
    
    # Calculate tile bounds
    bounds = tile_bounds(z, x, y)
    
    # Query PostGIS for features in bounds
    services = db.query(ServiceRequest).filter(
        ST_Within(ServiceRequest.location, bounds)
    ).all()
    
    # Render tile with matplotlib/pillow
    img = render_tile(services, bounds)
    
    # Cache for 1 hour
    redis.setex(cache_key, 3600, img)
    
    return img
```

**Spatial Query Optimization**:
- Use PostGIS spatial indexes (GIST)
- Simplify geometries for performance
- Limit result set size
- Cache frequent queries

---

### 4.6 Analytics Service (Python/FastAPI)

**Purpose**: Dashboard data and reporting

**Port**: 8003

**Responsibilities**:
- Dashboard metrics aggregation
- Report generation
- KPI calculations
- Data export (CSV, PDF, Excel)
- Time-series analysis

**Key Endpoints**:
```python
GET  /analytics/dashboard
GET  /analytics/services
GET  /analytics/financial
GET  /analytics/geographic
POST /analytics/reports
GET  /analytics/export
```

**Dashboard Metrics**:
```python
def get_dashboard_metrics(user: User) -> DashboardMetrics:
    """
    Generate role-specific dashboard metrics
    """
    metrics = {}
    
    if user.role == 'DM_AUTHORITY':
        metrics = {
            'total_requests': count_by_status(),
            'critical_requests': count_critical(),
            'avg_response_time': calculate_avg_response_time(),
            'provider_performance': rank_providers(),
            'funds_donated': sum_donations(),
            'funds_allocated': sum_allocations(),
            'geographic_heatmap': generate_heatmap()
        }
    elif user.role == 'ORG_ADMIN':
        metrics = {
            'org_services': count_org_services(user.org_id),
            'avg_completion_time': calculate_org_completion_time(user.org_id),
            'team_performance': get_team_metrics(user.org_id),
            'funds_received': sum_org_allocations(user.org_id)
        }
    
    return metrics
```

---

### 4.7 Notifications Service (Python/FastAPI)

**Purpose**: Multi-channel notifications

**Port**: 8004

**Responsibilities**:
- Email sending (SMTP)
- SMS sending (via gateway)
- Notification templating
- Delivery tracking
- Retry logic for failures

**Key Endpoints**:
```python
POST /notifications/email
POST /notifications/sms
GET  /notifications/templates
POST /notifications/send
```

**Email Templates**:
- Service request created
- Request approved/rejected
- Provider assigned
- Status update
- Completion verification
- Donation receipt
- Fund allocation

**SMS Integration**:
```python
def send_sms(phone: str, message: str):
    """
    Send SMS via third-party gateway
    Only for CRITICAL priority events
    """
    if not is_critical_event(message):
        raise ValueError("SMS only for CRITICAL events")
    
    response = requests.post(
        SMS_GATEWAY_URL,
        json={
            'to': phone,
            'message': message[:160],  # SMS limit
            'from': 'IDRM'
        },
        headers={'Authorization': f'Bearer {SMS_API_KEY}'}
    )
    
    log_sms_sent(phone, message, response.status_code)
```

---

## 5. Data Architecture

### 5.1 Database Schema Overview

**9 Core Tables**:
1. **users** - User accounts
2. **organizations** - Service provider organizations
3. **service_requests** - Core service requests (MAIN TABLE)
4. **service_providers** - Provider details and capacity
5. **disaster_events** - Disaster event declarations
6. **donations** - Financial contributions
7. **fund_allocations** - Fund disbursements
8. **audit_logs** - Immutable action logs
9. **sessions** - Active user sessions (Redis + PostgreSQL)

### 5.2 Entity Relationship Diagram

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────┐
│    users     │────1:N──│ service_requests │──N:1────│ disaster_    │
│              │         │                  │         │ events       │
│ - user_id    │         │ - service_id     │         │              │
│ - email      │         │ - requestor_id   │         │ - event_id   │
│ - password   │         │ - service_type   │         │ - event_name │
│ - role       │         │ - priority       │         │ - event_type │
│ - org_id     │───┐     │ - location       │         │ - severity   │
└──────────────┘   │     │ - status         │         │ - area       │
                   │     │ - assigned_to    │         └──────────────┘
                   │     │ - disaster_id    │
                   │     └──────────────────┘
                   │              │
                   │              │ N:1
                   │              ▼
                   │     ┌──────────────────┐
                   └─────│ organizations    │
                    1:N  │                  │
                         │ - org_id         │
                         │ - name           │
                         │ - type           │
                         │ - location       │
                         │ - is_verified    │
                         └──────────────────┘
                                  │
                                  │ 1:N
                                  ▼
                         ┌──────────────────┐
                         │ service_providers│
                         │                  │
                         │ - provider_id    │
                         │ - user_id        │
                         │ - org_id         │
                         │ - service_types  │
                         │ - coverage_area  │
                         │ - capacity       │
                         │ - current_load   │
                         └──────────────────┘

┌──────────────┐         ┌──────────────────┐
│  donations   │──N:1────│ disaster_events  │
│              │         └──────────────────┘
│ - donation_id│
│ - donor_id   │
│ - amount     │
│ - purpose    │
│ - event_id   │
└──────────────┘

┌──────────────────┐
│ fund_allocations │
│                  │
│ - allocation_id  │
│ - service_id     │
│ - provider_id    │
│ - amount         │
└──────────────────┘

┌──────────────┐
│  audit_logs  │
│              │
│ - log_id     │
│ - user_id    │
│ - action     │
│ - entity_type│
│ - entity_id  │
│ - changes    │
│ - timestamp  │
└──────────────┘
```

### 5.3 Data Types

**Spatial Data Types** (PostGIS):
```sql
-- Point for service request locations
location GEOMETRY(Point, 4326)

-- Polygon for coverage areas
coverage_area GEOMETRY(Polygon, 4326)

-- Polygon for disaster-affected areas
affected_area GEOMETRY(Polygon, 4326)
```

**SRID 4326**: WGS 84 (latitude/longitude)

**Enum Types**:
```sql
CREATE TYPE service_type AS ENUM (
    'MEDICAL', 'FOOD', 'SHELTER', 'RESCUE',
    'SANITATION', 'COMMUNICATION', 'TRANSPORT',
    'PSYCHOSOCIAL', 'LEGAL', 'OTHER'
);

CREATE TYPE priority_level AS ENUM (
    'CRITICAL', 'HIGH', 'MEDIUM', 'LOW'
);

CREATE TYPE service_status AS ENUM (
    'SUBMITTED', 'UNDER_REVIEW', 'APPROVED', 'REJECTED',
    'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'VERIFIED',
    'CANCELLED', 'DISPUTED'
);

CREATE TYPE privacy_level AS ENUM (
    'PUBLIC', 'PROTECTED', 'PRIVATE'
);
```

### 5.4 Indexing Strategy

**Primary Indexes**:
```sql
-- B-tree indexes for equality searches
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_service_requests_priority ON service_requests(priority);

-- GiST indexes for spatial queries
CREATE INDEX idx_service_requests_location 
    ON service_requests USING GIST(location);

CREATE INDEX idx_organizations_location 
    ON organizations USING GIST(location);

CREATE INDEX idx_providers_coverage 
    ON service_providers USING GIST(coverage_area);

CREATE INDEX idx_events_area 
    ON disaster_events USING GIST(affected_area);

-- GIN indexes for array and JSONB
CREATE INDEX idx_providers_types 
    ON service_providers USING GIN(service_types);

CREATE INDEX idx_requests_metadata 
    ON service_requests USING GIN(metadata);

-- Composite indexes for common queries
CREATE INDEX idx_requests_status_priority 
    ON service_requests(status, priority);

CREATE INDEX idx_requests_event_status 
    ON service_requests(disaster_event_id, status);

-- Partial indexes for active records
CREATE INDEX idx_active_providers 
    ON service_providers(is_available) 
    WHERE is_available = TRUE;
```

### 5.5 Caching Strategy

**Redis Data Structures**:

```
1. Sessions (Hash)
   Key: session:{user_id}
   TTL: 7 days
   Data: { refresh_token, created_at, last_accessed }

2. JWT Blacklist (String)
   Key: blacklist:{token}
   TTL: 7 days (refresh token expiry)
   Data: "1" (just existence check)

3. User Profiles (Hash)
   Key: user:{user_id}
   TTL: 1 hour
   Data: { email, full_name, role, org_id }

4. Service Request List (List)
   Key: services:recent
   TTL: 5 minutes
   Data: [service_id_1, service_id_2, ...]

5. Map Tiles (String - binary)
   Key: tile:{z}:{x}:{y}
   TTL: 1 hour
   Data: PNG image bytes

6. Analytics Cache (Hash)
   Key: analytics:dashboard:{user_id}
   TTL: 15 minutes
   Data: { total_requests, avg_time, ... }

7. Rate Limiting (String)
   Key: ratelimit:{user_id}:{endpoint}
   TTL: 1 minute
   Data: request_count
```

**Cache Invalidation**:
- **Write-Through**: Update cache on database write
- **Time-Based**: TTL expiration
- **Event-Based**: Invalidate on specific events (e.g., status change)

---

## 6. Security Architecture

### 6.1 Authentication Flow

```
┌──────────┐                 ┌──────────┐                 ┌──────────┐
│  Client  │                 │   Bun    │                 │   Auth   │
│          │                 │ Gateway  │                 │ Service  │
└────┬─────┘                 └────┬─────┘                 └────┬─────┘
     │                            │                            │
     │ POST /auth/login           │                            │
     │ {email, password}          │                            │
     │───────────────────────────>│                            │
     │                            │ POST /auth/login           │
     │                            │───────────────────────────>│
     │                            │                            │
     │                            │                      ┌─────┴─────┐
     │                            │                      │ Validate  │
     │                            │                      │ Password  │
     │                            │                      └─────┬─────┘
     │                            │                            │
     │                            │                      ┌─────┴─────┐
     │                            │                      │ Generate  │
     │                            │                      │ JWT Tokens│
     │                            │                      └─────┬─────┘
     │                            │ {access, refresh}          │
     │                            │<───────────────────────────┤
     │                            │                            │
     │                      ┌─────┴─────┐                     │
     │                      │ Store     │                     │
     │                      │ Refresh   │                     │
     │                      │ in Redis  │                     │
     │                      └─────┬─────┘                     │
     │                            │                            │
     │ {access, refresh}          │                            │
     │<───────────────────────────┤                            │
     │                            │                            │
     │                            │                            │
     │ GET /api/services          │                            │
     │ Header: Bearer {access}    │                            │
     │───────────────────────────>│                            │
     │                            │                            │
     │                      ┌─────┴─────┐                     │
     │                      │ Verify    │                     │
     │                      │ JWT       │                     │
     │                      │ Signature │                     │
     │                      └─────┬─────┘                     │
     │                            │                            │
     │                      ┌─────┴─────┐                     │
     │                      │ Check     │                     │
     │                      │ Blacklist │                     │
     │                      │ in Redis  │                     │
     │                      └─────┬─────┘                     │
     │                            │                            │
     │                      ┌─────┴─────┐                     │
     │                      │ Check     │                     │
     │                      │ RBAC      │                     │
     │                      │ (Casbin)  │                     │
     │                      └─────┬─────┘                     │
     │                            │                            │
     │                            │ Forward to Service         │
     │                            │───────────────────────────>│
```

### 6.2 Authorization (RBAC with Casbin)

**Policy Model**:
```
[request_definition]
r = sub, obj, act

[policy_definition]
p = sub, obj, act

[role_definition]
g = _, _

[policy_effect]
e = some(where (p.eft == allow))

[matchers]
m = g(r.sub, p.sub) && r.obj == p.obj && r.act == p.act
```

**Example Policies**:
```
# Role hierarchy
g, alice, DM_AUTHORITY
g, bob, ORG_ADMIN
g, charlie, SERVICE_PROVIDER

# Permissions
p, DM_AUTHORITY, /services/*, GET
p, DM_AUTHORITY, /services/*, POST
p, DM_AUTHORITY, /services/*/approve, POST
p, ORG_ADMIN, /services/*, GET
p, ORG_ADMIN, /services/*/assign, POST
p, SERVICE_PROVIDER, /services/assigned, GET
p, SERVICE_PROVIDER, /services/*/status, PUT
```

### 6.3 Data Encryption

**In Transit**:
- TLS 1.3 (NGINX)
- Certificate: Let's Encrypt (auto-renewal)
- HSTS headers

**At Rest**:
- PostgreSQL: Transparent Data Encryption (TDE)
- PII fields: AES-256 encryption
- Password: Bcrypt (cost factor 12)
- API keys: Encrypted in database

### 6.4 Security Layers (Defense in Depth)

```
┌─────────────────────────────────────────────────┐
│ Layer 1: Network (UFW Firewall)                │
│ - Allow only ports 22, 80, 443                  │
│ - Block all other inbound traffic               │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 2: NGINX (WAF, Rate Limiting)            │
│ - Rate limiting: 100 req/min per IP             │
│ - ModSecurity WAF rules                         │
│ - Request size limits                           │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 3: API Gateway (Authentication)          │
│ - JWT validation                                │
│ - Token blacklist check                         │
│ - Session validation                            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 4: Services (Authorization)              │
│ - RBAC enforcement (Casbin)                     │
│ - Resource ownership validation                 │
│ - Input validation (Pydantic)                   │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│ Layer 5: Database (Access Control)             │
│ - Connection pooling (max 20)                   │
│ - Prepared statements (SQL injection)           │
│ - Row-level security (future)                   │
└─────────────────────────────────────────────────┘
```

---

## 7. Deployment Architecture

### 7.1 Development Environment (Native Ubuntu)

**Purpose**: Local development and testing

**Setup**:
- Native Ubuntu 22.04/24.04
- All services run directly on host
- Database: PostgreSQL (systemd service)
- Cache: Redis (systemd service)
- Services: Run via Miniconda environments
- Gateway: Bun process

**Advantages**:
- Fast startup (no container overhead)
- Easy debugging
- Low memory usage (350MB total)

**Diagram**:
```
┌────────────────────────────────────────┐
│      Ubuntu 22.04/24.04 Host           │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ NGINX (systemd)                  │ │
│  │ Port 80/443                      │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Bun API Gateway                  │ │
│  │ Port 3000                        │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Python Services (Miniconda)      │ │
│  │ - Auth (8000)                    │ │
│  │ - Service Mgmt (8001)            │ │
│  │ - Geospatial (8002)              │ │
│  │ - Analytics (8003)               │ │
│  │ - Notifications (8004)           │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ PostgreSQL 16 + PostGIS (systemd)│ │
│  │ Port 5432                        │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ Redis 7.2 (systemd)              │ │
│  │ Port 6379                        │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

---

### 7.2 Staging/Production Environment (Docker)

**Purpose**: Production-like environment with isolation

**Setup**:
- Docker Compose orchestration
- 9 containers total
- Separate networks for security
- Volume mounts for persistence

**Container Architecture**:
```
┌─────────────────────────────────────────────────────┐
│              Docker Host (Ubuntu)                   │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │           idrm-network (bridge)               │ │
│  │                                               │ │
│  │  ┌─────────────┐  ┌─────────────┐           │ │
│  │  │   NGINX     │  │ Bun Gateway │           │ │
│  │  │  (80/443)   │  │   (3000)    │           │ │
│  │  └─────────────┘  └─────────────┘           │ │
│  │         │                 │                   │ │
│  │         └────────┬────────┘                   │ │
│  │                  │                            │ │
│  │  ┌───────────────┴──────────────────────┐    │ │
│  │  │     Python Microservices             │    │ │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐       │    │ │
│  │  │  │Auth  │  │Svc   │  │Geo   │       │    │ │
│  │  │  │8000  │  │Mgmt  │  │8002  │       │    │ │
│  │  │  └──────┘  │8001  │  └──────┘       │    │ │
│  │  │            └──────┘                  │    │ │
│  │  │  ┌──────┐  ┌──────┐                 │    │ │
│  │  │  │Analyt│  │Notif │                 │    │ │
│  │  │  │8003  │  │8004  │                 │    │ │
│  │  │  └──────┘  └──────┘                 │    │ │
│  │  └─────────────────────────────────────┘    │ │
│  │                  │                           │ │
│  │         ┌────────┴────────┐                 │ │
│  │         │                 │                 │ │
│  │  ┌──────▼──────┐  ┌──────▼──────┐          │ │
│  │  │ PostgreSQL  │  │    Redis    │          │ │
│  │  │  + PostGIS  │  │   (Cache)   │          │ │
│  │  │   (5432)    │  │   (6379)    │          │ │
│  │  └─────────────┘  └─────────────┘          │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
│  Volumes:                                          │
│  - postgres-data                                   │
│  - redis-data                                      │
│  - nginx-ssl                                       │
│  - logs                                            │
└─────────────────────────────────────────────────────┘
```

**Docker Compose Services**:
```yaml
services:
  nginx:
    image: nginx:1.24-alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on: [api-gateway]
  
  api-gateway:
    build: ./api-gateway
    ports: ["3000:3000"]
    environment:
      - DATABASE_URL=...
      - REDIS_URL=...
      - JWT_SECRET=...
    depends_on: [postgres, redis]
  
  auth-service:
    build: ./services/auth
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
  
  service-mgmt:
    build: ./services/service_mgmt
    ports: ["8001:8000"]
    depends_on: [postgres, redis]
  
  geospatial:
    build: ./services/geospatial
    ports: ["8002:8000"]
    depends_on: [postgres, redis]
  
  analytics:
    build: ./services/analytics
    ports: ["8003:8000"]
    depends_on: [postgres, redis]
  
  notifications:
    build: ./services/notifications
    ports: ["8004:8000"]
    depends_on: [postgres, redis]
  
  postgres:
    image: postgis/postgis:16-3.4
    environment:
      - POSTGRES_DB=idrm_db
      - POSTGRES_USER=idrm_user
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    ports: ["5432:5432"]
  
  redis:
    image: redis:7.2-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    ports: ["6379:6379"]
```

---

### 7.3 Production Deployment Considerations

**Server Specifications**:
- CPU: 16+ cores
- RAM: 32+ GB
- Storage: 500+ GB SSD
- Network: 1+ Gbps
- OS: Ubuntu 22.04/24.04 LTS

**Security Hardening**:
- UFW firewall (only 22, 80, 443 open)
- Fail2Ban (brute force protection)
- Automatic security updates
- SSH key-only authentication
- Non-root user for services

**SSL/TLS**:
- Let's Encrypt certificates
- Automatic renewal (certbot)
- TLS 1.3 only
- HSTS headers

**Monitoring**:
- Prometheus (metrics collection)
- Grafana (visualization)
- Alertmanager (alerts)

**Logging**:
- Centralized logging (ELK stack or similar)
- Log rotation (logrotate)
- Retention: 90 days

---

## 8. Integration Architecture

### 8.1 Internal Service Communication

**Communication Pattern**: HTTP/REST

**Service Discovery**:
- Development: Hardcoded localhost:port
- Docker: Container name resolution via Docker DNS

**Request Flow**:
```
Bun Gateway (3000)
    ↓ HTTP POST
Auth Service (8000) → Returns JWT
    ↓ HTTP GET (with JWT)
Service Mgmt (8001) → Validates, processes
    ↓ HTTP GET
Geospatial (8002) → Spatial queries
    ↓ HTTP POST
Notifications (8004) → Sends email/SMS
```

### 8.2 External Integrations

**Email Provider**:
- SMTP (Gmail, SendGrid, AWS SES)
- Credentials in environment variables

**SMS Gateway**:
- Third-party API (Twilio, AWS SNS, local provider)
- Webhook for delivery status

**Payment Gateway** (Future):
- Razorpay / Stripe
- Webhook for payment confirmation

**Geocoding Service** (Optional):
- OpenStreetMap Nominatim
- Google Maps Geocoding API

---

## 9. Scalability & Performance

### 9.1 Horizontal Scaling

**Stateless Services** (can be scaled):
- Bun API Gateway
- All Python microservices (Auth, Service Mgmt, Geospatial, Analytics, Notifications)

**Scaling Strategy**:
```
# Development: 1 instance each
# Staging: 1 instance each
# Production: Multiple instances

Production Setup (example):
- NGINX: 2 instances (load balanced)
- Bun Gateway: 3 instances
- Auth Service: 2 instances
- Service Mgmt: 3 instances
- Geospatial: 2 instances
- Analytics: 2 instances
- Notifications: 2 instances
```

**Load Balancing**:
- NGINX upstream with least_conn algorithm
- Health checks every 30 seconds

### 9.2 Vertical Scaling

**Stateful Services** (cannot easily scale horizontally):
- PostgreSQL
- Redis

**Scaling Strategy**:
- PostgreSQL: Increase instance size, add read replicas
- Redis: Increase memory, Redis Cluster for horizontal scaling

### 9.3 Performance Optimizations

**Database**:
- Connection pooling (SQLAlchemy: pool_size=20)
- Query optimization (EXPLAIN ANALYZE)
- Materialized views for analytics
- Partial indexes for filtered queries

**Caching**:
- Redis for frequently accessed data
- Cache warming on deployment
- CDN for static assets

**API**:
- Response compression (gzip)
- Pagination (limit 100 per page)
- Field filtering (sparse fieldsets)
- ETag for cache validation

**Geospatial**:
- Spatial index optimization
- Geometry simplification
- Tile caching (1 hour TTL)

### 9.4 Performance Targets

| Metric | Target |
|--------|--------|
| API Response Time (p95) | < 300ms |
| Map Tile Serving | < 100ms |
| Spatial Queries (50km) | < 500ms |
| Dashboard Load | < 2s |
| WebSocket Latency | < 50ms |
| Database Query (p95) | < 100ms |

---

## 10. High Availability & Disaster Recovery

### 10.1 Availability Strategy

**Target**: 99.5% uptime (max 3.65 hours downtime/month)

**Redundancy**:
- Multiple service instances
- Database replication (future)
- Health checks and auto-restart

**Health Checks**:
```python
@app.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "redis": await check_redis(),
        "disk_space": check_disk_space()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return JSONResponse(
        content={"status": "healthy" if all_healthy else "unhealthy", "checks": checks},
        status_code=status_code
    )
```

### 10.2 Backup Strategy

**PostgreSQL**:
- Full backup: Daily (retained 30 days)
- Incremental backup: Hourly (retained 7 days)
- WAL archiving: Continuous
- Offsite backup: S3/Wasabi

**Redis**:
- RDB snapshots: Every 6 hours
- AOF (Append-Only File): Every 1 second
- Backup retention: 7 days

**Backup Script**:
```bash
#!/bin/bash
# Daily PostgreSQL backup

BACKUP_DIR="/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/idrm_backup_$DATE.sql.gz"

docker exec idrm-postgres pg_dump -U idrm_user idrm_db | gzip > $BACKUP_FILE

# Upload to S3 (optional)
# aws s3 cp $BACKUP_FILE s3://idrm-backups/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### 10.3 Disaster Recovery

**RTO (Recovery Time Objective)**: 4 hours  
**RPO (Recovery Point Objective)**: 1 hour

**Recovery Procedure**:
1. Provision new server (1 hour)
2. Restore PostgreSQL from latest backup (1 hour)
3. Restore Redis from RDB snapshot (15 minutes)
4. Deploy application services (30 minutes)
5. Verify data integrity (30 minutes)
6. Update DNS (15 minutes)
7. Resume operations (total: 3.5 hours)

---

## 11. Appendices

### 11.1 Technology Version Matrix

| Technology | Minimum Version | Recommended | Latest Tested |
|-----------|-----------------|-------------|---------------|
| Ubuntu | 22.04 LTS | 24.04 LTS | 24.04 LTS |
| NGINX | 1.24 | 1.26 | 1.26 |
| Bun | 1.0 | 1.1+ | 1.1.8 |
| Python | 3.11 | 3.11 | 3.11.9 |
| PostgreSQL | 16 | 16 | 16.3 |
| PostGIS | 3.4 | 3.4 | 3.4.2 |
| Redis | 7.2 | 7.2 | 7.2.5 |
| Docker | 24.0 | 26.0 | 26.1 |

### 11.2 Port Allocation

| Service | Port | Protocol | Access |
|---------|------|----------|--------|
| NGINX | 80 | HTTP | Public |
| NGINX | 443 | HTTPS | Public |
| Bun API Gateway | 3000 | HTTP | Internal |
| Auth Service | 8000 | HTTP | Internal |
| Service Mgmt | 8001 | HTTP | Internal |
| Geospatial | 8002 | HTTP | Internal |
| Analytics | 8003 | HTTP | Internal |
| Notifications | 8004 | HTTP | Internal |
| PostgreSQL | 5432 | PostgreSQL | Internal |
| Redis | 6379 | Redis | Internal |
| SSH | 22 | SSH | Admin only |

### 11.3 Environment Variables

**Required**:
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
POSTGRES_PASSWORD=<strong-password>

# Redis
REDIS_URL=redis://:<password>@host:6379
REDIS_PASSWORD=<strong-password>

# JWT
JWT_SECRET=<random-64-char-string>
JWT_REFRESH_SECRET=<random-64-char-string>

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=<email>
SMTP_PASSWORD=<app-password>

# SMS (optional)
SMS_GATEWAY_URL=<url>
SMS_API_KEY=<key>
```

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| Solution Architect | TBD | | |
| Technical Lead | TBD | | |
| DevOps Lead | TBD | | |
| Security Architect | TBD | | |

---

**END OF HIGH-LEVEL DESIGN**

**Document Version**: 2.0  
**Last Updated**: May 10, 2026  
**Status**: Final for MVP  
**Next Review**: Post-MVP Launch
