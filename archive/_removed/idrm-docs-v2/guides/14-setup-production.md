> *Type: Guide (novice / how-to) · Audience: DevOps, admins · Status: Archived — v2 historical generation*

# IDRM Production Environment Setup v2.0

<!-- IDRM-CLEANUP doc=v2-g14-prod status=ANNOTATED-VARIANT pass=2026-08-16 -->
> ## 🗺️ VARIANT NOTE — production
> MVP production = native systemd on one Ubuntu server → [`../../../../docs/mvp/80-ops-deployment-and-operations.md`](../../../../docs/mvp/80-ops-deployment-and-operations.md);
> container/K8s/multi-node → **FFP** [`../../../../docs/ffp/80-ops-platform-and-deployment.md`](../../../../docs/ffp/80-ops-platform-and-deployment.md). *Program:* `../../_CLEANUP-LEDGER.md`, `../../../instructions.txt` §12.
## Secure Docker Deployment with SSL, Firewall, and Monitoring

**Version**: 2.0  
**Last Updated**: May 10, 2026  
**Environment**: Production  
**Stack**: Python Geospatial + Bun + Docker + SSL + Security

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Security Hardening](#security-hardening)
4. [SSL/TLS Setup](#ssltls-setup)
5. [Production Deployment](#production-deployment)
6. [Monitoring](#monitoring)
7. [Backups](#backups)
8. [Maintenance](#maintenance)

---

## 🎯 Overview

### Production Requirements

Production environment requires:
- ✅ SSL/TLS encryption (HTTPS only)
- ✅ Firewall configured (UFW)
- ✅ Fail2Ban for brute-force protection
- ✅ Automated backups
- ✅ Monitoring and alerting
- ✅ Zero-downtime deployments
- ✅ 99.9% uptime SLA

### Time Estimate

- **Fresh Production Setup**: 3-4 hours
- **Staging → Production Migration**: 1-2 hours

---

## ✅ Prerequisites

### Hardware Requirements

```
CPU:    16+ cores (recommended)
RAM:    32-64 GB (recommended)
Storage: 500 GB NVMe SSD
Backup:  500 GB separate storage
Network: 1 Gbps minimum
```

### Software Requirements

- [ ] Ubuntu 22.04 LTS (Server)
- [ ] Docker 24.0+
- [ ] Docker Compose 2.20+
- [ ] Domain name registered and DNS configured
- [ ] Email address for SSL certificates
- [ ] SSH key-based authentication configured

### DNS Configuration

**Required DNS Records**:

```
Type    Name              Value              TTL
A       @                 YOUR_SERVER_IP     3600
A       www               YOUR_SERVER_IP     3600
A       api               YOUR_SERVER_IP     3600
```

**Verify DNS**:
```bash
dig yourdomain.com +short
# Should return: YOUR_SERVER_IP

dig api.yourdomain.com +short
# Should return: YOUR_SERVER_IP
```

---

## 🔒 Security Hardening

### Step 1: System Updates

```bash
# Update all packages
sudo apt update && sudo apt full-upgrade -y

# Install security updates automatically
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

### Step 2: SSH Hardening

**Edit SSH Configuration**:

```bash
sudo nano /etc/ssh/sshd_config
```

**Recommended Settings**:

```bash
# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no

# Enable key-based authentication only
PubkeyAuthentication yes

# Disable empty passwords
PermitEmptyPasswords no

# Disable X11 forwarding (if not needed)
X11Forwarding no

# Set login grace time
LoginGraceTime 60

# Maximum authentication attempts
MaxAuthTries 3

# Allowed users (replace with your username)
AllowUsers your_username

# Use only strong ciphers
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com
```

**Restart SSH**:
```bash
sudo systemctl restart sshd
```

---

### Step 3: Firewall (UFW)

```bash
# Reset firewall rules
sudo ufw --force reset

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH from specific IP (recommended)
# Replace YOUR_IP with your actual IP address
sudo ufw allow from YOUR_IP to any port 22 proto tcp comment 'SSH from trusted IP'

# Or allow SSH from anywhere (less secure)
# sudo ufw allow 22/tcp comment 'SSH'

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp comment 'HTTP'
sudo ufw allow 443/tcp comment 'HTTPS'

# Enable firewall
sudo ufw --force enable

# Verify status
sudo ufw status numbered

# Example output:
#      To                         Action      From
#      --                         ------      ----
# [1]  22/tcp                     ALLOW IN    YOUR_IP
# [2]  80/tcp                     ALLOW IN    Anywhere
# [3]  443/tcp                    ALLOW IN    Anywhere
```

**CRITICAL**: Test SSH connection from another terminal BEFORE closing current session!

---

### Step 4: Fail2Ban

```bash
# Install Fail2Ban
sudo apt install -y fail2ban

# Create local configuration
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# Configure for NGINX and SSH
sudo tee /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = admin@yourdomain.com
sendername = Fail2Ban

[sshd]
enabled = true
port = 22
logpath = /var/log/auth.log

[nginx-http-auth]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log

[nginx-limit-req]
enabled = true
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 10

[nginx-botsearch]
enabled = true
port = http,https
logpath = /var/log/nginx/access.log
maxretry = 2
EOF

# Start and enable Fail2Ban
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# Check status
sudo fail2ban-client status

# Check bans
sudo fail2ban-client status sshd
```

---

### Step 5: System Limits

```bash
# Increase file descriptors
sudo tee -a /etc/security/limits.conf << 'EOF'
* soft nofile 65536
* hard nofile 65536
root soft nofile 65536
root hard nofile 65536
EOF

# Kernel parameters for production
sudo tee -a /etc/sysctl.conf << 'EOF'
# Network performance
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535

# Security
net.ipv4.conf.all.rp_filter = 1
net.ipv4.conf.default.rp_filter = 1
net.ipv4.icmp_echo_ignore_broadcasts = 1
net.ipv4.conf.all.accept_source_route = 0
net.ipv6.conf.all.accept_source_route = 0

# File system
fs.file-max = 2097152
EOF

# Apply
sudo sysctl -p
```

---

## 🔐 SSL/TLS Setup

### Step 6: Install Certbot

```bash
# Install Certbot for NGINX
sudo apt install -y certbot python3-certbot-nginx

# Verify installation
certbot --version
```

---

### Step 7: Obtain SSL Certificate

**Option A: Automated (Recommended)**:

```bash
# Obtain and configure SSL automatically
sudo certbot --nginx \
    -d yourdomain.com \
    -d www.yourdomain.com \
    -d api.yourdomain.com \
    --email admin@yourdomain.com \
    --agree-tos \
    --no-eff-email \
    --redirect

# Expected output:
# Successfully received certificate.
# Certificate is saved at: /etc/letsencrypt/live/yourdomain.com/fullchain.pem
# Key is saved at:         /etc/letsencrypt/live/yourdomain.com/privkey.pem
```

**Option B: Manual (for advanced configurations)**:

```bash
# Obtain certificate only (manual NGINX config)
sudo certbot certonly --nginx \
    -d yourdomain.com \
    -d www.yourdomain.com \
    -d api.yourdomain.com \
    --email admin@yourdomain.com
```

---

### Step 8: Test Auto-Renewal

```bash
# Test renewal process (dry run)
sudo certbot renew --dry-run

# Expected output:
# Congratulations, all simulated renewals succeeded

# Check renewal timer
sudo systemctl status certbot.timer

# Certificates auto-renew twice daily via systemd timer
```

---

### Step 9: SSL Configuration

**nginx/production.conf** (SSL portion):

```nginx
# SSL Configuration
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

# SSL protocols and ciphers
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
ssl_prefer_server_ciphers on;

# SSL session cache
ssl_session_cache shared:SSL:50m;
ssl_session_timeout 1d;
ssl_session_tickets off;

# OCSP stapling
ssl_stapling on;
ssl_stapling_verify on;
ssl_trusted_certificate /etc/letsencrypt/live/yourdomain.com/chain.pem;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;

# Security headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

---

## 🚀 Production Deployment

### Step 10: Environment Configuration

**.env.production**:

```bash
# ============================================
# IDRM Production Environment
# ============================================

# ------------------
# PostgreSQL + PostGIS
# ------------------
POSTGRES_DB=idrm_production
POSTGRES_USER=idrm_prod_user
POSTGRES_PASSWORD=GENERATE_SECURE_PASSWORD_HERE

DATABASE_URL=postgresql+asyncpg://idrm_prod_user:SECURE_PASSWORD@postgres:5432/idrm_production
DATABASE_URL_SYNC=postgresql://idrm_prod_user:SECURE_PASSWORD@postgres:5432/idrm_production

# ------------------
# Redis
# ------------------
REDIS_PASSWORD=GENERATE_SECURE_PASSWORD_HERE
REDIS_URL=redis://:SECURE_PASSWORD@redis:6379/0

# ------------------
# JWT
# ------------------
JWT_SECRET_KEY=GENERATE_HEX_64_CHARS_HERE
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# ------------------
# Services
# ------------------
AUTH_SERVICE_PORT=8000
SERVICE_MGMT_PORT=8001
GEOSPATIAL_SERVICE_PORT=8002
ANALYTICS_SERVICE_PORT=8003
NOTIFICATION_SERVICE_PORT=8004
API_GATEWAY_PORT=3000

# ------------------
# Geospatial
# ------------------
TILE_CACHE_DIR=/var/cache/tiles
MAX_TILE_CACHE_SIZE_MB=5000
ENABLE_TILE_CACHING=true

# ------------------
# Email (Production)
# ------------------
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=APP_PASSWORD_HERE
MAIL_FROM=noreply@yourdomain.com

# ------------------
# Environment
# ------------------
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=WARNING

# ------------------
# CORS
# ------------------
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,https://api.yourdomain.com

# ------------------
# Sentry (Error Tracking)
# ------------------
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project-id
```

**Generate Secrets**:
```bash
# PostgreSQL password
openssl rand -base64 32

# Redis password
openssl rand -base64 32

# JWT secret
openssl rand -hex 64
```

---

### Step 11: Docker Compose Production

**docker-compose.production.yml** (key differences from staging):

```yaml
version: '3.8'

services:
  postgres:
    image: postgis/postgis:16-3.4
    # ... (same as staging but with production env vars)
    volumes:
      - postgres-data:/var/lib/postgresql/data
      - /backups/postgres:/backups:rw  # Backup mount
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 4G
    restart: always  # Changed from unless-stopped

  redis:
    image: redis:7.2-alpine
    # ... (same as staging)
    restart: always

  geospatial-service:
    build:
      context: ./backend/services/geospatial
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 2G
      replicas: 2  # Production: multiple replicas
    restart: always

  # ... other services with production settings

  nginx:
    image: nginx:1.24-alpine
    volumes:
      - ./nginx/production.conf:/etc/nginx/conf.d/default.conf:ro
      - ./frontend/html-tailwind/dist:/usr/share/nginx/html:ro
      - /etc/letsencrypt:/etc/letsencrypt:ro  # SSL certificates
      - nginx-logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    restart: always

volumes:
  postgres-data:
    driver: local
    driver_opts:
      type: none
      device: /mnt/data/postgres
      o: bind
```

---

### Step 12: Deploy to Production

```bash
# Clone repository
git clone https://github.com/your-org/idrm-mvp.git /opt/idrm
cd /opt/idrm

# Checkout production branch
git checkout main

# Create environment file
cp .env.production.example .env.production
nano .env.production  # Add secure passwords

# Build images
docker compose -f docker-compose.production.yml build --no-cache

# Start services
docker compose -f docker-compose.production.yml up -d

# Run migrations
docker compose -f docker-compose.production.yml exec auth-service \
    alembic upgrade head

# Check status
docker compose -f docker-compose.production.yml ps
```

---

## 📊 Monitoring

### Step 13: Prometheus + Grafana

**Install Prometheus**:

```bash
# Create monitoring directory
mkdir -p /opt/idrm/monitoring/{prometheus,grafana}

# Prometheus configuration
tee /opt/idrm/monitoring/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'docker'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx-exporter:9113']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']
EOF

# Add to docker-compose.production.yml
cat >> docker-compose.production.yml << 'EOF'
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
    ports:
      - "9090:9090"
    networks:
      - idrm-network
    restart: always

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=CHANGE_ME
    ports:
      - "3001:3000"
    networks:
      - idrm-network
    restart: always
EOF
```

---

### Step 14: Log Aggregation

**Configure Centralized Logging**:

```bash
# Update docker-compose.production.yml for all services
services:
  geospatial-service:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

---

## 💾 Backups

### Step 15: Automated Backup Script

**/opt/idrm/scripts/backup-production.sh**:

```bash
#!/bin/bash
# IDRM Production Backup Script

set -e

BACKUP_DIR="/backups/idrm"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p $BACKUP_DIR/{database,volumes,configs}

echo "Starting backup: $DATE"

# Backup PostgreSQL
echo "Backing up database..."
docker compose -f /opt/idrm/docker-compose.production.yml exec -T postgres \
    pg_dump -U idrm_prod_user -Fc idrm_production > \
    $BACKUP_DIR/database/db_$DATE.dump

# Backup Docker volumes
echo "Backing up volumes..."
docker run --rm \
    -v idrm_postgres-data:/data:ro \
    -v $BACKUP_DIR/volumes:/backup \
    alpine tar czf /backup/postgres_$DATE.tar.gz /data

# Backup configuration files
echo "Backing up configs..."
tar czf $BACKUP_DIR/configs/configs_$DATE.tar.gz \
    /opt/idrm/.env.production \
    /opt/idrm/docker-compose.production.yml \
    /opt/idrm/nginx/production.conf

# Upload to S3 (optional)
if command -v aws &> /dev/null; then
    echo "Uploading to S3..."
    aws s3 sync $BACKUP_DIR s3://your-backup-bucket/idrm/ \
        --storage-class GLACIER
fi

# Clean old backups
echo "Cleaning old backups..."
find $BACKUP_DIR -type f -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $DATE"
echo "Size: $(du -sh $BACKUP_DIR | cut -f1)"
```

**Make Executable and Schedule**:

```bash
chmod +x /opt/idrm/scripts/backup-production.sh

# Add to crontab
crontab -e

# Daily backup at 2 AM
0 2 * * * /opt/idrm/scripts/backup-production.sh >> /var/log/idrm-backup.log 2>&1

# Weekly full backup at 3 AM Sunday
0 3 * * 0 /opt/idrm/scripts/backup-production.sh full >> /var/log/idrm-backup.log 2>&1
```

---

### Step 16: Test Backup Restore

```bash
# Test database restore
gunzip -c /backups/idrm/database/db_20260510_020000.dump | \
    docker compose -f /opt/idrm/docker-compose.production.yml exec -T postgres \
    pg_restore -U idrm_prod_user -d idrm_production_test -c

# Verify restore
docker compose -f /opt/idrm/docker-compose.production.yml exec postgres \
    psql -U idrm_prod_user -d idrm_production_test -c "\dt"
```

---

## 🔄 Zero-Downtime Deployment

### Step 17: Rolling Update Script

**/opt/idrm/scripts/deploy-production.sh**:

```bash
#!/bin/bash
# Zero-downtime production deployment

set -e

cd /opt/idrm

echo "Pulling latest code..."
git fetch origin main
git checkout main
git pull origin main

echo "Building new images..."
docker compose -f docker-compose.production.yml build

echo "Running database migrations..."
docker compose -f docker-compose.production.yml exec -T auth-service \
    alembic upgrade head

echo "Deploying services (zero-downtime)..."
# Update services one by one
for service in geospatial-service auth-service service-mgmt analytics notifications api-gateway; do
    echo "Updating $service..."
    docker compose -f docker-compose.production.yml up -d --no-deps --build $service
    sleep 10  # Wait for health check
done

echo "Reloading NGINX..."
docker compose -f docker-compose.production.yml exec nginx nginx -s reload

echo "Deployment complete!"
echo "New version: $(git describe --tags --always)"
```

---

## 📝 Maintenance

### Health Monitoring

```bash
# Check all services
docker compose -f /opt/idrm/docker-compose.production.yml ps

# Check logs for errors
docker compose -f /opt/idrm/docker-compose.production.yml logs --tail=100 | grep ERROR

# Monitor resource usage
docker stats --no-stream

# Check disk usage
df -h
docker system df
```

---

### Regular Maintenance Tasks

**Weekly**:
- [ ] Review logs for errors
- [ ] Check backup success
- [ ] Monitor disk space
- [ ] Review security logs
- [ ] Check SSL certificate expiry

**Monthly**:
- [ ] Update Docker images
- [ ] Review and optimize database
- [ ] Test disaster recovery
- [ ] Review access logs
- [ ] Update documentation

**Quarterly**:
- [ ] Security audit
- [ ] Performance optimization
- [ ] Capacity planning
- [ ] Update dependencies

---

## 🚨 Emergency Procedures

### Rollback Deployment

```bash
# Stop current version
docker compose -f /opt/idrm/docker-compose.production.yml down

# Checkout previous version
git checkout <previous-commit-hash>

# Start services
docker compose -f /opt/idrm/docker-compose.production.yml up -d
```

---

### Database Emergency Restore

```bash
# Stop application
docker compose -f /opt/idrm/docker-compose.production.yml stop

# Restore database
pg_restore -U idrm_prod_user -d idrm_production < /backups/last_good_backup.dump

# Start application
docker compose -f /opt/idrm/docker-compose.production.yml start
```

---

## ✅ Production Checklist

### Pre-Launch ✅
- [ ] SSL certificate installed and tested
- [ ] Firewall configured (UFW)
- [ ] Fail2Ban enabled
- [ ] Automated backups scheduled
- [ ] Monitoring configured
- [ ] DNS records verified
- [ ] Load testing completed
- [ ] Security audit passed
- [ ] Documentation updated

### Launch ✅
- [ ] All services healthy
- [ ] HTTPS enforced
- [ ] Logs being collected
- [ ] Backups verified
- [ ] Monitoring alerts working
- [ ] Emergency contacts notified

### Post-Launch ✅
- [ ] Monitor for 24 hours
- [ ] Review logs daily for 1 week
- [ ] Test backup restore
- [ ] Verify SSL auto-renewal
- [ ] Document any issues

---

**Production environment ready! 🎉**

**Critical**: Always test changes in staging first!
