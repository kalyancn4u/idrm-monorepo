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
