---
name: dependency-auditor
description: 'Audit and maintain Python dependencies for IXPANSION. Use when changing requirements, investigating import failures, reviewing upgrades, or checking whether runtime and test packages are declared.'
argument-hint: '[dependency or import question]'
user-invocable: true
---

# Dependency Auditor

Keep declared dependencies minimal, reproducible, and aligned with imports.

## Workflow

1. Inspect `requirements.txt`, all imports, CI setup, and the selected Python version.
2. Separate runtime dependencies from test-only dependencies.
3. Confirm every non-standard import is declared and every declared package is needed.
4. Prefer compatible, targeted upgrades over broad churn.
5. Install or update dependencies only when the task requires it.
6. Validate with compilation and tests:

```bash
python -m py_compile agent.py run_agent.py xai_client.py api/main.py
python -m unittest discover -s tests -v
```

Record compatibility concerns when a dependency upgrade changes Python, FastAPI, or client behavior.
