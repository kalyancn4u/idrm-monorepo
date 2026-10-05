# Threat Modeling 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/architects · Status: **FFP** (practice usable anytime) · Track: Security (#23)*
> *Instead of reacting to breaches, threat modeling asks **"how could this be attacked?"** while you design — so
> you build defences in. Read [Secure Coding 101](secure-coding-101.md) first.*

---

## 1. What threat modeling is

**Threat modeling** is a structured way to find security weaknesses *before* attackers do, by reasoning about a
system's design. It answers four questions (the Shostack framing):

1. **What are we building?** (a diagram of the system + data flows)
2. **What can go wrong?** (the threats)
3. **What are we going to do about it?** (mitigations)
4. **Did we do a good job?** (validate)

It's a *thinking* discipline, not a tool — cheap to do early, expensive to skip.

---

## 2. STRIDE: a checklist for "what can go wrong"

**STRIDE** is a popular way to enumerate threat types:

| Letter | Threat | IDRM example |
|--------|--------|--------------|
| **S**poofing | pretending to be someone else | a fake "coordinator" approving incidents |
| **T**ampering | unauthorised change | altering an incident's status in transit |
| **R**epudiation | denying an action | "I never rejected that request" (→ need audit) |
| **I**nformation disclosure | leaking data | exposing a victim's location/PII |
| **D**enial of service | overwhelming the system | flooding the API so real reports fail |
| **E**levation of privilege | gaining more rights | a citizen performing coordinator actions |

Each maps to defences you've already met: authentication (spoofing), integrity/TLS (tampering), the **audit**
trail (repudiation), privacy/least-privilege (disclosure), rate-limiting (DoS), RBAC (elevation).

---

## 3. How to do it (lightweight)

1. **Diagram** the system and where data crosses **trust boundaries** (browser→API, API→DB, uploads in).
2. For each component/flow, walk **STRIDE** and list plausible threats.
3. **Rate** them (likelihood × impact) and pick mitigations for the ones that matter.
4. **Record** decisions (an ADR/checklist) and revisit when the design changes.

Focus on **trust boundaries** — that's where most real threats live.

---

## 4. IDRM context

Threat modeling underpins IDRM's security choices even in the MVP: RBAC (elevation), RS256 JWT (spoofing/
tampering), the audit trail (repudiation), DPDP privacy rules (disclosure), and validation (tampering). As IDRM
grows into multi-service **FFP** — a gateway, more integrations, a bigger attack surface — regular threat
modeling becomes a formal part of the secure SDLC. See
[`../../idrm-ffp-docs/22-architecture-security-and-iam.md`](../../../docs/ffp/22-architecture-security-and-iam.md).

---

## 5. Mastery check

1. State the four threat-modeling questions.
2. Explain each letter of **STRIDE** with an IDRM example.
3. Define a **trust boundary** and why threats cluster there.
4. Describe the lightweight process end to end.
5. Map three STRIDE threats to IDRM defences you already know.

---

## 6. Go deeper

- Threat Modeling (Adam Shostack) · OWASP Threat Modeling — owasp.org/www-community/Threat_Modeling ·
  Microsoft STRIDE — learn.microsoft.com
- Related: [Secure Coding 101](secure-coding-101.md) · [IAM 101](iam-101.md) · [RBAC/ABAC 101](rbac-abac-101.md)

---
*Next:* E2E Testing 101 (Quality track) · *Up:* [Learning Paths](../00-start-learning-paths.md)
