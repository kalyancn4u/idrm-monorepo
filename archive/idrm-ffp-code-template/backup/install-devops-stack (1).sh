#!/usr/bin/env bash
# =============================================================================
# FILE    : scripts/install-devops-stack.sh
# PROJECT : IDRM — Full-stack + DSML DevOps Stack
#
# PURPOSE : Install the complete IDRM DevOps stack on Ubuntu 22.04 / 24.04.
#           Idempotent — checks before every install; safely skips what is
#           already present. Re-run at any time without side effects.
#
# USAGE   : bash scripts/install-devops-stack.sh [OPTIONS]
#
# OPTIONS :
#   -y, --yes            Auto-answer YES to all prompts (unattended / CI use)
#   -n, --dry-run        Print what WOULD be installed; touch nothing
#       --skip-optional  Skip optional tools: Wine, multimedia, GNOME apps
#   -h, --help           Print this help text
#
# REQUIRES:
#   · Ubuntu 22.04 LTS or 24.04 LTS (64-bit, x86_64)
#   · sudo privileges
#   · Active internet connection
#   · Run as a NORMAL USER — the script calls sudo internally where needed.
#     Running as root will cause it to exit immediately.
#
# WHAT IS INSTALLED (mirrors check-devops-stack.sh exactly):
#   APT   Core tools, Python build libs, Java 21, PostgreSQL 16 + PostGIS 3,
#         Redis, NGINX, VSCodium, Google Chrome, Docker Engine + Compose,
#         Grafana OSS, Elasticsearch, WineHQ Stable, pgAdmin 4,
#         VLC, GIMP, OBS Studio, Tilix, Remmina, virt-manager, Caffeine, and more
#   Snap  Postman, Postbird, JOSM, WebStorm, IntelliJ IDEA CE, PyCharm CE,
#         figma-linux, Prometheus
#   Bin   Miniconda (Python 3.11), Bun (JS runtime), nvm + Node.js,
#         DBeaver CE, MongoDB Compass, Cursor, Insomnia, Bruno, ksnip AppImage
#   Conda idrm-mvp environment (Python 3.11 + all packages from environment.yml)
#   npm   Claude Code (@anthropic-ai/claude-code)
#   Ext   11 VSCodium/VS Code extensions (privacy-screened set)
#   SQL   PostGIS extension enabled in idrm_db
#   Dock  Metabase (port 3000) and Loki (port 3100) as Docker containers
#
# OUTPUT  : Coloured terminal output   +   ~/idrm-install.log
#
# NOTES   :
#   · NOT installed (no native Linux package exists):
#       Google Keep  — use Chrome → ⋮ → "Install Keep…" (PWA)
#       Grok CLI     — install manually from github.com/nicowillis/grok
#   · WineHQ adds i386 architecture (required for 32-bit Windows support).
#   · After the script finishes, run:  source ~/.bashrc
#     to pick up all new PATH entries (conda, bun, nvm).
#   · Docker group membership requires a logout/login to take effect.
# =============================================================================

# Intentionally NO -e: a failed install of one tool must not abort the rest.
set -uo pipefail
IFS=$'\n\t'

# ──────────────────────────────────────────────────────────────────────────────
# Script paths & temporaries
# ──────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOG_FILE="${HOME}/idrm-install.log"
TMP_DIR="$(mktemp -d /tmp/idrm-install.XXXXXX)"
trap 'rm -rf "$TMP_DIR"' EXIT    # clean up temp files on exit regardless of how the script ends

# Filled in during pre-flight; used in repo URL templates
UBUNTU_CODENAME=""
UBUNTU_VERSION=""

# ──────────────────────────────────────────────────────────────────────────────
# CLI flags
# ──────────────────────────────────────────────────────────────────────────────
AUTO_YES=false
DRY_RUN=false
SKIP_OPTIONAL=false

for _arg in "$@"; do
    case "$_arg" in
        -y|--yes)          AUTO_YES=true ;;
        -n|--dry-run)      DRY_RUN=true; AUTO_YES=true ;;
        --skip-optional)   SKIP_OPTIONAL=true ;;
        -h|--help)
            # Print the header comment block as help text
            sed -n '/^# USAGE/,/^# OUTPUT/p' "$0" | sed 's/^# \?//'
            exit 0 ;;
        *)
            printf "Unknown option: %s\nRun with --help for usage.\n" "$_arg" >&2
            exit 1 ;;
    esac
done

# ──────────────────────────────────────────────────────────────────────────────
# Installation counters (shown in final summary)
# ──────────────────────────────────────────────────────────────────────────────
CNT_INSTALLED=0     # newly installed this run
CNT_SKIPPED=0       # already present, skipped
CNT_FAILED=0        # installation attempted but failed

_START_TS=$(date +%s)

# ──────────────────────────────────────────────────────────────────────────────
# Colours (auto-disabled when stdout is redirected / not a TTY)
# ──────────────────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_OK='\033[0;32m'; C_WARN='\033[1;33m'; C_ERR='\033[0;31m'
    C_INFO='\033[0;36m'; C_STEP='\033[0;35m'; C_DIM='\033[2m'
    C_BOLD='\033[1m'; C_RST='\033[0m'
else
    C_OK='' C_WARN='' C_ERR='' C_INFO='' C_STEP='' C_DIM='' C_BOLD='' C_RST=''
fi

# ──────────────────────────────────────────────────────────────────────────────
# Output helpers
# ──────────────────────────────────────────────────────────────────────────────
_log() { printf "%s\n" "$*" >> "$LOG_FILE"; }

step() {
    printf "\n${C_BOLD}${C_STEP}"
    printf "  ══════════════════════════════════════════════════════════════════\n"
    printf "   %s\n" "$1"
    printf "  ══════════════════════════════════════════════════════════════════${C_RST}\n\n"
    _log ""; _log "[$1]"; _log "$(date '+%H:%M:%S')"
}

ok()   { CNT_INSTALLED=$(( CNT_INSTALLED + 1 ))
         printf "  ${C_OK}✔${C_RST}  %s\n" "$*"; _log "[ok]   $*"; }

skip() { CNT_SKIPPED=$(( CNT_SKIPPED + 1 ))
         printf "  ${C_DIM}→  %s (already installed)${C_RST}\n" "$*"; _log "[skip] $*"; }

info() { printf "  ${C_INFO}·${C_RST}  %s\n" "$*"; _log "[info] $*"; }

warn() { CNT_FAILED=$(( CNT_FAILED + 1 ))
         printf "  ${C_WARN}⚠${C_RST}  %s\n" "$*"; _log "[warn] $*"; }

