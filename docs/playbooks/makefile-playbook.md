# Makefile Playbook

## What this document is

Every Makefile target in the IDRM monorepo, explained for a newcomer. Written
so you can find the right target for any task without reading the Makefile
itself. By the end you will understand what a Makefile is, why it is the
command surface for a polyglot repository, and how to use it daily.

## Part 1 - What a Makefile is

A Makefile is a plain text file that turns long commands into short ones. You
type `make dev`. Make runs `cd services/monolith && uvicorn app.main:app
--reload`. The long command is stored under the short name.

Make was created in 1976 at Bell Labs to compile C programs. Over fifty years
it became a general-purpose task runner, used for builds, tests, deployments,
database migrations, and documentation. It works everywhere, understands no
languages, and requires nothing but a shell. That is why it is the command
surface for a polyglot repository.

When you type `make <target>`, Make reads the Makefile, finds the rule for the
target, checks whether the target is out of date (by timestamps), and runs the
recipe. For modern uses, we tell Make to always run the recipe by marking the
target as phony.

## Part 2 - Why Makefiles in a polyglot monorepo

IDRM contains Python, TypeScript, JavaScript, Go, and Java. Each language has
its own tooling:

| Language | Install | Build | Test | Lint |
|---|---|---|---|---|
| Python | conda / pip | none | pytest | ruff |
| TypeScript | bun install | tsc / vite | jest / bun test | eslint |
| Go | go mod download | go build | go test | golangci-lint |
| Java | mvn install | mvn package | mvn test | checkstyle |

Without a unified interface, every developer must memorise all five. With a
Makefile, every developer memorises one.

The Makefile does not replace Turborepo or Bun. Each works at its proper level:

- **Makefiles** are the top-level human interface. `make dev` is what you type.
- **Makefiles delegate** to Turborepo for JS/TS and to native tools for Python,
  Go, and Java.
- **Turborepo** handles dependency ordering within the JS/TS ecosystem.
- **Bun** handles package installation and script execution within JS/TS.

Makefiles unify. Turborepo optimises. Bun installs.

## Part 3 - Anatomy of a Makefile

**Targets** are named tasks. `install:` defines a target. By convention, names
are lowercase with hyphens (`test-contract`, `db-migrate`).

**Dependencies** are other targets that must run first. `test: test-unit
test-contract test-e2e` runs all three in order.

**Recipes** are the commands under a target. They must be indented with a
**tab**, not spaces. This is Make's most common beginner mistake.

**Variables** store reusable values. `BUN := bun` then `$(BUN) install`. The
`:=` assignment evaluates immediately; `=` evaluates lazily.

**Phony targets** do not produce a file. Since every modern Makefile target is
an action, they are all phony. Declare them with `.PHONY: install dev test`.

**The default goal** is what runs when you type `make` bare. Set it to `help`
so a bare `make` prints the target list.

**The help target** lists every available task. It is the single most valuable
feature for onboarding. New contributors run `make` and immediately see what
is available.

**Special targets** include `.PHONY`, `.DEFAULT_GOAL`, `.ONESHELL` (run all
recipe lines in one shell), and `.DELETE_ON_ERROR`.

**Include** pulls in another file: `-include .env` loads environment variables
without erroring if the file is missing.

## Part 4 - The fifteen categories of tasks

The IDRM Makefile performs tasks in fifteen categories. Each has a clear
purpose.

### Setup and diagnostics

| Target | What it does |
|---|---|
| make help | Print every available target |
| make check-tools | Verify bun, python, conda are installed |
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
| make install-go | Go module download |
| make install-java | Maven install |
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
| make dev-gateway | API gateway (FFP) |

### Build

| Target | What it does |
|---|---|
| make build | Build everything |
| make build-apps | All frontend apps |
| make build-packages | All shared packages |
| make build-contracts | Regenerate the API client |
| make build-services | All backend services |
| make build-docker | All Docker images |

### Test

| Target | What it does |
|---|---|
| make test | All tests |
| make test-unit | Unit tests only |
| make test-integration | Integration tests |
| make test-contract | Contract tests |
| make test-compat | Backward compatibility |
| make test-e2e | End-to-end tests |
| make test-py | Python tests only |
| make test-js | JS/TS tests only |
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

### Contracts and code generation

| Target | What it does |
|---|---|
| make contracts-export | Export OpenAPI from the monolith |
| make contracts-validate | Lint the spec |
| make contracts-generate | Regenerate the typed client |
| make contracts-sync | All three, in order |
| make generate | All code generators |

### Database

| Target | What it does |
|---|---|
| make db-migrate | Apply pending migrations |
| make db-rollback | Roll back one migration |
| make db-revision m="..." | Create a new migration |
| make db-seed | Populate with sample data |
| make db-reset | Drop, recreate, migrate, seed |
| make db-shell | Open a psql shell |
| make db-history | Show migration history |

### Docker

| Target | What it does |
|---|---|
| make docker-build | Build all images |
| make docker-up | Start containers |
| make docker-down | Stop containers |
| make docker-logs | Tail container logs |
| make docker-shell | Open a shell in a container |

### Deployment

| Target | What it does |
|---|---|
| make deploy | Deploy everything |
| make deploy-backend | Restart the backend service |
| make deploy-web | Deploy the React web app |
| make deploy-mobile | EAS Build and submit |
| make release | Full release: tag + build + deploy |

### Cleanup and housekeeping

| Target | What it does |
|---|---|
| make clean | Remove build artefacts |
| make clean-js | Remove node_modules and dist |
| make clean-py | Remove __pycache__ and caches |
| make clean-turbo | Clear Turborepo cache |
| make clean-all | Everything above |
| make nuke | Destructive reset |

