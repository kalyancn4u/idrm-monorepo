#!/usr/bin/env bash
# expand-readmes.sh - replace terse READMEs with novice-friendly ones
# Run from the idrm-monorepo root folder.

set -u

if [ ! -d "apps" ] || [ ! -d "services" ]; then
    echo "ERROR: run me from the idrm-monorepo root."
    exit 1
fi

w() {
    local p="$1"
    mkdir -p "$(dirname "$p")"
    cat > "$p"
    echo "wrote $p"
}

w apps/README.md <<'ENDREADME'
# Apps

This folder holds every user-facing application in the IDRM monorepo.

An app is something a person opens: a web page, a mobile screen. Apps talk
to the backend over HTTP; they never touch the database directly.

## What is inside

| Folder | What it is | Runs on | Status |
|---|---|---|---|
| web/       | Pure HTML, CSS, vanilla JS | Any modern browser | Active (MVP) |
| web-react/ | React + TypeScript web app | Any modern browser | Placeholder (FFP) |
| mobile/    | Expo React Native app | iOS + Android | Placeholder (FFP) |

The three apps co-exist on purpose. During early development we do not know
which frontend experience will win. Keeping all three in one place lets us
compare and converge without rewriting the backend.

## How the apps share code

Apps never import from each other. They only import from packages/ at the
repository root. This keeps each app independent while letting them share
types, utilities, and the typed API client.

## Which one should I work on?

- Building the MVP? Start with web/.
- Building the FFP web experience? See web-react/.
- Building the mobile experience? See mobile/.
- Not sure? Read ../docs/architecture/multi-frontend-strategy.md

## Adding a new app

1. Create a folder under apps/.
2. Add a README.md explaining what it is.
3. Add a package.json with a name field.
4. Run bun install from the repository root.
ENDREADME

w apps/web/README.md <<'ENDREADME'
# Pure Web Interface

A plain HTML, CSS, and JavaScript interface. No framework, no bundler, no
build step. This is the MVP primary user-facing surface.

## Why it exists

The pure web app is the simplest possible proof that the backend API works.
It loads static files, calls the API with fetch, and renders the results.
If the API can serve this app, it can serve anything.

## What is inside

    apps/web/
      README.md          this file
      Makefile           "make serve" starts a local server
      static/            every file the browser loads
        css/             app.css (all styles)
        img/             icons and images
        js/              client-side JavaScript

Templates that Jinja2 renders live separately, at
../../services/monolith/app/templates/ because FastAPI renders them, not
the browser.

## How to run it

Option A, through the backend (recommended):

    cd ../../services/monolith
    make dev
    # open http://localhost:8000

Option B, standalone static server (no API):

    cd apps/web
    make serve
    # open http://localhost:8080

## How to test it

No test suite for pure HTML. Manual verification:

1. Start the backend (make dev in services/monolith/).
2. Open the page in a browser.
3. Confirm each screen renders and fetches data.

## Next steps

- Typed API client: ../../docs/architecture/typed-api-clients.md
- Design system: ../../docs/mvp/33-design-system.md
ENDREADME

w apps/web-react/README.md <<'ENDREADME'
# React Web App

The FFP (Full-Fledged Product) web interface: React + TypeScript + Vite.

## Why it exists

The pure web app in apps/web/ proves the API works. This app is the
production-grade web experience: richer interactions, better state
management, a component library.

It is a placeholder during the MVP. It becomes active when the FFP begins.

## Why a separate app (not a replacement)

The two web apps co-exist. The pure app is the baseline; the React app is
the future. Keeping them separate lets us prove the API against the simpler
app while building the richer one.

## How to scaffold it (when you are ready)

    cd apps
    bun create vite web-react --template react-ts
    cd web-react
    bun install

Then add the workspace dependencies to apps/web-react/package.json:

    "dependencies": {
      "@idrm/api-client": "workspace:*",
      "@idrm/types": "workspace:*",
      "@idrm/utils": "workspace:*"
    }

## Planned contents

    apps/web-react/
      package.json
      tsconfig.json      extends @idrm/config
      vite.config.ts
      index.html
      src/
        main.tsx         React entry point
        App.tsx          root component
        routes/          page components
        components/      shared pieces
      tests/
        contract/        oasprey contract tests

