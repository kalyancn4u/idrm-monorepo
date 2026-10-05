# Cloud 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/ops · Status: **FFP** — next-phase · Track: Operations (#34)*
> *"The cloud" is just someone else's computers, rented on demand. This guide demystifies it — and explains why
> IDRM's **MVP runs on a plain server** (on-prem/VM), with cloud scaling a deliberate FFP choice.*

---

## 1. What "the cloud" actually is

**Cloud computing** means renting computing resources — servers, storage, databases — from a provider (AWS, Azure,
Google Cloud) over the internet, instead of buying and running your own hardware. You pay for what you use and can
scale up or down on demand.

The appeal: no upfront hardware, elastic capacity, and global reach. The trade-offs: ongoing cost, dependence on a
provider, and — important for a government disaster system — **data sovereignty** (where the data physically lives,
which matters under India's DPDP Act).

---

## 2. The service models (how much they manage)

- **IaaS (Infrastructure as a Service)** — you rent raw machines/storage; you manage the OS and up. (e.g. a VM.)
- **PaaS (Platform as a Service)** — you deploy code; the platform manages the servers.
- **SaaS (Software as a Service)** — you just use finished software (e.g. Gmail).

More managed = less control but less operational burden.

---

## 3. Key cloud ideas

- **Elasticity / autoscaling** — automatically add capacity under load, remove it when idle (pairs with
  [Performance Testing 101](performance-testing-101.md)).
- **Regions & availability zones** — data centres in different places for resilience and locality.
- **Managed services** — provider-run databases, object storage, queues (less to operate).
- **Object storage** — S3-style storage; IDRM's **MinIO** speaks the same S3 API, so moving to cloud storage later
  is smooth ([data-stores spoke](../../instructions/data-stores.md)).

---

## 4. IDRM's position

- **MVP:** runs on a **single Ubuntu server or VM** (on-prem or a basic cloud VM = IaaS), native systemd, no
  managed cloud services. Simple, sovereign, cheap, easy to reason about.
- **FFP:** as national scale demands elasticity and high availability, IDRM can adopt cloud/hybrid infrastructure —
  autoscaling, managed data services, multi-region DR ([Disaster Recovery 101](disaster-recovery-101.md)) — while
  keeping **data-sovereignty** requirements front and centre. Containers/K8s ([Docker 101](docker-101.md)) are the
  usual vehicle.

> "Cloud-ready, not cloud-required": IDRM's clean architecture and S3-compatible storage make the move optional and
> low-friction, not forced.

---

## 5. Mastery check

1. Explain what the cloud is and its main trade-offs (incl. **data sovereignty**).
2. Distinguish **IaaS / PaaS / SaaS**.
3. Define **elasticity/autoscaling** and **regions/AZs**.
4. Explain why MinIO's S3 compatibility eases a future cloud move.
5. State IDRM's MVP vs FFP infrastructure posture.

---

## 6. Go deeper

- NIST definition of cloud computing (SP 800-145) — csrc.nist.gov · AWS/Azure/GCP intro docs
- Related: [Networking 101](networking-101.md) · [Docker 101](docker-101.md) · [SRE 101](sre-101.md)

---
*Next:* [Monitoring 101](monitoring-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