### Utilities and diagnostics

| Target | What it does |
|---|---|
| make tree | Print the project tree |
| make graph | Show Turborepo dependency graph |
| make prune | Prepare a pruned deployment bundle |
| make ports | Check if required ports are in use |
| make kill-ports | Kill processes on required ports |

### Documentation

| Target | What it does |
|---|---|
| make docs | Build the documentation site |
| make docs-serve | Serve documentation locally |
| make docs-deploy | Deploy documentation |

### Release and versioning

| Target | What it does |
|---|---|
| make tag | Create a git tag |
| make changelog | Generate a changelog |
| make release-prep | Prepare a release branch |

### Monorepo orchestration

| Target | What it does |
|---|---|
| make turbo-build | Delegate to Turborepo |
| make turbo-test | Delegate to Turborepo |
| make turbo-dev | Delegate to Turborepo |
| make filter-<app> | Run a target for a specific app |

## Part 5 - How root and local Makefiles chain together

The root Makefile does not contain the Python, Go, or Java recipes. It
delegates to the local Makefiles.

    make test
       -> make test-py
              -> cd services/monolith && pytest
       -> make test-js
              -> turbo run test --filter='./apps/*'
                     -> bun run --filter web-react test
                            -> jest tests/

A developer types `make test` and gets every test in the monorepo, regardless
of language.

Makefiles delegate with `$(MAKE)` — a variable that expands to the correct
`make` command and preserves flags like `-j` for parallelism. Use `$(MAKE)`,
not bare `make`, in recursive invocations.

For a full release, the execution graph is:

    release
    |-- qa
    |   |-- lint        (ruff + eslint + redocly)
    |   |-- typecheck   (mypy + tsc)
    |   +-- test        (pytest + jest)
    |-- build
    |   |-- build-contracts  (kubb generate)
    |   |-- build-packages   (turbo build)
    |   |-- build-apps       (turbo build)
    |   +-- build-services   (go/java builds)
    +-- deploy
        |-- deploy-backend   (systemctl restart)
        +-- deploy-web       (vercel deploy)

Each leaf is a real command. The tree is derived from `dependsOn` declarations.

## Part 6 - Best practices

1. Every target has a `help` entry. Update it in the same commit as the target.
2. Declare every action target as `.PHONY`. Otherwise a file named `install`
   silently shadows the target.
3. Use `$(MAKE)` for delegation, not `make`. Preserves `-j` and `-k`.
4. Prefer tabs, not spaces, in recipes. Make requires tabs.
5. Group related targets with comment banners.
6. Keep the root Makefile language-neutral. Language-specific flags belong in
   service Makefiles.
7. Use variables for tools. `BUN := bun` lets you swap with `make BUN=x`.
8. Make every destructive target ask for confirmation.
9. Keep targets idempotent. Running `make install` twice should be safe.
10. Fail fast. Use `.SHELLFLAGS := -eu -o pipefail -c`.

## Part 7 - Anti-patterns

1. Do not duplicate logic between root and service Makefiles. The root
   delegates; the service implements.
2. Do not put secrets in the Makefile. Use environment variables.
3. Do not chain too many targets in one recipe. If a target runs ten unrelated
   commands, split it.
4. Do not use `cd` without a subshell. `cd services/monolith && pytest` is
   safe; a bare `cd` on its own recipe line is not.
5. Do not ignore exit codes. `command || true` silences failures.
6. Do not use `make` for long-running processes without `-j`. Interactive
   targets block.
7. Do not version the Makefile separately from code. Same commit.

## Part 8 - Mastery workflows

### Onboarding a new contributor

    git clone <repo-url>
    cd idrm-monorepo
    make check-tools
    make setup
    make dev

Four commands and a working environment.

### Making a backend change

    git checkout -b feature/new-incident-field
    # edit services/monolith/app/modules/incidents/
    make db-revision m="add priority field"
    make db-migrate
    make test-py
    make contracts-sync
    make qa
    git commit -am "Add priority field to incidents"

### Making a frontend change

    git checkout -b feature/incident-priority-ui
    # edit apps/web-react/
    make dev-web-react
    make test-js
    make qa
    git commit -am "Show priority in incident list"

### Preparing a release

    make release-prep
    make tag
    make release

### Recovering from a broken state

    make doctor
    make clean
    make install
    make db-reset
    make contracts-sync

If all else fails:

    make nuke
    make setup

### Debugging a specific service

    make dev-backend
    make test-py
    make lint-py
    make db-shell

## Part 9 - Where the Makefiles live

| File | Scope |
|---|---|
| idrm-monorepo/Makefile | Whole monorepo (root orchestrator) |
| services/monolith/Makefile | Python monolith only |
| services/<service>/Makefile | One FFP service |
| apps/web/Makefile | Pure web app |
| apps/web-react/Makefile | React web app |
| apps/mobile/Makefile | Expo mobile app |
| gateway/Makefile | API gateway (FFP) |
| infra/Makefile | Infrastructure ops (optional) |

The filename must be exactly `Makefile` — capital M, no extension. Make looks
for that name first. Do not rename it, do not add an extension.

The root is the natural home because it is the first directory a developer
enters after clone, it has visibility over every sub-directory, and it
provides the `make help` entry point.

## Related

- The code reference: ./makefile-reference.md
- Implementation playbook: ./implementation-playbook.md
- Action plan: ./action-plan.md
- Bun commands: ./bun-commands.md
