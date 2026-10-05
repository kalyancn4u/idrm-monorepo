#!/usr/bin/env bash
# =============================================================================
# FILE    : scripts/update-maintain-system.sh
# PROJECT : IDRM — Full-stack + DSML DevOps Stack
#
# PURPOSE : One-shot system maintenance runner. Does the following in order:
#             1. Refresh and upgrade all Snap packages (+ snapd itself)
#             2. Remove old/disabled Snap revisions to reclaim disk space
#             3. apt update + upgrade (safe upgrades only)
#             4. apt dist-upgrade (dependency-aware; prompted unless --yes)
#             5. apt autoremove + autoclean + clean
#             6. (Optional) Docker system prune — removes stopped containers,
#                dangling images, and unused networks
#             7. Disk-space report: before vs after savings
#
# USAGE   : bash scripts/update-maintain-system.sh [OPTIONS]
#
# OPTIONS :
#   -y, --yes      Skip all confirmation prompts (for cron / CI)
#   -d, --docker   Also run Docker system prune (removes unused Docker data)
#   -h, --help     Print this help text and exit
#
# REQUIRES: sudo privileges  (script will check and prompt if needed)
#
# OUTPUT  : Coloured terminal output  +  ~/idrm-system-update.log
#
# EXAMPLE (manual run)  : bash scripts/update-maintain-system.sh
# EXAMPLE (cron weekly) : bash scripts/update-maintain-system.sh --yes --docker
# =============================================================================

set -euo pipefail
IFS=$'\n\t'

# ──────────────────────────────────────────────────────────────────────────────
# Script location — used to find project files (requirements.txt, etc.)
# ──────────────────────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ──────────────────────────────────────────────────────────────────────────────
# Parse CLI flags
# ──────────────────────────────────────────────────────────────────────────────
AUTO_YES=false
DOCKER_PRUNE=false

for _arg in "$@"; do
    case "$_arg" in
        -y|--yes)    AUTO_YES=true ;;
        -d|--docker) DOCKER_PRUNE=true ;;
        -h|--help)
            grep '^#' "$0" | grep -v '^#!/' | sed 's/^# \?//'
            exit 0 ;;
        *)
            printf "Unknown option: %s\nRun with --help for usage.\n" "$_arg" >&2
            exit 1 ;;
    esac
done

# ──────────────────────────────────────────────────────────────────────────────
# Colours
# ──────────────────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_OK='\033[0;32m'
    C_WARN='\033[1;33m'
    C_INFO='\033[0;36m'
    C_DIM='\033[2m'
    C_BOLD='\033[1m'
    C_RST='\033[0m'
    C_STEP='\033[0;35m'   # magenta for step headers
else
    C_OK='' C_WARN='' C_INFO='' C_DIM='' C_BOLD='' C_RST='' C_STEP=''
fi

# ──────────────────────────────────────────────────────────────────────────────
# Log file
# ──────────────────────────────────────────────────────────────────────────────
LOG_FILE="${HOME}/idrm-system-update.log"

# ──────────────────────────────────────────────────────────────────────────────
# Timing
# ──────────────────────────────────────────────────────────────────────────────
START_TS=$(date +%s)

# ──────────────────────────────────────────────────────────────────────────────
# Logging helpers
# ──────────────────────────────────────────────────────────────────────────────
log() {
    # Write to both terminal and log file
    printf "%s\n" "$*" | tee -a "$LOG_FILE"
}

step() {
    local msg="$1"
    printf "\n${C_BOLD}${C_STEP}  ══════════════════════════════════════════════════════\n"
    printf   "   %s\n" "$msg"
    printf   "  ══════════════════════════════════════════════════════${C_RST}\n\n"
    log "$(date '+%H:%M:%S') ▶ $msg"
}

ok()   { printf "  ${C_OK}✔${C_RST}  %s\n" "$*"; log "  [ok]  $*"; }
warn() { printf "  ${C_WARN}⚠${C_RST}  %s\n" "$*"; log "  [warn] $*"; }
info() { printf "  ${C_INFO}ℹ${C_RST}  %s\n" "$*"; log "  [info] $*"; }

