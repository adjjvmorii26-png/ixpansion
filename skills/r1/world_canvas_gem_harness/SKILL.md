---
name: world_canvas_gem_harness
description: Orchestrate deterministic World Canvas simulations with modular skill checks, adversarial validation, and evidence export.
---

# World Canvas Gem Skill Harness

A reusable IXPANSION lab for validating skill behavior against a deterministic local simulation. The browser harness is a test surface, not an autonomous agent or calibrated physical model.

## Capabilities
- `world_canvas_gem_harness:open_lab` — open the local harness.
- `world_canvas_gem_harness:run_suite` — execute all registered deterministic checks.
- `world_canvas_gem_harness:run_scenarios` — execute the versioned Python fixture registry and emit lineage-aware results.
- `world_canvas_gem_harness:export_evidence` — export a JSON report with per-check outcomes and state hash.
- `world_canvas_gem_harness:review_skill` — apply Dual Lens review to a skill change.
- `world_canvas_gem_harness:stress_invariants` — run Forge-Breakers negative checks.
- `world_canvas_gem_harness:audit_data_flow` — apply Zero-Copy ownership and boundedness review.

## Integration contract
1. Keep the harness under `labs/world-canvas-gem-harness/`.
2. Keep reusable skill instructions under `skills/r1/<skill>/SKILL.md`.
3. Validate candidate state before commit; rejected actions must not partially mutate committed state.
4. Rendering must be observational and must not mutate simulation state.
5. Bound undo history, event ledger, beacon capacity, and exported payload size.
6. Treat hashes as state fingerprints, never as authentication or provenance proof.
7. Label browser checks as local deterministic checks. Do not claim Gemini execution unless a real Gemini runtime adapter is installed and exercised.

## Roots
| Root | Path | Role |
|---|---|---|
| Lab | `labs/world-canvas-gem-harness/` | Browser simulation and local runner |
| Skill | `skills/r1/world_canvas_gem_harness/` | Orchestration instructions |
| Modules | `skills/r1/{dual_lens,zero_copy,forge_breakers}/` | Reusable review/test modules |
| Tests | `tests/skills/test_world_canvas_gem_harness.py` | Bundle contract tests |

## Commands

### world_canvas_gem_harness:open_lab
Open `labs/world-canvas-gem-harness/index.html` in a modern browser. No network or API key is required.

### world_canvas_gem_harness:run_suite
Select **Run all checks** in the harness. Record the exact pass/fail counts from the generated report.

### world_canvas_gem_harness:export_evidence
Use **Export evidence JSON**. Preserve the schema, timestamp, world tick, state hash, and per-check status.

### world_canvas_gem_harness:review_skill
Run the Dual Lens module: first inspect implementation contracts, then independently attempt adversarial counterexamples.

### world_canvas_gem_harness:stress_invariants
Run Forge-Breakers against boundary coordinates, energy limits, duplicate IDs, capacity limits, rejected commits, and undo/reset behavior.

### world_canvas_gem_harness:audit_data_flow
Run Zero-Copy review. Identify each clone/serialization boundary and retain defensive copies wherever transaction isolation depends on them.


### world_canvas_gem_harness:run_scenarios

Run `python skills/r1/world_canvas_gem_harness/scenario_runner.py --source-commit "$(git rev-parse HEAD)"`. This executes deterministic Python fixture adapters from `scenario-registry.json`, not the browser canvas. Preserve the report's runtime, source commit, scenario versions, check outcomes, and trust limitations. The runner rejects reports larger than 64 KiB before writing output.
