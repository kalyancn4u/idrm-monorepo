#!/usr/bin/env bash
set -euo pipefail
read -p "Version tag (e.g. v0.1.0): " tag
git tag -a "$tag" -m "Release $tag"
git push origin "$tag"
