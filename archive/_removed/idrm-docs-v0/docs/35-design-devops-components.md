> *Type: Document (specification) · Audience: Developers, DevOps · Status: Archived — v0 historical generation*

---
title: "IDRM MVP - Components & Modules List"
date: 2024-12-22 16:00:00 +0530
categories: [Architecture, Reference]
tags: [components, modules, reference]
author: IDRM Architecture Team
toc: true
---

# IDRM MVP - Complete Components & Modules List

<!-- IDRM-CLEANUP doc=v0-35-devops-components status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — DevOps components list (mostly FFP infra)
> A components/modules inventory with a DevOps lens. **Application modules** overlap the ten monolith modules —
> see the elucidation in [`../../../../docs/mvp/25-module-elucidation.md`](../../../../docs/mvp/25-module-elucidation.md)
> and conformance in [`../../../../docs/mvp/26-conformance-pics.md`](../../../../docs/mvp/26-conformance-pics.md).
> **Infra/DevOps components** here (gateway, containers, brokers, CI/CD, observability, scaling) are **FFP** →
> `docs/ffp/20` + `docs/ffp/80` + the component map `guides/mvp/learn/tech-stack-101.md`. *Program:*
> `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## 1. Edge Layer Components

### 1.1 NGINX Reverse Proxy
- **Technology**: NGINX 1.24
- **Port**: 80 (HTTP), 443 (HTTPS)
- **Functions**:
  - SSL/TLS termination
  - Reverse proxy and load balancing
  - Web Application Firewall (WAF)
  - Static content serving
  - Response caching
  - Rate limiting
  - Gzip compression

---

## 2. API Gateway Layer Components

### 2.1 API Gateway Service
- **Technology**: Node.js 20 LTS + Express.js 4.x
- **Port**: 3000
- **Functions**:
  - Single entry point for all API requests
  - Request routing to microservices
  - JWT token validation
  - API versioning management
  - Request/response transformation
  - CORS handling
  - Rate limiting enforcement
  - Response aggregation
- **Key Dependencies**:
  - express
  - helmet (security headers)
  - express-rate-limit
  - http-proxy-middleware
  - morgan (logging)
  - cors

---

## 3. Microservices Layer Components

### 3.1 Authentication Service
- **Technology**: Node.js 20 LTS + Express.js
- **Port**: 3001
- **Functions**:
  - User registration
  - User login/logout
  - JWT token generation (RS256)
  - JWT token validation
  - Token refresh mechanism
  - Session management
  - Token blacklisting
  - Password hashing (bcrypt, 12 rounds)
  - OAuth2 integration support
- **Key Dependencies**:
  - express
  - passport + passport-jwt
  - jsonwebtoken
  - bcrypt
  - ioredis
  - pg (PostgreSQL client)
- **Data Access**: PostgreSQL (users table), Redis (sessions, blacklist)

### 3.2 Service Management Service
- **Technology**: Python 3.11 + FastAPI 0.104+
- **Port**: 8001
- **Functions**:
  - Service request CRUD operations
  - Service request lifecycle management
  - Provider matching algorithm
  - Task assignment logic
  - Status tracking and updates
  - Service search and filtering
  - Bulk operations
  - Service validation
- **Key Dependencies**:
  - fastapi
  - uvicorn
  - sqlalchemy
  - geoalchemy2
  - pydantic
  - celery (async tasks)
- **Data Access**: PostgreSQL (service_requests, organizations)

### 3.3 Geospatial Service
- **Technology**: Python 3.11 + FastAPI 0.104+
- **Port**: 8002
- **Functions**:
  - Proximity search (ST_DWithin queries)
  - Distance calculations
  - Clustering analysis (DBSCAN, K-Means)
  - Service area calculations
  - Point-in-polygon queries
  - Geocoding/reverse geocoding
  - Route optimization
  - Heat map data generation
  - GeoServer layer management
- **Key Dependencies**:
  - fastapi
  - sqlalchemy + geoalchemy2
  - shapely
  - scikit-learn (clustering)
  - httpx (GeoServer API calls)
- **Data Access**: PostgreSQL+PostGIS, GeoServer

### 3.4 Communication Service
- **Technology**: Node.js 20 LTS + Socket.io 4.x
- **Port**: 3002
- **Functions**:
  - WebSocket connection management
  - Real-time bidirectional communication
  - Room-based broadcasting
  - Event-driven notifications
  - Online presence tracking
  - Message queuing
  - Connection state management
  - Heartbeat/ping-pong
- **Key Dependencies**:
  - socket.io
  - socket.io-redis (horizontal scaling)
  - ioredis
  - jsonwebtoken (connection auth)
- **Data Access**: Redis (pub/sub, presence)

### 3.5 Analytics Service
- **Technology**: Python 3.11 + FastAPI 0.104+
- **Port**: 8003
- **Functions**:
  - Dashboard metrics calculation
  - Data aggregation and reporting
  - Trend analysis
  - Performance monitoring
  - Report generation (PDF, Excel)
  - Heat map generation
  - Timeline analysis
  - Provider performance statistics
  - Impact metrics calculation
- **Key Dependencies**:
  - fastapi
  - pandas (data analysis)
  - numpy
  - matplotlib (charts)
  - reportlab (PDF generation)
  - openpyxl (Excel generation)
- **Data Access**: PostgreSQL (read-optimized queries)

### 3.6 Financial Service
- **Technology**: Python 3.11 + FastAPI 0.104+
- **Port**: 8004
- **Functions**:
  - Donation tracking
  - Fund allocation management
  - Payment processing integration
  - Financial transparency reporting
  - Budget management
  - Expenditure tracking
  - Audit trail maintenance
  - Receipt generation
  - Donor management
- **Key Dependencies**:
  - fastapi
  - sqlalchemy
  - decimal (precise calculations)
  - reportlab (receipts)
- **Data Access**: PostgreSQL (donations, allocations, expenditures)

---

## 4. Data Layer Components

### 4.1 PostgreSQL Database
- **Technology**: PostgreSQL 16
- **Port**: 5432
- **Functions**:
  - Primary relational data storage
  - ACID transaction support
  - Table partitioning
  - Full-text search
  - JSON/JSONB support
- **Key Schemas**:
  - users
  - organizations
  - disaster_events
  - service_requests
  - donations
  - allocations
  - expenditures
  - audit_logs

### 4.2 PostGIS Extension
- **Technology**: PostGIS 3.4
- **Functions**:
  - Spatial data types (POINT, POLYGON, LINESTRING)
  - Spatial indexing (GiST, SP-GiST)
  - Spatial functions (1000+ operations)
  - Coordinate system transformations
  - Distance calculations
  - Geometric operations
  - Topological relationships

### 4.3 Redis Cache
- **Technology**: Redis 7.2
- **Port**: 6379
- **Functions**:
  - Session storage
  - JWT token blacklist
  - API response caching
  - Rate limiting counters
  - Pub/Sub messaging
  - Geospatial queries (GEOADD/GEORADIUS)
  - Lock management
- **Data Structures Used**:
  - Strings (simple cache)
  - Hashes (sessions)
  - Sets (blacklists)
  - Sorted Sets (rate limiting)
  - Geo (spatial data)

### 4.4 GeoServer
- **Technology**: GeoServer 2.24
- **Port**: 8080
- **Functions**:
  - OGC Web Map Service (WMS)
  - OGC Web Feature Service (WFS)
  - OGC Web Coverage Service (WCS)
  - Web Map Tile Service (WMTS)
  - Map tile rendering
  - SLD styling
  - Layer management
  - Spatial data publishing
- **Data Sources**: PostgreSQL+PostGIS

---

## 5. Message Queue Components

### 5.1 RabbitMQ Message Broker
- **Technology**: RabbitMQ 3.12
- **Port**: 5672 (AMQP), 15672 (Management UI)
- **Functions**:
  - Asynchronous message queuing
  - Task distribution
  - Event broadcasting
  - Dead letter handling
  - Message persistence
  - Exchange routing (direct, topic, fanout)
- **Exchanges**:
  - events (topic exchange)
  - tasks (direct exchange)

### 5.2 Celery Workers
- **Technology**: Python 3.11 + Celery 5.x
- **Functions**:
  - Background task processing
  - Scheduled tasks (cron-like)
  - Task retry logic
  - Email sending
  - Report generation
  - Data export
  - Notification dispatch
- **Task Queues**:
  - default (general tasks)
  - high_priority (urgent tasks)
  - low_priority (batch processing)

---

## 6. Frontend Components (Not in Scope for HLD but Listed)

### 6.1 Web Application
- **Technology**: React 18 + Leaflet 1.9
- **Functions**:
  - User interface
  - Interactive maps
  - Service request forms
  - Dashboard visualization
  - Real-time updates

### 6.2 Mobile Application
- **Technology**: React Native
- **Functions**:
  - Mobile-optimized UI
  - GPS integration
  - Push notifications
  - Offline capability

### 6.3 Admin Dashboard
- **Technology**: React 18
- **Functions**:
  - System administration
  - User management
  - Analytics dashboards
  - Report generation

---

## 7. Supporting Modules

### 7.1 Authentication Module
- **Components**:
  - JWT Generator
  - JWT Validator
  - Password Hasher
  - Session Manager
  - Token Blacklist Manager
  - OAuth2 Client

### 7.2 Authorization Module
- **Components**:
  - Permission Checker
  - Role Manager
  - RBAC Engine
  - Resource Owner Validator

### 7.3 Logging Module
- **Components**:
  - Structured Logger
  - Log Formatter
  - Log Aggregator
  - Error Reporter

### 7.4 Validation Module
- **Components**:
  - Schema Validator (Pydantic/Joi)
  - Input Sanitizer
  - Business Rules Validator
  - Constraint Checker

### 7.5 Caching Module
- **Components**:
  - Cache Manager
  - Cache Invalidator
  - Cache Warmer
  - TTL Manager

### 7.6 Event Module
- **Components**:
  - Event Publisher
  - Event Subscriber
  - Event Handler
  - Domain Event Bus

### 7.7 Notification Module
- **Components**:
  - Email Sender
  - SMS Sender
  - Push Notification Sender
  - WebSocket Broadcaster
  - Notification Template Engine

### 7.8 Audit Module
- **Components**:
  - Audit Logger
  - Change Tracker
  - Activity Monitor
  - Compliance Reporter

---

## 8. Data Access Modules

### 8.1 Repository Layer
- **Components**:
  - UserRepository
  - ServiceRequestRepository
  - OrganizationRepository
  - DisasterEventRepository
  - DonationRepository
  - AllocationRepository

### 8.2 ORM Layer
- **Components**:
  - SQLAlchemy Models (Python services)
  - Sequelize Models (Node.js services)
  - Query Builder
  - Migration Manager (Alembic)

---

## 9. Integration Modules

### 9.1 Payment Gateway Integration
- **Functions**:
  - Payment processing
  - Transaction verification
  - Refund handling
  - Webhook processing

### 9.2 Email Service Integration
- **Functions**:
  - Transactional emails
  - Bulk emails
  - Template rendering
  - Delivery tracking

### 9.3 SMS Gateway Integration
- **Functions**:
  - SMS sending
  - Delivery status tracking
  - Template management

### 9.4 GeoServer Integration
- **Functions**:
  - Layer publishing
  - Style management
  - WMS/WFS requests
  - Tile generation

---

## 10. Operational Modules

### 10.1 Health Check Module
- **Components**:
  - Database Health Checker
  - Redis Health Checker
  - External Service Health Checker
  - Disk Space Monitor
  - Memory Monitor

### 10.2 Monitoring Module
- **Components**:
  - Metrics Collector (Prometheus)
  - Performance Tracker
  - Resource Monitor
  - Alert Manager

### 10.3 Backup Module
- **Components**:
  - Database Backup Manager
  - Incremental Backup Handler
  - Backup Rotation Manager
  - Restore Manager

### 10.4 Security Module
- **Components**:
  - Rate Limiter
  - IP Whitelist Manager
  - CORS Manager
  - Security Header Injector
  - Input Sanitizer
  - SQL Injection Preventer
  - XSS Preventer

---

## 11. Utility Modules

### 11.1 Configuration Module
- **Components**:
  - Environment Variable Loader
  - Configuration Validator
  - Secret Manager
  - Feature Flag Manager

### 11.2 Error Handling Module
- **Components**:
  - Exception Handler
  - Error Formatter
  - Error Logger
  - Error Reporter (Sentry)

### 11.3 Date/Time Module
- **Components**:
  - Timezone Converter
  - Timestamp Generator
  - Date Formatter
  - TTL Calculator

### 11.4 File Handling Module
- **Components**:
  - File Uploader
  - File Validator
  - Image Processor
  - Document Generator

---

## Component Summary by Technology

### Node.js Components (3)
1. API Gateway (Port 3000)
2. Authentication Service (Port 3001)
3. Communication Service (Port 3002)

### Python Components (4)
1. Service Management Service (Port 8001)
2. Geospatial Service (Port 8002)
3. Analytics Service (Port 8003)
4. Financial Service (Port 8004)

### Data Storage Components (4)
1. PostgreSQL + PostGIS (Port 5432)
2. Redis (Port 6379)
3. GeoServer (Port 8080)
4. RabbitMQ (Port 5672)

### Infrastructure Components (2)
1. NGINX (Port 80/443)
2. Celery Workers (background)

### Total Core Components: 13

---

## Module Interaction Matrix

| Component | Calls → | Called by ← |
|-----------|---------|-------------|
| NGINX | API Gateway, GeoServer | Web/Mobile Clients |
| API Gateway | All Microservices | NGINX |
| Auth Service | PostgreSQL, Redis | API Gateway, All Services |
| Service Mgmt | PostgreSQL, RabbitMQ, Redis | API Gateway |
| Geospatial | PostgreSQL, GeoServer | API Gateway, Service Mgmt |
| Communication | Redis | API Gateway, All Services |
| Analytics | PostgreSQL, Redis | API Gateway |
| Financial | PostgreSQL | API Gateway |
| PostgreSQL | - | All Services, GeoServer |
| Redis | - | Auth, Cache, Communication |
| GeoServer | PostgreSQL | NGINX, Geospatial Service |
| RabbitMQ | - | Service Mgmt, Celery |
| Celery Workers | PostgreSQL, Redis, External APIs | RabbitMQ |

---

## Deployment View

```
┌─────────────────────────────────────────┐
│           Ubuntu Server                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Docker Network: idrm-network      │ │
│  │                                    │ │
│  │  [NGINX:80/443]                    │ │
│  │       ↓                            │ │
│  │  [Gateway:3000]                    │ │
│  │       ↓                            │ │
│  │  [Auth:3001] [Services:8001-8004]  │ │
│  │  [Comm:3002]                       │ │
│  │       ↓                            │ │
│  │  [PostgreSQL:5432] [Redis:6379]    │ │
│  │  [GeoServer:8080]  [RabbitMQ:5672] │ │
│  │  [Celery Workers]                  │ │
│  └────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

**Total Components**: 13 core + 40+ supporting modules
**Total Ports Used**: 9 (80, 443, 3000, 3001, 3002, 5432, 6379, 8080, 5672)
**Languages**: JavaScript (Node.js), Python
**Databases**: PostgreSQL, Redis
**Message Queue**: RabbitMQ
**Map Server**: GeoServer
**Web Server**: NGINX

---

**Document Version**: 1.0  
**Date**: December 22, 2024  
**Purpose**: Component Reference
