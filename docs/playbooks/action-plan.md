# Action Plan - The Ordered Execution

## What this document is

The step-by-step execution plan for building IDRM from an empty repository to
a running MVP, and from there into the FFP. Read it in order. Do not skip
phases. Each phase has a clear success condition.

## How this relates to the other playbooks

- implementation-playbook.md: the mental model (structure, contract, loop).
- action-plan.md: the concrete execution (this document).
- makefile-playbook.md: the task list.
- bun-commands.md: the command reference.

## Phase 0 - Preparation

Install the tools. Every developer does this once per machine.

    Bun:
        curl -fsSL https://bun.sh/install | bash
    Python 3.11+ and Conda
    Java 17+ (for FFP services)
    Go 1.21+ (for FFP services)
    Docker (optional in the MVP)

Clone the repository, then create a working branch:

    git clone <repo-url> idrm-monorepo
    cd idrm-monorepo
    git checkout -b restructuring/monorepo

Success: bun --version prints a version; python3 --version prints 3.11+.

## Phase 1 - Rename

If the repository was previously named something else, rename it on GitHub:

    Settings then Repository name then idrm-monorepo

GitHub creates an automatic redirect from the old URL. Update the local
remote:

    git remote set-url origin git@github.com:<org>/idrm-monorepo.git

Tag the pre-rename state:

    git tag pre-monorepo-rename
    git push origin pre-monorepo-rename

Success: git remote -v shows the new URL.

## Phase 2 - Restructure

Create the top-level directories. These are all empty at first.

    mkdir -p apps/web apps/web-react apps/mobile
    mkdir -p packages/ui packages/api-client packages/types packages/config packages/utils
    mkdir -p services
    mkdir -p gateway/config gateway/docker
    mkdir -p shared/contracts/v1
    mkdir -p shared/libs/python shared/libs/java shared/libs/go shared/libs/ts
    mkdir -p shared/config
    mkdir -p infra/systemd infra/docker infra/k8s infra/terraform infra/ci
    mkdir -p tests/smoke tests/e2e
    mkdir -p docs/architecture docs/adr docs/playbooks docs/contributing

Move any existing code into services/monolith/:

    git mv code/app services/monolith/app
    git mv code/alembic services/monolith/alembic
    git mv code/scripts services/monolith/scripts
    git mv code/tests services/monolith/tests
    git mv code/alembic.ini services/monolith/alembic.ini
    git mv code/Makefile services/monolith/Makefile
    git mv code/pyproject.toml services/monolith/pyproject.toml
    git mv code/environment.yml services/monolith/environment.yml

Split the frontend:

    git mv code/frontend/templates services/monolith/app/templates
    git mv code/frontend/static apps/web/static

Remove the emptied directory:

    rmdir code

Update path references in alembic.ini, pyproject.toml, and the root
Makefile. See migration-mapping.md for the full list.

Success: the monolith still runs from services/monolith/.

## Phase 3 - Bun workspaces and Turborepo

Create the root package.json:

    {
      "name": "idrm-monorepo",
      "private": true,
      "workspaces": ["apps/*", "packages/*"],
      "scripts": {
        "dev": "turbo run dev",
        "build": "turbo run build",
        "test": "turbo run test",
        "lint": "turbo run lint"
      },
      "devDependencies": { "turbo": "^2.5.0", "typescript": "^5.4.0" },
      "packageManager": "bun@1.2.0"
    }

Create turbo.json:

    {
      "$schema": "https://turbo.build/schema.json",
      "tasks": {
        "build": { "dependsOn": ["^build"], "outputs": ["dist/**", ".expo/**"] },
        "dev":   { "cache": false, "persistent": true },
        "test":  { "dependsOn": ["^build"], "outputs": ["coverage/**"] },
        "lint":  {}
      }
    }

Install:

    bun install

Success: bunx turbo run build runs without error (nothing to build yet).

