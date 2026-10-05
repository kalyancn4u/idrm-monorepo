> *Type: Document (specification) · Audience: Developers · Status: Archived — v3 historical generation*

# IDRM: Project Structure - Version 3

<!-- IDRM-CLEANUP doc=v3-90-structure status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — project structure → `docs/mvp/20`/`30`
> MVP layout = modular monolith (`router→schemas→service→repository→models` per module) →
> [`../../../../docs/mvp/20-architecture-system.md`](../../../../docs/mvp/20-architecture-system.md) +
> [`../../../../docs/mvp/30-design-data-flow-and-modules.md`](../../../../docs/mvp/30-design-data-flow-and-modules.md)
> + `instructions/domain.md` §2. Multi-service layout → FFP. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Complete Directory Tree & File Organization

**Document Version**: 3.0  
**Date**: May 24, 2026  
**Status**: ✅ Production-Ready  
**Architecture**: Modular Monolith with Bun API Gateway  
**Target Audience**: Developers, DevOps engineers, new team members

---

## 📚 **Table of Contents**

1. [Complete Project Tree](#1-complete-project-tree)
2. [Root Directory](#2-root-directory)
3. [Backend Structure](#3-backend-structure)
4. [Bun Gateway Structure](#4-bun-gateway-structure)
5. [Frontend Structure](#5-frontend-structure)
6. [Database Structure](#6-database-structure)
7. [Documentation Structure](#7-documentation-structure)
8. [Infrastructure Structure](#8-infrastructure-structure)
9. [Testing Structure](#9-testing-structure)
10. [Setup Instructions](#10-setup-instructions)

---

# 1. **Complete Project Tree**

## 1.1 High-Level Overview

```
idrm/
├── backend/                    # Python FastAPI backend (modular monolith)
├── bun-gateway/                # Bun API gateway (TypeScript)
├── frontend/                   # Static frontend (HTML/CSS/JS)
├── database/                   # Database schemas, migrations, seeds
├── docs/                       # User-facing documentation
├── instructions/               # AI/Claude reference documentation
├── notebooks/                  # Jupyter notebooks (analysis, prototypes)
├── scripts/                    # Utility scripts (backup, deployment)
├── tests/                      # Integration & E2E tests
├── .github/                    # GitHub Actions CI/CD
├── docker-compose.yml          # Local development setup
├── .gitignore                  # Git ignore rules
├── README.md                   # Project overview
└── LICENSE                     # License file
```

---

## 1.2 Complete Directory Tree

```
idrm/
│
├── backend/                                    # PYTHON FASTAPI BACKEND
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                            # FastAPI application entry point
│   │   │
│   │   ├── api/                               # API ROUTES (Modular!)
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                        # Shared dependencies (DB session, auth)
│   │   │   ├── v1/                            # API version 1
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py                    # Authentication endpoints
│   │   │   │   ├── services.py                # Service request endpoints
│   │   │   │   ├── users.py                   # User management endpoints
│   │   │   │   ├── organizations.py           # Organization endpoints
│   │   │   │   ├── geo.py                     # Geospatial endpoints
│   │   │   │   ├── analytics.py               # Analytics endpoints
│   │   │   │   └── admin.py                   # Admin endpoints
│   │   │   │
│   │   │   └── router.py                      # API router aggregator
│   │   │
│   │   ├── models/                            # SQLALCHEMY ORM MODELS
│   │   │   ├── __init__.py
│   │   │   ├── user.py                        # User model
│   │   │   ├── service.py                     # ServiceRequest model
│   │   │   ├── organization.py                # Organization model
│   │   │   ├── notification.py                # Notification model
│   │   │   └── audit.py                       # AuditLog model
│   │   │
│   │   ├── schemas/                           # PYDANTIC SCHEMAS
│   │   │   ├── __init__.py
│   │   │   ├── user.py                        # User request/response schemas
│   │   │   ├── service.py                     # Service schemas
│   │   │   ├── organization.py                # Organization schemas
│   │   │   ├── auth.py                        # Auth schemas (login, token)
│   │   │   └── common.py                      # Common schemas (pagination, etc.)
│   │   │
│   │   ├── crud/                              # DATABASE OPERATIONS
│   │   │   ├── __init__.py
│   │   │   ├── user.py                        # User CRUD operations
│   │   │   ├── service.py                     # Service CRUD operations
│   │   │   ├── organization.py                # Organization CRUD
│   │   │   └── base.py                        # Base CRUD class
│   │   │
│   │   ├── services/                          # BUSINESS LOGIC
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py                # Authentication logic
│   │   │   ├── service_matching.py            # Auto-matching algorithm
│   │   │   ├── geospatial.py                  # Geospatial calculations
│   │   │   ├── notifications.py               # Email/SMS sending
│   │   │   └── analytics.py                   # Analytics calculations
│   │   │
│   │   ├── core/                              # CORE UTILITIES
│   │   │   ├── __init__.py
│   │   │   ├── config.py                      # Configuration (from .env)
│   │   │   ├── security.py                    # JWT, password hashing
│   │   │   ├── database.py                    # DB connection, session
│   │   │   ├── redis.py                       # Redis client
│   │   │   ├── cache.py                       # Cache manager
│   │   │   └── exceptions.py                  # Custom exceptions
│   │   │
│   │   └── utils/                             # HELPER UTILITIES
│   │       ├── __init__.py
│   │       ├── email.py                       # Email utilities
│   │       ├── sms.py                         # SMS utilities
│   │       └── validators.py                  # Custom validators
│   │
│   ├── alembic/                               # DATABASE MIGRATIONS
│   │   ├── versions/                          # Migration files
│   │   │   ├── 001_initial_schema.py
│   │   │   ├── 002_add_geospatial.py
│   │   │   └── ...
│   │   ├── env.py                             # Alembic environment
│   │   └── alembic.ini                        # Alembic config
│   │
│   ├── tests/                                 # UNIT TESTS
│   │   ├── __init__.py
│   │   ├── conftest.py                        # Pytest fixtures
│   │   ├── test_api/
│   │   │   ├── test_auth.py
│   │   │   ├── test_services.py
│   │   │   └── ...
│   │   ├── test_services/
│   │   │   ├── test_service_matching.py
│   │   │   └── ...
│   │   └── test_crud/
│   │       └── ...
│   │
│   ├── requirements.txt                       # Python dependencies
│   ├── requirements-dev.txt                   # Dev dependencies
│   ├── pytest.ini                             # Pytest configuration
│   ├── .env.example                           # Environment variables template
│   ├── Dockerfile                             # Docker image for backend
│   └── main.py                                # CLI entry point
│
├── bun-gateway/                               # BUN API GATEWAY
│   ├── src/
│   │   ├── index.ts                           # Main server file
│   │   ├── middleware/
│   │   │   ├── cors.ts                        # CORS middleware
│   │   │   ├── rateLimit.ts                   # Rate limiting
│   │   │   ├── auth.ts                        # JWT validation
│   │   │   ├── security.ts                    # Security headers
│   │   │   └── logger.ts                      # Request logging
│   │   │
│   │   ├── routes/
│   │   │   ├── api.ts                         # API proxy routes
│   │   │   └── static.ts                      # Static file routes
│   │   │
│   │   ├── utils/
│   │   │   ├── redis.ts                       # Redis client
│   │   │   ├── jwt.ts                         # JWT utilities
│   │   │   └── config.ts                      # Configuration
│   │   │
│   │   └── types/
│   │       └── index.ts                       # TypeScript types
│   │
│   ├── public/                                # Static files served by gateway
│   │   └── (symlink to ../frontend/)
│   │
│   ├── tests/
│   │   ├── middleware.test.ts
│   │   └── routes.test.ts
│   │
│   ├── package.json                           # Node dependencies
│   ├── tsconfig.json                          # TypeScript config
│   ├── .env.example                           # Environment variables
│   ├── Dockerfile                             # Docker image
│   └── bun.lockb                              # Bun lock file
│
├── frontend/                                  # STATIC FRONTEND
│   ├── index.html                             # Landing page
│   │
│   ├── pages/                                 # HTML PAGES
│   │   ├── auth/
│   │   │   ├── login.html
│   │   │   ├── register.html
│   │   │   └── forgot-password.html
│   │   │
│   │   ├── app/                               # Authenticated pages
│   │   │   ├── dashboard.html                 # Main dashboard
│   │   │   ├── create-service.html            # Create request
│   │   │   ├── service-detail.html            # View details
│   │   │   ├── my-services.html               # User's requests
│   │   │   └── map.html                       # Full map view
│   │   │
│   │   ├── provider/
│   │   │   ├── provider-dashboard.html
│   │   │   ├── available-services.html
│   │   │   └── my-services.html
│   │   │
│   │   └── admin/
│   │       ├── admin-dashboard.html
│   │       ├── users.html
│   │       └── analytics.html
│   │
│   ├── assets/                                # STATIC ASSETS
│   │   ├── css/
│   │   │   ├── tailwind.min.css               # Tailwind CSS
│   │   │   └── custom.css                     # Custom styles
│   │   │
│   │   ├── js/
│   │   │   ├── app.js                         # Main app logic
│   │   │   ├── auth.js                        # Authentication
│   │   │   ├── services.js                    # Service operations
│   │   │   ├── map.js                         # Map handling (Leaflet)
│   │   │   ├── analytics.js                   # Charts (Chart.js)
│   │   │   ├── utils.js                       # Utilities
│   │   │   └── config.js                      # API endpoints config
│   │   │
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   ├── favicon.ico
│   │   │   └── icons/
│   │   │
│   │   └── fonts/
│   │       └── (if any custom fonts)
│   │
│   └── templates/                             # SERVER-RENDERED TEMPLATES
│       ├── email/                             # Email templates (Jinja2)
│       │   ├── welcome.html
│       │   ├── password-reset.html
│       │   ├── service-created.html
│       │   └── service-completed.html
│       │
│       └── pdf/                               # PDF templates
│           ├── service-receipt.html
│           └── monthly-report.html
│
├── database/                                  # DATABASE FILES
│   ├── schemas/                               # SQL SCHEMAS
│   │   ├── 01_users.sql                       # Users table
│   │   ├── 02_organizations.sql               # Organizations table
│   │   ├── 03_service_requests.sql            # Service requests table
│   │   ├── 04_notifications.sql               # Notifications table
│   │   ├── 05_audit_logs.sql                  # Audit logs table
│   │   ├── 06_indexes.sql                     # All indexes
│   │   └── 07_views.sql                       # Useful views
│   │
│   ├── seeds/                                 # MOCK/SEED DATA
│   │   ├── mock_data_unittest.sql             # For unit tests (10 users, 25 requests)
│   │   ├── mock_data_integration.sql          # For integration tests (100 users, 500 requests)
│   │   ├── mock_data_full.sql                 # Full dataset (1500 users, 8000 requests)
│   │   └── generators/                        # Python scripts to generate mock data
│   │       ├── generate_users.py
│   │       ├── generate_services.py
│   │       └── generate_disaster_scenarios.py
│   │
│   └── backups/                               # BACKUP SCRIPTS
│       ├── backup.sh                          # Backup script
│       ├── restore.sh                         # Restore script
│       └── README.md                          # Backup documentation
│
├── docs/                                      # USER DOCUMENTATION
│   ├── getting-started/
│   │   ├── README.md
│   │   ├── installation.md
│   │   └── first-steps.md
│   │
│   ├── user-guide/
│   │   ├── citizens.md
│   │   ├── providers.md
│   │   ├── coordinators.md
│   │   └── administrators.md
│   │
│   ├── api-reference/
│   │   ├── authentication.md
│   │   ├── services.md
│   │   ├── geospatial.md
│   │   └── analytics.md
│   │
│   └── deployment/
│       ├── development.md
│       ├── staging.md
│       └── production.md
│
├── instructions/                              # AI/CLAUDE REFERENCE
│   ├── architecture/
│   │   ├── IDRM-PRD-v3.md
│   │   ├── IDRM-HLD-v3.md
│   │   ├── IDRM-LLD-v3.md
│   │   └── PROJECT-STRUCTURE-v3.md            # This file!
│   │
│   ├── implementation/
│   │   ├── 40-DATA-FORMATS.md
│   │   ├── 41-CODE-STANDARDS.md
│   │   ├── 42-VERIFICATION-CHECKLISTS.md
│   │   └── ...
│   │
│   └── reference/
│       └── IDRM-V3-CLARIFICATIONS-AND-DECISIONS.md
│
├── notebooks/                                 # JUPYTER NOTEBOOKS
│   ├── exploration/
│   │   ├── 01-data-exploration.ipynb
│   │   ├── 02-geospatial-analysis.ipynb
│   │   └── 03-user-behavior-analysis.ipynb
│   │
│   ├── prototypes/
│   │   ├── matching-algorithm-prototype.ipynb
│   │   └── clustering-prototype.ipynb
│   │
│   ├── training/
│   │   ├── beginner-python-fastapi.ipynb
│   │   └── postgis-tutorial.ipynb
│   │
│   └── reports/
│       ├── monthly-metrics.ipynb
│       └── disaster-response-analysis.ipynb
│
├── scripts/                                   # UTILITY SCRIPTS
│   ├── backup.sh                              # Database backup
│   ├── restore.sh                             # Database restore
│   ├── deploy.sh                              # Deployment script
│   ├── load-test.sh                           # Load testing
│   └── setup-dev.sh                           # Dev environment setup
│
├── tests/                                     # INTEGRATION & E2E TESTS
│   ├── integration/
│   │   ├── test_auth_flow.py
│   │   ├── test_service_flow.py
│   │   └── test_provider_flow.py
│   │
│   ├── e2e/
│   │   ├── test_complete_journey.py
│   │   └── test_disaster_scenario.py
│   │
│   └── performance/
│       ├── locustfile.py                      # Locust load tests
│       └── ab-test.sh                         # Apache Bench tests
│
├── .github/                                   # GITHUB ACTIONS CI/CD
│   └── workflows/
│       ├── test.yml                           # Run tests on push
│       ├── deploy-staging.yml                 # Deploy to staging
│       └── deploy-production.yml              # Deploy to production
│
├── docker-compose.yml                         # Local development setup
├── docker-compose.prod.yml                    # Production setup
├── .env.example                               # Environment variables template
├── .gitignore                                 # Git ignore rules
├── .dockerignore                              # Docker ignore rules
├── README.md                                  # Project overview
├── CONTRIBUTING.md                            # Contribution guidelines
├── LICENSE                                    # License (MIT or GPL)
└── CHANGELOG.md                               # Version history
```

---

# 2. **Root Directory**

## 2.1 Root Files Explained

```
docker-compose.yml
├─ Purpose: Local development environment
├─ Services: postgres, redis, backend, bun-gateway
├─ Usage: docker-compose up -d
└─ Ports: 3000 (gateway), 8000 (backend), 5432 (postgres), 6379 (redis)

docker-compose.prod.yml
├─ Purpose: Production-like environment
├─ Differences: No hot-reload, optimized builds
└─ Usage: docker-compose -f docker-compose.prod.yml up -d

.env.example
├─ Purpose: Template for environment variables
├─ Copy to: .env (not committed to git)
└─ Contains: DB credentials, API keys, secrets

README.md
├─ Purpose: Project overview & quick start
├─ Sections: About, Setup, Usage, Contributing
└─ First file newcomers read

CONTRIBUTING.md
├─ Purpose: Contribution guidelines
├─ Sections: Code standards, PR process, testing
└─ Linked from README

LICENSE
├─ Purpose: Software license
├─ Type: MIT or GPL-3.0 (TBD by government)
└─ Protects contributors and users

CHANGELOG.md
├─ Purpose: Version history
├─ Format: Keep a Changelog standard
└─ Sections: v3.0.0, v2.0.0, etc.
```

---

# 3. **Backend Structure**

## 3.1 Backend App Structure

```
backend/app/

WHY THIS STRUCTURE:
└─ Modular Monolith: All in one codebase, but organized by feature
└─ Scalable: Can extract modules to microservices later
└─ Testable: Clear separation of concerns

LAYERS:

1. API Layer (app/api/v1/)
   ├─ Responsibilities: Request handling, validation
   ├─ Files: auth.py, services.py, users.py, etc.
   └─ Depends on: schemas, services

2. Schema Layer (app/schemas/)
   ├─ Responsibilities: Request/response validation
   ├─ Files: user.py, service.py, etc.
   └─ Technology: Pydantic

3. Service Layer (app/services/)
   ├─ Responsibilities: Business logic
   ├─ Files: auth_service.py, service_matching.py
   └─ Depends on: crud, models

4. CRUD Layer (app/crud/)
   ├─ Responsibilities: Database operations
   ├─ Files: user.py, service.py, etc.
   └─ Depends on: models

5. Model Layer (app/models/)
   ├─ Responsibilities: Database schema definition
   ├─ Files: user.py, service.py, etc.
   └─ Technology: SQLAlchemy

6. Core Layer (app/core/)
   ├─ Responsibilities: Shared utilities
   ├─ Files: config.py, security.py, database.py
   └─ No dependencies (foundation)
```

---

## 3.2 Key Backend Files

```python
# backend/app/main.py
"""
FastAPI application entry point.
Includes all routers, middleware, startup/shutdown events.
"""

from fastapi import FastAPI
from app.api.router import api_router
from app.core.config import settings

app = FastAPI(
    title="IDRM API",
    version="3.0.0",
    description="Integrated Disaster Response Management System",
)

# Include routers
app.include_router(api_router, prefix="/api")

# Startup event
@app.on_event("startup")
async def startup():
    # Initialize database connection pool
    # Warm cache
    pass

# Health check
@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

```python
# backend/app/api/router.py
"""
API router aggregator.
Combines all v1 routers.
"""

from fastapi import APIRouter
from app.api.v1 import auth, services, users, organizations, geo, analytics, admin

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(services.router, prefix="/v1/services", tags=["services"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(organizations.router, prefix="/v1/organizations", tags=["organizations"])
api_router.include_router(geo.router, prefix="/v1/geo", tags=["geospatial"])
api_router.include_router(analytics.router, prefix="/v1/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/v1/admin", tags=["admin"])
```

```python
# backend/app/core/config.py
"""
Configuration management.
Loads from environment variables.
"""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # App
    APP_NAME: str = "IDRM"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    # SMS
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_PHONE_NUMBER: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

# 4. **Bun Gateway Structure**

## 4.1 Bun Gateway Files

```typescript
// bun-gateway/src/index.ts
/**
 * Bun API Gateway main server.
 * Handles rate limiting, auth, security, static files.
 */

import { serve } from "bun";
import { corsMiddleware } from "./middleware/cors";
import { rateLimitMiddleware } from "./middleware/rateLimit";
import { authMiddleware } from "./middleware/auth";
import { securityHeadersMiddleware } from "./middleware/security";
import { loggerMiddleware } from "./middleware/logger";
import { apiProxy } from "./routes/api";
import { staticFiles } from "./routes/static";

serve({
  port: 3000,
  async fetch(req) {
    // Middleware chain
    await loggerMiddleware(req);
    
    const corsResponse = corsMiddleware(req);
    if (corsResponse) return corsResponse;
    
    const rateLimitResponse = await rateLimitMiddleware(req);
    if (rateLimitResponse) return rateLimitResponse;
    
    const authResponse = authMiddleware(req);
    if (authResponse) return authResponse;
    
    // Route requests
    const url = new URL(req.url);
    
    if (url.pathname.startsWith("/api/")) {
      return await apiProxy(req);
    }
    
    return await staticFiles(req);
  },
});

console.log("🚀 Bun API Gateway running on http://localhost:3000");
```

---

# 5. **Frontend Structure**

## 5.1 Frontend Organization

```
frontend/

PHILOSOPHY:
├─ Static files (HTML/CSS/JS)
├─ No build step (for simplicity)
├─ Progressive enhancement
└─ Works without JavaScript (basic functionality)

STRUCTURE:

pages/
├─ Organized by user flow
├─ auth/ → Authentication pages
├─ app/ → Authenticated citizen pages
├─ provider/ → Provider-specific pages
└─ admin/ → Admin-only pages

assets/css/
├─ tailwind.min.css → Framework
└─ custom.css → Project-specific styles

assets/js/
├─ app.js → Main application logic
├─ auth.js → Authentication handling
├─ services.js → Service request operations
├─ map.js → Leaflet map handling
├─ analytics.js → Chart.js visualizations
├─ utils.js → Helper functions
└─ config.js → API endpoints, constants

templates/
├─ Server-rendered with Jinja2 (Python)
├─ email/ → Email templates
└─ pdf/ → PDF templates (rendered with WeasyPrint)
```

---

# 6. **Database Structure**

## 6.1 Database Files Organization

```
database/

schemas/
├─ Purpose: SQL table definitions
├─ One file per table/group
├─ Numbered for execution order
└─ Can be run independently or via Alembic

seeds/
├─ Purpose: Test/demo data
├─ Three levels: unittest, integration, full
├─ generators/ → Python scripts to create data
└─ Can regenerate anytime

backups/
├─ Purpose: Backup & restore scripts
├─ backup.sh → Creates timestamped backups
├─ restore.sh → Restores from backup
└─ README.md → Documentation
```

---

## 6.2 Migration Strategy

```
DATABASE MIGRATIONS:

Development:
├─ Make model changes in app/models/
├─ Generate migration: alembic revision --autogenerate -m "description"
├─ Review migration file: alembic/versions/XXX_description.py
├─ Apply migration: alembic upgrade head
└─ Rollback if needed: alembic downgrade -1

Production:
├─ Test migration on staging first
├─ Backup database: ./scripts/backup.sh
├─ Apply migration: alembic upgrade head
├─ Verify: Check logs, test critical flows
└─ Rollback if issues: alembic downgrade -1
```

---

# 7. **Documentation Structure**

## 7.1 Two Documentation Sets

```
docs/ (USER-FACING)
├─ Audience: End users, developers using IDRM
├─ Style: Tutorial, step-by-step
├─ Format: Markdown, screenshots welcome
└─ Examples: "How to create a service request"

instructions/ (AI/CLAUDE REFERENCE)
├─ Audience: AI assistants, Claude Code, developers
├─ Style: Comprehensive specs, technical details
├─ Format: Structured markdown, code examples
└─ Examples: "Complete API contract for /api/v1/services"

WHY SEPARATE:
├─ Different audiences have different needs
├─ Users want simple guides
├─ AI needs complete specifications
└─ Prevents mixing concerns
```

---

# 8. **Infrastructure Structure**

## 8.1 Docker Setup

```
DOCKER FILES:

backend/Dockerfile
├─ Purpose: Python backend image
├─ Base: python:3.11-slim
├─ Includes: Requirements, app code
└─ Entrypoint: uvicorn app.main:app

bun-gateway/Dockerfile
├─ Purpose: Bun gateway image
├─ Base: oven/bun:1.1
├─ Includes: Dependencies, src code
└─ Entrypoint: bun run src/index.ts

docker-compose.yml (Development)
services:
  postgres:
    image: postgis/postgis:15-3.3
    ports: ["5432:5432"]
    volumes: ["./data/postgres:/var/lib/postgresql/data"]
  
  redis:
    image: redis:7.2-alpine
    ports: ["6379:6379"]
  
  backend:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [postgres, redis]
    volumes: ["./backend:/app"]  # Hot reload
    command: uvicorn app.main:app --reload --host 0.0.0.0
  
  bun-gateway:
    build: ./bun-gateway
    ports: ["3000:3000"]
    depends_on: [backend]
    volumes: ["./bun-gateway/src:/app/src", "./frontend:/app/public"]
    command: bun run --hot src/index.ts
```

---

# 9. **Testing Structure**

## 9.1 Test Organization

```
TESTING STRATEGY:

backend/tests/ (Unit Tests)
├─ Purpose: Test individual functions/classes
├─ Scope: Single file/module
├─ Speed: Fast (<1s per test)
├─ Coverage target: 80%
└─ Run: pytest backend/tests/

tests/integration/ (Integration Tests)
├─ Purpose: Test API endpoints end-to-end
├─ Scope: Multiple components together
├─ Speed: Medium (1-5s per test)
├─ Database: Uses test database
└─ Run: pytest tests/integration/

tests/e2e/ (End-to-End Tests)
├─ Purpose: Test complete user flows
├─ Scope: Frontend + Backend + Database
├─ Speed: Slow (10-30s per test)
├─ Browser: Selenium/Playwright (future)
└─ Run: pytest tests/e2e/

tests/performance/ (Load Tests)
├─ Purpose: Test under load
├─ Tools: Locust, Apache Bench
├─ Metrics: Requests/sec, response time
└─ Run: locust -f tests/performance/locustfile.py
```

---

# 10. **Setup Instructions**

## 10.1 First-Time Setup

```bash
# 1. Clone repository
git clone https://github.com/idrm-project/idrm.git
cd idrm

# 2. Copy environment file
cp .env.example .env
# Edit .env with your values

# 3. Start services with Docker
docker-compose up -d

# 4. Wait for services to be ready
docker-compose ps  # Check all services are "Up"

# 5. Run database migrations
docker-compose exec backend alembic upgrade head

# 6. Load mock data (optional)
docker-compose exec postgres psql -U postgres -d idrm < database/seeds/mock_data_unittest.sql

# 7. Access the application
# Frontend: http://localhost:3000
# Backend API Docs: http://localhost:8000/docs
# Backend Health: http://localhost:8000/health

# 8. Run tests
docker-compose exec backend pytest
```

---

## 10.2 Development Workflow

```bash
# Start development environment
docker-compose up -d

# View logs
docker-compose logs -f backend      # Backend logs
docker-compose logs -f bun-gateway  # Gateway logs

# Access database
docker-compose exec postgres psql -U postgres -d idrm

# Access Redis CLI
docker-compose exec redis redis-cli

# Run migrations
docker-compose exec backend alembic revision --autogenerate -m "description"
docker-compose exec backend alembic upgrade head

# Run tests
docker-compose exec backend pytest --cov=app --cov-report=html
# Coverage report at backend/htmlcov/index.html

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

---

## 10.3 File Naming Conventions

```
PYTHON FILES:
├─ snake_case for all files: user_service.py
├─ Test files: test_user_service.py
└─ Private modules: _internal.py

TYPESCRIPT FILES:
├─ camelCase for files: rateLimit.ts
├─ PascalCase for classes: UserService.ts
└─ Test files: rateLimit.test.ts

HTML/CSS/JS:
├─ kebab-case for files: login-page.html
├─ camelCase for JS functions: getUserData()
└─ PascalCase for classes: class ServiceManager {}

SQL FILES:
├─ Lowercase with underscores: 01_create_users.sql
├─ Numbered for order: 01, 02, 03
└─ Descriptive names

DIRECTORIES:
├─ Lowercase, underscores: api_gateway
├─ No spaces, no special chars
└─ Plural for collections: models/, schemas/
```

---

## 10.4 Adding New Features

```
WORKFLOW FOR NEW FEATURE:

Example: Add "Service Rating" feature

1. Create branch
   git checkout -b feature/service-rating

2. Database (if needed)
   ├─ Add model: backend/app/models/rating.py
   ├─ Create migration: alembic revision --autogenerate -m "add service rating"
   └─ Apply: alembic upgrade head

3. Backend
   ├─ Schema: backend/app/schemas/rating.py
   ├─ CRUD: backend/app/crud/rating.py
   ├─ API: backend/app/api/v1/services.py (add rating endpoints)
   └─ Tests: backend/tests/test_api/test_rating.py

4. Frontend
   ├─ Add to service detail page: frontend/pages/app/service-detail.html
   ├─ Add rating widget: frontend/assets/js/services.js
   └─ Styling: frontend/assets/css/custom.css

5. Documentation
   ├─ User guide: docs/user-guide/citizens.md (how to rate)
   └─ API reference: docs/api-reference/services.md (rating endpoints)

6. Test
   ├─ Unit tests: pytest backend/tests/
   ├─ Integration: pytest tests/integration/
   └─ Manual: http://localhost:3000

7. Commit & PR
   git add .
   git commit -m "feat: add service rating feature"
   git push origin feature/service-rating
   # Create PR on GitHub
```

---

**END OF PROJECT STRUCTURE DOCUMENTATION v3.0**

**Total Pages**: ~35 pages  
**Completeness**: Production-ready structure  
**Status**: ✅ Ready for development
