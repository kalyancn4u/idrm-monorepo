> *Type: Guide (novice / how-to) · Audience: DevOps, admins · Status: Archived — v1 historical generation*

# IDRM Platform Setup - Production Environment

<!-- IDRM-CLEANUP doc=v1-g13-prod status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — production deploy
> MVP production = **native systemd on a single Ubuntu server** → [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md)
> (+ [`backup-restore-101`](../../../../guides/mvp/learn/backup-restore-101.md)). Container/K8s/multi-node production → **FFP**
> [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.

> Production-grade deployment with security hardening, SSL, automated backups, and monitoring

## 🎯 Goal

Deploy a production-ready IDRM platform with:
- Maximum security and performance
- SSL/TLS encryption (Let's Encrypt)
- Automated backups
- Zero-downtime deployment capability
- Comprehensive monitoring
- Disaster recovery procedures

## ⚠️ Critical Production Requirements

- **NEVER expose database ports publicly**
- **ALWAYS use HTTPS** (no HTTP in production)
- **ALWAYS use strong passwords** (32+ characters)
- **ALWAYS enable firewall** (UFW)
- **ALWAYS enable fail2ban**
- **ALWAYS implement backups**
- **ALWAYS use environment variables** (never hardcode secrets)

## 📋 Prerequisites

- ✅ Completed `setup-prerequisites.md`
- ✅ Docker and Docker Compose installed
- ✅ Domain name configured (DNS propagated)
- ✅ Production server (8+ CPU, 32+ GB RAM, 200+ GB SSD)
- ✅ SSL certificate strategy planned (Let's Encrypt)
- ✅ Backup storage configured

---

## Table of Contents

1. [Server Hardening](#server-hardening)
2. [Security Configuration](#security-configuration)
3. [SSL Certificate Setup](#ssl-certificate-setup)
4. [Production Docker Compose](#production-docker-compose)
5. [Environment Configuration](#environment-configuration)
6. [Deploy Application](#deploy-application)
7. [Backup Strategy](#backup-strategy)
8. [Monitoring Setup](#monitoring-setup)
9. [Zero-Downtime Deployment](#zero-downtime-deployment)
10. [Disaster Recovery](#disaster-recovery)

---

## Server Hardening

### 1. System Updates and Security

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install security tools
sudo apt install -y \
  ufw \
  fail2ban \
  unattended-upgrades \
  logwatch \
  rkhunter \
  aide

# Enable automatic security updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

### 2. Create Deployment User (Non-root)

```bash
# Create deployment user
sudo useradd -m -s /bin/bash idrm-prod
sudo usermod -aG docker idrm-prod

# Set strong password
sudo passwd idrm-prod

# Configure sudo with password
echo "idrm-prod ALL=(ALL) ALL" | sudo tee /etc/sudoers.d/idrm-prod
```

### 3. SSH Hardening

```bash
# Backup SSH config
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.backup

# Edit SSH config
sudo nano /etc/ssh/sshd_config
```

**Update these settings**:
```bash
# Disable root login
PermitRootLogin no

# Disable password authentication (use SSH keys only)
PasswordAuthentication no
PubkeyAuthentication yes

# Use SSH protocol 2 only
Protocol 2

# Change default port (optional but recommended)
Port 2222

# Disable empty passwords
PermitEmptyPasswords no

# Max authentication attempts
MaxAuthTries 3

# Login grace time
LoginGraceTime 30
```

```bash
# Restart SSH
sudo systemctl restart sshd

# TEST NEW SSH CONNECTION BEFORE CLOSING CURRENT SESSION!
# In a new terminal:
ssh -p 2222 idrm-prod@your-server-ip
```

### 4. Firewall Configuration (UFW)

```bash
# Reset UFW
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH on custom port
sudo ufw allow 2222/tcp comment 'SSH'

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Enable UFW
sudo ufw --force enable

# Verify
sudo ufw status verbose
```

### 5. Fail2Ban Configuration

```bash
# Create jail for SSH
sudo nano /etc/fail2ban/jail.local
```

**Add**:
```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3
destemail = admin@yourdomain.com
sendername = Fail2Ban
action = %(action_mwl)s

[sshd]
enabled = true
port = 2222
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
port = http,https
logpath = /var/log/nginx/error.log

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
```

```bash
# Restart Fail2Ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Check status
sudo fail2ban-client status
```

---

## Security Configuration

### 1. Secure Shared Memory

```bash
# Edit fstab
sudo nano /etc/fstab
```

**Add at the end**:
```bash
tmpfs /run/shm tmpfs defaults,noexec,nosuid 0 0
```

```bash
# Apply
sudo mount -a
```

### 2. Kernel Hardening

```bash
# Edit sysctl
sudo nano /etc/sysctl.conf
```

**Add**:
```bash
# IP Forwarding (disable if not needed)
net.ipv4.ip_forward = 0

# SYN flood protection
net.ipv4.tcp_syncookies = 1

# Ignore ICMP redirects
net.ipv4.conf.all.accept_redirects = 0
net.ipv6.conf.all.accept_redirects = 0

# Ignore send redirects
net.ipv4.conf.all.send_redirects = 0

# Disable source packet routing
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# Log Martians
net.ipv4.conf.all.log_martians = 1
```

```bash
# Apply
sudo sysctl -p
```

### 3. Docker Security

```bash
# Create Docker daemon config
sudo nano /etc/docker/daemon.json
```

**Add**:
```json
{
  "icc": false,
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "userland-proxy": false,
  "no-new-privileges": true
}
```

```bash
# Restart Docker
sudo systemctl restart docker
```

---

## SSL Certificate Setup

### 1. Install Certbot

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
```

### 2. Obtain SSL Certificate

```bash
# Stop NGINX if running
docker compose down nginx 2>/dev/null || true

# Obtain certificate for your domain
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d www.yourdomain.com \
  -d api.yourdomain.com \
  --email admin@yourdomain.com \
  --agree-tos \
  --non-interactive \
  --staple-ocsp

# Verify certificates
sudo ls -la /etc/letsencrypt/live/yourdomain.com/
```

### 3. Setup Auto-Renewal

```bash
# Test renewal
sudo certbot renew --dry-run

# Create renewal script
sudo nano /etc/cron.d/certbot-renewal
```

**Add**:
```bash
0 0,12 * * * root certbot renew --quiet --deploy-hook "docker exec idrm-nginx nginx -s reload"
```

### 4. Copy Certificates for Docker

```bash
# Create SSL directory
sudo mkdir -p /home/idrm-prod/idrm-production/ssl

# Copy certificates
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem \
  /home/idrm-prod/idrm-production/ssl/

sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem \
  /home/idrm-prod/idrm-production/ssl/

# Set permissions
sudo chown -R idrm-prod:idrm-prod /home/idrm-prod/idrm-production/ssl
sudo chmod 600 /home/idrm-prod/idrm-production/ssl/*.pem
```

---

## Production Docker Compose

### 1. Create Production Structure

```bash
# Switch to deployment user
sudo su - idrm-prod

# Create project directory
mkdir -p /home/idrm-prod/idrm-production
cd /home/idrm-prod/idrm-production

# Create structure
mkdir -p {docker,infrastructure/{nginx/conf.d,postgres/init},data/{postgres,redis,geoserver},logs,ssl,backups}
```

### 2. Production docker-compose.yml

```bash
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    container_name: idrm-postgres
    restart: always
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "-E UTF8"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
      - ./infrastructure/postgres/init:/docker-entrypoint-initdb.d
      - ./backups/postgres:/backups
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5
    # NEVER expose in production!
    # ports are only accessible via internal network

  redis:
    image: redis:7.2-alpine
    container_name: idrm-redis
    restart: always
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 2gb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - ./data/redis:/data
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  geoserver:
    image: kartoza/geoserver:2.24.0
    container_name: idrm-geoserver
    restart: always
    environment:
      GEOSERVER_ADMIN_USER: ${GEOSERVER_ADMIN_USER}
      GEOSERVER_ADMIN_PASSWORD: ${GEOSERVER_ADMIN_PASSWORD}
      INITIAL_MEMORY: 4G
      MAXIMUM_MEMORY: 8G
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASS: ${DB_PASSWORD}
      POSTGRES_HOST: postgres
      POSTGRES_PORT: 5432
    volumes:
      - ./data/geoserver:/opt/geoserver/data_dir
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true
    depends_on:
      postgres:
        condition: service_healthy
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/geoserver/web/ || exit 1"]
      interval: 60s
      timeout: 30s
      retries: 3
      start_period: 120s

  api-gateway:
    build:
      context: ./backend/api-gateway
      dockerfile: Dockerfile
    container_name: idrm-api-gateway
    restart: always
    environment:
      NODE_ENV: production
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
    security_opt:
      - no-new-privileges:true
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

  service-management:
    build:
      context: ./backend/services/service-management
      dockerfile: Dockerfile
    container_name: idrm-service-mgmt
    restart: always
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
    volumes:
      - ./logs/services:/app/logs
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  geospatial-service:
    build:
      context: ./backend/services/geospatial
      dockerfile: Dockerfile
    container_name: idrm-geospatial
    restart: always
    environment:
      DATABASE_URL: postgresql://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      GEOSERVER_URL: http://geoserver:8080/geoserver
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true
    depends_on:
      postgres:
        condition: service_healthy
      geoserver:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
      args:
        - VITE_API_URL=${FRONTEND_API_URL}
        - VITE_WS_URL=${FRONTEND_WS_URL}
        - VITE_GEOSERVER_URL=${FRONTEND_GEOSERVER_URL}
    container_name: idrm-frontend
    restart: always
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true

  nginx:
    image: nginx:1.24-alpine
    container_name: idrm-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./infrastructure/nginx/conf.d:/etc/nginx/conf.d:ro
      - ./infrastructure/nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - ./logs/nginx:/var/log/nginx
    networks:
      - idrm-network
    security_opt:
      - no-new-privileges:true
    depends_on:
      - api-gateway
      - frontend
      - geoserver
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  idrm-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  geoserver_data:
    driver: local
EOF
```

---

## Environment Configuration

### 1. Production .env File

```bash
cat > .env << 'EOF'
# Environment
ENVIRONMENT=production

# Database (CHANGE ALL PASSWORDS!)
DB_NAME=idrm_production
DB_USER=idrm_user
DB_PASSWORD=GENERATE_SECURE_PASSWORD_32_CHARS

# Redis
REDIS_PASSWORD=GENERATE_SECURE_PASSWORD_32_CHARS

# JWT (CRITICAL - NEVER REUSE FROM STAGING!)
JWT_SECRET=GENERATE_SECURE_RANDOM_64_CHARS
JWT_EXPIRATION=3600

# GeoServer
GEOSERVER_ADMIN_USER=admin
GEOSERVER_ADMIN_PASSWORD=GENERATE_SECURE_PASSWORD_16_CHARS

# CORS (Your actual domain)
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Frontend URLs (Use your actual domain)
FRONTEND_API_URL=https://yourdomain.com/api/v1
FRONTEND_WS_URL=wss://yourdomain.com
FRONTEND_GEOSERVER_URL=https://yourdomain.com/geoserver

# Domain
DOMAIN=yourdomain.com
SSL_EMAIL=admin@yourdomain.com

# Backup
BACKUP_RETENTION_DAYS=30
BACKUP_S3_BUCKET=idrm-backups  # If using S3
EOF

# Generate production passwords
echo "=== PRODUCTION PASSWORDS ===" > .env.production-secrets
echo "SAVE THESE IN A PASSWORD MANAGER!" >> .env.production-secrets
echo "" >> .env.production-secrets
echo "DB_PASSWORD=$(openssl rand -base64 32)" >> .env.production-secrets
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env.production-secrets
echo "JWT_SECRET=$(openssl rand -hex 64)" >> .env.production-secrets
echo "GEOSERVER_ADMIN_PASSWORD=$(openssl rand -base64 16)" >> .env.production-secrets

# Secure files
chmod 600 .env
chmod 600 .env.production-secrets

echo "⚠️  CRITICAL: Copy passwords from .env.production-secrets to .env"
echo "⚠️  CRITICAL: Save .env.production-secrets in password manager"
echo "⚠️  CRITICAL: Delete .env.production-secrets after copying"
```

---

## Production NGINX Configuration

```bash
cat > infrastructure/nginx/conf.d/idrm-production.conf << 'EOF'
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=30r/s;

# Upstream definitions
upstream api_gateway {
    server api-gateway:3000;
    keepalive 32;
}

upstream geoserver {
    server geoserver:8080;
    keepalive 16;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Let's Encrypt challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
    
    # Redirect to HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS Server
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_stapling on;
    ssl_stapling_verify on;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval';" always;
    
    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    # Frontend (Static Files)
    location / {
        root /usr/share/nginx/html;
        try_files $uri $uri/ /index.html;
        
        # Caching
        expires 1h;
        add_header Cache-Control "public, immutable";
        
        # Rate limiting
        limit_req zone=general_limit burst=20 nodelay;
    }
    
    # API Gateway
    location /api {
        proxy_pass http://api_gateway;
        proxy_http_version 1.1;
        
        # Headers
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Rate limiting
        limit_req zone=api_limit burst=20 nodelay;
        
        # No caching
        proxy_cache_bypass $http_upgrade;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
    
    # WebSocket
    location /socket.io {
        proxy_pass http://api_gateway;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # WebSocket timeouts
        proxy_connect_timeout 7d;
        proxy_send_timeout 7d;
        proxy_read_timeout 7d;
    }
    
    # GeoServer
    location /geoserver {
        proxy_pass http://geoserver/geoserver;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Caching for tiles
        proxy_cache_valid 200 1h;
        expires 1h;
    }
    
    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
```

---

## Deploy Application

### 1. Build Images

```bash
cd /home/idrm-prod/idrm-production

# Build all images
docker compose build --no-cache

# Pull base images
docker compose pull
```

### 2. Start Services

```bash
# Start in detached mode
docker compose up -d

# Monitor startup
docker compose logs -f

# Wait for all services to be healthy
docker compose ps
```

### 3. Initialize Database

```bash
# Run migrations (if using Alembic)
docker compose exec service-management alembic upgrade head

# Verify database
docker compose exec postgres psql -U idrm_user -d idrm_production -c "\dt"
```

---

## Backup Strategy

### 1. Automated Database Backups

```bash
# Create backup script
cat > /home/idrm-prod/backup-database.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/idrm-prod/idrm-production/backups/postgres"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="idrm_production_${TIMESTAMP}.sql.gz"

# Create backup
docker compose -f /home/idrm-prod/idrm-production/docker-compose.yml \
  exec -T postgres pg_dump -U idrm_user idrm_production | gzip > "${BACKUP_DIR}/${BACKUP_FILE}"

# Delete backups older than 30 days
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_FILE}"
EOF

chmod +x /home/idrm-prod/backup-database.sh
```

### 2. Schedule Backups

```bash
# Add to crontab
crontab -e
```

**Add**:
```bash
# Database backup at 2 AM daily
0 2 * * * /home/idrm-prod/backup-database.sh >> /home/idrm-prod/backup.log 2>&1

# Volume backup weekly (Sunday 3 AM)
0 3 * * 0 /home/idrm-prod/backup-volumes.sh >> /home/idrm-prod/backup.log 2>&1
```

### 3. Volume Backup Script

```bash
cat > /home/idrm-prod/backup-volumes.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/home/idrm-prod/idrm-production/backups/volumes"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL data
docker run --rm \
  -v idrm-production_postgres_data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/postgres_${TIMESTAMP}.tar.gz /data

# Backup GeoServer data
docker run --rm \
  -v idrm-production_geoserver_data:/data \
  -v ${BACKUP_DIR}:/backup \
  alpine tar czf /backup/geoserver_${TIMESTAMP}.tar.gz /data

echo "Volume backups completed"
EOF

chmod +x /home/idrm-prod/backup-volumes.sh
```

---

## Monitoring Setup

### 1. Container Health Monitoring

```bash
# Create monitoring script
cat > /home/idrm-prod/monitor-health.sh << 'EOF'
#!/bin/bash

cd /home/idrm-prod/idrm-production

# Check all containers
UNHEALTHY=$(docker compose ps | grep -i "unhealthy" | wc -l)

if [ $UNHEALTHY -gt 0 ]; then
    echo "WARNING: ${UNHEALTHY} unhealthy containers detected!"
    docker compose ps
    # Send alert (integrate with your monitoring system)
fi
EOF

chmod +x /home/idrm-prod/monitor-health.sh

# Run every 5 minutes
crontab -e
```

**Add**:
```bash
*/5 * * * * /home/idrm-prod/monitor-health.sh >> /home/idrm-prod/health-monitor.log 2>&1
```

### 2. Log Rotation

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/idrm
```

**Add**:
```bash
/home/idrm-prod/idrm-production/logs/*/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 idrm-prod idrm-prod
    sharedscripts
}
```

---

## Zero-Downtime Deployment

### 1. Blue-Green Deployment Script

```bash
cat > /home/idrm-prod/deploy.sh << 'EOF'
#!/bin/bash

set -e

cd /home/idrm-prod/idrm-production

echo "Starting zero-downtime deployment..."

# Pull latest code
git pull origin main

# Build new images
docker compose build

# Start new containers (will run alongside old ones temporarily)
docker compose up -d --no-deps --build api-gateway service-management geospatial-service frontend

# Wait for health checks
sleep 30

# Reload NGINX (will pick up new containers)
docker compose exec nginx nginx -s reload

# Remove old images
docker image prune -f

echo "Deployment completed successfully!"
EOF

chmod +x /home/idrm-prod/deploy.sh
```

---

## Disaster Recovery

### 1. Full System Restore Procedure

```bash
cat > /home/idrm-prod/restore.sh << 'EOF'
#!/bin/bash

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup-file.sql.gz>"
    exit 1
fi

echo "WARNING: This will restore database from backup!"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    exit 1
fi

# Stop services
docker compose down

# Restore database
gunzip < $BACKUP_FILE | docker compose exec -T postgres psql -U idrm_user idrm_production

# Start services
docker compose up -d

echo "Restore completed!"
EOF

chmod +x /home/idrm-prod/restore.sh
```

---

## Final Verification

```bash
# Comprehensive production test
cat > /home/idrm-prod/verify-production.sh << 'EOF'
#!/bin/bash

echo "=== IDRM Production Verification ==="

# Check HTTPS
echo -n "Testing HTTPS... "
curl -sI https://yourdomain.com | grep -q "200 OK" && echo "✓" || echo "✗"

# Check API
echo -n "Testing API... "
curl -s https://yourdomain.com/api/health | grep -q "healthy" && echo "✓" || echo "✗"

# Check database
echo -n "Testing Database... "
docker compose exec -T postgres psql -U idrm_user -d idrm_production -c "SELECT 1" > /dev/null 2>&1 && echo "✓" || echo "✗"

# Check SSL certificate
echo -n "Testing SSL... "
echo | openssl s_client -connect yourdomain.com:443 2>/dev/null | grep -q "Verify return code: 0" && echo "✓" || echo "✗"

# Check firewall
echo -n "Testing Firewall... "
sudo ufw status | grep -q "Status: active" && echo "✓" || echo "✗"

# Check fail2ban
echo -n "Testing Fail2Ban... "
sudo fail2ban-client status | grep -q "Number of jail" && echo "✓" || echo "✗"

echo ""
echo "Production verification complete!"
EOF

chmod +x /home/idrm-prod/verify-production.sh
./verify-production.sh
```

---

## Post-Deployment Checklist

- ✅ All containers are healthy
- ✅ HTTPS working with valid SSL certificate
- ✅ HTTP redirects to HTTPS
- ✅ API endpoints responding correctly
- ✅ Database accessible internally (NOT externally)
- ✅ Firewall configured and active
- ✅ Fail2Ban running
- ✅ Backups scheduled
- ✅ Log rotation configured
- ✅ Monitoring in place
- ✅ Emergency contacts documented
- ✅ Disaster recovery tested

---

**🎉 Production environment is live! Monitor closely for the first 48 hours! 🚀**
