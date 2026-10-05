#!/usr/bin/env bash
# =============================================================================
# scripts/setup-staging.sh
# PURPOSE: Bring IDRM up on a STAGING host using Docker Compose. Idempotent —
#          `docker compose up -d` only recreates what actually changed.
#
# STEPS:
#   1. Ensure a .env.staging exists (copied from the example if needed)
#   2. Start the data layer (postgres + redis) and wait until healthy
#   3. Build + start the app services (profile "app") — if their Dockerfiles exist
#   4. Apply database migrations (alembic) — if the backend is running
#
# USAGE:   ./scripts/setup-staging.sh
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_lib.sh"
cd "$REPO_ROOT"

COMPOSE_FILE="infra/docker/full-stack.yml"
ENV_FILE=".env.staging"

# Docker Compose ships either as "docker compose" (plugin) or "docker-compose" (legacy).
dc() {
  if docker compose version >/dev/null 2>&1; then docker compose "$@";
  elif have docker-compose; then docker-compose "$@";
  else die "Docker Compose not found — install Docker Desktop or the compose plugin."; fi
}

have docker || die "Docker is not installed — see start-here/COMPLETE-DevSecOps-GUIDE.md."

# 1 --------------------------------------------------------------------------
step "1/4 Staging environment file"
if [ -s "$ENV_FILE" ]; then
  ok "$ENV_FILE present — leaving it untouched"
elif [ -f ".env.staging.example" ]; then
  cp ".env.staging.example" "$ENV_FILE"; ok "Created $ENV_FILE from example — edit it with real staging values"
else
  warn "No $ENV_FILE and no example — falling back to .env defaults (fine for a smoke test, not real staging)"
  ENV_FILE=".env"
fi

# 2 --------------------------------------------------------------------------
step "2/4 Data layer (postgres + redis)"
# --wait blocks until healthchecks pass (or times out). Idempotent.
dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --wait postgres redis \
  || warn "Healthcheck wait timed out — check: dc -f $COMPOSE_FILE logs postgres redis"
ok "Database + Redis running"

# 3 --------------------------------------------------------------------------
step "3/4 Application services (profile: app)"
if dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" --profile app build >/dev/null 2>&1; then
  dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" --profile app up -d
  ok "App services (backend, gateway, nginx) up"
else
  warn "App images can't build yet (Dockerfiles arrive with the backend/gateway code)."
  warn "Data layer is up, so you can run the apps locally against it in the meantime."
fi

# 4 --------------------------------------------------------------------------
step "4/4 Database migrations"
if dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" ps backend 2>/dev/null | grep -q "backend"; then
  # alembic upgrade head is idempotent — it only applies migrations not yet recorded.
  dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend alembic upgrade head \
    || warn "Could not run migrations (alembic not wired up yet) — skip for now."
else
  log "Backend not running — skipping migrations (the SQL in database/init already seeds a fresh DB)."
fi

ok "Staging bring-up complete.  Status:  docker compose -f $COMPOSE_FILE ps"
