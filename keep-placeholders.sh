#!/usr/bin/env bash
# =====================================================================
# keep-placeholders.sh
# Restores empty placeholder directories as tracked .gitkeep files.
# Only touches directories that have NO tracked files.
# Safe to re-run.
# =====================================================================
set -u
[ -d "apps" ] || { echo "Run from idrm-monorepo root."; exit 1; }

created=0; skipped=0; already=0

keep() {
    local d="$1"
    [ -d "$d" ] || mkdir -p "$d"
    if [ -f "$d/.gitkeep" ]; then
        already=$((already + 1)); return
    fi
    local tracked
    tracked=$(git ls-files "$d" 2>/dev/null | wc -l | tr -d ' ')
    if [ "$tracked" -gt 0 ]; then
        skipped=$((skipped + 1)); return
    fi
    : > "$d/.gitkeep"
    echo "  + $d/.gitkeep"
    created=$((created + 1))
}

echo "Restoring placeholder directories..."
echo ""

# --- Root FFP placeholders ---
keep gateway/docker
keep infra/ci
keep infra/k8s
keep infra/terraform
keep packages/api-client/src/gen
keep tests/e2e

# --- Frontend placeholders ---
keep apps/web-react/src
keep apps/mobile/assets

# --- BFF placeholders (future FFP) ---
keep services/bff-web
keep services/bff-mobile

# --- Archive: idrm-ffp-code-template (from git clean output) ---
T=archive/idrm-ffp-code-template
keep $T/configs
keep $T/docs/deployment
keep $T/dsml/data
keep $T/dsml/experiments
keep $T/dsml/mlops
keep $T/dsml/models
keep $T/dsml/pipelines
keep $T/dsml/training
keep $T/dsml/projects/churn-prediction
keep $T/dsml/projects/misuse-anomaly-detection
keep $T/dsml/projects/recommendation-system/config
keep $T/dsml/projects/recommendation-system/data
keep $T/dsml/projects/recommendation-system/models
keep $T/dsml/projects/recommendation-system/reports
keep $T/dsml/projects/recommendation-system/src
keep $T/infra/k8s
keep $T/infra/terraform
keep $T/scripts
keep $T/src/backend/contracts
keep $T/src/backend/todo-later
keep $T/src/frontend/mobile-expo/components
keep $T/src/frontend/mobile-expo/navigation
keep $T/src/frontend/mobile-expo/screens
keep $T/src/frontend/web-html/public/images/icons
keep $T/src/frontend/web-html/src/assets
keep $T/src/frontend/web-html/src/js/modules
keep $T/src/frontend/web-html/src/js/ui
keep $T/src/frontend/web-html/src/js/utils
keep $T/src/frontend/web-react/public
keep $T/tests

echo ""
echo "----------------------------------------"
printf "  Created:  %d\n" "$created"
printf "  Already:  %d  (had .gitkeep)\n" "$already"
printf "  Skipped:  %d  (had tracked files)\n" "$skipped"
echo "----------------------------------------"
echo ""

if [ "$created" -eq 0 ]; then
    echo "Nothing to do. All placeholders present or tracked."
else
    echo "Next steps:"
    echo "  git add ."
    echo "  git status"
    echo "  git commit -m 'chore: restore placeholder directories with .gitkeep'"
    echo "  git push"
fi