# ──────────────────────────────────────────────────────────────────────────────
# Confirm prompt (skipped if --yes)
# ──────────────────────────────────────────────────────────────────────────────
confirm() {
    local msg="${1:-Continue?}"
    if $AUTO_YES; then
        info "Auto-yes mode: skipping prompt — $msg"
        return 0
    fi
    printf "\n  ${C_WARN}%s [y/N]${C_RST} " "$msg"
    read -r -n 1 _reply
    echo ""
    [[ "$_reply" =~ ^[Yy]$ ]]
}

# ──────────────────────────────────────────────────────────────────────────────
# Disk usage helper (returns bytes)
# ──────────────────────────────────────────────────────────────────────────────
disk_used_bytes() {
    df --output=used / 2>/dev/null | tail -1 | tr -d ' '
}

human_bytes() {
    # Convert 1K-blocks → human-readable string using numfmt
    local kb="$1"
    numfmt --to=iec-i --suffix=B --from-unit=1024 "$kb" 2>/dev/null || echo "${kb}K"
}

# ──────────────────────────────────────────────────────────────────────────────
# Checks
# ──────────────────────────────────────────────────────────────────────────────
preflight_checks() {
    # sudo availability
    if ! sudo -n true 2>/dev/null; then
        warn "sudo password may be required during this run."
        sudo true   # trigger password prompt now, not mid-update
    fi
    ok "sudo access confirmed"

    # snap availability
    if ! command -v snap &>/dev/null; then
        warn "snap not found — Snap update steps will be skipped"
    else
        ok "snap found: $(snap --version | head -1)"
    fi

    # apt availability
    if ! command -v apt &>/dev/null; then
        printf "  ✘  apt not found — this script requires an apt-based system.\n" >&2
        exit 1
    fi
    ok "apt found"
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 1 — Snap update
# ──────────────────────────────────────────────────────────────────────────────
update_snap() {
    if ! command -v snap &>/dev/null; then
        info "Snap not installed — skipping Snap update step."
        return 0
    fi

    step "STEP 1/10 · Snap — refresh all packages (including snapd itself)"

    # Refresh snapd first; ignore error if already up to date
    info "Refreshing snapd..."
    sudo snap refresh snapd 2>&1 | tee -a "$LOG_FILE" || true

    # Refresh all other snaps
    info "Refreshing all installed snaps..."
    sudo snap refresh 2>&1 | tee -a "$LOG_FILE" || true

    ok "Snap refresh complete"
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 2 — Snap old revision cleanup
# ──────────────────────────────────────────────────────────────────────────────
cleanup_snap_revisions() {
    if ! command -v snap &>/dev/null; then
        return 0
    fi

    step "STEP 2/10 · Snap — remove old / disabled revisions"

    local removed=0

    # List disabled (old) revisions and remove them
    snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | \
    while read -r snap_name revision; do
        info "Removing $snap_name (rev $revision)..."
        sudo snap remove "$snap_name" --revision="$revision" 2>&1 | tee -a "$LOG_FILE" || true
        removed=$(( removed + 1 ))
    done

    if [[ $removed -eq 0 ]]; then
        ok "No old snap revisions found — nothing to remove"
    else
        ok "Removed $removed old snap revision(s)"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 3 — apt update
# ──────────────────────────────────────────────────────────────────────────────
apt_update() {
    step "STEP 3/10 · APT — update package index"
    sudo apt update 2>&1 | tee -a "$LOG_FILE"
    ok "Package index updated"
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 4 — apt upgrade
# ──────────────────────────────────────────────────────────────────────────────
apt_upgrade() {
    step "STEP 4/10 · APT — upgrade installed packages"

    # Show what will be upgraded
    local upgradable
    upgradable=$(apt list --upgradable 2>/dev/null | grep -vc "Listing…" || echo 0)
    info "$upgradable package(s) upgradable"

    if [[ "$upgradable" -eq 0 ]]; then
        ok "All packages already up to date"
        return 0
    fi

    if ! confirm "Proceed with apt upgrade ($upgradable packages)?"; then
        warn "apt upgrade skipped by user"
        return 0
    fi

    sudo apt upgrade -y 2>&1 | tee -a "$LOG_FILE"
    ok "apt upgrade complete"

    # dist-upgrade handles changed dependencies (e.g. kernel updates)
    if confirm "Also run apt dist-upgrade (handles dependency changes)?"; then
        sudo apt dist-upgrade -y 2>&1 | tee -a "$LOG_FILE"
        ok "apt dist-upgrade complete"
    else
        info "dist-upgrade skipped"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 5 — apt cleanup
# ──────────────────────────────────────────────────────────────────────────────
apt_cleanup() {
    step "STEP 5/10 · APT — remove orphans and clean cache"

    info "Running apt autoremove..."
    sudo apt autoremove -y 2>&1 | tee -a "$LOG_FILE"
    ok "Orphaned packages removed"

    info "Running apt autoclean..."
    sudo apt autoclean -y 2>&1 | tee -a "$LOG_FILE"
    ok "Partial package files cleaned"

    info "Running apt clean..."
    sudo apt clean 2>&1 | tee -a "$LOG_FILE"
    ok "Downloaded package cache cleared"
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 6 — Conda update (if installed)
# ──────────────────────────────────────────────────────────────────────────────
conda_update() {
    step "STEP 8/10 · Conda — update conda itself, base env, and idrm-mvp pip packages"

    if ! command -v conda &>/dev/null; then
        info "conda not found — skipping Conda update step"
        return 0
    fi

    # Update conda package manager itself
    info "Updating conda..."
    conda update -n base -c defaults conda --yes 2>&1 | tee -a "$LOG_FILE" || true
    ok "conda updated"

    # Update all packages in idrm-mvp conda environment
    if conda env list 2>/dev/null | grep -q "idrm-mvp"; then
        info "Updating conda packages in idrm-mvp environment..."
        conda update --all -n idrm-mvp --yes 2>&1 | tee -a "$LOG_FILE" || true
        ok "idrm-mvp conda packages updated"

        # Also upgrade pip packages from requirements.txt
        # Try REPO_ROOT first, then common locations
        local req_txt=""
        for candidate in \
            "${REPO_ROOT}/src/backend/requirements.txt" \
            "${HOME}/idrm/src/backend/requirements.txt" \
            "${HOME}/projects/idrm/src/backend/requirements.txt"; do
            [[ -f "$candidate" ]] && { req_txt="$candidate"; break; }
        done

        if [[ -n "$req_txt" ]]; then
            info "Upgrading pip packages from ${req_txt}..."
            conda run -n idrm-mvp pip install -r "$req_txt" --upgrade \
                2>&1 | tee -a "$LOG_FILE" || true
            ok "idrm-mvp pip packages upgraded"
        else
            info "src/backend/requirements.txt not found — skipping pip upgrade"
            info "  Run manually: conda activate idrm-mvp && pip install -r src/backend/requirements.txt --upgrade"
        fi
    else
        info "idrm-mvp conda environment not found — skipping"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 6 — Bun self-upgrade
# ──────────────────────────────────────────────────────────────────────────────
update_bun() {
    step "STEP 6/10 · Bun — self-upgrade to latest stable"

    # Source Bun from its install location if not yet on PATH
    export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"
    export PATH="$BUN_INSTALL/bin:$PATH"

    if ! command -v bun &>/dev/null; then
        info "Bun not installed — skipping"
        return 0
    fi

    info "Current Bun version: $(bun --version 2>/dev/null)"
    # 'bun upgrade' updates Bun itself to the latest stable release
    bun upgrade 2>&1 | tee -a "$LOG_FILE" || true
    ok "Bun updated to: $(bun --version 2>/dev/null)"
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 7 — npm global packages (Claude Code, etc.)
# ──────────────────────────────────────────────────────────────────────────────
update_npm_globals() {
    step "STEP 7/10 · npm global packages — update Claude Code and other globals"

    # Source nvm so Node.js / npm are on PATH for this session
    export NVM_DIR="$HOME/.nvm"
    [[ -s "$NVM_DIR/nvm.sh" ]] && source "$NVM_DIR/nvm.sh" || true

    if ! command -v npm &>/dev/null; then
        info "npm not on PATH (nvm not sourced or Node.js not installed)"
        info "  To install: source ~/.bashrc && nvm install 20"
        return 0
    fi

    info "npm version: $(npm --version 2>/dev/null)"
    info "Updating all global npm packages..."
    # npm update -g upgrades every globally-installed package (Claude Code, etc.)
    npm update -g 2>&1 | tee -a "$LOG_FILE" || true
    ok "npm global packages updated"

    # Confirm Claude Code specifically
    if command -v claude &>/dev/null; then
        ok "Claude Code: $(claude --version 2>/dev/null | head -1)"
    else
        info "Claude Code not found after update — install: npm i -g @anthropic-ai/claude-code"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 9 — Docker image refresh (Loki + Metabase)
# ──────────────────────────────────────────────────────────────────────────────
update_docker_images() {
    step "STEP 9/10 · Docker images — pull latest Loki and Metabase"

    if ! command -v docker &>/dev/null; then
        info "Docker not installed — skipping image updates"
        return 0
    fi

    if ! docker info &>/dev/null 2>&1; then
        warn "Docker daemon not running — skipping image pulls"
        warn "  Start it: sudo systemctl start docker"
        return 0
    fi

    # Only pull images that are already present locally (don't auto-pull new ones)
    for image in "grafana/loki:latest" "metabase/metabase:latest"; do
        local repo="${image%%:*}"
        if docker images --format '{{.Repository}}' 2>/dev/null | grep -q "^${repo}$"; then
            info "Pulling latest ${image}..."
            docker pull "$image" 2>&1 | tee -a "$LOG_FILE" || true
            ok "${repo} image updated"
        else
            info "${repo}: not present locally — skipping (run install script to pull)"
        fi
    done
}

# ──────────────────────────────────────────────────────────────────────────────
# STEP 10 — Docker prune (optional, requires --docker flag)
# ──────────────────────────────────────────────────────────────────────────────
docker_cleanup() {
    step "STEP 10/10 · Docker — prune unused data"

    if ! command -v docker &>/dev/null; then
        info "Docker not installed — skipping Docker cleanup"
        return 0
    fi

    if ! $DOCKER_PRUNE; then
        info "Docker prune skipped (run with --docker to enable)"
        return 0
    fi

    warn "Docker prune removes stopped containers, dangling images & unused networks."
    warn "Running volumes are NOT removed. Unused volumes require a separate step."
    if ! confirm "Proceed with Docker system prune?"; then
        info "Docker prune skipped by user"
        return 0
    fi

    info "Pruning stopped containers, dangling images, unused networks..."
    docker system prune -f 2>&1 | tee -a "$LOG_FILE"
    ok "Docker system prune complete"

    info "Pruning dangling images..."
    docker image prune -f 2>&1 | tee -a "$LOG_FILE"
    ok "Docker image prune complete"

    # Volumes — DANGEROUS, prompt separately even in --yes mode
    printf "\n  ${C_WARN}⚠  Docker volume prune PERMANENTLY removes unused volumes.${C_RST}\n"
    printf "  ${C_WARN}   This can delete database data if volumes are not mounted.${C_RST}\n"
    printf "  ${C_WARN}   Prune unused Docker volumes? [y/N]${C_RST} "
    read -r -n 1 _vreply
    echo ""
    if [[ "$_vreply" =~ ^[Yy]$ ]]; then
        docker volume prune -f 2>&1 | tee -a "$LOG_FILE"
        ok "Docker volume prune complete"
    else
        info "Docker volume prune skipped (good default)"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Disk-space report
# ──────────────────────────────────────────────────────────────────────────────
disk_report() {
    local before_kb="$1"
    local after_kb
    after_kb=$(disk_used_bytes)
    local saved_kb=$(( before_kb - after_kb ))
    local total_kb; total_kb=$(df --output=size / 2>/dev/null | tail -1 | tr -d ' ')
    local avail_kb; avail_kb=$(df --output=avail / 2>/dev/null | tail -1 | tr -d ' ')

    printf "\n${C_BOLD}${C_INFO}"
    echo   "  ╔══════════════════════════════════════════════════════════╗"
    echo   "  ║  💾  DISK SPACE REPORT                                   ║"
    echo   "  ╠══════════════════════════════════════════════════════════╣"
    printf "  ║  Before    : %-44s║\n" "$(human_bytes "$before_kb") used"
    printf "  ║  After     : %-44s║\n" "$(human_bytes "$after_kb") used"
    if [[ $saved_kb -gt 0 ]]; then
        printf "  ║  ${C_OK}Freed${C_INFO}     : %-44s║\n" "$(human_bytes "$saved_kb") reclaimed  🎉"
    else
        printf "  ║  Change    : %-44s║\n" "+$(human_bytes "$(( -saved_kb ))") (upgrades installed)"
    fi
    printf "  ║  Available : %-44s║\n" "$(human_bytes "$avail_kb") free of $(human_bytes "$total_kb")"
    echo   "  ╚══════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"

    {
        echo ""
        echo "DISK REPORT"
        echo "  Before    : $(human_bytes "$before_kb")"
        echo "  After     : $(human_bytes "$after_kb")"
        echo "  Freed     : $(human_bytes "$saved_kb")"
        echo "  Available : $(human_bytes "$avail_kb") / $(human_bytes "$total_kb")"
    } >> "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
# Final summary
# ──────────────────────────────────────────────────────────────────────────────
print_summary() {
    local before_kb="$1"
    local end_ts; end_ts=$(date +%s)
    local elapsed=$(( end_ts - START_TS ))
    local mins=$(( elapsed / 60 ))
    local secs=$(( elapsed % 60 ))

    disk_report "$before_kb"

    printf "${C_BOLD}${C_INFO}"
    echo   "  ╔══════════════════════════════════════════════════════════╗"
    echo   "  ║  ✅  UPDATE & MAINTENANCE COMPLETE                       ║"
    printf "  ║  Time elapsed : %-42s║\n" "${mins}m ${secs}s"
    printf "  ║  Log file     : %-42s║\n" "~/idrm-system-update.log"
    echo   "  ╚══════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"

    {
        echo ""
        echo "COMPLETE"
        echo "  Elapsed : ${mins}m ${secs}s"
        echo "  Log     : $LOG_FILE"
        echo "  Date    : $(date)"
    } >> "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
# Banner
# ──────────────────────────────────────────────────────────────────────────────
print_banner() {
    printf "\n${C_BOLD}${C_INFO}"
    echo   "  ╔══════════════════════════════════════════════════════════╗"
    echo   "  ║  🔄  IDRM — System Update & Maintenance                 ║"
    echo   "  ║      Snap · APT · Bun · npm · Conda · Docker           ║"
    echo   "  ╚══════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"
    printf "  ${C_DIM}Host :${C_RST} %s  |  ${C_DIM}User :${C_RST} %s\n" \
           "$(hostname)" "$(whoami)"
    printf "  ${C_DIM}Date :${C_RST} %s\n" "$(date '+%Y-%m-%d %H:%M:%S')"
    printf "  ${C_DIM}Log  :${C_RST} %s\n\n" "$LOG_FILE"

    $DOCKER_PRUNE && \
        printf "  ${C_WARN}⚠  Docker prune is ENABLED (--docker flag)${C_RST}\n\n"

    $AUTO_YES && \
        printf "  ${C_WARN}⚠  Auto-yes mode ENABLED — prompts will be skipped${C_RST}\n\n"

    # Initialise log file
    {
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo " IDRM System Update & Maintenance Log"
        echo " Started : $(date)"
        echo " Host    : $(hostname) | User : $(whoami)"
        echo " OS      : $(lsb_release -ds 2>/dev/null || uname -sr)"
        echo " Flags   : auto-yes=$AUTO_YES docker-prune=$DOCKER_PRUNE"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } > "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
# main
# ──────────────────────────────────────────────────────────────────────────────
main() {
    print_banner

    # Snapshot disk usage before we start
    local before_kb
    before_kb=$(disk_used_bytes)

    # Pre-flight
    step "PRE-FLIGHT · Checking requirements"
    preflight_checks

    # Run all steps
    update_snap
    cleanup_snap_revisions
    apt_update
    apt_upgrade
    apt_cleanup
    update_bun
    update_npm_globals
    conda_update
    update_docker_images
    docker_cleanup

    # Report
    print_summary "$before_kb"
}

# ──────────────────────────────────────────────────────────────────────────────
main "$@"
