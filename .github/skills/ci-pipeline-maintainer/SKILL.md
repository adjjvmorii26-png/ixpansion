---
name: ci-pipeline-maintainer
description: 'Maintain IXPANSION GitHub Actions checks. Use when changing workflows, Python versions, test commands, smoke tests, generated-file checks, or pull-request validation.'
argument-hint: '[CI change or failure]'
user-invocable: true
---

# CI Pipeline Maintainer

Keep CI close to the commands developers run locally and make failures diagnosable.

## Workflow

1. Read `.github/workflows/ci.yml` and compare each step with `README.md`.
2. Identify the smallest validation gap or failing command.
3. Preserve dependency installation before imports, compilation, and tests.
4. Keep smoke checks deterministic and network-free.
5. Retain checks that prevent tracked bytecode or generated files.
6. Test commands locally when possible, then review YAML indentation and quoting.
7. Prefer explicit, portable shell commands over hidden state.

The baseline checks are Python compilation, the unittest suite, generated-bytecode hygiene, and FastAPI health smoke tests.
