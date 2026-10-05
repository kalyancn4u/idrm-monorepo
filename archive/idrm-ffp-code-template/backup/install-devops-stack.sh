#!/usr/bin/env bash
# =============================================================================
# FILE    : scripts/install-devops-stack.sh
# PROJECT : IDRM — Full-stack + DSML DevOps Stack
#
# PURPOSE : Install the complete IDRM DevOps stack on Ubuntu 22.04 / 24.04.
#           IDEMPOTENT — every step checks before acting; re-running is safe
#           and only installs what is genuinely missing.
#
# ── THREE-PHASE DESIGN ───────────────────────────────────────────────────────
#   Phase 1 — Add all third-party APT repositories (signed-by keyring method)
#   Phase 2 — Single  apt-get update  (never called twice)
#   Phase 3 — Install packages, snaps, curl-based runtimes, conda env
#
# ── USAGE ────────────────────────────────────────────────────────────────────
#   bash scripts/install-devops-stack.sh [OPTIONS]
#
# OPTIONS :
#   -n, --dry-run   Show every action without executing anything
#   -y, --yes       Skip optional prompts (auto installs everything; good for CI)
#   -h, --help      Print this help text and exit
#
# ── REQUIRES ─────────────────────────────────────────────────────────────────
#   Ubuntu 22.04 LTS or 24.04 LTS (64-bit x86_64, x86)
#   sudo privileges  ·  run as a normal user (NOT as root)
#       — the script calls sudo internally where needed.
#         Running as root will cause it to exit immediately.
#   Internet connection
#
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
# ── OUTPUT ───────────────────────────────────────────────────────────────────
#   Coloured terminal log  +  ~/idrm-install.log
#
# ── SECURITY NOTES ───────────────────────────────────────────────────────────
#   All APT repos use the modern signed-by keyring method (no apt-key add).
#   No hardcoded passwords anywhere in this script.
# =============================================================================
#
# TODO: {{{
# NOTES   :
#   · NOT installed (no native Linux package exists):
#       Google Keep  — use Chrome → ⋮ → "Install Keep…" (PWA)
#       Grok CLI     — install manually from github.com/nicowillis/grok
#   · WineHQ adds i386 architecture (required for 32-bit Windows support).
#   · After the script finishes, run:  source ~/.bashrc
#     to pick up all new PATH entries (conda, bun, nvm).
#   · Docker group membership requires a logout/login to take effect.
# =============================================================================
# }}}
#
# Intentionally NO -e: a failed install of one tool must not abort the rest.
set -uo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── CLI flags ─────────────────────────────────────────────────────────────────
DRY=false
AUTO_YES=false
for _arg in "$@"; do
    case "$_arg" in
        -n|--dry-run) DRY=true ;;
        -y|--yes)     AUTO_YES=true ;;
        -h|--help)
            grep '^#' "$0" | grep -v '^#!/' | sed 's/^# \?//'; exit 0 ;;
    esac
done

# ── Colours ───────────────────────────────────────────────────────────────────
#   auto-disabled when stdout is redirected / not a TTY
# ──────────────────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_FRESH='\033[0;32m' C_SKIP='\033[2m' C_WARN='\033[1;33m'
    C_FAIL='\033[0;31m'  C_INFO='\033[0;36m' C_DRY='\033[0;35m'
    C_BOLD='\033[1m'     C_RST='\033[0m'
else
    C_FRESH='' C_SKIP='' C_WARN='' C_FAIL='' C_INFO='' C_DRY='' C_BOLD='' C_RST=''
fi

# ── Counters ──────────────────────────────────────────────────────────────────
_FRESH=0 _SKIPPED=0 _FAILED=0 _DRY_CT=0

# ── Log file ──────────────────────────────────────────────────────────────────
LOG_FILE="${HOME}/idrm-install.log"

# ── Print helpers ─────────────────────────────────────────────────────────────
fresh() { _FRESH=$((_FRESH+1));   printf "  ${C_FRESH}✔${C_RST}  %s\n" "$*"; echo "[installed] $*" >> "$LOG_FILE"; }
skip()  { _SKIPPED=$((_SKIPPED+1)); printf "  ${C_SKIP}⏭  %s${C_RST}\n" "$*"; echo "[skipped]   $*" >> "$LOG_FILE"; }
fail()  { _FAILED=$((_FAILED+1));  printf "  ${C_FAIL}✘${C_RST}  %s\n" "$*"; echo "[FAILED]    $*" >> "$LOG_FILE"; }
warn()  { printf "  ${C_WARN}⚠${C_RST}  %s\n" "$*"; echo "[warn]      $*" >> "$LOG_FILE"; }
info()  { printf "  ${C_INFO}ℹ${C_RST}  %s\n" "$*"; echo "[info]      $*" >> "$LOG_FILE"; }
note_dry() { _DRY_CT=$((_DRY_CT+1)); printf "  ${C_DRY}◌${C_RST}  [DRY-RUN] %s\n" "$*"; echo "[dry-run]   $*" >> "$LOG_FILE"; }
step()  { printf "\n  ${C_INFO}▶${C_RST}  ${C_BOLD}%s${C_RST}\n" "$*"; }

section() {
    printf "\n${C_BOLD}  ──────────────────────────────────────────────────────────────────────\n"
    printf   "   %s\n" "$1"
    printf   "  ──────────────────────────────────────────────────────────────────────${C_RST}\n\n"
    { echo ""; echo "[$1]"; } >> "$LOG_FILE"
}

confirm() {
    $AUTO_YES && return 0
    printf "\n  ${C_WARN}%s [y/N]${C_RST} " "$1"
    read -r -n1 _r; echo ""
    [[ "$_r" =~ ^[Yy]$ ]]
}

# ── Core install helpers ───────────────────────────────────────────────────────

