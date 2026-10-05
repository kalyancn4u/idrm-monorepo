#!/usr/bin/env bash
# =============================================================================
# FILE    : scripts/check-devops-stack.sh
# PROJECT : IDRM — Full-stack + DSML DevOps Stack
#
# PURPOSE : Verify the installation status, version, and service health of
#           every tool in the IDRM Full-stack + DSML DevOps stack.
#           Mostly read-only; --fix-java can install/upgrade Java if needed.
#
# USAGE   : bash scripts/check-devops-stack.sh [OPTIONS]
#
# OPTIONS :
#   -q, --quiet      Print only missing / warning items (skip green rows)
#   -s, --services   Show a dedicated services-status summary at the end
#   -j, --fix-java   If Java is missing or < 21, install openjdk-21-jdk/jre
#                    via apt (requires sudo)
#   -h, --help       Print this help text and exit
#
# OUTPUT  : Coloured terminal report   +   ~/idrm-stack-check.log
#
# REQUIRES: bash ≥ 4.0, standard coreutils (awk, grep, sed, dpkg, systemctl)
#           No root required unless --fix-java is used.
#
# NOTES   :
#   • Package-name corrections vs the original list:
#       liblua_5.1-dev    → liblua5.1-dev
#       libluajit_5.1-dev → libluajit-5.1-dev
#       Ksnop             → ksnip   (typo in original list)
#       default-jre/jdk   → openjdk-21-jre/jdk  (22.04 default is Java 11)
#   • Freemium / free-personal tools are included and checked normally;
#     their license tier is shown in the LICENSE column — no warnings.
#   • Items with no official Linux package:
#       Figma       — no official Linux desktop app (browser / unofficial snap)
#       Google Keep — no official Linux desktop app (Chrome PWA recommended)
#   • Grok        — treated as log-pattern CLI tool (ELK / Logstash context)
#   • Elasticsearch — returned to open-source (AGPL) in Sep 2024
#   • Claude Code — requires Node.js 18+ (via nvm) or native binary
# =============================================================================

set -uo pipefail   # intentionally omit -e so missing tools don't abort the run
IFS=$'\n\t'

# ──────────────────────────────────────────────────────────────────────────────
# Parse CLI flags
# ──────────────────────────────────────────────────────────────────────────────
QUIET=false
SHOW_SERVICES=false
FIX_JAVA=false

for _arg in "$@"; do
    case "$_arg" in
        -q|--quiet)    QUIET=true ;;
        -s|--services) SHOW_SERVICES=true ;;
        -j|--fix-java) FIX_JAVA=true ;;
        -h|--help)
            grep '^#' "$0" | grep -v '^#!/' | sed 's/^# \?//'
            exit 0 ;;
    esac
done

# ──────────────────────────────────────────────────────────────────────────────
# Colours  (auto-disabled when stdout is not a TTY)
# ──────────────────────────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
    C_OK='\033[0;32m'       # green
    C_MISS='\033[0;31m'     # red
    C_WARN='\033[1;33m'     # yellow
    C_INFO='\033[0;36m'     # cyan
    C_DIM='\033[2m'
    C_BOLD='\033[1m'
    C_RST='\033[0m'
else
    C_OK='' C_MISS='' C_WARN='' C_INFO='' C_DIM='' C_BOLD='' C_RST=''
fi

SYM_OK="✔"
SYM_MISS="✘"
SYM_WARN="⚠"
SYM_NOTE="ℹ"

# ──────────────────────────────────────────────────────────────────────────────
# Counters
# ──────────────────────────────────────────────────────────────────────────────
_TOTAL=0
_INSTALLED=0
_MISSING=0
_WARNED=0

# ──────────────────────────────────────────────────────────────────────────────
# Column widths
# ──────────────────────────────────────────────────────────────────────────────
W_NAME=24
W_VER=24
W_LIC=20

# ──────────────────────────────────────────────────────────────────────────────
# Log file
# ──────────────────────────────────────────────────────────────────────────────
LOG_FILE="${HOME}/idrm-stack-check.log"

