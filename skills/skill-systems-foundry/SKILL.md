# Skill Systems Foundry

A portable workflow for skill dependency maps, deterministic input fuzzing, repair proposals, Gem compatibility checks, and source/export drift detection.

Notion is canonical. GitHub exports are derived. All checks are offline and advisory unless a test explicitly executes.

## Engines
- Dependency graph: find missing references, cycles, duplicates, and orphaned skills.
- Instruction fuzzing: generate bounded, deterministic test inputs; do not execute the target skill.
- Repair loop: propose a minimal patch, test in isolation, compare, and preserve rollback. No automatic source rewrite.
- Compatibility bench: static lint per target profile; never call it runtime proof.
- Drift radar: compare fetched Notion snapshots and GitHub exports using SHA-256; never overwrite on mismatch.

## Evidence
Separate static checks, desk tests, runtime tests, and live integration. Record source URL, version, repository ref, seed, results, and hashes. Missing access is BLOCKED.

No secret storage, external calls, destructive changes, activation, merge, or deployment.