# apt_pkg "Label" pkg [pkg2 ...]  — install only missing packages
apt_pkg() {
    local label="$1"; shift
    local missing=()
    for pkg in "$@"; do
        dpkg -l "$pkg" 2>/dev/null | grep -q '^ii' || missing+=("$pkg")
    done
    [[ ${#missing[@]} -eq 0 ]] && { skip "$label"; return 0; }
    if $DRY; then note_dry "apt-get install -y ${missing[*]}"; return 0; fi
    sudo apt-get install -y "${missing[@]}" >>"$LOG_FILE" 2>&1
    dpkg -l "${missing[0]}" 2>/dev/null | grep -q '^ii' \
        && fresh "$label  (new: ${missing[*]})" \
        || fail "$label — apt install failed  (see $LOG_FILE)"
}

# snap_pkg "Label" snap-name [snap flags ...]  — install snap only if missing
snap_pkg() {
    # Ensure snapd daemon is running and up to date
    # sudo systemctl start snapd 2>/dev/null || true
    # sudo snap install snapd 2>/dev/null || true

    local label="$1" snapname="$2"; shift 2
    local flags=("$@")
    command -v snap &>/dev/null || { fail "$label — snapd not available"; return; }
    snap list "$snapname" 2>/dev/null | grep -q "^${snapname}" \
        && { skip "$label"; return 0; }
    if $DRY; then note_dry "snap install $snapname ${flags[*]:-}"; return 0; fi
    sudo snap install "$snapname" "${flags[@]}" >>"$LOG_FILE" 2>&1
    snap list "$snapname" 2>/dev/null | grep -q "^${snapname}" \
        && fresh "$label" \
        || fail "$label — snap install failed  (see $LOG_FILE)"
}

# add_repo "Label" keyring key-url "source-line" list-file
# Adds APT repo via signed-by keyring; idempotent (skips if list-file exists).
add_repo() {
    local label="$1" keyring="$2" key_url="$3" source_line="$4" list_file="$5"
    [[ -f "$list_file" ]] && { skip "repo: $label"; return 0; }
    if $DRY; then note_dry "add_repo $label → $list_file"; return 0; fi
    curl -fsSL "$key_url" | sudo gpg --dearmor -o "$keyring" >>"$LOG_FILE" 2>&1 \
        || { fail "repo: $label — GPG key download failed"; return 1; }
    echo "$source_line" | sudo tee "$list_file" >>"$LOG_FILE"
    fresh "repo: $label"
}

# svc_enable service — enable + start a systemd service (idempotent)
svc_enable() {
    local svc="$1"
    systemctl list-unit-files "${svc}.service" 2>/dev/null \
        | grep -q "${svc}.service" || { warn "service $svc: unit not found — skip"; return; }
    $DRY && { note_dry "systemctl enable --now $svc"; return 0; }
    sudo systemctl enable --now "$svc" >>"$LOG_FILE" 2>&1 \
        && info "service $svc: enabled + started" \
        || warn  "service $svc: already running or enable returned non-zero"
}

# codium_ext "ext.id" — install VSCodium/VS Code extension if missing
codium_ext() {
    local ext_id="$1"
    local editor=""
    command -v codium &>/dev/null && editor="codium"
    [[ -z "$editor" ]] && command -v code &>/dev/null && editor="code"
    if [[ -z "$editor" ]]; then skip "ext: $ext_id  (editor not installed yet)"; return; fi
    for dir in "${HOME}/.vscode-oss/extensions" "${HOME}/.vscode/extensions"; do
        [[ -d "$dir" ]] && ls "$dir" 2>/dev/null | grep -qi "^${ext_id}-" \
            && { skip "ext: $ext_id"; return 0; }
    done
    $DRY && { note_dry "$editor --install-extension $ext_id"; return 0; }
    "$editor" --install-extension "$ext_id" >>"$LOG_FILE" 2>&1
    fresh "ext: $ext_id"
}

# ═════════════════════════════════════════════════════════════════════════════
# BANNER
# ═════════════════════════════════════════════════════════════════════════════
print_banner() {
    echo ""
    printf "${C_BOLD}${C_INFO}"
    echo   "  ╔══════════════════════════════════════════════════════════════════════╗"
    echo   "  ║  🚀  IDRM DevOps Stack Installer                                   ║"
    echo   "  ║      Full-stack + DSML  ·  Ubuntu 22.04 / 24.04 LTS              ║"
    echo   "  ╚══════════════════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"
    printf "  ${C_BOLD}Host${C_RST} : %s\n" "$(hostname)"
    printf "  ${C_BOLD}User${C_RST} : %s\n" "$(whoami)"
    printf "  ${C_BOLD}OS${C_RST}   : %s\n" "$(lsb_release -ds 2>/dev/null || uname -sr)"
    printf "  ${C_BOLD}Log${C_RST}  : %s\n" "$LOG_FILE"
    $DRY && printf "  ${C_DRY}Mode : DRY-RUN — no changes will be made${C_RST}\n"

    # Initialise the log file (overwrite any previous run's log)
    echo ""
    {
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo " IDRM DevOps Stack Installer"
        echo " Started  : $(date)"
        echo " Host     : $(hostname)  |  User: $(whoami)"
        echo " OS       : $(lsb_release -ds 2>/dev/null || uname -sr)"
        echo " Dry-run  : $DRY"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } > "$LOG_FILE"
}

# ═════════════════════════════════════════════════════════════════════════════
# PREFLIGHT
# ═════════════════════════════════════════════════════════════════════════════
pre_flight() {
    section "🔍  PREFLIGHT CHECKS"

    # Must be Ubuntu
    local os_id; os_id=$(. /etc/os-release 2>/dev/null && echo "$ID")
    if [[ "$os_id" != "ubuntu" ]]; then
        fail "OS is '$os_id' — this script requires Ubuntu 22.04 or 24.04"; exit 1
    fi
    info "OS: Ubuntu $(. /etc/os-release && echo "$VERSION_ID") ✔"

    # Must not be root
    if [[ "$(id -u)" -eq 0 ]]; then
        fail "Do not run as root. The script calls sudo internally."; exit 1
    fi
    info "Running as non-root user: $(whoami) ✔"

    # Warm up sudo once; keep it alive throughout the install
    if ! $DRY; then
        info "Verifying sudo access (password prompt may appear)..."
        sudo -v || { fail "sudo not available or password incorrect"; exit 1; }
        ( while true; do sudo -n true; sleep 50; done ) &
        _SUDO_KEEPALIVE=$!
        trap 'kill $_SUDO_KEEPALIVE 2>/dev/null; exit' INT TERM EXIT
    fi
    info "sudo access confirmed ✔"

    # Disk space (warn if < 10 GB free)
    local free_gb; free_gb=$(df --output=avail / | tail -1 | awk '{printf "%.0f",$1/1048576}')
    (( free_gb < 10 )) \
        && warn "Only ${free_gb} GB free — at least 10 GB recommended" \
        || info "Disk: ${free_gb} GB free ✔"

    # Enable Ubuntu universe repo (prometheus, obs-studio, etc. live here)
    if ! grep -r "^deb.*universe" /etc/apt/sources.list \
            /etc/apt/sources.list.d/ 2>/dev/null | grep -q universe; then
        $DRY || sudo add-apt-repository universe -y >>"$LOG_FILE" 2>&1
        info "Ubuntu universe repo: enabled"
    else
        info "Ubuntu universe repo: already enabled ✔"
    fi
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 1 — REPOSITORIES
#  
#  All repos are added FIRST, then a single `apt-get update` runs.
#  This is more efficient than updating after each repo.
# ═════════════════════════════════════════════════════════════════════════════

# Install curl, gnupg, wget before trying to add any repos
bootstrap_deps() {
    step "Bootstrap: ensuring curl, gnupg, wget, lsb-release are present"
    local needed=()
    # software-properties-common
    for p in curl gnupg wget lsb-release ca-certificates apt-transport-https; do
        dpkg -l "$p" 2>/dev/null | grep -q '^ii' || needed+=("$p")
    done
    [[ ${#needed[@]} -eq 0 ]] && { info "Bootstrap deps already present ✔"; return; }
    $DRY && { note_dry "apt-get install -y ${needed[*]}"; return; }
    sudo apt-get install -y "${needed[@]}" >>"$LOG_FILE" 2>&1
    info "Bootstrap deps installed: ${needed[*]}"
}


setup_repos() {
    section "📋  PHASE 1 — CONFIGURING APT REPOSITORIES"
    info "All repos use the modern signed-by keyring method (no deprecated apt-key add)."

    local CODENAME ARCH
    CODENAME=$(lsb_release -cs)
    ARCH=$(dpkg --print-architecture)

    # sudo mkdir -p /etc/apt/keyrings

    # ── 1. PostgreSQL PGDG (official PostgreSQL APT repo) ────────────────────
    # Required for postgresql-16, postgresql-16-postgis-3, postgresql-contrib-16
    add_repo "PGDG (PostgreSQL 16 + PostGIS 3.4)" \
        "/usr/share/keyrings/postgresql-keyring.gpg" \
        "https://www.postgresql.org/media/keys/ACCC4CF8.asc" \
        "deb [signed-by=/usr/share/keyrings/postgresql-keyring.gpg] https://apt.postgresql.org/pub/repos/apt ${CODENAME}-pgdg main" \
        "/etc/apt/sources.list.d/pgdg.list"

    # ── 2. VSCodium (privacy-first VS Code build, open-source) ───────────────
    add_repo "VSCodium" \
        "/usr/share/keyrings/vscodium-archive-keyring.gpg" \
        "https://gitlab.com/paulcarroty/vscodium-deb-rpm-repo/raw/master/pub.gpg" \
        "deb [signed-by=/usr/share/keyrings/vscodium-archive-keyring.gpg] https://download.vscodium.com/debs vscodium main" \
        "/etc/apt/sources.list.d/vscodium.list"

    # ── 3. Google Chrome ─────────────────────────────────────────────────────
    add_repo "Google Chrome stable" \
        "/usr/share/keyrings/google-chrome-keyring.gpg" \
        "https://dl.google.com/linux/linux_signing_key.pub" \
        "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome-keyring.gpg] https://dl.google.com/linux/chrome/deb/ stable main" \
        "/etc/apt/sources.list.d/google-chrome.list"

    # ── 4. Docker CE (engine + compose plugin) ───────────────────────────────
    add_repo "Docker Engine" \
        "/usr/share/keyrings/docker-keyring.gpg" \
        "https://download.docker.com/linux/ubuntu/gpg" \
        "deb [arch=${ARCH} signed-by=/usr/share/keyrings/docker-keyring.gpg] https://download.docker.com/linux/ubuntu ${CODENAME} stable" \
        "/etc/apt/sources.list.d/docker.list"

    # ── 5. Grafana OSS (monitoring dashboards) ───────────────────────────────
    add_repo "Grafana OSS" \
        "/usr/share/keyrings/grafana-keyring.gpg" \
        "https://apt.grafana.com/gpg.key" \
        "deb [signed-by=/usr/share/keyrings/grafana-keyring.gpg] https://apt.grafana.com stable main" \
        "/etc/apt/sources.list.d/grafana.list"

    # ── 6. Elasticsearch (AGPL — returned to open source Sep 2024) ───────────
    add_repo "Elasticsearch 8.x (AGPL / OSS since Sep 2024)" \
        "/usr/share/keyrings/elasticsearch-keyring.gpg" \
        "https://artifacts.elastic.co/GPG-KEY-elasticsearch" \
        "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" \
        "/etc/apt/sources.list.d/elasticsearch.list"

    # ── 7. pgAdmin 4 (optional PostgreSQL GUI) ───────────────────────────────
    add_repo "pgAdmin 4" \
        "/usr/share/keyrings/pgadmin4-keyring.gpg" \
        "https://www.pgadmin.org/static/packages_pgadmin_org.pub" \
        "deb [signed-by=/usr/share/keyrings/pgadmin4-keyring.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/${CODENAME} pgadmin4 main" \
        "/etc/apt/sources.list.d/pgadmin4.list"

    # ── 8. WineHQ Stable (Windows compatibility layer — requires i386) ────────
    # WineHQ needs i386 (32-bit) arch enabled to install 32-bit Windows libs.
    dpkg --print-foreign-architectures 2>/dev/null | grep -q i386 || {
        $DRY || sudo dpkg --add-architecture i386
        info "i386 architecture enabled (required for WineHQ)"
    }
    add_repo "WineHQ stable" \
        "/usr/share/keyrings/winehq-archive.key" \
        "https://dl.winehq.org/wine-builds/winehq.key" \
        "deb [arch=amd64,i386 signed-by=/usr/share/keyrings/winehq-archive.key] https://dl.winehq.org/wine-builds/ubuntu/ ${CODENAME} main" \
        "/etc/apt/sources.list.d/winehq.list"

}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 2 — SINGLE apt-get update
# ═════════════════════════════════════════════════════════════════════════════
do_apt_update() {
    section "🔄  PHASE 2 — REFRESHING PACKAGE INDEX (once)"
    $DRY && { note_dry "apt-get update"; return 0; }
    info "Running apt-get update — may take a moment..."
    sudo apt-get update >>"$LOG_FILE" 2>&1 \
        && info "Package index refreshed ✔" \
        || warn "apt-get update returned non-zero (some repos may be temporarily unreachable)"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 3 — INSTALL SECTIONS
# ═════════════════════════════════════════════════════════════════════════════

install_core() {
    section "📦  3-A  CORE BUILD TOOLS & SYSTEM LIBRARIES"
    # Essential compilers and build tools
    apt_pkg "Build essentials (gcc, g++, make, cmake)" \
        build-essential make cmake
    # Network and download tools (also needed for repo setup)
    apt_pkg "Network & download tools" \
        curl wget git gnupg apt-transport-https ca-certificates \
        lsb-release software-properties-common \
        net-tools dnsutils
    # Archive tools
    apt_pkg "Archive utilities" unzip zip xz-utils
    # System monitoring and productivity
    apt_pkg "Monitoring & productivity (htop, glances, tmux)" htop glances tmux
    # Search and text processing tools
    apt_pkg "Search tools (jq, HTTPie, ripgrep, id-utils)" \
        jq httpie ripgrep id-utils
    # Desktop notifications — used by setup scripts to alert completion
    apt_pkg "Desktop notifications (libnotify-bin / notify-send)" libnotify-bin
    # Vim with all language bindings
    apt_pkg "Vim + language compile deps (ruby, perl, lua, luajit)" \
        vim ruby-dev libperl-dev python3-dev \
        liblua5.1-0-dev libluajit-5.1-dev luajit
    # SSH client
    apt_pkg "OpenSSH client" openssh-client
}

install_python_build_libs() {
    section "🔧  3-B  PYTHON BUILD DEPENDENCIES"
    info "C library headers needed when conda/pip builds packages from source."
    apt_pkg "SSL + FFI headers"        libssl-dev libffi-dev
    apt_pkg "Compression headers"      libbz2-dev liblzma-dev
    apt_pkg "Database + REPL headers"  libreadline-dev libsqlite3-dev
    # apt_pkg "Terminal headers"         libncurses5-dev libncursesw5-dev
    apt_pkg "Terminal headers"         libncurses-dev
    apt_pkg "XML + security headers"   libxml2-dev libxmlsec1-dev
    apt_pkg "Tcl/Tk headers (tkinter)" tk-dev
}

install_ssh() {
    section "🔐  3-C  SSH SERVER"
    apt_pkg "OpenSSH server" openssh-server
    svc_enable ssh
}

install_java() {
    section "☕  3-D  JAVA RUNTIME (≥ 21)"
    info "Checks installed version — installs openjdk-21 if missing or < 21."
    local needs_jre=false needs_jdk=false

    if command -v java &>/dev/null; then
        local major; major=$(java --version 2>&1 | grep -oP '(?<=version ")\d+|\b\d+\b' | head -1)
        (( ${major:-0} >= 21 )) \
            && skip "Java JRE (v${major} — already ≥ 21)" \
            || { warn "Java JRE v${major} < 21 — upgrading to openjdk-21"; needs_jre=true; }
    else
        needs_jre=true
    fi

    if command -v javac &>/dev/null; then
        local jmaj; jmaj=$(javac --version 2>&1 | grep -oP '\d+' | head -1)
        (( ${jmaj:-0} >= 21 )) \
            && skip "Java JDK (v${jmaj} — already ≥ 21)" \
            || needs_jdk=true
    else
        needs_jdk=true
    fi

    $needs_jre && apt_pkg "OpenJDK 21 JRE" openjdk-21-jre || true
    $needs_jdk && apt_pkg "OpenJDK 21 JDK" openjdk-21-jdk || true
}

install_miniconda() {
    section "🐍  3-E  MINICONDA (Python 3.11 env manager)"
    info "Installs to ~/miniconda3. Uses conda envs — NOT global venv/pip."

    command -v conda &>/dev/null \
        && { skip "Miniconda ($(conda --version 2>/dev/null))"; return 0; }
    [[ -d "$HOME/miniconda3" ]] \
        && { skip "~/miniconda3 exists — run: export PATH=\"\$HOME/miniconda3/bin:\$PATH\""; return 0; }

    local arch; arch=$(uname -m)
    local url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${arch}.sh"
    $DRY && { note_dry "curl $url | bash -b -p ~/miniconda3"; return 0; }

    info "Downloading Miniconda installer for $arch..."
    curl -fsSL "$url" -o /tmp/miniconda.sh >>"$LOG_FILE" 2>&1 \
        || { fail "Miniconda — download failed"; rm -f /tmp/miniconda.sh; return; }
    bash /tmp/miniconda.sh -b -p "$HOME/miniconda3" >>"$LOG_FILE" 2>&1
    rm -f /tmp/miniconda.sh

    if [[ -f "$HOME/miniconda3/bin/conda" ]]; then
        export PATH="$HOME/miniconda3/bin:$PATH"
        "$HOME/miniconda3/bin/conda" init bash >>"$LOG_FILE" 2>&1
        fresh "Miniconda ($("$HOME/miniconda3/bin/conda" --version 2>/dev/null))"
        info "Tip: run  source ~/.bashrc  or open a new terminal to use conda"
    else
        fail "Miniconda — installer finished but conda binary not found"
    fi
}

install_bun() {
    section "⚡  3-F  BUN (JS/TS runtime)"
    info "Bun replaces Node.js/npm for this project — do NOT install npm/yarn/pnpm."

    command -v bun &>/dev/null \
        && { skip "Bun ($(bun --version 2>/dev/null))"; return 0; }

    $DRY && { note_dry "curl -fsSL https://bun.sh/install | bash"; return 0; }
    curl -fsSL https://bun.sh/install | bash >>"$LOG_FILE" 2>&1
    export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
    export PATH="$BUN_INSTALL/bin:$PATH"
    command -v bun &>/dev/null \
        && fresh "Bun ($(bun --version 2>/dev/null))" \
        || { fail "Bun — not found after install"; info "Try: source ~/.bashrc"; }
}

postgresql-server-dev-16install_postgresql() {
    section "🗄️   3-G  POSTGRESQL 16 + POSTGIS 3.4"
    info "Installed from the official PGDG apt repo — not the older Ubuntu version."

    # apt_pkg "PostgreSQL 16 core + contrib + server-dev" \
    #     postgresql-16 postgresql-client-16 postgresql-contrib-16 \
    #     postgresql-server-dev-16

    apt_pkg "PostgreSQL 16 core + contrib + server-dev" \
        postgresql-16 postgresql-client-16 postgresql-server-dev-16

    # PostGIS is CRITICAL — IDRM's entire geospatial feature set depends on it
    apt_pkg "PostGIS 3.4 (CRITICAL — IDRM geospatial engine)" \
        postgresql-16-postgis-3 postgresql-16-postgis-3-scripts

    svc_enable postgresql

    # Create the database if it does not exist yet (idrm_db setup happens in
    # setup-development-monolith.sh, but we can create it here if needed)
    # sudo -u postgres psql -c \
    #     "CREATE DATABASE idrm_db;" 2>/dev/null || true

    # ── FIX: ensure database exists before enabling extensions ─────────────
    if ! $DRY && pg_isready -q 2>/dev/null; then
        sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw idrm_db \
            || {
                sudo -u postgres createdb idrm_db >>"$LOG_FILE" 2>&1 \
                && info "Created database idrm_db ✔"
            }
    fi

    # Enable PostGIS SQL extension inside idrm_db (CREATE EXTENSION is idempotent)
    if ! $DRY && pg_isready -q 2>/dev/null; then
        sudo -u postgres psql -d idrm_db \
            -c "CREATE EXTENSION IF NOT EXISTS postgis;" \
            -c "CREATE EXTENSION IF NOT EXISTS postgis_topology;" \
            >>"$LOG_FILE" 2>&1 \
            && info "PostGIS extension enabled in idrm_db ✔" \
            || warn "Could not enable PostGIS in idrm_db (db may not exist yet — run setup-development-monolith.sh)"
    fi
}

install_redis() {
    section "🔴  3-H  REDIS"
    info "Cache, sessions, rate-limiting, pub/sub for IDRM."
    apt_pkg "Redis server + CLI tools" redis-server redis-tools
    svc_enable redis-server
}

install_db_guis() {
    section "🖥️   3-I  DATABASE GUI CLIENTS"

    snap_pkg "DBeaver CE (Community Edition)" dbeaver-ce --classic
    snap_pkg "Postbird (PostgreSQL-focused GUI)" postbird

    if dpkg -l pgadmin4-desktop 2>/dev/null | grep -q '^ii'; then
        skip "pgAdmin 4 Desktop (already installed)"
    elif confirm "Install pgAdmin 4 (optional — full PostgreSQL web UI)?"; then
        apt_pkg "pgAdmin 4 Desktop" pgadmin4-desktop
    else
        info "pgAdmin 4 skipped. Install later:  sudo apt install pgadmin4-desktop"
    fi

    # MongoDB Compass has a version-specific download URL — note it instead of auto-fetching
    if dpkg -l mongodb-compass 2>/dev/null | grep -q '^ii'; then
        skip "MongoDB Compass (already installed)"
    else
        info "MongoDB Compass: download the .deb from https://www.mongodb.com/try/download/compass"
        info "  Then install: sudo apt install ./mongodb-compass_*_amd64.deb"
    fi
}

install_nginx() {
    # ── NGINX (reverse proxy / API gateway) ───────────────────────────────────
    section "🌐  3-J  NGINX (web server / reverse proxy)"
    apt_pkg "NGINX" nginx
    svc_enable nginx
}

install_editors() {
    section "✏️   3-K  EDITORS & IDEs"

    # VSCodium — privacy-first VS Code build (open-source, no MS telemetry)
    apt_pkg "VSCodium (privacy-first VS Code build)" codium

    # JetBrains IDEs — all free for non-commercial use (since Oct 2024).
    # --classic required: these IDEs need system-level filesystem access.
    snap_pkg "WebStorm (free for non-commercial use since Oct 2024)" \
        webstorm --classic
    snap_pkg "IntelliJ IDEA Community Edition (free, open-source)" \
        intellij-idea-community --classic
    snap_pkg "PyCharm Community Edition (free, open-source)" \
        pycharm-community --classic

    # Cursor — no official apt/snap; download link provided
    command -v cursor &>/dev/null \
        && skip "Cursor (AI editor — already installed)" \
        || { info "Cursor: no official apt/snap — download AppImage from https://cursor.sh"
             info "  chmod +x cursor-*.AppImage && ./cursor-*.AppImage"; }
}

install_extensions() {
    section "🧩  3-L  VSCODIUM / VSCODE EXTENSIONS (privacy-screened set)"
    info "All extensions available on Open VSX — VSCodium compatible."

    codium_ext "ms-python.python"            # Python language support
    codium_ext "ms-python.vscode-pylance"    # Python IntelliSense (type-aware)
    codium_ext "ms-python.black-formatter"   # Black auto-formatter
    codium_ext "bradlc.vscode-tailwindcss"   # Tailwind CSS IntelliSense
    codium_ext "oven.bun-vscode"             # Bun runtime support
    codium_ext "dbaeumer.vscode-eslint"      # ESLint linting
    codium_ext "esbenp.prettier-vscode"      # Prettier formatter
    codium_ext "mhutchie.git-graph"          # Git history visualiser (replaces GitLens)
    codium_ext "usernamehw.errorlens"        # Inline error display (local-only, no telemetry)
    codium_ext "yoavbls.pretty-ts-errors"   # Readable TypeScript errors
    codium_ext "dsznajder.es7-react-js-snippets" # React/ES7 snippets

    # Write workspace settings with telemetry OFF and Black formatter
    local settings="${REPO_ROOT}/.vscode/settings.json"
    if [[ ! -f "$settings" ]]; then
        $DRY && { note_dry "write .vscode/settings.json"; return; }
        mkdir -p "${REPO_ROOT}/.vscode"
        cat > "$settings" << 'SETTINGS'
{
    "telemetry.telemetryLevel": "off",
    "git.blame.editorDecoration.enabled": true,
    "python.defaultInterpreterPath": "${env:HOME}/miniconda3/envs/idrm-mvp/bin/python",
    "[python]": { "editor.defaultFormatter": "ms-python.black-formatter" },
    "editor.formatOnSave": true,
    "editor.rulers": [88, 120],
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "terminal.integrated.env.linux": { "CONDA_DEFAULT_ENV": "idrm-mvp" }
}
SETTINGS
        fresh "Workspace .vscode/settings.json  (telemetry off, Black, pytest)"
    else
        skip ".vscode/settings.json  (already exists — not overwritten)"
    fi
}

install_terminal() {
    section "💻  3-M  TERMINAL"
    apt_pkg "Tilix tiling terminal emulator" tilix
}

install_monitoring() {
    section "📊  3-N  MONITORING & OBSERVABILITY"

    # Prometheus — snap is the simplest install path
    # snap_install "prometheus"              "Prometheus (monitoring)"

    apt_pkg "Prometheus (metrics + alerting)" prometheus
    apt_pkg "Grafana OSS (dashboards)" grafana
    svc_enable grafana-server

    # Loki — runs as a Docker container; pull the image
    if command -v docker &>/dev/null; then
        docker images 2>/dev/null | grep -qi "grafana/loki" \
            && skip "Loki Docker image (grafana/loki — already pulled)" \
            || {
                $DRY && note_dry "docker pull grafana/loki:latest" || {
                    info "Pulling Grafana Loki image..."
                    docker pull grafana/loki:latest >>"$LOG_FILE" 2>&1 \
                        && fresh "Loki Docker image (grafana/loki:latest)" \
                        || fail "Loki — docker pull failed (is Docker daemon running?)"
                }
            }
    else
        warn "Loki skipped — Docker not installed yet. Run after Docker is installed:"
        warn "  docker pull grafana/loki:latest"
    fi

    # ── Metabase (Business Intelligence dashboard) ───────────────────────────
    if command -v docker &>/dev/null; then
        docker images 2>/dev/null | grep -qi "metabase" \
            && skip "Metabase Docker image (metabase — already pulled)" \
            || {
                $DRY && note_dry "docker pull metabase/metabase:latest" || {
                    info "Pulling Metabase image..."
                    docker pull metabase/metabase >>"$LOG_FILE" 2>&1 \
                        && fresh "Metabase Docker image (metabase/metabase)" \
                        || fail "Metabase — docker pull failed (is Docker daemon running?)"
                }
            }
    else
        warn "Metabase skipped — Docker not installed yet. Run after Docker is installed:"
        # warn "  docker pull metabase/metabase:latest"
        warn "  docker pull metabase/metabase"
    fi

    run_metabase=false
    # TBD: The '!' reverses the failure code to success
    if ! $run_metabase; then
        warn "Access denied: Metbase run snippet for reference purpose only."
    else
        if docker ps -a 2>/dev/null | grep -q "metabase"; then
            skip "Metabase container (metabase — already running)"
        else
            info "Starting Metabase (BI dashboard — port 3000)…"
            $DRY && note_dry "[dry-run] docker run metabase/metabase → port 3000" || {
                docker pull metabase/metabase 2>&1 | tee -a "$LOG_FILE"
                docker run -d --name metabase \
                    --restart unless-stopped \
                    -p 3000:3000 \
                    -v metabase-data:/metabase-data \
                    metabase/metabase 2>&1 | tee -a "$LOG_FILE" \
                    && ok "Metabase started → http://localhost:3000" \
                    || warn "Metabase failed to start — check: docker logs metabase"
            }
        fi
    fi
}

install_search() {
    section "🔎  3-O  SEARCH & INDEXING"

    apt_pkg "Elasticsearch 8.x (AGPL / free basic tier)" elasticsearch
    dpkg -l elasticsearch 2>/dev/null | grep -q '^ii' && svc_enable elasticsearch || true

    apt_pkg "ripgrep (fast grep / rg)" ripgrep
    apt_pkg "id-utils (mkid / lid / gid code-tag DB)" id-utils

    command -v grok &>/dev/null \
        && skip "grok (log-pattern CLI — already installed)" \
        || { info "grok: no standard apt package"; \
             info "  Use Logstash's built-in grok or install from github.com/nicholasgasior/golog"; }
}

install_claude_code() {
    section "🤖  3-P  CLAUDE CODE (AI coding assistant)"
    info "Requires Node.js 18+. Installed via nvm — does NOT conflict with Bun."

    command -v claude &>/dev/null \
        && { skip "Claude Code ($(claude --version 2>/dev/null | head -1))"; return 0; }

    # ── nvm + Node.js LTS (needed only for Claude Code) ───────────────────────────
    # Install nvm if not present
    if [[ ! -d "$HOME/.nvm" ]]; then
        $DRY && { note_dry "curl .../nvm/install.sh | bash"; } || {
            info "Installing nvm (Node Version Manager)..."
            curl -fsSL "https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh" \
                | bash >>"$LOG_FILE" 2>&1
        }
    else
        info "nvm already present at ~/.nvm"
    fi

    export NVM_DIR="$HOME/.nvm"
    [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh" || true

    if ! declare -f nvm &>/dev/null && ! command -v nvm &>/dev/null; then
        fail "Claude Code — nvm not available after install"
        warn "Manually: source ~/.bashrc && nvm install 20 && npm i -g @anthropic-ai/claude-code"
        return
    fi

    if $DRY; then
        note_dry "nvm install 20 && npm install -g @anthropic-ai/claude-code"
        return 0
    fi

    info "Installing Node.js 20 LTS via nvm..."
    nvm install 20 >>"$LOG_FILE" 2>&1
    nvm use 20     >>"$LOG_FILE" 2>&1
    info "Installing Claude Code via npm..."
    npm install -g @anthropic-ai/claude-code >>"$LOG_FILE" 2>&1
    command -v claude &>/dev/null \
        && fresh "Claude Code ($(claude --version 2>/dev/null | head -1))" \
        || fail "Claude Code — 'claude' not found after npm install"
}

install_api_tools() {
    section "🔁  3-Q  API TESTING TOOLS"

    snap_pkg "Postman (API testing GUI)" postman

    # ── Bruno (privacy-clean API client) ──────────────────────────────────────────
    # Bruno — git-native, no login, privacy-clean; install via GitHub releases API
    if command -v bruno &>/dev/null; then
        skip "Bruno API client (already installed)"
    else
        $DRY && { note_dry "download + install latest bruno deb from github.com/usebruno/bruno"; } || {
            info "Fetching latest Bruno release from GitHub API..."
            local burl
            burl=$(curl -fsSL "https://api.github.com/repos/usebruno/bruno/releases/latest" \
                   2>/dev/null \
                   | grep "browser_download_url" \
                   | grep "amd64_linux.deb" \
                   | head -1 \
                   | cut -d'"' -f4)
            if [[ -n "$burl" ]]; then
                curl -fsSL "$burl" -o /tmp/bruno.deb >>"$LOG_FILE" 2>&1
                sudo apt-get install -y /tmp/bruno.deb >>"$LOG_FILE" 2>&1
                rm -f /tmp/bruno.deb
                command -v bruno &>/dev/null \
                    && fresh "Bruno API client (git-native, no login, offline-first)" \
                    || fail "Bruno — deb install failed  (see $LOG_FILE)"
            else
                warn "Bruno: could not resolve download URL from GitHub API"
                info "Install manually from https://usebruno.com"
            fi
        }
    fi

    # ── Insomnia (API testing) ────────────────────────────────────────────────────
    # Insomnia note (requires login since 2023)
    command -v insomnia &>/dev/null || dpkg -l insomnia 2>/dev/null | grep -q '^ii' \
        && skip "Insomnia (already installed — account login required since 2023)" \
        || { info "Insomnia: download .deb from https://insomnia.rest (account login required)"; }
}

install_docker() {
    section "🐳  3-R  DOCKER ENGINE + COMPOSE PLUGIN"
    info "Docker Engine (CE) from the official Docker apt repo."

    apt_pkg "Docker Engine CE" \
        docker-ce docker-ce-cli containerd.io
    apt_pkg "Docker Compose v2 plugin + Buildx" \
        docker-compose-plugin docker-buildx-plugin

    # Add user to docker group so 'docker' works without sudo
    if ! groups "$USER" 2>/dev/null | grep -q '\bdocker\b'; then
        $DRY && note_dry "usermod -aG docker $USER" || {
            sudo usermod -aG docker "$USER"
            warn "Added $USER to docker group — LOG OUT and back in for this to take effect"
        }
    else
        skip "docker group: $USER already a member"
    fi

    svc_enable docker
}

install_browser() {
    # ── Google Chrome ─────────────────────────────────────────────────────────
    # Used for: Figma web, Google Keep PWA, and general testing
    section "🌍  3-S  GOOGLE CHROME"
    apt_pkg "Google Chrome stable" google-chrome-stable
}

install_multimedia() {
    section "🎬  3-T  MULTIMEDIA & GRAPHICS"
    apt_pkg "VLC media player"             vlc
    apt_pkg "GIMP image editor"            gimp
    apt_pkg "OBS Studio (recording/streaming)" obs-studio
}

install_design() {
    section "🎨  3-U  DESIGN & SCREEN CAPTURE"
    apt_pkg "Ksnip (screenshot tool)" ksnip
    apt_pkg "Caffeine (prevent sleep/screensaver)" caffeine
    
    info "Figma: no official Linux desktop app — use Chrome (excellent PWA support)"
    info "  Optional unofficial snap: sudo snap install figma-linux"
    
    # Figma — no official Linux app; this is an unofficial Electron wrapper.
    # snap_install "figma-linux"             "Figma (unofficial wrapper)"
    snap_pkg "Figma (unofficial wrapper)" figma-linux
}

install_system_tools() {
    section "🛠️   3-V  SYSTEM TOOLS & REMOTE ACCESS"
    apt_pkg "VMM — Virtual Machine Manager (QEMU/KVM GUI)" virt-manager
    apt_pkg "Remmina (RDP / VNC / SSH remote desktop client)" remmina
}

install_wine() {
    section "🍷  3-W  WINEHQ STABLE + WINETRICKS"
    info "winehq-stable from the official WineHQ apt repo (i386 already enabled)."
    apt_pkg "WineHQ stable" winehq-stable
    apt_pkg "Winetricks (Wine config + app installer helper)" winetricks
}

install_josm() {
    section "🗺️   3-X  GIS & MAPPING TOOLS"
    snap_pkg "JOSM (OpenStreetMap editor)" josm
}

install_gnome_apps() {
    section "🧩  3-Y  GNOME PRODUCTIVITY APPS"
    apt_pkg "GNOME Text Editor"  gnome-text-editor
    apt_pkg "GNOME Calendar"     gnome-calendar
    apt_pkg "GNOME Sudoku"       gnome-sudoku
    apt_pkg "GNOME To Do"        gnome-todo
    info "Google Keep: no official Linux app — Chrome → ⋮ → 'Install Keep…' (PWA)"
}

install_conda_env() {
    section "🐍  3-Z  IDRM CONDA ENVIRONMENT + PYTHON PACKAGES"
    info "Creates idrm-mvp env from environment.yml, then syncs pip packages."

    # Source conda if it was just installed this run
    if ! command -v conda &>/dev/null; then
        [[ -f "$HOME/miniconda3/bin/conda" ]] \
            && { export PATH="$HOME/miniconda3/bin:$PATH"; info "conda sourced from ~/miniconda3"; } \
            || { fail "conda env: idrm-mvp — conda not on PATH"; return; }
    fi

    local env_yml="${REPO_ROOT}/environment.yml"
    local req_txt="${REPO_ROOT}/src/backend/requirements.txt"

    # Create env
    if conda env list 2>/dev/null | grep -qE "^[* ]*idrm-mvp[[:space:]]"; then
        skip "conda env: idrm-mvp (already exists)"
    else
        [[ -f "$env_yml" ]] || { fail "environment.yml not found at $env_yml"; return; }
        $DRY && { note_dry "conda env create -f $env_yml"; } || {
            info "Creating idrm-mvp env (2-5 min)..."
            conda env create -f "$env_yml" >>"$LOG_FILE" 2>&1 \
                && fresh "conda env: idrm-mvp (Python 3.11 + all pip packages from environment.yml)" \
                || fail "conda env create failed — check $LOG_FILE"
        }
    fi

    # Sync pip packages
    conda env list 2>/dev/null | grep -qE "^[* ]*idrm-mvp[[:space:]]" || return
    [[ -f "$req_txt" ]] || { warn "requirements.txt not found — pip sync skipped"; return; }
    $DRY && { note_dry "conda run -n idrm-mvp pip install -r $req_txt"; return; }
    info "Syncing pip packages..."
    conda run -n idrm-mvp pip install -r "$req_txt" >>"$LOG_FILE" 2>&1 \
        && fresh "pip packages synced in idrm-mvp env" \
        || warn "pip sync returned non-zero — check $LOG_FILE"
}

# ═════════════════════════════════════════════════════════════════════════════
# PHASE 4 — ENABLE SERVICES
# ═════════════════════════════════════════════════════════════════════════════
enable_services() {
    section "⚡  PHASE 4 — ENABLING & STARTING SERVICES"
    info "Each call is idempotent — already-running services are left unchanged."
    svc_enable ssh
    svc_enable postgresql
    svc_enable redis-server
    svc_enable nginx
    svc_enable docker
    svc_enable grafana-server
    svc_enable prometheus
    dpkg -l elasticsearch 2>/dev/null | grep -q '^ii' && svc_enable elasticsearch || true
}

# ═════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═════════════════════════════════════════════════════════════════════════════
print_summary() {
    local total=$(( _FRESH + _SKIPPED + _FAILED ))
    $DRY && total=$(( total + _DRY_CT ))

    printf "\n${C_BOLD}${C_INFO}"
    echo   "  ╔══════════════════════════════════════════════════════════════╗"
    echo   "  ║  📋  INSTALL SUMMARY                                        ║"
    echo   "  ╠══════════════════════════════════════════════════════════════╣"
    printf "  ║  ${C_FRESH}✔${C_INFO}  Installed this run : ${C_FRESH}%-5d${C_INFO}                              ║\n" "$_FRESH"
    printf "  ║  ${C_SKIP}⏭  Already present  : %-5d${C_RST}${C_INFO}                              ║\n" "$_SKIPPED"
    printf "  ║  ${C_FAIL}✘${C_INFO}  Failed            : ${C_FAIL}%-5d${C_INFO}                              ║\n" "$_FAILED"
    $DRY && printf "  ║  ${C_DRY}◌${C_INFO}  Would install     : ${C_DRY}%-5d${C_INFO}  (dry-run)              ║\n" "$_DRY_CT"
    printf "  ║  Total             : %-5d                              ║\n" "$total"
    echo   "  ╠══════════════════════════════════════════════════════════════╣"
    printf "  ║  Log : %-53s║\n" "$LOG_FILE"
    echo   "  ╚══════════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"

    [[ $_FAILED -gt 0 ]] && printf \
        "  ${C_WARN}%d item(s) failed — see $LOG_FILE for details.${C_RST}\n\n" "$_FAILED"

    printf "  ${C_BOLD}Next steps after this script completes:${C_RST}\n"
    echo   "    1. Reload shell      :  source ~/.bashrc"
    echo   "    2. Activate env      :  conda activate idrm-mvp"
    echo   "    3. Verify the stack  :  bash scripts/check-devops-stack.sh"
    echo   "    4. Log out + back in :  (required for docker group to take effect)"
    echo   ""

    {
        echo "SUMMARY"
        printf "  Installed : %d\n" "$_FRESH"
        printf "  Skipped   : %d\n" "$_SKIPPED"
        printf "  Failed    : %d\n" "$_FAILED"
        echo  "  Finished  : $(date)"
    } >> "$LOG_FILE"
}

# ══════════════════════════════════════════════════════════════════════════════
#  MAIN — orchestrates all phases in the correct dependency order
# ══════════════════════════════════════════════════════════════════════════════
main() {
    print_banner

    # Phase 0: Checks — must pass before anything is installed
    pre_flight

    # Phase 1: Repos — add ALL third-party apt repos before running apt update
    bootstrap_deps
    setup_repos

    # Phase 2: Single apt update
    do_apt_update

    # Phase 3 — install everything
    install_core
    install_python_build_libs
    install_ssh
    install_java
    install_miniconda
    install_bun
    install_postgresql
    install_redis
    install_db_guis
    install_nginx
    install_editors

    # Phase x: IDE extensions — install after VSCodium is guaranteed present
    install_extensions
    install_terminal
    install_monitoring
    install_search
    
    # Phase x: Claude Code — install after nvm + node are guaranteed present
    install_claude_code
    install_api_tools
    install_docker
    install_browser
    install_multimedia
    install_design
    install_system_tools
    install_wine
    install_josm
    install_gnome_apps
    install_conda_env

    # Phase x — enable/start services
    enable_services

    print_summary
}

main "$@"
