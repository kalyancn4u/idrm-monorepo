#!/usr/bin/env bash
# =============================================================================
# scripts/setup-development-modular.sh
# PURPOSE: Dev setup for the "modular" view of the backend.
#
# PLEASE READ (so this isn't confusing):
#   IDRM's MVP is a *modular monolith* — ONE FastAPI process on port 8000 with
#   clean internal module boundaries (auth, services, geo, analytics,
#   notifications). There is NO separate per-module deployment yet. So today this
#   "modular" setup is intentionally IDENTICAL to the monolith setup.
#
#   It exists as a clearly-named placeholder for the FUTURE microservices split
#   described in archive/MIGRATION-TO-MICROSERVICES-v3.md. When modules are
#   actually extracted into separate services, add their extra steps here.
#
#   To avoid duplicated logic (DRY), this script delegates to the monolith setup.
#
# USAGE:   ./scripts/setup-development-modular.sh
# =============================================================================
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/_lib.sh"

warn "Modular monolith: 'modular' dev setup currently == monolith setup (single FastAPI process on :8000)."
log  "Delegating to setup-development-monolith.sh …"
# 'exec' replaces this process with the monolith script, passing along any arguments.
exec "${SCRIPT_DIR}/setup-development-monolith.sh" "$@"
