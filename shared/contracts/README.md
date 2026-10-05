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
