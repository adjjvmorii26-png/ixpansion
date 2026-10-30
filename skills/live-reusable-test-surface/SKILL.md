---
name: live-reusable-test-surface
version: 0.2.0
description: Reusable browser preview surface plus evidence-first Playwright smoke testing for web applications and renderer previews.
---

# Live Reusable Test Surface

## Purpose
Provide a reusable visual surface and a repeatable browser evidence runner for testing web UIs, pull-request previews, local development servers, Holodeck renderers, and canvas prototypes.

## Components
- `assets/test-surface.html`: manual sandboxed iframe preview with viewport presets, reload, reset, and direct-open fallback.
- `scripts/browser-smoke.mjs`: optional Playwright smoke runner that captures a screenshot and JSON evidence report.

## Manual preview workflow
1. Identify a deployed preview URL, local development URL, or HTML fixture.
2. Open `assets/test-surface.html` in a browser or serve the containing directory from a local development server.
3. Enter an HTTP(S) URL and press **Load**.
4. Select a viewport preset and inspect responsive layout, navigation, forms, loading states, and visible failures.
5. Use reload/reset to repeat the visual check.
6. If the target blocks iframe embedding with CSP `frame-ancestors` or `X-Frame-Options`, use **Open separately**. Do not bypass the target's framing policy.
7. Record expected and observed behavior. A frame load event is not proof of application health.

## Automated smoke workflow
The runner is an optional development dependency; it does not add Playwright to the repository's runtime dependencies.

Install in a development environment:
```sh
npm install --save-dev playwright
npx playwright install chromium
```

Run an observation-only check:
```sh
node skills/live-reusable-test-surface/scripts/browser-smoke.mjs https://example.com
```

Observation-only runs produce a **REVIEW** result, not PASS, because no expected behavior was asserted.

Run with explicit assertions:
```sh
node skills/live-reusable-test-surface/scripts/browser-smoke.mjs https://example.com \
  --expect-title "Example Domain" \
  --expect-text "Example Domain" \
  --viewport 1280x800 \
  --out artifacts/browser-smoke
```

The runner emits a timestamped JSON report and screenshot. Exit codes:
- `0`: assertions passed, or observation-only run completed without a hard failure.
- `1`: navigation, browser execution, or supplied assertion failure.
- `2`: invalid arguments or Playwright missing.

The JSON report records the target, viewport, final URL, main document status, page title, uncaught page errors, console errors, failed requests, HTTP error responses, assertion outcomes, screenshot path, and result. Review console errors and failed subrequests as evidence; not every subrequest failure necessarily means the application itself failed.

## Safety and limitations
- Treat target pages as untrusted content. Do not enter secrets into unfamiliar targets.
- The manual iframe uses a sandbox. Some apps requiring popups, downloads, authentication flows, or top-level navigation may not work within it.
- Cross-origin browser security prevents the manual surface from reading target DOM, console, network responses, or internal state.
- The Playwright runner opens the target directly in a separate headless Chromium session. It does not bypass CSP, perform login, submit forms, or attempt to evade access controls.
- A local URL is reachable only from the machine running the browser. A hosted runner cannot automatically reach a developer's localhost.
- The runner is a smoke-test primitive, not a full test suite. Assertions must encode meaningful expected behavior, and screenshot presence alone does not prove correctness.
- The runner writes evidence to the selected output directory. Keep generated artifacts out of version control unless they are intentionally reviewed and committed.

## Evidence record template
- Target:
- Commit / branch:
- Browser and OS:
- Viewport:
- Expected:
- Observed:
- Result: PASS / FAIL / REVIEW / BLOCKED
- Evidence report:
- Screenshot:
- Follow-up:
