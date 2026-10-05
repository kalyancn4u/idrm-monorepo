# OAuth 2.1 + PKCE 101

> *Type: Guide (101 / foundational) · Audience: novices → developers · Status: **FFP** — next-phase · Track: Security (#20)*
> *How can an app get permission to act on your behalf **without** you handing it your password? OAuth. This
> guide explains OAuth 2.1 and the PKCE protection. It pairs with [OIDC 101](oidc-101.md); both are **FFP**.*

---

## 1. What OAuth is (and isn't)

**OAuth** is a standard for **delegated authorization** — letting one app access certain resources on your behalf
without seeing your password. Classic example: letting an app read your calendar without giving it your Google
password.

- OAuth = **authorization** ("what may this app do for me?").
- It is *not* authentication by itself — proving *who you are* is OIDC's job, layered on top ([OIDC 101](oidc-101.md)).

**OAuth 2.1** is the consolidated, security-hardened update of OAuth 2.0 — it folds in years of best practice and
removes unsafe legacy flows.

---

## 2. The cast and the tokens

- **Resource Owner** — you, the user.
- **Client** — the app wanting access (IDRM's web/mobile app).
- **Authorization Server** — issues tokens after the user consents (often the same IdP as OIDC).
- **Resource Server** — the API holding the data (IDRM's `/api/v1`).
- **Access token** — the time-limited "pass" the client presents to the API (as in [IAM 101](iam-101.md)).

---

## 3. The Authorization Code flow — and why PKCE

The recommended flow: the user logs in at the authorization server, which returns a short **authorization code**;
the client swaps that code for an **access token**. The risk: on public clients (mobile apps, browser SPAs) a
malicious app could intercept the code.

**PKCE (Proof Key for Code Exchange, "pixy")** closes that hole:

1. The client makes a secret **code verifier** and sends a hashed version (**code challenge**) when it starts.
2. When exchanging the code for a token, it must present the original verifier.
3. An attacker who steals the code can't use it — they don't have the verifier.

**In OAuth 2.1, PKCE is mandatory** for these flows. (The old "implicit" flow, which exposed tokens in URLs, is
removed.)

---

## 4. How it fits IDRM (FFP)

IDRM's **FFP** uses OAuth 2.1 + PKCE (with OIDC for identity) so its React and mobile clients obtain tokens
securely via an IdP, and partner integrations get **scoped, delegated** access to the API — without password
sharing. The **MVP** stays simpler: direct RS256 JWT login, no third-party delegation. See
[`../../instructions/security.md`](../../../archive/instructions/security.md).

---

## 5. Mastery check

1. Explain **delegated authorization** and how OAuth avoids password sharing.
2. Distinguish OAuth (authorization) from OIDC (authentication).
3. Name the roles and what an **access token** is for.
4. Explain the **Authorization Code** flow and what **PKCE** protects against.
5. State what OAuth 2.1 made mandatory/removed, and IDRM's MVP-vs-FFP position.

---

## 6. Go deeper

- OAuth 2.1 — oauth.net/2.1 · PKCE (RFC 7636) — datatracker.ietf.org/doc/html/rfc7636 · OAuth 2.0 Security BCP
- Related: [OIDC 101](oidc-101.md) · [IAM 101](iam-101.md) · [Secure Coding 101](secure-coding-101.md)

---
*Next:* [MFA 101](mfa-101.md) · *Up:* [Learning Paths](../00-start-learning-paths.md)
