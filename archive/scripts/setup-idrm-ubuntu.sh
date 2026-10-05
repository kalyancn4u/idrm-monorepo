#!/bin/bash

################################################################################
# IDRM MVP - Ubuntu Monolith Setup Script
# 
# This script sets up a complete development environment for IDRM on Ubuntu
# - PostgreSQL 16 + PostGIS 3.4 (native)
# - MinIO (S3-compatible object storage, native systemd service) + mc client
# - Miniconda (Python 3.11)
# - Development tools (VSCodium, DBeaver, Chrome)
# - All necessary dependencies
#
# Features:
# - Idempotent: Safe to run multiple times
# - Progress indicators and notifications
# - Checks before installing
# - Detailed logging
#
# Usage:
#   chmod +x setup-idrm-ubuntu.sh
#   ./setup-idrm-ubuntu.sh
#
# Tested on: Ubuntu 22.04 LTS, 24.04 LTS
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="$HOME/idrm-setup.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

notify() {
    if command -v notify-send &> /dev/null; then
        notify-send "IDRM Setup" "$1"
    fi
}

check_installed() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

check_version() {
    local cmd=$1
    local min_version=$2
    local current_version=$($cmd 2>/dev/null || echo "0")
    
    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" = "$min_version" ]; then
        return 0
    else
        return 1
    fi
}

################################################################################
# System Information
################################################################################

log_info "========================================="
log_info "IDRM MVP - Ubuntu Setup Script"
log_info "========================================="
log_info "System: $(lsb_release -d | cut -f2)"
log_info "Kernel: $(uname -r)"
log_info "User: $USER"
log_info "Home: $HOME"
log_info "Date: $(date)"
log_info "Log file: $LOG_FILE"
log_info "========================================="

################################################################################
# 1. System Updates and Base Dependencies
################################################################################

log_info "Step 1: Updating system and installing base dependencies..."

if [ -f /var/run/reboot-required ]; then
    log_warning "System reboot required. Please reboot and run this script again."
    exit 1
fi

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    log_error "Please do not run this script as root or with sudo"
    log_error "The script will ask for sudo password when needed"
    exit 1
fi

# Update package lists
log_info "Updating package lists..."
sudo apt update

# Install essential build tools
log_info "Installing essential build tools..."
sudo apt install -y \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    curl \
    wget \
    git \
    gnupg \
    lsb-release \
    unzip \
    zip \
    libssl-dev \
    libffi-dev \
    libbz2-dev \
    libreadline-dev \
    libsqlite3-dev \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libxml2-dev \
    libxmlsec1-dev \
    liblzma-dev

log_success "Base dependencies installed"

################################################################################
# 2. PostgreSQL 16 + PostGIS 3.4
################################################################################

log_info "Step 2: Installing PostgreSQL 16 + PostGIS 3.4..."

if check_installed psql; then
    CURRENT_PG_VERSION=$(psql --version | grep -oP '\d+' | head -1)
    if [ "$CURRENT_PG_VERSION" -ge 16 ]; then
        log_success "PostgreSQL $CURRENT_PG_VERSION already installed"
    else
        log_warning "PostgreSQL $CURRENT_PG_VERSION found, but version 16+ required"
        read -p "Upgrade to PostgreSQL 16? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_error "PostgreSQL 16 required. Exiting."
            exit 1
        fi
    fi
else
    log_info "Installing PostgreSQL 16..."
    
    # Add PostgreSQL official repository
    sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    
    sudo apt update
    sudo apt install -y postgresql-16 postgresql-contrib-16 postgresql-server-dev-16
    
    log_success "PostgreSQL 16 installed"
fi

# Install PostGIS
if dpkg -l | grep -q postgis; then
    log_success "PostGIS already installed"
else
    log_info "Installing PostGIS 3.4..."
    sudo apt install -y postgresql-16-postgis-3 postgresql-16-postgis-3-scripts
    log_success "PostGIS 3.4 installed"
fi

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check PostgreSQL status
if sudo systemctl is-active --quiet postgresql; then
    log_success "PostgreSQL is running"
else
    log_error "PostgreSQL failed to start"
    exit 1
