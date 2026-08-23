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

## Counterfactual Twin

The twin instantiates two `BridgeHub` graphs with the same seed and applies each
paired signal to both. Exact `StateCore` snapshots identify the first semantic
split; resonance signatures identify when coarse telemetry later reflects it.
This separation prevents an unchanged aggregate metric from hiding a real
counterfactual mutation.

## Divergence Forensics

Every paired intervention stores exact semantic deltas, aggregate status fields,
and both resonance signatures. `divergence_forensics` computes semantic and
resonance magnitudes, derives a camouflage index, and classifies the boundary as
latent mutation, visible mutation, phantom signal, or synchronized state. The
evidence hash is computed over the complete comparison, so CI can preserve a
replayable causal record rather than a lossy alert.

## Causal Attribution

The attribution engine replays every paired intervention against two controls:
an ablated world where both realities receive the same signal, and an isolated
world where only that intervention differs. Comparing semantic or resonance
divergence across these worlds yields a replay-backed classification instead of
a post-hoc story. The causal fingerprint records only stable classifications,
world outcomes, and boundary kinds, making it useful as a regression signature.

## Resilience Ledger

Counterfactual divergence is followed by identical recovery experiences. The
ledger samples recursive state deltas and resonance signatures at each step,
classifying recovery as elastic, delayed, hysteretic, plastic, relapsed, or
inert. In particular, it can detect a hysteretic trace where dashboards return
to agreement while underlying semantic history remains different.
