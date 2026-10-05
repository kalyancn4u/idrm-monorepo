# Makefile Playbook

## What this document is

Every Makefile target in the IDRM monorepo, grouped by purpose, explained for
a newcomer. Written so you can find the right target for any task without
reading the Makefile itself.

## What a Makefile is

A Makefile is a plain text file that turns long commands into short ones. You
type `make dev`. Make runs `cd services/monolith && uvicorn app.main:app
--reload`. The long command is stored under the short name.

Make has been around since 1976. It works everywhere, understands no
languages, and requires nothing but a shell. That is why it is the command
surface for a polyglot repository.

## Why a Makefile in a monorepo

IDRM contains Python, TypeScript, JavaScript, Go, and Java. Each language has
its own tooling. Without a unified interface, every developer must memorise
all five. With a Makefile, every developer memorises one.

    make test      runs pytest, jest, go test, and mvn test as needed
    make lint      runs ruff, eslint, and redocly
    make qa        runs everything before you commit

The Makefile delegates to Turborepo for JS/TS work and to native tools for
Python, Go, and Java.

## The full task list, by category

### Setup and diagnostics

| Target | What it does |
|---|---|
| make help | Print every available target |
| make check-tools | Verify bun, python, and other tools are installed |
| make doctor | Diagnose the environment |
| make version | Print tool versions |
| make info | Print repository info |
| make setup | Full first-time setup |

### Dependencies

| Target | What it does |
|---|---|
| make install | Install everything |
| make install-js | Bun install only |
| make install-py | Python conda environment |
| make update | Update all dependencies |
| make outdated | Report outdated packages |

### Development

| Target | What it does |
|---|---|
| make dev | Start all dev servers |
| make dev-web | Pure web only |
| make dev-web-react | React web only |
| make dev-mobile | Expo mobile only |
| make dev-backend | FastAPI monolith only |

### Build

| Target | What it does |
|---|---|
| make build | Build everything |
| make build-apps | All frontend apps |
| make build-packages | All shared packages |
| make build-contracts | Regenerate the API client |
| make build-services | All backend services |

### Test

| Target | What it does |
|---|---|
| make test | All tests |
| make test-py | Python tests only |
| make test-js | JS/TS tests only |
| make test-contract | Contract tests |
| make test-e2e | End-to-end tests |
| make coverage | Coverage report |

### Quality

| Target | What it does |
|---|---|
| make lint | All linters |
| make lint-py | Ruff |
| make lint-js | ESLint |
| make lint-contracts | Redocly |
| make format | Auto-format everything |
| make typecheck | mypy + tsc |
| make qa | lint + typecheck + test |

### Contracts

| Target | What it does |
|---|---|
| make contracts-export | Export OpenAPI from the monolith |
| make contracts-validate | Lint the spec |
| make contracts-generate | Regenerate the typed client |
| make contracts-sync | All three, in order |

### Database

| Target | What it does |
|---|---|
| make db-migrate | Apply pending migrations |
| make db-rollback | Roll back one migration |
| make db-revision m="..." | Create a new migration |
| make db-seed | Populate with sample data |
| make db-reset | Drop, recreate, migrate, seed |
| make db-shell | Open a psql shell |

### Docker

| Target | What it does |
|---|---|
| make docker-build | Build all images |
| make docker-up | Start containers |
| make docker-down | Stop containers |
| make docker-logs | Tail container logs |

### Deploy

| Target | What it does |
|---|---|
| make deploy | Deploy everything |
| make deploy-backend | Restart the backend service |
| make deploy-web | Deploy the web app |

### Cleanup

| Target | What it does |
|---|---|
| make clean | Remove build artefacts |
| make clean-all | Also remove Docker images |
| make tree | Print the project tree |

## The everyday targets

You will type three targets most days.

    make dev       start working
    make qa        before every commit
    make test      when you need faster feedback

## The pre-commit rule

Never commit without `make qa` passing. It runs:

    1. ruff check      Python lint
    2. eslint          JS/TS lint
    3. redocly         OpenAPI lint
    4. mypy            Python types
    5. tsc             TypeScript types
    6. pytest          Python tests
    7. jest            JS/TS tests

If any fails, fix it. Do not push a red build.

## How the Makefile is organised

The root Makefile handles cross-cutting tasks. Each service and app has its
own Makefile for local tasks.

    idrm-monorepo/Makefile                  root orchestrator
    services/monolith/Makefile              Python service
    services/incidents-service/Makefile     Go service (FFP)
    services/reports-service/Makefile       Java service (FFP)
    apps/web/Makefile                       pure web
    apps/web-react/Makefile                 React web
    apps/mobile/Makefile                    Expo mobile

The root delegates. The local Makefiles implement.

## How to add a target

1. Add the target name to the .PHONY line.
2. Add the target and its recipe.
3. Add the target to the help output.
4. Test it.
5. Commit.

The .PHONY declaration is required so Make does not look for a file named
after the target.

## Rules

1. Use tabs for indentation. Make requires tabs, not spaces.
2. Every action target goes in .PHONY.
3. Never put secrets in the Makefile. Use environment variables.
4. Prefer delegation to service Makefiles over duplication.
5. Keep the help target accurate. If a target exists, it belongs in help.

## Summary

One Makefile per project. Root orchestrates. Local implements. Fifteen
categories of task. Three targets you will use every day. Never commit
without make qa.

## Related

- Implementation playbook: ./implementation-playbook.md
- Migration mapping: ./migration-mapping.md
