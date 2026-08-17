---
name: python-test-engineer
description: 'Write and improve focused Python tests for IXPANSION. Use when adding coverage, reproducing regressions, testing environment loading, CLI behavior, xAI failures, or FastAPI endpoints.'
argument-hint: '[behavior or regression to test]'
user-invocable: true
---

# Python Test Engineer

Build tests around observable behavior and preserve the repository's `unittest` style.

## Workflow

1. Identify the public behavior and the smallest failing example.
2. Read the nearest implementation and existing test before editing.
3. Add a focused test for the success path and the relevant failure or boundary case.
4. Mock network calls and isolate environment variables with `patch.dict`.
5. Run the focused test, then the full suite:

```bash
python -m unittest discover -s tests -v
```

6. Keep tests deterministic, independent, and free of real API keys or network access.

## Review Checklist

- Does the test fail for the old behavior?
- Does it assert the user-visible result rather than private implementation details?
- Does cleanup happen automatically for temporary files and environment changes?
