> *Type: Guide (novice / how-to) · Audience: DevOps · Status: Archived — v1 historical generation*

# IDRM Platform Setup - Staging Environment (Pre-Production)

<!-- IDRM-CLEANUP doc=v1-g12-staging status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — staging → FFP
> Separate staging/pre-production environments are an **FFP** concern (multi-environment CI/CD) → [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md).
> The MVP runs on a single native Ubuntu server (ADR-006). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

> Docker-based staging environment that mirrors production for integration testing and validation

## 🎯 Goal

Set up a staging environment that:
- Uses Docker containers for all services
- Mirrors production architecture exactly
- Enables thorough testing before production deployment
- Supports continuous integration workflows

## ⚠️ Important Notes

- **This is NOT for development** - Use monolith setup for development
- **This IS for testing** - Pre-production validation and QA
- All services run in Docker containers
- Uses Docker Compose for orchestration

## 📋 Prerequisites

Before starting, complete:
- ✅ `setup-prerequisites.md` - All prerequisites
- ✅ Docker and Docker Compose installed
- ✅ Git repository access
- ✅ Staging server ready (4+ CPU, 16+ GB RAM)

---

## Table of Contents

1. [Server Preparation](#server-preparation)
2. [Project Setup](#project-setup)
3. [Docker Compose Configuration](#docker-compose-configuration)
4. [Environment Configuration](#environment-configuration)
5. [Build and Deploy](#build-and-deploy)
6. [Database Initialization](#database-initialization)
7. [SSL Setup (Optional)](#ssl-setup-optional)
8. [Verification](#verification)
9. [Monitoring](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## Server Preparation

### 1. Update System

```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git ufw fail2ban
```

### 2. Configure Firewall

```bash
# Enable UFW
sudo ufw --force enable

# Allow SSH (CRITICAL - do this first!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Docker API (internal only)
# sudo ufw allow from 172.16.0.0/12 to any port 2375

# Check status
sudo ufw status verbose
```

### 3. Install Fail2Ban

```bash
# Install
sudo apt install -y fail2ban

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local
```

**Update settings**:
```ini
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log
```

```bash
# Restart Fail2Ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban
```

### 4. Create Deployment User

```bash
# Create user
sudo useradd -m -s /bin/bash idrm-deploy
sudo usermod -aG docker idrm-deploy

# Set password
sudo passwd idrm-deploy

# Add to sudoers
echo "idrm-deploy ALL=(ALL) NOPASSWD:ALL" | sudo tee /etc/sudoers.d/idrm-deploy
```

---

## Project Setup

### 1. Clone Repository

```bash
# Switch to deployment user
sudo su - idrm-deploy

# Create project directory
mkdir -p /home/idrm-deploy/idrm-staging
cd /home/idrm-deploy/idrm-staging

# Clone repository (replace with your repo URL)
git clone https://github.com/your-org/idrm-platform.git .

# Or create structure manually
mkdir -p {docker,infrastructure,frontend,backend}
```

### 2. Create Directory Structure

```bash
# Create required directories
mkdir -p docker/{nginx,postgres,redis,geoserver}
mkdir -p infrastructure/{nginx/conf.d,postgres/init,geoserver/data}
mkdir -p logs/{nginx,postgres,api-gateway,services}
mkdir -p data/{postgres,redis,geoserver}
mkdir -p ssl

# Set permissions
chmod -R 755 infrastructure
chmod -R 755 logs
chmod -R 755 data
```

---

## Docker Compose Configuration

### 1. Create Main docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL + PostGIS
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8 --locale=en_US.UTF-8"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./infrastructure/postgres/init:/docker-entrypoint-initdb.d
    networks:
      - idrm-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # DO NOT expose port in production
    # ports:
    #   - "5432:5432"

  # Redis
  redis:
    image: redis:7.2-alpine
    container_name: idrm-redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - ./data/redis:/data
    networks:
      - idrm-network
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # GeoServer
  geoserver:
    image: kartoza/geoserver:2.24.0
    container_name: idrm-geoserver
    restart: unless-stopped
    environment:
      GEOSERVER_ADMIN_USER: ${GEOSERVER_ADMIN_USER}
      GEOSERVER_ADMIN_PASSWORD: ${GEOSERVER_ADMIN_PASSWORD}
      INITIAL_MEMORY: 2G
      MAXIMUM_MEMORY: 4G
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASS: ${DB_PASSWORD}
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
    volumes:
      - ./data/geoserver:/opt/geoserver/data_dir
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/geoserver/web/ || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  # API Gateway (Bun)
  api-gateway:
    build:
      context: ./backend/api-gateway
      dockerfile: Dockerfile
    container_name: idrm-api-gateway
    restart: unless-stopped
    environment:
      NODE_ENV: staging
      PORT: 3000
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME}
      DB_USER: ${DB_USER}
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      JWT_SECRET: ${JWT_SECRET}
      JWT_EXPIRATION: 3600
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
    volumes:
      - ./logs/api-gateway:/app/logs
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Service Management Microservice
  service-management:
    build:
      context: ./backend/services/service-management
      dockerfile: Dockerfile
    container_name: idrm-service-mgmt
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
      SERVICE_PORT: 8000
    volumes:
      - ./logs/services:/app/logs
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Geospatial Microservice
  geospatial-service:
    build:
      context: ./backend/services/geospatial
      dockerfile: Dockerfile
    container_name: idrm-geospatial
    restart: unless-stopped
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      GEOSERVER_URL: http://geoserver:8080/geoserver
      SERVICE_PORT: 8000
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      geoserver:
        condition: service_healthy

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: idrm-frontend
    restart: unless-stopped
    environment:
      VITE_API_URL: ${FRONTEND_API_URL}
      VITE_WS_URL: ${FRONTEND_WS_URL}
      VITE_GEOSERVER_URL: ${FRONTEND_GEOSERVER_URL}
    networks:
      - idrm-network

  # NGINX Reverse Proxy
  nginx:
    image: nginx:1.24-alpine
    container_name: idrm-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/conf.d:/etc/nginx/conf.d
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    networks:
      - idrm-network
    depends_on:
      - api-gateway
      - frontend
      - geoserver

networks:
  idrm-network:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  geoserver_data:
EOF
```

---

## Environment Configuration

### 1. Create .env File

```bash
cat > .env << 'EOF'
# Environment
ENVIRONMENT=staging

# Database
DB_NAME=idrm_staging
DB_USER=idrm_user
DB_PASSWORD=CHANGE_ME_SECURE_PASSWORD_HERE

# Redis
REDIS_PASSWORD=CHANGE_ME_REDIS_PASSWORD

# JWT
JWT_SECRET=CHANGE_ME_RANDOM_64_CHAR_STRING
JWT_EXPIRATION=3600

# GeoServer
GEOSERVER_ADMIN_USER=admin
GEOSERVER_ADMIN_PASSWORD=CHANGE_ME_GEOSERVER_PASSWORD

# CORS
ALLOWED_ORIGINS=http://staging.example.com,https://staging.example.com

# Frontend URLs
FRONTEND_API_URL=http://staging.example.com/api/v1
FRONTEND_WS_URL=ws://staging.example.com
FRONTEND_GEOSERVER_URL=http://staging.example.com/geoserver

# Domain (for SSL)
DOMAIN=staging.example.com
SSL_EMAIL=admin@example.com
EOF

# Generate secure passwords
echo "DB_PASSWORD=$(openssl rand -base64 32)" >> .env.generated
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env.generated
echo "JWT_SECRET=$(openssl rand -hex 64)" >> .env.generated
echo "GEOSERVER_ADMIN_PASSWORD=$(openssl rand -base64 16)" >> .env.generated

# Secure the file
chmod 600 .env
chmod 600 .env.generated

echo "Generated passwords saved to .env.generated"
echo "Copy these to .env file and delete .env.generated"
```

---

## Dockerfiles

### 1. API Gateway Dockerfile

```bash
mkdir -p backend/api-gateway
cat > backend/api-gateway/Dockerfile << 'EOF'
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

RUN echo 'const res = await fetch("http://localhost:3000/health"); process.exit(res.ok ? 0 : 1);' > healthcheck.js

EXPOSE 3000

CMD ["bun", "run", "src/index.js"]
EOF
```

### 2. Python Service Dockerfile

```bash
mkdir -p backend/services/service-management
cat > backend/services/service-management/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev --no-interaction --no-ansi

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
```

### 3. Frontend Dockerfile

```bash
mkdir -p frontend
cat > frontend/Dockerfile << 'EOF'
FROM oven/bun:1 as builder

WORKDIR /app

COPY package.json bun.lockb* ./
RUN bun install --frozen-lockfile

COPY . .
RUN bun run build

FROM nginx:1.24-alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
EOF
```

---

## NGINX Configuration

### 1. Create NGINX Config

```bash
cat > infrastructure/nginx/nginx.conf << 'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    gzip on;

    include /etc/nginx/conf.d/*.conf;
}
EOF
```

### 2. Create Site Config

```bash
cat > infrastructure/nginx/conf.d/idrm-staging.conf << 'EOF'
upstream api_gateway {
    server api-gateway:3000;
}

upstream geoserver {
    server geoserver:8080;
}

server {
    listen 80;
    server_name staging.example.com;

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }

    # API Gateway
    location /api {
        proxy_pass http://api_gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # WebSocket
    location /socket.io {
        proxy_pass http://api_gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
    }

    # GeoServer
    location /geoserver {
        proxy_pass http://geoserver/geoserver;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
```

---

## Database Initialization

### 1. Create Init Script

```bash
cat > infrastructure/postgres/init/01-init.sql << 'EOF'
-- IDRM Staging Database Initialization

-- Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Verify
SELECT PostGIS_Version();

-- Create tables (same as production schema)
-- Include full schema from monolith setup here
EOF
```

---

## Build and Deploy

### 1. Build Docker Images

```bash
# Build all images
docker compose build

# Or build individually
docker compose build api-gateway
docker compose build service-management
docker compose build frontend
```

### 2. Start Services

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f api-gateway
```

### 3. Verify Services

```bash
# Wait for services to be healthy
sleep 30

# Check health
docker compose ps

# All services should show "healthy" status
```

---

## SSL Setup (Optional)

### 1. Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Stop NGINX container temporarily
docker compose stop nginx

# Obtain certificate
sudo certbot certonly --standalone \
  -d staging.example.com \
  --email admin@example.com \
  --agree-tos \
  --non-interactive

# Copy certificates
sudo cp /etc/letsencrypt/live/staging.example.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/staging.example.com/privkey.pem ssl/
sudo chown idrm-deploy:idrm-deploy ssl/*

# Restart NGINX
docker compose start nginx
```

### 2. Update NGINX for HTTPS

```bash
cat > infrastructure/nginx/conf.d/idrm-staging.conf << 'EOF'
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name staging.example.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name staging.example.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Rest of configuration same as HTTP version
    # ...
}
EOF

# Reload NGINX
docker compose exec nginx nginx -s reload
```

---

## Verification

### Complete System Test

```bash
# Test script
cat > test-staging.sh << 'EOF'
#!/bin/bash

echo "Testing IDRM Staging Environment..."

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test PostgreSQL
echo -n "Testing PostgreSQL... "
docker compose exec -T postgres psql -U idrm_user -d idrm_staging -c "SELECT 1" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test Redis
echo -n "Testing Redis... "
docker compose exec -T redis redis-cli -a $REDIS_PASSWORD ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test API Gateway
echo -n "Testing API Gateway... "
curl -s http://localhost:3000/health | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test GeoServer
echo -n "Testing GeoServer... "
curl -s -I http://localhost:8080/geoserver/web/ | grep -q "200"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test NGINX
echo -n "Testing NGINX... "
curl -s -I http://localhost | grep -q "200"
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""
echo "Staging environment test complete!"
EOF

chmod +x test-staging.sh
./test-staging.sh
```

---

## Monitoring

### 1. View Logs

```bash
# All logs
docker compose logs -f

# Specific service
docker compose logs -f api-gateway

# Last 100 lines
docker compose logs --tail=100 postgres

# Since timestamp
docker compose logs --since=2024-01-01T00:00:00
```

### 2. Resource Usage

```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up
docker system prune -a
```

---

## Troubleshooting

### Common Issues

**Issue 1: Container won't start**
```bash
# Check logs
docker compose logs <service-name>

# Restart service
docker compose restart <service-name>

# Rebuild and restart
docker compose up -d --build <service-name>
```

**Issue 2: Database connection failed**
```bash
# Check if postgres is healthy
docker compose ps postgres

# Test connection
docker compose exec postgres psql -U idrm_user -d idrm_staging -c "SELECT 1"

# Check network
docker network inspect idrm-staging_idrm-network
```

**Issue 3: Port conflicts**
```bash
# Find what's using port 80
sudo lsof -i :80

# Stop conflicting service
sudo systemctl stop apache2  # or other service

# Restart NGINX
docker compose restart nginx
```

---

## Maintenance

### Backup

```bash
# Backup database
docker compose exec postgres pg_dump -U idrm_user idrm_staging > backup-$(date +%Y%m%d).sql

# Backup volumes
docker run --rm \
  -v idrm-staging_postgres_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/postgres-data-$(date +%Y%m%d).tar.gz /data
```

### Updates

```bash
# Pull latest images
docker compose pull

# Rebuild
docker compose build

# Restart
docker compose up -d

# Clean old images
docker image prune -a
```

---

**Staging environment ready! Deploy your code and test thoroughly before production! 🚀**
