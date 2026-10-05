# Architecture

Documents that explain how the IDRM monorepo is structured and why.

## What is inside

| File | Question it answers |
|---|---|
| monorepo-structure.md     | What are the top-level folders and what goes in each? |
| multi-frontend-strategy.md | Why do three frontends co-exist and how do they share code? |
| typed-api-clients.md      | How do frontends stay in sync with the backend API? |
| contract-testing.md       | How do we prove the backend honours the contract? |
| layered-architecture.md   | What are the layers? (the blueprint) |
| layered-architecture-rationale.md | Why are the layers that way? (the reasoning) |
| language-stack.md         | Why these five languages, and not more? |
| supporting-languages.md   | SQL, YAML, JSON, Protobuf, gRPC, HCL, Ansible, Bash |
| tooling-decisions.md      | Why Bun, Turborepo, and Expo |

## Who should read this

Anyone who wants to understand the shape of the system before writing code.
New contributors should read this folder after the walkthrough
(../walkthrough/README.md) and before their first pull request.

## Reading order

1. monorepo-structure.md - the folder layout.
2. layered-architecture.md - the blueprint.
3. layered-architecture-rationale.md - the reasoning.
4. multi-frontend-strategy.md - the frontends.
5. typed-api-clients.md and contract-testing.md - the contract.
6. language-stack.md and supporting-languages.md - the languages.
7. tooling-decisions.md - the tooling.

## The one-minute version

Six top-level areas: apps/, packages/, services/, shared/, infra/, gateway/.
Four network tiers: presentation, edge, domain, data. Four internal layers
per service: controller, service, domain, repository. Five languages:
Python, TypeScript, JavaScript, Go, Java. One contract, one typed client,
many consumers. Bun installs; Turborepo orchestrates; Expo packages.

## Next steps

- The reasoning behind each choice: ../adr/
- The tutorial walkthrough: ../walkthrough/README.md
