# Secure Coding 101

> *Type: Guide (101 / foundational) · Audience: developers (readable by all) · Status: MVP — current · Track: Security (#24)*
> *Most breaches come from ordinary coding mistakes, not master hackers. This guide covers the everyday habits
> that keep IDRM safe — framed around the OWASP Top 10 and IDRM's own rules (including India's DPDP Act).*

---

## 1. The mindset: never trust input

The root cause of most vulnerabilities is trusting data you shouldn't. **Every input from outside — form fields,
URLs, API bodies, uploaded files — is untrusted until validated.** Secure coding is mostly the discipline of
distrust, applied consistently.

The **OWASP Top 10** is the industry's list of the most common web risks; the habits below map to it.

---

## 2. The big classes of bug (and how IDRM avoids them)

- **Injection (e.g. SQL injection)** — attacker input becomes part of a command. *Never* build SQL by gluing
  strings. IDRM uses **SQLAlchemy** with **parameterised queries**, so input is treated as data, not code.
- **Cross-Site Scripting (XSS)** — malicious script injected into a page. Escape/encode output; in the future
  React frontend, rely on its auto-escaping and forbid `dangerouslySetInnerHTML` on unsanitised data.
- **Broken authentication/authorization** — covered in [IAM 101](iam-101.md) and [RBAC/ABAC 101](rbac-abac-101.md):
  check permissions **on the server**, every time.
- **Security misconfiguration** — default passwords, verbose errors, open ports. Ship safe defaults; strict CORS;
  **TLS/HTTPS everywhere**.
- **Sensitive data exposure** — see privacy (§4).

---

## 3. Input validation, the IDRM way

- Validate **at the boundary** with **Pydantic** schemas — type, range, allowed enum values (e.g. `priority`
  must be one of low/medium/high/critical). Reject early with a clear error `code`.
- Client-side validation is for UX; the **server is always the authority** (an attacker can bypass the browser).
- Uploaded files are validated too: type, size (≤10 MB), dimensions — see privacy next.

---

## 4. Privacy & secrets (DPDP Act 2023)

IDRM handles disaster victims' data, so privacy is a hard requirement:

- **Strip EXIF/GPS** from uploaded photos before storing; compress/resize per the media rules. The face
  **detection-only** quality gate stores nothing biometric (recognition is a consented FFP feature).
- **No personal data in logs, URLs, or query strings.** Logs must never contain tokens or passwords
  (see [Observability 101](observability-101.md)).
- **Secrets** (DB passwords, signing keys) live in environment/secret storage — **never** hard-coded or committed
  to Git. No secret ever ships in frontend code.

---

## 5. Everyday secure habits

- **Least privilege** — code, users, and services get the *minimum* access they need.
- **Fail safe** — on error, deny by default; don't leak stack traces to users.
- **Keep dependencies updated** — known-vulnerable libraries are a top breach vector.
- **Review security in PRs** — a second set of eyes catches most issues (Threat Modeling 101 goes deeper — FFP).

---

## 6. Mastery check

1. State the core secure-coding mindset in one sentence.
2. Explain **SQL injection** and **XSS**, and how IDRM prevents each.
3. Explain why server-side **validation** is authoritative over the browser.
4. List IDRM's privacy rules for uploads and logs (DPDP Act).
5. Explain **least privilege** and where **secrets** must (not) live.

---

## 7. Go deeper

- OWASP Top 10 — owasp.org/www-project-top-ten · OWASP Cheat Sheets — cheatsheetseries.owasp.org ·
  OWASP ASVS — owasp.org/www-project-application-security-verification-standard
- India DPDP Act 2023 — meity.gov.in · security spoke [`../../instructions/security.md`](../../instructions/security.md)
- Related: [IAM 101](iam-101.md) · [RBAC/ABAC 101](rbac-abac-101.md) · [Secure Coding ↔ Testing](testing-101.md)

---
*Next:* Testing 101 (Quality track) · *Up:* [Learning Paths](../00-start-learning-paths.md)
