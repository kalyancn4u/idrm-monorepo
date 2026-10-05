# IDRM MVP — task menu.  Run `make help` to list targets.
.DEFAULT_GOAL := help
.PHONY: setup install migrate seed run format lint typecheck test test-unit test-integration test-api coverage qa clean help

setup:      ## one-time: create the conda env + install dependencies
	conda env create -f environment.yml || conda env update -f environment.yml

install:    ## refresh Python dependencies from pyproject.toml
	pip install -e ".[dev]"

migrate:    ## apply DB schema to latest (Alembic)
	alembic upgrade head

seed:       ## load the rich, idempotent sample data
	python scripts/seed.py

run:        ## start the app locally with auto-reload (http://127.0.0.1:8000)
	uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

format:     ## auto-apply Black + isort
	black app tests && isort app tests

lint:       ## Ruff — no errors allowed
	ruff check app tests

typecheck:  ## mypy — clean
	mypy app

test:       ## run the whole pytest suite
	pytest

test-unit:  ## just the fast unit tests
	pytest tests/unit

test-integration: ## integration tests (needs the test DB + bucket)
	pytest tests/integration

test-api:   ## API contract tests
	pytest tests/api

coverage:   ## tests + coverage report, fail under 80%
	pytest --cov=app --cov-report=term-missing --cov-fail-under=80

qa:         ## the pre-PR gate: everything a machine can check, in order
	$(MAKE) format lint typecheck coverage

clean:      ## remove caches and build artifacts
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage

help:       ## list every target with its description
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-18s\033[0m %s\n",$$1,$$2}'
