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
| [`bridges`](bridges/) | Python | 102 | Counterfactual twins, causal replay, resilience analysis, semantic treaties, reversible braids, and Kintsugi ledger repair |
| [`mycelium`](mycelium/) | Python | 12 | Consent-bounded living substrate: spores, hyphal gradients, and dream compilation |
| [`ixpansion`](ixpansion/) | Python | 37 | Self-expanding HEX mesh: agent-coupled routing, HEX witnesses, world scenes, mutations, and preserved glitches |
| [`solid-organism`](solid-organism/) | Python | 13 | Deterministic organism labs: kintsugi seams, dice constellations, consent-bounded cordyceps, negative space, and synthetic mood superposition |
| [`constellation`](constellation/) | Python | 42 | Dispersed repository resonance: scored concepts, adapter targets, integration graphs, and phased ritual contracts |
| [`chrono_forge`](lab/chrono_forge/) | Python | 93 | Pinned ritual automation: pulse heartbeat, sentinel invariants, sandbox entropy budget, Forge Mind triage, and proof runner |

## Run Tests

```bash
make test
# or: python3 -m pytest
```

The complete monorepo suite contains **715 tests**.

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

## Chrono Forge

Chrono Forge is the executable refinement bench for pulse-driven agents and sandbox worlds. Its pinned runner proves the critical heartbeat, sentinel, sandbox, smoke, and Forge Mind paths on every schedule; optional acts cover flux, void timing, proof density, constellations, and handshake artifacts. The Runtime Vault centralizes state under an atomic, lock-protected `.runtime/lab` root; every new proof record is linked by sequence and SHA-256, with Sentinel failing closed on a broken chain. The Pulse Oracle converts that evidence into deterministic entropy forecasts and reversible ritual recommendations. A three-faction Parliament votes those forecasts into sealed, self-contained policy directives. The Reversible Mandate Engine then rehearses each mandate on a ghost timeline before live execution; it enforces quorum, freshness, entropy floors, rollback thresholds, and a hard seven-tick cap while sealing one hash-chained witness per tick. Witness failure restores the pre-mandate world and records the rollback as evidence rather than hiding it. The Mandate Resonance Loom verifies each execution certificate and publishes a Nexus-compatible pulse; rehearsal pulses are explicitly marked as dreams. The Mandate Genome Forge then converts verified outcomes into sealed, data-only behavioral lineages: successes are breedable under a compatibility radius, while dreams and rollbacks remain quarantined evidence. The Ancestral Echo Engine rehearses a sealed lineage against the present world without mutation, classifying it as resonant, drifting, fossilized, quarantined, or dormant. The Genome Observatory compiles that population into a sealed lineage atlas with diversity pressure, ancestry checks, monoculture warnings, and unrelated pairing recommendations. The Evolution Council then compiles ancestry, resonance, diversity, and safety warnings into a sealed advisory playbook; breeding proposals remain non-executable without explicit operator consent. A separate two-phase Evolution Consent Gate binds approval to an out-of-band HMAC key, a nonce, the Council hash, and a hash-chained request witness before any single breeding action can run. The Temporal Paradox Resolver then correlates every sealed JSONL ledger without mutation, grouping related witnesses into deterministic paradox constellations with a bounded risk index; it classifies identity collisions, state forks, clock regressions, replay echoes, broken chains, and post-terminal activity into fail-closed forensic resolutions. The Repair Dream Weaver then compiles those constellations into sealed, data-only recovery blueprints: forks branch without deleting evidence, regressions name their rewind anchors, and every mutating action remains explicitly non-executable. The Ghost Repair Theater then rehearses those blueprints on synthetic branches—preserving fork witnesses, splitting regressed timelines, partitioning identity collisions, and quarantining unsafe archetypes without touching a source ledger. The Recovery Quorum then convenes Archivist, Sentinel, and Explorer offices over those stages; safe branches receive sealed consent packets, blocked archetypes go to a human tribunal, and no packet ever carries execution authority. The Recovery Atlas fuses those four sealed perspectives into one deterministic HTML/SVG constellation, making paradox risk, ghost branches, office votes, and human-signature packets visible without granting execution authority. A separate manual-only Recovery Treaty Compiler can bind one ready packet to immutable source bytes under two independent out-of-band HMAC keys; its only granted authority is presentation to a human tribunal, never mutation. A manual Recovery Tribunal Dossier then seals that handoff into a printable witness-glyph certificate with an explicit empty executor registry and offline checklist. A manual Recovery Verdict Recorder then seals approve/reject/defer outcomes under two independent juror keys; even approval only authorizes drafting a separate executor contract, never mutation itself.

