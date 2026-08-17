---
name: cli-ux-optimizer
description: 'Improve the IXPANSION command-line experience. Use when changing argparse options, defaults, help text, exit codes, validation, offline behavior, or CLI error messages.'
argument-hint: '[CLI workflow or failure path]'
user-invocable: true
---

# CLI UX Optimizer

Make `run_agent.py` predictable for both first-time users and scripts.

## Workflow

1. Run `python run_agent.py --help` and inspect the current parser.
2. Identify defaults, required configuration, output, and exit behavior.
3. Validate invalid combinations before doing work or making network calls.
4. Use concise `argparse` errors with an actionable remedy; avoid tracebacks for expected input or configuration failures.
5. Preserve the offline default path.
6. Test documented commands and missing-configuration paths.
7. Run:

```bash
python -m py_compile run_agent.py
python run_agent.py --goal "Smoke test"
```

Do not change output formatting casually when users or scripts may rely on it.
