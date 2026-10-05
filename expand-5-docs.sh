#!/usr/bin/env bash
set -u
[ -d "docs" ] || { echo "Run from the idrm-monorepo root."; exit 1; }
w() { local p="$1"; mkdir -p "$(dirname "$p")"; cat > "$p"; echo "wrote $p"; }

w docs/adr/README.md <<'ENDREADME'
# Architecture Decision Records

Short documents recording why a decision was made.

## What an ADR is

An ADR captures one decision, its context, and its consequences, in under
one page. The format was popularised by Michael Nygard in 2011 and is used
by AWS, Google, and most large engineering organisations.

## Format

Every ADR follows this structure:

- Title (numbered: 0001, 0002, ...)
- Status (Proposed, Accepted, Superseded by NNNN)
- Date
- Context (what problem, what constraints)
- Decision (what we decided)
- Consequences (what changes as a result)

## What is inside this folder

    docs/adr/
      README.md          this file
      template.md        the template every new ADR follows
      0001-...md         the first decision
      0002-...md         and so on

## How to add an ADR

1. Copy template.md to NNNN-your-title.md (zero-padded to four digits).
2. Fill in the six sections.
3. Open a pull request. ADRs are reviewed like code.
4. Once merged, the ADR is permanent. If the decision later changes, do not
   edit the old ADR. Write a new one that supersedes it.

## Reading order

Read them in numerical order. Each builds on the ones before it.

## Next steps

- The decisions currently recorded are in the numbered files beside this one.
- The reasoning behind them: ../../docs/architecture/
ENDREADME

w docs/architecture/README.md <<'ENDREADME'
# Architecture

Documents that explain how the IDRM monorepo is structured and why.

## What is inside

| File | Question it answers |
|---|---|
| monorepo-structure.md     | What are the top-level folders and what goes in each? |
| multi-frontend-strategy.md | Why do three frontends co-exist and how do they share code? |
| typed-api-clients.md      | How do frontends stay in sync with the backend API? |
| contract-testing.md       | How do we prove the backend honours the contract? |
| layered-architecture.md   | How many layers, and which layer does what? |
| language-stack.md         | Why these five languages, and not more? |

## Who should read this

Anyone who wants to understand the shape of the system before writing code.
New contributors should read this folder after the walkthrough
(../walkthrough/README.md) and before their first pull request.

## The one-minute version

Six top-level areas: apps/, packages/, services/, shared/, infra/, gateway/.
Four network tiers: presentation, edge, domain, data. Four internal layers
per service: controller, service, domain, repository. Five languages:
Python, TypeScript, JavaScript, Go, Java. One contract, one typed client,
many consumers.

## Next steps

- The reasoning behind each choice: ../adr/
- The tutorial walkthrough: ../walkthrough/README.md
ENDREADME

w docs/contributing/README.md <<'ENDREADME'
# Contributing

Guides for making a change to the IDRM monorepo.

## What is inside

| Guide | What it covers |
|---|---|
| adding-a-service.md             | How to add a new backend service |
| adding-a-package.md             | How to add a new shared package |
| adding-an-app.md                | How to add a new frontend app |
| adding-a-contract-endpoint.md   | How to add a new API endpoint |
| coding-standards.md             | Naming, formatting, testing conventions |

## The universal rules

1. Open a branch. Never commit directly to main.
2. Run make qa before every commit. It must pass.
3. Every change needs a test. No exceptions.
4. Every pull request needs one approval and green CI.
5. Path-scoped CI: a change to services/ does not run frontend tests, and
   vice versa.

## The everyday workflow

    git checkout -b feature/short-name
    # make your changes
    make qa
    git add .
    git commit -m "feat: short description"
    git push -u origin feature/short-name
    # open a pull request on GitHub

## Where to ask for help

- Confused about a concept? Check the 101 guides in ../../guides/mvp/learn/.
- Confused about a decision? Check ../../docs/adr/.
- Confused about the shape? Check ../architecture/.

## Next steps

- Coding standards: ./coding-standards.md
- The repository structure: ../architecture/monorepo-structure.md
ENDREADME

echo "Script 5 done."
