---
name: verified-repo-refinement
description: Evidence-led repository auditing and iterative code refinement. Use when scanning a repository, tracing security or reliability risks, making focused fixes, adding regression tests, validating pull requests, or producing an auditable status report.
---

# Verified Repository Refinement

Use this skill to turn repository audits into small, reviewable, test-backed improvements. It is optimized for IXPANSION's large mixed-language monorepo, but the workflow is portable.

## Operating contract

1. **Inspect before editing.** Read repository guidance (AGENTS.md, CONTRIBUTING, CI workflows, package manifests) and inspect the current branch, base SHA, worktree state, and relevant files.
2. **Evidence before claims.** Record exact paths, line numbers, commit SHAs, test commands, exit codes, CI run IDs, and timestamps. A tool returning no data is not a pass.
3. **Trace, don't pattern-match blindly.** A risky API or HTML sink is a review candidate, not proof of a vulnerability. Follow data from source to sink, including sanitization, encoding, trust boundaries, and execution context.
4. **One coherent change per patch.** Prefer one risk, component, or tightly coupled behavior per PR. Avoid repository-wide rewrites and unrelated formatting.
5. **Regression test the behavior.** Add tests that fail before the fix and pass after it. Prefer behavioral tests; use source-contract tests only where runtime testing is impractical, and explain their limits.
6. **Validate in layers.** Run focused tests first, then relevant package checks, then broader CI. Never substitute compile-only checks for behavioral tests.
7. **No unauthorized side effects.** Do not merge, deploy, publish releases, rotate secrets, modify production data, or push directly to a protected/default branch without explicit approval. Prefer a feature branch and draft PR.
8. **Report uncertainty honestly.** Separate confirmed defects, plausible candidates, accepted risks, blocked checks, and unverified assumptions.

## Workflow

### Phase 0: Establish the baseline

Capture:
- repository and default branch;
- current base/head commit SHAs and branch cleanliness;
- applicable repository instructions and contribution conventions;
- CI workflows, required checks, test commands, supported runtime versions;
- open PRs or overlapping branches touching the same files.

Do not assume remembered audit state is current. Re-fetch live repository evidence.

### Phase 1: Build a risk-led inventory

Prioritize by exploitability, impact, reachability, and confidence:
- trust boundaries: request input, environment variables, files, databases, webhooks, model/tool output;
- code execution: `eval`, `exec`, shell invocation, dynamic imports, deserialization;
- web boundaries: HTML injection sinks, URL construction, unsafe redirects, CORS, CSP, auth/session handling;
- persistence: write ordering, concurrency, restart behavior, fail-open defaults, data integrity;
- reliability: timeouts, cancellation, retries, unbounded queues/logs, stale state, race conditions;
- deployment: build/runtime mismatch, environment configuration, secrets, health checks, cache and rate limits.

For each candidate record: path, line, source, sink, trust boundary, exploit preconditions, impact, existing mitigations, confidence, and suggested test.

### Phase 2: Trace the behavior

For every candidate:
1. Identify the actual source and whether it is attacker- or externally-controlled.
2. Follow transformations to the sink. Distinguish validation, canonicalization, escaping, and safe text rendering; they are not interchangeable.
3. Check all callers and alternate paths, not just the first matching line.
4. Inspect tests and runtime configuration for existing guarantees.
5. Classify as **confirmed**, **plausible**, **not exploitable in current path**, or **needs runtime evidence**.

Do not report raw grep counts as vulnerability counts.

### Phase 3: Design a bounded patch

Write a short change contract before editing:
- defect or behavior being corrected;
- invariant that must hold after the fix;
- files expected to change;
- regression test that proves the invariant;
- compatibility and migration risks;
- explicit non-goals.

Choose the smallest safe implementation. Preserve public contracts and existing architecture unless the defect requires a contract change. For DOM work, prefer DOM APIs plus `textContent`/text nodes for untrusted text; do not replace one unsafe HTML sink with another. For network loops, define timeout, cancellation, response validation, and lock-release behavior. For persistence, test ordering, concurrency, restart, and fail-closed semantics.

