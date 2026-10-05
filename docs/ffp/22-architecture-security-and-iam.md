# IDRM FFP — Security & IAM Design (Enterprise)

> *Type: Document (specification) · Audience: security reviewers, developers · Status: FFP — next-phase (planned)*
> *Extends the MVP security doc [`../idrm-mvp-docs/22-architecture-security-and-iam.md`](../mvp/22-architecture-security-and-iam.md). States the **enterprise controls** the MVP deferred (§9 there). Aligns with the authoritative [`../../docs/05-security.md`](../../docs/05-security.md) and the blueprint's identity guidance (NIST SP 800-63-4 family).*

> **Principle:** MVP security (RS256 JWT, RBAC, TLS, bcrypt, audit, DPDP posture) **remains in force**. The
> FFP adds **zero-trust across services**, federated identity, and policy-based authorization — introduced
> per the triggers in [`21-architecture-decisions.md`](21-architecture-decisions.md).

> **FFP acronyms (expanded once):** **OIDC** = OpenID Connect (federated login on top of OAuth) · **SSO** =
> Single Sign-On · **MFA** = Multi-Factor Authentication · **ABAC** = Attribute-Based Access Control (rules from
> attributes like area/jurisdiction, beyond role) · **mTLS** = mutual TLS (both sides present certificates) ·
> **WAF** = Web Application Firewall · **KMS / Vault** = Key Management Service / secrets vault · **SIEM** =
> Security Information & Event Management · **Zero-trust** = never trust by network location; verify every call.

---

## 1. What the FFP adds (vs MVP)

| Area | MVP | FFP |
|---|---|---|
| Sign-in | email+password | **OIDC / SSO** (agency IdPs), **OAuth 2.1 + PKCE** |
| Second factor | — | **MFA / OTP** |
| Authorization | RBAC (4 roles) + ownership | **RBAC + ABAC** (area / jurisdiction / org policy) |
| Roles | citizen/provider/coordinator/admin | **full hierarchy** + read-only **Auditor** |
| Tokens | RS256 JWT (app-signed) | same, **verified at the APISIX gateway** (`openid-connect`/`jwt-auth`) |
| Service-to-service | in-process | **mTLS**, zero-trust, per-service identities |
| Secrets | env vars / `.env` | **secrets vault / KMS**, rotation |
| At rest | transport + hashing | **field-level PII AES-256** at rest |
| Biometrics | detection only (no data stored) | **FaceNet recognition** with **explicit consent** + DPDP safeguards |

## 2. Identity & authentication
- **OIDC/SSO** lets agencies bring their own identity providers; IDRM is a relying party.
- **OAuth 2.1 + PKCE** for public clients (React SPA, React Native).
- **MFA** for privileged roles (coordinator/admin/auditor) and sensitive actions.
- The gateway (APISIX) **verifies tokens centrally** before routing; services trust the verified identity.
- Guidance: **NIST SP 800-63-4 / 800-63B-4** (supersedes older editions).

## 3. Authorization — RBAC + ABAC
RBAC (from MVP) is extended with **ABAC**: policies evaluate **attributes** — the actor's org/jurisdiction,
the resource's area/owner, event membership — so a district coordinator sees only their jurisdiction, a
provider only their org's assignments. Policy is evaluated at the gateway and/or service (e.g. OPA). The
full role hierarchy (Volunteer/Organizer/Manager/Executive/Event-Admin/**Auditor**/SysAdmin) is realised here.

## 4. Zero-trust across services
Never trust the network: **mTLS** between services, per-service identities, least-privilege service accounts,
and gateway-enforced authN/authZ on every hop. Segmented trust zones (public → edge → application → data).

## 5. Data protection at scale
TLS 1.3 everywhere; **field-level AES-256** for PII at rest; **secrets vault/KMS** with rotation; encrypted
backups; per-service least-privilege DB/MinIO accounts. Object storage stays private (pre-signed URLs).

## 6. Biometric handling (FaceNet) — consent-first
Missing-person matching uses biometric **embeddings** — **only** with **explicit, purpose-limited consent**,
strict **retention limits**, access confined to authorized roles, full audit, and **DPDP Act 2023**
safeguards. This is a deliberate, guarded reversal of the MVP's deferral (FFP-ADR-014).

## 7. Audit, threat model & compliance
Append-only audit extends across services (correlation IDs tie a request end-to-end). Threat modelling
(STRIDE + OWASP) per service; abuse cases; secure SDLC; vulnerability management (SAST/SCA/DAST — see
[`70-quality-test-strategy.md`](70-quality-test-strategy.md)). Compliance: **DPDP Act 2023**, **NIST CSF 2.0**,
**ISO/IEC 27001**, OWASP ASVS, WCAG 2.2.

---

*Related:* [`25-module-elucidation.md`](25-module-elucidation.md) · [`26-conformance-pics.md`](26-conformance-pics.md) · [`20-architecture-system.md`](20-architecture-system.md) · [`21-architecture-decisions.md`](21-architecture-decisions.md) ·
[`40-api-specification.md`](40-api-specification.md) · MVP security [`../idrm-mvp-docs/22-architecture-security-and-iam.md`](../mvp/22-architecture-security-and-iam.md) ·
[`../../docs/05-security.md`](../../docs/05-security.md).
