> *Type: Document (specification) · Audience: DevOps · Status: Archived — v2 historical generation*

# IDRM CI/CD Pipeline Guide v2.0

<!-- IDRM-CLEANUP doc=v2-80-cicd status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — CI/CD = FFP
> CI/CD pipelines are **FFP** — MVP deploys natively via systemd (ADR-006), [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md);
> FFP automation → [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Automated Testing, Building, and Deployment

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Stack**: Bun + pytest + Docker + GitHub Actions / GitLab CI

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [GitHub Actions Setup](#github-actions-setup)
3. [GitLab CI Setup](#gitlab-ci-setup)
4. [Manual Deployment](#manual-deployment)
5. [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### CI/CD Pipeline Stages

```
┌─────────────┐
│   COMMIT    │
└──────┬──────┘
       ↓
┌─────────────┐
│   1. LINT   │  ← Black, Flake8, Bun lint
└──────┬──────┘
       ↓
┌─────────────┐
│  2. TEST    │  ← pytest, bun test
└──────┬──────┘
       ↓
┌─────────────┐
│  3. BUILD   │  ← Docker images
└──────┬──────┘
       ↓
┌─────────────┐
│ 4. STAGING  │  ← Auto-deploy to staging
└──────┬──────┘
       ↓
┌─────────────┐
│5. PRODUCTION│  ← Manual approval
└─────────────┘
```

### Key Changes from v1.0

**REMOVED** ❌:
- npm/Node.js commands
- Java/GeoServer build steps
- Python venv setup

**ADDED** ✅:
- Bun commands for frontend
- pytest for Python testing
- Python geospatial service builds
- Miniconda cache

---

## 🚀 GitHub Actions Setup

### File Structure

```
.github/
└── workflows/
    ├── ci-cd.yml          # Main pipeline
    ├── pr-check.yml       # PR validation
    └── nightly.yml        # Nightly tests
```

---

### Main CI/CD Pipeline

**.github/workflows/ci-cd.yml**:

```yaml
name: IDRM CI/CD Pipeline

on:
  push:
    branches: [main, staging, develop]
  pull_request:
    branches: [main, staging]
  workflow_dispatch:

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # ==========================================
  # CODE QUALITY - Linting
  # ==========================================
  lint:
    name: Code Quality Checks
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      # Python linting
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install Python linting tools
        run: |
          pip install black==23.11.0 flake8==6.1.0 mypy==1.7.0
      
      - name: Run Black (Python formatter)
        run: |
          black --check backend/
      
      - name: Run Flake8 (Python linter)
        run: |
          flake8 backend/ --max-line-length=100 --exclude=__pycache__,migrations
      
      - name: Run MyPy (Type checking)
        run: |
          mypy backend/ --ignore-missing-imports
        continue-on-error: true
      
      # Bun linting (TypeScript)
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
      
      - name: Install Bun dependencies
        working-directory: ./frontend
        run: bun install --frozen-lockfile
      
      - name: Lint TypeScript
        working-directory: ./frontend
        run: bun run lint
      
      - name: Check TypeScript types
        working-directory: ./frontend
        run: bun run type-check
        continue-on-error: true

  # ==========================================
  # BACKEND TESTS - Python/FastAPI
  # ==========================================
  test-backend:
    name: Backend Tests (Python)
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgis/postgis:16-3.4
        env:
          POSTGRES_DB: test_db
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      
      redis:
        image: redis:7.2-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y gdal-bin libgdal-dev
      
      - name: Install Python dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-asyncio pytest-cov pytest-xdist
      
      - name: Run pytest
        env:
          DATABASE_URL: postgresql+asyncpg://test_user:test_password@localhost:5432/test_db
          DATABASE_URL_SYNC: postgresql://test_user:test_password@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
          JWT_SECRET_KEY: test_secret_key_for_ci
        run: |
          cd backend
          pytest tests/ \
            -v \
            --cov=. \
            --cov-report=xml \
            --cov-report=html \
            --cov-report=term \
            -n auto
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
          flags: backend
          name: backend-coverage
      
      - name: Upload coverage artifacts
        uses: actions/upload-artifact@v3
        with:
          name: backend-coverage
          path: backend/htmlcov/

  # ==========================================
  # FRONTEND TESTS - Bun/TypeScript
  # ==========================================
  test-frontend:
    name: Frontend Tests (Bun)
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
      
      - name: Install dependencies
        working-directory: ./frontend
        run: bun install --frozen-lockfile
      
      - name: Run Bun tests
        working-directory: ./frontend
        run: bun test --coverage
      
      - name: Build frontend (HTML/Tailwind)
        working-directory: ./frontend/html-tailwind
        run: bun run build
      
      - name: Build frontend (React SPA)
        working-directory: ./frontend/react-spa
        run: bun run build

  # ==========================================
  # SECURITY SCANNING
  # ==========================================
  security:
    name: Security Scanning
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

  # ==========================================
  # BUILD DOCKER IMAGES
  # ==========================================
  build:
    name: Build Docker Images
    runs-on: ubuntu-latest
    needs: [lint, test-backend, test-frontend]
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'
    
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service:
          - name: geospatial-service
            context: ./backend/services/geospatial
            dockerfile: Dockerfile
          - name: auth-service
            context: ./backend/services/auth
            dockerfile: Dockerfile
          - name: service-mgmt
            context: ./backend/services/service_mgmt
            dockerfile: Dockerfile
          - name: api-gateway
            context: ./frontend
            dockerfile: Dockerfile.bun
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Log in to Container Registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/${{ matrix.service.name }}
          tags: |
            type=ref,event=branch
            type=sha,prefix={{branch}}-
            type=semver,pattern={{version}}
      
      - name: Build and push Docker image
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.service.context }}
          file: ${{ matrix.service.context }}/${{ matrix.service.dockerfile }}
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # ==========================================
  # DEPLOY TO STAGING
  # ==========================================
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/staging'
    environment:
      name: staging
      url: https://staging.yourdomain.com
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Deploy to staging server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          port: ${{ secrets.STAGING_PORT }}
          script: |
            cd /opt/idrm
            git fetch origin staging
            git checkout staging
            git pull origin staging
            
            # Pull latest images
            docker compose -f docker-compose.staging.yml pull
            
            # Run migrations
            docker compose -f docker-compose.staging.yml up -d postgres redis
            sleep 10
            docker compose -f docker-compose.staging.yml exec -T auth-service \
              alembic upgrade head
            
            # Deploy services
            docker compose -f docker-compose.staging.yml up -d --no-deps
            
            # Health check
            sleep 20
            curl -f http://localhost/api/health || exit 1
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        if: always()
        with:
          status: ${{ job.status }}
          text: 'Staging deployment ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  # ==========================================
  # DEPLOY TO PRODUCTION
  # ==========================================
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [build]
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://yourdomain.com
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Deploy to production server
        uses: appleboy/ssh-action@v1.0.0
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          port: ${{ secrets.PROD_PORT }}
          script: |
            cd /opt/idrm
            git fetch origin main
            git checkout main
            git pull origin main
            
            # Create backup
            /opt/idrm/scripts/backup-production.sh
            
            # Pull latest images
            docker compose -f docker-compose.production.yml pull
            
            # Run migrations (with backup)
            docker compose -f docker-compose.production.yml exec -T postgres \
              pg_dump -U idrm_prod_user idrm_production > /tmp/pre_migration_backup.sql
            docker compose -f docker-compose.production.yml exec -T auth-service \
              alembic upgrade head
            
            # Zero-downtime deployment
            /opt/idrm/scripts/deploy-production.sh
            
            # Verify deployment
            sleep 30
            curl -f https://yourdomain.com/api/health || exit 1
      
      - name: Notify deployment
        uses: 8398a7/action-slack@v3
        if: always()
        with:
          status: ${{ job.status }}
          text: 'Production deployment ${{ job.status }}'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

### PR Check Workflow

**.github/workflows/pr-check.yml**:

```yaml
name: Pull Request Checks

on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  pr-checks:
    name: PR Quality Checks
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Check PR title
        run: |
          PR_TITLE="${{ github.event.pull_request.title }}"
          if ! echo "$PR_TITLE" | grep -qE '^(feat|fix|docs|style|refactor|perf|test|chore):'; then
            echo "PR title must start with: feat|fix|docs|style|refactor|perf|test|chore:"
            exit 1
          fi
      
      - name: Check for breaking changes
        run: |
          git diff origin/main...HEAD --name-only | grep -E '(docker-compose|Dockerfile|requirements\.txt)' && \
          echo "::warning::This PR modifies infrastructure files" || true
      
      - name: Run all tests
        uses: ./.github/workflows/ci-cd.yml
        with:
          skip-deploy: true
```

---

## 🦊 GitLab CI Setup

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
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"
  POSTGRES_DB: test_db
  POSTGRES_USER: test_user
  POSTGRES_PASSWORD: test_password

# Cache configuration
cache:
  paths:
    - .cache/pip
    - node_modules/
    - frontend/node_modules/

# ==========================================
# LINTING STAGE
# ==========================================
lint:python:
  stage: lint
  image: python:3.11-slim
  before_script:
    - pip install black flake8 mypy
  script:
    - black --check backend/
    - flake8 backend/ --max-line-length=100
    - mypy backend/ --ignore-missing-imports
  allow_failure: false

lint:typescript:
  stage: lint
  image: oven/bun:latest
  before_script:
    - cd frontend
    - bun install --frozen-lockfile
  script:
    - bun run lint
    - bun run type-check
  allow_failure: false

# ==========================================
# TESTING STAGE
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
    DATABASE_URL: postgresql+asyncpg://test_user:test_password@postgres:5432/test_db
    DATABASE_URL_SYNC: postgresql://test_user:test_password@postgres:5432/test_db
    REDIS_URL: redis://redis:6379/0
    JWT_SECRET_KEY: test_secret
  before_script:
    - apt-get update && apt-get install -y gdal-bin libgdal-dev
    - pip install -r backend/requirements.txt pytest pytest-cov pytest-asyncio
  script:
    - cd backend
    - pytest tests/ -v --cov=. --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml
    paths:
      - backend/coverage.xml
    expire_in: 1 week

test:frontend:
  stage: test
  image: oven/bun:latest
  before_script:
    - cd frontend
    - bun install --frozen-lockfile
  script:
    - bun test --coverage
    - bun run build
  artifacts:
    paths:
      - frontend/dist/
    expire_in: 1 week

# ==========================================
# BUILD STAGE
# ==========================================
build:geospatial:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd backend/services/geospatial
    - docker build -t $CI_REGISTRY_IMAGE/geospatial:$CI_COMMIT_SHORT_SHA .
    - docker tag $CI_REGISTRY_IMAGE/geospatial:$CI_COMMIT_SHORT_SHA $CI_REGISTRY_IMAGE/geospatial:latest
    - docker push $CI_REGISTRY_IMAGE/geospatial:$CI_COMMIT_SHORT_SHA
    - docker push $CI_REGISTRY_IMAGE/geospatial:latest
  only:
    - main
    - staging

build:auth:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd backend/services/auth
    - docker build -t $CI_REGISTRY_IMAGE/auth:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE/auth:$CI_COMMIT_SHORT_SHA
  only:
    - main
    - staging

build:api-gateway:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd frontend
    - docker build -f Dockerfile.bun -t $CI_REGISTRY_IMAGE/api-gateway:$CI_COMMIT_SHORT_SHA .
    - docker push $CI_REGISTRY_IMAGE/api-gateway:$CI_COMMIT_SHORT_SHA
  only:
    - main
    - staging

# ==========================================
# DEPLOY STAGE
# ==========================================
deploy:staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client curl
    - eval $(ssh-agent -s)
    - echo "$STAGING_SSH_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan -H $STAGING_HOST >> ~/.ssh/known_hosts
  script:
    - |
      ssh $STAGING_USER@$STAGING_HOST << 'EOF'
        cd /opt/idrm
        git fetch origin staging
        git checkout staging
        git pull origin staging
        docker compose -f docker-compose.staging.yml pull
        docker compose -f docker-compose.staging.yml up -d
        docker compose -f docker-compose.staging.yml exec -T auth-service alembic upgrade head
        
        # Health check
        sleep 20
        curl -f http://localhost/api/health || exit 1
      EOF
  only:
    - staging
  environment:
    name: staging
    url: https://staging.yourdomain.com

deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client curl
    - eval $(ssh-agent -s)
    - echo "$PROD_SSH_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan -H $PROD_HOST >> ~/.ssh/known_hosts
  script:
    - |
      ssh $PROD_USER@$PROD_HOST << 'EOF'
        cd /opt/idrm
        
        # Backup before deployment
        /opt/idrm/scripts/backup-production.sh
        
        # Pull latest code
        git fetch origin main
        git checkout main
        git pull origin main
        
        # Deploy with zero downtime
        /opt/idrm/scripts/deploy-production.sh
        
        # Verify
        sleep 30
        curl -f https://yourdomain.com/api/health || exit 1
      EOF
  only:
    - main
  when: manual
  environment:
    name: production
    url: https://yourdomain.com
```

---

## 🔧 Manual Deployment

### Deployment Scripts

**scripts/deploy-staging.sh**:

```bash
#!/bin/bash
# Manual staging deployment

set -e

echo "Deploying to STAGING..."

cd /opt/idrm
git fetch origin staging
git checkout staging
git pull origin staging

# Build and start
docker compose -f docker-compose.staging.yml build --no-cache
docker compose -f docker-compose.staging.yml up -d

# Migrations
docker compose -f docker-compose.staging.yml exec -T auth-service \
    alembic upgrade head

# Health check
sleep 30
curl -f http://localhost/api/health || exit 1
curl -f http://localhost/geo/health || exit 1

echo "Staging deployment complete!"
```

---

**scripts/deploy-production.sh** (Zero-downtime):

```bash
#!/bin/bash
# Production zero-downtime deployment

set -e

echo "Starting production deployment..."

cd /opt/idrm

# Backup
echo "Creating backup..."
/opt/idrm/scripts/backup-production.sh

# Pull code
echo "Pulling latest code..."
git fetch origin main
git checkout main
git pull origin main

# Build images
echo "Building images..."
docker compose -f docker-compose.production.yml build

# Migrations (with backup)
echo "Running migrations..."
docker compose -f docker-compose.production.yml exec -T postgres \
    pg_dump -U idrm_prod_user idrm_production > /tmp/pre_migration_$(date +%Y%m%d_%H%M%S).sql
docker compose -f docker-compose.production.yml exec -T auth-service \
    alembic upgrade head

# Rolling update (zero-downtime)
echo "Updating services..."
SERVICES="geospatial-service auth-service service-mgmt analytics notifications api-gateway"

for service in $SERVICES; do
    echo "Updating $service..."
    docker compose -f docker-compose.production.yml up -d --no-deps --build $service
    
    # Wait for health check
    sleep 15
    
    # Verify service health
    docker compose -f docker-compose.production.yml ps $service | grep "Up" || exit 1
done

# Reload NGINX
echo "Reloading NGINX..."
docker compose -f docker-compose.production.yml exec nginx nginx -s reload

# Final health check
echo "Verifying deployment..."
sleep 30
curl -f https://yourdomain.com/api/health || exit 1
curl -f https://yourdomain.com/geo/health || exit 1

echo "Production deployment complete!"
echo "Version: $(git describe --tags --always)"
```

---

## 📊 Monitoring CI/CD

### GitHub Actions Dashboard

```
https://github.com/your-org/idrm-mvp/actions
```

### GitLab CI Dashboard

```
https://gitlab.com/your-org/idrm-mvp/-/pipelines
```

### Slack Notifications

Add webhook to GitHub/GitLab for notifications:

```yaml
# GitHub Actions
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}

# GitLab CI
after_script:
  - 'curl -X POST -H "Content-type: application/json" 
     --data "{\"text\":\"Deployment: $CI_JOB_STATUS\"}" 
     $SLACK_WEBHOOK_URL'
```

---

## 🐛 Troubleshooting

### Issue 1: Tests Fail on CI but Pass Locally

**Cause**: Environment differences

**Solution**:
```bash
# Run tests with CI environment
docker run --rm \
    -e DATABASE_URL=postgresql://test:test@localhost/test \
    -e REDIS_URL=redis://localhost:6379 \
    python:3.11 \
    pytest tests/

# Match CI Python version exactly
```

---

### Issue 2: Docker Build Fails

**Cause**: Cache issues or network timeout

**Solution**:
```bash
# Clear Docker cache
docker builder prune -af

# Build with no cache
docker build --no-cache -t myimage .

# Increase timeout
docker build --network=host -t myimage .
```

---

### Issue 3: Deployment Fails on Migration

**Cause**: Breaking database changes

**Solution**:
```bash
# Always test migrations in staging first
docker compose -f docker-compose.staging.yml exec auth-service \
    alembic upgrade head

# If fails, create rollback migration
alembic downgrade -1
```

---

### Issue 4: Secrets Not Available

**GitHub**:
```
Settings → Secrets and variables → Actions → New repository secret
```

**GitLab**:
```
Settings → CI/CD → Variables → Add variable
```

Required secrets:
- `STAGING_HOST`, `STAGING_USER`, `STAGING_SSH_KEY`
- `PROD_HOST`, `PROD_USER`, `PROD_SSH_KEY`
- `SLACK_WEBHOOK` (optional)

---

## ✅ CI/CD Checklist

### Initial Setup ✅
- [ ] GitHub Actions / GitLab CI configured
- [ ] Secrets added
- [ ] Test pipeline on feature branch
- [ ] Staging deployment verified
- [ ] Production deployment verified

### Ongoing ✅
- [ ] All tests passing
- [ ] Coverage > 80%
- [ ] No security vulnerabilities
- [ ] Staging deployments automatic
- [ ] Production deployments manual
- [ ] Notifications working

---

**CI/CD pipeline complete! 🎉**

**Next**: Set up monitoring and alerts
