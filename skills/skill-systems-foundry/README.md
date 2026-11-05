# Skill Systems Foundry

Offline, deterministic quality pipeline for reusable skills.

## Run

```bash
python scripts/skill_lab.py pipeline --root skills --seed 1337 --count 16 --profile portable
PYTHONPATH=scripts python -m unittest discover -s tests -v
```

Commands: `scan`, `graph`, `fuzz`, `compat`, `drift`, `repair-plan`, and `pipeline`.

The offline pipeline executes discovery, dependency mapping, bounded fuzz-case generation, static compatibility lint, diagnosis, and repair proposals. It reports regression execution, live Notion verification, and export review as not run unless separately invoked. Add `--export-dir <folder>` to run local snapshot drift checks. Failure patterns FP-001 through FP-006 are maintained in `failure_patterns.json`.

Fuzz cases are generated only, not executed. Repair is proposal-only. Compatibility is static lint, not runtime proof. Drift compares local snapshots; it does not fetch Notion. Human review is required before promotion.