fi

################################################################################
# 3. Create IDRM Database and User
################################################################################

log_info "Step 3: Setting up IDRM database..."

# Check if database exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw idrm_db; then
    log_warning "Database 'idrm_db' already exists"
    read -p "Recreate database? This will DELETE all existing data! (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo -u postgres psql -c "DROP DATABASE idrm_db;"
        sudo -u postgres psql -c "DROP USER IF EXISTS idrm_user;"
        log_info "Existing database dropped"
    else
        log_info "Keeping existing database"
    fi
fi

# Create user and database if they don't exist
if ! sudo -u postgres psql -c "SELECT 1 FROM pg_user WHERE usename = 'idrm_user'" | grep -q 1; then
    log_info "Creating database user 'idrm_user'..."
    sudo -u postgres psql -c "CREATE USER idrm_user WITH PASSWORD 'idrm_secure_password_2024';"
    log_success "Database user created"
fi

if ! sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw idrm_db; then
    log_info "Creating database 'idrm_db'..."
    sudo -u postgres psql -c "CREATE DATABASE idrm_db OWNER idrm_user;"
    log_success "Database created"
fi

# Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE idrm_db TO idrm_user;"

# Enable PostGIS extension
log_info "Enabling PostGIS extension..."
sudo -u postgres psql -d idrm_db -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d idrm_db -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;"

# Verify PostGIS
PG_VERSION=$(sudo -u postgres psql -d idrm_db -c "SELECT PostGIS_version();" -t | xargs)
log_success "PostGIS enabled: $PG_VERSION"

# Configure PostgreSQL for local access
PG_HBA_FILE="/etc/postgresql/16/main/pg_hba.conf"
if ! grep -q "idrm_user" "$PG_HBA_FILE"; then
    log_info "Configuring PostgreSQL authentication..."
    sudo bash -c "echo '# IDRM access' >> $PG_HBA_FILE"
    sudo bash -c "echo 'local   idrm_db   idrm_user   md5' >> $PG_HBA_FILE"
    sudo bash -c "echo 'host    idrm_db   idrm_user   127.0.0.1/32   md5' >> $PG_HBA_FILE"
    sudo systemctl reload postgresql
    log_success "PostgreSQL authentication configured"
fi

################################################################################
# 3B. MinIO Object Storage (S3-compatible, native systemd service)
################################################################################
#
# The MVP stores uploaded photos/documents (incident evidence, completion proof)
# in MinIO, not in PostgreSQL. MinIO speaks the S3 API, so the same code carries
# unchanged into the FFP (distributed MinIO / cloud S3). Installed natively as a
# systemd service (no Docker in the MVP).

log_info "Step 3B: Installing MinIO object storage..."

MINIO_USER="minio-user"
MINIO_DATA_DIR="/var/lib/minio"
MINIO_ENV_FILE="/etc/default/minio"
MINIO_ROOT_USER="idrm_minio_admin"
MINIO_ROOT_PASSWORD="idrm_minio_password_2024"
MINIO_BUCKET="idrm-uploads"

# Install the MinIO server binary
if check_installed minio; then
    log_success "MinIO already installed: $(minio --version 2>/dev/null | head -1)"
else
    log_info "Downloading MinIO server binary..."
    wget -q https://dl.min.io/server/minio/release/linux-amd64/minio -O /tmp/minio
    sudo install -m 755 /tmp/minio /usr/local/bin/minio
    rm -f /tmp/minio
    log_success "MinIO server installed to /usr/local/bin/minio"
fi

# Install the MinIO client (mc) — used to create the bucket
if check_installed mc; then
    log_success "MinIO client (mc) already installed"
else
    log_info "Downloading MinIO client (mc)..."
    wget -q https://dl.min.io/client/mc/release/linux-amd64/mc -O /tmp/mc
    sudo install -m 755 /tmp/mc /usr/local/bin/mc
    rm -f /tmp/mc
    log_success "MinIO client installed to /usr/local/bin/mc"
fi

# Create a dedicated system user and data directory
if ! id -u "$MINIO_USER" &>/dev/null; then
    log_info "Creating system user '$MINIO_USER'..."
    sudo useradd -r -s /sbin/nologin "$MINIO_USER"
