# KITEBRIDGE Validation Ledger

Append-only evidence log for the KITEBRIDGE implementation on PR #424. This file records observed CI outcomes; it is not a deployment record.

## 2026-11-15 · Guarded Chromium session lifecycle

### Implementation under test

- Chromium session creation uses Cloudflare Browser Run REST endpoint POST /accounts/{account_id}/browser-run/devtools/browser.
- Guardrails are included in the session creation JSON body.
- Session keep-alive is bounded to 10,000–1,200,000 milliseconds.
- Returned session ID and websocket endpoint are validated.
- Session cleanup uses DELETE on the session endpoint; 404 is treated as already expired.
- Policy compiler supports up to 50 allowedDomains and four allowedDomainSets, with explicit no-network mode.
- Domain-set-only policies omit allowedDomains. An explicit empty allowedDomains list is reserved for deny-all mode.
- No live Cloudflare Browser Run requests were made; tests use an injected fake transport.

### CI run on prior head

Commit: b53369c6d71cae657bc83f0e90edd3e20d751714

| Check | Observed result |
|---|---|
| Secret guard #119 | PASS |
| CI v2 #966 gate | PASS |
| CI v2 #966 lint | PASS |
| CI v2 #966 Docker | PASS |
| Primary CI #2938 lint | PASS |
| Primary CI #2938 Docker | PASS |
| Primary CI #2938 Vercel runtime contract | PASS |
| Python 3.11 full suite | FAIL: 2,985 passed, 1 failed |
| Python 3.12 full suite | FAIL: 2,985 passed, 1 failed |

Both Python failures were the same test-harness defect in tests/test_kitebridge_chromium.py. FakeTransport initialized its response with a truthiness fallback, so an intentionally empty dictionary was replaced by a valid default session response. The test test_invalid_session_response_is_rejected therefore did not exercise the intended malformed response.

### Correction

Commit: 6bd989767cced3ea4de21ea002b68652b7fed88d

FakeTransport now uses the default response only when response is None. An explicit empty dictionary is preserved and should cause the launcher to reject the malformed response.

### Current verification boundary

Latest code head at the time of this entry: 6bd989767cced3ea4de21ea002b68652b7fed88d.

Fresh GitHub Actions runs for this exact head had not surfaced at the time this entry was written. The failed prior run is not evidence that the fix passed. Do not mark the Python matrix green until new Python 3.11 and 3.12 full-suite jobs complete successfully.

Vercel GitHub status contexts reported build-rate-limit failures on the prior head. A separate Vercel Deployments status context was successful on that prior head. These are distinct from Python test results. The connected Vercel plugin returned no IXPANSION project or deployment records in the selected team scope; treat this as a connector visibility/scope gap, not proof that the project does not exist.

No merge, production deployment, live Cloudflare API call, or runtime secret provisioning occurred.
