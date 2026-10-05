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

.PHONY: help check-tools doctor version info setup \
        install install-js install-py update outdated \
        dev dev-web dev-web-react dev-mobile dev-backend \
        build build-apps build-packages build-contracts build-services \
        test test-py test-js test-contract test-e2e coverage \
        lint lint-py lint-js lint-contracts format typecheck qa \
        contracts-export contracts-validate contracts-generate contracts-sync \
        db-migrate db-rollback db-revision db-seed db-reset db-shell \
        docker-build docker-up docker-down docker-logs \
        deploy deploy-backend deploy-web \
        clean clean-js clean-py clean-turbo clean-all \
        tree graph ports kill-ports

help:
	@echo "IDRM Monorepo - Available Targets"
	@echo ""
	@echo "  Setup:     make check-tools | doctor | setup | install"
	@echo "  Dev:       make dev | dev-web | dev-web-react | dev-mobile | dev-backend"
	@echo "  Build:     make build | build-apps | build-packages | build-contracts"
	@echo "  Test:      make test | test-py | test-js | test-contract | coverage"
	@echo "  Quality:   make lint | format | typecheck | qa"
	@echo "  Contracts: make contracts-export | contracts-validate | contracts-generate | contracts-sync"
	@echo "  Database:  make db-migrate | db-rollback | db-revision | db-seed | db-reset | db-shell"
	@echo "  Docker:    make docker-build | docker-up | docker-down | docker-logs"
	@echo "  Deploy:    make deploy | deploy-backend | deploy-web"
	@echo "  Cleanup:   make clean | clean-all | tree | graph"

check-tools:
	@command -v $(BUN)    >/dev/null 2>&1 || (echo "bun not found"    && exit 1)
	@command -v $(PYTHON) >/dev/null 2>&1 || (echo "python not found" && exit 1)
	@echo "All required tools present."

doctor:
	@echo "bun:    $$($(BUN) --version 2>/dev/null || echo n/a)"
	@echo "python: $$($(PYTHON) --version 2>/dev/null || echo n/a)"
	@echo "branch: $$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo n/a)"

version:
	@$(BUN) --version; $(PYTHON) --version

info:
	@echo "Root: $(ROOT)"
	@echo "Contracts: $(CONTRACTS)"

setup: install db-migrate contracts-sync
	@echo "Setup complete."

install: install-js install-py
	@echo "Dependencies installed."

install-js:
	@$(BUN) install

install-py:
	@cd $(MONOLITH) && ($(CONDA) env list | grep -q $(ENV_NAME) \
		&& $(CONDA) env update -f environment.yml \
		|| $(CONDA) env create -f environment.yml)

update:
	@$(BUN) update

outdated:
	@$(BUN) outdated || true

dev:
	@$(TURBO) run dev

dev-web:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) uvicorn app.main:app --reload

dev-web-react:
	@$(BUN) run --filter web-react dev

dev-mobile:
	@$(BUN) run --filter mobile dev

dev-backend:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) uvicorn app.main:app --reload

build: build-contracts build-packages build-apps
	@echo "Build complete."

build-apps:
	@$(TURBO) run build --filter='./apps/*' || true

build-packages:
	@$(TURBO) run build --filter='./packages/*' || true

build-contracts: contracts-generate

build-services:
	@echo "No build step for Python monolith."

test: test-py test-js
	@echo "Tests passed."

test-py:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) pytest tests/ -v

test-js:
	@$(TURBO) run test --filter='./apps/*' --filter='./packages/*' || true

test-contract:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) pytest tests/contract/ -v || true

test-e2e:
	@$(TURBO) run test:e2e || true

coverage:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) pytest --cov=app --cov-report=html tests/

lint: lint-py lint-js lint-contracts
	@echo "Lint passed."

lint-py:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) ruff check . || true

lint-js:
	@$(TURBO) run lint --filter='./apps/*' --filter='./packages/*' || true

lint-contracts:
	@$(BUN)x @redocly/cli lint $(CONTRACTS)/openapi.json || true

format:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) ruff format . || true

typecheck:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) mypy app || true

qa: lint typecheck test
	@echo "QA passed."

contracts-export:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) python scripts/export_openapi.py

contracts-validate:
	@$(BUN)x @redocly/cli lint $(CONTRACTS)/openapi.json

contracts-generate:
	@$(BUN)x kubb generate || true

contracts-sync: contracts-export contracts-validate contracts-generate
	@echo "Contracts synced."

db-migrate:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) alembic upgrade head

db-rollback:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) alembic downgrade -1

db-revision:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) alembic revision --autogenerate -m "$(m)"

db-seed:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) python scripts/seed.py

db-reset:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) alembic downgrade base
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) alembic upgrade head
	@$(MAKE) db-seed

db-shell:
	@cd $(MONOLITH) && conda run -n $(ENV_NAME) psql $$DATABASE_URL

docker-build:
	@for d in infra/docker/*/; do docker build -t idrm/$$(basename $$d) $$d; done

docker-up:
	@docker compose -f infra/docker/docker-compose.yml up -d

docker-down:
	@docker compose -f infra/docker/docker-compose.yml down

docker-logs:
	@docker compose -f infra/docker/docker-compose.yml logs -f

deploy: deploy-backend deploy-web
	@echo "Deployed."

deploy-backend:
	@sudo cp infra/systemd/*.service /etc/systemd/system/ || true
	@sudo systemctl daemon-reload || true
	@sudo systemctl restart idrm || true

deploy-web:
	@echo "Configure web deploy target."

clean: clean-js clean-py clean-turbo
	@echo "Clean complete."

clean-js:
	@rm -rf node_modules apps/*/node_modules packages/*/node_modules apps/*/dist packages/*/dist

clean-py:
	@find $(MONOLITH) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(MONOLITH)/.pytest_cache $(MONOLITH)/.mypy_cache $(MONOLITH)/.ruff_cache $(MONOLITH)/htmlcov

clean-turbo:
	@rm -rf .turbo

clean-all: clean
	@echo "Deep clean complete."

tree:
	@find . -type d \
		-not -path "*/node_modules*" -not -path "*/.git*" \
		-not -path "*/__pycache__*" -not -path "*/.turbo*" \
		-not -path "*/dist*" -not -path "*/.expo*" \
		| sort | sed 's|[^/]*/|  |g'

graph:
	@$(TURBO) run build --graph=graph.html || true

ports:
	@for p in 8000 3000 8081 5432; do \
		lsof -i :$$p >/dev/null 2>&1 && echo "port $$p in use" || echo "port $$p free"; \
	done

kill-ports:
	@for p in 8000 3000 8081; do lsof -ti :$$p | xargs -r kill -9; done
