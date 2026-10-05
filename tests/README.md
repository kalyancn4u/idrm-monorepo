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
