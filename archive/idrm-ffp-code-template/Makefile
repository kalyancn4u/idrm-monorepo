# =============================================================================
# IDRM Makefile — shortcuts for the common commands. Run `make` (or `make help`)
# to list everything. Each target just calls the matching script/command, so you
# don't have to remember the long forms.
#
# ROOKIE NOTE: Makefile recipe lines MUST be indented with a TAB (not spaces).
# =============================================================================
.DEFAULT_GOAL := help
SHELL := /bin/bash
DB_NAME ?= idrm_db
COMPOSE := docker compose -f infra/docker/full-stack.yml

.PHONY: help chmod prereqs setup setup-modular db-init dev docker-up docker-down docker-logs staging production test lint fmt clean

help:  ## Show this help
	@grep -hE '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

chmod:  ## Make the setup scripts executable (run once after cloning)
	chmod +x scripts/*.sh

prereqs:  ## Install missing prerequisites (Bun, Conda, Postgres+PostGIS, Redis)
	./scripts/setup-prerequisites.sh

setup:  ## Full local dev setup (conda env, deps, .env, database) — idempotent
	./scripts/setup-development-monolith.sh

setup-modular:  ## Dev setup, modular view (delegates to monolith today)
	./scripts/setup-development-modular.sh

db-init:  ## (Re)apply DB extensions, schema, and seed data — safe to re-run
	psql -d $(DB_NAME) -f database/init/01-extensions.sql
	psql -d $(DB_NAME) -f database/init/02-schema.sql
	psql -d $(DB_NAME) -f database/init/03-seed-data.sql

dev:  ## Print the 5-terminal dev startup commands
	@echo "Terminal 1: cd src/backend/app-python && conda activate idrm-mvp && uvicorn main:app --reload --port 8000"
	@echo "Terminal 2: cd src/backend/api-gateway && bun run dev    # HTTP :3000 / WS :3001"
	@echo "Terminal 3: cd src/frontend/web-html  && bun run dev     # :5173"
	@echo "Terminal 4: cd src/frontend/web-react && bun run dev     # :5174"
	@echo "Terminal 5: cd src/frontend/mobile-expo && npx expo start"

docker-up:  ## Start the data layer (postgres + redis) via Docker Compose
	$(COMPOSE) up -d --wait postgres redis

docker-down:  ## Stop compose services (data volumes are kept)
	$(COMPOSE) down

docker-logs:  ## Tail compose logs
	$(COMPOSE) logs -f

staging:  ## Bring up staging via Docker Compose
	./scripts/setup-staging.sh

production:  ## Deploy to production (guarded — needs .env.production)
	./scripts/setup-production.sh

test:  ## Run backend tests (pytest) inside the conda env
	-conda run -n idrm-mvp pytest -q

lint:  ## Lint Python with ruff (if installed)
	-conda run -n idrm-mvp ruff check src/backend

fmt:  ## Auto-format Python with ruff (if installed)
	-conda run -n idrm-mvp ruff format src/backend

clean:  ## Remove Python caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache .mypy_cache htmlcov .coverage dist build