# ──────────────────────────────────────────────────────────────────────────────
# print_banner
# ──────────────────────────────────────────────────────────────────────────────
print_banner() {
    printf "\n${C_BOLD}${C_INFO}"
    echo   "  ╔════════════════════════════════════════════════════════════════════╗"
    echo   "  ║  🔍  IDRM DevOps Stack — Health Checker                          ║"
    echo   "  ║      Full-stack + DSML  ·  Ubuntu 22.04 / 24.04 LTS             ║"
    echo   "  ╚════════════════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"
    printf "  ${C_DIM}Host   :${C_RST} %s\n"    "$(hostname 2>/dev/null || echo unknown)"
    printf "  ${C_DIM}User   :${C_RST} %s\n"    "$(whoami  2>/dev/null || echo unknown)"
    printf "  ${C_DIM}Date   :${C_RST} %s\n"    "$(date '+%Y-%m-%d %H:%M:%S')"
    printf "  ${C_DIM}OS     :${C_RST} %s\n"    "$(lsb_release -ds 2>/dev/null || uname -sr)"
    printf "  ${C_DIM}Log    :${C_RST} %s\n\n"  "$LOG_FILE"

    # Initialise / overwrite log file
    {
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo " IDRM DevOps Stack Health Check"
        echo " Generated : $(date)"
        echo " Host : $(hostname) | User : $(whoami)"
        echo " OS   : $(lsb_release -ds 2>/dev/null || uname -sr)"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    } > "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
# section <emoji + title>
# ──────────────────────────────────────────────────────────────────────────────
section() {
    printf "\n${C_BOLD}  ──────────────────────────────────────────────────────────────────────\n"
    printf   "   %s\n" "$1"
    printf   "  ──────────────────────────────────────────────────────────────────────${C_RST}\n"
    printf   "  ${C_DIM}  %-${W_NAME}s %-${W_VER}s %-${W_LIC}s %s${C_RST}\n" \
             "TOOL" "VERSION / STATUS" "LICENSE" "NOTES"
    echo ""
    echo "" >> "$LOG_FILE"
    echo "[$1]" >> "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
# row  status  name  version  license  notes
#   status: ok | miss | warn | note
# ──────────────────────────────────────────────────────────────────────────────
row() {
    local status="$1" name="$2" ver="${3:--}" lic="${4:-Free/OSS}" notes="${5:-}"
    _TOTAL=$(( _TOTAL + 1 ))

    # Truncate long version strings
    [[ ${#ver} -gt $(( W_VER - 1 )) ]] && ver="${ver:0:$((W_VER-2))}…"

    case "$status" in
        ok)
            _INSTALLED=$(( _INSTALLED + 1 ))
            $QUIET && { echo "[ok]   $name | $ver | $lic | $notes" >> "$LOG_FILE"; return; }
            printf "  ${C_OK}${SYM_OK}${C_RST}  %-${W_NAME}s ${C_OK}%-${W_VER}s${C_RST} %-${W_LIC}s ${C_DIM}%s${C_RST}\n" \
                   "$name" "$ver" "$lic" "$notes"
            ;;
        miss)
            _MISSING=$(( _MISSING + 1 ))
            printf "  ${C_MISS}${SYM_MISS}${C_RST}  %-${W_NAME}s ${C_MISS}%-${W_VER}s${C_RST} %-${W_LIC}s ${C_DIM}%s${C_RST}\n" \
                   "$name" "NOT INSTALLED" "$lic" "$notes"
            ;;
        warn)
            _WARNED=$(( _WARNED + 1 ))
            printf "  ${C_WARN}${SYM_WARN}${C_RST}  %-${W_NAME}s ${C_WARN}%-${W_VER}s${C_RST} %-${W_LIC}s ${C_DIM}%s${C_RST}\n" \
                   "$name" "$ver" "$lic" "$notes"
            ;;
        note)
            $QUIET && { echo "[note] $name | $ver | $lic | $notes" >> "$LOG_FILE"; return; }
            printf "  ${C_INFO}${SYM_NOTE}${C_RST}  %-${W_NAME}s ${C_DIM}%-${W_VER}s${C_RST} %-${W_LIC}s ${C_DIM}%s${C_RST}\n" \
                   "$name" "$ver" "$lic" "$notes"
            ;;
    esac
    echo "[$status] $name | $ver | $lic | $notes" >> "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check a CLI binary
#   chk_bin  "Display Name"  cmd  "version-expression"  "License"  ["Notes"]
# ──────────────────────────────────────────────────────────────────────────────
chk_bin() {
    local name="$1" cmd="$2" vexpr="$3" lic="$4" notes="${5:-}"
    if command -v "$cmd" &>/dev/null; then
        local ver; ver=$(eval "$vexpr" 2>/dev/null | head -1) || ver="installed"
        [[ -z "$ver" ]] && ver="installed"
        row ok "$name" "$ver" "$lic" "$notes"
    else
        row miss "$name" "" "$lic" "$notes"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check an APT package via dpkg
#   chk_deb  "Display Name"  pkg  "License"  ["Notes"]
# ──────────────────────────────────────────────────────────────────────────────
chk_deb() {
    local name="$1" pkg="$2" lic="$3" notes="${4:-}"
    if dpkg -l "$pkg" 2>/dev/null | grep -q '^ii'; then
        local ver; ver=$(dpkg -l "$pkg" 2>/dev/null | awk '/^ii/{print $3; exit}')
        row ok "$name" "$ver" "$lic" "$notes"
    else
        row miss "$name" "" "$lic" "$notes"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check a Snap package
#   chk_snap  "Display Name"  snap-name  "License"  ["Notes"]
# ──────────────────────────────────────────────────────────────────────────────
chk_snap() {
    local name="$1" snapname="$2" lic="$3" notes="${4:-}"
    if command -v snap &>/dev/null && snap list "$snapname" 2>/dev/null | grep -q "^${snapname}"; then
        local ver; ver=$(snap list "$snapname" 2>/dev/null | awk "NR==2{print \$2}")
        row ok "$name" "$ver" "$lic" "$notes"
    else
        row miss "$name" "" "$lic" "$notes"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check a systemd service
#   chk_svc  "Display Name"  service-unit  "version-expression"  "License" ["Notes"]
# ──────────────────────────────────────────────────────────────────────────────
chk_svc() {
    local name="$1" svc="$2" vexpr="$3" lic="$4" notes="${5:-}"
    local ver="" active="" enabled=""

    active=$(systemctl is-active  "${svc}" 2>/dev/null || echo "unknown")
    enabled=$(systemctl is-enabled "${svc}" 2>/dev/null || echo "unknown")

    if systemctl list-unit-files "${svc}.service" 2>/dev/null | grep -q "${svc}.service"; then
        [[ -n "$vexpr" ]] && ver=$(eval "$vexpr" 2>/dev/null | head -1 || true)
        [[ -z "$ver" ]]   && ver="installed"
        local svc_tag="svc:${active}(${enabled})"
        if [[ "$active" == "active" ]]; then
            row ok   "$name" "$ver" "$lic" "● running | $svc_tag $notes"
        else
            row warn "$name" "$ver" "$lic" "◌ ${active} | $svc_tag $notes"
        fi
    else
        row miss "$name" "" "$lic" "service not found | $notes"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check a VSCodium / VS Code extension
#   chk_ext  "ext.id"
# ──────────────────────────────────────────────────────────────────────────────
chk_ext() {
    local ext_id="$1"
    local ext_dir_oss="${HOME}/.vscode-oss/extensions"
    local ext_dir_ms="${HOME}/.vscode/extensions"
    local found=false

    for dir in "$ext_dir_oss" "$ext_dir_ms"; do
        [[ -d "$dir" ]] && ls "$dir" 2>/dev/null | grep -qi "^${ext_id}-" && found=true && break
    done

    if $found; then
        row ok "  ext: ${ext_id}" "installed" "Open VSX / Various"
    else
        row miss "  ext: ${ext_id}" "" "Open VSX / Various"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check whether the idrm-mvp conda environment exists
#   chk_conda_env  "env-name"   returns 0 if found, 1 if missing
# ──────────────────────────────────────────────────────────────────────────────
chk_conda_env() {
    local env_name="$1"
    if ! command -v conda &>/dev/null; then
        row miss "conda env: ${env_name}" "" "conda / MIT" \
            "conda not on PATH — install Miniconda first"
        return 1
    fi
    if conda env list 2>/dev/null | grep -qE "^[* ]*${env_name}[[:space:]]"; then
        local py_ver
        py_ver=$(conda run -n "$env_name" python --version 2>/dev/null | head -1 \
                 || echo "exists")
        row ok "conda env: ${env_name}" "$py_ver" "conda / MIT" \
            "activate: conda activate ${env_name}"
        return 0
    else
        row miss "conda env: ${env_name}" "" "conda / MIT" \
            "Run: conda env create -f environment.yml"
        return 1
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: check a pip package inside the idrm-mvp conda environment
#   chk_pip  "Display Name"  "pip-package-name"  "License"  ["Notes"]
#
# Uses `conda run` so the environment does NOT need to be active first.
# ──────────────────────────────────────────────────────────────────────────────
chk_pip() {
    local name="$1" pkg="$2" lic="$3" notes="${4:-}"

    # Skip cleanly if conda itself is not installed
    if ! command -v conda &>/dev/null; then
        row note "$name" "conda missing" "$lic" "$notes"
        return
    fi

    # Skip cleanly if the idrm-mvp environment has not been created yet
    if ! conda env list 2>/dev/null | grep -qE "^[* ]*idrm-mvp[[:space:]]"; then
        row note "$name" "idrm-mvp env missing" "$lic" \
            "create env first: conda env create -f environment.yml"
        return
    fi

    local ver
    # `pip show <pkg>` prints "Version: x.y.z" if installed
    ver=$(conda run -n idrm-mvp pip show "$pkg" 2>/dev/null \
          | awk '/^Version:/{print $2}')

    if [[ -n "$ver" ]]; then
        row ok "$name" "$ver" "$lic" "$notes"
    else
        row miss "$name" "" "$lic" \
            "${notes:+${notes} · }install: conda activate idrm-mvp && pip install ${pkg}"
    fi
}

# ──────────────────────────────────────────────────────────────────────────────
# Helper: verify the PostGIS SQL extension is enabled inside idrm_db
#   chk_postgis_ext — no arguments
#
# Tries postgres peer auth first (works right after installation),
# then falls back to the idrm_user account.
# ──────────────────────────────────────────────────────────────────────────────
chk_postgis_ext() {
    if ! command -v psql &>/dev/null; then
        row miss "PostGIS SQL extension" "" "pg-ext / GPL-2" \
            "psql not found — install postgresql-client"
        return
    fi

    # pg_isready returns 0 if the server is accepting connections
    if ! pg_isready -q 2>/dev/null; then
        row warn "PostGIS SQL extension" "PG not reachable" "pg-ext / GPL-2" \
            "Start PostgreSQL first: sudo systemctl start postgresql"
        return
    fi

    # Ask PostGIS for its library version number
    local pg_ver
    pg_ver=$(psql -U postgres -d idrm_db \
                 -tAc "SELECT PostGIS_lib_version();" 2>/dev/null \
             || psql -d idrm_db \
                    -tAc "SELECT PostGIS_lib_version();" 2>/dev/null \
             || echo "")
    pg_ver=$(echo "$pg_ver" | tr -d ' \n')

    if [[ -n "$pg_ver" ]]; then
        row ok "PostGIS SQL extension" "$pg_ver" "pg-ext / GPL-2" \
            "✓ enabled in idrm_db (postgis + postgis_topology)"
    else
        row miss "PostGIS SQL extension" "" "pg-ext / GPL-2" \
            "psql -d idrm_db -c 'CREATE EXTENSION IF NOT EXISTS postgis;'"
    fi
}

# ══════════════════════════════════════════════════════════════════════════════
#   M A I N
# ══════════════════════════════════════════════════════════════════════════════
main() {
    print_banner

    # ── 1. Core Build Tools & System Libraries ────────────────────────────────
    section "📦  CORE BUILD TOOLS & SYSTEM LIBRARIES"
    chk_deb "build-essential"       build-essential     "apt / GPL"
    chk_bin "make"                  make                "make --version | head -1"         "apt / GPL-3"
    chk_bin "cmake"                 cmake               "cmake --version | head -1"        "apt / BSD-3"
    chk_bin "curl"                  curl                "curl --version | head -1"         "apt / curl-lic"
    chk_bin "git"                   git                 "git  --version"                   "apt / GPL-2"
    chk_bin "vim"                   vim                 "vim  --version | head -1"         "apt / Charityware"
    chk_bin "htop"                  htop                "htop --version | head -1"         "apt / GPL-2"
    chk_bin "glances"               glances             "glances --version | head -1"      "apt|pip / LGPL-3"
    chk_bin "ripgrep (rg)"          rg                  "rg   --version | head -1"         "apt / MIT|Unlicense"
    chk_bin "luajit"                luajit              "luajit -v 2>&1 | head -1"         "apt / MIT"
    chk_deb "openssh-client"        openssh-client      "apt / BSD"
    chk_deb "ruby-dev"              ruby-dev            "apt / BSD-2"                      "Vim compile dep"
    chk_deb "libperl-dev"           libperl-dev         "apt / GPL|Artistic"               "Vim compile dep"
    chk_deb "python3-dev"           python3-dev         "apt / PSF"
    chk_deb "liblua5.1-dev"         liblua5.1-dev       "apt / MIT"                        "⚑ was liblua_5.1-dev in list"
    chk_deb "libluajit-5.1-dev"     libluajit-5.1-dev   "apt / MIT"                        "⚑ was libluajit_5.1-dev in list"
    chk_deb "idutils"               idutils             "apt / GPL-3"                      "mkid / lid / gid / aid"

    # ── APT infrastructure (needed to add any third-party apt repo) ──────────
    # These are rarely missing on a fresh Ubuntu install, but the setup scripts
    # require them for adding the PostgreSQL, VSCodium, Chrome, and Wine repos.
    chk_bin "wget"                  wget     "wget --version | head -1"      "apt / GPL-3"    \
        "downloads installers: Miniconda, DBeaver, Chrome, PGDG key"
    chk_bin "gnupg (gpg)"          gpg      "gpg --version | head -1"       "apt / GPL-3"    \
        "GPG key management — required for all signed-by keyring repo installs"
    chk_deb "software-properties-common" software-properties-common "apt / GPL" \
        "provides add-apt-repository command"
    chk_deb "apt-transport-https"   apt-transport-https  "apt / GPL"         \
        "enables https:// URIs in /etc/apt/sources.list.d/*.list files"
    chk_deb "ca-certificates"       ca-certificates      "apt / MPL-2"       \
        "SSL certificate chain — required for any HTTPS apt repo"
    chk_deb "lsb-release"           lsb-release          "apt / GPL"         \
        "provides \$(lsb_release -cs) — used in repo URL templates"
    chk_deb "unzip"                 unzip                "apt / Info-ZIP"     \
        "extract .zip archives (installers, assets)"
    chk_deb "zip"                   zip                  "apt / Info-ZIP"     \
        "create .zip archives"

    # ── General dev utilities ────────────────────────────────────────────────
    chk_bin "jq"             jq    "jq --version | head -1"   "apt / MIT"     \
        "JSON processor — parses API responses, config files"
    chk_bin "HTTPie (http)"  http  "http --version | head -1" "apt / BSD"     \
        "human-friendly API testing from the terminal (like curl but readable)"
    chk_deb "libnotify-bin"  libnotify-bin "apt / LGPL"                       \
        "provides notify-send — desktop notifications used in setup scripts"

    # ── 1b. Python Build Dependencies ────────────────────────────────────────
    section "🔧  PYTHON BUILD DEPENDENCIES (C extension compile deps)"
    # When conda or pip compiles a Python package from source (rather than
    # using a pre-built wheel), it needs the development headers for the
    # underlying C libraries. Even with binary wheels, several of these are
    # referenced at import time on some platforms.
    chk_deb "libssl-dev"       libssl-dev       "apt / OpenSSL"  \
        "SSL/TLS — required by cryptography, asyncpg, httpx"
    chk_deb "libffi-dev"       libffi-dev       "apt / MIT"      \
        "Foreign Function Interface — required by cffi, cryptography"
    chk_deb "libbz2-dev"       libbz2-dev       "apt / BSD"      \
        "bzip2 compression — required by Python stdlib bz2 module"
    chk_deb "libreadline-dev"  libreadline-dev  "apt / GPL-3"    \
        "readline history in Python interactive REPL"
    chk_deb "libsqlite3-dev"   libsqlite3-dev   "apt / Public Domain" \
        "SQLite3 — required by Python stdlib sqlite3 module"
    chk_deb "libncurses5-dev"  libncurses5-dev  "apt / MIT"      \
        "ncurses terminal UI — required when compiling Python from source"
    chk_deb "libncursesw5-dev" libncursesw5-dev "apt / MIT"      \
        "ncurses wide-character variant (Unicode terminal support)"
    chk_deb "xz-utils"         xz-utils         "apt / Public Domain" \
        "xz/lzma compression — required by Python stdlib lzma module"
    chk_deb "tk-dev"           tk-dev           "apt / BSD"      \
        "Tkinter GUI toolkit — required by Python stdlib tkinter module"
    chk_deb "libxml2-dev"      libxml2-dev      "apt / MIT"      \
        "XML parsing — required by lxml, python-xmlsec"
    chk_deb "libxmlsec1-dev"   libxmlsec1-dev   "apt / MIT"      \
        "XML digital signatures — required by python-xmlsec (SAML/SSO)"
    chk_deb "liblzma-dev"      liblzma-dev      "apt / Public Domain" \
        "LZMA compression — backup for Python lzma module on older Ubuntu"

    # ── 2. SSH Server ─────────────────────────────────────────────────────────
    section "🔐  SSH SERVER"
    chk_svc "openssh-server" ssh \
        "ssh -V 2>&1 | head -1" "apt / BSD" "remote access daemon"

    # ── 3. Java Runtime ──────────────────────────────────────────────────────
    section "☕  JAVA RUNTIME (≥ 21 required)"
    # 'default-jre/jdk' on Ubuntu 22.04 = Java 11; 24.04 = Java 21.
    # We always check the actual installed major version against 21.
    # Pass --fix-java to auto-install openjdk-21 if missing or outdated.

    _check_java_role() {
        local role="$1" cmd="$2" pkg="$3"

        if command -v "$cmd" &>/dev/null; then
            local ver_str; ver_str=$($cmd --version 2>&1 | head -1)
            # Extract leading integer (e.g. "17" from "openjdk 17.0.2" or
            # "21" from 'java version "21.0.1"')
            local major; major=$(echo "$ver_str" | grep -oP '(?<=version ")\d+|\b\d+\b' | head -1)
            if [[ -n "$major" ]] && (( major >= 21 )); then
                row ok "Java ${role} ✓" "$ver_str" "apt / GPL-2+CE" \
                    "v${major} — meets ≥21 requirement"
            else
                row warn "Java ${role} ✗" "$ver_str" "apt / GPL-2+CE" \
                    "v${major} < 21 → install ${pkg}"
                if $FIX_JAVA; then
                    printf "  ${C_INFO}  ↳ --fix-java: installing %s …${C_RST}\n" "$pkg"
                    sudo apt-get install -y "$pkg" 2>&1 | tail -3
                fi
            fi
        else
            row miss "Java ${role}" "NOT INSTALLED" "apt / GPL-2+CE" \
                "sudo apt install ${pkg}"
            if $FIX_JAVA; then
                printf "  ${C_INFO}  ↳ --fix-java: installing %s …${C_RST}\n" "$pkg"
                sudo apt-get install -y "$pkg" 2>&1 | tail -3
            fi
        fi
    }

    _check_java_role "JRE" java  openjdk-21-jre
    _check_java_role "JDK" javac openjdk-21-jdk

    # ── 4. Runtimes & Package Managers ───────────────────────────────────────
    section "⚙️   RUNTIMES & PACKAGE MANAGERS"
    chk_bin "Miniconda (conda)" conda "conda --version"   "direct-install / BSD" \
        "use env: idrm-mvp (python 3.11)"
    chk_bin "Bun"               bun   "bun --version"     "curl-install / MIT" \
        "JS/TS runtime — NO npm/yarn/pnpm"
    # Node.js via nvm — needed only for Claude Code on this general DevOps machine
    if command -v node &>/dev/null; then
        row ok "Node.js (nvm)" "$(node --version 2>/dev/null)" "nvm / MIT" \
            "via nvm only — for Claude Code"
    else
        row note "Node.js (nvm)" "not installed" "nvm / MIT" \
            "Required only for Claude Code — install via nvm, not apt"
    fi

    # ── 5. Databases & IDRM Core Dependencies ────────────────────────────────
    section "🗄️   DATABASES & IDRM GEOSPATIAL DEPENDENCIES"

    # ── PostgreSQL core ──────────────────────────────────────────────────────
    chk_bin "PostgreSQL 16 (psql)" psql \
        "psql --version" "apt / PostgreSQL" \
        "pgdg apt repo — install: scripts/setup-idrm-ubuntu.sh"
    chk_svc "PostgreSQL service" postgresql \
        "psql --version | head -1" "apt / PostgreSQL" ""

    # ── PostgreSQL extended packages ──────────────────────────────────────────
    # postgresql-contrib adds extra modules: pg_stat_statements (query stats),
    # pg_trgm (fuzzy text search), pg_crypto, and others used by IDRM.
    chk_deb "postgresql-contrib-16" postgresql-16 "apt / PostgreSQL" \
        "meta-check (contrib installs alongside postgresql-16)"
    chk_deb "postgresql-server-dev-16" postgresql-server-dev-16 "apt / PostgreSQL" \
        "C headers for building PostgreSQL extensions (needed by PostGIS make)"

    # ── PostGIS — CRITICAL for IDRM ───────────────────────────────────────────
    # PostGIS adds geospatial column types (GEOMETRY, GEOGRAPHY) and spatial
    # functions (ST_Distance, ST_DWithin, ST_AsGeoJSON) to PostgreSQL.
    # IDRM stores disaster event locations, service zones, and field team
    # positions as PostGIS geometry — the entire geo feature set depends on this.
    chk_deb "postgresql-16-postgis-3" postgresql-16-postgis-3 "apt / GPL-2" \
        "PostGIS 3.x — CRITICAL: IDRM geo features cannot work without this"
    chk_deb "postgresql-16-postgis-3-scripts" postgresql-16-postgis-3-scripts "apt / GPL-2" \
        "PostGIS SQL upgrade and loader scripts"

    # ── PostGIS SQL extension (enabled inside idrm_db) ───────────────────────
    # Installing the apt package above is not enough — the extension must also
    # be enabled inside the idrm_db database with CREATE EXTENSION.
    # This check connects to idrm_db and asks PostGIS for its version number.
    chk_postgis_ext

    # ── PostgreSQL client utilities ───────────────────────────────────────────
    # These are standalone binaries from the postgresql-client package.
    # setup-development-monolith.sh uses pg_isready + createdb.
    # The backup scripts use pg_dump / pg_restore.
    chk_bin "pg_isready" pg_isready \
        "pg_isready --version 2>&1 | head -1" "apt / PostgreSQL" \
        "checks if PostgreSQL is accepting connections (part of postgresql-client)"
    chk_bin "pg_dump"    pg_dump \
        "pg_dump --version   | head -1" "apt / PostgreSQL" \
        "database backup tool — used in scripts/backup-db.sh"
    chk_bin "createdb"   createdb \
        "createdb --version  | head -1" "apt / PostgreSQL" \
        "create new databases from CLI — used in setup-development-monolith.sh"

    # ── Redis ────────────────────────────────────────────────────────────────
    chk_svc "Redis (redis-server)" redis-server \
        "redis-server --version | head -1" "apt / BSD-3" ""
    # redis-cli is how setup-prerequisites.sh verifies Redis is working.
    # The service check above tells us if the daemon is running; this tells
    # us if the client CLI is on PATH (they can differ if only partial install).
    chk_bin "redis-cli"  redis-cli \
        "redis-cli --version | head -1" "apt / BSD-3" \
        "Redis CLI — used in prerequisites.sh to verify Redis connectivity"

    # ── 6. Database GUIs ─────────────────────────────────────────────────────
    section "🖥️   DATABASE GUI CLIENTS"
    # DBeaver CE — may be snap or deb
    if command -v dbeaver &>/dev/null; then
        row ok "DBeaver CE" "$(dbeaver --version 2>/dev/null | head -1 || echo installed)" \
            "deb|snap / Apache-2" "Community Edition — recommended"
    elif command -v snap &>/dev/null && snap list dbeaver-ce 2>/dev/null | grep -q dbeaver-ce; then
        row ok "DBeaver CE" \
            "$(snap list dbeaver-ce 2>/dev/null | awk 'NR==2{print $2}')" \
            "snap / Apache-2" "Community Edition — recommended"
    else
        row miss "DBeaver CE" "" "deb|snap / Apache-2" "Community Edition"
    fi

    # Postbird — free, works, installable via snap (last upstream release ~2020
    # but snap package remains functional; included per user request)
    if command -v snap &>/dev/null && snap list postbird 2>/dev/null | grep -q postbird; then
        row ok "Postbird" \
            "$(snap list postbird 2>/dev/null | awk 'NR==2{print $2}')" \
            "snap / MIT (Free)" "PostgreSQL GUI · last upstream release ~2020"
    else
        row miss "Postbird" "" "snap / MIT (Free)" \
            "snap install postbird · last upstream release ~2020"
    fi

    # MongoDB Compass
    if command -v mongodb-compass &>/dev/null || dpkg -l mongodb-compass 2>/dev/null | grep -q '^ii'; then
        local _ver; _ver=$(dpkg -l mongodb-compass 2>/dev/null | awk '/^ii/{print $3}' || echo installed)
        row ok "MongoDB Compass" "$_ver" "deb / SSPL" "GUI for MongoDB"
    else
        row miss "MongoDB Compass" "" "deb / SSPL" \
            "Download from mongodb.com/compass"
    fi

    # pgAdmin 4 — full-featured PostgreSQL web UI (optional)
    # Installed from the pgAdmin apt repo: https://www.pgadmin.org/download/
    if command -v pgadmin4 &>/dev/null || dpkg -l pgadmin4-desktop 2>/dev/null | grep -q '^ii'; then
        local _pgav; _pgav=$(dpkg -l pgadmin4-desktop 2>/dev/null | awk '/^ii/{print $3}' \
                             || echo installed)
        row ok "pgAdmin 4" "$_pgav" "apt / PostgreSQL" \
            "Full-featured PostgreSQL web UI (optional)"
    else
        row miss "pgAdmin 4" "" "apt / PostgreSQL" \
            "Optional — pgadmin4 apt repo; DBeaver CE covers most needs"
    fi

    # ── 7. Web Server ────────────────────────────────────────────────────────
    section "🌐  WEB SERVER"
    chk_svc "NGINX" nginx "nginx -v 2>&1 | head -1" "apt / BSD-2"

    # ── 8. Editors & IDEs ────────────────────────────────────────────────────
    section "✏️   EDITORS & IDEs"

    # VSCodium (privacy-first, preferred)
    if command -v codium &>/dev/null; then
        row ok "VSCodium" \
            "$(codium --version 2>/dev/null | head -1)" \
            "deb-repo / MIT" "Privacy-first build ✓ preferred"
    else
        row miss "VSCodium" "" "deb-repo / MIT" \
            "Install from vscodium.com APT repo"
    fi

    # VS Code (Microsoft) — optional alongside VSCodium
    if command -v code &>/dev/null; then
        row ok "VS Code (Microsoft)" \
            "$(code --version 2>/dev/null | head -1)" \
            "deb-repo / Microsoft" "Set telemetryLevel=off in settings"
    else
        row miss "VS Code (Microsoft)" "" "deb-repo / Microsoft" \
            "Optional — VSCodium is preferred for privacy"
    fi

    # Cursor — AI-first editor (VS Code fork, proprietary)
    if command -v cursor &>/dev/null; then
        row ok "Cursor" \
            "$(cursor --version 2>/dev/null | head -1 || echo installed)" \
            "deb|AppImage / Proprietary" "AI-first editor"
    elif ls "${HOME}"/.local/bin/cursor "${HOME}"/Applications/cursor*.AppImage \
         2>/dev/null | head -1 &>/dev/null; then
        row ok "Cursor" "AppImage" "AppImage / Proprietary" "AI-first editor"
    else
        row miss "Cursor" "" "deb|AppImage / Proprietary" \
            "Download from cursor.sh"
    fi

    # JetBrains — all free for non-commercial use since Oct 2024
    chk_snap "WebStorm" webstorm "snap / Free non-commercial" \
        "Free for non-commercial use (since Oct 2024)"
    chk_snap "IntelliJ IDEA CE" intellij-idea-community "snap / Apache-2" \
        "Community = fully free & open source"
    chk_snap "PyCharm CE" pycharm-community "snap / Apache-2" \
        "Community = fully free & open source"

    # ── 9. VSCodium / VS Code Extensions ────────────────────────────────────
    section "🧩  VSCODIUM / VSCODE EXTENSIONS  (privacy-screened set)"
    chk_ext "ms-python.python"
    chk_ext "ms-python.vscode-pylance"
    chk_ext "ms-python.black-formatter"
    chk_ext "bradlc.vscode-tailwindcss"
    chk_ext "oven.bun-vscode"
    chk_ext "dbaeumer.vscode-eslint"
    chk_ext "esbenp.prettier-vscode"
    chk_ext "mhutchie.git-graph"
    chk_ext "usernamehw.errorlens"
    chk_ext "yoavbls.pretty-ts-errors"
    chk_ext "dsznajder.es7-react-js-snippets"

    # ── 10. Terminal ─────────────────────────────────────────────────────────
    section "💻  TERMINAL"
    chk_bin "Tilix" tilix "tilix --version 2>&1 | head -1" "apt / GPL-3" \
        "Tiling terminal emulator"

    # ── 11. Monitoring & Observability ───────────────────────────────────────
    section "📊  MONITORING & OBSERVABILITY"

    chk_bin "Prometheus" prometheus \
        "prometheus --version 2>&1 | head -1" "binary|apt / Apache-2"

    chk_svc "Grafana OSS" grafana-server \
        "grafana-server --version 2>&1 | head -1" "apt-repo / AGPLv3" \
        "Grafana OSS — free"

    # Loki — binary or Docker
    if command -v loki &>/dev/null; then
        row ok "Loki (binary)" \
            "$(loki --version 2>/dev/null | head -1 || echo installed)" \
            "binary / AGPLv3" "Grafana log aggregation"
    elif command -v docker &>/dev/null && docker ps 2>/dev/null | grep -qi loki; then
        row ok "Loki (Docker)" "container running" "docker / AGPLv3" \
            "Grafana log aggregation"
    else
        row miss "Loki" "" "binary|docker / AGPLv3" \
            "docker run -p 3100:3100 grafana/loki"
    fi

    # ── 12. Search, Log & Text Tools ─────────────────────────────────────────
    section "🔎  SEARCH, LOG & TEXT TOOLS"

    # Elasticsearch — AGPL (open source again since Sep 2024)
    if systemctl list-unit-files elasticsearch.service 2>/dev/null | grep -q elasticsearch \
       || dpkg -l elasticsearch 2>/dev/null | grep -q '^ii'; then
        local _esver; _esver=$(dpkg -l elasticsearch 2>/dev/null | awk '/^ii/{print $3}' || echo installed)
        local _esact; _esact=$(systemctl is-active elasticsearch 2>/dev/null || echo unknown)
        if [[ "$_esact" == "active" ]]; then
            row ok "Elasticsearch" "$_esver" "apt-repo / AGPL-3" \
                "● running | OSS again since Sep 2024"
        else
            row warn "Elasticsearch" "$_esver" "apt-repo / AGPL-3" \
                "◌ ${_esact} | OSS again since Sep 2024"
        fi
    else
        row miss "Elasticsearch" "" "apt-repo / AGPL-3" \
            "Returned to OSS (AGPL-3) in Sep 2024"
    fi

    # ripgrep (already in build tools; repeated here for log-tool context)
    chk_bin "ripgrep (rg)" rg "rg --version | head -1" "apt / MIT|Unlicense" ""

    # Grok — log-pattern CLI (context: ELK/log parsing; no standard apt pkg)
    if command -v grok &>/dev/null; then
        row ok "grok" \
            "$(grok --version 2>/dev/null | head -1 || echo installed)" \
            "binary / MIT" "Log pattern matching CLI"
    else
        row miss "grok" "" "binary / MIT" \
            "Log-pattern CLI; also built into Logstash — install from GitHub"
    fi

    # ── 13. AI Dev Tools ─────────────────────────────────────────────────────
    section "🤖  AI CODING TOOLS"

    if command -v claude &>/dev/null; then
        row ok "Claude Code" \
            "$(claude --version 2>/dev/null | head -1 || echo installed)" \
            "npm|native / Anthropic" "Needs Anthropic API key / Pro-Max sub"
    else
        row miss "Claude Code" "" "npm|native / Anthropic" \
            "npm i -g @anthropic-ai/claude-code  (needs Node ≥18 via nvm)"
    fi

    # ── 14. API Testing ──────────────────────────────────────────────────────
    section "🔁  API TESTING TOOLS"

    chk_snap "Postman" postman "snap / Freemium" \
        "Free individual plan; login required"

    # Insomnia — works by default; account login required since 2023
    if command -v insomnia &>/dev/null || dpkg -l insomnia 2>/dev/null | grep -q '^ii'; then
        local _iv; _iv=$(dpkg -l insomnia 2>/dev/null | awk '/^ii/{print $3}' || echo installed)
        row ok "Insomnia" "$_iv" "deb / MIT (Free)" \
            "Account login required since 2023"
    else
        row miss "Insomnia" "" "deb / MIT (Free)" \
            "Download from insomnia.rest · account login required"
    fi

    # Bruno — git-native, no login, privacy-clean; good alongside Insomnia
    if command -v bruno &>/dev/null; then
        row ok "Bruno" \
            "$(bruno --version 2>/dev/null | head -1 || echo installed)" \
            "deb|AppImage / MIT (Free)" "No login · git-native · offline-first"
    else
        row miss "Bruno" "" "deb|AppImage / MIT (Free)" \
            "usebruno.com · no login · offline-first alternative"
    fi

    # ── 15. Containers & Orchestration ───────────────────────────────────────
    section "🐳  CONTAINERS & ORCHESTRATION"

    chk_bin "Docker Engine" docker "docker --version | head -1" \
        "apt / Apache-2" "Community Edition — free"

    if command -v docker &>/dev/null; then
        if docker compose version &>/dev/null 2>&1; then
            row ok "Docker Compose (plugin)" \
                "$(docker compose version --short 2>/dev/null || echo installed)" \
                "apt / Apache-2" "v2 plugin — preferred"
        elif command -v docker-compose &>/dev/null; then
            row ok "Docker Compose (v1)" \
                "$(docker-compose --version 2>/dev/null | head -1)" \
                "apt / Apache-2" "v1 standalone · migrate to 'docker compose' v2 plugin"
        else
            row miss "Docker Compose" "" "apt / Apache-2" \
                "apt install docker-compose-plugin"
        fi
    fi

    chk_svc "Docker daemon" docker \
        "docker --version | head -1" "apt / Apache-2" ""

    # Docker Desktop — free for personal/individual use; GUI for Engine
    if dpkg -l docker-desktop 2>/dev/null | grep -q '^ii'; then
        row ok "Docker Desktop" \
            "$(dpkg -l docker-desktop 2>/dev/null | awk '/^ii/{print $3}')" \
            "deb / Free (personal)" \
            "GUI for Docker Engine · paid for orgs >250 emp"
    else
        row miss "Docker Desktop" "" "deb / Free (personal)" \
            "docs.docker.com/desktop/linux · optional GUI"
    fi

    # Metabase (runs as Docker container or standalone JAR)
    if command -v docker &>/dev/null && docker ps 2>/dev/null | grep -qi metabase; then
        row ok "Metabase (Docker)" "container running" "docker / AGPL-3 (Free)" \
            "BI & analytics — port 3000"
    elif command -v docker &>/dev/null && docker images 2>/dev/null | grep -qi metabase; then
        row ok "Metabase" "image pulled (stopped)" "docker / AGPL-3 (Free)" \
            "Image present; start: docker run -p 3000:3000 metabase/metabase"
    else
        row miss "Metabase" "" "docker / AGPL-3 (Free)" \
            "docker pull metabase/metabase · run on port 3000"
    fi

    # ── 16. Browser ──────────────────────────────────────────────────────────
    section "🌍  BROWSER"

    chk_bin "Google Chrome" google-chrome \
        "google-chrome --version" "deb / Google ToS" \
        "For Figma (web), Google Keep PWA, DevTools"

    # Chrome extensions can't be checked from bash — note for user
    row note "Chrome Extensions" "(browser-internal)" "N/A" \
        "React DevTools, Redux DevTools — install inside Chrome"

    # ── 17. Multimedia & Graphics ────────────────────────────────────────────
    section "🎬  MULTIMEDIA & GRAPHICS"

    chk_bin "VLC" vlc "vlc --version 2>&1 | head -1" "apt|snap / GPL-2" \
        "(listed twice — installed once)"
    chk_bin "GIMP" gimp "gimp --version" "apt|snap / GPL-3" ""

    if command -v obs &>/dev/null || dpkg -l obs-studio 2>/dev/null | grep -q '^ii'; then
        local _obsver; _obsver=$(dpkg -l obs-studio 2>/dev/null | awk '/^ii/{print $3}' || echo installed)
        row ok "OBS Studio" "$_obsver" "apt|snap / GPL-2" "Screen recording & streaming"
    else
        row miss "OBS Studio" "" "apt|snap / GPL-2" ""
    fi

    # ── 18. Design & Screenshot Tools ────────────────────────────────────────
    section "🎨  DESIGN & SCREEN CAPTURE"

    # Figma — NO official Linux desktop app (confirmed by Figma team)
    if command -v snap &>/dev/null && snap list figma-linux 2>/dev/null | grep -q figma-linux; then
        row warn "Figma (figma-linux)" \
            "$(snap list figma-linux 2>/dev/null | awk 'NR==2{print $2}')" \
            "snap / Unofficial wrapper" \
            "⚠ Unofficial Electron wrapper — no official Linux app from Figma"
    else
        row note "Figma" "no official Linux app" "Web / Figma ToS" \
            "Use Chrome — works well; or install unofficial 'figma-linux' snap"
    fi

    # Ksnip — user wrote 'Ksnop' which is a typo; correct package is ksnip
    if command -v ksnip &>/dev/null; then
        row ok "Ksnip (screenshot)" \
            "$(ksnip --version 2>/dev/null | head -1 || echo installed)" \
            "apt|AppImage / GPL-2" "⚑ 'Ksnop' in list → corrected to ksnip"
    else
        row miss "Ksnip (screenshot)" "" "apt|AppImage / GPL-2" \
            "⚑ Original list said 'Ksnop' — correct name is ksnip"
    fi

    # ── 19. System Utilities ─────────────────────────────────────────────────
    section "🛠️   SYSTEM & UTILITIES"

    chk_deb "Caffeine"        caffeine    "apt / GPL"          "Prevents screen lock / sleep"
    chk_bin "Remmina"         remmina     "remmina --version 2>&1 | head -1" \
        "apt|snap / GPL-2" "Remote Desktop (RDP / VNC / SSH)"

    # VMM = Virtual Machine Manager (virt-manager)
    if command -v virt-manager &>/dev/null || dpkg -l virt-manager 2>/dev/null | grep -q '^ii'; then
        local _vmmver; _vmmver=$(dpkg -l virt-manager 2>/dev/null | awk '/^ii/{print $3}' || echo installed)
        row ok "VMM (virt-manager)" "$_vmmver" "apt / GPL-2" "QEMU/KVM GUI"
    else
        row miss "VMM (virt-manager)" "" "apt / GPL-2" "pkg: virt-manager"
    fi

    # ── 20. Wine ────────────────────────────────────────────────────────────
    section "🍷  WINE (WINDOWS COMPATIBILITY)"

    chk_bin "WineHQ Stable (wine)" wine \
        "wine --version" "winehq-apt / LGPL" \
        "pkg: winehq-stable from winehq.org APT repo"
    chk_bin "Winetricks"           winetricks \
        "winetricks --version" "apt / LGPL" \
        "Wine helper scripts"

    # ── 21. GIS & Mapping ───────────────────────────────────────────────────
    section "🗺️   GIS & MAPPING"

    chk_snap "JOSM" josm "snap / GPL-2" \
        "OpenStreetMap editor (Java-based)"

    # ── 22. GNOME & Productivity Apps ───────────────────────────────────────
    section "🧩  GNOME & PRODUCTIVITY APPS"

    chk_deb "Text Editor (GNOME)"  gnome-text-editor  "apt / GPL-3" \
        "Or 'gedit' on Ubuntu < 22.04"
    chk_deb "GNOME Calendar"       gnome-calendar     "apt / GPL-3" ""
    chk_deb "GNOME Sudoku"         gnome-sudoku       "apt / GPL-3" ""
    chk_deb "GNOME To Do"          gnome-todo         "apt / GPL-3" \
        "'TODO App' from your list"

    # Google Keep — no native Linux app (confirmed)
    row note "Google Keep (KeepApp)" "Chrome PWA only" "Google ToS / Free" \
        "No official Linux app — Chrome → ⋮ → 'Install Keep…'"

    # ── 23. Conda Environment & Python Packages ──────────────────────────────
    section "🐍  CONDA ENVIRONMENT & PYTHON PACKAGES (idrm-mvp)"
    # This section checks whether the idrm-mvp conda environment exists and
    # whether all required Python packages are installed inside it.
    # The env is defined in environment.yml and src/backend/requirements.txt.
    #
    # If many items show "idrm-mvp env missing", run:
    #   conda env create -f environment.yml
    # then re-run this script.

    chk_conda_env "idrm-mvp"

    # Geospatial tier (conda-managed — checked via conda run)
    chk_pip "  shapely (conda-managed)"  shapely     "conda-forge / BSD-3" \
        "geometry engine; GEOS C lib bundled by conda-forge"

    # Web framework
    chk_pip "  fastapi"           fastapi           "pip / MIT"
    chk_pip "  uvicorn"           uvicorn           "pip / BSD-2"

    # Database ORM and drivers
    chk_pip "  sqlalchemy"        sqlalchemy        "pip / MIT"    "ORM; v2.x required"
    chk_pip "  asyncpg"           asyncpg           "pip / Apache-2" "async PG driver"
    chk_pip "  psycopg2"          psycopg2          "pip / LGPL"   "sync PG driver (Alembic)"

    # Geospatial PostGIS extension (pip-managed — pure Python)
    chk_pip "  geoalchemy2"       geoalchemy2       "pip / MIT"    \
        "PostGIS column types for SQLAlchemy — pure Python, pip-managed"

    # Migrations
    chk_pip "  alembic"           alembic           "pip / MIT"    "DB schema migrations"

    # Validation
    chk_pip "  pydantic"          pydantic          "pip / MIT"    "v2.x required"
    chk_pip "  pydantic-settings" pydantic-settings "pip / MIT"    ".env → typed config"
    chk_pip "  python-dotenv"     python-dotenv     "pip / BSD-3"

    # Auth
    chk_pip "  python-jose"       python-jose       "pip / MIT"    "JWT tokens"
    chk_pip "  passlib"           passlib           "pip / BSD-2"  "bcrypt password hashing"
    chk_pip "  python-multipart"  python-multipart  "pip / Apache-2" "form/file upload parsing"

    # HTTP client
    chk_pip "  httpx"             httpx             "pip / BSD-3"

    # Code quality
    chk_pip "  black"             black             "pip / MIT"    "code formatter"
    chk_pip "  flake8"            flake8            "pip / MIT"    "PEP-8 linter"
    chk_pip "  mypy"              mypy              "pip / MIT"    "static type checker"

    # Testing
    chk_pip "  pytest"            pytest            "pip / MIT"    "test runner"
    chk_pip "  pytest-asyncio"    pytest-asyncio    "pip / Apache-2" "async test support"

    # ── Project-internal: _lib.sh ─────────────────────────────────────────────
    # All four IDRM deploy scripts (staging, production, monolith, modular)
    # source scripts/_lib.sh which provides: have(), ok(), warn(), step(),
    # die(), log(), confirm(), os_family(), and REPO_ROOT.
    # Without this file every deploy script will fail immediately.
    section "📁  PROJECT-INTERNAL FILES"
    local _lib="${SCRIPT_DIR}/_lib.sh"
    if [[ -f "$_lib" ]]; then
        row ok "scripts/_lib.sh" "present" "project / MIT" \
            "shared bash library — sourced by all deploy scripts"
    else
        row miss "scripts/_lib.sh" "" "project / MIT" \
            "REQUIRED: all setup-*.sh scripts source this file"
    fi

    # ── 24. Services Dashboard ──────────────────────────────────────────────
    if $SHOW_SERVICES; then
        section "⚡  SERVICES HEALTH DASHBOARD"
        printf "  ${C_DIM}  %-28s %-12s %-12s${C_RST}\n" "SERVICE" "ACTIVE" "ENABLED"
        echo ""
        for svc in postgresql redis-server nginx docker grafana-server \
                   prometheus elasticsearch ssh; do
            local _act _enb _colour
            _act=$(systemctl is-active  "$svc" 2>/dev/null || echo "—")
            _enb=$(systemctl is-enabled "$svc" 2>/dev/null || echo "—")
            if [[ "$_act" == "active" ]]; then _colour="$C_OK"; else _colour="$C_MISS"; fi
            printf "  ${_colour}  %-28s %-12s %-12s${C_RST}\n" "$svc" "$_act" "$_enb"
        done
    fi

    # ── 24. Final Summary ───────────────────────────────────────────────────
    print_summary
}

# ──────────────────────────────────────────────────────────────────────────────
# print_summary
# ──────────────────────────────────────────────────────────────────────────────
print_summary() {
    local pct=0
    [[ $_TOTAL -gt 0 ]] && pct=$(( _INSTALLED * 100 / _TOTAL ))
    local filled=$(( pct / 5 ))
    local empty=$(( 20 - filled ))
    local bar=""
    local i
    for (( i=0; i<filled; i++ )); do bar+="█"; done
    for (( i=0; i<empty;  i++ )); do bar+="░"; done

    printf "\n${C_BOLD}${C_INFO}"
    echo   "  ╔═══════════════════════════════════════════════════════════╗"
    echo   "  ║  📋  SUMMARY                                              ║"
    echo   "  ╠═══════════════════════════════════════════════════════════╣"
    printf "  ║  Progress  : ${C_RST}[${C_OK}%s${C_RST}${C_DIM}%s${C_RST}${C_BOLD}${C_INFO}] %3d%%                              ║\n" \
           "$bar" "" "$pct"
    printf "  ║  ${C_OK}${SYM_OK}${C_INFO}  Installed : ${C_OK}%-5d${C_INFO}                                        ║\n" \
           "$_INSTALLED"
    printf "  ║  ${C_MISS}${SYM_MISS}${C_INFO}  Missing   : ${C_MISS}%-5d${C_INFO}                                        ║\n" \
           "$_MISSING"
    printf "  ║  ${C_WARN}${SYM_WARN}${C_INFO}  Warnings  : ${C_WARN}%-5d${C_INFO}                                        ║\n" \
           "$_WARNED"
    printf "  ║     Total    : %-5d                                        ║\n" \
           "$_TOTAL"
    echo   "  ╠═══════════════════════════════════════════════════════════╣"
    printf "  ║  Log → %-52s║\n" "$LOG_FILE"
    echo   "  ╚═══════════════════════════════════════════════════════════╝"
    printf "${C_RST}\n"

    [[ $_MISSING -gt 0 ]] && printf \
        "  ${C_DIM}Tip: run with '-q' to see only missing items.${C_RST}\n"
    [[ $SHOW_SERVICES == false ]] && printf \
        "  ${C_DIM}Tip: run with '-s' to show the live services dashboard.${C_RST}\n"
    echo ""

    {
        echo ""
        echo "────────────────────────────────────────────"
        echo "SUMMARY"
        printf "  Installed : %d / %d  (%d%%)\n" "$_INSTALLED" "$_TOTAL" "$pct"
        printf "  Missing   : %d\n" "$_MISSING"
        printf "  Warnings  : %d\n" "$_WARNED"
        echo "  Generated : $(date)"
        echo "────────────────────────────────────────────"
    } >> "$LOG_FILE"
}

# ──────────────────────────────────────────────────────────────────────────────
main "$@"
