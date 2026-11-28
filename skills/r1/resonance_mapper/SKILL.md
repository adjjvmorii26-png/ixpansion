---
name: resonance_mapper
description: Map cross-module resonance patterns, visualize coherence gradients, and report bounded trend hypotheses.
---

# Resonance Mapper Skill

## Description
Maps cross-module resonance patterns and identifies emergent behaviors. Visualizes coherence gradients and detects threshold crossings before they become critical. Generates resonance graphs for organism visualization.

## Capabilities
- Map inter-module resonance patterns
- Identify emergent behaviors from coherence gradients
- Detect threshold crossings early
- Generate resonance visualizations
- Predict coherence trend directions

## Integration
- Imports from: `api.coherence_regulator`
- Exports: `map_resonance()`, `detect_thresholds()`, `generate_graph()`
- Triggers: coherence updates
- Dependencies: pyvis, json, numpy

## Usage
```python
from skills.resonance_mapper import map_patterns
graph = map_patterns(module_states)
```

## Safety
Label forecasts as hypotheses with source, freshness, and confidence. A resonance score is not authorization to change module state, delete resources, or trigger deployment.


## Safety and authorization

Resonance forecasts are advisory hypotheses, not authorization. Require explicit approval and a rollback reference before any downstream action changes module state, deletes resources, or triggers deployment.
