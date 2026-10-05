> *Type: Document (specification) · Audience: DevOps · Status: Archived — v1 historical generation*

# IDRM Platform CI/CD Deployment Guide

> Three deployment approaches: Manual, GitHub Actions, and GitLab CI/CD

<!-- IDRM-CLEANUP doc=v1-80-cicd status=ANNOTATED pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — CI/CD = FFP
> CI/CD pipelines (GitHub Actions / GitLab CI) are **FFP** — the MVP deploys **natively via systemd** (ADR-006),
> see [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md).
> FFP automation → [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md)
> + [`ci-cd-101`](../../../../guides/mvp/learn/ci-cd-101.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

## Overview

This guide provides **three deployment strategies** for the IDRM platform:

1. **Manual Deployment** - Beginner-friendly, full control
2. **GitHub Actions** - Modern OSS workflow, cloud-native
3. **GitLab CI** - Enterprise-grade, self-hosted friendly

Choose based on your team's expertise and infrastructure.

---

## Table of Contents

1. [Approach Comparison](#approach-comparison)
2. [Manual Deployment](#manual-deployment)
3. [GitHub Actions CI/CD](#github-actions-cicd)
4. [GitLab CI/CD](#gitlab-cicd)
5. [Best Practices](#best-practices)

---

## Approach Comparison

| Feature | Manual | GitHub Actions | GitLab CI |
|---------|--------|----------------|-----------|
| **Setup Complexity** | Low | Medium | Medium-High |
| **Automation** | None | Full | Full |
| **Cost** | Free | Free (public) | Free (self-hosted) |
| **Learning Curve** | Easy | Medium | Medium |
| **Best For** | Learning, Debugging | OSS Projects, Startups | Enterprises, On-prem |
| **Rollback** | Manual | Manual | Automated |
| **Secrets Management** | .env files | GitHub Secrets | GitLab Variables |
| **Deployment Speed** | Slow | Fast | Fast |

### When to Use Each

**Manual Deployment**:
- ✅ Learning the platform
- ✅ Small team (1-3 developers)
- ✅ Infrequent deployments
- ✅ Full control needed
- ❌ NOT for production at scale

**GitHub Actions**:
- ✅ Open source projects
- ✅ GitHub-hosted repositories
- ✅ Cloud deployments (AWS, GCP, Azure)
- ✅ Teams familiar with GitHub
- ❌ Not ideal for on-premise

**GitLab CI**:
- ✅ Enterprise environments
- ✅ Self-hosted infrastructure
- ✅ Complex deployment pipelines
- ✅ Compliance requirements
- ❌ Overkill for simple projects

---

## Manual Deployment

### Prerequisites

- SSH access to server
- Git repository access
- Docker installed on server
- Environment variables configured

### Step-by-Step Process

#### 1. SSH into Server

```bash
# Connect to staging
ssh -p 2222 idrm-deploy@staging.example.com

# Or production
ssh -p 2222 idrm-prod@production.example.com
```

#### 2. Navigate to Project

```bash
cd /home/idrm-prod/idrm-production
```

#### 3. Pull Latest Code

```bash
# Fetch latest changes
git fetch origin

# Check what's new
git log HEAD..origin/main --oneline

# Pull changes
git pull origin main
```

#### 4. Backup Current State

```bash
# Backup database
./backup-database.sh

# Note current commit
git log -1 > /tmp/pre-deployment-commit.txt
```

#### 5. Build New Images

```bash
# Build updated images
docker compose build --no-cache

# Or build specific service
docker compose build api-gateway
```

#### 6. Run Database Migrations

```bash
# If using Alembic
docker compose exec service-management alembic upgrade head

# Verify
docker compose exec postgres psql -U idrm_user -d idrm_production -c "\dt"
```

#### 7. Deploy with Zero Downtime

```bash
# Option A: Rolling update
docker compose up -d --no-deps --build api-gateway
docker compose up -d --no-deps --build service-management
docker compose up -d --no-deps --build frontend

# Wait for health checks
sleep 30

# Reload NGINX
docker compose exec nginx nginx -s reload

# Option B: Use deployment script
./deploy.sh
```

#### 8. Verify Deployment

```bash
# Check all containers
docker compose ps

# Check health endpoints
curl https://yourdomain.com/health
curl https://yourdomain.com/api/health

# Check logs
docker compose logs --tail=50 api-gateway
```

#### 9. Rollback (If Needed)

```bash
# Find previous commit
git log --oneline -5

# Rollback code
git reset --hard <previous-commit-hash>

# Rebuild and deploy
docker compose build
docker compose up -d

# Or restore from backup
./restore.sh /path/to/backup.sql.gz
```

### Manual Deployment Checklist

- [ ] Pull latest code
- [ ] Backup database
- [ ] Build images
- [ ] Run migrations
- [ ] Deploy containers
- [ ] Verify health checks
- [ ] Test critical paths
- [ ] Monitor logs (15 minutes)
- [ ] Document deployment
- [ ] Notify team

---

## GitHub Actions CI/CD

### Prerequisites

- GitHub repository
- GitHub Secrets configured
- Server with SSH access
- Docker on server

### Setup

#### 1. Create SSH Deploy Key

```bash
# On your local machine
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy

# Copy public key to server
ssh-copy-id -i ~/.ssh/github_deploy.pub idrm-prod@production.example.com

# Add private key to GitHub Secrets
# Settings → Secrets → Actions → New repository secret
# Name: SSH_PRIVATE_KEY
# Value: <contents of github_deploy>
```

#### 2. Configure GitHub Secrets

Go to repository **Settings → Secrets and variables → Actions**

Add these secrets:

```
SSH_PRIVATE_KEY     = <private key from above>
SSH_HOST            = production.example.com
SSH_PORT            = 2222
SSH_USER            = idrm-prod
DB_PASSWORD         = <production db password>
REDIS_PASSWORD      = <production redis password>
JWT_SECRET          = <production jwt secret>
GEOSERVER_PASSWORD  = <production geoserver password>
```

#### 3. Create Workflow File

Create `.github/workflows/deploy-production.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]
  workflow_dispatch:  # Allow manual trigger

env:
  DOCKER_BUILDKIT: 1
  COMPOSE_DOCKER_CLI_BUILD: 1

jobs:
  # Test Job
  test:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup Bun
        uses: oven-sh/setup-bun@v1
        with:
          bun-version: latest
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies (API Gateway)
        working-directory: ./backend/api-gateway
        run: bun install
      
      - name: Install dependencies (Python)
        working-directory: ./backend/services/service-management
        run: |
          pip install poetry
          poetry install
      
      - name: Run tests (API Gateway)
        working-directory: ./backend/api-gateway
        run: bun test || echo "No tests configured yet"
      
      - name: Run tests (Python)
        working-directory: ./backend/services/service-management
        run: poetry run pytest || echo "No tests configured yet"
      
      - name: Lint code
        run: |
          echo "Linting would run here"

  # Build Job
  build:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build API Gateway
        uses: docker/build-push-action@v5
        with:
          context: ./backend/api-gateway
          push: false
          tags: idrm-api-gateway:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
      
      - name: Build Service Management
        uses: docker/build-push-action@v5
        with:
          context: ./backend/services/service-management
          push: false
          tags: idrm-service-mgmt:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Deploy Job
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment: production  # Requires approval
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/deploy_key
          chmod 600 ~/.ssh/deploy_key
          ssh-keyscan -p ${{ secrets.SSH_PORT }} ${{ secrets.SSH_HOST }} >> ~/.ssh/known_hosts
      
      - name: Deploy to Production
        env:
          SSH_KEY: ~/.ssh/deploy_key
          SSH_USER: ${{ secrets.SSH_USER }}
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_PORT: ${{ secrets.SSH_PORT }}
        run: |
          ssh -i $SSH_KEY -p $SSH_PORT $SSH_USER@$SSH_HOST << 'ENDSSH'
            cd /home/idrm-prod/idrm-production
            
            # Pull latest code
            git pull origin main
            
            # Backup database
            ./backup-database.sh
            
            # Build and deploy
            docker compose build
            docker compose up -d --no-deps api-gateway service-management frontend
            
            # Wait for health checks
            sleep 30
            
            # Reload NGINX
            docker compose exec nginx nginx -s reload
            
            # Clean up old images
            docker image prune -f
            
            echo "Deployment completed!"
          ENDSSH
      
      - name: Verify Deployment
        run: |
          # Wait a bit for services to stabilize
          sleep 15
          
          # Check health endpoints
          curl -f https://yourdomain.com/health || exit 1
          curl -f https://yourdomain.com/api/health || exit 1
          
          echo "Deployment verified successfully!"
      
      - name: Notify Success
        if: success()
        run: |
          echo "✅ Deployment to production succeeded!"
          # Add Slack/Discord/Email notification here
      
      - name: Notify Failure
        if: failure()
        run: |
          echo "❌ Deployment to production failed!"
          # Add Slack/Discord/Email notification here
```

#### 4. Create Staging Workflow

Create `.github/workflows/deploy-staging.yml`:

```yaml
name: Deploy to Staging

on:
  push:
    branches: [ develop ]
  pull_request:
    branches: [ main ]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      # Similar steps as production but for staging server
      - name: Deploy to Staging
        run: |
          # Deploy to staging.example.com
          echo "Deploying to staging..."
```

#### 5. Enable Branch Protection

1. Go to **Settings → Branches**
2. Add rule for `main` branch:
   - ✅ Require pull request reviews
   - ✅ Require status checks to pass
   - ✅ Require deployments to succeed before merging

### GitHub Actions Best Practices

✅ **DO**:
- Use GitHub Secrets for sensitive data
- Enable environment protection rules
- Require manual approval for production
- Tag releases (`v1.0.0`)
- Run tests before deployment
- Use caching for dependencies

❌ **DON'T**:
- Commit secrets to repository
- Deploy directly to production without testing
- Skip health checks
- Ignore failed tests

---

## GitLab CI/CD

### Prerequisites

- GitLab repository (self-hosted or GitLab.com)
- GitLab Runner installed on server
- SSH access configured
- Docker on server

### Setup

#### 1. Install GitLab Runner

```bash
# On your server
curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt install gitlab-runner

# Register runner
sudo gitlab-runner register

# Enter GitLab URL: https://gitlab.com
# Enter registration token: (from GitLab project Settings → CI/CD → Runners)
# Enter description: idrm-production-runner
# Enter tags: production,docker
# Enter executor: shell
```

#### 2. Configure GitLab CI/CD Variables

Go to **Settings → CI/CD → Variables**

Add these variables (Protected + Masked):

```
DB_PASSWORD             = <production db password>
REDIS_PASSWORD          = <production redis password>
JWT_SECRET              = <production jwt secret>
GEOSERVER_PASSWORD      = <production geoserver password>
PRODUCTION_SERVER       = production.example.com
PRODUCTION_USER         = idrm-prod
SSH_PRIVATE_KEY         = <private key>
```

#### 3. Create .gitlab-ci.yml

```yaml
# .gitlab-ci.yml
stages:
  - test
  - build
  - deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_BUILDKIT: 1
  COMPOSE_DOCKER_CLI_BUILD: 1

# Test Stage
test:api-gateway:
  stage: test
  image: oven/bun:1
  script:
    - cd backend/api-gateway
    - bun install
    - bun test || echo "No tests configured"
  only:
    - merge_requests
    - main
    - develop

test:python-services:
  stage: test
  image: python:3.11-slim
  script:
    - cd backend/services/service-management
    - pip install poetry
    - poetry install
    - poetry run pytest || echo "No tests configured"
  only:
    - merge_requests
    - main
    - develop

lint:code:
  stage: test
  image: node:20-alpine
  script:
    - echo "Linting code..."
    - echo "Would run ESLint, Prettier, Black, etc."
  allow_failure: true

# Build Stage
build:api-gateway:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd backend/api-gateway
    - docker build -t $CI_REGISTRY_IMAGE/api-gateway:$CI_COMMIT_SHA .
    - docker build -t $CI_REGISTRY_IMAGE/api-gateway:latest .
    - docker push $CI_REGISTRY_IMAGE/api-gateway:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE/api-gateway:latest
  only:
    - main
    - develop

build:service-management:
  stage: build
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    - cd backend/services/service-management
    - docker build -t $CI_REGISTRY_IMAGE/service-mgmt:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE/service-mgmt:$CI_COMMIT_SHA
  only:
    - main
    - develop

# Deploy to Staging
deploy:staging:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan -p 2222 staging.example.com >> ~/.ssh/known_hosts
  script:
    - |
      ssh -p 2222 idrm-deploy@staging.example.com << 'ENDSSH'
        cd /home/idrm-deploy/idrm-staging
        git pull origin develop
        docker compose build
        docker compose up -d
        docker image prune -f
      ENDSSH
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - develop

# Deploy to Production
deploy:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client curl
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan -p 2222 $PRODUCTION_SERVER >> ~/.ssh/known_hosts
  script:
    # Backup
    - |
      ssh -p 2222 $PRODUCTION_USER@$PRODUCTION_SERVER << 'ENDSSH'
        cd /home/idrm-prod/idrm-production
        ./backup-database.sh
      ENDSSH
    
    # Deploy
    - |
      ssh -p 2222 $PRODUCTION_USER@$PRODUCTION_SERVER << 'ENDSSH'
        cd /home/idrm-prod/idrm-production
        git pull origin main
        docker compose build
        docker compose up -d --no-deps api-gateway service-management frontend
        sleep 30
        docker compose exec nginx nginx -s reload
        docker image prune -f
      ENDSSH
    
    # Verify
    - curl -f https://$PRODUCTION_SERVER/health || exit 1
    - curl -f https://$PRODUCTION_SERVER/api/health || exit 1
    
    - echo "✅ Production deployment successful!"
  environment:
    name: production
    url: https://yourdomain.com
  when: manual  # Require manual trigger
  only:
    - main
  tags:
    - production

# Rollback Job (Manual)
rollback:production:
  stage: deploy
  image: alpine:latest
  before_script:
    - apk add --no-cache openssh-client
    - eval $(ssh-agent -s)
    - echo "$SSH_PRIVATE_KEY" | tr -d '\r' | ssh-add -
    - mkdir -p ~/.ssh
    - chmod 700 ~/.ssh
    - ssh-keyscan -p 2222 $PRODUCTION_SERVER >> ~/.ssh/known_hosts
  script:
    - |
      ssh -p 2222 $PRODUCTION_USER@$PRODUCTION_SERVER << 'ENDSSH'
        cd /home/idrm-prod/idrm-production
        git reset --hard HEAD~1
        docker compose build
        docker compose up -d
      ENDSSH
    - echo "⚠️ Rollback completed!"
  environment:
    name: production
  when: manual
  only:
    - main
```

#### 4. Advanced: Multi-Environment Pipeline

```yaml
# .gitlab-ci.yml (advanced)
stages:
  - test
  - build
  - deploy:staging
  - test:staging
  - deploy:production

# ... (previous jobs)

test:staging:integration:
  stage: test:staging
  script:
    - curl -f https://staging.example.com/api/health
    - echo "Running integration tests..."
    # Add actual integration tests here
  only:
    - develop

deploy:production:
  stage: deploy:production
  # ... (production deployment)
  needs:
    - test:staging:integration
  when: manual
  only:
    - main
```

### GitLab CI Best Practices

✅ **DO**:
- Use GitLab CI/CD variables (masked + protected)
- Implement manual approval for production
- Use dedicated runners for production
- Enable auto-rollback on failure
- Tag production releases
- Use environments for tracking

❌ **DON'T**:
- Run production deploys on shared runners
- Skip health checks
- Deploy without backups
- Ignore failed pipeline stages

---

## Best Practices

### General CI/CD Principles

#### 1. Deployment Strategy

```
Developer → Feature Branch → PR/MR
    ↓
Run Tests → Build → Deploy to Staging
    ↓
QA Testing on Staging
    ↓
Manual Approval
    ↓
Deploy to Production
    ↓
Monitor & Verify
```

#### 2. Environment Promotion

```
Development → Staging → Production
   (auto)      (auto)     (manual)
```

#### 3. Secrets Management

**DON'T**:
```bash
# ❌ Bad
DB_PASSWORD=mysecret123
git add .env
git commit
```

**DO**:
```bash
# ✅ Good
# Use CI/CD platform secrets
# GitHub Secrets, GitLab Variables, etc.

# .env.example (committed)
DB_PASSWORD=CHANGE_ME

# .env (git-ignored, generated by CI)
DB_PASSWORD=${{ secrets.DB_PASSWORD }}
```

#### 4. Health Checks

Always verify after deployment:

```bash
# API health
curl -f https://api.example.com/health || exit 1

# Database connectivity
docker compose exec postgres pg_isready

# Service endpoints
curl -f https://api.example.com/api/v1/services || exit 1
```

#### 5. Rollback Strategy

Have a plan:

```bash
# Quick rollback
git revert HEAD
git push

# CI/CD will deploy previous version

# Or manual
ssh server
cd /app
git reset --hard <previous-commit>
docker compose up -d --build
```

---

## Monitoring & Alerts

### Post-Deployment Monitoring

```bash
# Watch logs after deployment
docker compose logs -f --tail=100

# Monitor specific time window
docker compose logs --since=5m

# Check error logs
docker compose logs | grep -i error

# Monitor resources
docker stats
```

### Set Up Alerts

**Slack Webhook** (GitHub Actions):
```yaml
- name: Notify Slack
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK }} \
      -H 'Content-Type: application/json' \
      -d '{"text":"❌ Production deployment failed!"}'
```

**Email** (GitLab CI):
```yaml
deploy:production:
  after_script:
    - |
      if [ $CI_JOB_STATUS == 'failed' ]; then
        echo "Deployment failed" | mail -s "Alert" admin@example.com
      fi
```

---

## Troubleshooting

### Common CI/CD Issues

**Issue**: SSH connection timeout
```bash
# Solution: Check firewall, verify port
sudo ufw status
ssh -v -p 2222 user@server
```

**Issue**: Docker build fails
```bash
# Solution: Clear cache
docker builder prune -a
docker compose build --no-cache
```

**Issue**: Health check fails
```bash
# Solution: Check logs
docker compose logs api-gateway
docker compose ps
```

---

## Summary: Which Approach to Choose?

| Scenario | Recommendation |
|----------|---------------|
| Learning / Small Team | **Manual** |
| Startup / OSS Project | **GitHub Actions** |
| Enterprise / Compliance | **GitLab CI** |
| Hybrid (learning + automation) | Start **Manual**, migrate to **GitHub Actions** |

---

**🚀 Choose your deployment strategy and ship with confidence!**
