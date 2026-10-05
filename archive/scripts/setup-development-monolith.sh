#!/usr/bin/env bash
# =============================================================================
# scripts/setup-development-monolith.sh
# PURPOSE: Bootstrap a LOCAL development environment for the IDRM modular monolith.
#          Idempotent — re-running skips anything already in place.
#
# STEPS (each one checks "is this already done?" before acting):
#   1. Verify prerequisites (bun, conda, psql, redis-cli)
#   2. Create the 'idrm-mvp' conda env (Python 3.11)         — skip if it exists
#   3. pip install backend Python deps                       — skip if file empty
#   4. bun install in each JS app that has a package.json    — skip if not scaffolded
#   5. Ensure a .env exists                                  — never overwrite yours
#   6. Create DB role + database, enable extensions, load schema + seed (all idempotent SQL)
#
# USAGE:   ./scripts/setup-development-monolith.sh
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_lib.sh"
cd "$REPO_ROOT"

# These can be overridden from the environment, e.g.  DB_NAME=foo ./setup-development-monolith.sh
CONDA_ENV="${CONDA_ENV:-idrm-mvp}"
DB_NAME="${DB_NAME:-idrm_db}"
DB_USER="${DB_USER:-idrm_user}"
DB_PASS="${DB_PASS:-idrm_secure_password_2024}"

# 1 -------------------------------------------------------------------------
verify_prereqs() {
  step "1/6 Verifying prerequisites"
  local missing=0
  for c in bun conda psql redis-cli; do
    if have "$c"; then ok "$c found"; else err "$c missing"; missing=1; fi
  done
  [ "$missing" -eq 0 ] || die "Missing tools — run ./scripts/setup-prerequisites.sh first."
}

# 2 -------------------------------------------------------------------------
setup_conda() {
  step "2/6 Conda env '$CONDA_ENV' (Python 3.11)"
  # 'conda env list' lists existing envs; if ours is there, do nothing.
  if conda env list | grep -qE "^[* ]*${CONDA_ENV}[[:space:]]"; then
    ok "Env '$CONDA_ENV' already exists — skipping create"
  else
    log "Creating conda env '$CONDA_ENV'…"
    conda create -y -n "$CONDA_ENV" python=3.11
    ok "Created '$CONDA_ENV'"
  fi
}

# 3 -------------------------------------------------------------------------
setup_python_deps() {
  step "3/6 Python dependencies"
  local req="src/backend/requirements.txt"
  if [ ! -s "$req" ]; then warn "$req is empty — skipping pip install"; return; fi
  # 'conda run -n <env> <cmd>' runs inside the env WITHOUT needing 'conda activate'
  # (activate doesn't work reliably inside non-interactive scripts).
  conda run -n "$CONDA_ENV" python -m pip install --upgrade pip
  conda run -n "$CONDA_ENV" pip install -r "$req"
  ok "Python deps installed into '$CONDA_ENV'"
}

# 4 -------------------------------------------------------------------------
setup_js_deps() {
  step "4/6 JavaScript dependencies (bun)"
  local dirs=("src/backend/api-gateway" "src/frontend/web-html" "src/frontend/web-react" "src/frontend/mobile-expo")
  for d in "${dirs[@]}"; do
    if [ -f "$d/package.json" ]; then
      log "bun install → $d"
      ( cd "$d" && bun install )   # subshell so our working dir doesn't change
      ok "$d dependencies installed"
    else
      warn "$d has no package.json yet — skipping (not scaffolded)"
    fi
  done
}

# 5 -------------------------------------------------------------------------
setup_env() {
  step "5/6 Environment file (.env)"
  if [ -s ".env" ]; then
    ok ".env already present — leaving it untouched (your secrets are safe)"
  else
    warn ".env is empty/missing. A committed development .env ships with this repo;"
    warn "if you removed it, copy the defaults from start-here/COMPLETE-SETUP-GUIDE.md."
  fi
}

# 6 -------------------------------------------------------------------------
setup_database() {
  step "6/6 Database (role · database · extensions · schema · seed)"
  have psql || { warn "psql missing — skipping DB setup"; return; }

  # Is a server actually running and reachable? If not, guide the user and bail gracefully.
  if ! pg_isready -q 2>/dev/null; then
    warn "PostgreSQL server not reachable. Start it first, e.g.:"
    warn "   Linux: sudo service postgresql start    macOS: brew services start postgresql@16"
    warn "Then re-run this script (it will pick up where it left off)."
    return
  fi

  # Create the login role if it doesn't already exist (idempotent).
  if psql -tAc "SELECT 1 FROM pg_roles WHERE rolname='${DB_USER}'" postgres 2>/dev/null | grep -q 1; then
    ok "Role '${DB_USER}' already exists"
  else
    log "Creating role '${DB_USER}'…"
    psql postgres -c "CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';" \
      || warn "Couldn't create role (need a superuser?). Create it manually, then re-run."
  fi

  # Create the database if it doesn't already exist (idempotent).
  if psql -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" postgres 2>/dev/null | grep -q 1; then
    ok "Database '${DB_NAME}' already exists"
  else
    log "Creating database '${DB_NAME}'…"
    createdb -O "${DB_USER}" "${DB_NAME}" 2>/dev/null \
      || psql postgres -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};" \
      || warn "Couldn't create database — create it manually, then re-run."
  fi

  # Apply init SQL. These files use CREATE EXTENSION/TABLE IF NOT EXISTS and ON CONFLICT,
  # so applying them repeatedly is SAFE (won't duplicate or error on existing objects).
  local f
  for f in database/init/01-extensions.sql database/init/02-schema.sql database/init/03-seed-data.sql; do
    if [ -f "$f" ]; then
      log "Applying $f"
      if psql -v ON_ERROR_STOP=1 -d "${DB_NAME}" -f "$f" >/dev/null 2>&1; then ok "Applied $f"
      else warn "Issue applying $f — re-run after fixing (continuing for now)"; fi
    fi
  done
}

main() {
  step "IDRM development setup (modular monolith) — idempotent"
  verify_prereqs
  setup_conda
  setup_python_deps
  setup_js_deps
  setup_env
  setup_database

  step "✅ Setup complete — start the stack in 5 terminals"
  cat <<'NEXT'
  Terminal 1 — Backend (FastAPI monolith):
      cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000
  Terminal 2 — API Gateway (Bun):
      cd src/backend/api-gateway && bun run dev          # HTTP :3000 · WebSocket :3001
  Terminal 3 — HTML/Tailwind web (citizens):
      cd src/frontend/web-html && bun run dev            # :5173
  Terminal 4 — React SPA (admin):
      cd src/frontend/web-react && bun run dev           # :5174
  Terminal 5 — React Native (field workers · Post-MVP):
      cd src/frontend/mobile-expo && npx expo start

  Tip: `make dev` (see the Makefile) prints these too.
NEXT
}
main "$@"
