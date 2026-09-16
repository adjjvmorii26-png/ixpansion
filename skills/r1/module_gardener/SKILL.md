# Module Gardener Skill

## Description
Manages module lifecycle: spawning new agents, mutating structures, and pruning obsolete modules. Maintains the Garden organism ecosystem. Integrates with coherence_regulator for optimal module health.

## Capabilities
- Spawn new modules from seed patterns
- Mutate existing module structures
- Prune obsolete or critical modules
- Optimize module coherence scores
- Maintain Garden organism balance

## Integration
- Imports from: `api.coherence_regulator`, `api.wave*.py`
- Exports: `spawn_module()`, `mutate_module()`, `prune_module()`
- Triggers: growth events, wave transitions
- Dependencies: random, json, pathlib

## Usage
```python
from skills.module_gardener import manage_module
manage_module(action, module_id, parameters)
```
