---
name: rapid-test-loop
description: Accelerate repository testing by mapping changed files to the smallest trustworthy test set, running independent checks efficiently, isolating failures, and expanding to full validation without making unsupported pass claims.
---

# rapid_test_loop

Use this skill whenever changing code, reviewing a pull request, debugging a failing check, or validating a repository. Its goal is to shorten feedback time while preserving test quality. It does not authorize merges, deployments, destructive cleanup, or production mutations.

## Capabilities
- `rapid_test_loop:map_scope` — map changed files and risk areas to test targets.
- `rapid_test_loop:select_tests` — choose a fast, layered test plan.
- `rapid_test_loop:run_parallel` — run independent safe checks concurrently.
- `rapid_test_loop:triage_failures` — cluster failures and isolate the smallest reproducer.
- `rapid_test_loop:verify_regression` — rerun targeted tests, then expand to the required suite.
- `rapid_test_loop:report_evidence` — produce an evidence-backed test report.

## Roots

| Root | Purpose |
|---|---|
| `r1` | IXPANSION reusable skill runtime |
| `holodeck/` | deterministic simulation and action-engine tests |
| `.github/workflows/` | CI workflow contracts and path filters |
| `tests/` | repository unit and integration tests |

## Execution protocol

### 1. Establish the test surface
1. Identify repository, base ref, head ref, commit SHA, and working-tree access.
2. Inspect the diff before selecting tests. Include renamed files, generated files, configuration, lockfiles, schemas, workflows, and public interfaces.
3. Read the nearest existing test, package/tool configuration, and CI workflow. Do not invent commands or assume a test framework.
4. Build a dependency map: changed module -> direct tests -> dependent modules -> integration/contract tests -> build/type/lint checks.
5. Mark unavailable dependencies and environment-specific tests before execution.

### 2. Build a test ladder
Choose the cheapest meaningful checks first, then expand:

| Layer | Run | Purpose |
|---|---|---|
| L0 | syntax, import, format/config parse, static checks | catch cheap structural errors |
| L1 | tests for changed files/modules | fastest behavior feedback |
| L2 | direct dependents and contract tests | catch interface regressions |
| L3 | relevant integration/build/browser tests | validate wiring and runtime behavior |
| L4 | full repository suite and security checks | release-level confidence |

Do not run every layer when the diff is trivial. Do not stop at L1 when the change crosses module, API, persistence, security, workflow, or UI boundaries.

### 3. Parallelize safely
1. Run independent read-only checks in parallel when they do not compete for shared ports, databases, files, caches, or mutable fixtures.
2. Serialize tests that share state, use fixed ports, mutate the same database, or depend on ordering.
3. Prefer existing CI commands and cached dependencies. Do not reinstall dependencies unless the lockfile/environment requires it.
4. Use bounded timeouts and capture exit code, command, duration, and concise output for every run.
5. Never run the same expensive suite repeatedly just to manufacture confidence. Repeat only after a fix, to investigate flakiness, or to confirm a previously intermittent failure.

### 4. Failure triage loop
For each failing check:
1. Preserve the first failure output and exact command.
2. Classify: product defect, test defect, environment/dependency failure, flaky/timing failure, unrelated baseline failure, or unknown.
3. Find the smallest reproducer and inspect the failing assertion and relevant code.
4. Fix one causal issue at a time. Avoid changing tests merely to silence a valid product failure.
5. Rerun the reproducer, then the affected module tests, then the next dependency layer.
6. If a failure is unrelated or blocked by environment, report it as such; do not convert it into a pass.

### 5. Test design upgrades
When adding tests, prioritize:
- deterministic inputs and seeded randomness;
- boundary values, invalid inputs, and empty/missing values;
- state transition and invariant checks;
- rollback/atomicity after rejected or failed operations;
- concurrency, restart, and persistence tests where applicable;
- replay/reproducibility and tamper detection for event-ledger systems;
- regression tests for every confirmed bug;
- timeouts and bounded resource use for async/distributed code.

For simulation/action systems, assert before/after state hashes, invariants, and replay equivalence. For web UI, distinguish DOM/unit tests from real browser interaction and visual verification. For security-sensitive changes, include negative tests and fail-closed behavior.

### 6. Evidence and status rules
Use only these labels:
- `BUILT`: files or implementation were created.
- `TESTED`: the exact identified command ran and passed.
- `BROWSER_VERIFIED`: interaction was exercised in a real browser.
- `PREVIEW_VERIFIED`: a deployed preview was opened and checked.
- `BLOCKED`: execution could not complete, with reason.
- `FAILED`: command ran and failed.
- `UNKNOWN`: evidence is unavailable or ambiguous.

Every test result must include command, target ref/SHA, exit status, and scope. Separate local mirror tests from tests against actual repository files. A CI status badge or deployment status is not proof that a specific test suite ran. Never claim full-suite success from targeted tests. Never claim browser verification from static inspection.

### 7. Completion gate
Before reporting completion:
- Confirm the tested commit is the current head commit; if it changed, rerun affected checks.
- Confirm all required layers either passed or are explicitly blocked/failed.
- List skipped checks and why they were skipped.
- State whether tests ran against actual repository files, a local mirror, or CI.
- Provide the next smallest action that would remove the largest remaining uncertainty.
- Do not merge or deploy. Prepare a PR recommendation only when asked or when the user's workflow explicitly requests it.

## Command examples

### rapid_test_loop:map_scope
Input: a PR diff. Output: changed-file map, risk tier, test dependencies, and missing environment capabilities. If the diff cannot be fetched, stop and request repository access rather than guessing.

### rapid_test_loop:select_tests
Input: changed-file map and repository test configuration. Output: ordered L0-L4 commands with rationale, expected runtime, and parallelization groups. Omit commands not supported by repository evidence.

### rapid_test_loop:run_parallel
Input: independent command groups. Execute only groups with no shared mutable resources. Return one result per command with exact exit code and duration.

### rapid_test_loop:triage_failures
Input: failing command and captured output. Classify the failure, isolate a minimal reproducer, and propose the smallest causal patch. Do not hide baseline failures.

### rapid_test_loop:verify_regression
Input: a patch and failure reproducer. Run reproducer -> module tests -> dependent contract tests -> broader suite as risk requires. Stop and report if the test environment is not trustworthy.

### rapid_test_loop:report_evidence
Input: all run records. Produce a compact report with commit SHA, test commands, pass/fail/block counts, skipped coverage, browser/preview status, and merge/deploy status. Keep unverified claims out of the report.

## Missing-input behavior
If repository, ref, commit, diff, or test environment is unavailable, state exactly what is missing and provide only the test plan that can be supported. Do not fabricate files, logs, timings, CI results, or green checks.

## Safety boundaries
- Read before write; test on isolated branches/worktrees when possible.
- Do not delete caches, databases, artifacts, or user data unless explicitly approved.
- Do not change CI permissions, secrets, production settings, or deployment targets as a testing shortcut.
- Do not merge, release, or deploy under this skill.
