#!/usr/bin/env bash
# =============================================================================
# scripts/_lib.sh  —  Shared helpers used by every IDRM setup script.
#
# ROOKIE NOTES
#   • "Sourcing" = loading these functions into another script with:
#         source "$(dirname "$0")/_lib.sh"
#     so we write the logging/checks ONCE (DRY) instead of copy-pasting.
#   • Everything here is built to be IDEMPOTENT: running a script twice does the
#     same thing as running it once — it never re-does work that's already done.
#   • You normally don't run this file directly; the other scripts use it.
# =============================================================================

# Bash safety switches (explained):
#   -e          : stop the script the moment any command fails
#   -u          : treat the use of an undefined variable as an error
#   -o pipefail : if any command in a "a | b | c" pipe fails, the whole pipe fails
set -euo pipefail

# ---- Pretty, color-aware logging -------------------------------------------
# We only emit color codes when writing to a real terminal ([ -t 1 ]). That keeps
# log files clean when output is redirected (e.g. ./setup.sh > setup.log).
if [ -t 1 ]; then
  C_RESET="\033[0m"; C_INFO="\033[0;36m"; C_OK="\033[0;32m"
  C_WARN="\033[0;33m"; C_ERR="\033[0;31m"; C_STEP="\033[1;35m"
else
  C_RESET=""; C_INFO=""; C_OK=""; C_WARN=""; C_ERR=""; C_STEP=""
fi
log()  { printf "%b\n" "${C_INFO}•${C_RESET} $*"; }                 # neutral info
ok()   { printf "%b\n" "${C_OK}✓${C_RESET} $*"; }                  # success
warn() { printf "%b\n" "${C_WARN}!${C_RESET} $*" >&2; }            # warning (to stderr)
err()  { printf "%b\n" "${C_ERR}✗${C_RESET} $*" >&2; }            # error   (to stderr)
step() { printf "\n%b\n" "${C_STEP}▶ $*${C_RESET}"; }              # section header
die()  { err "$*"; exit 1; }                                       # print error + stop

# ---- Tiny utilities ---------------------------------------------------------

# have <command>  → true if the command exists on PATH (our main idempotency check)
have() { command -v "$1" >/dev/null 2>&1; }

# os_family → debian | fedora | macos | unknown  (so we pick the right installer)
os_family() {
  case "$(uname -s)" in
    Linux*)  if have apt-get; then echo "debian"; elif have dnf; then echo "fedora"; else echo "linux"; fi ;;
    Darwin*) echo "macos" ;;
    *)       echo "unknown" ;;
  esac
}

# confirm "Question?"  → returns success only if the user types y/Y.
# Honors a non-interactive override: set ASSUME_YES=1 to skip all prompts (useful in CI).
confirm() {
  if [ "${ASSUME_YES:-0}" = "1" ]; then return 0; fi
  local reply
  printf "%b" "${C_WARN}?${C_RESET} $* [y/N] " >&2
  read -r reply || true
  [[ "$reply" =~ ^[Yy]$ ]]
}

# ensure_env FILE KEY VALUE  → add 'KEY=VALUE' to FILE only if KEY isn't already there.
# Idempotent: re-running never duplicates or overwrites an existing key.
ensure_env() {
  local file="$1" key="$2" value="$3"
  touch "$file"
  if grep -qE "^${key}=" "$file" 2>/dev/null; then return 0; fi
  printf "%s=%s\n" "$key" "$value" >> "$file"
}

# REPO_ROOT = the project root (one level above scripts/). Works no matter the
# directory you launch the script from.
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export REPO_ROOT
