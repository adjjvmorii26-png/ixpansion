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

No page credentials, cookies, basic-auth data, custom page headers, or arbitrary CDP commands are accepted. The adapter validates the initial target as HTTPS, default-port, credential-free, fragment-free, non-IP, well-formed, bounded, and exact-host-allowlisted. Payload and response sizes are bounded. The provider token is sent only to the Cloudflare API endpoint.

## Chromium session guardrails

Cloudflare Browser Run session guardrails restrict HTTP and HTTPS requests made by Puppeteer, Playwright, and CDP sessions. The restriction applies to navigation, redirects, and page dependencies such as APIs, scripts, images, and fonts. The policy is fixed for the session lifetime.

KITEBRIDGE exposes build_chromium_guardrails(...) to compile a validated Cloudflare guardrail object:
- Up to 50 allowedDomains hostname patterns.
- Up to four allowedDomainSets references.
- Exact hostnames and one leading wildcard pattern such as *.example.com.
- Domain-set-only policies emit allowedDomainSets without an empty allowedDomains property. Cloudflare interprets an explicit empty allowedDomains array as deny-all.
- Explicit allow_no_network=True produces {"allowedDomains": []}, which blocks all HTTP/HTTPS requests; it cannot be combined with domains or domain sets.
- Omitting both allowlist properties is rejected by the helper because Cloudflare treats that as unrestricted network access.

KITEBRIDGE now provides CloudflareChromiumSessionLauncher, which POSTs the compiled policy to Browser Run's documented /devtools/browser session-creation endpoint and returns a BrowserSessionLease containing the session ID, websocket URL, policy, and bounded keep-alive. The websocket URL is hidden from the lease repr to reduce accidental log exposure. close(lease) releases the session and treats an already-expired 404 as successful cleanup. The launcher never creates a session without an explicit allowlist or explicit no-network policy. Its fake-transport tests do not make Cloudflare API calls. Cloudflare's guardrails are session-level request controls, not a general policy for every Cloudflare product.

Outbound Worker exception: Cloudflare documents that HTTP requests routed through outboundByHost to an outbound Worker are handled by that Worker rather than the normal network path. The Worker must apply its own destination policy. KITEBRIDGE does not configure outbound Workers.

## Kitesurf limitation

Cloudflare explicitly states that Browser Run guardrails are unavailable for Quick Actions, including the Kitesurf snapshot path used by this adapter. Therefore the initial exact-host URL validation does not constrain redirects or subresource requests made by Kitesurf. Do not send untrusted arbitrary URLs to Kitesurf until an independently enforced browser-service or trusted egress-proxy boundary exists. Keep the current Kitesurf allowlist limited to trusted, controlled origins.

## Evidence contract

Each Kitesurf capture returns source URL, UTC capture time, task ID and engine identity; rendered Markdown, base64 screenshot and accessibility tree; SHA-256 hashes for each representation; state=LIVE and verification=PENDING.

The local verifier checks only payload integrity. It does not prove that the remote page is truthful, current, safe, or authored by the claimed source. A screenshot is evidence of a render, not a trust oracle.

## Security and activation gates

- Keep the Cloudflare API token in the runtime secret manager; never put it in the outbox, Notion, Drive, logs, or repository.
- For self-hosted Kitesurf, require Cloudflare Access or equivalent authentication before exposing any endpoint.
- Never enable arbitrary untrusted Kitesurf URLs without independent egress enforcement.
- Never create a Chromium session without a compiled, non-empty allowlist or an explicit no-network policy.
- Verify blocked requests using Cloudflare's documented guardrail response headers before declaring the integration active.

## Validation

Unit tests use deterministic inputs and no Cloudflare API requests. Live account connectivity, Browser Run permissions, compatibility, guardrail enforcement, performance, cost, and production activation are not verified by these tests.

## Next gates

1. Run the unit suite and CI on this PR head.
2. Exercise the Chromium session launcher against a staging Cloudflare account and prove an off-allowlist request is blocked, checking Cloudflare's documented response headers.
3. Benchmark an agreed public URL corpus against Chromium for compatibility, latency, CPU, memory, extraction accuracy, and output size.
4. Add independent redirect/egress control for Kitesurf before any untrusted URL support.
5. Configure runtime secrets and test one explicitly approved public target before enabling scheduled work.
