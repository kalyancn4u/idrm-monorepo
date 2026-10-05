> *Type: Guide (novice / how-to) · Audience: Novices, developers · Status: Archived — v2 historical generation*

# IDRM Complete Setup Guide v2.0

<!-- IDRM-CLEANUP doc=v2-g11-complete status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — setup → current
> MVP setup/run = [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> + [`../../../../guides/mvp/30-contribute-developer-guide.md`](../../../../guides/mvp/30-contribute-developer-guide.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Staging + Production + CI/CD - All-in-One Reference

**Version**: 2.0  
**Stack**: Pure Python (NO Java GeoServer) + Bun + Miniconda  
**Covers**: Staging Setup | Production Setup | CI/CD Pipelines

---

## 📋 Quick Navigation

- [Part 1: Staging Setup (Docker)](#part-1-staging-setup-docker)
- [Part 2: Production Setup (Docker + Security)](#part-2-production-setup-docker--security)
- [Part 3: CI/CD Pipelines](#part-3-cicd-pipelines)

---

# PART 1: Staging Setup (Docker)

## 🎯 Goal

Deploy IDRM in Docker containers for **pre-production testing** with full production parity.

**Key Difference from v1.0**: Uses **Python Geospatial Service** (NOT Java GeoServer)

**Estimated Time**: 1-2 hours

---

## Prerequisites

- [ ] Ubuntu 22.04/24.04 LTS
- [ ] 16+ GB RAM
- [ ] Docker + Docker Compose installed
- [ ] Git installed
- [ ] Completed `setup-prerequisites_v2.md`

---

## Docker Compose Configuration

### docker-compose.staging.yml

```yaml
version: '3.8'

services:
  # ==========================================
  # PostgreSQL + PostGIS
  # ==========================================
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres-staging
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-idrm_db}
      POSTGRES_USER: ${POSTGRES_USER:-idrm_user}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      PGDATA: /var/lib/postgresql/data/pgdata
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d:ro
    networks:
      - idrm-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-idrm_user}"]
      interval: 10s
      timeout: 5s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G

  # ==========================================
  # Redis Cache
  # ==========================================
  redis:
    image: redis:7.2-alpine
    container_name: idrm-redis-staging
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --appendonly yes
    volumes:
      - redis-data:/data
    networks:
      - idrm-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  # ==========================================
  # Python Geospatial Service
  # REPLACES Java GeoServer!
  # ==========================================
  geospatial-service:
    build:
      context: ./backend/services/geospatial
      dockerfile: Dockerfile
    container_name: idrm-geospatial-staging
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER:-idrm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-idrm_db}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      PORT: 8002
      LOG_LEVEL: INFO
    volumes:
      - tile-cache:/var/cache/tiles
      - ./backend/services/geospatial:/app:ro
    networks:
      - idrm-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 1G

  # ==========================================
  # Auth Service (Python/FastAPI)
  # ==========================================
  auth-service:
    build:
      context: ./backend/services/auth
      dockerfile: Dockerfile
    container_name: idrm-auth-staging
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-idrm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-idrm_db}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
      PORT: 8000
    networks:
      - idrm-network
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 15s
      timeout: 5s
      retries: 3

  # ==========================================
  # Service Management (Python/FastAPI)
  # ==========================================
  service-mgmt:
    build:
      context: ./backend/services/service_mgmt
      dockerfile: Dockerfile
    container_name: idrm-service-mgmt-staging
    environment:
      DATABASE_URL: postgresql+asyncpg://${POSTGRES_USER:-idrm_user}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB:-idrm_db}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      PORT: 8001
    networks:
      - idrm-network
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # ==========================================
  # Bun API Gateway
  # ==========================================
  api-gateway:
    build:
      context: ./frontend
      dockerfile: Dockerfile.bun
      args:
        BUN_VERSION: 1.0.0
    container_name: idrm-api-gateway-staging
    environment:
      PORT: 3000
      AUTH_SERVICE_URL: http://auth-service:8000
      SERVICE_MGMT_URL: http://service-mgmt:8001
      GEOSPATIAL_URL: http://geospatial-service:8002
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379/0
      JWT_SECRET_KEY: ${JWT_SECRET_KEY}
    networks:
      - idrm-network
    depends_on:
      - auth-service
      - service-mgmt
      - geospatial-service
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 15s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 512M

  # ==========================================
  # NGINX Reverse Proxy
  # ==========================================
  nginx:
    image: nginx:1.24-alpine
    container_name: idrm-nginx-staging
    volumes:
      - ./nginx/staging.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
      - nginx-logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - idrm-network
    depends_on:
      - api-gateway
      - geospatial-service
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "nginx", "-t"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 256M

volumes:
  postgres-data:
  redis-data:
  tile-cache:
  nginx-logs:

networks:
  idrm-network:
    driver: bridge
```

---

## Dockerfiles

### 1. Python Geospatial Service

**backend/services/geospatial/Dockerfile**:

```dockerfile
FROM python:3.11-slim

# Install system dependencies for GDAL
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create cache directory
RUN mkdir -p /var/cache/tiles

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

# Expose port
EXPOSE 8002

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
```

**requirements.txt**:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
geopandas==0.14.1
shapely==2.0.2
fiona==1.9.5
pyproj==3.6.1
sqlalchemy==2.0.23
geoalchemy2==0.14.2
psycopg2-binary==2.9.9
redis==5.0.1
pillow==10.1.0
mercantile==1.2.1
python-dotenv==1.0.0
```

---

### 2. Bun API Gateway

**frontend/Dockerfile.bun**:

```dockerfile
FROM oven/bun:1.0.0-slim

WORKDIR /app

# Copy package files
COPY package.json bun.lockb ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source
COPY . .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Expose port
EXPOSE 3000

# Run application
CMD ["bun", "run", "src/index.ts"]
```

---

## NGINX Configuration

**nginx/staging.conf**:

```nginx
upstream api_gateway {
    least_conn;
    server api-gateway:3000;
}

upstream geospatial_service {
    server geospatial-service:8002;
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=10r/m;

server {
    listen 80;
    server_name _;

    client_max_body_size 20M;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # API Gateway
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://api_gateway/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    # Python Geospatial Service
    # REPLACES /geoserver/ from old stack!
    location /geo/ {
        proxy_pass http://geospatial_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # Cache tiles
        proxy_cache_valid 200 1h;
        proxy_cache_bypass $http_pragma;
    }

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
}
```

---

## Environment File

**.env.staging**:

```bash
# Generate these securely!
# openssl rand -base64 32

POSTGRES_DB=idrm_db
POSTGRES_USER=idrm_user
POSTGRES_PASSWORD=staging_db_password_CHANGE_ME

REDIS_PASSWORD=staging_redis_password_CHANGE_ME

JWT_SECRET_KEY=staging_jwt_secret_CHANGE_ME_use_openssl_rand_hex_64
```

---

## Deployment Steps

```bash
# 1. Clone repository
git clone https://github.com/your-org/idrm-mvp.git
cd idrm-mvp

# 2. Create environment file
cp .env.staging.example .env.staging
# Edit with secure passwords
nano .env.staging

# 3. Build images
docker compose -f docker-compose.staging.yml build

# 4. Start services
docker compose -f docker-compose.staging.yml up -d

# 5. Check status
docker compose -f docker-compose.staging.yml ps

# 6. View logs
docker compose -f docker-compose.staging.yml logs -f

# 7. Run migrations
docker compose -f docker-compose.staging.yml exec auth-service \
    alembic upgrade head

# 8. Verify services
curl http://localhost/api/health
curl http://localhost/geo/health
```

---

# PART 2: Production Setup (Docker + Security)

## 🎯 Goal

Deploy IDRM securely in production with SSL, firewall, and monitoring.

**Estimated Time**: 3-4 hours

---

## Additional Requirements

- [ ] Domain name registered
- [ ] DNS configured
- [ ] Email for SSL certificates
- [ ] 32+ GB RAM server
- [ ] Backup storage planned

---

## Security Hardening

### 1. Firewall Setup (UFW)

```bash
# Enable firewall
sudo ufw --force enable

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (restrict to your IP)
sudo ufw allow from YOUR_IP to any port 22 proto tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable
sudo ufw enable

# Check status
sudo ufw status numbered
```

---

### 2. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run

# Auto-renewal is set up via systemd timer
sudo systemctl status certbot.timer
```

---

### 3. Production NGINX Configuration

**nginx/production.conf**:

```nginx
# HTTP -> HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=100r/m;
    
    # API Gateway
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://api-gateway:3000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Geospatial Service
    location /geo/ {
        proxy_pass http://geospatial-service:8002/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_cache_valid 200 1h;
    }

    # Frontend
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
    }
}
```

---

### 4. Fail2Ban Configuration

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Configure for NGINX
sudo tee /etc/fail2ban/jail.local << 'EOF'
[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
EOF

# Restart Fail2Ban
sudo systemctl restart fail2ban

# Check status
sudo fail2ban-client status
```

---

### 5. Automated Backups

**scripts/backup.sh**:

```bash
#!/bin/bash
# IDRM Production Backup Script

BACKUP_DIR="/var/backups/idrm"
DATE=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://your-backup-bucket"  # Optional

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker compose -f docker-compose.production.yml exec -T postgres \
    pg_dump -U idrm_user idrm_db | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Backup volumes
docker run --rm \
    -v idrm_postgres-data:/data \
    -v $BACKUP_DIR:/backup \
    alpine tar czf /backup/volumes_$DATE.tar.gz /data

# Optional: Upload to S3
# aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz $S3_BUCKET/

# Keep only last 30 days
find $BACKUP_DIR -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Setup cron**:
```bash
# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /path/to/scripts/backup.sh >> /var/log/idrm-backup.log 2>&1
```

---

# PART 3: CI/CD Pipelines

## 🎯 Goal

Automate testing, building, and deployment.

---

## GitHub Actions

**.github/workflows/ci-cd.yml**:

```yaml
name: IDRM CI/CD Pipeline

on:
  push:
    branches: [ main, staging ]
  pull_request:
    branches: [ main ]

jobs:
  # ==========================================
  # Linting & Code Quality
  # ==========================================
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Python linting
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install Python linting tools
        run: |
          pip install black flake8 mypy
      
      - name: Run Black
        run: black --check backend/
      
      - name: Run Flake8
        run: flake8 backend/ --max-line-length=100
      
      # Bun linting
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
      
      - name: Install dependencies
        run: cd frontend && bun install
      
      - name: Lint TypeScript
        run: cd frontend && bun run lint

  # ==========================================
  # Backend Tests
  # ==========================================
  test-backend:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7.2-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:test@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ -v --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  # ==========================================
  # Frontend Tests
  # ==========================================
  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
      
      - name: Install dependencies
        run: cd frontend && bun install
      
      - name: Run tests
        run: cd frontend && bun test

  # ==========================================
  # Build Docker Images
  # ==========================================
  build:
    needs: [lint, test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Build and push geospatial service
        uses: docker/build-push-action@v4
        with:
          context: ./backend/services/geospatial
          push: true
          tags: ghcr.io/${{ github.repository }}/geospatial:latest
      
      - name: Build and push API gateway
        uses: docker/build-push-action@v4
        with:
          context: ./frontend
          file: ./frontend/Dockerfile.bun
          push: true
          tags: ghcr.io/${{ github.repository }}/api-gateway:latest

  # ==========================================
  # Deploy to Staging
  # ==========================================
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/staging'
    
    steps:
      - name: Deploy to staging server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /opt/idrm
            git pull origin staging
            docker compose -f docker-compose.staging.yml pull
            docker compose -f docker-compose.staging.yml up -d
            docker compose -f docker-compose.staging.yml exec -T auth-service alembic upgrade head

  # ==========================================
  # Deploy to Production
  # ==========================================
  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    
    steps:
      - name: Deploy to production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/idrm
            git pull origin main
            docker compose -f docker-compose.production.yml pull
            docker compose -f docker-compose.production.yml up -d --no-deps --build
            docker compose -f docker-compose.production.yml exec -T auth-service alembic upgrade head
```

---

## GitLab CI/CD

**.gitlab-ci.yml**:

```yaml
stages:
  - lint
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: ""

# ==========================================
# Linting
# ==========================================
lint:python:
  stage: lint
  image: python:3.11
  script:
    - pip install black flake8
    - black --check backend/
    - flake8 backend/ --max-line-length=100

lint:typescript:
  stage: lint
  image: oven/bun:latest
  script:
    - cd frontend
    - bun install
    - bun run lint

# ==========================================
# Testing
# ==========================================
test:backend:
  stage: test
  image: python:3.11
  services:
    - name: postgis/postgis:16-3.4
      alias: postgres
    - name: redis:7.2-alpine
      alias: redis
  variables:
    POSTGRES_DB: test_db
    POSTGRES_PASSWORD: test
    DATABASE_URL: postgresql://postgres:test@postgres:5432/test_db
    REDIS_URL: redis://redis:6379/0
  script:
    - pip install -r backend/requirements.txt pytest pytest-cov
    - cd backend
    - pytest tests/ -v --cov=.
  coverage: '/TOTAL.*\s+(\d+%)$/'

test:frontend:
  stage: test
  image: oven/bun:latest
  script:
    - cd frontend
    - bun install
    - bun test

# ==========================================
# Build
# ==========================================
build:images:
  stage: build
  image: docker:latest
  services:
    - docker:dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - docker build -t $CI_REGISTRY_IMAGE/geospatial:$CI_COMMIT_SHORT_SHA ./backend/services/geospatial
    - docker push $CI_REGISTRY_IMAGE/geospatial:$CI_COMMIT_SHORT_SHA
    - docker build -t $CI_REGISTRY_IMAGE/api-gateway:$CI_COMMIT_SHORT_SHA -f ./frontend/Dockerfile.bun ./frontend
    - docker push $CI_REGISTRY_IMAGE/api-gateway:$CI_COMMIT_SHORT_SHA
  only:
    - main
    - staging

# ==========================================
# Deploy Staging
# ==========================================
deploy:staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$STAGING_SSH_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
  script:
    - ssh -o StrictHostKeyChecking=no $STAGING_USER@$STAGING_HOST "
        cd /opt/idrm &&
        git pull origin staging &&
        docker compose -f docker-compose.staging.yml pull &&
        docker compose -f docker-compose.staging.yml up -d &&
        docker compose -f docker-compose.staging.yml exec -T auth-service alembic upgrade head
      "
  only:
    - staging
  environment:
    name: staging
    url: https://staging.idrm.example.com

# ==========================================
# Deploy Production
# ==========================================
deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$PROD_SSH_KEY" | tr -d '\r' | ssh-add -
  script:
    - ssh -o StrictHostKeyChecking=no $PROD_USER@$PROD_HOST "
        cd /opt/idrm &&
        git pull origin main &&
        docker compose -f docker-compose.production.yml pull &&
        docker compose -f docker-compose.production.yml up -d --no-deps &&
        docker compose -f docker-compose.production.yml exec -T auth-service alembic upgrade head
      "
  only:
    - main
  when: manual
  environment:
    name: production
    url: https://idrm.example.com
```

---

## Summary Checklist

### Staging ✅
- [ ] Docker Compose with Python geospatial (NO GeoServer)
- [ ] All 6 services containerized
- [ ] NGINX configured for `/geo/` endpoint
- [ ] Health checks on all services
- [ ] Integration tests passing

### Production ✅
- [ ] SSL certificate obtained
- [ ] Firewall (UFW) configured
- [ ] Fail2Ban enabled
- [ ] Automated backups scheduled
- [ ] Monitoring planned
- [ ] Zero-downtime deployment ready

### CI/CD ✅
- [ ] Linting configured (Black, Flake8 for Python)
- [ ] Tests automated (pytest, bun test)
- [ ] Docker builds automated
- [ ] Staging deployment automated
- [ ] Production deployment (manual approval)
- [ ] Coverage reports generated

---

**All setup guides complete! Ready for deployment! 🚀**
