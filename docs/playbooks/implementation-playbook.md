# Implementation Playbook

## What this document is

The ordered, step-by-step plan for building IDRM from an empty repository to
a running MVP, and from there into the FFP. Written so a complete novice can
follow it.

## The mental model

Three things must exist before any code runs:

- A **structure** that tells everyone where things go.
- A **contract** that tells every part of the system what the others promise.
- A **loop** that turns a change into a tested, deployed artefact.

This playbook builds all three in order.

## Part 1 - Structure

### Step 1.1 Install tools

    Node.js 20 or Bun 1.2+
    Python 3.11+ and Conda
    Java 17+ and Maven (for FFP services)
    Go 1.21+ (for FFP services)
    Docker (optional in MVP)

### Step 1.2 Create the folder skeleton

    apps/web apps/web-react apps/mobile
    packages/api-client packages/types packages/utils packages/config packages/ui
    services/monolith
    gateway/config gateway/docker
    shared/contracts/v1
    shared/libs/python shared/libs/java shared/libs/go shared/libs/ts
    shared/config
    infra/systemd infra/docker infra/k8s infra/terraform infra/ci
    tests/smoke tests/e2e
    docs/architecture docs/adr docs/playbooks docs/contributing
    .github/workflows .github/ISSUE_TEMPLATE
    .vscode .devcontainer

### Step 1.3 Add root orchestration files

    package.json       workspace manifest for Bun
    turbo.json         task graph for Turborepo
    Makefile           language-neutral command surface
    .gitignore         what to skip
    .gitattributes     LF line endings everywhere
    .editorconfig      consistent editor settings
    .bun-version       pinned Bun version

## Part 2 - The contract

### Step 2.1 Export the OpenAPI spec

The FastAPI monolith generates its own OpenAPI document. Write a small script
that dumps it:

    services/monolith/scripts/export_openapi.py

Run it:

    make contracts-export

Result: shared/contracts/v1/openapi.json

### Step 2.2 Generate the typed client

Install Kubb at the root. Add a kubb.config.ts. Run:

    make contracts-generate

Result: packages/api-client/src/gen/ populated with typed functions.

### Step 2.3 Wire the client into apps

In each app's package.json:

    "dependencies": {
      "@idrm/api-client": "workspace:*",
      "@idrm/types": "workspace:*",
      "@idrm/utils": "workspace:*"
    }

Run `bun install` at the root. The workspace links them.

## Part 3 - The loop

### Step 3.1 The Makefile

The root Makefile exposes a small, memorable set of targets:

    make install       install everything
    make dev           start all dev servers
    make test          run all tests
    make lint          lint everything
    make qa            lint + typecheck + test
    make contracts-sync export + validate + generate
    make help          list every target

Underneath, Make delegates to Turborepo for JS/TS and to native tools for
Python.

### Step 3.2 Tests

Three kinds of test, in three locations:

    services/monolith/tests/unit/         pure functions, no I/O
    services/monolith/tests/integration/  services plus a real test database
    services/monolith/tests/contract/     Schemathesis against the OpenAPI spec

Frontend tests live beside each app, in its own tests/ folder.

### Step 3.3 CI

Three workflows, path-scoped:

    .github/workflows/backend.yml    runs on services/ and shared/contracts/
    .github/workflows/frontend.yml   runs on apps/ and packages/
    .github/workflows/contract.yml   runs on shared/contracts/

A change to apps/web-react/ does not run Python tests. A change to
services/monolith/ does not build the mobile app.

## Part 4 - Phases of the build

### Phase A - Bare skeleton

- Folder structure.
- Root orchestration files.
- Empty placeholder READMEs.
- No code, no tests. Just the shape.

Success: `make tree` shows the full skeleton.

### Phase B - Monolith runs

- FastAPI app boots.
- Health endpoint responds.
- One module (say, users) has a working route.

Success: `curl http://localhost:8000/health` returns 200.

### Phase C - Contract round-trips

- Export the OpenAPI spec.
- Generate the typed client.
- Have one frontend call one endpoint through the client.

Success: the round trip works end-to-end.

### Phase D - Feature by feature

For each of the ten modules, repeat:

1. Write the migration.
2. Write the model, schema, repository, service, router.
3. Write the tests.
4. Write the frontend piece.
5. Run make qa.

### Phase E - Seed and verify

- Write an idempotent seed script.
- Run it against a fresh database.
- Confirm the app shows real data.

### Phase F - Deploy

- Write the systemd unit.
- Write the environment file.
- Deploy to a Linux host.
- Confirm the app runs and the database migrates.

## Part 5 - Growing into the FFP

The Strangler Fig pattern, applied one module at a time.

For each module to extract:

1. Copy the module from services/monolith/app/modules/ to
   services/<name>-service/.
2. Choose a language for the new service.
3. Point the new service at its own database schema.
4. Replace local function calls with HTTP calls.
5. Add a route in gateway/config/routes.yaml.
6. Run contract tests against the new service.
7. Once stable, remove the module from the monolith.

The four internal layers do not change. Only the deployment shape changes.

## Part 6 - The everyday workflow

    git checkout -b feature/short-name
    # make changes
    make qa
    git add .
    git commit -m "feat: short description"
    git push -u origin feature/short-name
    # open a pull request

If make qa fails, fix the failure. Do not push a red build.

## Summary

Three things in order: structure, contract, loop. Then feature by feature.
Then deploy. Then extract into services. The tree never changes between
phases. Only the contents grow.

## Related

- Makefile playbook: ./makefile-playbook.md
- Migration mapping: ./migration-mapping.md
- Layered architecture: ../architecture/layered-architecture.md
