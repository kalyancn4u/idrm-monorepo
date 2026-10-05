# Shared Config

Configuration shared across services: environment templates, feature flags,
and constants that must stay in sync.

## What belongs here

- Example environment files (env.example) that new services copy.
- Feature flag definitions used by more than one service.
- Cross-service constants (standard header names, error codes).

## What does not belong here

- Secrets. Those live in environment variables on the server, never in the
  repository.
- Service-specific config. Keep it inside the service.
- Build config. That lives in packages/config/.

## Status in the MVP

Placeholder. Populate when a second service needs the same config that the
monolith already uses.