### Phase 4: Test and refine

Run checks in this order:
1. New focused regression test.
2. Existing tests for the affected module/component.
3. Static checks, lint, type checks, syntax/compile checks as applicable.
4. Relevant integration/contract tests.
5. Full suite or CI matrix when practical.

After a failure:
- preserve the exact failure output;
- identify whether it is caused by the patch, baseline, environment, or external service;
- make the smallest correction;
- rerun the failing test and all directly affected checks.

Do not claim a test passed unless the command or CI check actually completed successfully. A skipped, pending, cancelled, timed-out, rate-limited, or missing check is not a pass.

### Phase 5: Review the diff

Before committing:
- inspect the complete diff and changed-file list;
- check for secrets, generated noise, unrelated changes, debug code, and brittle assertions;
- verify tests exercise the original failure mode;
- check accessibility, keyboard behavior, reduced-motion behavior, and mobile constraints for UI changes;
- ensure documentation and claims match actual behavior;
- run whitespace/diff checks.

### Phase 6: Deliver safely

- Create a descriptive feature branch.
- Use conventional, scoped commit messages.
- Open a draft PR unless the user explicitly requests another review state.
- Include: problem, root cause, implementation, tests with exact results, CI run/check links, known limitations, and rollback notes.
- Do not merge or deploy without explicit authorization.
- If CI is blocked by external rate limits or unavailable credentials, label it **blocked**, not failed application behavior and not passed.

## HTML and DOM security playbook

Use `scripts/scan_html_sinks.py` for a first-pass inventory. The scanner is intentionally a candidate finder:
- It reports sink occurrences and surrounding context.
- It does not prove that a sink receives untrusted data.
- It does not understand all framework abstractions, runtime sanitizers, template engines, or dataflow.
- Each result requires manual source-to-sink tracing.

For each HTML page:
- identify every dynamic value rendered into the DOM;
- classify values as trusted constants, validated structured data, or untrusted text;
- check `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, string-built templates, inline event-handler attributes, `srcdoc`, and dangerous URL attributes such as `javascript:`; the scanner inventories these as untriaged candidates only;
- use `textContent`, `createTextNode`, and explicit element construction for plain text;
- if rich HTML is genuinely required, use a maintained sanitizer with a narrowly defined allowlist and test the sanitizer boundary;
- validate URL schemes and destinations separately from HTML escaping;
- cap unbounded logs/lists and handle fetch timeouts, HTTP errors, content types, cancellation, and overlapping requests;
- preserve keyboard access, focus visibility, semantic labels, reduced-motion preferences, and mobile performance.

Do not declare the repository HTML backlog cleared because one page or one PR is fixed. Track inventory totals separately from confirmed issues and fixed paths.

## Evidence ledger

Maintain a compact ledger during the task:

| Item | Evidence |
|---|---|
| Baseline | branch + base SHA |
| Finding | path:line + source-to-sink explanation |
| Change | commit SHA + changed paths |
| Regression | exact command + exit code + result |
| CI | workflow/run ID + check state |
| External blockers | check name + observed reason |
| Safety | merge/deploy status |

Use **PASS**, **FAIL**, **BLOCKED**, **PENDING**, or **NOT RUN**. Never convert missing evidence into PASS.

## Final report format

1. **Completed:** exact files/commits and behavior changed.
2. **Validation:** commands, counts, runtimes, CI run IDs, and states.
3. **Findings remaining:** confirmed issues and untriaged candidates, clearly separated.
4. **Blockers/limitations:** external service, permissions, rate limits, missing runtime access.
5. **Repository state:** branch, PR URL/state, merge/deploy status.
6. **Next highest-value target:** one specific path or risk, justified by evidence.

Keep reports concise. No unsupported green claims, no invented metrics, and no claim that a scan is exhaustive unless its scope and exclusions are stated.
