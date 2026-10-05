# Disaster Recovery 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/ops · Status: **FFP** — next-phase · Track: Operations (#38)*
> *What happens if the whole system — server, data centre — is lost? Disaster Recovery is the plan to bring the
> service back. Read [Backup & Restore 101](backup-restore-101.md) first; DR builds on it.*

> **Naming note:** "disaster" here means an **IT disaster** (data-centre failure), the plan for recovering IDRM
> **itself** — distinct from the human disasters IDRM helps with. The irony is real: IDRM must survive the very
> events it responds to.

---

## 1. Backup vs Disaster Recovery

- **Backup** — the copies of your data ([Backup & Restore 101](backup-restore-101.md)).
- **Disaster Recovery (DR)** — the **whole plan** to restore the *running service* after a major failure: backups
  **plus** replacement infrastructure, procedures, and people. Backup is a building block; DR is the building.

A pile of backups with no plan to stand the system back up is not disaster recovery.

---

## 2. The two numbers that define DR

- **RPO (Recovery Point Objective)** — how much data you can afford to lose (e.g. "≤ 15 minutes"). Drives backup
  frequency/replication.
- **RTO (Recovery Time Objective)** — how fast you must be back (e.g. "≤ 1 hour"). Drives how much standby
  infrastructure you keep ready.

Tighter RPO/RTO = more resilience, more cost. You set them by **how critical** the service is — and IDRM is very
critical.

---

## 3. DR strategies (cost vs speed)

- **Backup & restore** — cheapest, slowest: rebuild from backups when needed.
- **Pilot light** — a minimal copy always running; scale it up on disaster.
- **Warm standby** — a scaled-down live copy ready to take over quickly.
- **Hot standby / active-active** — a full second site running in parallel; near-instant failover, highest cost.

Pick per your RTO/RPO and budget.

---

## 4. What a DR plan contains

- Defined **RPO/RTO** per service tier.
- **Off-site, tested backups** (the golden rule: an untested backup isn't one).
- **Runbooks** for failover and restore ([Incident Response 101](incident-response-101.md)).
- **Regular DR drills** — actually practise recovering, don't just document it (ties to
  [Disaster Drill Testing 101](disaster-drill-scenario-testing-101.md)).

---

## 5. IDRM context

- **MVP:** the DR foundation — reliable, **off-host, encrypted**, **tested** backups (Postgres PITR + MinIO), plus
  a written recovery runbook. Enough to rebuild the single-server system.
- **FFP:** continuous archiving (**pgBackRest**), geo-redundant storage, multi-region standby, automated failover,
  and formal RPO/RTO targets — see [`../../instructions/backup-and-dr.md`](../../../archive/instructions/backup-and-dr.md).

---

## 6. Mastery check

1. Distinguish **backup** from **disaster recovery**.
2. Define **RPO** and **RTO** and what each drives.
3. Compare backup-&-restore, pilot light, warm, and hot standby.
4. List what a DR plan must contain (incl. drills).
5. State IDRM's MVP DR foundation vs FFP evolution.

---

## 7. Go deeper

- NIST SP 800-34 (Contingency Planning) — csrc.nist.gov · pgBackRest — pgbackrest.org · cloud DR whitepapers
- Related: [Backup & Restore 101](backup-restore-101.md) · [Incident Response 101](incident-response-101.md) · [SRE 101](sre-101.md)

---
*Next:* [SRE 101](sre-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
