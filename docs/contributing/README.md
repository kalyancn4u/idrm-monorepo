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
