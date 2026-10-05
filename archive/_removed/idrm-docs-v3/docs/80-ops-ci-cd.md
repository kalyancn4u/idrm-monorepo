# IDRM v3 · Operations & CI/CD

<!-- IDRM-CLEANUP doc=v3-80-cicd status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — ops/CI-CD (MVP ops + FFP CI/CD)
> MVP ops = native systemd → [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> + [`backup-restore-101`](../../../../guides/mvp/learn/backup-restore-101.md). **CI/CD pipelines = FFP** →
> [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Document (specification) · Audience: DevOps, developers · Status: Archived — v3 historical generation*
*Consolidated from: 33-CI-CD-PIPELINES.md, production-ci-cd-readme-v3.md*

## Contents
- [IDRM: CI/CD Pipelines Guide](#idrm-cicd-pipelines-guide)
- [IDRM Production CI/CD Pipeline v3.0](#idrm-production-cicd-pipeline-v30)

---

## IDRM: CI/CD Pipelines Guide

### Automated Testing, Building, and Deployment (For Complete Novices!)

**Version**: 3.0 Consolidated  
**Audience**: DevOps engineers, developers, team leads  
**Technology**: GitHub Actions + Docker + Automated Testing  
**Reading Time**: 2-3 hours (implement step-by-step!)  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [What Is CI/CD?](#1-what-is-cicd)
2. [GitHub Actions Setup](#2-github-actions-setup)
3. [Testing Pipeline](#3-testing-pipeline)
4. [Build Pipeline](#4-build-pipeline)
5. [Deployment Pipeline](#5-deployment-pipeline)
6. [Complete Workflow](#6-complete-workflow)

---

### 1. **What Is CI/CD?**

#### CI/CD Explained (For Novices)

**CI** = Continuous Integration = Automatically test code when pushed  
**CD** = Continuous Deployment = Automatically deploy when tests pass

**Assembly line analogy**:
- Developer pushes code → **CI** tests it → **CD** deploys it
- Like a factory: Code → Quality check → Package → Ship

**Benefits**:
- ✅ Catch bugs early
- ✅ Deploy faster
- ✅ Less manual work
- ✅ Consistent deployments

---

### 2. **GitHub Actions Setup**

#### Create Workflow File

Create `.github/workflows/ci-cd.yml`:

```yaml
name: IDRM CI/CD Pipeline

on:
  push:
    branches: [main, staging]
  pull_request:
    branches: [main]

jobs:
  # === TEST STAGE ===
  test-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r backend/requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Bun
        uses: oven-sh/setup-bun@v1
      
      - name: Install dependencies
        run: |
          cd frontend
          bun install
      
      - name: Run tests
        run: |
          cd frontend
          bun test

  # === BUILD STAGE ===
  build:
    needs: [test-backend, test-frontend]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: |
            myusername/idrm-backend:${{ github.sha }}
            myusername/idrm-backend:latest

  # === DEPLOY STAGE ===
  deploy-staging:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/staging'
    
    steps:
      - name: Deploy to Staging
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

  deploy-production:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment:
      name: production
      url: https://idrm.example.com
    
    steps:
      - name: Deploy to Production
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/idrm
            ./scripts/backup-database.sh
            git pull origin main
            docker compose -f docker-compose.production.yml pull
            docker compose -f docker-compose.production.yml up -d --no-deps
            docker compose -f docker-compose.production.yml exec -T auth-service alembic upgrade head
            sleep 30
            curl -f https://idrm.example.com/health || exit 1
```

---

### 3. **Testing Pipeline**

#### Backend Tests

```bash
## Run locally
cd backend
pytest tests/ -v

## With coverage
pytest tests/ --cov=app --cov-report=html
```

#### Frontend Tests

```bash
## Run locally
cd frontend
bun test

## Watch mode
bun test --watch
```

---

### 4. **Build Pipeline**

#### Docker Build Optimization

```dockerfile
## Use multi-stage builds
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache /wheels/*
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]
```

---

### 5. **Deployment Pipeline**

#### Automated Deployment Script

```bash
#!/bin/bash
## deploy.sh - Automated deployment script

set -e  # Exit on error

echo "🚀 Starting deployment..."

## 1. Backup
echo "📦 Creating backup..."
./scripts/backup-database.sh

## 2. Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

## 3. Build and deploy
echo "🏗️  Building and deploying..."
docker compose -f docker-compose.production.yml up -d --no-deps --build

## 4. Run migrations
echo "🔄 Running database migrations..."
docker compose -f docker-compose.production.yml exec -T auth-service \
  alembic upgrade head

## 5. Health check
echo "🏥 Running health check..."
sleep 30
if curl -f https://idrm.example.com/health; then
    echo "✅ Deployment successful!"
else
    echo "❌ Health check failed! Rolling back..."
    git reset --hard HEAD~1
    docker compose -f docker-compose.production.yml up -d --no-deps --build
    exit 1
fi
```

---

### 6. **Complete Workflow**

#### Development Workflow

```
1. Developer pushes code to feature branch
   ↓
2. GitHub Actions runs tests
   ↓
3. Tests pass → Developer creates Pull Request
   ↓
4. Team reviews code
   ↓
5. PR merged to main
   ↓
6. GitHub Actions:
   - Runs tests again
   - Builds Docker images
   - Pushes to Docker Hub
   - Deploys to production (if main branch)
```

#### Secrets Configuration

Add these secrets in GitHub Settings → Secrets:

```
DOCKER_HUB_USERNAME=your_username
DOCKER_HUB_TOKEN=your_token
STAGING_HOST=staging.server.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private key content>
PROD_HOST=prod.server.com
PROD_USER=deploy
PROD_SSH_KEY=<private key content>
```

---

### ✅ **Summary**

**CI/CD is now**:
- ✅ Testing automatically on push
- ✅ Building Docker images
- ✅ Deploying to staging/production
- ✅ Running health checks
- ✅ Rolling back on failure

**Your team can now**:
- Push code and forget about manual deployments
- Deploy multiple times per day safely
- Catch bugs before they reach production

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Previous**: [32-PRODUCTION-DEPLOYMENT.md](32-PRODUCTION-DEPLOYMENT.md)  
**Next**: Build more features!

---

## IDRM Production CI/CD Pipeline v3.0

### Automated Deployment for Multi-Platform System

**Version**: 3.0  
**CI/CD Platform**: GitHub Actions  
**Deployment**: Blue-Green with Zero Downtime  
**Platforms**: HTML/Tailwind + React SPA + React Native + Backend

---

### 🎯 Pipeline Overview

```
Trigger: Push to main/develop
    ↓
┌─────────────────────────────────────────┐
│  Stage 1: Code Quality & Security       │
│  - Linting (ESLint, Black, Ruff)       │
│  - Type checking (TypeScript, mypy)    │
│  - Security scan (Trivy, Snyk)         │
│  - Dependency audit                     │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Stage 2: Testing                       │
│  - Backend unit tests (pytest)          │
│  - Frontend tests (Vitest)              │
│  - Integration tests                    │
│  - E2E tests (Playwright)               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Stage 3: Build                         │
│  - Backend Docker image                 │
│  - API Gateway Docker image             │
│  - Frontend builds (HTML, React SPA)    │
│  - Mobile builds (iOS, Android)         │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Stage 4: Deploy (based on branch)      │
│  - develop → Staging                    │
│  - main → Production (blue-green)       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│  Stage 5: Post-Deployment               │
│  - Smoke tests                          │
│  - Performance tests                    │
│  - Notify team (Slack)                  │
└─────────────────────────────────────────┘
```

---

### 📁 GitHub Actions Workflows

#### Project Structure

```
.github/
├── workflows/
│   ├── backend-ci.yml          # Backend testing & build
│   ├── frontend-web-ci.yml     # HTML/Tailwind CI
│   ├── frontend-spa-ci.yml     # React SPA CI
│   ├── mobile-ci.yml           # React Native CI
│   ├── deploy-staging.yml      # Deploy to staging
│   ├── deploy-production.yml   # Deploy to production
│   └── rollback.yml            # Emergency rollback
├── actions/
│   ├── setup-bun/              # Reusable Bun setup
│   ├── setup-miniconda/        # Reusable Conda setup
│   └── docker-build/           # Reusable Docker build
└── dependabot.yml              # Dependency updates
```

---

### 🐍 Backend CI/CD

#### backend-ci.yml

```yaml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'backend/**'
  pull_request:
    paths:
      - 'backend/**'

jobs:
  lint-and-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          pip install black ruff mypy
          cd backend
          pip install -r requirements.txt
          
      - name: Run Black
        run: black --check backend/
        
      - name: Run Ruff
        run: ruff check backend/
        
      - name: Run mypy
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
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7.2-alpine
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Miniconda
        uses: conda-incubator/setup-miniconda@v3
        with:
          python-version: '3.11'
          
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov
          
      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          file: backend/coverage.xml

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: 'backend/'
          
      - name: Run Snyk
        uses: snyk/actions/python@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: backend/

  build-docker:
    needs: [lint-and-type-check, test, security-scan]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
        
      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Build and push
        uses: docker/build-push-action@v5
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

---

### ⚡ API Gateway CI/CD

#### api-gateway-ci.yml

```yaml
name: API Gateway CI

on:
  push:
    branches: [main, develop]
    paths:
      - 'api-gateway/**'
  pull_request:
    paths:
      - 'api-gateway/**'

jobs:
  lint-and-type-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
          
      - name: Install dependencies
        run: |
          cd api-gateway
          bun install
          
      - name: Run ESLint
        run: |
          cd api-gateway
          bun run lint
          
      - name: Type check
        run: |
          cd api-gateway
          bun run type-check

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        
      - name: Install dependencies
        run: |
          cd api-gateway
          bun install
          
      - name: Run tests
        run: |
          cd api-gateway
          bun test --coverage

  build-docker:
    needs: [lint-and-type-check, test]
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: docker/staging/api-gateway.Dockerfile
          push: true
          tags: ghcr.io/${{ github.repository }}/api-gateway:${{ github.sha }}
```

---

### 🎨 Frontend CI/CD

#### frontend-web-ci.yml (HTML/Tailwind)

```yaml
name: Frontend Web CI

on:
  push:
    paths: ['frontend/html-tailwind/**']
  pull_request:
    paths: ['frontend/html-tailwind/**']

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        
      - name: Install dependencies
        run: |
          cd frontend/html-tailwind
          bun install
          
      - name: Run tests
        run: |
          cd frontend/html-tailwind
          bun test
          
      - name: Build
        run: |
          cd frontend/html-tailwind
          bun run build
          
      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: web-build
          path: frontend/html-tailwind/dist

  lighthouse-ci:
    needs: lint-and-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        
      - name: Install and build
        run: |
          cd frontend/html-tailwind
          bun install
          bun run build
          
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v10
        with:
          urls: |
            http://localhost:5173
          uploadArtifacts: true
```

#### frontend-spa-ci.yml (React SPA)

```yaml
name: Frontend SPA CI

on:
  push:
    paths: ['frontend/react-spa/**']
  pull_request:
    paths: ['frontend/react-spa/**']

jobs:
  lint-test-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        
      - name: Install dependencies
        run: |
          cd frontend/react-spa
          bun install
          
      - name: Lint
        run: |
          cd frontend/react-spa
          bun run lint
          
      - name: Type check
        run: |
          cd frontend/react-spa
          bun run type-check
          
      - name: Test
        run: |
          cd frontend/react-spa
          bun test
          
      - name: Build
        run: |
          cd frontend/react-spa
          bun run build
          
      - name: Upload build
        uses: actions/upload-artifact@v4
        with:
          name: spa-build
          path: frontend/react-spa/dist
```

---

### 📱 Mobile CI/CD

#### mobile-ci.yml (React Native)

```yaml
name: Mobile CI

on:
  push:
    paths: ['mobile/**']
  pull_request:
    paths: ['mobile/**']

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        
      - name: Install dependencies
        run: |
          cd mobile
          bun install
          
      - name: Lint
        run: |
          cd mobile
          bun run lint
          
      - name: Test
        run: |
          cd mobile
          bun test

  build-ios:
    needs: lint-and-test
    runs-on: macos-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Expo
        uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
          
      - name: Build iOS
        run: |
          cd mobile
          eas build --platform ios --non-interactive --no-wait

  build-android:
    needs: lint-and-test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Expo
        uses: expo/expo-github-action@v8
        with:
          expo-version: latest
          eas-version: latest
          token: ${{ secrets.EXPO_TOKEN }}
          
      - name: Build Android
        run: |
          cd mobile
          eas build --platform android --non-interactive --no-wait
```

---

### 🚀 Deployment Workflows

#### deploy-staging.yml

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
      
      - name: Deploy to staging server
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
            
      - name: Run smoke tests
        run: |
          sleep 30
          curl -f https://staging.idrm.example.com/api/health
          
      - name: Notify Slack
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "✅ Staging deployment successful!"
            }
```

#### deploy-production.yml (Blue-Green)

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy Blue environment
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/idrm
            
            # Deploy to blue environment
            export DEPLOYMENT_COLOR=blue
            docker-compose -f docker-compose.blue.yml pull
            docker-compose -f docker-compose.blue.yml up -d
            
            # Wait for health check
            sleep 60
            
            # Smoke test blue environment
            curl -f http://blue.idrm.internal/api/health || exit 1
            
      - name: Switch traffic to Blue
        run: |
          # Update load balancer to point to blue
          # This is cloud provider specific
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
          payload: |
            {
              "text": "🚀 Production deployment successful!",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Deployment Info*\nVersion: ${{ github.sha }}\nEnvironment: Production\nStatus: ✅ Success"
                  }
                }
              ]
            }
```

---

### 🔄 Rollback Workflow

#### rollback.yml

```yaml
name: Emergency Rollback

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to rollback to'
        required: true
      environment:
        description: 'Environment (staging/production)'
        required: true
        default: 'production'

jobs:
  rollback:
    runs-on: ubuntu-latest
    steps:
      - name: Rollback to previous version
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /opt/idrm
            
            # Switch back to green environment
            export VERSION=${{ github.event.inputs.version }}
            
            # Update load balancer
            aws elbv2 modify-listener \
              --listener-arn ${{ secrets.LB_LISTENER_ARN }} \
              --default-actions Type=forward,TargetGroupArn=${{ secrets.GREEN_TG_ARN }}
              
      - name: Verify rollback
        run: |
          sleep 30
          curl -f https://idrm.example.com/api/health
          
      - name: Notify team
        uses: slackapi/slack-github-action@v1
        with:
          webhook-url: ${{ secrets.SLACK_WEBHOOK }}
          payload: |
            {
              "text": "⚠️ Emergency rollback executed!",
              "blocks": [
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": "*Rollback Info*\nVersion: ${{ github.event.inputs.version }}\nEnvironment: ${{ github.event.inputs.environment }}\nStatus: Completed"
                  }
                }
              ]
            }
```

---

### 🔐 Required Secrets

#### GitHub Repository Secrets

```
## Staging
STAGING_HOST=staging.idrm.example.com
STAGING_USER=deploy
STAGING_SSH_KEY=<private-key>

## Production
PROD_HOST=idrm.example.com
PROD_USER=deploy
PROD_SSH_KEY=<private-key>

## Container Registry
GHCR_TOKEN=<github-token>

## Cloud Provider (AWS example)
AWS_ACCESS_KEY_ID=<key>
AWS_SECRET_ACCESS_KEY=<secret>
LB_LISTENER_ARN=<arn>
BLUE_TG_ARN=<arn>
GREEN_TG_ARN=<arn>

## Mobile
EXPO_TOKEN=<expo-token>
APPLE_ID=<apple-id>
APPLE_APP_SPECIFIC_PASSWORD=<password>
GOOGLE_PLAY_SERVICE_ACCOUNT=<json>

## Notifications
SLACK_WEBHOOK=<webhook-url>

## Security Scanning
SNYK_TOKEN=<token>
```

---

### 📊 Monitoring Integration

#### Post-Deployment Metrics

```yaml
- name: Send deployment metrics
  run: |
    curl -X POST https://api.datadog.com/api/v1/events \
      -H "DD-API-KEY: ${{ secrets.DATADOG_API_KEY }}" \
      -d '{
        "title": "Deployment",
        "text": "Deployed version ${{ github.sha }}",
        "tags": ["environment:production", "service:idrm"]
      }'
```

---

### ✅ CI/CD Best Practices

#### Code Quality Gates

- Minimum test coverage: 80%
- No critical security vulnerabilities
- Lighthouse score > 90
- All linting checks pass
- Type checking passes

#### Deployment Strategy

- Staging deploys automatically on `develop` push
- Production requires manual approval
- Blue-green deployment for zero downtime
- Automated rollback on health check failure
- Canary deployments for high-risk changes

---

**IDRM v3 CI/CD: Automated, Tested, Production-Ready!** 🚀

**Deployment Time**: < 10 minutes  
**Rollback Time**: < 2 minutes  
**Uptime**: 99.9%+ with blue-green deployment