die()  { printf "\n  ${C_ERR}✘  ERROR: %s${C_RST}\n\n" "$*" >&2
         _log "[die]  $*"; exit 1; }

note() { printf "  ${C_DIM}ℹ  %s${C_RST}\n" "$*"; _log "[note] $*"; }

confirm() {
    # In --yes or --dry-run mode every prompt is auto-confirmed
    $AUTO_YES && { info "Auto-yes: $*"; return 0; }
    printf "\n  ${C_WARN}%s [y/N]${C_RST} " "${1:-Continue?}"
    read -r -n 1 _reply; echo ""
    [[ "$_reply" =~ ^[Yy]$ ]]
}

# ──────────────────────────────────────────────────────────────────────────────
# Is-installed helpers (used for idempotency checks)
# ──────────────────────────────────────────────────────────────────────────────
is_bin()  { command -v "$1" &>/dev/null; }
is_deb()  { dpkg -l "$1" 2>/dev/null | grep -q '^ii'; }
is_snap() { command -v snap &>/dev/null && snap list "$1" 2>/dev/null | grep -q "^$1"; }

# ──────────────────────────────────────────────────────────────────────────────
# APT batch queue
# Packages are queued with apt_queue() and installed all at once with apt_flush().
# This is far more efficient than one `apt-get install` call per package.
# ──────────────────────────────────────────────────────────────────────────────
APT_QUEUE=()

apt_queue() {
    # $1 = apt package name   $2 = optional display name
    local pkg="$1" display="${2:-$1}"
    if is_deb "$pkg"; then
        skip "$display"
    else
        APT_QUEUE+=("$pkg")
        info "Queued: $display"
    fi
}

