# IDRM Instructions — Security & IAM

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Rule:** the **API is the security boundary**. UI hiding is UX, never enforcement — the server re-checks every call.

## Authentication & authorization
- **MVP (LOCKED):** RS256 **JWT** — short access (~60 min) + rotating, revocable **refresh** (~7 d).
  **RBAC** over 4 roles (`citizen`, `provider`, `coordinator`, `admin`) + a narrow **guest** path.
  NIST-aligned passwords (length > composition, **bcrypt cost 12**), **5-attempt / 15-min lockout**.
- **FFP additions:** OIDC/SSO, **OAuth 2.1 + PKCE**, MFA, **ABAC**, full role hierarchy + Auditor role —
  via an IdP (e.g. Keycloak) fronted by the gateway ([`api-gateway.md`](api-gateway.md)).
- Token storage (clients): access in **memory**; refresh in **httpOnly+Secure+SameSite cookie** (web) /
  secure device storage (RN). **Never `localStorage`.**

## Application security
- **OWASP Top-10** + **OWASP API Security Top-10** mitigation is a build requirement; WAF at the gateway
  (`coraza-waf` / OWASP CRS) in FFP.
- **TLS/HTTPS everywhere**, cert management at the gateway/edge; strict CSP; CORS locked to known origins.
- No secrets in code/bundles; secrets via env/vault. **No PII in URLs/query strings.**

## Privacy & compliance (India)
- **DPDP Act 2023**: media is compressed + **EXIF/GPS stripped** client-side; **face DETECTION-only** quality
  gate (nothing biometric stored). Recognition/matching = consented **FFP** feature.
- Per-request privacy levels (Public/Protected/Private) = FFP. Full audit trail via the `audit` module.

## Canonical docs
- [`../idrm-ffp-docs/22-architecture-security-and-iam.md`](../idrm-ffp-docs/22-architecture-security-and-iam.md)
- Frontend security: [`../idrm-ffp-docs/61-frontend-engineering-standards.md`](../idrm-ffp-docs/61-frontend-engineering-standards.md) §9–10

## Trusted external references
- OWASP Top 10 — owasp.org/www-project-top-ten · OWASP API Security Top 10 — owasp.org/API-Security ·
  OWASP ASVS — owasp.org/www-project-application-security-verification-standard
- NIST SP 800-63-4 / 800-63B (digital identity) — pages.nist.gov/800-63-4 · NIST CSF 2.0 — nist.gov/cyberframework
- OAuth 2.1 — oauth.net/2.1 · OIDC — openid.net/connect · JWT — datatracker.ietf.org/doc/html/rfc7519
- India DPDP Act 2023 — meity.gov.in
