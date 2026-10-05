# IDRM Instructions — API Gateway

> Spoke of [`../instructions.txt`](../instructions.txt). Thin router: decisions + pointers, not a doc copy.
> **Phase rule:** a gateway is **FFP only**. The MVP FastAPI monolith serves directly (no gateway, no NGINX).

## Decision — APISIX (retained) vs Kong (evaluated 2026-08-14)
For the **free/open, on-prem** build, **Apache APISIX** is chosen. In their OSS editions APISIX ships
**OIDC (`openid-connect`), OAuth2.1/PKCE via an IdP, WAF/OWASP-CRS (`coraza-waf`), advanced rate-limiting,
request validation, and admin RBAC** as **free** plugins — several of which **Kong gates behind paid
Enterprise**. IDRM needs OIDC + OAuth2.1+PKCE + OWASP on a free self-hosted stack → APISIX wins on
cost-to-capability. **Kong stays valid only if** Kong Enterprise is purchased or the team prefers its
ecosystem — that is a **new decision to raise with the user**, never a silent swap.

## Gateway responsibilities (APISIX plugin in [brackets])
- Load balancing / upstream mgmt + active & passive **health checks**
- AuthN/Z: JWT [jwt-auth] · OAuth2.1+PKCE / OIDC [openid-connect] · Keycloak/OPA [authz-keycloak, opa] · HMAC
- Request routing (host/path/method/header/priority)
- Rate-limiting & throttling [limit-req, limit-count, limit-conn]
- Response caching + static-object serving [proxy-cache]
- Protocol translation: HTTP/2, gRPC & gRPC-Web, gRPC↔REST [grpc-transcode], WebSocket, TCP/UDP stream
- Request/response transformation [proxy-rewrite, response-rewrite]
- Security: CORS [cors] · CSRF [csrf] · IP/UA limits [ip-restriction, ua-restriction] · TLS+certs [ssl] ·
  OWASP Top-10 [coraza-waf]
- Traffic control: circuit breaker [api-breaker] · canary [traffic-split] · mirroring [proxy-mirror]
- Observability: [prometheus, opentelemetry, skywalking, http/kafka-logger]

Engine: OpenResty/NGINX + Lua, **etcd** config store, hot plugin reload.
**Edge/BFF** (Bun/Node/Deno) runs **behind** the gateway to compose per-client responses — the public
`/api/v1` contract is never forked. See [`backend-services.md`](backend-services.md).

## Canonical docs
- [`../idrm-ffp-docs/20-architecture-system.md`](../idrm-ffp-docs/20-architecture-system.md) ·
  [`../idrm-ffp-docs/21-architecture-decisions.md`](../idrm-ffp-docs/21-architecture-decisions.md)
- Auth specifics: [`security.md`](security.md)

## Trusted external references
- Apache APISIX — apisix.apache.org/docs · plugin hub — apisix.apache.org/plugins
- Kong Gateway (comparison) — docs.konghq.com · OWASP Coraza — coraza.io
- OWASP API Security Top 10 — owasp.org/API-Security
