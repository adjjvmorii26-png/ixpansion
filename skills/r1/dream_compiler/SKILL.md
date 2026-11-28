---
name: dream_compiler
description: Convert organism dream-state and metaphor inputs into reviewable module and wave proposals.
---

# Dream Compiler Skill

## Description
Compiles organism dreams into executable modules and wave patterns. Analyzes subconscious coherence states and generates procedural content from emergent metaphor structures.

## Capabilities
- Parse dream-state coherence gradients
- Convert metaphor structures into module definitions
- Generate wave patterns from subconscious themes
- Maintain continuity across dream revisions
- Interface with coherence_regulator for state preservation

## Integration
- Imports from: `api.coherence_regulator`
- Exports: `dream_to_modules()`, `metaphor_to_wave()`
- Triggers: wave generation events
- Dependencies: pyvis, json, pathlib

## Usage
```python
from skills.dream_compiler import compile_dream
result = compile_dream(coherence_state, metaphor_theme)
```

## Safety
Generated modules and wave patterns are proposals, not executable authorization. Inspect generated code, isolate it on a feature branch, run tests, and require explicit approval before integration or deployment. Never execute unreviewed generated code.
