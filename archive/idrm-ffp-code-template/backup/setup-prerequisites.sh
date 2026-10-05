#!/usr/bin/env bash
# =============================================================================
# scripts/setup-prerequisites.sh
# PURPOSE: Make sure every tool IDRM needs is installed — installing ONLY the
#          ones that are missing. Safe to run any number of times (idempotent).
#
# Tools: Bun (JS runtime) · Miniconda (Python env) · PostgreSQL 16 + PostGIS 3.4 · Redis 7.2+
#
# HOW IT STAYS IDEMPOTENT: before installing anything we check `have <tool>`.
# If the tool is already there, we print its version and skip it.
#
# USAGE:   ./scripts/setup-prerequisites.sh
#          ASSUME_YES=1 ./scripts/setup-prerequisites.sh   # never prompt (CI)
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_lib.sh"

OS="$(os_family)"
# Use sudo only when we're not root AND sudo exists (so the script works in containers too).
SUDO=""; if [ "$(id -u)" -ne 0 ] && have sudo; then SUDO="sudo"; fi

# pkg_install <debian-pkg> <fedora-pkg> <brew-pkg> — install a package per-OS.
pkg_install() {
  case "$OS" in
    debian) $SUDO apt-get update -y && $SUDO apt-get install -y "$1" ;;
    fedora) $SUDO dnf install -y "$2" ;;
    macos)  have brew || die "Homebrew not found — install from https://brew.sh then re-run."; brew install "$3" ;;
    *)      return 1 ;;
  esac
}

# ---- Bun --------------------------------------------------------------------
ensure_bun() {
  if have bun; then ok "Bun already installed ($(bun --version))"; return; fi
  step "Installing Bun (JavaScript runtime — replaces Node.js/npm)"
  curl -fsSL https://bun.sh/install | bash
  # Make bun usable in THIS shell right away (the installer edits ~/.bashrc for future shells).
  export BUN_INSTALL="${BUN_INSTALL:-$HOME/.bun}"; export PATH="$BUN_INSTALL/bin:$PATH"
  have bun && ok "Bun installed ($(bun --version))" \
           || warn "Bun installed — open a new terminal (or run: source ~/.bashrc) to use it."
}

# ---- Miniconda --------------------------------------------------------------
ensure_conda() {
  if have conda; then ok "Conda already installed ($(conda --version))"; return; fi
  local mc="$HOME/miniconda3"
  if [ -d "$mc" ]; then
    warn "Found $mc but 'conda' isn't on PATH. Add it:  export PATH=\"$mc/bin:\$PATH\""; return
  fi
  step "Installing Miniconda (Python environment manager — replaces venv/pip)"
  local url
  case "$(uname -s)-$(uname -m)" in
    Linux-x86_64)  url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh" ;;
    Linux-aarch64) url="https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-aarch64.sh" ;;
    Darwin-arm64)  url="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh" ;;
    Darwin-x86_64) url="https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-x86_64.sh" ;;
    *) warn "Unsupported arch for auto-install — install Miniconda manually: https://docs.conda.io/projects/miniconda/"; return ;;
  esac
  curl -fsSL "$url" -o /tmp/miniconda.sh
  bash /tmp/miniconda.sh -b -p "$mc"   # -b = batch/no-prompts, -p = install path
  rm -f /tmp/miniconda.sh
  export PATH="$mc/bin:$PATH"
  have conda && ok "Miniconda installed ($(conda --version))" \
             || warn "Miniconda installed — open a new terminal to use 'conda'."
}

# ---- PostgreSQL + PostGIS ---------------------------------------------------
ensure_postgres() {
  if have psql; then
    ok "PostgreSQL client already installed ($(psql --version))"
  else
    step "Installing PostgreSQL + PostGIS"
    case "$OS" in
      debian) $SUDO apt-get update -y
              $SUDO apt-get install -y postgresql postgresql-contrib postgis postgresql-postgis \
                || warn "For exactly PostgreSQL 16 + PostGIS 3.4, add the PGDG apt repo: https://wiki.postgresql.org/wiki/Apt" ;;
      fedora) $SUDO dnf install -y postgresql-server postgresql-contrib postgis ;;
      macos)  brew install postgresql@16 postgis ;;
      *)      warn "Install PostgreSQL 16 + PostGIS 3.4 manually for your OS."; return ;;
    esac
    ok "PostgreSQL installed"
  fi
  log "Verify PostGIS later with:  psql -d idrm_db -c \"SELECT postgis_full_version();\""
}

# ---- Redis ------------------------------------------------------------------
ensure_redis() {
  if have redis-cli; then ok "Redis already installed ($(redis-cli --version))"; return; fi
  step "Installing Redis 7.2+ (cache, sessions, rate limiting, pub/sub)"
  case "$OS" in
    debian) pkg_install redis-server "" "" ;;
    fedora) $SUDO dnf install -y redis ;;
    macos)  brew install redis ;;
    *)      warn "Install Redis 7.2+ manually for your OS."; return ;;
  esac
  ok "Redis installed"
}

main() {
  step "IDRM prerequisites (OS family: ${OS}) — only missing tools are installed"
  [ "$OS" = "unknown" ] && warn "Unrecognized OS — auto-install may not work; follow start-here/COMPLETE-SETUP-GUIDE.md."

  ensure_bun
  ensure_conda
  ensure_postgres
  ensure_redis

  step "Summary"
  have bun       && ok "Bun         $(bun --version)"                        || warn "Bun: not on PATH (open a new terminal?)"
  have conda     && ok "Conda       $(conda --version | awk '{print $2}')"   || warn "Conda: not on PATH (open a new terminal?)"
  have psql      && ok "PostgreSQL  $(psql --version | awk '{print $3}')"    || warn "PostgreSQL: missing"
  have redis-cli && ok "Redis       $(redis-cli --version | awk '{print $2}')" || warn "Redis: missing"

  echo
  ok "Prerequisites check complete. Next:  ./scripts/setup-development-monolith.sh"
}
main "$@"