## Phase 4 - Apps and packages

Scaffold the React web app:

    cd apps
    bun create vite web-react --template react-ts
    cd web-react
    bun install
    cd ../..

Scaffold the Expo mobile app:

    cd apps
    bun create expo-app mobile --template blank-typescript
    cd mobile
    bun install
    cd ../..

Add the shared packages (types, utils, config, ui) as folders with a
package.json and an src/index.ts. See packages/README.md for the shape.

Wire workspace dependencies into each app package.json:

    "dependencies": {
      "@idrm/types": "workspace:*",
      "@idrm/utils": "workspace:*",
      "@idrm/api-client": "workspace:*"
    }

Run bun install at the root.

Success: each app builds with bun run build in its folder.

## Phase 5 - Contracts and typed client

Write the OpenAPI export script:

    services/monolith/scripts/export_openapi.py

Run it:

    cd services/monolith
    python scripts/export_openapi.py

Install Kubb at the root:

    bun add -D @kubb/cli @kubb/swagger @kubb/swagger-ts @kubb/swagger-client

Create kubb.config.ts pointing at the exported spec and outputting to
packages/api-client/src/gen/. Run:

    bunx kubb generate

Import the generated client in apps/web-react and call one endpoint.

Success: TypeScript autocompletes the response shape in the editor.

## Phase 6 - Testing infrastructure

Python contract tests:

    cd services/monolith
    pip install schemathesis pytest

Create services/monolith/tests/contract/test_openapi.py that loads the spec
and asserts live responses conform. Run:

    pytest tests/contract/ -v

JavaScript contract tests:

    cd apps/web-react
    bun add -D oasprey jest

Create apps/web-react/tests/contract/api.test.ts that loads the spec and
uses toSatisfyApiSpec. Run:

    bun test tests/contract/

Success: both test suites pass against the running backend.

## Phase 7 - CI/CD

Create three path-scoped GitHub Actions workflows:

    .github/workflows/backend.yml    runs on services/ and shared/contracts/
    .github/workflows/frontend.yml   runs on apps/ and packages/
    .github/workflows/contract.yml   runs on shared/contracts/ changes

Backend uses actions/setup-python. Frontend uses oven-sh/setup-bun.
Contract validates the OpenAPI spec and confirms the generated client is
up-to-date.

Use bun install --frozen-lockfile in CI for deterministic installs.

Success: pushing a change to apps/ runs only the frontend workflow.

## Phase 8 - Documentation

- Rewrite the root README.md with the new tree and quick-start commands.
- Update docs/mvp/ references from code/ to services/monolith/.
- Write docs/architecture/monorepo-structure.md.
- Write docs/contributing/ guides.
- Update PENDING.md with the bring-up checklist.

Success: a newcomer can clone, read the README, and run make dev-backend.

## Phase 9 - FFP extension

For each domain to extract (users, incidents, resources, etc.):

1. Copy the module from services/monolith/app/modules/<name>/ to
   services/<name>-service/.
2. Choose a language for the new service.
3. Point the service at its own database schema.
4. Replace local function calls with HTTP calls to other services.
5. Add a route in gateway/config/routes.yaml.
6. Run contract tests against the new service.
7. Once stable, remove the module from the monolith.

The four internal layers (controller, service, domain, repository) do not
change. Only the deployment shape does.

Success: a request to /api/v1/<domain>/* reaches the new service and
returns a response that passes the same contract tests as the monolith.

## The everyday workflow

    git checkout -b feature/short-name
    # make changes
    make qa
    git add .
    git commit -m "feat: short description"
    git push -u origin feature/short-name
    # open a pull request

If make qa fails, fix it. Do not push a red build.

## Related

- Implementation playbook: ./implementation-playbook.md
- Makefile playbook: ./makefile-playbook.md
- Bun commands: ./bun-commands.md
- Migration mapping: ./migration-mapping.md
