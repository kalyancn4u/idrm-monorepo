# IDRM Deployment Guide
## From Development to Production — Complete Reference

**Version**: 3.0  
**Last Updated**: May 29, 2026  
**Audience**: Developers, DevOps engineers, system administrators  
**Platforms**: HTML/Tailwind + React SPA + React Native + Python Backend

---

## 📋 Table of Contents

1. [Understanding the Three Environments](#1-understanding-the-three-environments)
2. [Staging Environment (Docker Compose)](#2-staging-environment-docker-compose)
3. [Production Environment (Cloud)](#3-production-environment-cloud)
4. [CI/CD Pipeline (GitHub Actions)](#4-cicd-pipeline-github-actions)
5. [Mobile App Deployment (Expo)](#5-mobile-app-deployment-expo)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Understanding the Three Environments

### 1.1 What Are Environments?

Environments are separate, isolated copies of the application running in different places with different purposes.

| Aspect | Development | Staging | Production |
|---|---|---|---|
| **Purpose** | Write and test code | Pre-production testing | Serve real users |
| **Location** | Your laptop | Test server | Cloud servers |
| **Data** | Test/seed data | Realistic fake data | Real user data |
| **Docker** | ❌ No (native processes) | ✅ Yes | ✅ Yes |
| **Mistakes OK?** | ✅ Break things freely | ⚠️ Somewhat | ❌ Never |
| **Uptime** | Doesn't matter | Should be stable | 99.9%+ required |
| **Cost** | Free | 1 server (~$20–50/mo) | Multiple servers ($200–$3,000+/mo) |

### 1.2 The Deployment Flow

```
Developer laptop (Development)
    ↓ git push origin develop
GitHub Actions CI triggers
    ↓ Tests pass + Docker images built
Auto-deploy to Staging
    ↓ QA team tests, issues fixed
Manual approval (PR to main)
    ↓ git push origin main
GitHub Actions CI triggers
    ↓ Tests pass + Docker images built
Blue-Green deploy to Production
    ↓ Smoke tests pass
Traffic switches to new version
```

### 1.3 Technology Stack per Environment

| Component | Development | Staging | Production |
|---|---|---|---|
| Backend | `uvicorn --reload` (native) | Docker container (Miniconda image) | Docker + replicas |
| API Gateway | `bun run dev` (native) | Docker container | Docker + replicas |
| Database | systemd service | Docker container | Managed DB / Docker |
| Redis | systemd service | Docker container | Managed Redis / Docker |
| Frontend | Vite dev server | NGINX in Docker | NGINX in Docker |
| SSL | None | Self-signed / Let's Encrypt | Let's Encrypt + auto-renewal |

### 🚩 Ports per environment (and running them on one host)

All three environments use the **same ports** — `8000` (backend), `3000`/`3001` (gateway), `5432` (Postgres), `6379` (Redis) — plus `80`/`443` (NGINX) in staging/production.

🚩 **On a single host, only ONE environment can run at a time** (otherwise "port is already allocated"). Development uses the **system** Postgres/Redis; staging/production run their **own** in Docker — both bind `5432`/`6379`, so switching means stopping one set first:

```bash
# Going to Docker (staging/prod): stop the native dev processes + system services first
sudo systemctl stop postgresql redis-server
# Going back to native dev: stop the Docker stack first
docker compose -f infra/docker/full-stack.yml down
```

🚩 **Exposure differs by environment.** In dev everything is on `localhost` (no firewall needed). In **production, only `80`/`443` (NGINX) should face the internet** — keep `8000`, `3000`, `5432`, `6379` internal to the host/Docker network.

> Full step-by-step, including the dev→staging→prod **switch checklists**, is in **`docs/IDRM-UBUNTU-PORTS-AND-ENVIRONMENTS.md`**.

---

## 2. Staging Environment (Docker Compose)

Staging uses Docker Compose to create a production-like environment on a single server. Every service runs in a container.

### 2.1 Prerequisites

```bash
# Ubuntu 22.04+
sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER  # Log out and back in after this

# Verify
docker --version          # Docker version 24.x+
docker-compose --version  # Docker Compose version 2.x+
```

### 2.2 Directory Structure

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

### 2.3 Dockerfiles

**backend.Dockerfile** (uses Miniconda for geospatial library support):
```dockerfile
FROM continuumio/miniconda3:latest
WORKDIR /app
COPY src/backend/app-python/environment.yml .
RUN conda env create -f environment.yml
SHELL ["conda", "run", "-n", "idrm-mvp", "/bin/bash", "-c"]
COPY src/backend/app-python/ .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 8000
CMD ["conda", "run", "--no-capture-output", "-n", "idrm-mvp", \
     "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**api-gateway.Dockerfile**:
```dockerfile
FROM oven/bun:latest
WORKDIR /app
COPY src/backend/api-gateway/package.json src/backend/api-gateway/bun.lockb ./
RUN bun install --frozen-lockfile
COPY src/backend/api-gateway/ .
RUN bun build ./src/index.ts --outdir ./dist
EXPOSE 3000 3001
CMD ["bun", "run", "dist/index.js"]
```

**frontend-web.Dockerfile** (HTML/Tailwind — multi-stage build):
```dockerfile
FROM oven/bun:latest AS builder
WORKDIR /app
COPY src/frontend/web-html/package.json src/frontend/web-html/bun.lockb ./
RUN bun install --frozen-lockfile
COPY src/frontend/web-html/ .
RUN bun run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/staging/nginx/web.conf /etc/nginx/conf.d/default.conf
EXPOSE 80 443
```

**frontend-admin.Dockerfile** (React SPA — same pattern):
```dockerfile
FROM oven/bun:latest AS builder
WORKDIR /app
COPY src/frontend/web-react/package.json src/frontend/web-react/bun.lockb ./
RUN bun install --frozen-lockfile
COPY src/frontend/web-react/ .
RUN bun run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY docker/staging/nginx/admin.conf /etc/nginx/conf.d/default.conf
EXPOSE 80 443
```

### 2.4 Docker Compose Configuration

```yaml
# docker/staging/docker-compose.yml
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

### 2.5 NGINX Configuration

```nginx
# docker/staging/nginx/nginx.conf
events { worker_connections 1024; }

http {
    upstream api_gateway  { server api-gateway:3000; }
    upstream frontend_web { server frontend-web:80; }
    upstream frontend_admin { server frontend-admin:80; }

    # HTTP → HTTPS redirect
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

        location / {
            proxy_pass http://frontend_web;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        location /api/ {
            proxy_pass http://api_gateway;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
        }
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

### 2.6 Environment File

```bash
# .env.staging
DB_USER=idrm_staging_user
DB_PASSWORD=idrm_staging_secure_password_2024
DB_NAME=idrm_staging_db
REDIS_PASSWORD=redis_staging_password_2024
JWT_SECRET_KEY=your-staging-secret-key-at-least-32-characters-long
DOMAIN=staging.idrm.example.com
ADMIN_DOMAIN=admin.staging.idrm.example.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=staging@idrm.example.com
SMTP_PASSWORD=staging-email-password
```

### 2.7 Deploy Script

```bash
#!/bin/bash
# scripts/deploy-staging.sh
set -e

echo "Deploying IDRM v3 to Staging..."
set -a; source .env.staging; set +a
cd docker/staging

git pull origin develop
docker-compose build --no-cache
docker-compose down
docker-compose up -d

echo "Waiting for services to be healthy..."
sleep 30

docker-compose exec -T backend conda run -n idrm-mvp alembic upgrade head

curl -f https://staging.idrm.example.com/api/health || exit 1
echo "Deployment complete!"
```

### 2.8 Staging Verification

```bash
# All services running?
docker-compose ps

# Health check
curl https://staging.idrm.example.com/api/health

# Check logs
docker-compose logs -f backend
docker-compose logs -f api-gateway

# Database
docker-compose exec postgres psql -U idrm_staging_user -d idrm_staging_db -c "SELECT COUNT(*) FROM users;"

# Redis
docker-compose exec redis redis-cli -a redis_staging_password_2024 ping

# Backup
docker-compose exec postgres pg_dump -U idrm_staging_user idrm_staging_db > backup.sql
```

---

## 3. Production Environment (Cloud)

### 3.1 Architecture

```
                            Internet
                               │
                               ↓
                        Load Balancer (AWS ALB / CloudFlare)
                               │
                ┌──────────────┼──────────────┐
                ↓              ↓              ↓
        Web Servers      Admin Servers   API Servers
      (NGINX + Web)    (NGINX + Admin) (API Gateway)
                └──────────────┼──────────────┘
                               ↓
                        Backend Services
                     (Python FastAPI + Bun)
                               │
                ┌──────────────┼──────────────┐
                ↓              ↓              ↓
          PostgreSQL       Redis         S3/Storage
       (Primary+Replica) (Cluster)    (Media/Logs)
```

### 3.2 Infrastructure Tiers

| Tier | Users | Resources | Monthly Cost |
|---|---|---|---|
| **MVP (Tier 1)** | 500–1,000 | Single server: 8 vCPU, 16GB RAM, 200GB SSD | ~$96 |
| **Growth (Tier 2)** | 2,000–5,000 | 2 app servers + LB + DB server | ~$250–300 |
| **Scale (Tier 3)** | 5,000–10,000 | 4 app servers + LB + DB replica + Redis cluster | ~$800–1,200 |
| **Enterprise** | 100,000+ | Auto-scaling (4–20 servers) + multi-region + CDN | $3,000–10,000 |

**When to scale**: CPU > 70% sustained OR p95 response time > 500ms OR > 800 concurrent users.

**Cloud Providers** (recommended order): DigitalOcean → Hetzner → Google Cloud → AWS.

### 3.3 Initial Server Setup

```bash
# SSH into server
ssh root@<server-ip>

# Update and install Docker
apt update && apt upgrade -y
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
systemctl enable docker

# Firewall — open ONLY the public web ports; everything else stays internal.
ufw allow OpenSSH    # 🚩 allow SSH BEFORE `ufw enable`, or you lock yourself out
ufw allow 80/tcp     # HTTP (redirect to HTTPS)
ufw allow 443/tcp    # HTTPS — the only real public entry point
ufw enable
ufw status verbose   # confirm the rules
# 🚩 Do NOT open 8000 / 3000 / 3001 / 5432 / 6379 — they stay internal (Docker network only).
# 🚩 On a cloud VM, also open 80/443 in the provider's Security Group / cloud firewall (a separate layer from ufw).
```

### 3.4 SSL Certificates

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificates (replace with your domains)
certbot --nginx -d idrm.example.com -d admin.idrm.example.com -d api.idrm.example.com

# Auto-renewal (add to crontab)
echo "0 0,12 * * * root certbot renew --quiet" | tee -a /etc/crontab
```

### 3.5 Production Docker Compose

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  backend:
    image: ghcr.io/your-org/idrm-backend:${VERSION}
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      ENVIRONMENT: production
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        max_attempts: 3
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  api-gateway:
    image: ghcr.io/your-org/idrm-gateway:${VERSION}
    environment:
      BACKEND_URL: http://backend:8000
      REDIS_URL: ${REDIS_URL}
      NODE_ENV: production
    deploy:
      replicas: 2

  nginx:
    image: ghcr.io/your-org/idrm-nginx:${VERSION}
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt:ro
    deploy:
      replicas: 2
```

### 3.6 Monitoring (Prometheus + Grafana)

```yaml
# monitoring/docker-compose.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3001:3000"

  loki:
    image: grafana/loki:latest
    volumes:
      - loki_data:/loki
    ports:
      - "3100:3100"
```

### 3.7 Automated Backups

**Backup strategy by environment:**

| Environment | Frequency | Retention | Location |
|-------------|-----------|-----------|----------|
| Development | None | — | Regenerate from seeds |
| Staging | Daily 11 PM IST | 7 days rolling | Local server |
| Production | Hourly | 24 hours | Local server |
| Production | Daily midnight | 30 days | Local server |
| Production | Weekly Sunday 1 AM | 90 days | Local + S3 |
| Production | Monthly 1st Sunday | 1 year | S3 Glacier |

```bash
#!/bin/bash
# scripts/backup-production.sh
# Usage: backup-production.sh <hourly|daily|weekly|monthly>

BACKUP_TYPE=${1:-daily}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/idrm"
DB_HOST="db.idrm.example.com"
DB_USER="idrm_prod"
DB_NAME="idrm_prod"

case $BACKUP_TYPE in
  hourly)
    pg_dump -U $DB_USER -h $DB_HOST $DB_NAME > ${BACKUP_DIR}/hourly/db_${DATE}.sql
    gzip ${BACKUP_DIR}/hourly/db_${DATE}.sql
    # Keep last 24 hours only
    find ${BACKUP_DIR}/hourly -mtime +1 -delete
    ;;
  daily)
    pg_dump -U $DB_USER -h $DB_HOST $DB_NAME > ${BACKUP_DIR}/daily/db_${DATE}.sql
    gzip ${BACKUP_DIR}/daily/db_${DATE}.sql
    # Also backup Redis
    redis-cli -h redis.idrm.example.com --rdb ${BACKUP_DIR}/daily/redis_${DATE}.rdb
    find ${BACKUP_DIR}/daily -mtime +30 -delete
    ;;
  weekly)
    pg_dump -U $DB_USER -h $DB_HOST $DB_NAME > ${BACKUP_DIR}/weekly/db_${DATE}.sql
    gzip ${BACKUP_DIR}/weekly/db_${DATE}.sql
    # Upload to S3 Standard
    if [ "${CLOUD_BACKUP_ENABLED:-false}" = "true" ]; then
      aws s3 cp ${BACKUP_DIR}/weekly/db_${DATE}.sql.gz s3://idrm-backups/weekly/
    fi
    find ${BACKUP_DIR}/weekly -mtime +90 -delete
    ;;
  monthly)
    pg_dump -U $DB_USER -h $DB_HOST $DB_NAME | gzip > ${BACKUP_DIR}/monthly/db_${DATE}.sql.gz
    # Upload to S3 Glacier (cold storage)
    if [ "${CLOUD_BACKUP_ENABLED:-false}" = "true" ]; then
      aws s3 cp ${BACKUP_DIR}/monthly/db_${DATE}.sql.gz \
        s3://idrm-backups/monthly/ --storage-class GLACIER
    fi
    find ${BACKUP_DIR}/monthly -mtime +365 -delete
    ;;
esac

echo "Backup [${BACKUP_TYPE}] complete: ${DATE}"
```

```bash
# Cron schedule (add with: crontab -e)

# Hourly backups
0 * * * * /root/scripts/backup-production.sh hourly

# Daily backup at midnight IST
30 18 * * * /root/scripts/backup-production.sh daily   # 18:30 UTC = midnight IST

# Weekly backup Sunday 1 AM IST
30 19 * * 0 /root/scripts/backup-production.sh weekly  # 19:30 UTC = 1 AM IST

# Monthly backup 1st Sunday 2 AM IST (runs if day 1-7 AND Sunday)
30 20 1-7 * 0 /root/scripts/backup-production.sh monthly
```

**Cloud backup** is opt-in. Set `CLOUD_BACKUP_ENABLED=true` in `/etc/idrm/env.prod` when budget allows (weekly + monthly go to S3, monthly to Glacier). Local-only is safe for the first 6 months.

### 3.8 Rollback Procedure

```bash
#!/bin/bash
# scripts/rollback-production.sh
PREVIOUS_VERSION=$1
if [ -z "$PREVIOUS_VERSION" ]; then echo "Usage: ./rollback-production.sh <version>"; exit 1; fi

export VERSION=$PREVIOUS_VERSION
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d
sleep 30
curl -f https://idrm.example.com/api/health || exit 1
echo "Rollback to $PREVIOUS_VERSION complete!"
```

### 3.9 Production Pre-Launch Checklist

**Infrastructure**:
- [ ] Domain DNS configured and propagated
- [ ] SSL certificates installed and auto-renewal enabled
- [ ] Firewall rules configured (22, 80, 443 only)
- [ ] Database replicas configured
- [ ] Redis cluster configured
- [ ] Backups automated and restore tested
- [ ] Monitoring dashboards live (Prometheus + Grafana)
- [ ] Alerting rules set (CPU > 80%, p95 > 500ms, error rate > 1%)

**Security**:
- [ ] SSH key-only authentication (no password login)
- [ ] Secrets stored in environment (not in code)
- [ ] Database connections SSL-encrypted
- [ ] CORS configured correctly (no wildcard `*` in production)
- [ ] Security headers enabled (HSTS, CSP, X-Frame-Options)
- [ ] Rate limiting tested

**Application**:
- [ ] All environment variables set
- [ ] Database migrations run
- [ ] Seed data applied (if needed)
- [ ] Health endpoint returns 200
- [ ] WebSocket connection verified
- [ ] CI/CD pipeline tested end-to-end
- [ ] Rollback procedure tested

---

## 4. CI/CD Pipeline (GitHub Actions)

### 4.1 Pipeline Overview

```
Push to develop → Staging deploy (automatic)
Push to main   → Production deploy (manual approval required)

Each push triggers:
  Stage 1: Code quality (lint, type check, security scan)
  Stage 2: Tests (unit, integration, E2E)
  Stage 3: Docker builds
  Stage 4: Deploy (staging auto / production manual)
  Stage 5: Smoke tests + Slack notification
```

### 4.2 Backend CI (`.github/workflows/backend-ci.yml`)

```yaml
name: Backend CI
on:
  push:
    branches: [main, develop]
    paths: ['backend/**']
  pull_request:
    paths: ['backend/**']

jobs:
  lint-and-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install tools
        run: pip install black ruff mypy
      - name: Black
        run: black --check backend/
      - name: Ruff
        run: ruff check backend/
      - name: mypy
        run: mypy backend/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready --health-interval 10s --health-timeout 5s --health-retries 5
      redis:
        image: redis:7.2-alpine
        options: >-
          --health-cmd "redis-cli ping" --health-interval 10s
    steps:
      - uses: actions/checkout@v4
      - name: Setup Miniconda
        uses: conda-incubator/setup-miniconda@v3
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          cd src/backend/app-python
          pip install -r requirements.txt pytest pytest-cov
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd src/backend/app-python
          pytest ../../tests/ -v --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: src/backend/app-python/coverage.xml

  build-docker:
    needs: [lint-and-type-check, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/staging/backend.Dockerfile
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
            ghcr.io/${{ github.repository }}/backend:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### 4.3 API Gateway CI (`.github/workflows/api-gateway-ci.yml`)

```yaml
name: API Gateway CI
on:
  push:
    branches: [main, develop]
    paths: ['src/backend/api-gateway/**']
  pull_request:
    paths: ['src/backend/api-gateway/**']

jobs:
  lint-test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
      - name: Install
        run: cd src/backend/api-gateway && bun install
      - name: Lint
        run: cd src/backend/api-gateway && bun run lint
      - name: Type check
        run: cd src/backend/api-gateway && bun run type-check
      - name: Test
        run: cd src/backend/api-gateway && bun test --coverage
      - name: Build Docker
        uses: docker/build-push-action@v5
        if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
        with:
          context: .
          file: docker/staging/api-gateway.Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/api-gateway:${{ github.sha }}
```

### 4.4 Frontend CI (`.github/workflows/frontend-ci.yml`)

```yaml
name: Frontend CI
on:
  push:
    paths: ['src/frontend/**']
  pull_request:
    paths: ['src/frontend/**']

jobs:
  # HTML/Tailwind
  web-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - name: Install, test, build
        run: |
          cd src/frontend/web-html
          bun install
          bun test
          bun run build

  # React SPA
  spa-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - name: Install, lint, type-check, test, build
        run: |
          cd src/frontend/web-react
          bun install
          bun run lint
          bun run type-check
          bun test
          bun run build

  # React Native
  mobile-ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: oven-sh/setup-bun@v1
      - name: Install, lint, test
        run: |
          cd src/frontend/mobile-expo
          bun install
          bun run lint
          bun test
```

### 4.5 Deploy Staging (`.github/workflows/deploy-staging.yml`)

```yaml
name: Deploy to Staging
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to staging
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/idrm
            git pull origin develop
            docker-compose -f docker-compose.staging.yml pull
            docker-compose -f docker-compose.staging.yml up -d
      - name: Smoke test
        run: |
          sleep 30
          curl -f https://staging.idrm.example.com/api/health
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: '{"text": "✅ Staging deployment successful!"}'
```

### 4.6 Deploy Production — Blue-Green (`.github/workflows/deploy-production.yml`)

```yaml
name: Deploy to Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production   # Requires manual approval in GitHub
    steps:
      - uses: actions/checkout@v4
      - name: Deploy blue environment
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/idrm
            export DEPLOYMENT_COLOR=blue
            docker-compose -f docker-compose.blue.yml pull
            docker-compose -f docker-compose.blue.yml up -d
            sleep 60
            curl -f http://blue.idrm.internal/api/health || exit 1
      - name: Switch traffic to blue
        run: |
          aws elbv2 modify-listener \
            --listener-arn ${{ secrets.LB_LISTENER_ARN }} \
            --default-actions Type=forward,TargetGroupArn=${{ secrets.BLUE_TG_ARN }}
      - name: Verify production
        run: |
          sleep 30
          curl -f https://idrm.example.com/api/health
      - name: Notify team
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: '{"text": "🚀 Production deployment successful! Version: ${{ github.sha }}"}'
```

### 4.7 Emergency Rollback (`.github/workflows/rollback.yml`)

```yaml
name: Emergency Rollback
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version SHA to rollback to'
        required: true
      environment:
        description: 'staging or production'
        required: true
        default: 'production'

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Rollback
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/idrm
            export VERSION=${{ github.event.inputs.version }}
            aws elbv2 modify-listener \
              --listener-arn ${{ secrets.LB_LISTENER_ARN }} \
              --default-actions Type=forward,TargetGroupArn=${{ secrets.GREEN_TG_ARN }}
      - name: Verify
        run: |
          sleep 30
          curl -f https://idrm.example.com/api/health
      - name: Notify
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: '{"text": "⚠️ Emergency rollback to ${{ github.event.inputs.version }} complete!"}'
```

### 4.8 Required GitHub Secrets

```
# Staging
STAGING_HOST          staging server IP
STAGING_USER          deploy
STAGING_SSH_KEY       SSH private key

# Production
PROD_HOST             production server IP
PROD_USER             deploy
PROD_SSH_KEY          SSH private key
LB_LISTENER_ARN       AWS load balancer listener ARN
BLUE_TG_ARN           Blue target group ARN
GREEN_TG_ARN          Green target group ARN

# Container Registry
GITHUB_TOKEN          (automatic — GitHub provides this)

# Mobile
EXPO_TOKEN            Expo account token

# Notifications
SLACK_WEBHOOK         Slack incoming webhook URL

# Security Scanning
SNYK_TOKEN            Snyk account token
```

### 4.9 CI/CD Quality Gates

Before any deployment proceeds, all of these must pass:
- Test coverage ≥ 80%
- No critical security vulnerabilities (Trivy/Snyk)
- All linting checks pass (Black, Ruff for Python; ESLint for JS/TS)
- Type checking passes (mypy for Python; tsc for TypeScript)

---

## 5. Mobile App Deployment (Expo)

### 5.1 Staging Build (TestFlight / Internal Testing)

```bash
# Configure staging environment
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

# Build and submit for both platforms
eas build --platform ios --profile staging
eas build --platform android --profile staging
eas submit --platform ios --profile staging
eas submit --platform android --profile staging
```

### 5.2 Production Build

```bash
cd src/frontend/mobile-expo

# iOS → App Store
eas build --platform ios --profile production
eas submit --platform ios --latest

# Android → Play Store
eas build --platform android --profile production
eas submit --platform android --latest

# OTA update (no app store review needed for minor changes)
eas update --branch production --message "Bug fixes and improvements"
```

---

## 6. Troubleshooting

### 6.1 Container Won't Start

```bash
# View logs
docker-compose logs -f <service-name>

# Backend: conda env not found
# → Check that environment.yml is correct and base image is miniconda

# Database: port already in use
# → Kill the process using the port
sudo lsof -i :5432  # find PID
sudo kill <PID>
```

### 6.2 Database Connection Failed

```bash
# Check PostgreSQL is healthy
docker-compose exec postgres pg_isready -U $DB_USER

# Test connection from backend container
docker-compose exec backend env DATABASE_URL=$DATABASE_URL python -c \
  "from sqlalchemy import create_engine; create_engine('$DATABASE_URL').connect(); print('OK')"

# Check DATABASE_URL format
# Correct: postgresql://user:pass@host:5432/dbname
# Common mistake: missing port, or using localhost instead of service name
```

### 6.3 Redis Connection Failed

```bash
docker-compose exec redis redis-cli -a $REDIS_PASSWORD ping
# Expected: PONG
# If failed: check REDIS_PASSWORD matches what redis was started with
```

### 6.4 WebSocket Not Connecting

```bash
# Check Bun gateway is running
docker-compose ps api-gateway
# Check WebSocket port is exposed
docker-compose exec api-gateway netstat -ln | grep 3001
# Check NGINX is proxying WebSocket correctly (Upgrade header must be set)
```

### 6.5 SSL Certificate Issues

```bash
# Renew certificate
certbot renew --dry-run     # Test first
certbot renew               # Actually renew

# Check expiry
openssl x509 -in /etc/letsencrypt/live/<domain>/cert.pem -text -noout | grep "Not After"
```

---

*This guide was merged from: `setup-staging-v3.md`, `setup-production-v3.md`, `production-ci-cd-readme-v3.md`, and `48-COMPLETE-DEPLOYMENT-GUIDE.md` (conceptual sections only).*

*For development setup (running locally without Docker), see [IDRM-DEVELOPMENT-GUIDE.md](./IDRM-DEVELOPMENT-GUIDE.md).*
