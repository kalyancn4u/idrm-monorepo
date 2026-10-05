# Supporting Languages and Formats

## What this document is

The five programming languages (Python, TypeScript, JavaScript, Go, Java) are
the ones you build services in. This document covers the languages and
formats you use *within* those services: configuration, data, contracts,
infrastructure.

None of these count as a service language. None require a runtime of their
own. All are necessary.

## The list

| Language / format | Type | Where it is used |
|---|---|---|
| SQL | Query language | All database access |
| YAML | Data serialisation | Config files, Kubernetes, CI |
| JSON | Data serialisation | API payloads, configs, lockfiles |
| Protobuf | Interface definition | Optional: FFP service-to-service messaging |
| gRPC IDL | Interface definition | Optional: FFP high-performance RPC |
| HCL | Infrastructure definition | Terraform (FFP cloud resources) |
| Ansible | Configuration automation | Server provisioning, repeatable setup |
| Bash | Shell scripting | Makefiles, scripts, CI steps |
| Markdown | Documentation format | Every README and doc in this repo |

## SQL

Every service that stores data uses SQL. In IDRM the database is PostgreSQL
with the PostGIS extension for geospatial work.

Two ways you encounter SQL:

- **Directly** in migration files (Alembic for Python, Flyway for Java,
  golang-migrate for Go) and in seed scripts.
- **Indirectly** through an ORM (SQLAlchemy in Python, Hibernate in Java,
  sqlx in Go). The ORM writes the SQL; you write the model.

Rule of thumb: write SQL in migrations and reports; let the ORM handle CRUD.

## YAML

YAML is the human-readable format used by Kubernetes, GitHub Actions, APISIX,
and many other tools. It appears in:

- `.github/workflows/*.yml` - CI pipelines.
- `infra/k8s/*.yaml` - Kubernetes manifests (FFP).
- `gateway/config/routes.yaml` - API gateway routing.
- `docker-compose.yml` - local development stack.

Rule of thumb: YAML is for humans to read and machines to parse. Keep it flat
and commented. Never put secrets in a committed YAML file.

## JSON

JSON is the format of API payloads and machine-readable configuration. It
appears in:

- Every request and response body over HTTP.
- `shared/contracts/v1/openapi.json` - the exported OpenAPI spec.
- `package.json`, `tsconfig.json`, `app.json` - project metadata.

Rule of thumb: JSON is for machines. If a file must be hand-edited, prefer
YAML or TOML.

## Protobuf and gRPC IDL

Protobuf is a schema language for structured data. gRPC is a remote procedure
call framework that uses Protobuf as its interface definition language.

IDRM does not use these in the MVP. In the FFP, they become relevant if two
services need to exchange high-frequency binary messages faster than JSON
over HTTP allows.

If adopted, Protobuf definitions live in:

    shared/contracts/v1/protobuf/

and are compiled into Python, Go, and Java stubs by the build system.

## HCL (Terraform)

HashiCorp Configuration Language describes cloud infrastructure: databases,
buckets, DNS, load balancers, and network rules. It appears in:

    infra/terraform/

In the MVP there is no Terraform. In the FFP, when IDRM runs on AWS or GCP,
Terraform provisions the cloud resources.

Rule of thumb: Terraform describes what should exist, not how to create it.
Run `terraform plan` before every `terraform apply`.

## Ansible

Ansible playbooks automate server configuration: installing packages, writing
config files, starting services. It appears in:

    infra/ansible/

Ansible is useful when you have servers to configure but do not want to
containerise everything. It is a good fit for the MVP's single-host deploy
if systemd alone becomes insufficient.

## Bash

Shell scripts glue everything together. They appear in:

- `scripts/*.sh` - operational scripts.
- The root `Makefile` - task orchestration.
- `.github/workflows/*.yml` - individual CI steps.

Rule of thumb: any shell script longer than 50 lines should probably be
rewritten in Python or Go. Bash is for glue, not logic.

## Markdown

Every README, ADR, playbook, and guide in this repository is written in
Markdown. It is the lingua franca of technical documentation: readable as
plain text, renderable on GitHub, convertible to PDF or HTML.

Rule of thumb: if you write a comment longer than five lines, it is
documentation. Move it to Markdown.

## The complete list at a glance

| For... | Use... |
|---|---|
| Talking to the database | SQL |
| Configuring CI, Kubernetes, APISIX | YAML |
| Talking over HTTP | JSON |
| High-performance service-to-service (FFP) | Protobuf, gRPC |
| Provisioning cloud resources (FFP) | HCL (Terraform) |
| Configuring servers | Ansible |
| Gluing scripts together | Bash |
| Writing documentation | Markdown |

## Next steps

- The five service languages: ./language-stack.md
- Where everything lives: ./monorepo-structure.md
