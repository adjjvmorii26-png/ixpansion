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

## Cross-Project Resonance

The repository-level bridge exposes three contracts:

1. **State propagation** — `omega_prime` atom state becomes mood input for the fractal engine.
2. **Event routing** — `project_root` mesh deliveries are mirrored into the `omega_prime` reactor.
3. **Resonance telemetry** — status fields are canonicalized into a stable SHA-256 pulse.
4. **Temporal analysis** — locked JSONL journals feed attractor detection, drift rates,
   and mutation verdicts through `bridges.resonance_cli`.

`PulseOracle` treats identical pulses as attractors and uses hexadecimal Hamming
distance to distinguish stable drift from mutation. This gives CI a compact,
replayable signal for detecting unintended behavioral changes.