fi
sudo mkdir -p "$MINIO_DATA_DIR"
sudo chown -R "$MINIO_USER:$MINIO_USER" "$MINIO_DATA_DIR"

# Environment file (credentials + volumes + console port)
if [ ! -f "$MINIO_ENV_FILE" ]; then
    log_info "Writing MinIO environment file $MINIO_ENV_FILE..."
    sudo bash -c "cat > $MINIO_ENV_FILE" << EOF
# MinIO configuration for IDRM (MVP). CHANGE THESE CREDENTIALS for anything
# beyond local development, and keep them out of source control.
MINIO_ROOT_USER=$MINIO_ROOT_USER
MINIO_ROOT_PASSWORD=$MINIO_ROOT_PASSWORD
MINIO_VOLUMES="$MINIO_DATA_DIR"
# S3 API on :9000, web console on :9001
MINIO_OPTS="--console-address :9001"
EOF
    sudo chmod 640 "$MINIO_ENV_FILE"
    log_success "MinIO environment file created"
else
    log_success "MinIO environment file already exists"
fi

# systemd service
if [ ! -f /etc/systemd/system/minio.service ]; then
    log_info "Creating MinIO systemd service..."
    sudo bash -c 'cat > /etc/systemd/system/minio.service' << EOF
[Unit]
Description=MinIO Object Storage (IDRM)
Documentation=https://min.io/docs
Wants=network-online.target
After=network-online.target

[Service]
User=$MINIO_USER
Group=$MINIO_USER
EnvironmentFile=$MINIO_ENV_FILE
ExecStart=/usr/local/bin/minio server \$MINIO_VOLUMES \$MINIO_OPTS
Restart=always
RestartSec=5
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    log_success "MinIO systemd service created"
fi

# Start and enable
sudo systemctl enable minio >/dev/null 2>&1
sudo systemctl restart minio

# Wait for the S3 endpoint to come up
log_info "Waiting for MinIO to become ready on :9000..."
for i in $(seq 1 20); do
    if curl -fsS http://127.0.0.1:9000/minio/health/live >/dev/null 2>&1; then
        break
    fi
    sleep 1
done

if sudo systemctl is-active --quiet minio; then
    log_success "MinIO is running (S3: http://localhost:9000 · Console: http://localhost:9001)"
    # Create the IDRM bucket (idempotent)
    log_info "Creating bucket '$MINIO_BUCKET'..."
    mc alias set idrmlocal http://127.0.0.1:9000 "$MINIO_ROOT_USER" "$MINIO_ROOT_PASSWORD" >/dev/null 2>&1 || true
    mc mb --ignore-existing "idrmlocal/$MINIO_BUCKET" >/dev/null 2>&1 || true
    log_success "Bucket '$MINIO_BUCKET' ready"
else
    log_error "MinIO failed to start — check: sudo journalctl -u minio -e"
fi

################################################################################
# 4. Miniconda Installation
################################################################################

log_info "Step 4: Installing Miniconda..."

CONDA_DIR="$HOME/miniconda3"

if [ -d "$CONDA_DIR" ]; then
    log_success "Miniconda already installed at $CONDA_DIR"
else
    log_info "Downloading Miniconda installer..."
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /tmp/miniconda.sh
    
    log_info "Installing Miniconda..."
    bash /tmp/miniconda.sh -b -p "$CONDA_DIR"
    
    rm /tmp/miniconda.sh
    log_success "Miniconda installed"
fi

# Initialize conda
log_info "Initializing conda..."
eval "$($CONDA_DIR/bin/conda shell.bash hook)"
"$CONDA_DIR/bin/conda" init bash

# Add conda to PATH if not already there
if ! grep -q "miniconda3/bin" "$HOME/.bashrc"; then
    echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> "$HOME/.bashrc"
fi

# Verify conda
if [ -f "$CONDA_DIR/bin/conda" ]; then
    CONDA_VERSION=$("$CONDA_DIR/bin/conda" --version)
    log_success "Conda installed: $CONDA_VERSION"
