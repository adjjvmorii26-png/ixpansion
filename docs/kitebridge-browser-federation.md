# KITEBRIDGE // Federated Browser Execution

KITEBRIDGE adds a bounded, evidence-producing browser route to the Connector Federation Layer.

## Routing contract

| Task class | Route | Reason |
|---|---|---|
| Public documentation, JS-rendered public pages, one-shot extraction | Cloudflare Browser Run with browser=kitesurf | Stateless, agent-oriented capture |
| Authenticated dashboards, persistent sessions, WebGL/video, bot/TLS challenge workflows | Chromium-capable Browser Run path | Kitesurf does not currently provide these capabilities |

Kitesurf is experimental. Compatibility must be measured per target rather than inferred from standards-test coverage.

## Adapter

integrations/kitebridge/kitesurf.py exposes KitesurfBrowserAdapter.capture(url, task_id=...). It calls Browser Run /snapshot?browser=kitesurf and requests Markdown, screenshot, and accessibility-tree formats in one request.

Required runtime configuration:
- CLOUDFLARE_ACCOUNT_ID
- CLOUDFLARE_BROWSER_RUN_API_TOKEN with Browser Run edit permission
- IXPANSION_KITESURF_ALLOWED_HOSTS, a comma-separated list of exact hostnames

No page credentials, cookies, basic-auth data, custom page headers, or arbitrary CDP commands are accepted. Only HTTPS on the default port is accepted. The exact hostname must be allowlisted. Payload and response sizes are bounded. The provider token is sent only to the Cloudflare API endpoint.

## Evidence contract

Each capture returns source URL, UTC capture time, task ID and engine identity; rendered Markdown, base64 screenshot and accessibility tree; SHA-256 hashes for each representation; state=LIVE and verification=PENDING.

The local verifier checks only payload integrity. It does not prove that the remote page is truthful, current, safe, or authored by the claimed source. A screenshot is evidence of a render, not a trust oracle.

## Security boundary and activation gate

The hostname allowlist validates the initial requested URL. It does not prove that redirects or subresource requests remain within the allowlist, and it is not a complete SSRF/egress boundary. Do not activate this adapter for untrusted arbitrary URLs until redirect and outbound-request restrictions are enforced by the browser service or a trusted egress proxy. Keep the Cloudflare API token in the runtime secret manager; never put it in the outbox, Notion, Drive, logs, or repository.

For self-hosted Kitesurf, require Cloudflare Access or an equivalent authentication layer before exposing any endpoint. Kitesurf has no built-in authentication, and an unprotected endpoint can be abused to browse outbound from the account and consume paid Dynamic Worker resources. Self-hosting requires a Workers Paid plan because it uses Dynamic Workers.

## Validation

Unit tests use a fake transport and make no Cloudflare API requests. Live account connectivity, Browser Run permissions, compatibility, redirect containment, performance, cost, and production activation are not verified by these tests.

## Next gates

1. Run the unit suite and CI on this PR head.
2. Benchmark an agreed public URL corpus against Chromium for compatibility, latency, CPU, memory, extraction accuracy, and output size.
3. Add redirect/egress enforcement before any untrusted URL support.
4. Configure runtime secrets and test one explicitly approved public target before enabling scheduled work.
