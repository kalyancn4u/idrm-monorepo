#!/usr/bin/env bash
# =============================================================================
# scripts/setup-production.sh
# PURPOSE: Deploy IDRM to PRODUCTION via Docker Compose — with safety guards so
#          you can't accidentally ship dev defaults. Idempotent.
#
# SAFETY (this script refuses to run if):
#   • .env.production is missing
#   • it still contains the dev default DB password or JWT secret
#   • you don't explicitly confirm (set ASSUME_YES=1 for unattended CI deploys)
#
# USAGE:   ./scripts/setup-production.sh
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_lib.sh"
cd "$REPO_ROOT"

COMPOSE_FILE="infra/docker/full-stack.yml"
ENV_FILE=".env.production"

dc() {
  if docker compose version >/dev/null 2>&1; then docker compose "$@";
  elif have docker-compose; then docker-compose "$@";
  else die "Docker Compose not found."; fi
}

# ---- Pre-flight safety checks ----------------------------------------------
step "Pre-flight safety checks"
have docker || die "Docker is required on the production host."
[ -s "$ENV_FILE" ] || die "Missing $ENV_FILE — create it with REAL production secrets (and NEVER commit it)."

# Block known dev defaults from ever reaching production.
if grep -q "idrm_secure_password_2024" "$ENV_FILE"; then
  die "$ENV_FILE still has the dev DB password — set a strong, unique one."
fi
if grep -q "change-in-production" "$ENV_FILE"; then
  die "$ENV_FILE still has the placeholder JWT secret — generate a real one (e.g. openssl rand -hex 32)."
fi
ok "Secrets look non-default"

confirm "Deploy IDRM to PRODUCTION now using $ENV_FILE + $COMPOSE_FILE?" || die "Aborted by user."

# ---- Deploy ----------------------------------------------------------------
step "1/3 Data layer"
dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" up -d --wait postgres redis \
  || die "Data layer failed health checks — aborting before touching app services."
ok "Database + Redis healthy"

step "2/3 Application services"
dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" --profile app build \
  || die "App images failed to build — fix the Dockerfiles, then re-run."
dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" --profile app up -d --wait \
  || warn "Some app services are not healthy yet — inspect: docker compose -f $COMPOSE_FILE logs"

step "3/3 Database migrations"
dc --env-file "$ENV_FILE" -f "$COMPOSE_FILE" exec -T backend alembic upgrade head \
  || warn "Migrations not applied (backend/alembic not ready) — run them once available."

ok "Production deploy complete."
warn "Before going live, confirm: TLS via NGINX, off-host backups, firewall rules, and"
warn "monitoring (Prometheus + Grafana) — see start-here/COMPLETE-DevSecOps-GUIDE.md & COMPLETE-MONITORING-GUIDE.md."
