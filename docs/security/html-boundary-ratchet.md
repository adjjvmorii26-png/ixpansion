# HTML Boundary Ratchet

IXPANSION uses two complementary gates:

1. Full inventory (scripts/audit_html_sinks.py) records existing sink debt across the repository.
2. Boundary Ratchet (scripts/html_boundary_ratchet.py) blocks sink patterns introduced or modified on added HTML lines in a pull request.

This avoids two bad extremes: ignoring newly introduced injection surfaces, or blocking every unrelated PR because of old dashboard debt.

## How it works

The ratchet diffs the PR against its base with zero-context hunks, maps added/modified lines, runs the existing sink inventory against changed HTML files, and fails when a detected sink is on one of those lines. It emits html-boundary-ratchet.json for review and CI artifact retention.

## Preferred rendering patterns

- Plain text: textContent or createTextNode.
- Structured UI: createElement, set validated properties, then replaceChildren.
- Rich HTML: a maintained sanitizer with a narrow allowlist and explicit context.
- Avoid string-built HTML from API, URL, storage, or user-controlled values.
- Avoid inline event handlers; use addEventListener.

## Exception handling

There is intentionally no broad ignore switch. If a sink is required, replace it with a safe DOM construction pattern where possible. If a finding is a false positive, document the exact file/line, reason, reviewer, and expiry in the PR discussion. Do not silently whitelist an entire directory.

## Limits

This is a regression ratchet, not a complete taint analyzer. It does not prove that an unchanged sink is safe, nor does it catch every multi-line data flow. The full inventory remains advisory and all findings still need source-to-sink review. Browser testing is a separate validation layer.
