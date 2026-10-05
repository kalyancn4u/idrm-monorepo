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
