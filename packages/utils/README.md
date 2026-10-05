# @idrm/utils

Framework-free helper functions shared across every frontend app.

## Why it exists

Small, pure functions used in more than one app (date formatting,
validation, string manipulation) belong in one place, tested once.

## What belongs here

- Pure functions with no framework dependency
- Formatting helpers (dates, numbers, distances)
- Validation predicates (email shape, phone shape)
- Small algorithms that are identical across apps

## What does not belong here

- React components (use @idrm/ui)
- Framework-specific code (that belongs in each app)
- API calls (use @idrm/api-client)

## How to use it

    import { formatDistanceKm, isEmail } from '@idrm/utils';

## Rule of thumb

If a function is used by one app, keep it in that app. Move it here the
second time another app needs it.
