# Skill Systems Foundry

Offline, deterministic quality pipeline for reusable skills.

## Run

```bash
python scripts/skill_lab.py pipeline --root skills --seed 1337 --count 16 --profile portable
PYTHONPATH=scripts python -m unittest discover -s tests -v
```

Commands: `scan`, `graph`, `fuzz`, `compat`, `drift`, `repair-plan`, and `pipeline`.

The pipeline connects discovery, dependency mapping, bounded fuzz-case generation, failure-pattern diagnosis, repair proposals, regression gates, drift checks, and export review. Failure patterns FP-001 through FP-006 are maintained in `failure_patterns.json`.

Fuzz cases are generated only, not executed. Repair is proposal-only. Compatibility is static lint, not runtime proof. Drift compares local snapshots; it does not fetch Notion. Human review is required before promotion.