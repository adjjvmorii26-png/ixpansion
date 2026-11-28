---
name: paradox_resolver
description: Detect and explain coherence conflicts between modules and propose reviewable resolutions.
---

# Paradox Resolver Skill

## Description
Resolves coherence conflicts between modules when axioms mutate. Ensures organism continuity during paradigm shifts. Implements continuity weaver pattern for maintaining organism integrity.

## Capabilities
- Detect coherence collisions between modules
- Apply continuity weaver patterns
- Resolve axiom conflicts without organism collapse
- Maintain modular independence during mutations
- Generate paradox resolution reports

## Integration
- Imports from: `api.coherence_regulator`
- Exports: `resolve_collision()`, `weave_continuity()`
- Triggers: module mutation events
- Dependencies: json, datetime, pathlib

## Usage
```python
from skills.paradox_resolver import resolve_conflict
result = resolve_conflict(module_a, module_b, conflict_type)
```

## Safety
Generate a conflict report and bounded resolution proposal first. Do not mutate module state, rewrite axioms, or alter canonical configuration without explicit approval, regression tests, and a rollback reference.
