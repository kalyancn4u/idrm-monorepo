#!/usr/bin/env bash
# Build a Marp slide deck from a folder of Markdown chapters. GENERIC over SRC_DIR.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# What to build (all overridable via env):
SRC_REL="${SRC_DIR:-docs/walkthrough}"                # folder of NN-*.md chapters
case "$SRC_REL" in /*) SRC_DIR="$SRC_REL" ;; *) SRC_DIR="$REPO_ROOT/$SRC_REL" ;; esac
OUT_DIR="${OUT_DIR:-$SRC_DIR/slides}"                 # default: slides/ INSIDE the source folder
FOOTER="${FOOTER:-IDRM MVP — Code Walk-Through}"      # slide footer text
COMBINED="${COMBINED:-walkthrough-full}"              # basename of the all-chapters deck
THEME="${THEME:-$SRC_DIR/assets/marp-theme.css}"
CONFIG="${MARP_CONFIG:-$REPO_ROOT/.marprc.yml}"
PDF=""
[ "${1:-}" = "--pdf" ] && PDF="1"
[ -d "$SRC_DIR" ] || { echo "Source folder not found: $SRC_DIR" >&2; exit 1; }

# Default to npx; CI (or anyone with Marp installed) sets MARP_CMD=marp.
MARP_CMD="${MARP_CMD:-npx --yes @marp-team/marp-cli@latest}"
marp_bin="${MARP_CMD%% *}"
command -v "$marp_bin" >/dev/null 2>&1 || { echo "Install Node.js, or set MARP_CMD=marp" >&2; exit 1; }

mkdir -p "$OUT_DIR"
# Marp keeps relative <img> paths (it does NOT inline them) -> copy assets next to the decks.
if compgen -G "$SRC_DIR/assets/"'*.svg' > /dev/null 2>&1; then
  mkdir -p "$OUT_DIR/assets"; cp "$SRC_DIR/assets/"*.svg "$OUT_DIR/assets/" 2>/dev/null || true
fi

FRONT_MATTER=$'---\nmarp: true\ntheme: walkthrough\npaginate: true\nfooter: \''"$FOOTER"$'\'\n---\n\n'

mapfile -t CHAPTERS < <(find "$SRC_DIR" -maxdepth 1 -name '[0-9][0-9]-*.md' | sort)
[ "${#CHAPTERS[@]}" -gt 0 ] || { echo "No chapters (NN-*.md) in $SRC_DIR" >&2; exit 1; }

TEMP_FILES=()
cleanup() { for t in "${TEMP_FILES[@]:-}"; do [ -f "$t" ] && rm -f "$t"; done; }
trap cleanup EXIT

marp_build() {  # $1 in.md  $2 out  $3 optional --pdf
  # shellcheck disable=SC2086
  $MARP_CMD "$1" -o "$2" -c "$CONFIG" --no-stdin --allow-local-files --theme "$THEME" ${3:-}
}

# one deck per chapter
for ch in "${CHAPTERS[@]}"; do
  base="$(basename "$ch" .md)"; tmp="$SRC_DIR/_build_${base}.md"; TEMP_FILES+=("$tmp")
  printf '%s' "$FRONT_MATTER" > "$tmp"; cat "$ch" >> "$tmp"
  echo "Building $(basename "$ch")"; marp_build "$tmp" "$OUT_DIR/${base}.html"
  [ -n "$PDF" ] && marp_build "$tmp" "$OUT_DIR/${base}.pdf" "--pdf"
done

# one combined deck
combined="$SRC_DIR/_build_${COMBINED}.md"; TEMP_FILES+=("$combined")
printf '%s' "$FRONT_MATTER" > "$combined"; first=1
for ch in "${CHAPTERS[@]}"; do
  [ "$first" -eq 1 ] || printf '\n\n---\n\n' >> "$combined"; cat "$ch" >> "$combined"; first=0
done
marp_build "$combined" "$OUT_DIR/${COMBINED}.html"
[ -n "$PDF" ] && marp_build "$combined" "$OUT_DIR/${COMBINED}.pdf" "--pdf"
echo "Done -> $OUT_DIR (open ${COMBINED}.html)"
