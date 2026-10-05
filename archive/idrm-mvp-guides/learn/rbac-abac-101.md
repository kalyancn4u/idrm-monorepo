# RBAC / ABAC 101

> *Type: Guide (101 / foundational) · Audience: novices → developers · Status: MVP — current · Track: Security (#22)*
> *Once IDRM knows who you are ([IAM 101](iam-101.md)), it must decide what you may do. The two standard models
> are **RBAC** and **ABAC**. This guide explains both and shows exactly which IDRM uses, and when.*

---

## 1. The problem being solved

**Authorization** = deciding whether a specific user may perform a specific action on a specific thing. A citizen
must not verify their own rescue; a provider must not approve critical incidents. We need a *systematic* way to
express such rules — not scattered `if` statements.

---

## 2. RBAC — Role-Based Access Control

**RBAC** grants permissions to **roles**, and assigns **roles to users**. You don't give Priya permissions; you
give the *provider* role permissions, and make Priya a provider.

IDRM's four roles + guest, and a sample of what each may do:

| Role | Can (examples) | Cannot |
|------|----------------|--------|
| **citizen** | create/cancel own help request, upload photos | accept, verify, approve |
| **provider** | accept, work, complete incidents; manage own resources | approve critical, verify |
| **coordinator** | approve critical, verify completion, reject invalid | act as a provider on the same case |
| **admin** | coordinator powers + user/system administration | — |
| **guest** | narrow emergency reporting only | almost everything else |

**Why RBAC for the MVP:** it's simple, auditable, and matches India's real chain of command
(citizen → provider → government coordinator). It answers "what can a *role* do?" — which covers the MVP's needs
cleanly.

---

## 3. ABAC — Attribute-Based Access Control

**ABAC** decides using **attributes** (of the user, the resource, the context) evaluated as **policies** —
finer-grained than roles. A policy reads like a sentence:

> *"Allow a **provider** to accept an incident **only if** it's in **their district** **and** during **their
> active shift**."*

Here district and shift are *attributes*, not roles. ABAC shines when rules depend on relationships and context
that pure roles can't express.

**Trade-off:** ABAC is powerful but more complex to write, test, and reason about. That complexity isn't worth it
until the system needs it.

---

## 4. RBAC vs ABAC — and IDRM's decision

| | RBAC | ABAC |
|---|------|------|
| Decides by | role | attributes + policy |
| Strength | simple, clear, auditable | fine-grained, context-aware |
| Cost | coarse-grained | complex to manage |

**IDRM decision (locked):** **RBAC in the MVP** (4 roles + guest). **ABAC** — plus a full role hierarchy and an
**Auditor** role — is deferred to **FFP**, added when scale/multi-agency rules demand it. The role *names* stay
stable across both phases, so ABAC will *refine* authorization later without breaking it.

---

## 5. For developers

- Enforce on the **server**, at the boundary of each protected action (a role/permission check in the router or
  service layer) — never rely on the UI hiding a control.
- Keep permission logic **centralised and testable**, not sprinkled through the code.
- Every sensitive action lands in the **audit** trail (who did what, when).

---

## 6. Mastery check

1. Explain **RBAC** and how a user gets permissions.
2. List IDRM's roles and one thing each may and may not do.
3. Explain **ABAC** and give a policy that RBAC alone can't express.
4. State IDRM's decision (RBAC now, ABAC/Auditor in FFP) and why.
5. Say where authorization must be enforced, and why the UI isn't enough.

---

## 7. Go deeper

- IDRM security & IAM: [`../../idrm-ffp-docs/22-architecture-security-and-iam.md`](../../idrm-ffp-docs/22-architecture-security-and-iam.md) ·
  spoke [`../../instructions/security.md`](../../instructions/security.md)
- NIST RBAC — csrc.nist.gov/projects/role-based-access-control · NIST SP 800-162 (ABAC) · OWASP Access Control Cheat Sheet — cheatsheetseries.owasp.org
- Related: [IAM 101](iam-101.md)

---
*Next:* [Secure Coding 101](secure-coding-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
