# Security — How IDRM Is Kept Safe

> **Part of:** IDRM Documentation · `05-security.md`
> **Answers:** How does IDRM protect people, data, and access?
> **Source posters:** Posters 24–25 (Phase 5 Security)
> **Audience:** Security engineers (readable by all) · **Depth:** Overview
> **Status:** Draft

---

## How to read this document

1. [Security by design](#1-security-by-design) — the mindset.
2. [Authentication](#2-authentication--who-you-are) — proving who you are.
3. [Authorization](#3-authorization--what-youre-allowed-to-do) — what you're allowed to do.
4. [Data protection](#4-data-protection) — encryption and privacy.
5. [Audit & accountability](#5-audit--accountability) — a trustworthy record.
6. [Threat model](#6-threat-model) — how we think about attacks.
7. [Security controls at a glance](#7-security-controls-at-a-glance).
8. [Compliance](#8-compliance).

---

## 1. Security by design

Security in IDRM is **built in, not bolted on** — it applies across every layer (see the Security, Governance
& Compliance layer in [`02-architecture.md`](02-architecture.md)). Because disaster data can be sensitive and
decisions are high-stakes, IDRM treats **confidentiality, integrity, availability, and accountability** as
first-class requirements.

**Four security layers:**

| Layer | Covers |
|---|---|
| **Application security** | RBAC, authorization, input validation, OWASP Top 10. |
| **Data security** | Encryption, data masking, secure storage. |
| **Infrastructure security** | Network protection, TLS, hardening. |
| **Operational security** | Monitoring, logging, audit, incident response. |

**Principles in action:** **Zero Trust** (never trust, always verify) · **Defense in Depth** (independent
layers) · **Least Privilege** (minimum access) · **Secure by Default** (safety built in) · **Visibility &
Accountability** (detect, respond, learn).

---

## 2. Authentication — who you are

Authentication confirms a user's identity before they can do anything.

| Element | What it means |
|---|---|
| **Login / logout** | Secure sign-in with sessions that expire safely. |
| **JWT** | A signed token that proves a valid session for API calls. |
| **OIDC** | A standard way to sign in, optionally via a trusted identity provider (for organisations). |
| **Password policy** | Strong passwords, securely hashed — never stored in plain text. |
| **Multi-factor (future-ready)** | The design leaves room for a second factor (e.g. OTP) as needs grow. |

---

## 3. Authorization — what you're allowed to do

Once identity is known, authorization decides what that person can see and do.

- **Role-Based Access Control (RBAC):** permissions follow your **role** (citizen, volunteer, coordinator,
  administrator, …), so people only reach what their job requires.
- **Least privilege:** everyone gets the minimum access needed — nothing more.
- **Finer control when needed:** the design can extend to attribute-based rules (context such as area or
  ownership) as scenarios demand.

**The security workflow (every request):** 1) user authentication (OIDC / MFA) → 2) token issuance (JWT) →
3) authorization (RBAC) → 4) secure access to resources → 5) encrypted data handling → 6) audit & monitoring.
Tokens are validated at every request; all traffic is encrypted (TLS 1.2+); access is limited by role and
least privilege; all activity is logged and auditable.

---

## 4. Data protection

| Protection | How IDRM applies it |
|---|---|
| **Encryption in transit** | All traffic over **HTTPS/TLS**, so data can't be read on the wire. |
| **Encryption at rest** | Sensitive data protected where it's stored. |
| **PII protection** | Personal information is minimised, access-controlled, and handled per privacy law. |
| **Input validation** | All incoming data is validated (Pydantic) to block malformed or malicious input. |
| **Secure defaults** | Security headers, safe cookies, and hardened settings are on by default. |

---

## 5. Audit & accountability

Every meaningful action — who did what, when — is written to an **immutable audit trail**. This makes IDRM
**accountable and transparent**: incidents can be reconstructed, misuse can be detected, and compliance can be
demonstrated. Audit data feeds the monitoring and alerting described in
[`07-operations.md`](07-operations.md).

---

## 6. Threat model

IDRM models threats systematically — using **OWASP** and **STRIDE**, clear trust boundaries, defined assets,
and a simple risk rating.

### 6.1 What we protect (assets)
User identities & credentials · incident & operational data · geospatial data & maps · systems & applications ·
APIs & integrations · infrastructure & networks · audit logs & backups.

### 6.2 Trust boundaries & secure data flows
Data crosses from **Untrusted** (internet / public users) → **DMZ** (web app / gateway) → **Trusted**
(internal services & data). External systems (OIDC provider, SMS/email gateway, maps/weather APIs) sit outside.
At each boundary, traffic is authenticated, validated, and rate-limited; all traffic is TLS 1.2+; data is
encrypted in transit and at rest — so trust is *earned* at every step, never assumed.

### 6.3 STRIDE categories
| Category | Threat |
|---|---|
| **S**poofing | Impersonation of users, services, or systems. |
| **T**ampering | Unauthorized modification of data or code. |
| **R**epudiation | Denying actions due to lack of audit. |
| **I**nformation disclosure | Exposure of sensitive information. |
| **D**enial of service | Making services or resources unavailable. |
| **E**levation of privilege | Gaining higher access than authorized. |

### 6.4 Threat actors
Opportunistic attackers · malicious insiders · organized cyber criminals · nation-state / APTs · third-party
compromise · insider mistakes (human error).

### 6.5 OWASP Top 10 (2021) → IDRM relevance → key mitigations
| OWASP risk | Relevance to IDRM | Key mitigations |
|---|---|---|
| A01 Broken Access Control | Unauthorized access to incidents, resources, admin | RBAC, least privilege, policy enforcement |
| A02 Cryptographic Failures | Weak encryption, hard-coded secrets | TLS 1.2+, encryption at rest, secrets management |
| A03 Injection | SQL/NoSQL/command injection via APIs/inputs | Input validation, parameterized queries, ORM |
| A04 Insecure Design | Missing threat modeling | Secure SDLC, threat modeling, design reviews |
| A05 Security Misconfiguration | Open ports, default creds | Hardening, config management, patching |
| A06 Vulnerable Components | Outdated libraries | Dependency scanning, timely updates |
| A07 Identification & Auth Failures | Weak auth, credential stuffing | OIDC, MFA, rate limiting, account lockout |
| A08 Software & Data Integrity | Unsigned updates, tampered data | Code signing, checksums, integrity controls |
| A09 Security Logging Failures | Insufficient logging/monitoring | Centralized logs, alerts, retention |
| A10 Server-Side Request Forgery | SSRF via internal URLs/metadata | Egress filtering, URL validation |

### 6.6 Risk assessment
Each risk is rated by **likelihood × impact** into Low / Medium / High / Critical, and mitigations are
prioritised accordingly (Critical and High first).

### 6.7 Practices
Identify assets & data flows → define trust boundaries → identify threats (STRIDE + OWASP) → assess & prioritise
risks → define mitigations & controls → validate through testing → review regularly and after changes.

---

## 7. Security controls at a glance

| Control | Purpose |
|---|---|
| **HTTPS / TLS** | Encrypt all traffic. |
| **JWT / session security** | Protect authenticated sessions. |
| **RBAC (extensible to ABAC)** | Enforce who can do what. |
| **Input validation** | Reject malformed/malicious data. |
| **CSRF protection** | Stop forged requests from other sites. |
| **XSS protection** | Prevent malicious scripts in the browser. |
| **SQL-injection protection** | Safe database access via the ORM. |
| **Rate limiting** | Blunt brute-force and abuse. |
| **File-upload validation** | Ensure uploaded files are safe. |
| **Security headers** | Harden the browser's behaviour. |
| **Audit trails** | Record actions for accountability. |

---

## 8. Compliance

IDRM aligns its security and privacy practices with recognised standards:

- **ISO/IEC 27001** — information security management.
- **NIST Cybersecurity Framework (CSF)** — identify, protect, detect, respond, recover.
- **OWASP Top 10 & OWASP ASVS** — web risks and application security verification.
- **DPDP Act, 2023 (India)** — digital personal data protection and privacy.
- **WCAG 2.1 / 2.2 AA** — accessibility (security must never lock people out unfairly).

The reasoning behind key security choices is recorded for maintainers in
[`99-decisions-and-history.md`](99-decisions-and-history.md).

---

## Where this leads

- How these controls are tested → [`06-quality.md`](06-quality.md)
- How audit, monitoring, and recovery run day to day → [`07-operations.md`](07-operations.md)
- Any unfamiliar term → [`90-glossary.md`](90-glossary.md)

---

*"Secure by design. Trust by default."*