apt_flush() {
    # $1 = human-readable label for the batch
    local label="${1:-packages}"
    if [[ ${#APT_QUEUE[@]} -eq 0 ]]; then
        info "Nothing to install in this batch."
        return 0
    fi
    local count=${#APT_QUEUE[@]}
    info "Installing ${count} package(s) via apt…"
    if $DRY_RUN; then
        note "[dry-run] would install: ${APT_QUEUE[*]}"
        APT_QUEUE=()
        return 0
    fi
    sudo apt-get install -y "${APT_QUEUE[@]}" 2>&1 | tee -a "$LOG_FILE" \
        && ok "$label: ${count} package(s) installed" \
        || warn "$label: one or more packages failed — check $LOG_FILE"
    APT_QUEUE=()
}

# ──────────────────────────────────────────────────────────────────────────────
# Third-party APT repo setup (idempotent, modern signed-by method)
#
# add_repo  <name>  <key-url>  <keyfile>  <deb-line>
#   name     — short identifier → /etc/apt/sources.list.d/<name>.list
#   key-url  — GPG key URL (ASCII-armoured or binary; gpg --dearmor is applied)
#   keyfile  — destination for the dearmoured key (under /etc/apt/keyrings/)
#   deb-line — full deb line referencing signed-by=<keyfile>
#
# The function is idempotent: if the .list file already exists it prints
# "already configured" and returns immediately without touching the key or repo.
# ──────────────────────────────────────────────────────────────────────────────
add_repo() {
    local name="$1" keyurl="$2" keyfile="$3" repoline="$4"
    local listfile="/etc/apt/sources.list.d/${name}.list"

    if [[ -f "$listfile" ]]; then
        skip "APT repo: $name"
        return 0
    fi

    info "Adding APT repo: $name"
    if $DRY_RUN; then
        note "[dry-run] would add: $listfile"
        return 0
    fi

    sudo mkdir -p /etc/apt/keyrings
    # Download and dearmour the signing key
    curl -fsSL "$keyurl" 2>/dev/null \
        | sudo gpg --dearmor -o "$keyfile" \
        || { warn "Failed to fetch GPG key for $name — skipping this repo."; return 1; }
    sudo chmod 644 "$keyfile"
    # Write the deb line into the sources list
    echo "$repoline" | sudo tee "$listfile" > /dev/null
    ok "APT repo: $name"
}

# ──────────────────────────────────────────────────────────────────────────────
# Snap installer helper
#   snap_install  <snap-name>  <display-name>  [snap-flags]
# ──────────────────────────────────────────────────────────────────────────────
snap_install() {
    local pkg="$1" display="${2:-$1}" flags="${3:-}"
    if is_snap "$pkg"; then
        skip "$display (snap)"
        return 0
    fi
    info "Installing snap: $display"
    if $DRY_RUN; then
        note "[dry-run] snap install $pkg $flags"
        return 0
    fi
    # shellcheck disable=SC2086  (flags is intentionally word-split here)
    sudo snap install "$pkg" $flags 2>&1 | tee -a "$LOG_FILE" \
        && ok "$display" \
        || warn "$display snap install failed"
}

# ──────────────────────────────────────────────────────────────────────────────
# Download and install a .deb from a URL
#   deb_url  <display-name>  <url>
# ──────────────────────────────────────────────────────────────────────────────
deb_url() {
    local display="$1" url="$2"
    local tmp="${TMP_DIR}/${display// /_}.deb"
    info "Downloading $display…"
    if $DRY_RUN; then
        note "[dry-run] would download $url → install via apt"
        return 0
    fi
    curl -fsSL "$url" -o "$tmp" \
        || { warn "Download failed: $display ($url)"; return 1; }
    sudo apt-get install -y "$tmp" 2>&1 | tee -a "$LOG_FILE" \
        && ok "$display installed" \
        || warn "$display: deb install failed"
    rm -f "$tmp"
}

# ──────────────────────────────────────────────────────────────────────────────
# Resolve the download URL for the latest GitHub release asset
#   github_asset_url  <org/repo>  <grep-pattern>
# Returns the first URL matching the pattern, or empty string on failure.
# ──────────────────────────────────────────────────────────────────────────────
github_asset_url() {
    curl -fsSL "https://api.github.com/repos/$1/releases/latest" 2>/dev/null \
      | grep -oP '"browser_download_url"\s*:\s*"\K[^"]+' \
      | grep -iP "$2" \
      | head -1
}

# ──────────────────────────────────────────────────────────────────────────────
# Install an AppImage, create symlink in ~/.local/bin, write a .desktop entry
#   appimage_install  <display-name>  <url>  <cmd-symlink-name>
# ──────────────────────────────────────────────────────────────────────────────
appimage_install() {
    local display="$1" url="$2" cmd="$3"
    local apps="${HOME}/Applications"
    local dest="${apps}/${cmd}.AppImage"

    if [[ -f "$dest" ]]; then
        skip "$display (AppImage)"
        return 0
    fi
    info "Downloading $display AppImage…"
    if $DRY_RUN; then
        note "[dry-run] would download $url → $dest"
        return 0
    fi
    mkdir -p "$apps" "${HOME}/.local/bin"
    curl -fsSL "$url" -o "$dest" \
        || { warn "Failed to download $display"; return 1; }
    chmod +x "$dest"
    # Symlink so the command is available as `$cmd` on PATH
    ln -sf "$dest" "${HOME}/.local/bin/${cmd}"
    # Ensure ~/.local/bin is in PATH for future shells
    if ! grep -q '\.local/bin' "${HOME}/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "${HOME}/.bashrc"
    fi
    ok "$display → ~/.local/bin/$cmd"
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 0 — Banner & pre-flight
# ══════════════════════════════════════════════════════════════════════════════
print_banner() {
    printf "\n${C_BOLD}${C_STEP}"
    echo   "  ╔══════════════════════════════════════════════════════════════════╗"
    echo   "  ║  🚀  IDRM — Full DevOps Stack Installer                        ║"
    echo   "  ║      Ubuntu 22.04 / 24.04 LTS  ·  Full-stack + DSML           ║"
    echo   "  ╚══════════════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"
    printf "  ${C_DIM}Host :${C_RST} %s  |  ${C_DIM}User :${C_RST} %s\n" "$(hostname)" "$(whoami)"
    printf "  ${C_DIM}Date :${C_RST} %s\n"   "$(date '+%Y-%m-%d %H:%M:%S')"
    printf "  ${C_DIM}Log  :${C_RST} %s\n\n" "$LOG_FILE"
    $DRY_RUN       && printf "  ${C_WARN}DRY-RUN mode — nothing will be installed${C_RST}\n"
    $SKIP_OPTIONAL && printf "  ${C_DIM}--skip-optional active (Wine / multimedia / GNOME apps skipped)${C_RST}\n"
    echo ""
}

pre_flight() {
    step "PRE-FLIGHT — Checking requirements"

    # Must not be run as root (the script calls sudo internally)
    [[ "$(id -u)" -eq 0 ]] && die \
        "Do not run as root. Run as your normal user; sudo is called internally."

    # sudo must be available and authorised
    sudo -v || die "sudo access required — add your user to the sudoers group."
    ok "sudo access confirmed"

    # Ubuntu version detection
    UBUNTU_VERSION=$(lsb_release -rs 2>/dev/null || echo "unknown")
    UBUNTU_CODENAME=$(lsb_release -cs 2>/dev/null || echo "jammy")
    case "$UBUNTU_VERSION" in
        22.04) ok "Ubuntu $UBUNTU_VERSION LTS (${UBUNTU_CODENAME}) — supported" ;;
        24.04) ok "Ubuntu $UBUNTU_VERSION LTS (${UBUNTU_CODENAME}) — supported" ;;
        *)     warn "Ubuntu $UBUNTU_VERSION is untested — continuing at your own risk." ;;
    esac

    # Internet connectivity (try two hosts in case one is down)
    if curl -fsSL --max-time 6 https://deb.debian.org > /dev/null 2>&1 \
    || curl -fsSL --max-time 6 https://pypi.org          > /dev/null 2>&1; then
        ok "Internet connection confirmed"
    else
        warn "Could not reach external mirrors — some installs may fail."
    fi

    # Initialise the log file (overwrite any previous run's log)
    {
        echo "═══════════════════════════════════════════════════════════════"
        echo " IDRM DevOps Stack — Installation Log"
        echo " Started      : $(date)"
        echo " Host / User  : $(hostname) / $(whoami)"
        echo " OS           : Ubuntu $UBUNTU_VERSION ($UBUNTU_CODENAME)"
        echo " Dry-run      : $DRY_RUN"
        echo " Skip-optional: $SKIP_OPTIONAL"
        echo "═══════════════════════════════════════════════════════════════"
    } > "$LOG_FILE"
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — Third-party APT repositories
#  All repos are added FIRST, then a single `apt-get update` runs.
#  This is more efficient than updating after each repo.
# ══════════════════════════════════════════════════════════════════════════════
setup_repos() {
    step "PHASE 1/10 — Third-party APT repositories"

    # Bootstrap: install the tools needed to add repos if missing
    # (curl, gpg, and lsb-release might not be on a minimal Ubuntu install)
    if ! is_bin gpg || ! is_bin curl || ! is_deb ca-certificates; then
        info "Installing repo prerequisites (curl, gpg, ca-certificates)…"
        sudo apt-get update -qq 2>&1 | tee -a "$LOG_FILE"
        sudo apt-get install -y curl wget gpg ca-certificates lsb-release \
            software-properties-common apt-transport-https 2>&1 | tee -a "$LOG_FILE"
    fi
    sudo mkdir -p /etc/apt/keyrings

    # ── 1. PostgreSQL PGDG (official PostgreSQL APT repo) ────────────────────
    # Required for postgresql-16, postgresql-16-postgis-3, postgresql-contrib-16
    add_repo "pgdg" \
        "https://www.postgresql.org/media/keys/ACCC4CF8.asc" \
        "/etc/apt/keyrings/pgdg.gpg" \
        "deb [signed-by=/etc/apt/keyrings/pgdg.gpg] https://apt.postgresql.org/pub/repos/apt ${UBUNTU_CODENAME}-pgdg main"

    # ── 2. VSCodium (privacy-first VS Code build, open-source) ───────────────
    add_repo "vscodium" \
        "https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg" \
        "/etc/apt/keyrings/vscodium.gpg" \
        "deb [signed-by=/etc/apt/keyrings/vscodium.gpg] https://download.vscodium.com/debs vscodium main"

    # ── 3. Google Chrome ─────────────────────────────────────────────────────
    add_repo "google-chrome" \
        "https://dl.google.com/linux/linux_signing_key.pub" \
        "/etc/apt/keyrings/google-chrome.gpg" \
        "deb [arch=amd64 signed-by=/etc/apt/keyrings/google-chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main"

    # ── 4. Docker CE (engine + compose plugin) ───────────────────────────────
    add_repo "docker" \
        "https://download.docker.com/linux/ubuntu/gpg" \
        "/etc/apt/keyrings/docker.gpg" \
        "deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${UBUNTU_CODENAME} stable"

    # ── 5. Grafana OSS (monitoring dashboards) ───────────────────────────────
    add_repo "grafana" \
        "https://apt.grafana.com/gpg.key" \
        "/etc/apt/keyrings/grafana.gpg" \
        "deb [signed-by=/etc/apt/keyrings/grafana.gpg] https://apt.grafana.com stable main"

    # ── 6. Elasticsearch (AGPL — returned to open source Sep 2024) ───────────
    add_repo "elasticsearch" \
        "https://artifacts.elastic.co/GPG-KEY-elasticsearch" \
        "/etc/apt/keyrings/elasticsearch.gpg" \
        "deb [signed-by=/etc/apt/keyrings/elasticsearch.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main"

    # ── 7. pgAdmin 4 (optional PostgreSQL GUI) ───────────────────────────────
    add_repo "pgadmin4" \
        "https://www.pgadmin.org/static/packages_pgadmin_org.pub" \
        "/etc/apt/keyrings/pgadmin.gpg" \
        "deb [signed-by=/etc/apt/keyrings/pgadmin.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/${UBUNTU_CODENAME} pgadmin4 main"

    # ── 8. WineHQ Stable (Windows compatibility layer — requires i386) ────────
    # WineHQ needs i386 (32-bit) arch enabled to install 32-bit Windows libs.
    if ! dpkg --print-foreign-architectures 2>/dev/null | grep -q i386; then
        info "Enabling i386 architecture (required by WineHQ)…"
        $DRY_RUN || sudo dpkg --add-architecture i386
    fi
    add_repo "winehq" \
        "https://dl.winehq.org/wine-builds/winehq.key" \
        "/etc/apt/keyrings/winehq.gpg" \
        "deb [arch=amd64,i386 signed-by=/etc/apt/keyrings/winehq.gpg] https://dl.winehq.org/wine-builds/ubuntu/ ${UBUNTU_CODENAME} main"

    # ── 9. OBS Studio PPA (latest stable, beyond what Ubuntu ships) ───────────
    if ls /etc/apt/sources.list.d/obsproject* 2>/dev/null | head -1 &>/dev/null; then
        skip "OBS Studio PPA"
    else
        info "Adding OBS Studio PPA…"
        $DRY_RUN || sudo add-apt-repository -y ppa:obsproject/obs-studio \
            2>&1 | tee -a "$LOG_FILE" || true
    fi

    # ── Single apt update (all repos added above) ────────────────────────────
    info "Running apt-get update (all repos now configured)…"
    if ! $DRY_RUN; then
        sudo apt-get update -y 2>&1 | tee -a "$LOG_FILE" \
            && ok "Package index refreshed" \
            || warn "apt-get update had errors — some repos may be unreachable"
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — APT package installation (all batched by category)
# ══════════════════════════════════════════════════════════════════════════════
install_apt_packages() {
    step "PHASE 2/10 — APT packages"

    # ── 2a. Core system essentials ──────────────────────────────────────────
    info "→ System essentials"
    for pkg in \
        build-essential software-properties-common apt-transport-https \
        ca-certificates curl wget git gnupg lsb-release \
        unzip zip make cmake vim tmux net-tools dnsutils \
        htop glances jq httpie libnotify-bin \
        openssh-server openssh-client; do
        apt_queue "$pkg"
    done
    apt_flush "System essentials"

    # ── 2b. Python build dependencies ───────────────────────────────────────
    # These C library headers are needed when conda/pip compiles Python
    # packages from source rather than using pre-built binary wheels.
    info "→ Python build deps (C library headers)"
    for pkg in \
        python3-dev \
        libssl-dev libffi-dev libbz2-dev libreadline-dev libsqlite3-dev \
        libncurses5-dev libncursesw5-dev xz-utils tk-dev \
        libxml2-dev libxmlsec1-dev liblzma-dev; do
        apt_queue "$pkg"
    done
    apt_flush "Python build deps"

    # ── 2c. Vim language bindings + search tools ─────────────────────────────
    info "→ Vim language support + search tools"
    for pkg in ruby-dev libperl-dev liblua5.1-dev libluajit-5.1-dev luajit \
               idutils ripgrep; do
        apt_queue "$pkg"
    done
    apt_flush "Vim + search tools"

    # ── 2d. Java 21 ──────────────────────────────────────────────────────────
    # Ubuntu 22.04's default-jdk installs Java 11 — NOT 21.
    # We install openjdk-21 explicitly and set the active version via update-java-alternatives.
    info "→ Java 21 (project requires ≥ 21)"
    local _need_java=true
    if is_bin java; then
        local _jver; _jver=$(java --version 2>&1 | grep -oP '(?<=version ")\d+|\b\d+\b' | head -1)
        if [[ -n "$_jver" ]] && (( _jver >= 21 )); then
            skip "Java (v${_jver} ≥ 21)"
            _need_java=false
        else
            warn "Java ${_jver} found but < 21 — upgrading to openjdk-21"
        fi
    fi
    if $_need_java; then
        apt_queue openjdk-21-jdk "Java 21 JDK"
        apt_queue openjdk-21-jre "Java 21 JRE"
    fi
    apt_flush "Java 21"
    # After install, make Java 21 the default if multiple versions present
    if is_bin update-java-alternatives && ! $DRY_RUN; then
        sudo update-java-alternatives --set java-1.21.0-openjdk-amd64 2>/dev/null || true
    fi

    # ── 2e. PostgreSQL 16 + PostGIS 3 ───────────────────────────────────────
    # CRITICAL for IDRM: the entire geospatial feature set depends on PostGIS.
    # postgresql-16-postgis-3         = the PostGIS extension binary
    # postgresql-16-postgis-3-scripts = SQL upgrade/loader scripts
    # postgresql-contrib-16           = extra modules (pg_stat_statements, pg_trgm)
    # postgresql-server-dev-16        = C headers for building PG extensions
    info "→ PostgreSQL 16 + PostGIS 3 (IDRM core dependency)"
    for pkg in \
        postgresql-16 postgresql-contrib-16 postgresql-server-dev-16 \
        postgresql-16-postgis-3 postgresql-16-postgis-3-scripts; do
        apt_queue "$pkg"
    done
    apt_flush "PostgreSQL + PostGIS"

    # ── 2f. Redis ────────────────────────────────────────────────────────────
    # redis-tools installs redis-cli (used by setup-prerequisites.sh to verify Redis)
    info "→ Redis (cache · sessions · rate limiting · pub/sub)"
    apt_queue redis-server "Redis server"
    apt_queue redis-tools  "Redis CLI tools (redis-cli)"
    apt_flush "Redis"

    # ── 2g. NGINX ────────────────────────────────────────────────────────────
    info "→ NGINX (reverse proxy / API gateway)"
    apt_queue nginx
    apt_flush "NGINX"

    # ── 2h. VSCodium ─────────────────────────────────────────────────────────
    # Privacy-first VS Code build: no Microsoft telemetry, Open VSX extensions.
    info "→ VSCodium (privacy-first VS Code build)"
    apt_queue codium "VSCodium"
    apt_flush "VSCodium"

    # ── 2i. Google Chrome ────────────────────────────────────────────────────
    # Used for: Figma web, Google Keep PWA, and general testing
    info "→ Google Chrome"
    apt_queue google-chrome-stable "Google Chrome"
    apt_flush "Google Chrome"

    # ── 2j. Docker Engine + Compose v2 plugin ─────────────────────────────────
    # Docker Desktop is covered separately in the binary phase (optional).
    info "→ Docker Engine + Compose plugin"
    for pkg in \
        docker-ce docker-ce-cli containerd.io \
        docker-buildx-plugin docker-compose-plugin; do
        apt_queue "$pkg"
    done
    apt_flush "Docker Engine"

    # ── 2k. Grafana OSS ──────────────────────────────────────────────────────
    info "→ Grafana OSS (monitoring dashboards)"
    apt_queue grafana "Grafana OSS"
    apt_flush "Grafana"

    # ── 2l. Elasticsearch ────────────────────────────────────────────────────
    # Returned to open-source (AGPL-3) in September 2024.
    info "→ Elasticsearch (full-text search + log aggregation)"
    apt_queue elasticsearch
    apt_flush "Elasticsearch"

    # ── 2m. pgAdmin 4 ────────────────────────────────────────────────────────
    info "→ pgAdmin 4 (PostgreSQL web GUI — optional)"
    apt_queue pgadmin4-desktop "pgAdmin 4"
    apt_flush "pgAdmin 4"

    # ── 2n. System tools ─────────────────────────────────────────────────────
    info "→ System utilities (Tilix, Remmina, virt-manager, winetricks)"
    for pkg in tilix remmina virt-manager winetricks; do
        apt_queue "$pkg"
    done
    apt_flush "System utilities"

    # ── 2o. WineHQ Stable ────────────────────────────────────────────────────
    if $SKIP_OPTIONAL; then
        note "Skipping WineHQ (--skip-optional)"
    else
        if confirm "Install WineHQ Stable (Windows app compatibility layer)?"; then
            info "→ WineHQ Stable"
            apt_queue winehq-stable "WineHQ Stable"
            apt_flush "WineHQ"
        fi
    fi

    # ── 2p. Multimedia: VLC, GIMP, OBS Studio, Caffeine ─────────────────────
    if $SKIP_OPTIONAL; then
        note "Skipping multimedia tools (--skip-optional)"
    else
        if confirm "Install multimedia tools? (VLC, GIMP, OBS Studio, Caffeine)"; then
            info "→ Multimedia tools"
            for pkg in vlc gimp obs-studio caffeine; do
                apt_queue "$pkg"
            done
            apt_flush "Multimedia tools"
        fi
    fi

    # ── 2q. GNOME productivity apps ──────────────────────────────────────────
    if $SKIP_OPTIONAL; then
        note "Skipping GNOME apps (--skip-optional)"
    else
        info "→ GNOME apps (calendar, text editor, sudoku, todo)"
        for pkg in gnome-text-editor gnome-calendar gnome-sudoku gnome-todo; do
            apt_queue "$pkg"
        done
        apt_flush "GNOME apps"
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — Snap packages
# ══════════════════════════════════════════════════════════════════════════════
install_snaps() {
    step "PHASE 3/10 — Snap packages"

    if ! is_bin snap; then
        warn "snapd not found — skipping all snap installs."
        return
    fi
    # Ensure snapd daemon is running and up to date
    sudo systemctl start snapd 2>/dev/null || true
    sudo snap install snapd 2>/dev/null || true

    # API testing
    snap_install "postman"                 "Postman"

    # PostgreSQL GUI
    snap_install "postbird"                "Postbird (PostgreSQL GUI)"

    # OpenStreetMap editor (Java-based, snap is the cleanest install)
    snap_install "josm"                    "JOSM (OpenStreetMap editor)"

    # JetBrains IDEs — all free for non-commercial use (since Oct 2024).
    # --classic required: these IDEs need system-level filesystem access.
    snap_install "webstorm"                "WebStorm (JS/TS IDE)"      "--classic"
    snap_install "intellij-idea-community" "IntelliJ IDEA Community"   "--classic"
    snap_install "pycharm-community"       "PyCharm Community"         "--classic"

    # Figma — no official Linux app; this is an unofficial Electron wrapper.
    snap_install "figma-linux"             "Figma (unofficial wrapper)"

    # Prometheus — snap is the simplest install path
    snap_install "prometheus"              "Prometheus (monitoring)"
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 4 — Binary & deb installers
# ══════════════════════════════════════════════════════════════════════════════

# ── Miniconda (Python 3.11 environment manager) ───────────────────────────────
_install_miniconda() {
    if is_bin conda || [[ -d "${HOME}/miniconda3" ]]; then
        skip "Miniconda"; return
    fi
    info "Installing Miniconda (Python 3.11 environment manager)…"
    local mc_url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
    local mc_sh="${TMP_DIR}/miniconda.sh"
    if $DRY_RUN; then
        note "[dry-run] would download Miniconda installer and run -b -p ~/miniconda3"
        return 0
    fi
    curl -fsSL "$mc_url" -o "$mc_sh" \
        || { warn "Failed to download Miniconda"; return 1; }
    bash "$mc_sh" -b -p "${HOME}/miniconda3" 2>&1 | tee -a "$LOG_FILE"
    rm -f "$mc_sh"
    # Make conda available in the current shell session
    export PATH="${HOME}/miniconda3/bin:$PATH"
    # Persist to .bashrc for all future shell sessions (idempotent check)
    if ! grep -q "miniconda3/bin" "${HOME}/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/miniconda3/bin:$PATH"' >> "${HOME}/.bashrc"
    fi
    "${HOME}/miniconda3/bin/conda" init bash 2>&1 | tee -a "$LOG_FILE"
    ok "Miniconda installed → ~/miniconda3"
}

# ── Bun (JavaScript / TypeScript runtime) ────────────────────────────────────
_install_bun() {
    if is_bin bun; then
        skip "Bun ($(bun --version 2>/dev/null))"; return
    fi
    info "Installing Bun (JS/TS runtime — replaces Node for frontend + gateway)…"
    if $DRY_RUN; then
        note "[dry-run] would run: curl -fsSL https://bun.sh/install | bash"
        return 0
    fi
    curl -fsSL https://bun.sh/install | bash 2>&1 | tee -a "$LOG_FILE"
    export BUN_INSTALL="${HOME}/.bun"
    export PATH="${BUN_INSTALL}/bin:$PATH"
    if ! grep -q ".bun/bin" "${HOME}/.bashrc" 2>/dev/null; then
        { echo 'export BUN_INSTALL="$HOME/.bun"'
          echo 'export PATH="$BUN_INSTALL/bin:$PATH"'; } >> "${HOME}/.bashrc"
    fi
    ok "Bun installed"
}

# ── nvm + Node.js LTS (needed only for Claude Code) ──────────────────────────
_install_nvm_node() {
    if [[ -d "${HOME}/.nvm" ]]; then
        skip "nvm"
    else
        info "Installing nvm (Node Version Manager — required for Claude Code)…"
        if $DRY_RUN; then
            note "[dry-run] would install nvm + Node.js LTS"
        else
            curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh \
                | bash 2>&1 | tee -a "$LOG_FILE"
            ok "nvm installed"
        fi
    fi
    # Source nvm so it is available in the current shell (nvm modifies PATH)
    export NVM_DIR="${HOME}/.nvm"
    # shellcheck source=/dev/null
    [[ -s "${NVM_DIR}/nvm.sh" ]] && source "${NVM_DIR}/nvm.sh"

    if is_bin node; then
        skip "Node.js ($(node --version 2>/dev/null))"
    else
        info "Installing Node.js LTS via nvm…"
        $DRY_RUN || { nvm install --lts 2>&1 | tee -a "$LOG_FILE"
                      nvm use --lts 2>&1 | tee -a "$LOG_FILE"; }
        ok "Node.js LTS installed"
    fi
}

# ── DBeaver CE (database GUI) ─────────────────────────────────────────────────
_install_dbeaver() {
    # Already installed as deb or snap?
    if is_bin dbeaver || is_deb dbeaver-ce || is_snap dbeaver-ce; then
        skip "DBeaver CE"; return
    fi
    # dbeaver.io provides a stable "latest" URL — no version guessing needed
    deb_url "DBeaver CE" "https://dbeaver.io/files/dbeaver-ce_latest_amd64.deb"
}

# ── MongoDB Compass (MongoDB GUI) ─────────────────────────────────────────────
_install_mongodb_compass() {
    if is_deb mongodb-compass || is_bin mongodb-compass; then
        skip "MongoDB Compass"; return
    fi
    local url; url=$(github_asset_url "mongodb-js/compass" "mongodb-compass_[0-9].*amd64\.deb")
    if [[ -z "$url" ]]; then
        warn "Cannot resolve MongoDB Compass URL — install from mongodb.com/compass"
        return 1
    fi
    deb_url "MongoDB Compass" "$url"
}

# ── Cursor (AI-first code editor, VS Code fork) ───────────────────────────────
_install_cursor() {
    if is_bin cursor \
       || ls "${HOME}/Applications/cursor.AppImage" 2>/dev/null | head -1 &>/dev/null; then
        skip "Cursor"; return
    fi
    # Cursor publishes a stable AppImage URL (no version in the path)
    appimage_install "Cursor" \
        "https://downloader.cursor.sh/linux/appImage/x64" \
        "cursor"
}

# ── Insomnia (API testing) ────────────────────────────────────────────────────
_install_insomnia() {
    if is_deb insomnia || is_bin insomnia; then
        skip "Insomnia"; return
    fi
    local url; url=$(github_asset_url "Kong/insomnia" "Insomnia\.Core.*\.deb")
    if [[ -z "$url" ]]; then
        warn "Cannot resolve Insomnia URL — install from insomnia.rest"
        return 1
    fi
    deb_url "Insomnia" "$url"
    note "Insomnia requires an account login since 2023"
}

# ── Bruno (privacy-clean API client) ─────────────────────────────────────────
_install_bruno() {
    if is_bin bruno || is_deb bruno; then
        skip "Bruno"; return
    fi
    local url; url=$(github_asset_url "usebruno/bruno" "bruno.*amd64.*\.deb")
    if [[ -z "$url" ]]; then
        warn "Cannot resolve Bruno URL — install from usebruno.com"
        return 1
    fi
    deb_url "Bruno" "$url"
}

# ── ksnip (screenshot tool — 'Ksnop' in original list is a typo) ─────────────
_install_ksnip() {
    if is_bin ksnip || is_deb ksnip; then
        skip "ksnip (screenshot)"; return
    fi
    # Try deb first; fall back to AppImage
    local deb_url_val; deb_url_val=$(github_asset_url "ksnip/ksnip" "ksnip.*amd64\.deb")
    if [[ -n "$deb_url_val" ]]; then
        deb_url "ksnip" "$deb_url_val"
    else
        local img_url; img_url=$(github_asset_url "ksnip/ksnip" "ksnip.*x86_64\.AppImage")
        if [[ -n "$img_url" ]]; then
            appimage_install "ksnip" "$img_url" "ksnip"
        else
            warn "Cannot resolve ksnip download URL — install from github.com/ksnip/ksnip"
        fi
    fi
}

install_binaries() {
    step "PHASE 4/10 — Binary & deb installers"
    _install_miniconda
    _install_bun
    _install_nvm_node
    _install_dbeaver
    _install_mongodb_compass
    _install_cursor
    _install_insomnia
    _install_bruno
    _install_ksnip
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 5 — Service setup (enable + start all systemd services)
# ══════════════════════════════════════════════════════════════════════════════
setup_services() {
    step "PHASE 5/10 — Enabling and starting services"

    local services=(
        "postgresql"      "PostgreSQL database"
        "redis-server"    "Redis cache"
        "nginx"           "NGINX web server"
        "docker"          "Docker daemon"
        "grafana-server"  "Grafana OSS"
        "elasticsearch"   "Elasticsearch"
    )

    local i=0
    while [[ $i -lt ${#services[@]} ]]; do
        local svc="${services[$i]}" label="${services[$((i+1))]}"
        i=$(( i + 2 ))

        if ! systemctl list-unit-files "${svc}.service" 2>/dev/null \
             | grep -q "${svc}.service"; then
            note "$label — service unit not installed yet (skip)"
            continue
        fi

        if $DRY_RUN; then
            note "[dry-run] would enable + start $svc"
            continue
        fi

        sudo systemctl enable "$svc"  2>/dev/null || true
        sudo systemctl start  "$svc"  2>/dev/null || true
        local st; st=$(systemctl is-active "$svc" 2>/dev/null || echo "unknown")
        if [[ "$st" == "active" ]]; then
            ok "$label — running"
        else
            warn "$label — failed to start (status: $st); check: journalctl -u $svc"
        fi
    done

    # Docker group: add the current user so docker can be used without sudo
    if is_bin docker; then
        if groups "$(whoami)" | grep -q docker; then
            skip "Docker group (user already in group)"
        else
            info "Adding $(whoami) to the docker group…"
            $DRY_RUN || sudo usermod -aG docker "$(whoami)"
            ok "Docker group — effective after next login"
        fi
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 6 — Conda environment (idrm-mvp)
# ══════════════════════════════════════════════════════════════════════════════
setup_conda_env() {
    step "PHASE 6/10 — Conda environment (idrm-mvp)"

    # Miniconda may have just been installed; expose it to the current shell
    [[ -f "${HOME}/miniconda3/bin/conda" ]] \
        && export PATH="${HOME}/miniconda3/bin:$PATH"

    if ! is_bin conda; then
        warn "conda not on PATH — cannot create idrm-mvp env. Run: source ~/.bashrc"
        return
    fi

    local env_yml="${REPO_ROOT}/environment.yml"
    if [[ ! -f "$env_yml" ]]; then
        warn "environment.yml not found at ${env_yml}"
        note "Copy the file from the project root and re-run this script."
        return
    fi

    if conda env list 2>/dev/null | grep -qE "^[* ]*idrm-mvp[[:space:]]"; then
        skip "idrm-mvp conda environment"
        info "To update packages: conda env update -f environment.yml --prune"
    else
        info "Creating idrm-mvp conda environment (Python 3.11 + all deps)…"
        if $DRY_RUN; then
            note "[dry-run] would run: conda env create -f $env_yml"
        else
            conda env create -f "$env_yml" 2>&1 | tee -a "$LOG_FILE" \
                && ok "idrm-mvp environment created" \
                || warn "idrm-mvp creation failed — check $LOG_FILE"
        fi
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 7 — Docker-based services (Metabase, Loki)
# ══════════════════════════════════════════════════════════════════════════════
install_docker_services() {
    step "PHASE 7/10 — Docker-based services"

    if ! is_bin docker; then
        warn "Docker not found — skipping Metabase and Loki."
        return
    fi

    # ── Metabase (Business Intelligence dashboard) ───────────────────────────
    if docker ps -a 2>/dev/null | grep -q "metabase"; then
        skip "Metabase container"
    else
        info "Starting Metabase (BI dashboard — port 3000)…"
        if $DRY_RUN; then
            note "[dry-run] docker run metabase/metabase → port 3000"
        else
            docker pull metabase/metabase 2>&1 | tee -a "$LOG_FILE"
            docker run -d --name metabase \
                --restart unless-stopped \
                -p 3000:3000 \
                -v metabase-data:/metabase-data \
                metabase/metabase 2>&1 | tee -a "$LOG_FILE" \
                && ok "Metabase started → http://localhost:3000" \
                || warn "Metabase failed to start — check: docker logs metabase"
        fi
    fi

    # ── Loki (Grafana log aggregation) ───────────────────────────────────────
    if docker ps -a 2>/dev/null | grep -q "^/loki$\|[ /]loki$"; then
        skip "Loki container"
    else
        info "Starting Loki (log aggregation — port 3100)…"
        if $DRY_RUN; then
            note "[dry-run] docker run grafana/loki → port 3100"
        else
            docker pull grafana/loki 2>&1 | tee -a "$LOG_FILE"
            docker run -d --name loki \
                --restart unless-stopped \
                -p 3100:3100 \
                grafana/loki 2>&1 | tee -a "$LOG_FILE" \
                && ok "Loki started → http://localhost:3100" \
                || warn "Loki failed to start — check: docker logs loki"
        fi
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 8 — VSCodium / VS Code extensions (privacy-screened set)
# ══════════════════════════════════════════════════════════════════════════════
install_extensions() {
    step "PHASE 8/10 — Editor extensions"

    # Use whichever editor is installed; VSCodium is preferred
    local editor_cmd=""
    if is_bin codium; then
        editor_cmd="codium"
    elif is_bin code; then
        editor_cmd="code"
    else
        warn "Neither codium nor code found — skipping extension installs."
        return
    fi
    info "Using: $editor_cmd"

    # The project's privacy-screened extension set (matches check-devops-stack.sh)
    local extensions=(
        "ms-python.python"                  # Python language support
        "ms-python.vscode-pylance"          # Python type checking / IntelliSense
        "ms-python.black-formatter"         # Black formatter (format on save)
        "bradlc.vscode-tailwindcss"         # Tailwind CSS IntelliSense
        "oven.bun-vscode"                   # Bun runtime support
        "dbaeumer.vscode-eslint"            # ESLint (runs local install)
        "esbenp.prettier-vscode"            # Prettier (runs local install)
        "mhutchie.git-graph"               # Git history visualisation (no telemetry)
        "usernamehw.errorlens"              # Inline error / warning display
        "yoavbls.pretty-ts-errors"          # Human-readable TypeScript errors
        "dsznajder.es7-react-js-snippets"   # React/JSX snippets
    )

    # Determine the extensions directory for the installed editor
    local ext_dir="${HOME}/.vscode-oss/extensions"
    [[ "$editor_cmd" == "code" ]] && ext_dir="${HOME}/.vscode/extensions"

    for ext in "${extensions[@]}"; do
        if [[ -d "$ext_dir" ]] && ls "$ext_dir" 2>/dev/null | grep -qi "^${ext}-"; then
            skip "ext: $ext"
        else
            info "Installing: $ext"
            if $DRY_RUN; then
                note "[dry-run] $editor_cmd --install-extension $ext"
            else
                "$editor_cmd" --install-extension "$ext" \
                    --force 2>&1 | tee -a "$LOG_FILE" \
                    && ok "ext: $ext" \
                    || warn "ext: $ext install failed"
            fi
        fi
    done
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 9 — Claude Code (via npm after nvm is loaded)
# ══════════════════════════════════════════════════════════════════════════════
install_claude_code() {
    step "PHASE 9/10 — Claude Code"

    # Load nvm so npm is on PATH (nvm was installed in Phase 4)
    export NVM_DIR="${HOME}/.nvm"
    # shellcheck source=/dev/null
    [[ -s "${NVM_DIR}/nvm.sh" ]] && source "${NVM_DIR}/nvm.sh"

    if is_bin claude; then
        skip "Claude Code ($(claude --version 2>/dev/null | head -1))"
        return
    fi
    if ! is_bin npm; then
        warn "npm not found — Claude Code requires Node.js (installed via nvm)."
        note "After sourcing ~/.bashrc, run: npm install -g @anthropic-ai/claude-code"
        return
    fi
    info "Installing Claude Code via npm…"
    if $DRY_RUN; then
        note "[dry-run] npm install -g @anthropic-ai/claude-code"
    else
        npm install -g @anthropic-ai/claude-code 2>&1 | tee -a "$LOG_FILE" \
            && ok "Claude Code installed" \
            || warn "Claude Code install failed — check $LOG_FILE"
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 10 — PostGIS SQL extension (enable inside idrm_db)
# ══════════════════════════════════════════════════════════════════════════════
setup_postgis_extension() {
    step "PHASE 10/10 — PostGIS SQL extension in idrm_db"
    # Installing the apt package (Phase 2) is not enough.
    # The extension must also be enabled inside the actual database.
    # This is idempotent: CREATE EXTENSION IF NOT EXISTS never errors on repeat.

    if ! is_bin psql; then
        warn "psql not found — skipping PostGIS extension setup."
        return
    fi
    if ! pg_isready -q 2>/dev/null; then
        warn "PostgreSQL is not running — skipping PostGIS extension setup."
        note "Start it: sudo systemctl start postgresql, then re-run this step."
        return
    fi

    # Check if PostGIS is already enabled
    local pg_ver
    pg_ver=$(sudo -u postgres psql -d idrm_db \
             -tAc "SELECT PostGIS_lib_version();" 2>/dev/null \
             | tr -d ' \n')

    if [[ -n "$pg_ver" ]]; then
        skip "PostGIS SQL extension in idrm_db (v${pg_ver})"
        return
    fi

    info "Enabling PostGIS extension in idrm_db…"
    if $DRY_RUN; then
        note "[dry-run] would CREATE EXTENSION postgis + postgis_topology in idrm_db"
        return
    fi

    # Create the database if it does not exist yet (idrm_db setup happens in
    # setup-development-monolith.sh, but we can create it here if needed)
    sudo -u postgres psql -c \
        "CREATE DATABASE idrm_db;" 2>/dev/null || true

    sudo -u postgres psql -d idrm_db \
        -c "CREATE EXTENSION IF NOT EXISTS postgis;" \
        -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;" \
        2>&1 | tee -a "$LOG_FILE" \
        && ok "PostGIS extension enabled in idrm_db" \
        || warn "PostGIS extension setup failed — run setup-development-monolith.sh"
}

# ══════════════════════════════════════════════════════════════════════════════
#  FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print_summary() {
    local end_ts; end_ts=$(date +%s)
    local elapsed=$(( end_ts - _START_TS ))
    local mins=$(( elapsed / 60 )) secs=$(( elapsed % 60 ))

    printf "\n${C_BOLD}${C_STEP}"
    echo   "  ╔══════════════════════════════════════════════════════════════════╗"
    echo   "  ║  📋  INSTALLATION SUMMARY                                        ║"
    echo   "  ╠══════════════════════════════════════════════════════════════════╣"
    printf "  ║  ${C_OK}✔${C_STEP}  Newly installed   : ${C_OK}%-5d${C_STEP}                                   ║\n" "$CNT_INSTALLED"
    printf "  ║  ${C_DIM}→${C_STEP}  Already present   : ${C_DIM}%-5d${C_STEP}                                   ║\n" "$CNT_SKIPPED"
    printf "  ║  ${C_WARN}⚠${C_STEP}  Failed / skipped  : ${C_WARN}%-5d${C_STEP}                                   ║\n" "$CNT_FAILED"
    printf "  ║     Time elapsed    : %dm %02ds%-32s║\n" "$mins" "$secs" ""
    echo   "  ╠══════════════════════════════════════════════════════════════════╣"
    printf "  ║  Log → %-60s║\n" "$LOG_FILE"
    echo   "  ╚══════════════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"

    [[ $CNT_FAILED -gt 0 ]] && printf \
        "  ${C_WARN}⚠  %d item(s) failed. Review: %s${C_RST}\n\n" "$CNT_FAILED" "$LOG_FILE"

    printf "${C_BOLD}  Next steps:${C_RST}\n"
    printf "  ${C_DIM}1.${C_RST}  Reload shell environment:  ${C_INFO}source ~/.bashrc${C_RST}\n"
    printf "  ${C_DIM}2.${C_RST}  Activate the conda env:    ${C_INFO}conda activate idrm-mvp${C_RST}\n"
    printf "  ${C_DIM}3.${C_RST}  Configure project (DB/env):${C_INFO}bash scripts/setup-development-monolith.sh${C_RST}\n"
    printf "  ${C_DIM}4.${C_RST}  Verify everything:         ${C_INFO}bash scripts/check-devops-stack.sh${C_RST}\n"
    printf "  ${C_DIM}5.${C_RST}  Docker group is effective after logout / login.\n"
    printf "\n  ${C_DIM}ℹ${C_RST}  Google Keep  — no native Linux app; use Chrome → ⋮ → Install\n"
    printf "  ${C_DIM}ℹ${C_RST}  Grok CLI     — no apt package; see github.com/nicowillis/grok\n\n"
}

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN — orchestrates all phases in the correct dependency order
# ══════════════════════════════════════════════════════════════════════════════
main() {
    print_banner

    # Phase 0: Checks — must pass before anything is installed
    pre_flight

    # Phase 1: Repos — add ALL third-party apt repos before running apt update
    setup_repos

    # Phase 2: APT — install all apt packages (batched per category)
    install_apt_packages

    # Phase 3: Snaps — install all snap packages
    install_snaps

    # Phase 4: Binaries — Miniconda, Bun, nvm, deb downloads, AppImages
    install_binaries

    # Phase 5: Services — enable + start systemd units, add user to docker group
    setup_services

    # Phase 6: Conda env — create idrm-mvp after Miniconda is guaranteed present
    setup_conda_env

    # Phase 7: Docker services — Metabase, Loki (requires Docker to be running)
    install_docker_services

    # Phase 8: IDE extensions — install after VSCodium is guaranteed present
    install_extensions

    # Phase 9: Claude Code — install after nvm + node are guaranteed present
    install_claude_code

    # Phase 10: PostGIS SQL extension — enable inside idrm_db
    setup_postgis_extension

    print_summary
}

main "$@"
