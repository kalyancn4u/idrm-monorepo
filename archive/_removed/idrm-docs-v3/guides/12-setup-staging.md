# IDRM v3 · Staging Setup

<!-- IDRM-CLEANUP doc=v3-g12-staging status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — staging = FFP
> Separate staging = **FFP** (multi-env CI/CD) → [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md).
> MVP = single native Ubuntu server. *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: DevOps · Status: Archived — v3 historical generation*
*Consolidated from: 31-STAGING-SETUP.md, setup-staging-v3.md*

## Contents
- [IDRM: Staging Environment Setup](#idrm-staging-environment-setup)
- [IDRM Staging Environment Setup v3.0](#idrm-staging-environment-setup-v30)

---

## IDRM: Staging Environment Setup

### Docker-Based Pre-Production Environment (For Complete Novices!)

**Version**: 3.0 Consolidated  
**Audience**: DevOps beginners, system administrators, developers  
**Technology**: Docker Compose + Python + PostgreSQL + NGINX  
**Reading Time**: 2-3 hours (implement step-by-step!)  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [What Is Staging?](#1-what-is-staging)
2. [Prerequisites](#2-prerequisites)
3. [Docker Setup](#3-docker-setup)
4. [Configuration Files](#4-configuration-files)
5. [Deployment](#5-deployment)
6. [Verification](#6-verification)
7. [Troubleshooting](#7-troubleshooting)

---

### 1. **What Is Staging?**

#### 1.1 Staging Explained (For Novices)

**Staging** = A copy of production environment for testing

**Restaurant analogy**:
- **Development** = Test kitchen (your computer)
- **Staging** = Soft opening (friends & family test)
- **Production** = Grand opening (real customers)

**Why staging?**:
- ✅ Test in production-like environment
- ✅ Catch bugs before they reach users
- ✅ Verify deployments work
- ✅ Train team on new features
- ✅ Show clients demos

---

### 2. **Prerequisites**

#### Hardware Requirements

```
Minimum:
- CPU: 8 cores
- RAM: 16 GB
- Disk: 200 GB SSD

Recommended:
- CPU: 16 cores
- RAM: 32 GB
- Disk: 500 GB NVMe SSD
```

#### Software Checklist

- [ ] Ubuntu 22.04/24.04 LTS
- [ ] Docker 24.0+
- [ ] Docker Compose 2.20+
- [ ] Git installed
- [ ] 200GB free disk space

---

### 3. **Docker Setup**

#### Installation

```bash
## Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

## Add user to docker group
sudo usermod -aG docker $USER

## Restart and verify
docker --version
docker compose version
```

#### Create Docker Network

```bash
docker network create idrm-network
```

---

### 4. **Configuration Files**

#### Create `.env.staging`

```bash
## Database
POSTGRES_DB=idrm_staging
POSTGRES_USER=idrm_staging_user
POSTGRES_PASSWORD=CHANGE_ME_staging_db_secure_password

## Redis
REDIS_PASSWORD=CHANGE_ME_staging_redis_password

## JWT
JWT_SECRET_KEY=CHANGE_ME_use_openssl_rand_hex_32

## Environment
ENVIRONMENT=staging
DEBUG=True
```

**Generate secure passwords**:
```bash
openssl rand -base64 32  # For database
openssl rand -hex 32      # For JWT secret
```

#### Create `docker-compose.staging.yml`

```yaml
version: '3.8'

services:
  # PostgreSQL + PostGIS
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres-staging
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - idrm-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  # Redis
  redis:
    image: redis:7.2-alpine
    container_name: idrm-redis-staging
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis-data:/data
    networks:
      - idrm-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3
    restart: unless-stopped

  # Auth Service (Python FastAPI)
  auth-service:
    build:
      context: ./backend/services/auth
      dockerfile: Dockerfile
    container_name: idrm-auth-staging
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - idrm-network
    restart: unless-stopped

  # Service Management (Python FastAPI)
  service-mgmt:
    build:
      context: ./backend/services/service_mgmt
      dockerfile: Dockerfile
    container_name: idrm-service-mgmt-staging
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}
    depends_on:
      - postgres
    networks:
      - idrm-network
    restart: unless-stopped

  # Geospatial Service (Python FastAPI)
  geospatial:
    build:
      context: ./backend/services/geospatial
      dockerfile: Dockerfile
    container_name: idrm-geospatial-staging
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres/${POSTGRES_DB}
    depends_on:
      - postgres
    networks:
      - idrm-network
    restart: unless-stopped

  # NGINX
  nginx:
    image: nginx:1.24-alpine
    container_name: idrm-nginx-staging
    ports:
      - "80:80"
    volumes:
      - ./nginx/staging.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - auth-service
      - service-mgmt
      - geospatial
    networks:
      - idrm-network
    restart: unless-stopped

volumes:
  postgres-data:
  redis-data:

networks:
  idrm-network:
    external: true
```

---

### 5. **Deployment**

#### Build and Start

```bash
## Build all images
docker compose -f docker-compose.staging.yml build

## Start services
docker compose -f docker-compose.staging.yml up -d

## View logs
docker compose -f docker-compose.staging.yml logs -f

## Check status
docker compose -f docker-compose.staging.yml ps
```

---

### 6. **Verification**

#### Health Checks

```bash
## Test NGINX
curl http://localhost/health

## Test Auth Service
curl http://localhost/api/auth/health

## Test Geospatial Service
curl http://localhost/geo/health

## Check all containers
docker compose -f docker-compose.staging.yml ps
```

Expected: All services show "Up (healthy)"

---

### 7. **Troubleshooting**

#### Container Won't Start

```bash
## View logs
docker compose -f docker-compose.staging.yml logs <service-name>

## Restart specific service
docker compose -f docker-compose.staging.yml restart <service-name>

## Remove and recreate
docker compose -f docker-compose.staging.yml up -d --force-recreate <service-name>
```

#### Database Connection Error

```bash
## Check PostgreSQL is running
docker compose -f docker-compose.staging.yml ps postgres

## Test connection
docker compose -f docker-compose.staging.yml exec postgres \
  psql -U idrm_staging_user -d idrm_staging -c "SELECT version();"
```

---

### ✅ **Summary**

**You've successfully**:
- ✅ Set up Docker staging environment
- ✅ Configured all services
- ✅ Deployed IDRM stack
- ✅ Verified everything works

**Next**: [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Previous**: [25-BACKEND-IMPLEMENTATION.md](25-BACKEND-IMPLEMENTATION.md)  
**Next**: [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)

---

## IDRM Staging Environment Setup v3.0

### Docker-Based Multi-Platform Staging

**Version**: 3.0  
**Environment**: Staging (Pre-Production)  
**Platforms**: HTML/Tailwind + React SPA + React Native  
**Approach**: Docker Compose for consistency

---

### 🎯 Overview

Staging environment setup with Docker for:
- ✅ Production-like environment
- ✅ Consistent deployments
- ✅ Easy rollback
- ✅ Team collaboration
- ✅ Pre-production testing

**Architecture**:
```
Docker Network: idrm-staging

Services:
- postgres (PostgreSQL 16 + PostGIS 3.4)
- redis (Redis 7.2)
- backend (Python/FastAPI)
- api-gateway (Bun)
- frontend-web (HTML/Tailwind - NGINX)
- frontend-admin (React SPA - NGINX)
- (mobile builds separately via Expo)
```

---

### 📋 Prerequisites

- ✅ Ubuntu 22.04+ server
- ✅ Docker installed
- ✅ Docker Compose installed
- ✅ Domain name configured
- ✅ SSL certificate ready

```bash
## Install Docker
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

## Verify
docker --version
docker-compose --version
```

---

### 📁 Project Structure

```
idrm-mvp/
├── docker/
│   └── staging/
│       ├── docker-compose.yml
│       ├── backend.Dockerfile
│       ├── api-gateway.Dockerfile
│       ├── frontend-web.Dockerfile
│       ├── frontend-admin.Dockerfile
│       └── nginx/
│           ├── nginx.conf
│           └── ssl/
├── .env.staging
└── scripts/
    ├── deploy-staging.sh
    └── rollback-staging.sh
```

---

### 🐳 Step 1: Create Dockerfiles

#### backend.Dockerfile

```dockerfile
## docker/staging/backend.Dockerfile
FROM continuumio/miniconda3:latest

WORKDIR /app

## Copy environment file
COPY backend/environment.yml .

## Create conda environment
RUN conda env create -f environment.yml

## Make RUN commands use the conda environment
SHELL ["conda", "run", "-n", "idrm-mvp", "/bin/bash", "-c"]

## Copy application
COPY backend/ .

## Install additional dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

## Run with conda environment
CMD ["conda", "run", "--no-capture-output", "-n", "idrm-mvp", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### api-gateway.Dockerfile

```dockerfile
## docker/staging/api-gateway.Dockerfile
FROM oven/bun:latest

WORKDIR /app

## Copy package files
COPY api-gateway/package.json api-gateway/bun.lockb ./

## Install dependencies
RUN bun install --frozen-lockfile

## Copy application
COPY api-gateway/ .

## Build TypeScript
RUN bun build ./src/index.ts --outdir ./dist

EXPOSE 3000 3001

CMD ["bun", "run", "dist/index.js"]
```

#### frontend-web.Dockerfile

```dockerfile
## docker/staging/frontend-web.Dockerfile
FROM oven/bun:latest AS builder

WORKDIR /app

## Copy package files
COPY frontend/html-tailwind/package.json frontend/html-tailwind/bun.lockb ./

## Install dependencies
RUN bun install --frozen-lockfile

## Copy application
COPY frontend/html-tailwind/ .

## Build
RUN bun run build

## Production image
FROM nginx:alpine

## Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

## Copy nginx config
COPY docker/staging/nginx/web.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
```

#### frontend-admin.Dockerfile

```dockerfile
## docker/staging/frontend-admin.Dockerfile
FROM oven/bun:latest AS builder

WORKDIR /app

## Copy package files
COPY frontend/react-spa/package.json frontend/react-spa/bun.lockb ./

## Install dependencies
RUN bun install --frozen-lockfile

## Copy application
COPY frontend/react-spa/ .

## Build
RUN bun run build

## Production image
FROM nginx:alpine

## Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

## Copy nginx config
COPY docker/staging/nginx/admin.conf /etc/nginx/conf.d/default.conf

EXPOSE 80 443
```

---

### 🔧 Step 2: Docker Compose Configuration

#### docker-compose.yml

```yaml
## docker/staging/docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-staging-postgres
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ../../database/init:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - idrm-staging
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7.2-alpine
    container_name: idrm-staging-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - idrm-staging
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  backend:
    build:
      context: ../..
      dockerfile: docker/staging/backend.Dockerfile
    container_name: idrm-staging-backend
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: staging
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    ports:
      - "8000:8000"
    networks:
      - idrm-staging
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  api-gateway:
    build:
      context: ../..
      dockerfile: docker/staging/api-gateway.Dockerfile
    container_name: idrm-staging-gateway
    environment:
      BACKEND_URL: http://backend:8000
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      NODE_ENV: staging
    depends_on:
      - backend
      - redis
    ports:
      - "3000:3000"
      - "3001:3001"
    networks:
      - idrm-staging
    restart: unless-stopped

  frontend-web:
    build:
      context: ../..
      dockerfile: docker/staging/frontend-web.Dockerfile
    container_name: idrm-staging-web
    ports:
      - "5173:80"
    networks:
      - idrm-staging
    restart: unless-stopped

  frontend-admin:
    build:
      context: ../..
      dockerfile: docker/staging/frontend-admin.Dockerfile
    container_name: idrm-staging-admin
    ports:
      - "5174:80"
    networks:
      - idrm-staging
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: idrm-staging-nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - api-gateway
      - frontend-web
      - frontend-admin
    networks:
      - idrm-staging
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  idrm-staging:
    driver: bridge
```

---

### 🌐 Step 3: NGINX Configuration

#### nginx.conf

```nginx
## docker/staging/nginx/nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream api_gateway {
        server api-gateway:3000;
    }

    upstream frontend_web {
        server frontend-web:80;
    }

    upstream frontend_admin {
        server frontend-admin:80;
    }

    # HTTP redirect to HTTPS
    server {
        listen 80;
        server_name staging.idrm.example.com admin.staging.idrm.example.com;
        return 301 https://$host$request_uri;
    }

    # Main web frontend
    server {
        listen 443 ssl http2;
        server_name staging.idrm.example.com;

        ssl_certificate /etc/nginx/ssl/staging.crt;
        ssl_certificate_key /etc/nginx/ssl/staging.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;

        # Frontend
        location / {
            proxy_pass http://frontend_web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # API
        location /api/ {
            proxy_pass http://api_gateway;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # WebSocket
        location /ws {
            proxy_pass http://api_gateway;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
    }

    # Admin frontend
    server {
        listen 443 ssl http2;
        server_name admin.staging.idrm.example.com;

        ssl_certificate /etc/nginx/ssl/staging.crt;
        ssl_certificate_key /etc/nginx/ssl/staging.key;
        ssl_protocols TLSv1.2 TLSv1.3;

        location / {
            proxy_pass http://frontend_admin;
            proxy_set_header Host $host;
        }

        location /api/ {
            proxy_pass http://api_gateway;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
        }
    }
}
```

---

### 🔐 Step 4: Environment Configuration

#### .env.staging

```bash
## Database
DB_USER=idrm_staging_user
DB_PASSWORD=idrm_staging_secure_password_2024
DB_NAME=idrm_staging_db

## Redis
REDIS_PASSWORD=redis_staging_password_2024

## JWT
JWT_SECRET_KEY=your-staging-secret-key-at-least-32-characters-long

## Domain
DOMAIN=staging.idrm.example.com
ADMIN_DOMAIN=admin.staging.idrm.example.com

## Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=staging@idrm.example.com
SMTP_PASSWORD=staging-email-password
```

---

### 🚀 Step 5: Deployment

#### Deploy Script

```bash
#!/bin/bash
## scripts/deploy-staging.sh

set -e

echo "🚀 Deploying IDRM v3 to Staging"
echo "==============================="
echo ""

## Load environment
set -a
source .env.staging
set +a

## Navigate to docker directory
cd docker/staging

## Pull latest code
echo "1️⃣  Pulling latest code..."
git pull origin develop

## Build images
echo "2️⃣  Building Docker images..."
docker-compose build --no-cache

## Stop old containers
echo "3️⃣  Stopping old containers..."
docker-compose down

## Start new containers
echo "4️⃣  Starting new containers..."
docker-compose up -d

## Wait for services
echo "5️⃣  Waiting for services to be healthy..."
sleep 30

## Run migrations
echo "6️⃣  Running database migrations..."
docker-compose exec -T backend conda run -n idrm-mvp alembic upgrade head

## Health check
echo "7️⃣  Running health checks..."
curl -f https://staging.idrm.example.com/api/health || exit 1
curl -f https://admin.staging.idrm.example.com || exit 1

echo ""
echo "✅ Deployment complete!"
echo ""
echo "URLs:"
echo "  Web:   https://staging.idrm.example.com"
echo "  Admin: https://admin.staging.idrm.example.com"
echo "  API:   https://staging.idrm.example.com/api/docs"
```

#### Rollback Script

```bash
#!/bin/bash
## scripts/rollback-staging.sh

echo "⏮️  Rolling back to previous version..."

cd docker/staging

## Get previous image tags
PREVIOUS_TAG=$(docker images --format "{{.Tag}}" | grep staging | head -2 | tail -1)

## Rollback
docker-compose down
docker tag idrm-backend:${PREVIOUS_TAG} idrm-backend:latest
docker tag idrm-gateway:${PREVIOUS_TAG} idrm-gateway:latest
docker-compose up -d

echo "✅ Rollback complete!"
```

---

### 📱 Step 6: Mobile App Deployment (Expo)

#### Build for Staging

```bash
## Configure staging environment
cat > mobile/app.config.staging.js << 'EOF'
export default {
  expo: {
    name: "IDRM Staging",
    slug: "idrm-staging",
    version: "3.0.0",
    extra: {
      apiUrl: "https://staging.idrm.example.com/api/v1",
      wsUrl: "wss://staging.idrm.example.com/ws",
      environment: "staging"
    }
  }
}
EOF

## Build for iOS (TestFlight)
eas build --platform ios --profile staging

## Build for Android (Internal Testing)
eas build --platform android --profile staging

## Submit to TestFlight/Internal Testing
eas submit --platform ios --profile staging
eas submit --platform android --profile staging
```

---

### ✅ Verification

#### Health Check

```bash
## All services
curl https://staging.idrm.example.com/api/health
curl https://admin.staging.idrm.example.com

## Backend
docker-compose exec backend conda run -n idrm-mvp python -c "import app; print('OK')"

## Database
docker-compose exec postgres psql -U idrm_staging_user -d idrm_staging_db -c "SELECT COUNT(*) FROM users;"

## Redis
docker-compose exec redis redis-cli -a redis_staging_password_2024 ping
```

---

### 🔧 Maintenance

#### View Logs

```bash
## All services
docker-compose logs -f

## Specific service
docker-compose logs -f backend
docker-compose logs -f api-gateway
```

#### Update

```bash
## Pull latest code
git pull origin develop

## Rebuild and restart
./scripts/deploy-staging.sh
```

#### Backup Database

```bash
docker-compose exec postgres pg_dump -U idrm_staging_user idrm_staging_db > backup.sql
```

---

**IDRM v3 Staging: Production-Like Multi-Platform Testing!** 🐳

**Next**: `setup-production-v3.md` for production deployment with CI/CD
