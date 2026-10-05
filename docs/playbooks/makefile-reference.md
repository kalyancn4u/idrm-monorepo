# Makefile Reference

## What this document is

The complete Makefile code for the IDRM monorepo: the root orchestrator,
the service-level Makefiles, and the app-level Makefiles. Use it as a
template when adding a new service or app.

## Part 1 - The root Makefile

The root Makefile lives at `idrm-monorepo/Makefile`. It orchestrates every
language and delegates to local Makefiles.

Key sections:

    .DEFAULT_GOAL := help
    .ONESHELL:
    .SHELLFLAGS := -eu -o pipefail -c

    ROOT       := $(shell pwd)
    MONOLITH   := $(ROOT)/services/monolith
    CONTRACTS  := $(ROOT)/shared/contracts/v1
    API_CLIENT := $(ROOT)/packages/api-client

    BUN        := bun
    PYTHON     := python3
    CONDA      := conda
    ENV_NAME   := idrm
    TURBO      := $(BUN)x turbo
    DOCKER     := docker
    GIT        := git

The `.PHONY` line declares every action target. The `help` target prints a
grouped menu. Every other target falls into one of the fifteen categories
described in the playbook.

Representative targets from each category:

    # Setup
    check-tools:
    	@command -v $(BUN) >/dev/null 2>&1 || (echo "bun not found" && exit 1)
    	@command -v $(PYTHON) >/dev/null 2>&1 || (echo "python not found" && exit 1)
    	@echo "All required tools present."

    # Dependencies
    install: install-js install-py
    	@echo "All dependencies installed."

    install-js:
    	@$(BUN) install

    install-py:
    	@cd $(MONOLITH) && ($(CONDA) env list | grep -q $(ENV_NAME) \
    		&& $(CONDA) env update -f environment.yml \
    		|| $(CONDA) env create -f environment.yml)

    # Development
    dev:
    	@$(TURBO) run dev

    dev-backend:
    	@cd $(MONOLITH) && conda run -n $(ENV_NAME) uvicorn app.main:app --reload

    # Build
    build: build-contracts build-packages build-apps build-services
    	@echo "Full build complete."

    build-contracts: contracts-generate

    # Test
    test: test-py test-js
    	@echo "All tests passed."

    test-py:
    	@cd $(MONOLITH) && conda run -n $(ENV_NAME) pytest tests/ -v

    test-js:
    	@$(TURBO) run test --filter='./apps/*' --filter='./packages/*'

    # Quality
    qa: lint typecheck test
    	@echo "QA passed. Ready to commit."

    lint: lint-py lint-js lint-contracts
    	@echo "Lint passed."

    # Contracts
    contracts-sync: contracts-export contracts-validate contracts-generate
    	@echo "Contract workflow complete."

    contracts-export:
    	@cd $(MONOLITH) && conda run -n $(ENV_NAME) python scripts/export_openapi.py

    contracts-generate:
    	@$(BUN)x kubb generate

    # Database
    db-migrate:
    	@cd $(MONOLITH) && conda run -n $(ENV_NAME) alembic upgrade head

    db-seed:
    	@cd $(MONOLITH) && conda run -n $(ENV_NAME) python scripts/seed.py

    # Cleanup
    clean: clean-js clean-py clean-turbo
    	@echo "Clean complete."

    clean-py:
    	@find $(MONOLITH) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

    # Utilities
    tree:
    	@find . -type d \
    		-not -path "*/node_modules*" \
    		-not -path "*/.git*" \
    		-not -path "*/__pycache__*" \
    		| sort | sed 's|[^/]*/|  |g'

The complete root Makefile in this repository expands every category with
its full target set. Run `make help` to see the current list.

## Part 2 - Service-level Makefiles

Every service follows the same shape: `help`, `install`, `build`, `test`,
`lint`, `format`, `run`, `clean`. Only the recipes differ per language.

### Python service (the monolith)

    .DEFAULT_GOAL := help
    ENV_NAME := idrm
    CONDA    := conda

    .PHONY: help install dev test test-unit lint format typecheck migrate seed clean

    help:
    	@echo "Monolith - Available Targets"

    install:
    	@$(CONDA) env update -f environment.yml --prune

    dev:
    	@$(CONDA) run -n $(ENV_NAME) uvicorn app.main:app --reload

    test:
    	@$(CONDA) run -n $(ENV_NAME) pytest tests/ -v

    lint:
    	@$(CONDA) run -n $(ENV_NAME) ruff check .

    format:
    	@$(CONDA) run -n $(ENV_NAME) ruff format .

    typecheck:
    	@$(CONDA) run -n $(ENV_NAME) mypy app core modules

    migrate:
    	@$(CONDA) run -n $(ENV_NAME) alembic upgrade head

    seed:
    	@$(CONDA) run -n $(ENV_NAME) python scripts/seed.py

### Go service template

    .DEFAULT_GOAL := help
    .PHONY: help install build test lint format run clean

    help:
    	@echo "Service - Available Targets"

    install:
    	@go mod download

    build:
    	@go build -o bin/service ./cmd/service

    test:
    	@go test ./... -v

    lint:
    	@golangci-lint run

    format:
    	@gofmt -w .

    run:
    	@go run ./cmd/service

    clean:
    	@rm -rf bin/

### Java service template

    .DEFAULT_GOAL := help
    .PHONY: help install build test lint format run clean

    help:
    	@echo "Service - Available Targets"

    install:
    	@mvn install -DskipTests

    build:
    	@mvn package

    test:
    	@mvn test

    lint:
    	@mvn checkstyle:check

    format:
    	@mvn spotless:apply

    run:
    	@mvn spring-boot:run

    clean:
    	@mvn clean

## Part 3 - App-level Makefiles

Each frontend app has a Makefile that wraps Bun and Vite or Metro.

### React web app

    .DEFAULT_GOAL := help
    .PHONY: help dev build preview test test-contract lint typecheck clean

    help:
    	@echo "React Web - Available Targets"

    dev:
    	@bun run dev

    build:
    	@bun run build

    test:
    	@bun test

    test-contract:
    	@bun test tests/contract/

    lint:
    	@bunx eslint . --ext .ts,.tsx

    typecheck:
    	@bunx tsc --noEmit

    clean:
    	@rm -rf dist node_modules .turbo

### Expo mobile app

    .DEFAULT_GOAL := help
    .PHONY: help dev ios android web build lint typecheck clean

    help:
    	@echo "Expo Mobile - Available Targets"

    dev:
    	@bunx expo start

    ios:
    	@bunx expo start --ios

    android:
    	@bunx expo start --android

    web:
    	@bunx expo start --web

    build:
    	@bunx eas build

    lint:
    	@bunx eslint . --ext .ts,.tsx

    typecheck:
    	@bunx tsc --noEmit

    clean:
    	@rm -rf .expo node_modules dist

### Pure web app

Because the pure web app has no build step, its Makefile is minimal:

    .DEFAULT_GOAL := help
    .PHONY: help serve lint clean

    help:
    	@echo "Pure Web - Available Targets"

    serve:
    	@python3 -m http.server 8080 --directory .

    lint:
    	@echo "No lint configured."

    clean:
    	@echo "Nothing to clean."

## Part 4 - The delegation pattern

The root Makefile delegates to local Makefiles with `$(MAKE)`:

    test-py:
    	@cd services/monolith && $(MAKE) test

`$(MAKE)` expands to the current make command and preserves flags like `-j`.

## Related

- The conceptual guide: ./makefile-playbook.md
- Action plan: ./action-plan.md
- Bun commands: ./bun-commands.md
- Monorepo structure: ../architecture/monorepo-structure.md
