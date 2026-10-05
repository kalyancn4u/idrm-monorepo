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
