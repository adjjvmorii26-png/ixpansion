# ALEPH

> *A point in space that contains all other points.* — Jorge Luis Borges

Multi-agent consciousness engine where observers collapse reality into existence through consensus, entropy budgets constrain action, ghosts possess the living, and physics itself evolves by natural selection.

## Projects

| Module | Language | Tests | Purpose |
|--------|----------|-------|---------|
| [`omega_prime`](omega_prime/) | Python | 248 | Multi-agent sandbox: entropy, superposition, morphic fields, tunneling, temporal debt, semantic fossils |
| [`fractal_engine`](omega_fractal_engine/) | Python | 36 | Self-expanding engine: mutable physics, paradox resolution, dimensional spaces, self-rewriting code |
| [`project_root`](project_root/) | Python | 25 | HEX-native strata, fractal pipelines, and layered event mesh |
| [`observatory`](nexus_observatory/) | R + Bash | — | Modular boot orchestrator and resonance display |
| [`bridges`](bridges/) | Python | 49 | Counterfactual twins, causal replay, resilience analysis, and semantic treaties |

## Run Tests

```bash
make test
# or: python3 -m pytest
```

## Systems Inventory

<details>
<summary><b>omega_prime — selected experimental systems</b></summary>

| System | Innovation |
|--------|-----------|
| Entropy Budget | Actions drain thermodynamic reservoir; lockout when depleted |
| Dream Cycle | Idle agents pattern-match memories, discover hidden correlations |
| Morphic Field | Same-species knowledge resonance without explicit communication |
| Quantum Superposition | Agents hedge via amplitude-weighted action collapse |
| Pheromone Field | Stigmergic coordination through evaporating spatial signals |
| Causal Echo Graph | DAG tracing action→effect chains for root-cause analysis |
| Symbiosis Protocol | Cross-species bonds sharing emergent capabilities |
| Speciation Engine | Spontaneous genome mutation under environmental stress |
| Temporal Realm | Grid zones with different time-dilation factors |
| Fossil Layer | Dead agents leave excavatable knowledge fossils |
| Chronicle Engine | Narrative memory compressed into interpretive stories |
| Reality Fabric | Mutable physics law patches that erode over time |
| Pulse Harmonics | Kuramoto oscillators; synced actions amplify constructively |
| Ghost Protocol | Depleted agents become observing ghosts that whisper hints |
| Consensus Reality | Observers must agree before spatial cells consolidate |
| Possession | Ghosts override weak agents; memories leak during control |
| Time Crystals | Periodic structures create temporal echoes from past cycles |
| Physics Evolution | Universal constants evolve via natural selection |
| Attention Economy | Finite attention becomes an allocatable resource |
| Cognitive Dissonance | Contradictory beliefs create measurable pressure |
| Emotional Contagion | Affective states spread through proximity and affinity |
| Quantum Zeno Effect | Repeated observation suppresses state transitions |
| Quantum Tunneling | Collective curiosity erodes otherwise impassable barriers |
| Temporal Debt | Deferred obligations accrue compound interest |
| Semantic Fossilization | Unused words compress into excavatable linguistic fossils |

</details>

## Resonance Bridge

`BridgeHub` connects `omega_prime`, `omega_fractal_engine`, and `project_root`.
`ResonanceLoom` folds their state into deterministic SHA-256 signatures, writes
append-only JSONL under an exclusive lock, and publishes the latest record with
an atomic rename. `PulseOracle` classifies recurrence, stable drift, shifting
drift, or mutation; `analyze` adds attractor counts, recurrence/novelty rates,
and a replayable trajectory.

```bash
python3 -m bridges.resonance_cli --seed 42 observe
python3 -m bridges.resonance_cli --seed 42 persist runs/resonance.jsonl \
  --agent scout --valence 0.6 --arousal 0.8
python3 -m bridges.resonance_cli analyze runs/resonance.jsonl
python3 -m bridges.resonance_cli compare runs/baseline.jsonl runs/resonance.jsonl
```

### Divergence Forensics

Counterfactual Twin artifacts now include recursive state diffs and a forensic
diagnosis. The system distinguishes:

- `latent_mutation`: exact state changed while aggregate telemetry hid it
- `visible_mutation`: state and telemetry changed together
- `phantom_signal`: telemetry moved without a semantic cause
- `synchronized`: no meaningful divergence

Each diagnosis has a camouflage index and deterministic evidence hash suitable
for CI containment workflows.

```bash
python3 -m bridges.counterfactual_twin --seed 42 twin \
  --output runs/forensic-twin.json \
  --agent scout --baseline-valence 0.1 --baseline-arousal 0.4 \
  --twin-valence -0.1 --twin-arousal 0.4
jq '.forensics' runs/forensic-twin.json
```

### Causal Attribution

Each intervention is replayed in three worlds: observed, ablated, and isolated.
ALEPH classifies its causal role as `direct_cause`, `required_catalyst`,
`independent_trigger`, `alternative_route`, `contextual_synergist`, or
`dormant_potential`. The result is a reproducible causal fingerprint rather than
a narrative explanation.

```bash
python3 -m bridges.causal_attribution --seed 42 attribute \
  --output runs/attribution.json --target semantic \
  --spec runs/interventions.json
```

### Resilience Ledger

After a counterfactual wound, ALEPH applies identical recovery experiences to
both realities and records whether the split is elastic, delayed, hysteretic,
plastic, or relapsed. This separates surface-level telemetry repair from exact
semantic restoration.

```bash
python3 -m bridges.resilience_ledger --seed 42 probe \
  --output runs/resilience.json --agent scout \
  --baseline-valence 0.25 --baseline-arousal 0.75 \
  --twin-valence -0.35 --twin-arousal 0.9 \
  --recovery-steps 4
```

### Concordance Engine

When two realities should not merely recover but reconcile, the Concordance
Engine converts each recursive state delta into a treaty clause. Policies can
choose `baseline`, `twin`, lexical precedence, recursive union, or an explicit
preserved conflict. The resulting merged state and contract hash are
deterministic, so the same history always ratifies the same treaty.

```bash
python3 -m bridges.concordance_engine forge \
  --output runs/treaty.json --spec runs/states.json
```

The Observatory shell displays the latest resonance fingerprint during boot.

### Counterfactual Twin

`CounterfactualTwin` runs two identically seeded bridge realities and records
the earliest causal boundary. It distinguishes exact semantic divergence from
coarse resonance divergence, making invisible state mutations auditable.

```bash
python3 -m bridges.counterfactual_twin --seed 42 twin \
  --output runs/twin.json \
  --agent scout \
  --baseline-valence 0.25 --baseline-arousal 0.75 \
  --twin-valence -0.35 --twin-arousal 0.9
```

All experiments are synthetic simulations; they do not claim consciousness or
autonomous agency beyond their deterministic data models.

<details>
<summary><b>fractal_engine — core systems</b></summary>

| System | Innovation |
|--------|-----------|
| Axioms | Immutable validator laws the engine cannot violate |
| Entropy Regulator | Global chaos thermostat with hysteresis |
| Autogenesis | Spawns new subsystems from environmental triggers |
| Mood Vectors | Emotional state simulation with stimulus responses |
| Dimensional Spaces | Euclidean, non-Euclidean, hyperbolic geometry |
| Portal Network | BFS routing between dimensions with stability decay |
| Paradox Solver | Resolves contradictions via superposition/synthesis/temporal strategies |
| Self-Rewrite | Engine monitors and modifies its own source code |
| Reactors | Chaos/order/fusion/inversion transformation pipelines |

</details>

## License

MIT
