# ALEPH

> *A point in space that contains all other points.* — Jorge Luis Borges

Multi-agent consciousness engine where observers collapse reality into existence through consensus, entropy budgets constrain action, ghosts possess the living, and physics itself evolves by natural selection.

## Projects

| Module | Language | Tests | Purpose |
|--------|----------|-------|---------|
| [`omega_prime`](omega_prime/) | Python | 248 | Multi-agent sandbox: entropy, superposition, morphic fields, tunneling, temporal debt, semantic fossils |
| [`fractal_engine`](omega_fractal_engine/) | Python | 36 | Self-expanding engine: mutable physics, paradox resolution, dimensional spaces, self-rewriting code |
| [`project_root`](project_root/) | Python | 25 | HEX-native strata, fractal pipelines, and layered event mesh |
| [`observatory`](nexus_observatory/) | R + Bash + Python | 11 | Boot orchestrator, pulse journal, dashboard, Wave 9 runner, and sealed reliquary |
| [`projects`](projects/) | Python | 7 | Echolalia, schism, tide clock, interloper, and infinity listening-post labs |
| [`bridges`](bridges/) | Python | 95 | Counterfactual twins, causal replay, resilience analysis, semantic treaties, reversible braids, and Kintsugi ledger repair |
| [`mycelium`](mycelium/) | Python | 12 | Consent-bounded living substrate: spores, hyphal gradients, and dream compilation |
| [`ixpansion`](ixpansion/) | Python | 37 | Self-expanding HEX mesh: agent-coupled routing, HEX witnesses, world scenes, mutations, and preserved glitches |
| [`solid-organism`](solid-organism/) | Python | 13 | Deterministic organism labs: kintsugi seams, dice constellations, consent-bounded cordyceps, negative space, and synthetic mood superposition |
| [`constellation`](constellation/) | Python | 27 | Dispersed repository resonance: scored concepts, adapter targets, integration graphs, and phased ritual contracts |

## Run Tests

```bash
make test
# or: python3 -m pytest
```

## Systems Inventory
## Solid Organism Labs
## Nexus Command Surface

`nexus_observatory` now has a dependency-free NPM command surface over the same
resonance contract used by the shell modules. Cycles append a JSONL journal,
publish `resonance.jsonl.latest`, rebuild Markdown indexes, render a dashboard,
compare adjacent pulses, seal hash-chained relics, and run Project Wave 9.

```bash
cd nexus_observatory
npm run health
npm run quiet
npm run watch -- 2 10
npm run creative
npm run reliquary
npm run ci
```


Solid Organism is a compact laboratory for metaphors made executable. Kintsugi
turns fractures into golden, inspectable seams; constellation dice turn bounded
randomness into named star graphs; cordyceps treats refusal as immunity memory
rather than failure; negative-space reads absent cells as organizing evidence;
and mood superposition collapses synthetic affect vectors without claiming felt
experience.

```bash
python3 solid-organism/lab/kintsugi.py
python3 solid-organism/lab/constellation_dice.py
python3 solid-organism/lab/cordyceps.py
python3 solid-organism/lab/negative_space.py
python3 solid-organism/omega/experiments/mood_superposition.py
```

## IXpansion Mesh

## Constellation Corpus

Constellation Corpus turns dispersed concept repositories into one mergeable map instead of duplicating their scaffolding. Each source is scored for structural richness, symbolic payload, density, and adapter fit; recommendations become `integrate_concept`, `prototype_adapter`, or `preserve_reference` actions mapped to an existing IXpansion subsystem.

```bash
python3 -m constellation.engine plan
python3 -m constellation.engine graph
python3 -m constellation.engine weave --format markdown
python3 -m constellation.engine rehearse --format markdown
python3 -m constellation.engine recover --format markdown
make test-constellation
```

Before a concept touches its target, the Shadow Rehearsal replays every phase under a deterministic chaos budget. Nested targets are quarantined, failed releases receive rollback witnesses, and the complete ledger remains replayable from `weave_hash` plus `rehearsal_hash`. Recovery Braids close the loop: collision groups split into non-overlapping lanes, while rollback failures become bounded retry orbits tied to their original witnesses.

IXpansion is a deterministic self-expansion laboratory. World scenes emit
perceptions, four agents propose data-only actions, mesh edges route those
actions, a StateGraph absorbs mutations, and the HEX VM preserves ritual traces.
Every accepted action is routed through the selected topology and receives a
deterministic HEX **witness receipt**—a compact ritual whose emitted evidence
word is bound to the exact canonical action. Paradox systems never hide failure:
identity splits, temporal loops, and rule collisions remain inspectable.

```bash
python3 -m pytest ixpansion/tests -q
python3 ixpansion/src/interfaces/cli.py --scene hex_storm --topology ring --ticks 3 --compact
```


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

### Astral Braid Conservatory

A MYCELIUM dream can be dangerous before anyone understands its consequences.
The conservatory expands each dream into three reversible **shadow timelines**:
conservative, lateral, and paradox. Every timeline receives an explicit consent,
entropy, duration, and confidence audit; low-scoring futures remain visible but
cannot be promoted. The winning braid is published to an astral JSONL bus with a
deterministic certificate, while the original dream remains untouched in its
capsule.

```bash
python -m mycelium.interfaces.cli dream --seed 20260823 > artifacts/dream.json
python -m bridges.astral_braid \
  --dream-file artifacts/dream.json \
  --transcript artifacts/astral-bus.jsonl \
  --output artifacts/braid-report.json
```

### Proof Garden

The Proof Garden turns every promoted or quarantined braid into a growth ring in
an append-only Merkle ledger. Each ring binds the previous root, decision type,
dream evidence, and candidate count into a compact leaf. A nightly **pollen
packet** carries one event plus its Merkle audit path, so another runtime can
verify that exact decision without receiving—or trusting—the whole archive.

```bash
python -m bridges.proof_garden \
  --ledger artifacts/proof-garden.jsonl plant \
  --report artifacts/braid-report.json \
  --output artifacts/proof-packet.json
python -m bridges.proof_garden \
  --ledger artifacts/proof-garden.jsonl prove --sequence 1
python -m bridges.proof_garden \
  --ledger artifacts/proof-garden.jsonl audit
```

### Kintsugi Ledger

A fractured proof chain is evidence, not garbage. The Kintsugi Ledger scans for
the longest valid Merkle prefix, preserves every damaged byte in a scar ledger,
and atomically restores only the golden growth rings. The repair certificate
binds the preserved root to hashes of every quarantined fracture, so recovery
never becomes silent rewriting.

```bash
python -m bridges.kintsugi_ledger diagnose --ledger artifacts/proof-garden.jsonl
python -m bridges.kintsugi_ledger repair --ledger artifacts/proof-garden.jsonl
```

### Resurrection Garden

Quarantine is not oblivion. The Resurrection Garden re-reads a preserved
quarantine certificate whenever consent limits or available entropy change. It
can issue a deterministic **awakening certificate**, but that artifact has no
executor: its mandatory activation gate sends the candidate back through the
Astral Braid Conservatory. Futures marked for consent violations carry a
permanent seal; they may be studied, never revived.

```bash
python -m bridges.resurrection_garden \
  --report artifacts/braid-report.json \
  --proof-packet artifacts/proof-packet.json \
  --contract-file configs/resurrection_contract.json \
  --environment-file configs/resurrection_environment.json \
  --output artifacts/resurrection.json
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
