# IDRM v3 · Development Setup

<!-- IDRM-CLEANUP doc=v3-g11-dev status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — dev setup → current
> → [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md)
> + [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: Developers · Status: Archived — v3 historical generation*
*Consolidated from: 30-DEVELOPMENT-SETUP.md, setup-monolith-development-v3.md*

## Contents
- [IDRM: Development Setup Guide](#idrm-development-setup-guide)
- [IDRM Monolith Development Setup v3.0](#idrm-monolith-development-setup-v30)

---

## IDRM: Development Setup Guide

### Complete Local Environment Setup

**Version**: 3.0 Consolidated  
**Audience**: Developers setting up local development environment  
**Reading Time**: 45 minutes  
**Setup Time**: 2-3 hours  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [Overview](#1-overview)
2. [Prerequisites Verification](#2-prerequisites-verification)
3. [Project Setup](#3-project-setup)
4. [Database Initialization](#4-database-initialization)
5. [Service Configuration](#5-service-configuration)
6. [Running Services](#6-running-services)
7. [Testing & Verification](#7-testing--verification)
8. [Development Workflow](#8-development-workflow)
9. [Troubleshooting](#9-troubleshooting)

---

### 1. **Overview**

#### 1.1 What You'll Build

A complete local development environment with:
- ✅ All 8 Python microservices running
- ✅ PostgreSQL + PostGIS database
- ✅ Redis cache
- ✅ Bun API Gateway
- ✅ NGINX reverse proxy
- ✅ Sample data loaded

#### 1.2 Architecture Reminder

```
NGINX (80) → Bun Gateway (3000) → Python Services (8001-8008)
                                        ↓
                            PostgreSQL (5432) + Redis (6379)
```

#### 1.3 Time Estimate

- **Prerequisites installed**: 1-2 hours (if following 01-PREREQUISITES.md)
- **Project setup**: 30 minutes
- **Database initialization**: 15 minutes
- **Service configuration**: 30 minutes
- **First successful run**: 15 minutes
- **Total**: 2-3 hours

---

### 2. **Prerequisites Verification**

#### 2.1 Check All Prerequisites

Run this verification script:

```bash
#!/bin/bash
## verify-prerequisites.sh

echo "=== IDRM Prerequisites Verification ==="
echo ""

## Check Bun
echo "Checking Bun..."
if command -v bun &> /dev/null; then
    echo "✅ Bun installed: $(bun --version)"
else
    echo "❌ Bun NOT installed"
    exit 1
fi

## Check Miniconda
echo "Checking Miniconda..."
if command -v conda &> /dev/null; then
    echo "✅ Conda installed: $(conda --version)"
else
    echo "❌ Conda NOT installed"
    exit 1
fi

## Check Python 3.11
echo "Checking Python 3.11..."
conda activate base
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
if [[ $PYTHON_VERSION == 3.11* ]]; then
    echo "✅ Python 3.11 available"
else
    echo "⚠️  Python version: $PYTHON_VERSION (need 3.11)"
fi

## Check PostgreSQL
echo "Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    PG_VERSION=$(psql --version | awk '{print $3}')
    echo "✅ PostgreSQL installed: $PG_VERSION"
else
    echo "❌ PostgreSQL NOT installed"
    exit 1
fi

## Check PostGIS
echo "Checking PostGIS..."
POSTGIS_CHECK=$(psql -U postgres -c "SELECT PostGIS_Version();" 2>&1)
if [[ $POSTGIS_CHECK == *"3.4"* ]]; then
    echo "✅ PostGIS 3.4 installed"
else
    echo "⚠️  PostGIS version check: $POSTGIS_CHECK"
fi

## Check Redis
echo "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo "✅ Redis installed: $(redis-cli --version)"
else
    echo "❌ Redis NOT installed"
    exit 1
fi

## Check NGINX
echo "Checking NGINX..."
if command -v nginx &> /dev/null; then
    echo "✅ NGINX installed: $(nginx -v 2>&1)"
else
    echo "❌ NGINX NOT installed"
    exit 1
fi

echo ""
echo "=== Verification Complete ==="
```

**Save as `verify-prerequisites.sh`, make executable, and run:**

```bash
chmod +x verify-prerequisites.sh
./verify-prerequisites.sh
```

**Expected Output**: All ✅ marks

---

### 3. **Project Setup**

#### 3.1 Clone Repository

```bash
## Create project directory
mkdir -p ~/projects/idrm
cd ~/projects/idrm

## Initialize git (if using version control)
git init
git remote add origin <your-repo-url>
git pull origin main
```

#### 3.2 Directory Structure

Create this structure:

```bash
idrm/
├── api-gateway/           # Bun API Gateway
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├── services/              # Python microservices
│   ├── auth/
│   ├── service-mgmt/
│   ├── provider-mgmt/
│   ├── geospatial/
│   ├── notifications/
│   ├── search/
│   ├── admin/
│   └── chatbot/
├── frontend/              # Static files
│   ├── index.html
│   ├── login.html
│   └── assets/
├── config/                # Configuration files
│   ├── nginx.conf
│   └── env/
├── scripts/               # Setup scripts
│   ├── init-db.sh
│   └── load-sample-data.sh
├── docs/                  # Documentation
└── tests/                 # Test files
```

**Create structure:**

```bash
mkdir -p api-gateway/src
mkdir -p services/{auth,service-mgmt,provider-mgmt,geospatial,notifications,search,admin,chatbot}
mkdir -p frontend/assets
mkdir -p config/env
mkdir -p scripts
mkdir -p docs
mkdir -p tests
```

---

### 4. **Database Initialization**

#### 4.1 Create Database

```bash
## Start PostgreSQL (if not running)
sudo systemctl start postgresql

## Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE idrm_db;
CREATE USER idrm_user WITH PASSWORD 'secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;
\c idrm_db
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
\q
EOF
```

#### 4.2 Create Schema

Create `scripts/init-db.sql`:

```sql
-- Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(15),
    role VARCHAR(50) NOT NULL DEFAULT 'CITIZEN',
    organization_id UUID,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create service_requests table
CREATE TABLE service_requests (
    id SERIAL PRIMARY KEY,
    requester_id UUID NOT NULL REFERENCES users(id),
    service_type VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    location GEOMETRY(Point, 4326) NOT NULL,
    address VARCHAR(500),
    urgency VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',
    privacy_level VARCHAR(20) NOT NULL DEFAULT 'PROTECTED',
    assigned_provider_id UUID,
    disaster_event_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create spatial index
CREATE INDEX idx_service_location ON service_requests USING GIST(location);

-- Create service_providers table
CREATE TABLE service_providers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_name VARCHAR(255) NOT NULL,
    organization_type VARCHAR(50) NOT NULL,
    registration_number VARCHAR(100) UNIQUE,
    service_types TEXT[] NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(15) NOT NULL,
    location GEOMETRY(Point, 4326),
    service_area GEOMETRY(Polygon, 4326),
    max_capacity INTEGER DEFAULT 10,
    current_load INTEGER DEFAULT 0,
    rating DECIMAL(3,2) DEFAULT 0.00,
    is_verified BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create disaster_events table
CREATE TABLE disaster_events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    area GEOMETRY(Polygon, 4326) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- (Add remaining tables from 22-DATABASE-DESIGN.md)
```

**Run schema creation:**

```bash
psql -U idrm_user -d idrm_db -f scripts/init-db.sql
```

#### 4.3 Load Sample Data

Create `scripts/load-sample-data.sql`:

```sql
-- Insert admin user
INSERT INTO users (email, hashed_password, full_name, role, is_verified)
VALUES (
    'admin@idrm.gov.in',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztpql.Y5mA5S',  -- password: Admin123!
    'System Administrator',
    'SYSTEM_ADMIN',
    TRUE
);

-- Insert sample disaster event
INSERT INTO disaster_events (event_name, event_type, severity, area, start_date, created_by)
VALUES (
    'Chennai Floods 2026',
    'FLOOD',
    'SEVERE',
    ST_GeomFromText('POLYGON((80.1 13.0, 80.3 13.0, 80.3 13.2, 80.1 13.2, 80.1 13.0))', 4326),
    '2026-05-01',
    (SELECT id FROM users WHERE role = 'SYSTEM_ADMIN' LIMIT 1)
);

-- Insert sample service provider
INSERT INTO service_providers (
    organization_name, organization_type, service_types, 
    contact_email, contact_phone, location, max_capacity
)
VALUES (
    'City Hospital',
    'GOVERNMENT',
    ARRAY['MEDICAL', 'RESCUE'],
    'admin@cityhospital.gov.in',
    '9876543210',
    ST_SetSRID(ST_MakePoint(80.2707, 13.0827), 4326),
    50
);

-- Insert sample service requests
INSERT INTO service_requests (
    requester_id, service_type, description, location, urgency, status
)
SELECT 
    (SELECT id FROM users WHERE role = 'SYSTEM_ADMIN' LIMIT 1),
    'MEDICAL',
    'Need first aid kit',
    ST_SetSRID(ST_MakePoint(80.27 + (random() * 0.1 - 0.05), 13.08 + (random() * 0.1 - 0.05)), 4326),
    CASE WHEN random() < 0.3 THEN 'CRITICAL' WHEN random() < 0.6 THEN 'HIGH' ELSE 'MEDIUM' END,
    'APPROVED'
FROM generate_series(1, 20);
```

**Load sample data:**

```bash
psql -U idrm_user -d idrm_db -f scripts/load-sample-data.sql
```

---

### 5. **Service Configuration**

#### 5.1 Create Conda Environment

```bash
## Create environment with Python 3.11
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

## Install geospatial dependencies
conda install -c conda-forge geopandas gdal fiona pyproj shapely -y

## Install other dependencies
pip install --break-system-packages \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    sqlalchemy==2.0.23 \
    geoalchemy2==0.14.2 \
    psycopg2-binary==2.9.9 \
    asyncpg==0.29.0 \
    python-jose==3.3.0 \
    passlib==1.7.4 \
    bcrypt==4.1.1 \
    redis==5.0.1 \
    pydantic==2.5.0 \
    httpx==0.25.2 \
    python-multipart==0.0.6
```

#### 5.2 Environment Variables

Create `config/env/.env.development`:

```bash
## Database
DATABASE_URL=postgresql://idrm_user:secure_password_here@localhost:5432/idrm_db

## Redis
REDIS_URL=redis://localhost:6379/0

## JWT
JWT_SECRET_KEY=your-secret-key-change-in-production-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

## Services
AUTH_SERVICE_URL=http://localhost:8001
SERVICE_MGMT_URL=http://localhost:8002
PROVIDER_MGMT_URL=http://localhost:8003
GEOSPATIAL_URL=http://localhost:8004
NOTIFICATIONS_URL=http://localhost:8005
SEARCH_URL=http://localhost:8006
ADMIN_URL=http://localhost:8007
CHATBOT_URL=http://localhost:8008

## Email (for notifications)
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@idrm.gov.in

## Environment
ENVIRONMENT=development
DEBUG=true
```

#### 5.3 Service-Specific Config

Each service needs a `config.py`. Example for Auth Service:

```python
## services/auth/config.py
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL")
    
    # JWT
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    # Service
    service_name: str = "auth-service"
    service_port: int = 8001
    
    class Config:
        env_file = "../../config/env/.env.development"

settings = Settings()
```

---

### 6. **Running Services**

#### 6.1 Start Infrastructure

**Terminal 1 - Start PostgreSQL:**
```bash
sudo systemctl start postgresql
```

**Terminal 2 - Start Redis:**
```bash
redis-server
## Or: sudo systemctl start redis-server
```

#### 6.2 Start Python Services

**Create a startup script `scripts/start-all-services.sh`:**

```bash
#!/bin/bash

## Activate conda environment
eval "$(conda shell.bash hook)"
conda activate idrm-mvp

## Load environment variables
export $(cat config/env/.env.development | xargs)

## Start services in background
echo "Starting Auth Service (8001)..."
cd services/auth && uvicorn main:app --port 8001 --reload &

echo "Starting Service Management (8002)..."
cd ../service-mgmt && uvicorn main:app --port 8002 --reload &

echo "Starting Provider Management (8003)..."
cd ../provider-mgmt && uvicorn main:app --port 8003 --reload &

echo "Starting Geospatial Service (8004)..."
cd ../geospatial && uvicorn main:app --port 8004 --reload &

echo "Starting Notifications (8005)..."
cd ../notifications && uvicorn main:app --port 8005 --reload &

echo "Starting Search (8006)..."
cd ../search && uvicorn main:app --port 8006 --reload &

echo "Starting Admin (8007)..."
cd ../admin && uvicorn main:app --port 8007 --reload &

echo "Starting Chatbot (8008)..."
cd ../chatbot && uvicorn main:app --port 8008 --reload &

cd ../..
echo "All services started!"
echo "Check logs: tail -f services/*/logs/*.log"
```

**Run:**
```bash
chmod +x scripts/start-all-services.sh
./scripts/start-all-services.sh
```

**OR start manually in separate terminals:**

```bash
## Terminal 3
cd services/auth
conda activate idrm-mvp
uvicorn main:app --port 8001 --reload

## Terminal 4
cd services/service-mgmt
conda activate idrm-mvp
uvicorn main:app --port 8002 --reload

## (Repeat for services 8003-8008)
```

#### 6.3 Start Bun API Gateway

**Terminal 11:**
```bash
cd api-gateway
bun install
bun run dev
## Runs on port 3000
```

#### 6.4 Start NGINX

**Terminal 12:**
```bash
sudo nginx -c $(pwd)/config/nginx.conf
## Or: sudo systemctl start nginx
```

---

### 7. **Testing & Verification**

#### 7.1 Health Checks

```bash
## Check all services
curl http://localhost:8001/health  # Auth
curl http://localhost:8002/health  # Service Mgmt
curl http://localhost:8003/health  # Provider Mgmt
curl http://localhost:8004/health  # Geospatial
curl http://localhost:8005/health  # Notifications
curl http://localhost:8006/health  # Search
curl http://localhost:8007/health  # Admin
curl http://localhost:8008/health  # Chatbot

## Check API Gateway
curl http://localhost:3000/api/health

## Check NGINX
curl http://localhost/api/health
```

**Expected**: All return `{"status": "healthy"}`

#### 7.2 Test Authentication

```bash
## Register user
curl -X POST http://localhost/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "full_name": "Test User",
    "phone": "9876543210"
  }'

## Login
curl -X POST http://localhost/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@idrm.gov.in",
    "password": "Admin123!"
  }'
```

**Expected**: Receive JWT tokens

#### 7.3 Test Service Request

```bash
## Get access token from login, then:
TOKEN="<your_access_token>"

## Create service request
curl -X POST http://localhost/api/v1/services \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "service_type": "MEDICAL",
    "description": "Need first aid",
    "location": {"lat": 13.0827, "lon": 80.2707},
    "urgency": "HIGH"
  }'
```

---

### 8. **Development Workflow**

#### 8.1 Daily Startup

```bash
## 1. Start infrastructure
sudo systemctl start postgresql redis-server

## 2. Start services
./scripts/start-all-services.sh

## 3. Start API gateway
cd api-gateway && bun run dev

## 4. Start NGINX (if needed)
sudo systemctl start nginx
```

#### 8.2 Making Changes

**Backend (Python):**
- Edit files in `services/<service-name>/`
- Uvicorn auto-reloads (if `--reload` flag used)
- Check terminal for errors

**API Gateway (Bun):**
- Edit files in `api-gateway/src/`
- Bun auto-reloads in dev mode
- Check terminal for errors

**Database:**
- Edit schema in `scripts/`
- Run migrations: `psql -U idrm_user -d idrm_db -f scripts/migration_xxx.sql`

#### 8.3 Viewing Logs

```bash
## Python service logs (if configured)
tail -f services/auth/logs/app.log

## Or check terminal output
## Each service running in separate terminal shows logs
```

---

### 9. **Troubleshooting**

#### 9.1 Common Issues

**Issue: Port already in use**
```bash
## Find process using port
sudo lsof -i :8001
## Kill process
sudo kill -9 <PID>
```

**Issue: Database connection fails**
```bash
## Check PostgreSQL running
sudo systemctl status postgresql

## Check credentials
psql -U idrm_user -d idrm_db

## Check DATABASE_URL in .env.development
```

**Issue: PostGIS functions not found**
```bash
## Enable PostGIS extension
psql -U idrm_user -d idrm_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

**Issue: Python package not found**
```bash
## Check conda environment active
conda activate idrm-mvp
conda list | grep <package-name>

## Reinstall if needed
pip install --break-system-packages <package-name>
```

---

### ✅ **Development Setup Complete!**

**You now have**:
- ✅ All 8 services running locally
- ✅ Database initialized with sample data
- ✅ API Gateway routing requests
- ✅ NGINX serving frontend
- ✅ Complete development environment

**You can now**:
- Access http://localhost for frontend
- Access http://localhost/api for API
- Develop and test locally
- Make changes with auto-reload

**Next steps**:
→ [31-STAGING-SETUP.md](31-STAGING-SETUP.md) - Deploy to staging  
→ [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md) - Production deployment

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Previous**: [23-API-SPECIFICATION.md](23-API-SPECIFICATION.md)  
**Next**: [31-STAGING-SETUP.md](31-STAGING-SETUP.md) (Batch 3)

---

## IDRM Monolith Development Setup v3.0

### Native Ubuntu Setup - No Docker, Three Frontends

**Version**: 3.0  
**Environment**: Development (Local)  
**Platforms**: HTML/Tailwind + React SPA + React Native  
**Approach**: Native services, hot reload, instant feedback

---

### 🎯 Overview

This guide sets up IDRM v3 for **development** on native Ubuntu:
- ✅ PostgreSQL as systemd service
- ✅ Redis as systemd service
- ✅ Python backend with hot reload
- ✅ Bun API Gateway with hot reload
- ✅ Three frontends with hot reload
- ❌ **NO Docker** (saves 5-10s per restart)
- ⚡ **Instant feedback** (<100ms hot reload)

---

### 📋 Prerequisites

**Before starting, complete**:
- ✅ `setup-prerequisites-v3.md` (all software installed)
- ✅ Ubuntu 22.04+ running
- ✅ 16GB+ RAM available
- ✅ 150GB+ disk space

**Verify**:
```bash
bun --version        # Should show: 1.0.0+
conda --version      # Should show: 23.x+
psql --version       # Should show: 16.x
redis-cli ping       # Should return: PONG
```

---

### 📁 Step 1: Project Structure Setup

#### Clone Repository

```bash
## Create projects directory
mkdir -p ~/projects
cd ~/projects

## Clone IDRM repo
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp

## Verify structure
ls -la
## Should show:
## - backend/
## - api-gateway/
## - frontend/
## - mobile/
## - database/
## - docs/
```

#### Project Structure (v3)

```
idrm-mvp/
├── backend/                    # Python FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── api/v1/            # API routes
│   │   │   ├── auth.py        # Port 8000
│   │   │   ├── services.py    # Port 8001
│   │   │   ├── geo.py         # Port 8002 (Python geospatial)
│   │   │   ├── analytics.py   # Port 8003
│   │   │   └── notifications.py # Port 8004
│   │   ├── core/              # Config, DB, cache
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── tests/
│   ├── requirements.txt
│   └── environment.yml        # Miniconda environment
│
├── api-gateway/               # Bun server
│   ├── src/
│   │   ├── index.ts          # Main gateway (Port 3000)
│   │   ├── routes/
│   │   └── middleware/
│   ├── package.json
│   └── bunfig.toml
│
├── frontend/
│   ├── html-tailwind/         # Primary web (Port 5173)
│   │   ├── src/
│   │   │   ├── index.html
│   │   │   ├── pages/
│   │   │   ├── styles/
│   │   │   └── js/
│   │   ├── package.json
│   │   └── vite.config.js
│   │
│   └── react-spa/             # Admin dashboard (Port 5174)
│       ├── src/
│       │   ├── App.tsx
│       │   ├── pages/
│       │   └── components/
│       ├── package.json
│       └── vite.config.ts
│
├── mobile/                    # React Native (Expo)
│   ├── App.tsx
│   ├── src/
│   │   ├── screens/
│   │   ├── components/
│   │   └── navigation/
│   ├── app.json
│   └── package.json
│
└── database/
    └── init/
        ├── 01-extensions.sql
        ├── 02-schema.sql
        └── 03-seed-data.sql
```

---

### 🗄️ Step 2: Database Setup

#### Create Database

```bash
## Switch to postgres user
sudo -u postgres psql

## Create database and user (if not done in prerequisites)
CREATE USER idrm_user WITH PASSWORD 'idrm_secure_password_2024';
CREATE DATABASE idrm_db OWNER idrm_user;

## Connect to database
\c idrm_db

## Enable extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search

## Grant privileges
GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO idrm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO idrm_user;

## Exit
\q
```

#### Initialize Schema

```bash
## Navigate to database init scripts
cd ~/projects/idrm-mvp/database/init

## Run initialization scripts
psql -U idrm_user -d idrm_db -f 01-extensions.sql
psql -U idrm_user -d idrm_db -f 02-schema.sql
psql -U idrm_user -d idrm_db -f 03-seed-data.sql

## Verify tables
psql -U idrm_user -d idrm_db -c "\dt"
## Should show: users, service_requests, assignments, etc.

## Verify PostGIS
psql -U idrm_user -d idrm_db -c "SELECT PostGIS_version();"
```

---

### 🐍 Step 3: Backend Setup (Python/FastAPI)

#### Create Conda Environment

```bash
cd ~/projects/idrm-mvp/backend

## Create environment from environment.yml
conda env create -f environment.yml

## Or create manually
conda create -n idrm-mvp python=3.11 -y
conda activate idrm-mvp

## Install dependencies
pip install --break-system-packages -r requirements.txt

## Verify installation
pip list | grep fastapi
pip list | grep geopandas
pip list | grep redis
```

#### Configure Environment Variables

```bash
## Create .env file
cat > ~/projects/idrm-mvp/backend/.env << 'EOF'
## Database
DATABASE_URL=postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db

## Redis
REDIS_URL=redis://localhost:6379/0

## JWT
JWT_SECRET_KEY=your-secret-key-change-in-production-at-least-32-chars
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

## CORS - Three frontends
CORS_ORIGINS=http://localhost:5173,http://localhost:5174,exp://192.168.1.100:19000

## Environment
ENVIRONMENT=development
DEBUG=true

## Email (optional for dev)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

## Geospatial
GEOSPATIAL_SERVICE_URL=http://localhost:8002
EOF

## Secure the file
chmod 600 .env
```

#### Initialize Database Migrations

```bash
cd ~/projects/idrm-mvp/backend

## Activate environment
conda activate idrm-mvp

## Initialize Alembic (if not already done)
alembic init alembic

## Configure alembic.ini
nano alembic.ini
## Set: sqlalchemy.url = postgresql://idrm_user:idrm_secure_password_2024@localhost:5432/idrm_db

## Create initial migration
alembic revision --autogenerate -m "Initial schema"

## Apply migrations
alembic upgrade head

## Verify
alembic current
```

#### Test Backend

```bash
## Start backend
conda activate idrm-mvp
cd ~/projects/idrm-mvp/backend
uvicorn app.main:app --reload --port 8000

## In another terminal, test
http GET http://localhost:8000/health
## Should return: {"status": "healthy"}

## Check API docs
## Open: http://localhost:8000/docs (Swagger)
## Open: http://localhost:8000/redoc (ReDoc)
```

---

### ⚡ Step 4: API Gateway Setup (Bun)

#### Install Dependencies

```bash
cd ~/projects/idrm-mvp/api-gateway

## Install with Bun
bun install

## Verify package.json has:
## - @types/node
## - typescript
## - (other dependencies)
```

#### Configure Environment

```bash
## Create .env file
cat > ~/projects/idrm-mvp/api-gateway/.env << 'EOF'
## Backend services
BACKEND_AUTH_URL=http://localhost:8000
BACKEND_SERVICES_URL=http://localhost:8001
BACKEND_GEO_URL=http://localhost:8002
BACKEND_ANALYTICS_URL=http://localhost:8003
BACKEND_NOTIFICATIONS_URL=http://localhost:8004

## Frontend URLs (for CORS)
FRONTEND_HTML_URL=http://localhost:5173
FRONTEND_SPA_URL=http://localhost:5174
FRONTEND_MOBILE_URL=exp://192.168.1.100:19000

## Server
PORT=3000
NODE_ENV=development

## WebSocket
WS_ENABLED=true
WS_PORT=3001
EOF
```

#### Test API Gateway

```bash
cd ~/projects/idrm-mvp/api-gateway

## Start with Bun
bun run dev
## Should start on http://localhost:3000

## In another terminal, test
http GET http://localhost:3000/health
## Should return: {"status": "ok", "gateway": "running"}
```

---

### 🎨 Step 5: Frontend Setup (Three Platforms)

#### 5.1 HTML/Tailwind (Primary Web)

```bash
cd ~/projects/idrm-mvp/frontend/html-tailwind

## Install dependencies with Bun
bun install

## Should install:
## - vite
## - tailwindcss
## - autoprefixer
## - postcss

## Configure API URL
cat > src/config.js << 'EOF'
export const API_URL = 'http://localhost:3000/api/v1';
export const WS_URL = 'ws://localhost:3001';
EOF

## Start dev server
bun run dev
## Should start on http://localhost:5173

## Verify
## Open: http://localhost:5173
## Should see: IDRM landing page
```

#### 5.2 React SPA (Admin Dashboard)

```bash
cd ~/projects/idrm-mvp/frontend/react-spa

## Install dependencies with Bun
bun install

## Should install:
## - react, react-dom
## - react-router-dom
## - vite
## - tailwindcss
## - recharts (for charts)

## Configure API URL
cat > src/config.ts << 'EOF'
export const API_URL = process.env.NODE_ENV === 'development'
  ? 'http://localhost:3000/api/v1'
  : 'https://api.idrm.example.com/api/v1';

export const WS_URL = process.env.NODE_ENV === 'development'
  ? 'ws://localhost:3001'
  : 'wss://api.idrm.example.com/ws';
EOF

## Start dev server
bun run dev
## Should start on http://localhost:5174

## Verify
## Open: http://localhost:5174
## Should see: Admin dashboard
```

#### 5.3 React Native (Mobile App)

```bash
cd ~/projects/idrm-mvp/mobile

## Install dependencies with Bun
bun install

## Should install:
## - expo
## - react-native
## - react-navigation
## - expo-location
## - expo-notifications

## Get your local IP
ip addr show | grep inet
## Example: 192.168.1.100

## Configure API URL
cat > src/config.ts << 'EOF'
export const API_URL = __DEV__
  ? 'http://192.168.1.100:3000/api/v1'  // Use your IP!
  : 'https://api.idrm.example.com/api/v1';

export const WS_URL = __DEV__
  ? 'ws://192.168.1.100:3001'
  : 'wss://api.idrm.example.com/ws';
EOF

## Start Expo dev server
npx expo start

## Options:
## - Press 'i' for iOS simulator
## - Press 'a' for Android emulator
## - Scan QR code with Expo Go app on phone
```

---

### 🚀 Step 6: Start All Services (Development Mode)

#### Option 1: Manual Start (5 Terminals)

**Terminal 1 - Backend**:
```bash
cd ~/projects/idrm-mvp/backend
conda activate idrm-mvp
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - API Gateway**:
```bash
cd ~/projects/idrm-mvp/api-gateway
bun run dev
```

**Terminal 3 - HTML/Tailwind**:
```bash
cd ~/projects/idrm-mvp/frontend/html-tailwind
bun run dev
```

**Terminal 4 - React SPA**:
```bash
cd ~/projects/idrm-mvp/frontend/react-spa
bun run dev
```

**Terminal 5 - React Native**:
```bash
cd ~/projects/idrm-mvp/mobile
npx expo start
```

#### Option 2: Automated Start Script

Create `~/projects/idrm-mvp/dev-start-v3.sh`:

```bash
#!/bin/bash

echo "🚀 Starting IDRM v3 Development Environment"
echo "==========================================="
echo ""

## Check if services are already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Backend already running on port 8000"
else
    echo "1️⃣  Starting Backend (Python/FastAPI)..."
    gnome-terminal --tab -- bash -c "cd ~/projects/idrm-mvp/backend && conda activate idrm-mvp && uvicorn app.main:app --reload --port 8000; exec bash"
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  API Gateway already running on port 3000"
else
    echo "2️⃣  Starting API Gateway (Bun)..."
    gnome-terminal --tab -- bash -c "cd ~/projects/idrm-mvp/api-gateway && bun run dev; exec bash"
fi

if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  HTML/Tailwind already running on port 5173"
else
    echo "3️⃣  Starting HTML/Tailwind Frontend..."
    gnome-terminal --tab -- bash -c "cd ~/projects/idrm-mvp/frontend/html-tailwind && bun run dev; exec bash"
fi

if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  React SPA already running on port 5174"
else
    echo "4️⃣  Starting React SPA Frontend..."
    gnome-terminal --tab -- bash -c "cd ~/projects/idrm-mvp/frontend/react-spa && bun run dev; exec bash"
fi

echo "5️⃣  Starting React Native (manual)..."
gnome-terminal --tab -- bash -c "cd ~/projects/idrm-mvp/mobile && npx expo start; exec bash"

echo ""
echo "✅ All services starting!"
echo ""
echo "URLs:"
echo "  Backend:      http://localhost:8000"
echo "  API Gateway:  http://localhost:3000"
echo "  HTML/Tailwind: http://localhost:5173"
echo "  React SPA:    http://localhost:5174"
echo "  React Native: Expo DevTools (auto-opens)"
echo ""
echo "API Docs:     http://localhost:8000/docs"
echo ""
```

```bash
## Make executable
chmod +x ~/projects/idrm-mvp/dev-start-v3.sh

## Run
~/projects/idrm-mvp/dev-start-v3.sh
```

---

### ✅ Step 7: Verify All Services

#### Health Check Script

Create `~/projects/idrm-mvp/health-check-v3.sh`:

```bash
#!/bin/bash

echo "IDRM v3 Health Check"
echo "===================="
echo ""

## Backend
echo "1. Backend (8000):"
curl -s http://localhost:8000/health | jq || echo "❌ Not responding"
echo ""

## API Gateway
echo "2. API Gateway (3000):"
curl -s http://localhost:3000/health | jq || echo "❌ Not responding"
echo ""

## HTML/Tailwind
echo "3. HTML/Tailwind (5173):"
curl -s http://localhost:5173 > /dev/null && echo "✅ Running" || echo "❌ Not running"
echo ""

## React SPA
echo "4. React SPA (5174):"
curl -s http://localhost:5174 > /dev/null && echo "✅ Running" || echo "❌ Not running"
echo ""

## PostgreSQL
echo "5. PostgreSQL:"
pg_isready -U idrm_user -d idrm_db && echo "✅ Running" || echo "❌ Not running"
echo ""

## Redis
echo "6. Redis:"
redis-cli ping && echo "✅ Running" || echo "❌ Not running"
echo ""

echo "===================="
echo "Health check complete!"
```

```bash
chmod +x ~/projects/idrm-mvp/health-check-v3.sh
~/projects/idrm-mvp/health-check-v3.sh
```

---

### 🧪 Step 8: Run Tests

#### Backend Tests

```bash
cd ~/projects/idrm-mvp/backend
conda activate idrm-mvp

## Run all tests
pytest tests/ -v

## Run with coverage
pytest tests/ -v --cov=app --cov-report=html

## Open coverage report
## firefox htmlcov/index.html
```

#### Frontend Tests

```bash
## HTML/Tailwind
cd ~/projects/idrm-mvp/frontend/html-tailwind
bun test

## React SPA
cd ~/projects/idrm-mvp/frontend/react-spa
bun test

## React Native
cd ~/projects/idrm-mvp/mobile
bun test
```

---

### 🔧 Development Workflow

#### Daily Routine

```bash
## Morning startup
~/projects/idrm-mvp/dev-start-v3.sh

## Work on features
## - Edit code in VSCode
## - Save file → Hot reload (<100ms)
## - Test in browser/app

## Check logs as needed
## - Terminal 1: Backend logs
## - Terminal 2: API Gateway logs
## - Terminal 3-5: Frontend logs

## Run tests before commit
cd ~/projects/idrm-mvp/backend && pytest
cd ~/projects/idrm-mvp/frontend/react-spa && bun test

## Commit changes
git add .
git commit -m "feat: add new feature"
git push

## Evening shutdown
## Ctrl+C in each terminal
```

#### Hot Reload Performance

**v3 Native vs Docker**:
```
Change Python file → Backend reloads:
  Native: ~100ms
  Docker: ~5-10s (rebuild container)

Change TypeScript file → API Gateway reloads:
  Native (Bun): ~50ms
  Docker: ~3-5s

Change React file → Frontend reloads:
  Native (Vite HMR): ~50ms
  Docker: ~2-3s

Result: 50-100x faster iteration with native!
```

---

### 🐛 Troubleshooting

#### Port Already in Use

```bash
## Find process using port
sudo lsof -i :8000  # Backend
sudo lsof -i :3000  # API Gateway
sudo lsof -i :5173  # HTML/Tailwind
sudo lsof -i :5174  # React SPA

## Kill process
kill -9 <PID>
```

#### Backend Won't Start

```bash
## Check conda environment
conda activate idrm-mvp
which python  # Should show miniconda path

## Check database connection
psql -U idrm_user -d idrm_db -c "SELECT 1;"

## Check Redis
redis-cli ping

## View backend logs
cd ~/projects/idrm-mvp/backend
uvicorn app.main:app --reload --port 8000 --log-level debug
```

#### Frontend Won't Connect to Backend

```bash
## Check CORS configuration
## backend/app/main.py should have:
allow_origins=[
    "http://localhost:5173",  # HTML/Tailwind
    "http://localhost:5174",  # React SPA
    "exp://*",                # React Native
]

## Check API Gateway routing
curl http://localhost:3000/api/v1/health
```

#### React Native Can't Reach Backend

```bash
## Make sure you're using your local IP, not localhost
## In mobile/src/config.ts:
export const API_URL = 'http://192.168.1.100:3000/api/v1';
## Replace with YOUR IP from: ip addr show

## Check firewall allows ports
sudo ufw allow 3000
sudo ufw allow 19000  # Expo
```

---

### 📊 Resource Usage

```
Development Environment (all running):
Backend:         100-150 MB
API Gateway:     50-80 MB
HTML/Tailwind:   80-120 MB
React SPA:       100-150 MB
React Native:    200-300 MB
PostgreSQL:      150-200 MB
Redis:           30-50 MB
VSCode:          300-500 MB
Chrome:          500-800 MB
──────────────────────────────
TOTAL:           1.5-2.5 GB

Your 16-32GB system: Plenty of headroom! ✅
```

---

### 🎯 Next Steps

**Development environment ready!** Now you can:

1. ✅ Start implementing features
2. ✅ Follow `idrm-mvp-roadmap-v3.md` week-by-week plan
3. ✅ Use `QUICK-REFERENCE-V3.md` for daily commands
4. ✅ Reference `design-system-v3.md` for UI components

**For deployment**:
- Staging: Follow `setup-staging-v3.md` (Docker)
- Production: Follow `setup-production-v3.md` (CI/CD)

---

**IDRM v3 Development: Native, Fast, Multi-Platform!** ⚡

**Hot Reload**: <100ms  
**Platforms**: All three ready  
**Next**: Start coding features!
