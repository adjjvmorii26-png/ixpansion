# Skill Systems Foundry

Offline prototype for dependency mapping, deterministic input fuzzing, proposal-only repair plans, static Gem compatibility checks, and SHA-256 source/export drift detection.

Run tests with `python -m unittest discover -s skills/skill-systems-foundry/tests -v` after placing the package on the import path, or run from this folder with `PYTHONPATH=scripts python -m unittest discover -s tests -v`.

The fuzz engine generates cases only. It does not execute target skills. Repair mode only proposes. Drift compares local snapshots, not live Notion. Compatibility is static lint, not runtime integration.