else
    log_error "Conda installation failed"
    exit 1
fi

################################################################################
# 5. Development Tools
################################################################################
#
# NOTE: There is no JavaScript-runtime step here. The IDRM MVP frontend is
# HTML + Tailwind CSS v4 + vanilla JavaScript + Leaflet, served directly by
# FastAPI — it needs no Bun/Node/Deno build step (ADR-003 / ADR-014). Bun and
# the rest of the JS toolchain belong to the FFP phase.

log_info "Step 5: Installing development tools..."

# VSCodium (Open-source VSCode)
if check_installed codium; then
    log_success "VSCodium already installed"
else
    log_info "Installing VSCodium..."
    wget -qO - https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg \
        | gpg --dearmor \
        | sudo dd of=/usr/share/keyrings/vscodium-archive-keyring.gpg
    
    echo 'deb [ signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg ] https://download.vscodium.com/debs vscodium main' \
        | sudo tee /etc/apt/sources.list.d/vscodium.list
    
    sudo apt update
    sudo apt install -y codium
    log_success "VSCodium installed"
fi

# Alternatively, VSCode (official Microsoft version)
if ! check_installed codium && ! check_installed code; then
    log_info "Would you like to install VSCode (Microsoft version) instead? (y/n)"
    read -p "Install VSCode? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg
        sudo install -D -o root -g root -m 644 packages.microsoft.gpg /etc/apt/keyrings/packages.microsoft.gpg
        sudo sh -c 'echo "deb [arch=amd64,arm64,armhf signed-by=/etc/apt/keyrings/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main" > /etc/apt/sources.list.d/vscode.list'
        rm -f packages.microsoft.gpg
        
        sudo apt update
        sudo apt install -y code
        log_success "VSCode installed"
    fi
fi

# Google Chrome
if check_installed google-chrome; then
    log_success "Google Chrome already installed"
else
    log_info "Installing Google Chrome..."
    wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
    sudo apt update
    sudo apt install -y google-chrome-stable
    log_success "Google Chrome installed"
fi

# DBeaver (Database Management)
if check_installed dbeaver; then
    log_success "DBeaver already installed"
else
    log_info "Installing DBeaver..."
    wget https://dbeaver.io/files/dbeaver-ce_latest_amd64.deb -O /tmp/dbeaver.deb
    sudo apt install -y /tmp/dbeaver.deb
    rm /tmp/dbeaver.deb
    log_success "DBeaver installed"
fi

# Git configuration
log_info "Configuring Git..."
if [ -z "$(git config --global user.name)" ]; then
    read -p "Enter your Git username: " git_username
    git config --global user.name "$git_username"
fi

if [ -z "$(git config --global user.email)" ]; then
    read -p "Enter your Git email: " git_email
    git config --global user.email "$git_email"
fi

log_success "Git configured"

################################################################################
# 6. Additional Development Tools
################################################################################

log_info "Step 6: Installing additional development tools..."

# HTTPie (better curl)
if ! check_installed http; then
    sudo apt install -y httpie
    log_success "HTTPie installed"
fi

# jq (JSON processor)
if ! check_installed jq; then
    sudo apt install -y jq
    log_success "jq installed"
fi

# Postman (API testing) - Optional
if ! check_installed postman; then
    log_info "Would you like to install Postman? (y/n)"
    read -p "Install Postman? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo snap install postman
        log_success "Postman installed"
    fi
fi

# pgAdmin (PostgreSQL GUI) - Optional
if ! check_installed pgadmin4; then
    log_info "Would you like to install pgAdmin 4? (y/n)"
    read -p "Install pgAdmin? " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg
        sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/$(lsb_release -cs) pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'
        sudo apt update
        sudo apt install -y pgadmin4-desktop
        log_success "pgAdmin 4 installed"
    fi
fi

################################################################################
# 7. Create IDRM Project Structure
################################################################################

log_info "Step 7: Creating IDRM project structure..."

PROJECT_DIR="$HOME/projects/idrm-mvp"

if [ -d "$PROJECT_DIR" ]; then
    log_warning "Project directory already exists: $PROJECT_DIR"
    read -p "Reinitialize project structure? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Skipping project initialization"
    else
        rm -rf "$PROJECT_DIR"
        log_info "Removed existing project"
    fi
