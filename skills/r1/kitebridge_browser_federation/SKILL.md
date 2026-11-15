---
name: kitebridge-browser-federation
description: Route browser tasks through Cloudflare Kitesurf or guarded Chromium sessions with bounded evidence and fail-closed network policy.
---

# KITEBRIDGE Browser Federation Skill

## Capabilities
- kitebridge:classify_task — select Kitesurf or Chromium based on task requirements
- kitebridge:build_chromium_guardrails — compile Cloudflare session-level HTTP/HTTPS request restrictions
- kitebridge:open_guarded_chromium_session — acquire a bounded Chromium session with guardrails attached at creation and close it through its lease
- kitebridge:capture_public_page — capture trusted allowlisted public pages with Kitesurf
- kitebridge:verify_evidence — validate local evidence hashes without overstating source trust
- kitebridge:benchmark_route — compare compatible public tasks against Chromium

## Roots

| Root | Path | Responsibility |
|---|---|---|
| integration | integrations/kitebridge/ | Provider implementation and routing primitives |
| tests | tests/test_kitebridge_kitesurf.py and tests/test_kitebridge_routing.py | Fake-transport safety and route-policy contract tests |
| docs | docs/kitebridge-browser-federation.md | Architecture, configuration and activation gates |

## Network policy

Cloudflare Browser Run guardrails restrict HTTP and HTTPS requests for Puppeteer, Playwright, and CDP sessions, including navigation, redirects, APIs, scripts, images, and fonts. The policy is fixed at session creation. Respect Cloudflare's 50-entry allowedDomains and four-entry allowedDomainSets limits. A missing allowlist is unrestricted, so fail closed.

KITEBRIDGE's helper supports exact hostnames, one leading wildcard such as *.example.com, centrally maintained domain sets, and an explicit no-network mode. It enforces the 50-host and four-domain-set limits, rejects malformed patterns, IP literals, oversized lists, and ambiguous empty policies. For domain-set-only policies it omits allowedDomains; an explicit empty allowedDomains array means deny-all, not an empty contribution to the combined allowlist.

~~~python
from integrations.kitebridge import build_chromium_guardrails

guardrails = build_chromium_guardrails(
    allowed_hosts={"docs.example.com", "*.static.example.com"},
    allowed_domain_sets={"common-cdns"},
)
# Pass as the guardrails option when creating a Browser Run session.
~~~

For a self-contained page that must not access the network:

~~~python
guardrails = build_chromium_guardrails(allow_no_network=True)
# Produces {"allowedDomains": []}; all HTTP/HTTPS requests are blocked.
~~~

Use CloudflareChromiumSessionLauncher from integrations.kitebridge to create and close guarded sessions. Its launch() method posts the compiled guardrails object to Browser Run session creation, enforces the documented 10,000 to 1,200,000 ms keep-alive bounds, validates the returned session ID and websocket URL, and returns a lease whose repr hides the websocket URL. Call close(lease) in a finally block. Do not silently omit the guardrails option or fall back to an unrestricted session. An outbound Worker configured with outboundByHost is a separate request path and must enforce its own destination policy.

## Kitesurf boundary

Cloudflare Browser Run guardrails are unavailable for Quick Actions, including Kitesurf snapshots. The Kitesurf adapter validates only the initial URL; that does not constrain redirects or subresource requests. Keep Kitesurf limited to trusted controlled origins until a browser-service or trusted egress proxy provides independent enforcement.

Never pass page credentials, cookies, authorization headers, or provider secrets to the target page. Do not expose an unauthenticated self-hosted Kitesurf endpoint.

## Evidence

Kitesurf captures are LIVE/PENDING. SHA-256 hashes prove local payload integrity only. Never upgrade PENDING to VERIFIED based on hashes alone.

## Validation and activation

Unit tests use fake transports and do not contact Cloudflare. Before activation:
1. Implement a Chromium session launcher that always supplies compiled guardrails.
2. Prove an off-allowlist request is blocked and verify Cloudflare's documented response headers.
3. Benchmark compatible public pages against Chromium.
4. Keep arbitrary untrusted URLs disabled for Kitesurf until independent egress enforcement is verified.
