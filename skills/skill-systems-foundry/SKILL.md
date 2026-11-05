---
name: skill-systems-foundry
description: Five-engine skill quality workflow with a connected deterministic pipeline, failure-pattern diagnosis, proposal-only repair, Gem profile lint, and snapshot drift checks.
---

# Skill Systems Foundry

Notion is canonical. GitHub exports are derived.

## Connected pipeline

DISCOVER → MAP → FUZZ → DIAGNOSE → PROPOSE_REPAIR → REGRESSION_GATE → DRIFT_CHECK → EXPORT_REVIEW.

Run `python scripts/skill_lab.py pipeline --root <skills-directory> --seed 1337 --count 16 --profile portable`.

## Engines

- Dependency graph: missing targets, cycles, and orphan candidates.
- Instruction fuzzing: deterministic, bounded case generation (maximum 256). Cases are generated, not executed against target skills.
- Failure-pattern diagnosis: stable FP-001 through FP-006 mappings with minimal repair proposals.
- Self-healing loop: proposal-only. Preserve originals and rollback references; require regression evidence.
- Gem compatibility: static profile lint, not runtime proof.
- Drift radar: normalized SHA-256 comparison of local snapshots. Live Notion comparison remains a separate integration step.

## Promotion gates

Static lint → fuzz generation → diagnosis → proposed patch → regression execution → drift check → export review → human approval.

Never silently rewrite canonical Notion instructions, force-push, merge, activate, publish, delete, or deploy. Distinguish static, desk, execution, and live integration evidence.