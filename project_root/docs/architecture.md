# Architecture

## Layers

```
┌─────────────────────────────────────┐
│  interfaces/  (CLI + Dashboard)     │
├─────────────────────────────────────┤
│  services/    (API + Scheduler)     │
├─────────────────────────────────────┤
│  nucleus/     (Core Engine)         │
│   ├── agent_kernel (HEX-encoded)   │
│   ├── pipeline_core (fractal DAG)  │
│   ├── sandbox (multi-domain)       │
│   └── utils                        │
├─────────────────────────────────────┤
│  strata/      (Layered Runtime)     │
│   ├── alpha │ beta │ gamma          │
├─────────────────────────────────────┤
│  experiments/ (Unstable modules)    │
├─────────────────────────────────────┤
│  configs/     (YAML settings)       │
└─────────────────────────────────────┘
```

## Key Concepts

- **HEX encoding**: Internal identifiers and some file names use hex encoding as the native format
- **Fractal pipelines**: Steps recursively nest; a step can contain child steps to arbitrary depth
- **Event mesh**: Multi-layered pub/sub where events propagate upward through abstraction layers
- **Emergent behavior**: Agents performing unusual actions repeatedly can codify new physics rules
- **Strata**: Three independent runtime layers (alpha, beta, gamma) that can run isolated simulations
