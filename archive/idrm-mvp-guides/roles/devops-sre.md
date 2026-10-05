# Role-Mastery — DevOps / SRE

> *Type: Guide (role-mastery / learning journey) · Audience: DevOps/SRE, from novice → mastery · Status: MVP — current · Blueprint §25.9*
> *You keep IDRM running — reliably, during the very disasters it serves. **Phase note:** the MVP deploys
> **natively on Ubuntu with systemd (no Docker/K8s/CI-CD pipeline)**; containers, orchestration, and full CI/CD
> are **FFP** rungs.*

---

## 1. Your mission

Deploy, operate, and safeguard IDRM: get it running reliably, watch its health, respond to incidents, and
guarantee recovery — building toward measurable reliability (SLOs) as the system grows.

## 2. Your mastery map (phase-tagged)

```mermaid
flowchart LR
    A["Linux"] --> B["Git"]
    B --> C["Networking"]
    C --> D["Deployment (systemd)"]
    D --> E["Secrets"]
    E --> F["Logging / Metrics / Traces"]
    F --> G["Monitoring + SLOs"]
    G --> H["Incident Response"]
    H --> I["Backup / Restore"]
    I --> J["Disaster Recovery"]
    J --> K["Containers (FFP)"]
    K --> L["CI/CD (FFP)"]
    L --> M["Cloud / K8s (FFP)"]
    M --> N["Reliability / Mastery"]
```

*(Blueprint order front-loads containers/CI/CD; corrected — those are **FFP** for IDRM. MVP reliability is
reached on native systemd.)*

## 3. Your learning path (rung → what to read)

1. **Linux + Git + networking** → [Linux 101](../learn/linux-101.md) (systemd/journalctl) ·
   [Git/GitHub 101](../learn/git-github-101.md) · [Networking 101](../learn/networking-101.md)
2. **Deployment + secrets** → [`80-ops-deployment-and-operations.md`](../../idrm-mvp-docs/80-ops-deployment-and-operations.md)
   (Ubuntu native install/env/Alembic) · [Secure Coding 101](../learn/secure-coding-101.md) (secrets handling)
3. **Observability + monitoring + SLOs** → [Observability 101](../learn/observability-101.md) ·
   [Monitoring 101](../learn/monitoring-101.md) · [SRE 101](../learn/sre-101.md) (SLI/SLO/error budgets) ·
   [observability spoke](../../instructions/observability.md)
4. **Incident response** → [Incident Response 101](../learn/incident-response-101.md) (severity, runbooks,
   blameless post-mortems)
5. **Backup + DR** → [Backup & Restore 101](../learn/backup-restore-101.md) (pg_dump + WAL/PITR, MinIO
   consistency, restore drills) · [Disaster Recovery 101](../learn/disaster-recovery-101.md) (RPO/RTO) ·
   [backup-and-dr spoke](../../instructions/backup-and-dr.md)
6. **FFP rungs** → [Docker 101](../learn/docker-101.md) · [CI/CD 101](../learn/ci-cd-101.md) ·
   [Cloud 101](../learn/cloud-101.md) · [`../../idrm-ffp-docs/80-ops-platform-and-deployment.md`](../../idrm-ffp-docs/80-ops-platform-and-deployment.md)

## 4. What you own for IDRM

- **Reliable native deploys** (systemd services: PostgreSQL, MinIO, the app), health endpoints, and alerting.
- **Tested, off-host, encrypted backups** — a backup isn't real until a restore has succeeded.
- **Runbooks + on-call discipline**; blameless learning after every incident.
- Reliability is literal here: uptime is whether help reaches people.

## 5. MVP vs FFP for you

- **MVP:** native systemd on Ubuntu, scripted setup, basic monitoring + backups/DR foundation.
- **FFP:** Docker → Kubernetes, full CI/CD pipelines, distributed observability, autoscaling, formal SLOs/error
  budgets, multi-region DR.

## 6. Mastery test

You can **deploy and operate IDRM, make it observable, define and meet SLOs, respond to incidents, and guarantee
recovery** — on native systemd today, evolving to containers/CI-CD/cloud as FFP triggers arrive.

---
*Related:* [Solution Architect](solution-architect.md) · [Security Engineer](security-engineer.md) ·
[Backend Engineer](backend-engineer.md) · [Technical Support](technical-support.md)
