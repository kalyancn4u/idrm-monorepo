#!/usr/bin/env bash
set -u
[ -d "shared" ] || { echo "Run from the idrm-monorepo root."; exit 1; }
w() { local p="$1"; mkdir -p "$(dirname "$p")"; cat > "$p"; echo "wrote $p"; }

w shared/contracts/README.md <<'ENDREADME'
# Shared Contracts

The single source of truth for the IDRM API surface.

A contract is a machine-readable description of every HTTP endpoint: what
it accepts, what it returns, which errors it can produce. In this monorepo,
contracts are written in OpenAPI 3.1.

## Why contracts matter

Without a contract, every frontend writes its own HTTP calls, guesses at
the data shape, and drifts out of sync with the backend. With a contract:

- The backend is tested against it.
- A typed API client is generated from it (packages/api-client/).
- Every frontend that consumes the client fails to build when the contract
  changes in a breaking way.

## What is inside

    shared/contracts/
      README.md              this file
      v1/
        openapi.json         the exported OpenAPI spec

In the FFP, the spec may be split per domain (users.yaml, incidents.yaml,
and so on). In the MVP a single file is enough.

## How the spec is produced

The FastAPI monolith generates the OpenAPI document from its own code:

    make contracts-export      writes shared/contracts/v1/openapi.json

## How the spec is used

    make contracts-validate    lint the spec
    make contracts-generate    regenerate the typed client
    make contracts-sync        all three steps in order

## Rules

1. Never hand-edit openapi.json. It is generated from the code.
2. Never remove a field without a version bump. Frontends depend on it.
3. Commit the generated client alongside the contract change.

## Next steps

- How the client is generated: ../../docs/architecture/typed-api-clients.md
- How contracts are tested: ../../docs/architecture/contract-testing.md
ENDREADME

w shared/libs/README.md <<'ENDREADME'
# Shared Libraries (per language)

Code that more than one service needs, written once and imported everywhere.

Unlike packages/, which holds TypeScript libraries consumed by frontends,
this folder holds shared code for backend languages.

## What is inside

| Folder | Language | Consumed by |
|---|---|---|
| python/ | Python package | Python services |
| java/   | Maven module  | Java services |
| go/     | Go module     | Go services |
| ts/     | npm package   | TypeScript services |

All four are placeholders in the MVP. They are populated the first time two
services in the same language need the same helper.

## Why one folder per language

Sharing code across languages is nearly impossible. A Python module cannot
be imported by a Go service. Keeping one folder per language makes it
obvious where a new shared helper belongs.

## Rules

1. No business logic. Infrastructure only: logging, tracing, error types,
   HTTP clients, auth helpers.
2. Versioned. Each library gets a version; consumers pin it.
3. Tested. Same standards as any other code in the monorepo.

## When to create a shared library

Do not create one in advance. Create one the second time two services need
the same code. The first time, copy. The second time, extract.
ENDREADME

w shared/config/README.md <<'ENDREADME'
# Shared Config

Configuration shared across services: environment templates, feature flags,
and constants that must stay in sync.

## What belongs here

- Example environment files (env.example) that new services copy.
- Feature flag definitions used by more than one service.
- Cross-service constants (standard header names, error codes).

## What does not belong here

- Secrets. Those live in environment variables on the server, never in the
  repository.
- Service-specific config. Keep it inside the service.
- Build config. That lives in packages/config/.

## Status in the MVP

Placeholder. Populate when a second service needs the same config that the
monolith already uses.
ENDREADME

w tests/README.md <<'ENDREADME'
# Cross-Service Tests

Tests that exercise more than one part of the system at once.

Most tests live next to the code they test, inside services/monolith/tests/,
inside apps/web-react/tests/, and so on. This folder is for the small number
of tests that only make sense when the whole system is running.

## What is inside

| Folder | Purpose | Runs against |
|---|---|---|
| smoke/ | Fast checks that the stack is alive | A running backend |
| e2e/   | End-to-end user journeys across services | Full running stack |

## When to put a test here

- The test needs two or more services running.
- The test simulates a complete user journey (browser, API, database).
- The test verifies that a contract between two services still holds.

Everything else belongs inside the service or app it tests.

## How to run

    # from the repository root
    make test-e2e

The command relies on a running backend. Start it first with make dev-backend
in another terminal.

## Next steps

- Testing strategy: ../docs/mvp/70-quality-test-strategy.md
- Contract tests: ../docs/architecture/contract-testing.md
ENDREADME

w scripts/README.md <<'ENDREADME'
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
ENDREADME

echo "Script 4 done."