```bash
make test-lab
make mandate-dry
make mandate-run
python3 lab/pulse_oracle.py --horizon 9
python3 lab/ritual_parliament.py
python3 lab/reversible_mandate.py --dry-run
python3 bridges/mandate_resonance.py --no-publish
python3 lab/mandate_genome.py forge
python3 lab/mandate_genome.py list
python3 lab/genome_observatory.py census
python3 lab/genome_observatory.py atlas
python3 lab/ancestral_echo.py @latest --no-ledger
python3 lab/evolution_council.py --no-ledger
python3 lab/temporal_paradox.py --no-ledger
python3 lab/repair_dreams.py --no-ledger
python3 lab/repair_theater.py --no-ledger
python3 lab/recovery_quorum.py --no-ledger
python3 lab/recovery_atlas.py --output .runtime/lab/reports/recovery-atlas.html
ALEPH_TREATY_KEY_ONE=first-key ALEPH_TREATY_KEY_TWO=second-key \
  python3 lab/recovery_treaty.py sign .runtime/lab/ledgers/source.jsonl \
  --operator-one archivist --operator-two sentinel
ALEPH_VERDICT_KEY_ONE=juror-one ALEPH_VERDICT_KEY_TWO=juror-two \
  python3 lab/recovery_verdict.py record --report recovery-dossier.json \
  --verdict approve --rationale "separate human review is required" \
  --operator-one juror-one --operator-two juror-two
ALEPH_EXECUTOR_CONTRACT_KEY_ONE=reviewer-one ALEPH_EXECUTOR_CONTRACT_KEY_TWO=reviewer-two \
  python3 lab/recovery_executor_contract.py forge --report recovery-verdict.json
ALEPH_EXECUTOR_CONTRACT_KEY_ONE=reviewer-one ALEPH_EXECUTOR_CONTRACT_KEY_TWO=reviewer-two \
  python3 lab/recovery_shadow_red_cell.py convene --report recovery-executor-contract.json
python3 lab/run_pinned.py --critical-only
python3 lab/run_pinned.py
```

## Constellation Corpus

Constellation Corpus turns dispersed concept repositories into one mergeable map instead of duplicating their scaffolding. Each source is scored for structural richness, symbolic payload, density, and adapter fit; recommendations become `integrate_concept`, `prototype_adapter`, or `preserve_reference` actions mapped to an existing IXpansion subsystem.

```bash
python3 -m constellation.engine plan
python3 -m constellation.engine graph
python3 -m constellation.engine weave --format markdown
python3 -m constellation.engine rehearse --format markdown
python3 -m constellation.engine recover --format markdown
python3 -m constellation.engine negotiate --format markdown
python3 -m constellation.engine atlas --output runs/constellation-atlas.html
make test-constellation
```

Before a concept touches its target, the Shadow Rehearsal replays every phase under a deterministic chaos budget. Nested targets are quarantined, failed releases receive rollback witnesses, and the complete ledger remains replayable from `weave_hash` plus `rehearsal_hash`. Recovery Braids close the loop: collision groups split into non-overlapping lanes, while rollback failures become bounded retry orbits tied to their original witnesses. Lane Treaties then negotiate pairwise consent for namespace partitioning, event leases, witness exchange, rollback noninterference, and stale-lease arbitration. The Atlas compiles every layer into one dependency-free HTML/SVG observatory, preserving the full canonical hash chain.

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
