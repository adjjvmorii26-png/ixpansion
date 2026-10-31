---
name: live-reusable-test-surface
version: 0.3.0
description: Runtime-neutral local test chamber with bounded subprocess execution and structured evidence; browser automation is an optional adapter.
---

# Live Test Chamber

## Purpose

Provide a native execution and evidence layer for IXPANSION modules, Holodeck renderers, scripts, and local application components. The chamber separates execution from presentation: it runs a declared target, captures process evidence, evaluates explicit expectations, and emits a machine-readable report. It does not require a browser canvas or iframe.

## Architecture

- `scripts/live_test_chamber.py`: standard-library execution controller and CLI.
- Runtime adapters: Python and Node.js command builders. New adapters can implement the same command-builder contract.
- Evidence envelope: target, runtime, timestamps, exit status, duration, bounded stdout/stderr, expectations, and result.
- Optional presentation adapters may consume the JSON report. Browser automation is not part of the core.

## Run a local target

Run trusted project code only. This tool is an execution harness, not a security sandbox. It does not isolate filesystem access, prevent network access, or make hostile code safe.

Python:
```sh
python skills/live-reusable-test-surface/scripts/live_test_chamber.py \
  --root . --runtime python --target tests/test_example.py \
  --expect-exit 0 --expect-stdout "passed"
```

Node.js:
```sh
python skills/live-reusable-test-surface/scripts/live_test_chamber.py \
  --root . --runtime node --target scripts/example.mjs \
  --expect-exit 0
```

Evidence is written to stdout as JSON. Use `--report artifacts/live-test/report.json` to persist it. Exit codes: 0 PASS, 1 FAIL, 2 invalid invocation or missing runtime.

## Result semantics

- PASS: process exited with the expected code and every supplied stdout expectation matched.
- FAIL: process failed, timed out, or an expectation did not match.
- REVIEW: reserved for adapters that observe without assertions. The core CLI requires an explicit expected exit code.
- BLOCKED: reserved for policy or environment refusal before execution.

A zero exit code alone is not proof of semantic correctness. Add meaningful output expectations or a dedicated test suite.

## Safety boundary

- Accept only a target file inside the declared project root; reject path traversal and symlink escapes.
- Invoke runtimes with argument arrays, never a shell.
- Apply a timeout and cap the amount of output retained in the evidence report.
- Pass a minimal environment rather than inheriting all parent variables.
- Do not pass credentials or secrets to test targets.
- This is not an OS-level sandbox. Run only code you trust, preferably inside a disposable container/VM with network and filesystem policy configured externally.

## Optional adapters

Browser/Playwright, WebGPU, GPU simulation, and remote execution can be added as independent adapters. They must emit the same evidence envelope and must not upgrade REVIEW to PASS without explicit assertions.

## Evidence record

The JSON report contains schema version, target, runtime, timestamps, duration, exit code, timeout state, stdout/stderr excerpts, assertions, and result. Keep reports as build artifacts; do not commit generated output by default.
