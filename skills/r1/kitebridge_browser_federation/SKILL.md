---
name: kitebridge-browser-federation
description: Route public-page browser capture through Cloudflare Kitesurf with strict target policy, bounded evidence, and Chromium fallback boundaries.
---

# KITEBRIDGE Browser Federation Skill

## Capabilities
- kitebridge:classify_task — select Kitesurf or Chromium based on task requirements
- kitebridge:build_chromium_guardrails — create exact-host Cloudflare Browser Run guardrails for Chromium sessions
- kitebridge:capture_public_page — capture allowlisted public pages with Kitesurf
- kitebridge:verify_evidence — validate local evidence hashes without overstating source trust
- kitebridge:benchmark_route — compare compatible public tasks against Chromium

## Roots

| Root | Path | Responsibility |
|---|---|---|
| integration | integrations/kitebridge/ | Provider implementation and routing primitives |
| tests | tests/test_kitebridge_kitesurf.py and tests/test_kitebridge_routing.py | Fake-transport safety and route-policy contract tests |
| docs | docs/kitebridge-browser-federation.md | Architecture, configuration and activation gates |

## Routing rules

Apply HTTPS, exact-host allowlist, default-port, credential-free, fragment-free, non-IP, and URL-length checks before selecting either browser engine. Authenticated, persistent, WebGL/video, or bot-challenge tasks may select Chromium only after that common target policy passes. Never pass user cookies, passwords, authorization headers, or provider credentials to a page. Do not expose an unauthenticated self-hosted Kitesurf endpoint.

Kitesurf does not support Cloudflare Browser Run guardrails. Its initial URL allowlist does not constrain redirects or subresource requests. Do not send untrusted arbitrary URLs to Kitesurf until a browser-service-enforced or trusted egress proxy boundary exists.

Chromium Browser Run sessions using Puppeteer or Playwright must receive Cloudflare's `guardrails.allowedDomains` option at session creation. Use the helper below and fail closed if it cannot produce a valid exact-host list.

### kitebridge:classify_task

~~~python
route = select_browser_route(task, allowed_hosts=approved_hosts)
# "chromium" is only eligible when the session launcher applies guardrails.
# "kitesurf" is limited to trusted allowlisted origins until egress enforcement exists.
~~~

### kitebridge:build_chromium_guardrails

~~~python
guardrails = build_chromium_guardrails(allowed_hosts=approved_hosts)
# Pass as the guardrails option to Puppeteer/Playwright browser launch.
# Example shape: {"allowedDomains": ["docs.example.com"]}
~~~

### kitebridge:capture_public_page

~~~python
adapter = KitesurfBrowserAdapter()
evidence = adapter.capture("https://docs.example.com/guide", task_id="docs-check-001")
# Evidence is LIVE/PENDING; hashes are integrity checks, not source verification.
~~~

### kitebridge:verify_evidence

~~~python
assert KitesurfBrowserAdapter.verify_evidence(evidence)
# Never upgrade PENDING to VERIFIED based on hashes alone.
~~~

### kitebridge:benchmark_route

~~~text
Use the same public URL/task corpus on Kitesurf and Chromium.
Record compatibility, wall time, CPU, memory, output bytes, extraction accuracy,
and failure rate. Keep authenticated and challenge pages out of the Kitesurf corpus.
~~~
