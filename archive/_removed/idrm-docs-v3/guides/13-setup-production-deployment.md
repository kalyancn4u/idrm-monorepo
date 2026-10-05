# IDRM v3 · Production Deployment

<!-- IDRM-CLEANUP doc=v3-g13-prod status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — production (4758 L) → MVP native / FFP containers
> MVP production = native systemd on one Ubuntu server → [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md);
> container/K8s/multi-node → **FFP** [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
*Type: Guide (novice / how-to) · Audience: DevOps, admins · Status: Archived — v3 historical generation*
*Consolidated from: 32-PRODUCTION-DEPLOYMENT.md, setup-production-v3.md, 48-COMPLETE-DEPLOYMENT-GUIDE.md*

## Contents
- [IDRM: Production Deployment Guide](#idrm-production-deployment-guide)
- [IDRM Production Setup v3.0](#idrm-production-setup-v30)
- [IDRM: Complete Deployment Guide](#idrm-complete-deployment-guide)

---

## IDRM: Production Deployment Guide

### Secure, Scalable Production Environment (For Complete Novices!)

**Version**: 3.0 Consolidated  
**Audience**: System administrators, DevOps engineers, technical leads  
**Technology**: Docker + SSL + Firewall + Monitoring  
**Reading Time**: 3-4 hours (deploy step-by-step!)  
**Last Updated**: May 15, 2026

---

### 📚 **Table of Contents**

1. [Production Overview](#1-production-overview)
2. [Security Hardening](#2-security-hardening)
3. [SSL/TLS Setup](#3-ssltls-setup)
4. [Production Deployment](#4-production-deployment)
5. [Monitoring](#5-monitoring)
6. [Backups](#6-backups)
7. [Maintenance](#7-maintenance)

---

### 1. **Production Overview**

#### Hardware Requirements

```
Minimum:
- CPU: 16 cores
- RAM: 32 GB
- Disk: 500 GB NVMe SSD
- Bandwidth: 1 Gbps

Recommended:
- CPU: 32 cores
- RAM: 64 GB  
- Disk: 1 TB NVMe SSD RAID 10
- Bandwidth: 10 Gbps
```

#### Production Checklist

Before deploying to production:

- [ ] Domain name registered
- [ ] DNS configured (A records point to server)
- [ ] SSL certificate ready (Let's Encrypt)
- [ ] Firewall rules planned
- [ ] Backup strategy defined
- [ ] Monitoring tools chosen
- [ ] Team trained on procedures

---

### 2. **Security Hardening**

#### SSH Hardening

```bash
## Edit SSH config
sudo nano /etc/ssh/sshd_config

## Recommended settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
MaxAuthTries 3

## Restart SSH
sudo systemctl restart sshd
```

#### Firewall Setup (UFW)

```bash
## Enable firewall
sudo ufw --force enable

## Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

## Allow SSH (restrict to your IP)
sudo ufw allow from YOUR_IP to any port 22

## Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

## Enable
sudo ufw enable

## Check status
sudo ufw status numbered
```

#### Fail2Ban (Brute Force Protection)

```bash
## Install
sudo apt install -y fail2ban

## Configure
sudo nano /etc/fail2ban/jail.local

## Add:
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600

## Start
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

### 3. **SSL/TLS Setup**

#### Install Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### Obtain SSL Certificate

```bash
## Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com

## Test auto-renewal
sudo certbot renew --dry-run

## Auto-renewal is handled by systemd timer
sudo systemctl status certbot.timer
```

#### NGINX SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # Strong SSL settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256...';
    ssl_prefer_server_ciphers on;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

## Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

---

### 4. **Production Deployment**

#### Environment Variables

```bash
## Create .env.production
POSTGRES_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
ENVIRONMENT=production
DEBUG=False
```

#### Deploy

```bash
## Pull latest code
git pull origin main

## Build images
docker compose -f docker-compose.production.yml build --no-cache

## Start services with zero downtime
docker compose -f docker-compose.production.yml up -d --no-deps --build

## Run database migrations
docker compose -f docker-compose.production.yml exec auth-service \
  alembic upgrade head

## Health check
curl https://yourdomain.com/health
```

---

### 5. **Monitoring**

#### Basic Health Monitoring Script

```bash
#!/bin/bash
## health-check.sh

HEALTH_URL="https://yourdomain.com/health"

if curl -f -s $HEALTH_URL > /dev/null; then
    echo "✅ System healthy"
else
    echo "❌ System down - alerting team"
    # Send alert (email, Slack, PagerDuty, etc.)
fi
```

#### Cron Job (Every 5 Minutes)

```bash
## Edit crontab
crontab -e

## Add:
*/5 * * * * /opt/idrm/scripts/health-check.sh
```

---

### 6. **Backups**

#### Automated Database Backup

```bash
#!/bin/bash
## backup-database.sh

BACKUP_DIR="/backups/idrm"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

## Backup PostgreSQL
docker compose exec -T postgres pg_dump -U idrm_user idrm_db | \
  gzip > "$BACKUP_DIR/db_$TIMESTAMP.sql.gz"

## Keep only last 30 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete

echo "Backup completed: db_$TIMESTAMP.sql.gz"
```

#### Cron Job (Daily at 2 AM)

```bash
0 2 * * * /opt/idrm/scripts/backup-database.sh
```

---

### 7. **Maintenance**

#### Update Process

```bash
## 1. Backup first
./scripts/backup-database.sh

## 2. Pull latest code
git pull origin main

## 3. Deploy
docker compose -f docker-compose.production.yml up -d --no-deps --build

## 4. Run migrations
docker compose -f docker-compose.production.yml exec auth-service \
  alembic upgrade head

## 5. Verify
curl https://yourdomain.com/health
```

#### Rollback Procedure

```bash
## Revert to previous version
git reset --hard PREVIOUS_COMMIT_HASH

## Rebuild and deploy
docker compose -f docker-compose.production.yml up -d --no-deps --build
```

---

### ✅ **Summary**

**Production is now**:
- ✅ Secured with firewall and fail2ban
- ✅ Encrypted with SSL/TLS
- ✅ Monitored for health
- ✅ Backed up daily
- ✅ Ready for users!

**Next**: [33-CI-CD-PIPELINES.md](33-CI-CD-PIPELINES.md)

---

**Document Information**  
**Version**: 3.0 Consolidated  
**Created**: May 15, 2026  
**Previous**: [31-STAGING-SETUP.md](31-STAGING-SETUP.md)  
**Next**: [33-CI-CD-PIPELINES.md](33-CI-CD-PIPELINES.md)

---

## IDRM Production Setup v3.0

### Cloud Deployment with CI/CD - Multi-Platform

**Version**: 3.0  
**Environment**: Production  
**Platforms**: HTML/Tailwind + React SPA + React Native  
**Deployment**: Automated CI/CD with GitHub Actions

---

### 🎯 Production Architecture

```
                                Internet
                                   │
                                   ↓
                            Load Balancer (AWS ALB/CloudFlare)
                                   │
                    ┌──────────────┼──────────────┐
                    ↓              ↓              ↓
            Web Servers      Admin Servers   API Servers
          (NGINX + Web)    (NGINX + Admin) (API Gateway)
                    │              │              │
                    └──────────────┼──────────────┘
                                   ↓
                            Backend Services
                         (Python FastAPI + Bun)
                                   │
                    ┌──────────────┼──────────────┐
                    ↓              ↓              ↓
              PostgreSQL       Redis         S3/Storage
           (Primary + Replica) (Cluster)    (Media/Logs)
```

---

### 📋 Infrastructure Requirements

#### Cloud Provider Options

**Recommended** (in order):
1. **AWS** - Most features, highest cost
2. **Google Cloud** - Good balance
3. **DigitalOcean** - Simple, cost-effective
4. **Hetzner** - EU-based, very cost-effective

#### Minimum Resources

```
Production Tier 1 (1,000 users):
- 2x Application Servers (4 vCPU, 8GB RAM)
- 1x Database Server (4 vCPU, 16GB RAM, SSD)
- 1x Redis Server (2 vCPU, 4GB RAM)
- 1x Load Balancer
- 500GB Storage
- 1TB/month Bandwidth
Cost: ~$200-300/month

Production Tier 2 (10,000 users):
- 4x Application Servers (8 vCPU, 16GB RAM)
- 2x Database Servers (Primary + Replica)
- 2x Redis Servers (Cluster)
- Load Balancer + CDN
- 2TB Storage
- 5TB/month Bandwidth
Cost: ~$800-1200/month

Production Tier 3 (100,000+ users):
- Auto-scaling (4-20 app servers)
- Database cluster (3+ nodes)
- Redis cluster (6+ nodes)
- Multi-region deployment
- CDN + DDoS protection
- 10TB+ Storage
Cost: ~$3000-10,000/month
```

---

### 🚀 Step 1: Initial Server Setup

#### Provision Servers

**Using DigitalOcean (example)**:

```bash
## Install doctl
snap install doctl
doctl auth init

## Create VPC
doctl vpcs create --name idrm-production --region nyc3

## Create database server
doctl compute droplet create idrm-prod-db \
  --size s-4vcpu-8gb \
  --image ubuntu-22-04-x64 \
  --region nyc3 \
  --vpc-uuid <vpc-uuid>

## Create application servers
doctl compute droplet create idrm-prod-app-1 idrm-prod-app-2 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --region nyc3 \
  --vpc-uuid <vpc-uuid>

## Create load balancer
doctl compute load-balancer create \
  --name idrm-prod-lb \
  --region nyc3 \
  --forwarding-rules entry_protocol:https,entry_port:443,target_protocol:http,target_port:80,certificate_id:<cert-id>
```

#### Configure Servers

```bash
## SSH into each server
ssh root@<server-ip>

## Update system
apt update && apt upgrade -y

## Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
systemctl enable docker

## Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

## Configure firewall
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw enable
```

---

### 🔐 Step 2: Security Setup

#### SSL Certificates

```bash
## Install Certbot
apt install -y certbot python3-certbot-nginx

## Get certificates
certbot --nginx -d idrm.example.com -d admin.idrm.example.com -d api.idrm.example.com

## Auto-renewal
echo "0 0,12 * * * root certbot renew --quiet" | tee -a /etc/crontab
```

#### Secrets Management

```bash
## Install AWS Secrets Manager CLI
apt install -y awscli

## Store secrets
aws secretsmanager create-secret \
  --name idrm-production-db \
  --secret-string '{"username":"idrm_prod","password":"<strong-password>"}'

aws secretsmanager create-secret \
  --name idrm-production-jwt \
  --secret-string '{"secret":"<jwt-secret-key>"}'
```

#### Database Security

```bash
## PostgreSQL configuration
cat >> /etc/postgresql/16/main/postgresql.conf << EOF
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.key'
password_encryption = scram-sha-256
max_connections = 200
shared_buffers = 4GB
effective_cache_size = 12GB
EOF

## Firewall - only allow app servers
ufw allow from <app-server-1-ip> to any port 5432
ufw allow from <app-server-2-ip> to any port 5432
```

---

### 📦 Step 3: Application Deployment

#### Docker Compose for Production

```yaml
## docker-compose.production.yml
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
      restart_policy:
        condition: on-failure

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

---

### 🔄 Step 4: CI/CD Pipeline Setup

See `production-ci-cd-readme-v3.md` for detailed GitHub Actions configuration.

#### Deployment Workflow

```
Developer → Push to main
    ↓
GitHub Actions triggered
    ↓
1. Run tests
2. Build Docker images
3. Push to registry
4. Deploy to production (blue-green)
5. Run smoke tests
6. Switch traffic
```

---

### 📊 Step 5: Monitoring & Logging

#### Prometheus + Grafana

```yaml
## monitoring/docker-compose.yml
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

#### Application Monitoring

```python
## backend/app/middleware/monitoring.py
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def monitor_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    REQUEST_DURATION.observe(duration)
    
    return response
```

---

### 💾 Step 6: Backup & Recovery

#### Automated Backups

```bash
#!/bin/bash
## scripts/backup-production.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/idrm"

## Database backup
pg_dump -U idrm_prod -h db.idrm.example.com idrm_prod > ${BACKUP_DIR}/db_${DATE}.sql
gzip ${BACKUP_DIR}/db_${DATE}.sql

## Upload to S3
aws s3 cp ${BACKUP_DIR}/db_${DATE}.sql.gz s3://idrm-backups/database/

## Redis backup
redis-cli -h redis.idrm.example.com --rdb /tmp/redis_${DATE}.rdb
aws s3 cp /tmp/redis_${DATE}.rdb s3://idrm-backups/redis/

## Cleanup old backups (keep 30 days)
find ${BACKUP_DIR} -mtime +30 -delete

echo "Backup complete: ${DATE}"
```

```bash
## Add to crontab
0 2 * * * /root/scripts/backup-production.sh
```

---

### 🚨 Step 7: Incident Response

#### Rollback Procedure

```bash
#!/bin/bash
## scripts/rollback-production.sh

PREVIOUS_VERSION=$1

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: ./rollback-production.sh <version>"
    exit 1
fi

echo "Rolling back to version: $PREVIOUS_VERSION"

## Update version
export VERSION=$PREVIOUS_VERSION

## Deploy previous version
docker-compose -f docker-compose.production.yml pull
docker-compose -f docker-compose.production.yml up -d

## Health check
sleep 30
curl -f https://idrm.example.com/api/health || exit 1

echo "Rollback complete!"
```

---

### ✅ Production Checklist

#### Pre-Launch

- [ ] Domain configured and DNS pointing correctly
- [ ] SSL certificates installed and auto-renewal enabled
- [ ] Database replicas configured
- [ ] Redis cluster configured
- [ ] Backups automated and tested
- [ ] Monitoring dashboards configured
- [ ] Alerting rules set up
- [ ] Load balancer health checks configured
- [ ] DDoS protection enabled
- [ ] Rate limiting configured
- [ ] Secrets stored securely (not in code)
- [ ] CI/CD pipeline tested
- [ ] Rollback procedure tested
- [ ] Incident response plan documented

#### Security

- [ ] Firewall rules configured
- [ ] SSH key-only authentication
- [ ] Database connections encrypted
- [ ] API rate limiting enabled
- [ ] CORS configured correctly
- [ ] Security headers enabled (HSTS, CSP, etc.)
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] XSS prevention
- [ ] CSRF protection

#### Performance

- [ ] CDN configured for static assets
- [ ] Database indexes optimized
- [ ] Redis caching enabled
- [ ] Image optimization
- [ ] Gzip compression enabled
- [ ] HTTP/2 enabled
- [ ] Database connection pooling
- [ ] Query optimization

---

### 📱 Mobile App Production

#### App Store Deployment

```bash
## Build production version
cd mobile

## iOS
eas build --platform ios --profile production
eas submit --platform ios --latest

## Android
eas build --platform android --profile production
eas submit --platform android --latest
```

#### OTA Updates

```bash
## Push update without app store review
eas update --branch production --message "Bug fixes and improvements"
```

---

### 🎯 Scaling Strategy

#### Horizontal Scaling

```bash
## Add more app servers
doctl compute droplet create idrm-prod-app-3 idrm-prod-app-4 \
  --size s-2vcpu-4gb \
  --image ubuntu-22-04-x64 \
  --region nyc3

## Add to load balancer
doctl compute load-balancer add-droplets <lb-id> \
  --droplet-ids <app-3-id>,<app-4-id>
```

#### Database Scaling

```bash
## Read replicas for analytics
doctl databases replica create <db-id> \
  --name idrm-prod-db-replica \
  --region nyc3 \
  --size db-s-4vcpu-8gb
```

---

**IDRM v3 Production: Enterprise-Grade Multi-Platform Deployment!** 🚀

**Uptime Target**: 99.9%  
**Deployment**: Zero-downtime blue-green  
**Monitoring**: Real-time with alerts  
**Next**: See `production-ci-cd-readme-v3.md` for CI/CD details

---

## IDRM: Complete Deployment Guide

### From Development to Production - The Complete Journey

**Version**: 3.0 Unified  
**Audience**: Complete beginners, DevOps engineers, System administrators  
**Reading Time**: 4-6 hours (but worth it!)  
**Last Updated**: May 16, 2026

---

### 🎯 **What This Document Covers**

This is your **ONE-STOP deployment guide** for IDRM. Think of it as a complete roadmap from:
- 💻 **Development** (your laptop) → 
- 🧪 **Staging** (testing server) → 
- 🚀 **Production** (live for users) → 
- 🤖 **Automation** (CI/CD pipelines)

**You'll learn**:
- ✅ How to set up each environment
- ✅ What each environment is for
- ✅ Step-by-step instructions
- ✅ Troubleshooting common issues
- ✅ Security best practices
- ✅ Automated deployments

---

### 📚 **Table of Contents**

#### **Part 1: Understanding Deployments**
1. [What Are Environments?](#part-1-understanding-deployments)
2. [The Deployment Journey](#the-deployment-journey)
3. [Technology Stack Overview](#technology-stack-overview)

#### **Part 2: Development Environment**
4. [Development Setup (Your Laptop)](#part-2-development-environment)
5. [Local Development Workflow](#local-development-workflow)
6. [Common Development Issues](#common-development-issues)

#### **Part 3: Staging Environment**
7. [What Is Staging?](#part-3-staging-environment)
8. [Staging Server Setup](#staging-server-setup)
9. [Docker Deployment](#docker-deployment)
10. [Testing in Staging](#testing-in-staging)

#### **Part 4: Production Environment**
11. [Production Server Setup](#part-4-production-environment)
12. [Security Hardening](#security-hardening)
13. [SSL/TLS Configuration](#ssltls-configuration)
14. [Load Balancing & Scaling](#load-balancing--scaling)
15. [Monitoring & Logging](#monitoring--logging)
16. [Backup & Recovery](#backup--recovery)

#### **Part 5: CI/CD Pipelines**
17. [What Is CI/CD?](#part-5-cicd-pipelines)
18. [GitHub Actions Setup](#github-actions-setup)
19. [Automated Testing](#automated-testing)
20. [Automated Deployment](#automated-deployment)

#### **Part 6: Maintenance & Operations**
21. [Daily Operations](#part-6-maintenance--operations)
22. [Incident Response](#incident-response)
23. [Performance Optimization](#performance-optimization)

---

## **PART 1: Understanding Deployments**

### 1. **What Are Environments?**

#### 1.1 Simple Explanation

**Environments** = Different versions of your application running in different places

**Real-World Analogy**:

```
Building a Restaurant:
┌─────────────────────────────────────────────┐
│ 1. HOME KITCHEN (Development)               │
│    - You test recipes                       │
│    - Make mistakes, no problem              │
│    - Only you eat the food                  │
│                                             │
│ 2. FRIENDS & FAMILY NIGHT (Staging)        │
│    - Real kitchen, real environment         │
│    - Invite trusted people                  │
│    - Get feedback, fix issues               │
│                                             │
│ 3. GRAND OPENING (Production)              │
│    - Real customers                         │
│    - Everything must work perfectly         │
│    - Your reputation depends on it          │
└─────────────────────────────────────────────┘

Building IDRM:
┌─────────────────────────────────────────────┐
│ 1. DEVELOPMENT (Your Laptop)                │
│    - Write code                             │
│    - Test features                          │
│    - Break things safely                    │
│                                             │
│ 2. STAGING (Test Server)                   │
│    - Exact copy of production               │
│    - Team tests thoroughly                  │
│    - Catch bugs before users see them       │
│                                             │
│ 3. PRODUCTION (Live Server)                │
│    - Real users                             │
│    - 24/7 availability                      │
│    - Zero downtime goal                     │
└─────────────────────────────────────────────┘
```

---

#### 1.2 Environment Comparison

| Aspect | Development | Staging | Production |
|--------|-------------|---------|------------|
| **Purpose** | Write & test code | Pre-production testing | Serve real users |
| **Location** | Your laptop | Test server | Production servers |
| **Data** | Fake/test data | Fake but realistic | Real user data |
| **Users** | Just you | Team + testers | Everyone |
| **Mistakes OK?** | ✅ Yes! | ⚠️ Somewhat | ❌ NO! |
| **Speed** | Fast changes | Moderate | Careful changes |
| **Cost** | Free (your time) | Low (1 server) | High (multiple servers) |
| **Uptime** | Doesn't matter | Should be stable | 99.9%+ required |

---

### 2. **The Deployment Journey**

#### 2.1 Complete Flow (Beginner-Friendly)

```
WEEK 1-8: DEVELOPMENT
┌──────────────────────────────────────┐
│ You: Write code on laptop            │
│ Git: Save code to GitHub             │
│ Test: Run on http://localhost:8000   │
│ Repeat: Fix bugs, add features       │
└──────────────────────────────────────┘
         ↓
         ↓ (Code ready!)
         ↓

WEEK 9-12: STAGING
┌──────────────────────────────────────┐
│ Deploy: Push code to test server     │
│ Test: Team tests on staging.idrm.gov.in │
│ Find: Discover bugs in real environment │
│ Fix: Go back to development, fix bugs  │
│ Repeat: Until everything works         │
└──────────────────────────────────────┘
         ↓
         ↓ (Everything tested!)
         ↓

WEEK 13+: PRODUCTION
┌──────────────────────────────────────┐
│ Deploy: Push to production servers   │
│ Monitor: Watch for issues            │
│ Maintain: Fix bugs, add features     │
│ Scale: Add servers as users grow    │
└──────────────────────────────────────┘

WEEK 10+: CI/CD AUTOMATION
┌──────────────────────────────────────┐
│ Automate: Tests run automatically    │
│ Deploy: Automatic deployment         │
│ Monitor: Alerts if something breaks  │
└──────────────────────────────────────┘
```

---

#### 2.2 Timeline

**Realistic Timeline for IDRM**:

```
Month 1-2: Development
├─ Week 1-2:  Backend foundation
├─ Week 3-4:  Frontend basics
├─ Week 5-6:  Core features
└─ Week 7-8:  Polish & bug fixes

Month 3: Staging
├─ Week 9:    Deploy to staging
├─ Week 10:   Team testing
├─ Week 11:   Fix critical bugs
└─ Week 12:   Final staging tests

Month 4: Production
├─ Week 13:   Production deployment
├─ Week 14:   Monitor & stabilize
├─ Week 15:   First real users
└─ Week 16:   Scale & optimize

Ongoing: Maintenance
├─ Daily:     Monitor logs
├─ Weekly:    Deploy bug fixes
├─ Monthly:   Add features
└─ Quarterly: Major updates
```

---

### 3. **Technology Stack Overview**

#### 3.1 Complete Stack

```
FRONTEND:
├─ HTML/CSS (Pages & styling)
├─ JavaScript (Interactivity)
├─ Tailwind CSS (UI framework)
├─ Leaflet.js (Maps)
└─ Chart.js (Visualizations)

BACKEND:
├─ Python 3.11+ (Programming language)
├─ FastAPI (Web framework)
├─ Uvicorn (ASGI server)
└─ Gunicorn (Production server)

DATABASE:
├─ PostgreSQL 15+ (Main database)
├─ PostGIS (Spatial extension)
└─ pgAdmin (Management tool)

CACHING:
├─ Redis 7+ (In-memory cache)
└─ Redis Commander (Management tool)

INFRASTRUCTURE:
├─ Docker (Containerization)
├─ Docker Compose (Multi-container)
├─ NGINX (Reverse proxy)
└─ Let's Encrypt (SSL certificates)

MONITORING:
├─ Prometheus (Metrics)
├─ Grafana (Dashboards)
└─ Sentry (Error tracking)

CI/CD:
├─ GitHub Actions (Automation)
├─ Docker Hub (Container registry)
└─ SSH (Deployment)
```

---

#### 3.2 Ports & Services

**Port Reference** (memorize this!):

| Service | Development | Staging | Production |
|---------|-------------|---------|------------|
| **Frontend** | 3000 | 80 → 3000 | 80/443 → 3000 |
| **Backend API** | 8000 | 80 → 8000 | 80/443 → 8000 |
| **PostgreSQL** | 5432 | 5432 (internal) | 5432 (internal) |
| **Redis** | 6379 | 6379 (internal) | 6379 (internal) |
| **NGINX** | - | 80, 443 | 80, 443 |
| **Prometheus** | - | 9090 (internal) | 9090 (internal) |
| **Grafana** | - | 3001 (internal) | 3001 (internal) |

**Remember**:
- Development: Direct access (localhost)
- Staging/Production: Through NGINX reverse proxy

---

## **PART 2: Development Environment**

### 4. **Development Setup (Your Laptop)**

#### 4.1 Prerequisites

**What You Need**:

```
Hardware:
- CPU: 4+ cores (8 recommended)
- RAM: 8 GB minimum (16 GB recommended)
- Disk: 50 GB free space (SSD recommended)
- Internet: Required for downloads

Software to Install:
1. Operating System: Ubuntu 22.04/24.04 (or Windows with WSL2, or macOS)
2. Python: 3.11+
3. Node.js: 18+ (for frontend development)
4. PostgreSQL: 15+
5. Redis: 7+
6. Git: Latest version
7. Code Editor: VS Code recommended
```

---

#### 4.2 Step-by-Step Installation

##### **Step 1: Install Python 3.11**

**Ubuntu/Debian**:
```bash
## Update package list
sudo apt update

## Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

## Verify installation
python3.11 --version  # Should show: Python 3.11.x
```

**macOS**:
```bash
## Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

## Install Python
brew install python@3.11

## Verify
python3.11 --version
```

**Windows (WSL2)**:
```powershell
## Install WSL2 first
wsl --install -d Ubuntu-22.04

## Then follow Ubuntu instructions above
```

---

##### **Step 2: Install PostgreSQL 15**

**Ubuntu/Debian**:
```bash
## Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

## Install PostgreSQL + PostGIS
sudo apt update
sudo apt install postgresql-15 postgresql-15-postgis-3

## Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

## Verify
psql --version  # Should show: psql (PostgreSQL) 15.x
```

**macOS**:
```bash
## Install PostgreSQL
brew install postgresql@15 postgis

## Start PostgreSQL
brew services start postgresql@15

## Verify
psql --version
```

---

##### **Step 3: Install Redis**

**Ubuntu/Debian**:
```bash
## Install Redis
sudo apt install redis-server

## Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

## Verify
redis-cli ping  # Should return: PONG
```

**macOS**:
```bash
## Install Redis
brew install redis

## Start Redis
brew services start redis

## Verify
redis-cli ping
```

---

##### **Step 4: Install Git**

**Ubuntu/Debian**:
```bash
sudo apt install git

git --version
```

**macOS**:
```bash
brew install git

git --version
```

---

##### **Step 5: Install VS Code**

**Download from**: https://code.visualstudio.com/

**Recommended Extensions**:
- Python (Microsoft)
- Pylance
- PostgreSQL (Chris Kolkman)
- Redis (Dunn)
- GitLens
- Better Comments
- Tailwind CSS IntelliSense

---

#### 4.3 Clone & Setup IDRM

##### **Step 1: Clone Repository**

```bash
## Create workspace directory
mkdir -p ~/projects
cd ~/projects

## Clone repository
git clone https://github.com/your-org/idrm.git
cd idrm

## Check structure
ls -la
```

**You should see**:
```
idrm/
├── backend/          (Python/FastAPI)
├── frontend/         (HTML/CSS/JS)
├── database/         (SQL schemas)
├── docker/           (Docker configs)
├── docs/             (Documentation)
├── tests/            (Test files)
├── .env.example      (Environment template)
├── README.md
└── requirements.txt
```

---

##### **Step 2: Create Python Virtual Environment**

```bash
## Navigate to backend
cd backend

## Create virtual environment
python3.11 -m venv venv

## Activate virtual environment
source venv/bin/activate  # Linux/macOS
## OR
venv\Scripts\activate     # Windows

## You should see (venv) in your prompt:
(venv) user@laptop:~/projects/idrm/backend$
```

---

##### **Step 3: Install Python Dependencies**

```bash
## Make sure venv is activated!
(venv) $ pip install --upgrade pip

## Install all dependencies
(venv) $ pip install -r requirements.txt

## Verify critical packages
(venv) $ pip list | grep fastapi
fastapi                   0.109.0
(venv) $ pip list | grep psycopg
psycopg[binary]           3.1.13
```

**Dependencies Installed**:
```
Core:
- fastapi (Web framework)
- uvicorn (ASGI server)
- pydantic (Data validation)

Database:
- psycopg[binary] (PostgreSQL driver)
- sqlalchemy (ORM)
- alembic (Migrations)

Authentication:
- python-jose (JWT tokens)
- passlib (Password hashing)
- bcrypt (Hash algorithm)

Utilities:
- python-dotenv (Environment variables)
- redis (Redis client)
- httpx (HTTP client for testing)
```

---

##### **Step 4: Create Database**

```bash
## Switch to postgres user
sudo -u postgres psql

## Inside PostgreSQL shell:
postgres=# CREATE DATABASE idrm_dev;
postgres=# CREATE USER idrm_user WITH PASSWORD 'dev_password_123';
postgres=# GRANT ALL PRIVILEGES ON DATABASE idrm_dev TO idrm_user;

## Enable PostGIS extension
postgres=# \c idrm_dev
idrm_dev=# CREATE EXTENSION postgis;
idrm_dev=# CREATE EXTENSION pg_trgm;  -- For full-text search

## Verify
idrm_dev=# SELECT PostGIS_version();
## Should show PostGIS version

## Exit
idrm_dev=# \q
```

---

##### **Step 5: Configure Environment Variables**

```bash
## Navigate to backend directory
cd ~/projects/idrm/backend

## Copy example env file
cp .env.example .env

## Edit .env file
nano .env
```

**`.env` file content**:
```bash
## Application
APP_NAME=IDRM
APP_ENV=development
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production-abc123xyz789
API_VERSION=v1

## Server
HOST=127.0.0.1
PORT=8000
RELOAD=true

## Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=idrm_dev
DB_USER=idrm_user
DB_PASSWORD=dev_password_123
DATABASE_URL=postgresql://idrm_user:dev_password_123@localhost:5432/idrm_dev

## Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

## JWT Authentication
JWT_SECRET_KEY=jwt-dev-secret-key-change-in-production-xyz789
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

## CORS (Frontend URLs allowed)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

## Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@idrm.gov.in

## File Upload
MAX_UPLOAD_SIZE=10485760  # 10MB in bytes
UPLOAD_DIR=./uploads

## Logging
LOG_LEVEL=INFO
LOG_FILE=logs/idrm.log
```

**Save and exit** (Ctrl+X, Y, Enter in nano)

---

##### **Step 6: Run Database Migrations**

```bash
## Make sure venv is activated
(venv) $ cd ~/projects/idrm/backend

## Initialize Alembic (first time only)
(venv) $ alembic init alembic

## Create initial migration
(venv) $ alembic revision --autogenerate -m "Initial schema"

## Apply migrations
(venv) $ alembic upgrade head

## Verify tables created
psql -U idrm_user -d idrm_dev -c "\dt"
```

**You should see tables**:
```
 Schema |       Name        | Type  |   Owner   
--------+-------------------+-------+-----------
 public | alembic_version   | table | idrm_user
 public | users             | table | idrm_user
 public | organizations     | table | idrm_user
 public | service_requests  | table | idrm_user
 ...
```

---

##### **Step 7: Create Test Data (Optional)**

```bash
## Create seed script
(venv) $ python scripts/seed_database.py

## This creates:
## - Test users (all roles)
## - Test organizations
## - Sample service requests
```

**Default test users created**:
```
Admin:
- Email: admin@idrm.gov.in
- Password: Admin@123
- Role: SYSTEM_ADMIN

Citizen:
- Email: citizen@example.com
- Password: Citizen@123
- Role: CITIZEN

Provider:
- Email: provider@example.com
- Password: Provider@123
- Role: SERVICE_PROVIDER
```

---

#### 4.4 Start Development Server

##### **Start Backend**

```bash
## Terminal 1: Backend
cd ~/projects/idrm/backend
source venv/bin/activate

## Start FastAPI with auto-reload
(venv) $ uvicorn main:app --reload --host 127.0.0.1 --port 8000

## You should see:
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test it**:
```bash
## In another terminal
curl http://localhost:8000/api/v1/health

## Should return:
{"status":"healthy","timestamp":"2026-05-16T10:00:00Z"}
```

---

##### **Start Frontend**

```bash
## Terminal 2: Frontend (simple HTTP server)
cd ~/projects/idrm/frontend

## Python HTTP server (simplest option)
python3 -m http.server 3000

## OR Node.js (if you have it)
npx http-server -p 3000

## You should see:
Serving HTTP on 0.0.0.0 port 3000 (http://0.0.0.0:3000/) ...
```

**Access application**:
```
Frontend: http://localhost:3000
Backend API: http://localhost:8000
API Docs: http://localhost:8000/docs
```

---

#### 4.5 Development Workflow

##### **Daily Workflow**

```bash
## 1. Start your day
cd ~/projects/idrm/backend
source venv/bin/activate

## 2. Pull latest changes
git pull origin main

## 3. Start servers
## Terminal 1: Backend
uvicorn main:app --reload --port 8000

## Terminal 2: Frontend
cd ../frontend
python3 -m http.server 3000

## 4. Code, test, commit
## ... make changes ...

## 5. Run tests
pytest

## 6. Commit changes
git add .
git commit -m "feat: add new feature"
git push origin feature-branch

## 7. End of day - stop servers
## Ctrl+C in both terminals
```

---

### 5. **Local Development Workflow**

#### 5.1 Making Changes

##### **Backend Changes**

```bash
## 1. Create feature branch
git checkout -b feature/add-notification-system

## 2. Make changes to code
## Edit files in backend/app/

## 3. Run tests
pytest

## 4. Test manually in browser
## http://localhost:8000/docs

## 5. Commit
git add .
git commit -m "feat: add notification system"

## 6. Push
git push origin feature/add-notification-system
```

---

##### **Database Changes**

```bash
## 1. Modify models in backend/app/models/

## 2. Create migration
alembic revision --autogenerate -m "Add notifications table"

## 3. Review migration file
## Check alembic/versions/xxx_add_notifications_table.py

## 4. Apply migration
alembic upgrade head

## 5. Verify
psql -U idrm_user -d idrm_dev -c "\d notifications"
```

---

##### **Frontend Changes**

```bash
## 1. Edit HTML/CSS/JS files
## frontend/app/dashboard.html

## 2. Refresh browser to see changes
## http://localhost:3000/app/dashboard.html

## 3. Test on different browsers
## Chrome, Firefox, Safari

## 4. Commit
git add frontend/
git commit -m "feat: improve dashboard UI"
```

---

#### 5.2 Testing

##### **Run All Tests**

```bash
## Backend tests
cd backend
pytest

## With coverage
pytest --cov=app --cov-report=html

## Specific test file
pytest tests/test_services.py

## Specific test
pytest tests/test_services.py::test_create_service
```

---

##### **Manual Testing Checklist**

```
Authentication:
- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials
- [ ] Logout
- [ ] Access protected endpoint without token
- [ ] Refresh expired token

Service Requests:
- [ ] Create service request
- [ ] View service details
- [ ] Update service
- [ ] Cancel service
- [ ] Accept service (as provider)
- [ ] Complete service
- [ ] Verify service

Map Features:
- [ ] View services on map
- [ ] Search by location
- [ ] Filter by service type
- [ ] Cluster nearby services
```

---

### 6. **Common Development Issues**

#### 6.1 Database Connection Errors

**Problem**: `psycopg.OperationalError: connection refused`

**Solutions**:
```bash
## 1. Check if PostgreSQL is running
sudo systemctl status postgresql

## 2. Start PostgreSQL if not running
sudo systemctl start postgresql

## 3. Check connection settings in .env
## Make sure DB_HOST=localhost, DB_PORT=5432

## 4. Test connection manually
psql -U idrm_user -d idrm_dev -h localhost

## 5. Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log
```

---

**Problem**: `psycopg.OperationalError: password authentication failed`

**Solutions**:
```bash
## 1. Verify password in .env matches database

## 2. Reset user password
sudo -u postgres psql
postgres=# ALTER USER idrm_user WITH PASSWORD 'new_password';

## 3. Update .env with new password

## 4. Restart backend server
```

---

#### 6.2 Redis Connection Errors

**Problem**: `redis.exceptions.ConnectionError`

**Solutions**:
```bash
## 1. Check if Redis is running
redis-cli ping

## 2. Start Redis if not running
sudo systemctl start redis-server

## 3. Check Redis config
redis-cli
127.0.0.1:6379> CONFIG GET bind
127.0.0.1:6379> CONFIG GET port

## 4. Test connection
redis-cli
127.0.0.1:6379> SET test "hello"
127.0.0.1:6379> GET test
```

---

#### 6.3 Import Errors

**Problem**: `ModuleNotFoundError: No module named 'fastapi'`

**Solutions**:
```bash
## 1. Check if virtual environment is activated
## You should see (venv) in prompt

## 2. Activate if not active
source venv/bin/activate

## 3. Reinstall dependencies
pip install -r requirements.txt

## 4. Verify installation
pip list | grep fastapi
```

---

#### 6.4 Port Already in Use

**Problem**: `Error: [Errno 98] Address already in use`

**Solutions**:
```bash
## 1. Find process using port 8000
lsof -i :8000

## 2. Kill the process
kill -9 <PID>

## 3. Or use different port
uvicorn main:app --reload --port 8001
```

---

#### 6.5 CORS Errors

**Problem**: Browser console shows CORS error

**Solutions**:
```python
## 1. Check CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000

## 2. Verify CORS middleware in main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

## 3. Restart backend server
```

---

## **PART 3: Staging Environment**

### 7. **What Is Staging?**

#### 7.1 Staging Explained

**Staging** = A copy of production for final testing

**Why You Need It**:
```
Development:
✅ Fast changes
✅ Lots of bugs OK
❌ Not like real world

Production:
✅ Real users
✅ Must be perfect
❌ Too risky to test

Staging:
✅ Exactly like production
✅ Safe to test
✅ Catch bugs before users see them
```

---

#### 7.2 Staging vs Development vs Production

| Aspect | Development | Staging | Production |
|--------|-------------|---------|------------|
| **Environment** | Laptop | Single server | Multiple servers |
| **Data** | Fake | Fake but realistic | Real |
| **Database** | SQLite/PostgreSQL | PostgreSQL | PostgreSQL cluster |
| **Redis** | Optional | Redis | Redis cluster |
| **SSL** | No | Yes (staging cert) | Yes (production cert) |
| **Domain** | localhost | staging.idrm.gov.in | idrm.gov.in |
| **Monitoring** | No | Basic | Full monitoring |
| **Backups** | No | Daily | Hourly |
| **Users** | Just you | Team | Everyone |

---

### 8. **Staging Server Setup**

#### 8.1 Server Requirements

**Minimum Specs**:
```
Cloud Provider: AWS, DigitalOcean, Linode, etc.
OS: Ubuntu 24.04 LTS
CPU: 4 cores (8 recommended)
RAM: 8 GB (16 GB recommended)
Disk: 100 GB SSD (200 GB recommended)
Network: 100 Mbps+
```

**Cost Estimate**:
- DigitalOcean: $48/month (4 vCPU, 8GB RAM)
- AWS EC2: ~$60/month (t3.large)
- Linode: $48/month (8GB plan)

---

#### 8.2 Initial Server Setup

##### **Step 1: Create Server**

**DigitalOcean Example**:
```
1. Login to DigitalOcean
2. Click "Create" → "Droplets"
3. Choose:
   - Image: Ubuntu 24.04 LTS
   - Plan: Basic ($48/month - 4 vCPU, 8GB RAM)
   - Datacenter: Closest to your users
   - Add SSH key
4. Create Droplet
5. Note the IP address: 203.0.113.100
```

---

##### **Step 2: Initial Connection**

```bash
## SSH into server
ssh root@203.0.113.100

## Update system
apt update
apt upgrade -y

## Install basic tools
apt install -y curl wget git vim ufw
```

---

##### **Step 3: Create Deploy User**

```bash
## Create user
adduser deploy

## Add to sudo group
usermod -aG sudo deploy

## Setup SSH for deploy user
mkdir -p /home/deploy/.ssh
cp /root/.ssh/authorized_keys /home/deploy/.ssh/
chown -R deploy:deploy /home/deploy/.ssh
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys

## Test login
## In your local terminal:
ssh deploy@203.0.113.100
```

---

##### **Step 4: Configure Firewall**

```bash
## SSH back as root or use sudo
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

## Verify
sudo ufw status
```

---

#### 8.3 Install Docker

```bash
## Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

## Add deploy user to docker group
sudo usermod -aG docker deploy

## Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

## Logout and login again for group changes
exit
ssh deploy@203.0.113.100

## Verify
docker --version
docker compose version
```

---

### 9. **Docker Deployment**

#### 9.1 Project Structure for Deployment

```
/home/deploy/idrm/
├── docker-compose.yml
├── .env.staging
├── nginx/
│   ├── nginx.conf
│   └── ssl/  (SSL certificates)
├── backend/
│   ├── Dockerfile
│   ├── app/
│   └── requirements.txt
├── frontend/
│   └── (HTML/CSS/JS files)
├── database/
│   ├── init.sql
│   └── backups/
└── logs/
    ├── nginx/
    ├── backend/
    └── postgresql/
```

---

#### 9.2 Docker Compose Configuration

**Create `/home/deploy/idrm/docker-compose.yml`**:

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgis/postgis:15-3.3
    container_name: idrm_postgres_staging
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql
      - ./logs/postgresql:/var/log/postgresql
    networks:
      - idrm_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER} -d ${DB_NAME}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: idrm_redis_staging
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - idrm_network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: idrm_backend_staging
    env_file:
      - .env.staging
    environment:
      - DB_HOST=postgres
      - REDIS_HOST=redis
    volumes:
      - ./backend/app:/app/app
      - ./backend/uploads:/app/uploads
      - ./logs/backend:/app/logs
    ports:
      - "8000:8000"
    networks:
      - idrm_network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # NGINX Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: idrm_nginx_staging
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend:/usr/share/nginx/html:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - idrm_network
    depends_on:
      - backend
    restart: unless-stopped

networks:
  idrm_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
```

---

#### 9.3 Backend Dockerfile

**Create `/home/deploy/idrm/backend/Dockerfile`**:

```dockerfile
FROM python:3.11-slim

## Set working directory
WORKDIR /app

## Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

## Copy requirements
COPY requirements.txt .

## Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

## Copy application code
COPY . .

## Create directories
RUN mkdir -p /app/logs /app/uploads

## Expose port
EXPOSE 8000

## Run migrations and start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
```

---

#### 9.4 NGINX Configuration

**Create `/home/deploy/idrm/nginx/nginx.conf`**:

```nginx
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
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=30r/m;
    limit_req_zone $binary_remote_addr zone=auth_limit:10m rate=5r/m;

    # Upstream backend
    upstream backend {
        server backend:8000;
    }

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name staging.idrm.gov.in;
        
        location /.well-known/acme-challenge/ {
            root /usr/share/nginx/html;
        }
        
        location / {
            return 301 https://$server_name$request_uri;
        }
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name staging.idrm.gov.in;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/staging.idrm.gov.in.crt;
        ssl_certificate_key /etc/nginx/ssl/staging.idrm.gov.in.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers on;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

        # Frontend (static files)
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # Backend API
        location /api/ {
            limit_req zone=api_limit burst=10 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
        }

        # Authentication endpoints (stricter rate limit)
        location /api/v1/auth/ {
            limit_req zone=auth_limit burst=2 nodelay;
            
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint (no rate limit)
        location /api/v1/health {
            proxy_pass http://backend;
            access_log off;
        }
    }
}
```

---

#### 9.5 Environment Configuration

**Create `/home/deploy/idrm/.env.staging`**:

```bash
## Application
APP_NAME=IDRM
APP_ENV=staging
DEBUG=false
SECRET_KEY=staging-secret-key-CHANGE-THIS-abc123xyz789
API_VERSION=v1

## Server
HOST=0.0.0.0
PORT=8000

## Database
DB_HOST=postgres
DB_PORT=5432
DB_NAME=idrm_staging
DB_USER=idrm_user
DB_PASSWORD=CHANGE-THIS-strong-password-123
DATABASE_URL=postgresql://idrm_user:CHANGE-THIS-strong-password-123@postgres:5432/idrm_staging

## Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=CHANGE-THIS-redis-password-456
REDIS_URL=redis://:CHANGE-THIS-redis-password-456@redis:6379/0

## JWT Authentication
JWT_SECRET_KEY=CHANGE-THIS-jwt-secret-key-xyz789abc123
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

## CORS
CORS_ORIGINS=https://staging.idrm.gov.in

## Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=staging@idrm.gov.in
SMTP_PASSWORD=CHANGE-THIS-smtp-password
FROM_EMAIL=noreply@idrm.gov.in

## File Upload
MAX_UPLOAD_SIZE=10485760
UPLOAD_DIR=/app/uploads

## Logging
LOG_LEVEL=INFO
LOG_FILE=/app/logs/idrm.log
```

**⚠️ IMPORTANT: Change all passwords!**

---

#### 9.6 Deploy to Staging

##### **Step 1: Clone Repository**

```bash
## SSH into staging server
ssh deploy@203.0.113.100

## Clone repository
cd /home/deploy
git clone https://github.com/your-org/idrm.git
cd idrm

## Checkout main branch
git checkout main
```

---

##### **Step 2: Configure Environment**

```bash
## Copy environment file
cp .env.example .env.staging

## Edit with your values
nano .env.staging

## Change all passwords and secrets!
```

---

##### **Step 3: Get SSL Certificate**

```bash
## Install Certbot
sudo apt install certbot

## Get certificate
sudo certbot certonly --standalone -d staging.idrm.gov.in

## Copy certificates
sudo mkdir -p /home/deploy/idrm/nginx/ssl
sudo cp /etc/letsencrypt/live/staging.idrm.gov.in/fullchain.pem /home/deploy/idrm/nginx/ssl/staging.idrm.gov.in.crt
sudo cp /etc/letsencrypt/live/staging.idrm.gov.in/privkey.pem /home/deploy/idrm/nginx/ssl/staging.idrm.gov.in.key
sudo chown -R deploy:deploy /home/deploy/idrm/nginx/ssl
```

---

##### **Step 4: Build and Start**

```bash
## Build containers
docker compose build

## Start services
docker compose up -d

## Check status
docker compose ps

## Should see all services "Up" and "healthy"
```

---

##### **Step 5: Initialize Database**

```bash
## Run migrations
docker compose exec backend alembic upgrade head

## Verify tables
docker compose exec postgres psql -U idrm_user -d idrm_staging -c "\dt"

## Create admin user
docker compose exec backend python scripts/create_admin.py
```

---

##### **Step 6: Test Staging**

```bash
## Test health endpoint
curl https://staging.idrm.gov.in/api/v1/health

## Should return:
{"status":"healthy","timestamp":"2026-05-16T10:00:00Z"}

## Test frontend
## Open browser: https://staging.idrm.gov.in
```

---

### 10. **Testing in Staging**

#### 10.1 Staging Testing Checklist

```
Smoke Tests (5 minutes):
- [ ] Frontend loads
- [ ] API health check passes
- [ ] Can register new user
- [ ] Can login
- [ ] Can create service request

Functional Tests (30 minutes):
- [ ] All user workflows work
- [ ] Map displays correctly
- [ ] File uploads work
- [ ] Email notifications sent
- [ ] Search functionality works

Performance Tests (15 minutes):
- [ ] Page load times < 2s
- [ ] API response times < 500ms
- [ ] Can handle 10 concurrent users

Security Tests (30 minutes):
- [ ] HTTPS works
- [ ] No mixed content warnings
- [ ] XSS protection works
- [ ] SQL injection prevented
- [ ] CSRF tokens working

Integration Tests (1 hour):
- [ ] Complete citizen workflow
- [ ] Complete provider workflow
- [ ] Admin dashboard works
- [ ] Analytics accurate
```

---

#### 10.2 Load Testing

**Install Apache Bench**:
```bash
sudo apt install apache2-utils
```

**Test API**:
```bash
## Test health endpoint (100 requests, 10 concurrent)
ab -n 100 -c 10 https://staging.idrm.gov.in/api/v1/health

## Test login endpoint
ab -n 50 -c 5 -p login.json -T application/json https://staging.idrm.gov.in/api/v1/auth/login
```

**Expected Results**:
```
Requests per second: > 100
Time per request: < 100ms
Failed requests: 0
```

---

#### 10.3 Monitoring Staging

**View Logs**:
```bash
## All services
docker compose logs -f

## Specific service
docker compose logs -f backend

## Last 100 lines
docker compose logs --tail=100 nginx

## Specific time range
docker compose logs --since=2024-05-16T10:00:00
```

**Check Resources**:
```bash
## Container stats
docker stats

## Disk usage
df -h

## Memory usage
free -h
```

---

## **PART 4: Production Environment**

### 11. **Production Server Setup**

#### 11.1 Production Requirements

**Minimum Infrastructure**:

```
Web Servers (2+):
- Purpose: Serve frontend & API
- Specs: 8 vCPU, 16GB RAM, 200GB SSD each
- OS: Ubuntu 24.04 LTS
- Provider: AWS, DigitalOcean, Linode
- Cost: ~$96/month each = $192/month

Database Server (1):
- Purpose: PostgreSQL + PostGIS
- Specs: 8 vCPU, 32GB RAM, 500GB SSD
- OS: Ubuntu 24.04 LTS
- RAID 1 for redundancy
- Cost: ~$192/month

Redis Server (1):
- Purpose: Cache & sessions
- Specs: 4 vCPU, 8GB RAM, 100GB SSD
- OS: Ubuntu 24.04 LTS
- Cost: ~$48/month

Load Balancer (1):
- Purpose: Distribute traffic
- Managed service recommended
- Provider: AWS ALB, DigitalOcean LB
- Cost: ~$10-20/month

Total Monthly Cost: ~$450-500/month
```

**Scalable Infrastructure** (for growth):

```
Web Servers (5+):
Auto-scaling group: 2-10 instances

Database:
- Primary + Read Replica
- Managed PostgreSQL (AWS RDS, DO Managed DB)
- Automatic backups

Redis:
- Redis Cluster (3 nodes)
- Managed Redis recommended

CDN:
- CloudFlare or AWS CloudFront
- Static asset caching

Total Monthly Cost: $800-1500/month
```

---

#### 11.2 Server Security Hardening

##### **Step 1: SSH Security**

```bash
## Disable root login
sudo nano /etc/ssh/sshd_config

## Change these settings:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222  # Change default port

## Restart SSH
sudo systemctl restart sshd

## Now connect using:
ssh -p 2222 deploy@production-server
```

---

##### **Step 2: Install Fail2Ban**

```bash
## Install Fail2Ban
sudo apt install fail2ban

## Create custom config
sudo nano /etc/fail2ban/jail.local
```

**Fail2Ban configuration**:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
```

```bash
## Start Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

## Check status
sudo fail2ban-client status
```

---

##### **Step 3: Configure Firewall**

```bash
## Allow custom SSH port
sudo ufw allow 2222/tcp

## Allow HTTP & HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

## Allow from web servers to database (replace IPs)
sudo ufw allow from 203.0.113.10 to any port 5432  # Web server 1
sudo ufw allow from 203.0.113.11 to any port 5432  # Web server 2

## Deny all other incoming
sudo ufw default deny incoming
sudo ufw default allow outgoing

## Enable firewall
sudo ufw enable
```

---

#### 11.3 Production Database Setup

##### **Step 1: Install PostgreSQL**

```bash
## Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

## Install
sudo apt update
sudo apt install -y postgresql-15 postgresql-15-postgis-3

## Start
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

---

##### **Step 2: Configure PostgreSQL for Production**

```bash
## Edit PostgreSQL config
sudo nano /etc/postgresql/15/main/postgresql.conf
```

**Production settings**:
```ini
## Memory settings (for 32GB RAM server)
shared_buffers = 8GB
effective_cache_size = 24GB
maintenance_work_mem = 2GB
work_mem = 64MB

## Connection settings
max_connections = 200
superuser_reserved_connections = 3

## Write-ahead log
wal_level = replica
max_wal_size = 2GB
min_wal_size = 1GB

## Checkpoints
checkpoint_completion_target = 0.9
checkpoint_timeout = 10min

## Query planner
random_page_cost = 1.1  # For SSD

## Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_min_duration_statement = 1000  # Log queries > 1s
```

```bash
## Edit pg_hba.conf for remote access
sudo nano /etc/postgresql/15/main/pg_hba.conf
```

**Add these lines** (replace IPs with your web servers):
```
## Web servers
host    idrm_production    idrm_user    203.0.113.10/32    scram-sha-256
host    idrm_production    idrm_user    203.0.113.11/32    scram-sha-256
```

```bash
## Restart PostgreSQL
sudo systemctl restart postgresql
```

---

##### **Step 3: Create Production Database**

```bash
## Create database and user
sudo -u postgres psql

postgres=# CREATE DATABASE idrm_production;
postgres=# CREATE USER idrm_user WITH PASSWORD 'STRONG-PRODUCTION-PASSWORD-HERE';
postgres=# GRANT ALL PRIVILEGES ON DATABASE idrm_production TO idrm_user;

## Connect to database
postgres=# \c idrm_production

## Enable extensions
idrm_production=# CREATE EXTENSION postgis;
idrm_production=# CREATE EXTENSION pg_trgm;
idrm_production=# CREATE EXTENSION btree_gist;

## Verify
idrm_production=# SELECT PostGIS_version();

## Exit
idrm_production=# \q
```

---

### 12. **Security Hardening**

#### 12.1 Security Checklist

```
Infrastructure Security:
- [x] SSH key-only authentication
- [x] Firewall configured (ufw)
- [x] Fail2Ban installed
- [x] Non-standard SSH port
- [ ] VPN for database access
- [ ] Regular security updates

Application Security:
- [ ] HTTPS enforced (HTTP → HTTPS redirect)
- [ ] Strong SSL/TLS configuration
- [ ] Security headers configured
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints

Database Security:
- [ ] Strong passwords
- [ ] Network access restricted
- [ ] Regular backups
- [ ] Encrypted connections
- [ ] Audit logging enabled

Authentication:
- [ ] JWT tokens with short expiry
- [ ] Refresh tokens rotated
- [ ] Password hashing (bcrypt cost 12+)
- [ ] Rate limiting on auth endpoints
- [ ] Session invalidation on logout
```

---

#### 12.2 Environment Variables Security

**NEVER commit secrets to Git!**

```bash
## Production .env file
sudo nano /home/deploy/idrm/.env.production

## Set strict permissions
sudo chmod 600 /home/deploy/idrm/.env.production
sudo chown deploy:deploy /home/deploy/idrm/.env.production
```

**Generate strong secrets**:
```bash
## Generate random secret (32 characters)
openssl rand -hex 32

## Generate random password (16 characters)
openssl rand -base64 16
```

**Production `.env.production`**:
```bash
## Application
APP_NAME=IDRM
APP_ENV=production
DEBUG=false
SECRET_KEY=<GENERATED-SECRET-KEY-HERE>
API_VERSION=v1

## Server
HOST=0.0.0.0
PORT=8000

## Database
DB_HOST=203.0.113.20  # Database server IP
DB_PORT=5432
DB_NAME=idrm_production
DB_USER=idrm_user
DB_PASSWORD=<STRONG-DB-PASSWORD>
DATABASE_URL=postgresql://idrm_user:<PASSWORD>@203.0.113.20:5432/idrm_production

## Redis
REDIS_HOST=203.0.113.21  # Redis server IP
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=<STRONG-REDIS-PASSWORD>
REDIS_URL=redis://:<PASSWORD>@203.0.113.21:6379/0

## JWT
JWT_SECRET_KEY=<GENERATED-JWT-SECRET>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

## CORS
CORS_ORIGINS=https://idrm.gov.in

## Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@idrm.gov.in
SMTP_PASSWORD=<SMTP-APP-PASSWORD>
FROM_EMAIL=noreply@idrm.gov.in

## Sentry (Error tracking)
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

## Rate Limiting
RATE_LIMIT_PER_MINUTE=60
AUTH_RATE_LIMIT_PER_MINUTE=5
```

---

### 13. **SSL/TLS Configuration**

#### 13.1 Get SSL Certificate

**Using Let's Encrypt (Free)**:

```bash
## Install Certbot
sudo apt install certbot python3-certbot-nginx

## Stop NGINX temporarily
sudo systemctl stop nginx

## Get certificate
sudo certbot certonly --standalone -d idrm.gov.in -d www.idrm.gov.in

## Certificate files created:
## /etc/letsencrypt/live/idrm.gov.in/fullchain.pem
## /etc/letsencrypt/live/idrm.gov.in/privkey.pem

## Auto-renewal
sudo certbot renew --dry-run
```

---

#### 13.2 NGINX SSL Configuration

**Production NGINX config** (`/etc/nginx/sites-available/idrm`):

```nginx
## Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name idrm.gov.in www.idrm.gov.in;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://idrm.gov.in$request_uri;
    }
}

## HTTPS server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name idrm.gov.in www.idrm.gov.in;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/idrm.gov.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/idrm.gov.in/privkey.pem;

    # SSL configuration (Mozilla Intermediate)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_timeout 1d;
    ssl_session_cache shared:SSL:50m;
    ssl_session_tickets off;
    ssl_stapling on;
    ssl_stapling_verify on;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';" always;

    # Logging
    access_log /var/log/nginx/idrm-access.log combined;
    error_log /var/log/nginx/idrm-error.log warn;

    # Root directory
    root /var/www/idrm/frontend;
    index index.html;

    # Frontend
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        proxy_busy_buffers_size 8k;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

```bash
## Enable site
sudo ln -s /etc/nginx/sites-available/idrm /etc/nginx/sites-enabled/

## Test configuration
sudo nginx -t

## Reload NGINX
sudo systemctl reload nginx
```

---

### 14. **Load Balancing & Scaling**

#### 14.1 Load Balancer Setup

**Using NGINX as Load Balancer**:

```nginx
## /etc/nginx/nginx.conf

http {
    # Upstream backend servers
    upstream backend_servers {
        least_conn;  # Load balancing method
        
        server 203.0.113.10:8000 weight=1 max_fails=3 fail_timeout=30s;
        server 203.0.113.11:8000 weight=1 max_fails=3 fail_timeout=30s;
        
        # Add more servers as needed
        # server 203.0.113.12:8000 weight=1;
        
        # Health check
        keepalive 32;
    }

    server {
        listen 443 ssl http2;
        server_name idrm.gov.in;

        # ... SSL config ...

        location /api/ {
            proxy_pass http://backend_servers;
            
            # Proxy headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Connection reuse
            proxy_http_version 1.1;
            proxy_set_header Connection "";
        }
    }
}
```

---

#### 14.2 Auto-Scaling Strategy

**Horizontal Scaling (Add more servers)**:

```
When to scale UP (add servers):
- CPU usage > 70% for 5+ minutes
- Memory usage > 80%
- Response time > 500ms
- Request queue building up

When to scale DOWN (remove servers):
- CPU usage < 30% for 15+ minutes
- Memory usage < 50%
- Low traffic periods (night)

Minimum servers: 2 (for redundancy)
Maximum servers: 10 (cost control)
```

**Vertical Scaling (Bigger servers)**:

```
When to scale UP (bigger server):
- Consistently high CPU/RAM usage
- Database queries slow
- Cache misses high

Database scaling:
- Add read replicas for read-heavy workload
- Increase RAM for better cache
- Faster SSD/NVMe disks
```

---

### 15. **Monitoring & Logging**

#### 15.1 Prometheus & Grafana Setup

**Install Prometheus**:

```bash
## Create user
sudo useradd --no-create-home --shell /bin/false prometheus

## Download Prometheus
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar -xvf prometheus-2.45.0.linux-amd64.tar.gz
cd prometheus-2.45.0.linux-amd64

## Move files
sudo mv prometheus promtool /usr/local/bin/
sudo mkdir -p /etc/prometheus /var/lib/prometheus
sudo mv consoles console_libraries /etc/prometheus/

## Create config
sudo nano /etc/prometheus/prometheus.yml
```

**Prometheus config**:
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # IDRM Backend
  - job_name: 'idrm_backend'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['203.0.113.20:9187']

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['203.0.113.21:9121']

  # Node Exporter (system metrics)
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
```

**Create systemd service**:
```bash
sudo nano /etc/systemd/system/prometheus.service
```

```ini
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/usr/local/bin/prometheus \
  --config.file=/etc/prometheus/prometheus.yml \
  --storage.tsdb.path=/var/lib/prometheus/ \
  --web.console.templates=/etc/prometheus/consoles \
  --web.console.libraries=/etc/prometheus/console_libraries

[Install]
WantedBy=multi-user.target
```

```bash
## Set permissions
sudo chown -R prometheus:prometheus /etc/prometheus /var/lib/prometheus

## Start Prometheus
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus

## Verify
sudo systemctl status prometheus
```

---

**Install Grafana**:

```bash
## Add Grafana repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -

## Install
sudo apt-get update
sudo apt-get install grafana

## Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

## Access Grafana
## http://server-ip:3000
## Default login: admin/admin
```

**Configure Grafana**:
```
1. Login to Grafana (http://server-ip:3000)
2. Add Prometheus data source:
   - URL: http://localhost:9090
3. Import dashboards:
   - NGINX: Dashboard ID 12708
   - PostgreSQL: Dashboard ID 9628
   - Redis: Dashboard ID 11835
   - Node Exporter: Dashboard ID 1860
```

---

#### 15.2 Log Management

**Centralized Logging with Loki**:

```bash
## Install Loki
cd /tmp
wget https://github.com/grafana/loki/releases/download/v2.9.0/loki-linux-amd64.zip
unzip loki-linux-amd64.zip
sudo mv loki-linux-amd64 /usr/local/bin/loki

## Create config
sudo mkdir /etc/loki
sudo nano /etc/loki/config.yml
```

**Loki config**:
```yaml
auth_enabled: false

server:
  http_listen_port: 3100

ingester:
  lifecycler:
    address: 127.0.0.1
    ring:
      kvstore:
        store: inmemory
      replication_factor: 1
  chunk_idle_period: 5m
  chunk_retain_period: 30s

schema_config:
  configs:
    - from: 2023-01-01
      store: boltdb-shipper
      object_store: filesystem
      schema: v11
      index:
        prefix: index_
        period: 24h

storage_config:
  boltdb_shipper:
    active_index_directory: /var/lib/loki/index
    cache_location: /var/lib/loki/cache
    shared_store: filesystem
  filesystem:
    directory: /var/lib/loki/chunks

limits_config:
  enforce_metric_name: false
  reject_old_samples: true
  reject_old_samples_max_age: 168h

chunk_store_config:
  max_look_back_period: 0s

table_manager:
  retention_deletes_enabled: true
  retention_period: 720h
```

```bash
## Create directories
sudo mkdir -p /var/lib/loki/{index,cache,chunks}
sudo useradd --no-create-home --shell /bin/false loki
sudo chown -R loki:loki /var/lib/loki /etc/loki

## Create systemd service
sudo nano /etc/systemd/system/loki.service
```

```ini
[Unit]
Description=Loki
After=network.target

[Service]
Type=simple
User=loki
ExecStart=/usr/local/bin/loki -config.file=/etc/loki/config.yml

[Install]
WantedBy=multi-user.target
```

```bash
## Start Loki
sudo systemctl daemon-reload
sudo systemctl start loki
sudo systemctl enable loki
```

---

**Install Promtail (Log shipper)**:

```bash
## Download Promtail
cd /tmp
wget https://github.com/grafana/loki/releases/download/v2.9.0/promtail-linux-amd64.zip
unzip promtail-linux-amd64.zip
sudo mv promtail-linux-amd64 /usr/local/bin/promtail

## Create config
sudo nano /etc/loki/promtail-config.yml
```

```yaml
server:
  http_listen_port: 9080
  grpc_listen_port: 0

positions:
  filename: /var/lib/promtail/positions.yaml

clients:
  - url: http://localhost:3100/loki/api/v1/push

scrape_configs:
  # NGINX logs
  - job_name: nginx
    static_configs:
      - targets:
          - localhost
        labels:
          job: nginx
          __path__: /var/log/nginx/*log

  # Application logs
  - job_name: idrm
    static_configs:
      - targets:
          - localhost
        labels:
          job: idrm_backend
          __path__: /var/log/idrm/*log

  # System logs
  - job_name: system
    static_configs:
      - targets:
          - localhost
        labels:
          job: system
          __path__: /var/log/syslog
```

```bash
## Create directory
sudo mkdir -p /var/lib/promtail
sudo chown -R loki:loki /var/lib/promtail

## Create systemd service
sudo nano /etc/systemd/system/promtail.service
```

```ini
[Unit]
Description=Promtail
After=network.target

[Service]
Type=simple
User=loki
ExecStart=/usr/local/bin/promtail -config.file=/etc/loki/promtail-config.yml

[Install]
WantedBy=multi-user.target
```

```bash
## Start Promtail
sudo systemctl daemon-reload
sudo systemctl start promtail
sudo systemctl enable promtail
```

---

#### 15.3 Alerting

**Configure Alertmanager**:

```bash
## Install Alertmanager
cd /tmp
wget https://github.com/prometheus/alertmanager/releases/download/v0.26.0/alertmanager-0.26.0.linux-amd64.tar.gz
tar -xvf alertmanager-0.26.0.linux-amd64.tar.gz
cd alertmanager-0.26.0.linux-amd64

sudo mv alertmanager amtool /usr/local/bin/
sudo mkdir /etc/alertmanager

## Create config
sudo nano /etc/alertmanager/alertmanager.yml
```

```yaml
global:
  smtp_smarthost: 'smtp.gmail.com:587'
  smtp_from: 'alerts@idrm.gov.in'
  smtp_auth_username: 'alerts@idrm.gov.in'
  smtp_auth_password: 'app-password-here'

route:
  group_by: ['alertname', 'cluster']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'team-emails'

receivers:
  - name: 'team-emails'
    email_configs:
      - to: 'ops-team@idrm.gov.in'
        headers:
          Subject: '[ALERT] {{ .GroupLabels.alertname }}'
```

**Create alert rules** (`/etc/prometheus/alert_rules.yml`):

```yaml
groups:
  - name: idrm_alerts
    rules:
      # High CPU usage
      - alert: HighCPU
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is {{ $value }}%"

      # High memory usage
      - alert: HighMemory
        expr: (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 < 20
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low memory on {{ $labels.instance }}"
          description: "Only {{ $value }}% memory available"

      # API response time
      - alert: SlowAPI
        expr: http_request_duration_seconds{quantile="0.95"} > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Slow API responses"
          description: "95th percentile response time is {{ $value }}s"

      # Database connections
      - alert: HighDBConnections
        expr: pg_stat_database_numbackends > 180
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "{{ $value }} database connections"

      # Service down
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ $labels.job }} is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute"
```

---

### 16. **Backup & Recovery**

#### 16.1 Database Backups

**Automated PostgreSQL Backups**:

```bash
## Create backup script
sudo nano /usr/local/bin/backup-postgres.sh
```

```bash
#!/bin/bash
## PostgreSQL Backup Script

## Configuration
BACKUP_DIR="/var/backups/postgresql"
DB_NAME="idrm_production"
DB_USER="idrm_user"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

## Create backup directory
mkdir -p $BACKUP_DIR

## Backup database
pg_dump -U $DB_USER -d $DB_NAME -F c -f "$BACKUP_DIR/idrm_${DATE}.dump"

## Backup globals (users, roles)
pg_dumpall -U postgres --globals-only -f "$BACKUP_DIR/globals_${DATE}.sql"

## Compress
gzip "$BACKUP_DIR/idrm_${DATE}.dump"
gzip "$BACKUP_DIR/globals_${DATE}.sql"

## Upload to S3 (optional)
## aws s3 cp "$BACKUP_DIR/idrm_${DATE}.dump.gz" s3://idrm-backups/postgresql/

## Delete old backups
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete

## Log
echo "$(date): Backup completed - idrm_${DATE}.dump.gz" >> /var/log/backups.log
```

```bash
## Make executable
sudo chmod +x /usr/local/bin/backup-postgres.sh

## Test
sudo /usr/local/bin/backup-postgres.sh

## Schedule with cron (daily at 2 AM)
sudo crontab -e

## Add:
0 2 * * * /usr/local/bin/backup-postgres.sh
```

---

#### 16.2 Restore from Backup

**Restore PostgreSQL**:

```bash
## Stop application
sudo systemctl stop idrm-backend

## Drop existing database
sudo -u postgres psql -c "DROP DATABASE idrm_production;"

## Recreate database
sudo -u postgres psql -c "CREATE DATABASE idrm_production;"

## Restore
pg_restore -U idrm_user -d idrm_production /var/backups/postgresql/idrm_20260516_020000.dump

## Restore globals
psql -U postgres -f /var/backups/postgresql/globals_20260516_020000.sql

## Restart application
sudo systemctl start idrm-backend
```

---

#### 16.3 Disaster Recovery Plan

**Complete DR Procedure**:

```
1. IDENTIFY THE PROBLEM
   ├─ Check monitoring alerts
   ├─ Check error logs
   ├─ Identify affected services
   └─ Estimate impact

2. ASSESS SEVERITY
   ├─ Critical: All users affected
   ├─ High: Major feature broken
   ├─ Medium: Minor feature broken
   └─ Low: Cosmetic issue

3. IMMEDIATE ACTIONS (Critical)
   ├─ Alert team
   ├─ Enable maintenance mode
   ├─ Take server snapshot
   └─ Document timeline

4. RESTORE OPTIONS
   ├─ Option A: Rollback to previous version
   ├─ Option B: Restore from backup
   ├─ Option C: Hotfix
   └─ Option D: Failover to backup server

5. ROLLBACK PROCEDURE
   ├─ Stop current version
   ├─ Deploy previous version
   ├─ Restore database (if needed)
   ├─ Clear cache
   └─ Test functionality

6. POST-INCIDENT
   ├─ Root cause analysis
   ├─ Update runbook
   ├─ Implement preventive measures
   └─ Team retrospective
```

---

## **PART 5: CI/CD Pipelines**

### 17. **What Is CI/CD?**

#### 17.1 CI/CD Explained Simply

**CI/CD** = Continuous Integration / Continuous Deployment

**Without CI/CD** (Manual):
```
Developer writes code
↓ (manual)
Run tests locally
↓ (manual)
Push to GitHub
↓ (manual)
SSH to server
↓ (manual)
Pull code
↓ (manual)
Restart services
↓ (manual)
Test in production

Time: 30-60 minutes
Errors: Many!
```

**With CI/CD** (Automated):
```
Developer writes code
↓ (manual)
Push to GitHub
↓ (AUTOMATIC)
Run tests ✅
Build Docker image ✅
Deploy to staging ✅
Run integration tests ✅
Deploy to production ✅
Send notification ✅

Time: 5-10 minutes
Errors: Caught automatically!
```

---

#### 17.2 Benefits of CI/CD

```
Speed:
- Deploy 10x faster
- Minutes instead of hours
- Multiple deploys per day

Quality:
- Automatic testing
- Catch bugs before production
- Consistent builds

Confidence:
- Rollback easily
- Test every change
- Less manual errors

Visibility:
- See build status
- Track deployments
- Monitor metrics
```

---

### 18. **GitHub Actions Setup**

#### 18.1 GitHub Actions Workflow

**Create `.github/workflows/deploy.yml`**:

```yaml
name: IDRM CI/CD Pipeline

on:
  push:
    branches:
      - main
      - staging
  pull_request:
    branches:
      - main

env:
  PYTHON_VERSION: '3.11'
  NODE_VERSION: '18'

jobs:
  # Job 1: Run Tests
  test:
    name: Run Tests
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgis/postgis:15-3.3
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_pass
          POSTGRES_DB: test_db
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7-alpine
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run linter
        run: |
          cd backend
          pip install flake8
          flake8 app/ --max-line-length=120

      - name: Run tests
        env:
          DATABASE_URL: postgresql://test_user:test_pass@localhost:5432/test_db
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml

  # Job 2: Build Docker Image
  build:
    name: Build Docker Image
    runs-on: ubuntu-latest
    needs: test
    if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/staging'

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Login to Docker Hub
        uses: docker/login-action@v2
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: idrm/backend
          tags: |
            type=ref,event=branch
            type=sha

      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./backend
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  # Job 3: Deploy to Staging
  deploy-staging:
    name: Deploy to Staging
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/staging'
    environment: staging

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to staging server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.STAGING_HOST }}
          username: ${{ secrets.STAGING_USER }}
          key: ${{ secrets.STAGING_SSH_KEY }}
          script: |
            cd /home/deploy/idrm
            git pull origin staging
            docker compose pull
            docker compose up -d --force-recreate
            docker compose exec -T backend alembic upgrade head

      - name: Health check
        run: |
          sleep 10
          curl -f https://staging.idrm.gov.in/api/v1/health || exit 1

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Staging deployment completed'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}

  # Job 4: Deploy to Production
  deploy-production:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    environment: production

    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Deploy to production server 1
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST_1 }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /home/deploy/idrm
            git pull origin main
            docker compose pull
            docker compose up -d --force-recreate
            docker compose exec -T backend alembic upgrade head

      - name: Deploy to production server 2
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.PROD_HOST_2 }}
          username: ${{ secrets.PROD_USER }}
          key: ${{ secrets.PROD_SSH_KEY }}
          script: |
            cd /home/deploy/idrm
            git pull origin main
            docker compose pull
            docker compose up -d --force-recreate
            docker compose exec -T backend alembic upgrade head

      - name: Health check
        run: |
          sleep 10
          curl -f https://idrm.gov.in/api/v1/health || exit 1

      - name: Notify team
        uses: 8398a7/action-slack@v3
        with:
          status: ${{ job.status }}
          text: 'Production deployment completed! :rocket:'
          webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

#### 18.2 GitHub Secrets Configuration

**Add secrets in GitHub repository**:

```
Settings → Secrets and variables → Actions → New repository secret

Required secrets:
- DOCKER_USERNAME: Your Docker Hub username
- DOCKER_PASSWORD: Your Docker Hub password
- STAGING_HOST: staging.idrm.gov.in
- STAGING_USER: deploy
- STAGING_SSH_KEY: Private SSH key
- PROD_HOST_1: 203.0.113.10
- PROD_HOST_2: 203.0.113.11
- PROD_USER: deploy
- PROD_SSH_KEY: Private SSH key
- SLACK_WEBHOOK: https://hooks.slack.com/services/xxx
```

---

### 19. **Automated Testing**

#### 19.1 Unit Tests

**Backend unit tests** (`backend/tests/test_services.py`):

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_service_request():
    """Test creating a service request"""
    # Login first
    login_response = client.post("/api/v1/auth/login", json={
        "email": "citizen@example.com",
        "password": "Citizen@123"
    })
    token = login_response.json()["data"]["access_token"]
    
    # Create service request
    response = client.post(
        "/api/v1/services",
        json={
            "service_type": "MEDICAL",
            "priority": "CRITICAL",
            "location": {
                "type": "Point",
                "coordinates": [78.4867, 17.3850]
            },
            "address": "Charminar, Hyderabad",
            "description": "Test service request",
            "privacy_level": "PROTECTED"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["status"] == "success"
    assert "service_id" in response.json()["data"]

def test_unauthorized_access():
    """Test unauthorized access to protected endpoint"""
    response = client.get("/api/v1/services")
    assert response.status_code == 401
```

---

#### 19.2 Integration Tests

**Integration tests** (`backend/tests/test_integration.py`):

```python
import pytest
from fastapi.testclient import TestClient

def test_complete_service_workflow(client, test_user, test_provider):
    """Test complete service request workflow"""
    
    # 1. Citizen creates service request
    token = test_user.login()
    create_response = client.post(
        "/api/v1/services",
        json={...},
        headers={"Authorization": f"Bearer {token}"}
    )
    service_id = create_response.json()["data"]["service_id"]
    
    # 2. Provider accepts service
    provider_token = test_provider.login()
    accept_response = client.post(
        f"/api/v1/services/{service_id}/accept",
        json={"estimated_arrival": "2026-05-16T10:30:00Z"},
        headers={"Authorization": f"Bearer {provider_token}"}
    )
    assert accept_response.status_code == 200
    
    # 3. Provider completes service
    complete_response = client.post(
        f"/api/v1/services/{service_id}/complete",
        json={"completion_notes": "Done"},
        headers={"Authorization": f"Bearer {provider_token}"}
    )
    assert complete_response.status_code == 200
    
    # 4. Citizen verifies
    verify_response = client.post(
        f"/api/v1/services/{service_id}/verify",
        json={"verified": True, "rating": 5},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert verify_response.status_code == 200
    
    # 5. Check final status
    status_response = client.get(
        f"/api/v1/services/{service_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert status_response.json()["data"]["status"] == "VERIFIED"
```

---

### 20. **Automated Deployment**

#### 20.1 Deployment Script

**Create `/home/deploy/idrm/deploy.sh`**:

```bash
#!/bin/bash
## IDRM Deployment Script

set -e  # Exit on error

## Configuration
ENVIRONMENT=${1:-production}
BACKUP_DIR="/var/backups/idrm"
LOG_FILE="/var/log/idrm/deploy.log"

## Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'  # No Color

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1" | tee -a $LOG_FILE
    exit 1
}

## 1. Pre-deployment checks
log "Starting deployment to $ENVIRONMENT..."

## Check if running as deploy user
if [ "$(whoami)" != "deploy" ]; then
    error "Must run as deploy user"
fi

## Check disk space
FREE_SPACE=$(df -h / | awk 'NR==2 {print $4}' | sed 's/G//')
if (( $(echo "$FREE_SPACE < 10" | bc -l) )); then
    error "Less than 10GB free disk space"
fi

## 2. Backup database
log "Creating database backup..."
sudo -u postgres pg_dump -d idrm_production -F c -f "$BACKUP_DIR/pre-deploy-$(date +%Y%m%d_%H%M%S).dump" || error "Database backup failed"

## 3. Pull latest code
log "Pulling latest code..."
git fetch origin
git reset --hard origin/main || error "Git pull failed"

## 4. Build new Docker images
log "Building Docker images..."
docker compose build --no-cache || error "Docker build failed"

## 5. Run database migrations
log "Running database migrations..."
docker compose run --rm backend alembic upgrade head || error "Migration failed"

## 6. Deploy with zero downtime
log "Deploying new version..."

## Start new containers
docker compose up -d --no-deps --build backend || error "Deployment failed"

## Wait for health check
log "Waiting for service to be healthy..."
RETRY=0
MAX_RETRY=30
until curl -f http://localhost:8000/api/v1/health > /dev/null 2>&1; do
    RETRY=$((RETRY+1))
    if [ $RETRY -eq $MAX_RETRY ]; then
        error "Health check failed"
    fi
    sleep 2
done

## 7. Remove old containers
docker compose up -d --remove-orphans

## 8. Clean up
log "Cleaning up old images..."
docker image prune -f

## 9. Post-deployment checks
log "Running post-deployment checks..."

## Check API health
curl -f https://idrm.gov.in/api/v1/health || error "API health check failed"

## Check frontend
curl -f https://idrm.gov.in/ || error "Frontend check failed"

## 10. Success
log "Deployment completed successfully!"

## Send notification
curl -X POST $SLACK_WEBHOOK -H 'Content-Type: application/json' -d "{
    \"text\": \"Deployment to $ENVIRONMENT completed successfully!\"
}"
```

```bash
## Make executable
chmod +x /home/deploy/idrm/deploy.sh

## Run deployment
./deploy.sh production
```

---

#### 20.2 Rollback Script

**Create `/home/deploy/idrm/rollback.sh`**:

```bash
#!/bin/bash
## IDRM Rollback Script

set -e

log() {
    echo -e "\033[0;32m[$(date '+%Y-%m-%d %H:%M:%S')]\033[0m $1"
}

error() {
    echo -e "\033[0;31m[$(date '+%Y-%m-%d %H:%M:%S')] ERROR:\033[0m $1"
    exit 1
}

## Get previous version
CURRENT_COMMIT=$(git rev-parse HEAD)
log "Current commit: $CURRENT_COMMIT"

## Ask for confirmation
read -p "Rollback to previous commit? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    log "Rollback cancelled"
    exit 0
fi

## Rollback
log "Rolling back..."

## Revert to previous commit
git reset --hard HEAD~1 || error "Git rollback failed"

## Rebuild and deploy
docker compose down
docker compose up -d --build || error "Rollback deployment failed"

## Health check
sleep 10
curl -f http://localhost:8000/api/v1/health || error "Health check failed after rollback"

log "Rollback completed successfully!"
```

---

## **PART 6: Maintenance & Operations**

### 21. **Daily Operations**

#### 21.1 Daily Checklist

```
MORNING CHECKS (9:00 AM):
- [ ] Check monitoring dashboards (Grafana)
- [ ] Review error logs (last 24 hours)
- [ ] Check disk space (should be > 20%)
- [ ] Check backup status (last backup successful?)
- [ ] Review user signups (any suspicious patterns?)
- [ ] Check API response times (< 500ms average?)
- [ ] Verify SSL certificates (expiry > 30 days?)

AFTERNOON CHECKS (2:00 PM):
- [ ] Review service requests (any stuck in queue?)
- [ ] Check Redis cache hit ratio (> 80%?)
- [ ] Monitor database connections (< 150 active?)
- [ ] Review failed jobs/tasks
- [ ] Check email delivery (emails going out?)

END OF DAY (6:00 PM):
- [ ] Review daily metrics
- [ ] Update incident log (if any)
- [ ] Plan tomorrow's maintenance
- [ ] Check on-call schedule
```

---

#### 21.2 Weekly Maintenance

```
EVERY MONDAY:
- [ ] Review last week's metrics
- [ ] Update dependencies (if needed)
- [ ] Database optimization (VACUUM, ANALYZE)
- [ ] Check backup restoration (test restore)
- [ ] Security updates (apt update && apt upgrade)

EVERY FRIDAY:
- [ ] Deploy staging changes to production
- [ ] Clean up old logs (> 30 days)
- [ ] Review error trends
- [ ] Team sync meeting
```

---

#### 21.3 Monthly Tasks

```
FIRST OF MONTH:
- [ ] Rotate database backups to cold storage
- [ ] Review and renew SSL certificates (if needed)
- [ ] Security audit
- [ ] Performance report
- [ ] Cost analysis
- [ ] User feedback review

MID-MONTH:
- [ ] Disaster recovery drill
- [ ] Load testing
- [ ] Dependency updates
- [ ] Documentation updates
```

---

### 22. **Incident Response**

#### 22.1 Incident Response Plan

**Severity Levels**:

```
CRITICAL (P1):
- All users affected
- Complete service outage
- Data loss
Response: Immediate (< 15 min)
Example: Database down, website unreachable

HIGH (P2):
- Major feature broken
- Significant user impact
- Data corruption risk
Response: 1 hour
Example: Map not loading, API errors

MEDIUM (P3):
- Minor feature broken
- Some users affected
- Workaround available
Response: 4 hours
Example: Email notifications delayed

LOW (P4):
- Cosmetic issue
- Minimal impact
- Can be scheduled
Response: Next business day
Example: Typo in UI, minor styling issue
```

---

#### 22.2 Incident Response Workflow

```
1. DETECTION (0-5 min)
   ├─ Alert received (monitoring/user report)
   ├─ Acknowledge alert
   ├─ Assess severity
   └─ Create incident ticket

2. TRIAGE (5-15 min)
   ├─ Gather information
   ├─ Check recent changes
   ├─ Review logs/metrics
   └─ Identify affected systems

3. RESPONSE (15-30 min)
   ├─ Alert team if P1/P2
   ├─ Start incident bridge call
   ├─ Assign incident commander
   └─ Begin mitigation

4. MITIGATION (30-60 min)
   ├─ Implement fix or rollback
   ├─ Monitor impact
   ├─ Verify resolution
   └─ Communicate status

5. RECOVERY (1-2 hours)
   ├─ Full system check
   ├─ Data integrity verification
   ├─ Performance monitoring
   └─ User communication

6. POST-MORTEM (1-2 days)
   ├─ Timeline documentation
   ├─ Root cause analysis
   ├─ Action items
   └─ Team retrospective
```

---

#### 22.3 Common Incidents & Solutions

**Incident: Website Down**

```
Symptoms:
- Users can't access website
- "Connection timeout" error
- Monitoring alert: Service Down

Diagnosis:
1. Check NGINX: sudo systemctl status nginx
2. Check backend: docker ps
3. Check network: ping server-ip
4. Check DNS: dig idrm.gov.in

Solutions:
- NGINX down → sudo systemctl start nginx
- Backend down → docker compose up -d
- Server down → Contact hosting provider
- DNS issue → Check DNS records

Recovery Time: 5-15 minutes
```

---

**Incident: Slow Response Times**

```
Symptoms:
- Pages loading slowly (> 3s)
- API timeouts
- User complaints

Diagnosis:
1. Check CPU: top
2. Check memory: free -h
3. Check database: SELECT count(*) FROM pg_stat_activity;
4. Check Redis: redis-cli INFO stats
5. Check logs: tail -f /var/log/nginx/error.log

Solutions:
- High CPU → Restart services, scale up
- High memory → Restart services, investigate memory leak
- High DB connections → Restart backend, check connection pool
- Redis full → redis-cli FLUSHDB (if safe)
- NGINX errors → Check rate limiting, restart

Recovery Time: 15-30 minutes
```

---

**Incident: Database Connection Errors**

```
Symptoms:
- "psycopg.OperationalError"
- Backend can't connect to database
- No new data being saved

Diagnosis:
1. Check PostgreSQL: sudo systemctl status postgresql
2. Check connections: SELECT count(*) FROM pg_stat_activity;
3. Check pg_hba.conf: sudo nano /etc/postgresql/15/main/pg_hba.conf
4. Check network: telnet db-server 5432

Solutions:
- PostgreSQL down → sudo systemctl start postgresql
- Too many connections → Restart backend, increase max_connections
- Auth failure → Check credentials, update pg_hba.conf
- Network issue → Check firewall, check routes

Recovery Time: 10-20 minutes
```

---

### 23. **Performance Optimization**

#### 23.1 Database Optimization

**Regular Maintenance**:

```sql
-- Run weekly
VACUUM ANALYZE;

-- Check table bloat
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Reindex if needed
REINDEX DATABASE idrm_production;
```

**Query Optimization**:

```sql
-- Find slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    max_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_services_created_at 
ON service_requests(created_at DESC);

CREATE INDEX CONCURRENTLY idx_services_location 
ON service_requests USING GIST(location);
```

---

#### 23.2 Application Optimization

**Backend Optimization**:

```python
## Use connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True
)

## Cache expensive queries
from functools import lru_cache

@lru_cache(maxsize=128)
def get_service_types():
    return db.query(ServiceType).all()

## Use pagination
@router.get("/services")
def list_services(skip: int = 0, limit: int = 20):
    return db.query(Service).offset(skip).limit(limit).all()
```

---

#### 23.3 Frontend Optimization

```
Performance Targets:
- First Contentful Paint: < 1.5s
- Time to Interactive: < 3.5s
- Largest Contentful Paint: < 2.5s

Optimizations:
✅ Minify CSS/JS
✅ Compress images (WebP format)
✅ Use CDN for static assets
✅ Enable browser caching
✅ Lazy load images
✅ Code splitting
✅ Reduce bundle size
```

---

### 🎉 **CONGRATULATIONS!**

You've completed the **COMPLETE DEPLOYMENT GUIDE**!

---

### 📊 **What You've Learned**

```
✅ Part 1: Understanding deployments
✅ Part 2: Development environment setup
✅ Part 3: Staging environment with Docker
✅ Part 4: Production deployment & security
✅ Part 5: CI/CD with GitHub Actions
✅ Part 6: Maintenance & operations

Total: 6 comprehensive parts
Pages: ~100+ pages of content
Time to read: 4-6 hours
Time to implement: 2-4 weeks
```

---

### 🚀 **Your Journey**

```
Week 1-2: Development Setup
├─ Install all tools
├─ Clone repository
├─ Setup database
└─ Run locally

Week 3-4: Staging Deployment
├─ Setup staging server
├─ Configure Docker
├─ Deploy to staging
└─ Test thoroughly

Week 5-6: Production Deployment
├─ Setup production servers
├─ Configure load balancer
├─ Deploy to production
└─ Monitor closely

Week 7-8: Automation
├─ Setup CI/CD
├─ Configure monitoring
├─ Document processes
└─ Train team

Week 9+: Maintenance
├─ Daily operations
├─ Performance tuning
├─ Security updates
└─ Feature deployments
```

---

### 📋 **Quick Reference**

**Emergency Contacts**:
```
Team Lead: +91-XXXX-XXXX
DevOps: +91-XXXX-XXXX
Database Admin: +91-XXXX-XXXX
On-call: Check schedule
```

**Important URLs**:
```
Production: https://idrm.gov.in
Staging: https://staging.idrm.gov.in
Monitoring: https://grafana.idrm.gov.in
Alerts: #idrm-alerts (Slack)
Documentation: https://docs.idrm.gov.in
```

**Important Commands**:
```bash
## Check status
docker compose ps
systemctl status postgresql
systemctl status redis

## View logs
docker compose logs -f
tail -f /var/log/nginx/error.log

## Deploy
./deploy.sh production

## Rollback
./rollback.sh

## Backup
/usr/local/bin/backup-postgres.sh

## Health check
curl https://idrm.gov.in/api/v1/health
```

---

**Document Complete!**  
**Status**: ✅ Production-Ready  
**Version**: 3.0 Unified Complete  
**Last Updated**: May 16, 2026

**You're now ready to deploy IDRM from development to production!** 🎊
