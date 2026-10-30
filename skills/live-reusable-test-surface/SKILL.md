---
name: live-reusable-test-surface
version: 0.1.0
description: Launch a reusable browser-like test surface or canvas for previewing web apps, local development servers, deployed previews, and isolated HTML fixtures.
---

# Live Reusable Test Surface

## Purpose
Provide a reusable visual surface for testing a URL or HTML fixture without rebuilding a new test page for each run. Use when reviewing a web UI, PR preview, local dev server, Holodeck renderer, or canvas prototype.

## Modes
- URL mode: Load an HTTP(S) target inside a sandboxed iframe.
- Fixture mode: Paste self-contained HTML into a separate preview window or save it as a local fixture.
- Viewport mode: Test common desktop, tablet, and mobile viewport sizes.
- Reload/reset: Reload the target, clear the current target, and reset the viewport.
- Evidence mode: Record target URL, viewport, timestamp, expected behavior, observed behavior, and screenshots/logs supplied by the browser runner.

## Workflow
1. Identify the target: deployed preview URL, local development URL, or HTML fixture.
2. Open assets/test-surface.html in a browser or serve the containing directory from a local development server.
3. Enter the target URL and press Load. Only HTTP and HTTPS URLs are accepted.
4. Select a viewport preset and check responsive layout, navigation, forms, loading states, and visible runtime failures.
5. Repeat with reload and reset to check repeatability.
6. Record results as PASS, FAIL, or BLOCKED. Never mark a test passed merely because the page rendered.
7. If the target blocks iframe embedding with CSP frame-ancestors or X-Frame-Options, use Open separately and test the page directly. Do not attempt to bypass the site's framing policy.
8. For automated testing, prefer Playwright or the project's existing browser test harness. This visual surface is a manual preview tool, not an automation runner.

## Safety and limitations
- Treat the target page as untrusted content.
- The preview iframe is sandboxed. Some apps requiring popups, downloads, authentication flows, or top-level navigation may not work inside it.
- Cross-origin browser security prevents this page from reading the target's DOM, console, network responses, or internal state.
- Do not enter secrets into unfamiliar targets.
- Do not disable browser security, relax the iframe sandbox, or bypass CSP.
- A local URL is reachable only from the browser's machine/network. A hosted sandbox cannot automatically reach a user's localhost.
- The surface itself does not create a persistent remote browser session; persistence comes from keeping the page open or re-opening the same fixture.

## Test record template
- Target:
- Commit / branch:
- Browser and OS:
- Viewport:
- Expected:
- Observed:
- Result: PASS / FAIL / BLOCKED
- Evidence:
- Follow-up:
