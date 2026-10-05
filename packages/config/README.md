# @idrm/config

Shared ESLint, TypeScript, and build configuration used by every frontend
app.

## Why it exists

Without shared config, each app declares its own lint rules and TypeScript
strictness. Over time they drift, and a change that passes in one app fails
in another.

## What is inside

| File | What it does |
|---|---|
| eslint.js | Base ESLint config every app extends |
| tsconfig.base.json | Base TypeScript config every app extends |

## How apps use it

In tsconfig.json:

    { "extends": "@idrm/config/tsconfig.base.json" }

In .eslintrc.cjs:

    module.exports = { extends: ['@idrm/config/eslint'] };

## Rules

1. Changes here affect every app. Test in one app before merging.
2. Do not weaken strictness silently. Announce in the pull request.
3. Keep the base minimal. App-specific rules belong in the app.
