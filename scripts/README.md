# Root Scripts

Shell scripts that operate on the entire monorepo: bootstrap, lint, release.
Scripts that affect one service live next to that service.

## What is inside

| Script | Purpose | When to run |
|---|---|---|
| bootstrap.sh | One-command environment setup: install tools, dependencies, run migrations, seed data, sync contracts | Once, after cloning |
| lint-all.sh  | Run every linter in the monorepo | Before opening a PR |
| release.sh   | Tag a release and push it to GitHub | When shipping a version |

## How to run them

    bash scripts/bootstrap.sh     first-time setup
    bash scripts/lint-all.sh      lint everything
    bash scripts/release.sh       cut a release

Or via the root Makefile:

    make setup       equivalent to scripts/bootstrap.sh
    make lint        equivalent to scripts/lint-all.sh

## Rules

1. Every script starts with the shebang line and set -euo pipefail.
2. Every script is idempotent, safe to run twice.
3. Every script that reads paths uses the repository root as its anchor.
