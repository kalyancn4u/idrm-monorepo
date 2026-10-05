# Security Testing 101

> *Type: Guide (101 / foundational) · Audience: novices → developers/QA · Status: MVP-aware (deepens in FFP) · Track: Quality (#29)*
> *Secure coding builds defences in; security testing checks they actually hold. Read
> [Secure Coding 101](secure-coding-101.md) and [Threat Modeling 101](threat-modeling-101.md) first.*

---

## 1. What security testing is

**Security testing** deliberately probes the system for weaknesses an attacker could exploit — turning the
"what could go wrong?" of threat modeling into concrete checks. It complements functional testing: a feature can
work perfectly *and* be insecure.

---

## 2. The main techniques

- **SAST (Static Application Security Testing)** — scans the **source code** for risky patterns (e.g. unsafe SQL,
  hard-coded secrets). Runs early, in CI.
- **DAST (Dynamic Application Security Testing)** — attacks the **running app** from outside (e.g. OWASP **ZAP**),
  probing for injection, XSS, misconfig.
- **Dependency / SCA scanning** — checks third-party libraries for **known vulnerabilities** (a top breach vector).
- **Secrets scanning** — catches passwords/keys accidentally committed to Git.
- **Penetration testing** — skilled humans simulate a real attacker; periodic, deeper, usually FFP.

---

## 3. What to test in IDRM (mapped to what you know)

- **Authentication/authorization:** can a citizen reach a coordinator action? (RBAC — [RBAC/ABAC 101](rbac-abac-101.md))
- **Injection & XSS:** malicious input in incident fields ([Secure Coding 101](secure-coding-101.md)).
- **Access control on the API:** every endpoint under every role ([API Testing 101](api-testing-101.md)).
- **Privacy:** confirm EXIF/GPS stripped, no PII in logs/URLs (DPDP Act).
- **Transport:** TLS enforced; secure token handling.

Much of this is **automatable in CI**, so regressions are caught continuously.

---

## 4. IDRM phasing

- **MVP:** shift-left basics — SAST + dependency + secrets scanning in the pipeline, plus the RBAC/validation
  tests from [API Testing 101](api-testing-101.md). Pragmatic, automated.
- **FFP:** DAST, periodic penetration tests, WAF validation (the gateway's `coraza-waf`), and a formal secure-SDLC
  program as the attack surface grows. See
  [`../../idrm-ffp-docs/22-architecture-security-and-iam.md`](../../../docs/ffp/22-architecture-security-and-iam.md).

---

## 5. Mastery check

1. Explain how security testing differs from functional testing.
2. Define **SAST**, **DAST**, **SCA/dependency scanning**, and pen testing.
3. List IDRM-specific security tests and the guide each connects to.
4. Explain why dependency and secrets scanning matter.
5. State IDRM's MVP vs FFP security-testing posture.

---

## 6. Go deeper

- OWASP ZAP — zaproxy.org · OWASP Testing Guide — owasp.org/www-project-web-security-testing-guide ·
  OWASP Dependency-Check — owasp.org
- Related: [Secure Coding 101](secure-coding-101.md) · [Threat Modeling 101](threat-modeling-101.md) · [API Testing 101](api-testing-101.md)

---
*Next:* [Disaster Drill / Scenario Testing 101](disaster-drill-scenario-testing-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
