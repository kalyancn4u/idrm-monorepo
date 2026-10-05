# Language Stack

## What this document is

The five programming languages IDRM uses, why exactly those five, and which
one fits in which layer. Written so a newcomer can decide where a new piece
of code belongs.

## The five languages

| Language | Role | Primary fit |
|---|---|---|
| Python | MVP monolith, data services, scripting | Business logic with fast iteration |
| TypeScript | React web, Expo mobile, BFF, shared packages | Anything typed that runs in a browser or on Node/Bun |
| JavaScript | Pure web interface, build tooling | Browser-only, no build step |
| Go | High-concurrency microservices, CLI tools | Cloud-native, stateless, horizontally scaled services |
| Java | Complex business logic, long-lived enterprise services | Transactional, audited, enterprise-grade domains |

That is the complete set. There are no others.

## Why not fewer

Using only Python and TypeScript would force compromises:

- Python is poor at high-concurrency stateless services. It is excellent at
  business logic and data work but does not scale to thousands of concurrent
  connections per process without significant investment.
- TypeScript on the server (via Bun or Node) lacks Java's enterprise
  maturity: transactions, auditing, connection pooling, ORM maturity.
- Without Go, every stateless microservice carries Python's overhead or
  TypeScript's runtime.

## Why not more

Every additional language adds a build system, a dependency manager, a test
framework, a CI pipeline, and a talent pool to manage. The industry consensus
for a sustained polyglot monorepo is two to four additional languages.
Adding Rust, C++, C#, Kotlin, or Scala would each add cost without solving a
problem the five cannot.

## What fits where

### Python

- The MVP monolith (FastAPI).
- Data-heavy or ML-adjacent services in the FFP.
- Operational scripts.

Not for: high-concurrency stateless services; low-latency edge logic.

### TypeScript

- React web app.
- Expo mobile app.
- The API client package.
- The optional BFF layer (via Bun and Hono).
- Any shared type or utility package.

Not for: heavy computation; long-running background jobs at scale.

### JavaScript

- The pure web interface in apps/web/.
- Build tooling and configuration (Vite config, ESLint config).

Not for: anything requiring types; anything on the server.

### Go

- Stateless microservices that must scale horizontally.
- CLI tools (including scripts that ship to end users).
- Anything that needs a single static binary.
- The FFP gateway (if it is written in Go rather than configured in APISIX).

Not for: complex domain logic that changes frequently; data science work.

### Java

- Complex business logic services: reports, administration, audit.
- Long-lived systems where predictable maintenance matters more than speed
  of iteration.
- Services that need mature transaction handling across many tables.

Not for: greenfield rapid prototyping; small scripts.

## A worked example

Suppose IDRM needs a new "reports" service in the FFP. Which language?

- Is it a simple CRUD service? Go or Python.
- Does it need complex aggregation and PDF generation with well-established
  libraries? Java.
- Does it need to call other services concurrently and return quickly? Go.
- Is it a data-science job (churn detection, credibility scoring)? Python.

The choice follows from the problem, not from preference.

## How the choice was made

Each language occupies a distinct position in the trade-off space:

| Concern | Best fit |
|---|---|
| Fastest to write | Python |
| Safest for browser and mobile | TypeScript |
| Fastest to run and deploy | Go |
| Most predictable to maintain for years | Java |

Every language on the list earns its place by being the best at one of these.
No language is on the list just because it is popular.

## The supporting languages

Beyond the five, IDRM uses several supporting languages and formats. They are
not service languages; they are tools within every service and pipeline.

See supporting-languages.md for the full list: SQL, YAML, JSON, Protobuf,
gRPC IDL, HCL (Terraform), Ansible, Bash, and Markdown.

## Next steps

- Where each language lives in the tree: ./monorepo-structure.md
- The supporting languages: ./supporting-languages.md