## Next steps

- Multi-frontend strategy: ../../docs/architecture/multi-frontend-strategy.md
- Shared UI components: ../../packages/ui/README.md
ENDREADME

w apps/mobile/README.md <<'ENDREADME'
# Expo Mobile App

The FFP mobile interface: React Native built with Expo. Runs on iOS and
Android from the same codebase.

## Why it exists

Disaster responders work in the field, often outdoors, often with patchy
connectivity. They need a native mobile experience, not a browser.

This app is a placeholder during the MVP. It becomes active when the FFP
begins.

## Why Expo

Expo is the fastest way to build React Native apps:

- One codebase for iOS and Android.
- Over-the-air updates (EAS Update), no store review for small fixes.
- Built-in monorepo support since SDK 52.
- Runs on web too (via react-native-web) if needed later.

## How to scaffold it

    cd apps
    bun create expo-app mobile --template blank-typescript
    cd mobile
    bun install

Metro (the React Native bundler) is configured automatically for monorepos
in Expo SDK 52+. No manual metro.config.js needed.

## Planned contents

    apps/mobile/
      package.json
      app.json           Expo configuration (name, icons, splash)
      app/               Expo Router file-based routes
      assets/            icons and images
      components/        shared with web-react via packages/ui/

## Next steps

- Shared UI components: ../../packages/ui/README.md
- Expo monorepo guide: https://docs.expo.dev/guides/monorepos/
ENDREADME

w services/README.md <<'ENDREADME'
# Services

This folder holds every backend application in the IDRM monorepo.

A service is a program that responds to HTTP requests. It owns its own
data, enforces business rules, and exposes them through a versioned API
(/api/v1/...). Services are the only code allowed to talk to the database.

## What is inside

| Folder | What it is | Language | Status |
|---|---|---|---|
| monolith/                | The MVP: all ten domains in one FastAPI app | Python | Active |
| users-service/           | FFP extraction of the users domain         | TBD    | Placeholder |
| incidents-service/       | FFP extraction of the incidents domain     | TBD    | Placeholder |
| resources-service/       | FFP extraction of the resources domain     | TBD    | Placeholder |
| locations-service/       | FFP extraction of the locations domain     | TBD    | Placeholder |
| alerts-service/          | FFP extraction of the alerts domain        | TBD    | Placeholder |
| notifications-service/   | FFP extraction of notifications            | TBD    | Placeholder |
| reports-service/         | FFP extraction of reports                  | TBD    | Placeholder |
| files-service/           | FFP extraction of file handling            | TBD    | Placeholder |
| audit-service/           | FFP extraction of audit logging            | TBD    | Placeholder |
| administration-service/  | FFP extraction of administration           | TBD    | Placeholder |

In the MVP, all ten domains live inside monolith/. In the FFP, they are
extracted one at a time. The monolith shrinks as the FFP grows, until it is
empty and can be retired.

## The shape every service shares

    <service>/
      src/api/            HTTP handlers (controllers)
      src/domain/         business rules and models
      src/infrastructure/ database and external clients
      tests/              unit | integration | contract
      Makefile            make dev, make test, make lint
      README.md           what this service does

The folder shape is identical across languages. Only the files inside src/
differ between Python, Go, Java, or TypeScript.

## How a service talks to the world

- Down to data: through a repository, never raw SQL in business logic.
- Across to other services: through HTTP, using the shared contracts in
  ../shared/contracts/v1/.
- Up to frontends: through /api/v1/..., documented in OpenAPI.

## Where to start

- New to the codebase? Read ../docs/walkthrough/02-anatomy-of-a-module.md
- Adding a new service? Read ../docs/contributing/adding-a-service.md
ENDREADME

w gateway/README.md <<'ENDREADME'
# API Gateway

The single entry point for every HTTP request that reaches the IDRM backend.

## Why a gateway exists

Without one, every frontend must know the address of every backend service,
apply authentication itself, enforce rate limits itself, and retry failed
calls itself. With a gateway, that work happens once, in one place.

## What it does

