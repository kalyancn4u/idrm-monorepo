# Shared Libraries (per language)

Code that more than one service needs, written once and imported everywhere.

Unlike packages/, which holds TypeScript libraries consumed by frontends,
this folder holds shared code for backend languages.

## What is inside

| Folder | Language | Consumed by |
|---|---|---|
| python/ | Python package | Python services |
| java/   | Maven module  | Java services |
| go/     | Go module     | Go services |
| ts/     | npm package   | TypeScript services |

All four are placeholders in the MVP. They are populated the first time two
services in the same language need the same helper.

## Why one folder per language

Sharing code across languages is nearly impossible. A Python module cannot
be imported by a Go service. Keeping one folder per language makes it
obvious where a new shared helper belongs.

## Rules

1. No business logic. Infrastructure only: logging, tracing, error types,
   HTTP clients, auth helpers.
2. Versioned. Each library gets a version; consumers pin it.
3. Tested. Same standards as any other code in the monorepo.

## When to create a shared library

Do not create one in advance. Create one the second time two services need
the same code. The first time, copy. The second time, extract.
