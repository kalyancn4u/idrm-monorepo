#!/usr/bin/env bash
set -euo pipefail
echo "Bootstrapping idrm-monorepo..."
make check-tools
make install
make db-migrate || true
make db-seed    || true
make contracts-sync || true
echo "Bootstrap complete. Run 'make dev'."