| Concern | Handled by the gateway |
|---|---|
| Routing             | /api/v1/incidents/* goes to incidents service |
| Authentication      | Validates the JWT before forwarding |
| Rate limiting       | Per-client limits to prevent abuse |
| TLS termination     | HTTPS at the edge, HTTP inside the cluster |
| Request logging     | Adds correlation IDs for tracing |
| Circuit breaking    | Fails fast when a backend is unhealthy |

## What is inside

    gateway/
      README.md             this file
      config/
        routes.yaml         routing rules (documentation in MVP)
      docker/               (FFP) container build

## MVP vs FFP

- MVP: there is no running gateway. The FastAPI monolith serves /api/v1/*
  directly. The routes.yaml file exists as documentation of the routing
  that will activate in the FFP.
- FFP: APISIX starts up and reads routes.yaml. From then on, every request
  passes through the gateway.

## Why config-only in the MVP

Deploying an API gateway adds a process, a container, and a failure mode.
In the MVP there is only one backend service, so a gateway buys nothing.
The config is written now so the FFP switch is a one-line change, not a
re-architecture.

## Next steps

- Layered architecture: ../docs/architecture/layered-architecture.md
- Routing configuration: ./config/routes.yaml
ENDREADME

w infra/README.md <<'ENDREADME'
# Infrastructure

Everything required to run IDRM on real hardware: process managers,
containers, cluster manifests, cloud resources, and CI pipelines.

## What is inside

| Folder | What it holds | Used in |
|---|---|---|
| systemd/   | Unit files that start the monolith on a Linux VM | MVP |
| docker/    | Dockerfiles and Compose files | FFP |
| k8s/       | Kubernetes manifests and Helm charts | FFP |
| terraform/ | Cloud resources (databases, buckets, DNS) | FFP |
| ci/        | Pipeline definitions shared by every service | FFP |

## Why separate from services/

Code and the machines it runs on change for different reasons. A new
endpoint does not require a new systemd unit. A new deploy target does not
require a code change. Keeping them in separate trees keeps each pull
request focused.

## MVP path (today)

The MVP runs on a single Linux host:

1. Python environment created by:
     conda env create -f services/monolith/environment.yml
2. systemd/idrm.service starts uvicorn on port 8000.
3. systemd/idrm-migrate.service runs Alembic migrations once at boot.
4. PostgreSQL and MinIO run on the same host or as managed services.

## FFP path (later)

Each service becomes a container. Kubernetes schedules them. Terraform
provisions databases, buckets, and DNS. CI builds and pushes images on
every merge to main.

## What to read next

- Deploy the MVP: ../docs/mvp/80-ops-deployment-and-operations.md
- Plan the FFP: ../docs/ffp/80-ops-platform-and-deployment.md
ENDREADME

w packages/README.md <<'ENDREADME'
# Packages

Shared TypeScript and JavaScript libraries used by every frontend app.

A package is not a running program. It is a library that other code imports.
Every package declares its name under the @idrm/ scope in its package.json.

## What is inside

| Package | Purpose | Consumed by |
|---|---|---|
| api-client/ | Typed HTTP client generated from the OpenAPI contract | apps/web-react/, apps/mobile/ |
| types/      | TypeScript types shared across apps | every frontend |
| utils/      | Framework-free helper functions | every frontend |
| config/     | Base ESLint and TypeScript configs | every frontend |
| ui/         | Shared React Native components | apps/web-react/, apps/mobile/ |

## Rules

1. Packages never import from apps/. The dependency arrow points the other
   way: apps depend on packages.
2. Packages must not depend on each other in a loop. Keep the graph a DAG.
3. api-client/src/gen/ is machine-generated. Never edit it by hand. See
   ../docs/architecture/typed-api-clients.md.

## How to add a package

1. Create a folder under packages/.
2. Add a package.json with "name": "@idrm/<name>".
3. Export the public surface from src/index.ts.
4. Run bun install from the repository root.
5. Import it from an app with "@idrm/<name>": "workspace:*".
ENDREADME

w packages/api-client/README.md <<'ENDREADME'
# @idrm/api-client

The typed HTTP client that every React-based frontend uses to call the
backend API.

## Why it exists

Without a shared client, each frontend writes its own HTTP calls and drifts
out of sync with the backend. This package is generated from the OpenAPI
contract in shared/contracts/v1/, so every request and response has a
TypeScript type.

When the backend changes and the contract is regenerated, every app that
imported this package fails to build if it relied on a removed field,
before the change reaches production.

## What is inside

    packages/api-client/
      package.json
      README.md          this file
      src/
        index.ts         public exports
        gen/             MACHINE-GENERATED, never edit by hand

## How to regenerate

From the repository root:

    make contracts-export      refresh the OpenAPI spec from the backend
    make contracts-generate    regenerate this package

Or in one step:

    make contracts-sync

## How apps use it

    import { createIncident, listIncidents } from '@idrm/api-client';

## Rules

1. Never hand-edit anything under src/gen/.
2. Never commit a regenerated client without the contract change it reflects.
3. If the client fails to build after regeneration, the app that imported it
   must be updated. Do not silently loosen the types.

## Next steps

- How it works: ../../docs/architecture/typed-api-clients.md
- The contract: ../../shared/contracts/README.md
ENDREADME

w packages/types/README.md <<'ENDREADME'
# @idrm/types

TypeScript types shared across every frontend app.

## Why it exists

A type declared once is understood by every app that imports it. A type
redeclared in three places drifts. This package is the single home for
cross-app types.

## What belongs here

- Primitive aliases (UUID, ISODate, CurrencyCode)
- Enums that span apps (IncidentStatus, UserRole)
- Interfaces for shape contracts not covered by the API client

## What does not belong here

- Types specific to one app (keep them in that app)
- Runtime code (use @idrm/utils instead)
- API response shapes (those come from @idrm/api-client)

## How to use it

    import type { UUID, ISODate } from '@idrm/types';

## How to add a type

1. Add the declaration to packages/types/src/index.ts.
2. Export it.
3. Re-run bun install from the root if the package has not been installed
   yet.
ENDREADME

w packages/utils/README.md <<'ENDREADME'
# @idrm/utils

Framework-free helper functions shared across every frontend app.

## Why it exists

Small, pure functions used in more than one app (date formatting,
validation, string manipulation) belong in one place, tested once.

## What belongs here

- Pure functions with no framework dependency
- Formatting helpers (dates, numbers, distances)
- Validation predicates (email shape, phone shape)
- Small algorithms that are identical across apps

## What does not belong here

- React components (use @idrm/ui)
- Framework-specific code (that belongs in each app)
- API calls (use @idrm/api-client)

## How to use it

    import { formatDistanceKm, isEmail } from '@idrm/utils';

## Rule of thumb

If a function is used by one app, keep it in that app. Move it here the
second time another app needs it.
ENDREADME

w packages/config/README.md <<'ENDREADME'
# @idrm/config

Shared ESLint, TypeScript, and build configuration used by every frontend
app.

## Why it exists

Without shared config, each app declares its own lint rules and TypeScript
strictness. Over time they drift, and a change that passes in one app fails
in another.

## What is inside

| File | What it does |
|---|---|
| eslint.js | Base ESLint config every app extends |
| tsconfig.base.json | Base TypeScript config every app extends |

## How apps use it

In tsconfig.json:

    { "extends": "@idrm/config/tsconfig.base.json" }

In .eslintrc.cjs:

    module.exports = { extends: ['@idrm/config/eslint'] };

## Rules

1. Changes here affect every app. Test in one app before merging.
2. Do not weaken strictness silently. Announce in the pull request.
3. Keep the base minimal. App-specific rules belong in the app.
ENDREADME

w packages/ui/README.md <<'ENDREADME'
# @idrm/ui

Shared UI components used by apps/web-react/ and apps/mobile/.

## Why it exists

React web and React Native can share a surprising amount of component code
when components are built on React Native primitives and styled with
NativeWind (Tailwind for React Native). One component serves both targets.

## How the sharing works

- Written once, using React Native primitives (View, Text, Pressable).
- On web, react-native-web renders them as HTML.
- On mobile, React Native renders them natively.
- Styling uses NativeWind, Tailwind class syntax that works on both.

## What belongs here

- Buttons, inputs, cards, list items, badges
- Layout primitives (stack, grid, container)
- Design tokens (colours, spacing, typography)

## What does not belong here

- The pure web app (apps/web/), which has no React runtime.
- App-specific screens, which live in each app's src/routes/.

## How to use it

    import { Button, Card } from '@idrm/ui';

## Next steps

- Multi-frontend strategy: ../../docs/architecture/multi-frontend-strategy.md
- Design system: ../../docs/mvp/33-design-system.md
ENDREADME

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

w docs/adr/README.md <<'ENDREADME'
# Architecture Decision Records

Short documents recording why a decision was made.

## What an ADR is

An ADR captures one decision, its context, and its consequences, in under
one page. The format was popularised by Michael Nygard in 2011 and is used
by AWS, Google, and most large engineering organisations.

## Format

Every ADR follows this structure:

- Title (numbered: 0001, 0002, ...)
- Status (Proposed, Accepted, Superseded by NNNN)
- Date
- Context (what problem, what constraints)
- Decision (what we decided)
- Consequences (what changes as a result)

## What is inside this folder

    docs/adr/
      README.md          this file
      template.md        the template every new ADR follows
      0001-...md         the first decision
      0002-...md         and so on

## How to add an ADR

1. Copy template.md to NNNN-your-title.md (zero-padded to four digits).
2. Fill in the six sections.
3. Open a pull request. ADRs are reviewed like code.
4. Once merged, the ADR is permanent. If the decision later changes, do not
   edit the old ADR. Write a new one that supersedes it.

## Reading order

Read them in numerical order. Each builds on the ones before it.

## Next steps

- The decisions currently recorded are in the numbered files beside this one.
- The reasoning behind them: ../../docs/architecture/
ENDREADME

w docs/architecture/README.md <<'ENDREADME'
# Architecture

Documents that explain how the IDRM monorepo is structured and why.

## What is inside

| File | Question it answers |
|---|---|
| monorepo-structure.md     | What are the top-level folders and what goes in each? |
| multi-frontend-strategy.md | Why do three frontends co-exist and how do they share code? |
| typed-api-clients.md      | How do frontends stay in sync with the backend API? |
| contract-testing.md       | How do we prove the backend honours the contract? |
| layered-architecture.md   | How many layers, and which layer does what? |
| language-stack.md         | Why these five languages, and not more? |

## Who should read this

Anyone who wants to understand the shape of the system before writing code.
New contributors should read this folder after the walkthrough
(../walkthrough/README.md) and before their first pull request.

## The one-minute version

Six top-level areas: apps/, packages/, services/, shared/, infra/, gateway/.
Four network tiers: presentation, edge, domain, data. Four internal layers
per service: controller, service, domain, repository. Five languages:
Python, TypeScript, JavaScript, Go, Java. One contract, one typed client,
many consumers.

## Next steps

- The reasoning behind each choice: ../adr/
- The tutorial walkthrough: ../walkthrough/README.md
ENDREADME

w docs/contributing/README.md <<'ENDREADME'
# Contributing

Guides for making a change to the IDRM monorepo.

## What is inside

| Guide | What it covers |
|---|---|
| adding-a-service.md             | How to add a new backend service |
| adding-a-package.md             | How to add a new shared package |
| adding-an-app.md                | How to add a new frontend app |
| adding-a-contract-endpoint.md   | How to add a new API endpoint |
| coding-standards.md             | Naming, formatting, testing conventions |

## The universal rules

1. Open a branch. Never commit directly to main.
2. Run make qa before every commit. It must pass.
3. Every change needs a test. No exceptions.
4. Every pull request needs one approval and green CI.
5. Path-scoped CI: a change to services/ does not run frontend tests, and
   vice versa.

## The everyday workflow

    git checkout -b feature/short-name
    # make your changes
    make qa
    git add .
    git commit -m "feat: short description"
    git push -u origin feature/short-name
    # open a pull request on GitHub

## Where to ask for help

- Confused about a concept? Check the 101 guides in ../../guides/mvp/learn/.
- Confused about a decision? Check ../../docs/adr/.
- Confused about the shape? Check ../architecture/.

## Next steps

- Coding standards: ./coding-standards.md
- The repository structure: ../architecture/monorepo-structure.md
ENDREADME

echo ""
echo "Done. All 22 README files have been rewritten."
echo ""
echo "Next:"
echo "  git status"
echo "  git diff --stat"
echo "  git add ."
echo "  git commit -m 'docs: expand README files to novice-friendly form'"
echo "  git push"