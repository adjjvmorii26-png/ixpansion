# KITEBRIDGE // Federated Browser Execution

KITEBRIDGE adds a bounded, evidence-producing browser route to the Connector Federation Layer.

## Routing contract

| Task class | Route | Reason |
|---|---|---|
| Public documentation, JS-rendered public pages, one-shot extraction | Cloudflare Browser Run with browser=kitesurf | Stateless, agent-oriented capture |
| Authenticated dashboards, persistent sessions, WebGL/video, bot/TLS challenge workflows | Chromium-capable Browser Run session | Kitesurf does not currently provide these capabilities |

Kitesurf is experimental. Compatibility must be measured per target rather than inferred from standards-test coverage.

## Adapter

integrations/kitebridge/kitesurf.py exposes KitesurfBrowserAdapter.capture(url, task_id=...). It calls Browser Run /snapshot?browser=kitesurf and requests Markdown, screenshot, and accessibility-tree formats in one request.

Required runtime configuration:
- CLOUDFLARE_ACCOUNT_ID
- CLOUDFLARE_BROWSER_RUN_API_TOKEN with Browser Run edit permission
- IXPANSION_KITESURF_ALLOWED_HOSTS, a comma-separated list of exact hostnames

No page credentials, cookies, basic-auth data, custom page headers, or arbitrary CDP commands are accepted. Both Kitesurf and Chromium route selection apply the same exact-host allowlist and URL safety checks: HTTPS only, default port, no URL credentials, fragments, IP literals, malformed or oversized URLs, or non-allowlisted hosts. Capability flags select the engine only after target policy passes. Payload and response sizes are bounded. The provider token is sent only to the Cloudflare API endpoint.

## Chromium session guardrails

Cloudflare Browser Run documents `guardrails.allowedDomains` for Puppeteer and Playwright sessions. KITEBRIDGE exposes `build_chromium_guardrails(allowed_hosts=...)` to produce a normalized, exact-host-only allowlist. The Chromium session launcher must pass this object as its `guardrails` option. Do not silently omit it or fall back to an unguarded session.

Important limitation: Cloudflare documents that Browser Run guardrails are not supported by Kitesurf. Therefore the helper protects only the Chromium session path. It does not make the Kitesurf Quick Action safe against redirects or subresource egress.

## Evidence contract

Each Kitesurf capture returns source URL, UTC capture time, task ID and engine identity; rendered Markdown, base64 screenshot and accessibility tree; SHA-256 hashes for each representation; state=LIVE and verification=PENDING.

The local verifier checks only payload integrity. It does not prove that the remote page is truthful, current, safe, or authored by the claimed source. A screenshot is evidence of a render, not a trust oracle.

## Security boundary and activation gate

The hostname allowlist validates the initial requested URL. It does not prove that redirects or subresource requests remain within the allowlist, and it is not a complete SSRF/egress boundary. Do not activate Kitesurf for untrusted arbitrary URLs until redirect and outbound-request restrictions are enforced by the browser service or a trusted egress proxy. For Chromium sessions, require the documented Browser Run guardrails to be attached at session creation. Keep the Cloudflare API token in the runtime secret manager; never put it in the outbox, Notion, Drive, logs, or repository.

For self-hosted Kitesurf, require Cloudflare Access or an equivalent authentication layer before exposing any endpoint. Kitesurf has no built-in authentication, and an unprotected endpoint can be abused to browse outbound from the account and consume paid Dynamic Worker resources. Self-hosting requires a Workers Paid plan because it uses Dynamic Workers.

## Validation

Unit tests use a fake transport and make no Cloudflare API requests. Live account connectivity, Browser Run permissions, compatibility, redirect containment, performance, cost, and production activation are not verified by these tests.

## Next gates

1. Run the unit suite and CI on this PR head.
2. Benchmark an agreed public URL corpus against Chromium for compatibility, latency, CPU, memory, extraction accuracy, and output size.
3. Add enforced redirect/egress control for Kitesurf before any untrusted URL support.
4. Implement and integration-test the Chromium session launcher with `build_chromium_guardrails`.
5. Configure runtime secrets and test one explicitly approved public target before enabling scheduled work.
