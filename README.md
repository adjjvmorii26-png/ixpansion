# Omega Systems

Three interconnected experimental frameworks for multi-agent simulation, consciousness modeling, and observatory bootstrapping.

## Projects

| Project | Language | Tests | Purpose |
|---------|----------|-------|---------|
| **omega_prime** | Python 3.11+ | 110 | Multi-agent sandbox with entropy budgets, quantum superposition, morphic fields, pheromone trails, temporal realms, and emergent speciation |
| **omega_fractal_engine** | Python 3.11+ | 36 | Self-expanding consciousness engine with mutable physics, dimensional folding, paradox resolution, and self-rewriting code |
| **nexus_observatory** | R + Bash | — | Modular boot system with plugin architecture, health checks, and diagnostics |

## Quick Start

### Omega Prime
```bash
python3 -m pytest omega_prime/tests/
python3 omega_prime/scripts/run_dev.py
```

### Omega Fractal Engine
```bash
python3 -m pytest omega_fractal_engine/tests/
```

### Nexus Observatory
```bash
./nexus_observatory/nexus_boot.sh boot
./nexus_observatory/nexus_boot.sh doctor
```

## Architecture

```
├── omega_prime/                  # Multi-agent sandbox framework
│   ├── nucleus/kernel/           # StateCore, Reactor, PulseLoop, EntropyGovernor,
│   │                             #   SuperpositionState, CausalGraph, PulseHarmonics,
│   │                             #   ChronicleEngine
│   ├── nucleus/interfaces/       # AgentPort, SandboxPort, ProtocolPort
│   ├── agents/                   # BaseAgent, Registry, species (Sentinel/Architect/Wanderer),
│   │                             #   cognition (DreamCycle, MorphicField, GoalStack...),
│   │                             #   SymbiosisManager, SpeciationEngine, GhostProtocol
│   ├── sandbox/                  # Conductor, realms (void/lattice/continuum/temporal),
│   │                             #   modules (pheromone field, physics, reality fabric...),
│   │                             #   fossil layer, dimensional fold
│   ├── protocols/hex/            # Binary codec (3 dialects), glyph codec, event bus
│   └── tests/                    # 110 tests across all subsystems
│
├── omega_fractal_engine/         # Self-expanding consciousness engine
│   ├── nucleus/kernel/           # Axioms (immutable laws), EntropyRegulator, Pulse
│   ├── nucleus/genesis/          # Autogenesis (self-bootstrapping), RecursionDriver
│   ├── nucleus/identity/         # MoodVectors, dialects, signatures
│   ├── lattice/                  # Euclidean/non-Euclidean/hyperbolic spaces,
│   │                             #   TopologyEngine, PortalNetwork
│   ├── agents/                   # AgentFabricator with genetic blending
│   ├── rituals/                  # Convergence, divergence, metamorphosis, invocation
│   ├── archives/                 # EchoIndex (memory search), chronicle/anomalies/dreams
│   ├── reactors/                 # Chaos/order/fusion/inversion reactors
│   ├── meta/                     # ParadoxSolver (5 strategies), SelfRewrite
│   └── tests/                    # 36 tests
│
├── nexus_observatory/            # R package + bash boot system
│   ├── DESCRIPTION               # R package metadata
│   ├── R/                        # R wrappers for boot system
│   ├── nexus_boot.sh             # Shell entry point with plugin loading
│   └── modules.d/                # Drop-in boot modules
│
└── project_root/                 # Earlier prototype (superseded by omega_prime)
```

## Experimental Systems

| System | Project | Innovation |
|--------|---------|-----------|
| Entropy Budget | omega_prime | Actions drain a thermodynamic reservoir; lockout when depleted |
| Dream Cycle | omega_prime | Idle agents pattern-match memories and discover hidden correlations |
| Morphic Field | omega_prime | Same-species knowledge resonance without explicit communication |
| Quantum Superposition | omega_prime | Agents hedge decisions via amplitude-weighted action collapse |
| Pheromone Field | omega_prime | Stigmergic coordination through evaporating spatial signals |
| Causal Echo Graph | omega_prime | DAG tracing action→effect chains for root-cause analysis |
| Symbiosis Protocol | omega_prime | Cross-species bonds sharing emergent capabilities |
| Speciation Engine | omega_prime | Spontaneous genome mutation under environmental stress |
| Temporal Realm | omega_prime | Grid zones with different time-dilation factors |
| Fossil Layer | omega_prime | Dead agents leave excavatable knowledge fossils in terrain |
| Chronicle Engine | omega_prime | Narrative memory compressed into interpretive stories |
| Reality Fabric | omega_prime | Mutable physics law patches that erode over time |
| Pulse Harmonics | omega_prime | Kuramoto-coupled oscillators; synced actions amplify |
| Ghost Protocol | omega_prime | Depleted agents become observing ghosts that whisper hints |
| Glyph Codec | omega_prime | Self-evolving compression protocol with learned symbol table |
| Axiom System | fractal_engine | Immutable validator laws the engine cannot violate |
| Autogenesis | fractal_engine | Spawns new subsystems from environmental triggers |
| Mood Vectors | fractal_engine | Emotional state simulation with stimulus responses |
| Dimensional Spaces | fractal_engine | Euclidean, non-Euclidean, and hyperbolic geometry |
| Paradox Solver | fractal_engine | Resolves contradictions via superposition/synthesis/temporal strategies |
| Self-Rewrite | fractal_engine | Engine monitors and modifies its own source code |

## License
MIT