fi

if [ ! -d "$PROJECT_DIR" ]; then
    log_info "Creating project at $PROJECT_DIR..."
    
    mkdir -p "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    # Initialize Git
    git init
    git branch -M main
    
    # Create directory structure
    mkdir -p backend/app/{api/v1,core,db,models,schemas,services,tests}
    # Frontend = static HTML + Tailwind CSS + vanilla JS + Leaflet, served by FastAPI
    # (no JS build step in the MVP). Templates + static assets only.
    mkdir -p frontend/templates
    mkdir -p frontend/static/{css,js,img}
    mkdir -p database/{migrations,seeds,backups}
    mkdir -p docs
    mkdir -p scripts
    mkdir -p logs
    
    # Create .gitignore
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*.so
.Python
*.egg-info/
dist/
build/

# Conda
.conda/

# Environment
.env
.env.local
*.local

# Logs
logs/
*.log

# Database
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Backups
*.bak
database/backups/*.sql
EOF
    
    # Create README
    cat > README.md << 'EOF'
# IDRM MVP - Integrated Disaster Response Management

A unified, map-driven disaster response platform for India.

## Tech Stack

- **Database**: PostgreSQL 16 + PostGIS 3.4 (native)
- **Object storage**: MinIO (S3-compatible) for uploaded photos/documents
- **Backend**: Python 3.11 + FastAPI (Miniconda)
- **Frontend**: HTML + Tailwind CSS v4 + vanilla JavaScript + Leaflet, served by FastAPI (no JS build step)

## Quick Start

See `docs/SETUP.md` for detailed instructions.

## Development

```bash
# Backend + frontend are one FastAPI app (the frontend is served as
# static HTML/Tailwind/JS from the same server — there is no separate
# frontend dev server in the MVP).
conda activate idrm-mvp
cd backend
uvicorn app.main:app --reload   # serves the API and the web UI on :8000
```

## Database

```bash
# Connect to database
psql -U idrm_user -d idrm_db

# Backup
./scripts/backup-db.sh

# Restore
./scripts/restore-db.sh <backup-file>
```
EOF
    
    log_success "Project structure created"
fi

################################################################################
# 8. Create Conda Environment
################################################################################

log_info "Step 8: Creating conda environment 'idrm-mvp'..."

# Source conda
eval "$($HOME/miniconda3/bin/conda shell.bash hook)"

# Check if environment exists
if conda env list | grep -q "idrm-mvp"; then
    log_warning "Conda environment 'idrm-mvp' already exists"
    read -p "Recreate environment? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        conda env remove -n idrm-mvp -y
        log_info "Removed existing environment"
    else
        log_info "Keeping existing environment"
    fi
fi

if ! conda env list | grep -q "idrm-mvp"; then
    log_info "Creating Python 3.11 environment..."
    conda create -n idrm-mvp python=3.11 -y
    log_success "Conda environment created"
fi

# Create environment.yml
cat > "$PROJECT_DIR/backend/environment.yml" << 'EOF'
name: idrm-mvp
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
    - fastapi==0.104.1
    - uvicorn[standard]==0.24.0
    - sqlalchemy==2.0.23
    - asyncpg==0.29.0
    - geoalchemy2==0.14.2
    - psycopg2-binary==2.9.9
    - python-jose[cryptography]==3.3.0
    - passlib[bcrypt]==1.7.4
    - python-multipart==0.0.6
    - pydantic==2.5.0
    - pydantic-settings==2.1.0
    - python-dotenv==1.0.0
    - shapely==2.0.2
    - boto3==1.34.34
    - pytest==7.4.3
    - pytest-asyncio==0.21.1
    - httpx==0.25.2
    - black==23.11.0
    - flake8==6.1.0
    - mypy==1.7.1
EOF

log_success "Environment configuration created"

################################################################################
# 9. Create Utility Scripts
################################################################################

log_info "Step 9: Creating utility scripts..."

# Database backup script
cat > "$PROJECT_DIR/scripts/backup-db.sh" << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/projects/idrm-mvp/database/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/idrm_backup_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

echo "Backing up database to $BACKUP_FILE..."
PGPASSWORD='idrm_secure_password_2024' pg_dump -U idrm_user -d idrm_db > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
    gzip "$BACKUP_FILE"
    echo "Compressed to: ${BACKUP_FILE}.gz"
else
    echo "Backup failed!"
    exit 1
fi
EOF

# Database restore script
cat > "$PROJECT_DIR/scripts/restore-db.sh" << 'EOF'
#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: ./restore-db.sh <backup-file.sql.gz>"
    exit 1
fi

BACKUP_FILE=$1

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "Restoring database from $BACKUP_FILE..."

# Decompress if needed
if [[ $BACKUP_FILE == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" | PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user -d idrm_db
else
    PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user -d idrm_db < "$BACKUP_FILE"
fi

if [ $? -eq 0 ]; then
    echo "Restore successful!"
else
    echo "Restore failed!"
    exit 1
fi
EOF

# Dev startup script
cat > "$PROJECT_DIR/scripts/dev-start.sh" << 'EOF'
#!/bin/bash
PROJECT_ROOT="$HOME/projects/idrm-mvp"

echo "Starting IDRM development environment..."

# Check PostgreSQL
if ! systemctl is-active --quiet postgresql; then
    echo "Starting PostgreSQL..."
    sudo systemctl start postgresql
fi

# Start the app in a new terminal. The MVP is a single FastAPI app that serves
# BOTH the /api/v1 API and the web UI (static HTML + Tailwind + JS + Leaflet),
# so there is no separate frontend server to start.
gnome-terminal --tab --title="IDRM (API + Web UI)" -- bash -c "
    cd $PROJECT_ROOT/backend
    source $HOME/miniconda3/bin/activate idrm-mvp
    uvicorn app.main:app --reload --port 8000
    exec bash
"

echo "Development server starting..."
echo "App (API + Web UI): http://localhost:8000"
EOF

# Make scripts executable
chmod +x "$PROJECT_DIR"/scripts/*.sh

log_success "Utility scripts created"

################################################################################
# 10. Configure VSCodium/VSCode
################################################################################

log_info "Step 10: Configuring editor..."

# Create workspace settings
mkdir -p "$PROJECT_DIR/.vscode"

cat > "$PROJECT_DIR/.vscode/settings.json" << 'EOF'
{
    "python.defaultInterpreterPath": "${env:HOME}/miniconda3/envs/idrm-mvp/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "editor.rulers": [88, 120],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "terminal.integrated.env.linux": {
        "CONDA_DEFAULT_ENV": "idrm-mvp"
    }
}
EOF

cat > "$PROJECT_DIR/.vscode/extensions.json" << 'EOF'
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "bradlc.vscode-tailwindcss",
        "dbaeumer.vscode-eslint",
        "esbenp.prettier-vscode",
        "mhutchie.git-graph",
        "eamodio.gitlens"
    ]
}
EOF

log_success "Editor configured"

################################################################################
# 11. Configure DBeaver Connection
################################################################################

log_info "Step 11: Creating DBeaver connection template..."

mkdir -p "$HOME/.local/share/DBeaverData/workspace6/General/Scripts"

cat > "$PROJECT_DIR/docs/dbeaver-connection.md" << 'EOF'
# DBeaver Connection Setup

1. Open DBeaver
2. Click "New Database Connection"
3. Select PostgreSQL
4. Enter connection details:
   - Host: localhost
   - Port: 5432
   - Database: idrm_db
   - Username: idrm_user
   - Password: idrm_secure_password_2024
5. Click "Test Connection"
6. Click "Finish"

## Useful Queries

```sql
-- Check PostGIS version
SELECT PostGIS_version();

-- List all tables
\dt

-- View service requests
SELECT 
    service_id,
    service_type,
    priority,
    ST_AsText(location) as location_wkt,
    status,
    created_at
FROM service_requests;

-- Find services within 10km of a point
SELECT *
FROM service_requests
WHERE ST_DWithin(
    location::geography,
    ST_MakePoint(78.4867, 17.3850)::geography,
    10000
);
```
EOF

log_success "DBeaver connection template created"

################################################################################
# 12. Final Verification
################################################################################

log_info "Step 12: Final verification..."

echo ""
log_info "========================================="
log_info "Verification Results:"
log_info "========================================="

# PostgreSQL
if systemctl is-active --quiet postgresql; then
    PG_VERSION=$(psql --version | grep -oP '\d+\.\d+' | head -1)
    log_success "PostgreSQL $PG_VERSION - Running"
else
    log_error "PostgreSQL - Not running"
fi

# Database connectivity
if PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user -d idrm_db -c "SELECT 1" &> /dev/null; then
    log_success "Database connection - OK"
else
    log_error "Database connection - Failed"
fi

# PostGIS
POSTGIS_VERSION=$(PGPASSWORD='idrm_secure_password_2024' psql -U idrm_user -d idrm_db -t -c "SELECT PostGIS_version();" | xargs)
log_success "PostGIS - $POSTGIS_VERSION"

# MinIO
if sudo systemctl is-active --quiet minio; then
    log_success "MinIO - Running (S3 :9000 · Console :9001)"
else
    log_warning "MinIO - Not running"
fi

# Conda
if [ -f "$HOME/miniconda3/bin/conda" ]; then
    CONDA_VERSION=$("$HOME/miniconda3/bin/conda" --version | cut -d' ' -f2)
    log_success "Conda $CONDA_VERSION - Installed"
else
    log_error "Conda - Not found"
fi

# VSCodium/VSCode
if check_installed codium; then
    log_success "VSCodium - Installed"
elif check_installed code; then
    log_success "VSCode - Installed"
else
    log_warning "No code editor found"
fi

# Chrome
if check_installed google-chrome; then
    log_success "Google Chrome - Installed"
else
    log_warning "Google Chrome - Not installed"
fi

# DBeaver
if check_installed dbeaver; then
    log_success "DBeaver - Installed"
else
    log_warning "DBeaver - Not installed"
fi

# Git
GIT_VERSION=$(git --version | cut -d' ' -f3)
log_success "Git $GIT_VERSION - Configured"

################################################################################
# 13. Summary and Next Steps
################################################################################

echo ""
log_info "========================================="
log_success "IDRM Setup Complete!"
log_info "========================================="
echo ""
log_info "Project Location: $PROJECT_DIR"
log_info "Log File: $LOG_FILE"
echo ""
log_info "Next Steps:"
echo "  1. Reload your shell: source ~/.bashrc"
echo "  2. Activate conda environment: conda activate idrm-mvp"
echo "  3. Navigate to project: cd $PROJECT_DIR"
echo "  4. Follow the quick start guide in docs/"
echo ""
log_info "Database:"
echo "  • Database: idrm_db"
echo "  • User: idrm_user"
echo "  • Password: idrm_secure_password_2024"
echo "  • Connect: psql -U idrm_user -d idrm_db"
echo ""
log_info "Object storage (MinIO):"
echo "  • S3 endpoint: http://localhost:9000"
echo "  • Web console: http://localhost:9001"
echo "  • Access key: idrm_minio_admin"
echo "  • Secret key: idrm_minio_password_2024"
echo "  • Bucket: idrm-uploads"
echo "  • Service: sudo systemctl status minio"
echo "  • ⚠️  Change these credentials before any non-local use."
echo ""
log_info "Development Tools:"
echo "  • Editor: codium (or code)"
echo "  • Database GUI: DBeaver"
echo "  • Browser: Google Chrome"
echo "  • API Testing: HTTPie, Postman"
echo ""
log_info "Useful Scripts:"
echo "  • Backup DB: ./scripts/backup-db.sh"
echo "  • Restore DB: ./scripts/restore-db.sh <file>"
echo "  • Start Dev: ./scripts/dev-start.sh"
echo ""
log_info "Documentation:"
echo "  • DBeaver Setup: docs/dbeaver-connection.md"
echo "  • Project README: README.md"
echo ""

# Desktop notification
notify "IDRM setup complete! Check terminal for details."

log_success "All done! Happy coding! 🚀"
echo ""
