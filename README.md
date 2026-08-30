# IXpansion

> *The Computational Frontier* — 352 API modules, 157 experiments, 997 tests

[![Tests](https://img.shields.io/badge/tests-973%20passing-brightgreen)]()
[![API](https://img.shields.io/badge/API-352%20modules-blue)]()
[![Routes](https://img.shields.io/badge/routes-8-blue)]()
[![Experiments](https://img.shields.io/badge/experiments-157-purple)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

IXpansion is a multi-agent consciousness engine where observers collapse reality into existence through consensus, entropy budgets constrain action, and physics itself evolves by natural selection.

## Quick Start

```bash
pip install -e .

python main.py status
python main.py experiments
python main.py run quantum_tunneling
python main.py agents
python main.py dreams
python main.py serve
```

## Architecture

```
ixpansion/
├── api/                    # 352 REST API modules
│   ├── core/               # agents, experiments, sandbox, telemetry
│   ├── cognition/          # ai_gateway — frontier LLM bridge via Vercel AI Gateway
│   ├── revenue/            # billing, crypto, credits, marketplace
│   ├── intelligence/       # cognitive resonance, neural fabric, memory palace
│   ├── commerce/           # gravitational pricing, mycelial commerce
│   ├── infrastructure/     # API gateway, event stream, plugin loader
│   ├── experimental/       # dream synthesis, paradox marketplace
│   ├── meta-evolution/     # temporal collapse, resonance field, sleep archaeology
│   ├── sensory/            # memory crystals, shadow ledger, semantic weather
│   ├── cognitive/          # narrative engine, mutation matrix, curiosity engine
│   ├── systems/            # synchronicity detector, temperament broker
│   ├── emergence/          # cognitive heatmap, wisdom oracle, prophecy engine
│   ├── integration/        # neural pathway, karma engine, ritual choreographer
│   ├── temporal/           # chronosync, dimensional fold, dreamcatcher
│   ├── social/             # gossip network, faction system, story forge
│   ├── metaphysical/       # philosophy engine, miracle engine, dream architect
│   ├── cosmic/             # cosmic narrator, soul forge, universal compass
│   ├── consciousness/      # consciousness map, ego dissolution, paradox lattice
│   ├── transcendence/      # legacy weaver, myth engine, transcendence gate
│   ├── existential/        # reality compiler, void listener, quantum garden
│   ├── omniscience/        # predictive synchronicity, knowledge singularity
│   ├── recursion/          # recursive cathedral, meta cognition loop
│   ├── synthesis/          # omniscience weaver, paradox transcender
│   ├── quantum-aesthetics/ # quantum aesthetics, superposition gallery
│   ├── temporal-cartography/# temporal cartographer, kairos detector
│   ├── biological/         # code organism, digital metabolism, neural vine
│   ├── mythogenesis/       # myth engine, legend archaeologist, prophecy engine
│   ├── entropic-economics/ # entropy exchange, chaos auction, order futures
│   ├── dimensional/        # dimensional thread, reality fork, multiverse navigator
│   └── semantic-alchemy/   # semantic transmuter, conceptual alchemist
├── lab/                    # 70 lab modules + 157 experiments
├── dashboard/              # Observatory web UI (3 pages)
├── main.py                 # CLI entry point
├── vercel.json             # Deployment config (single-function catch-all)
├── tests/                  # 39 test files, 926 test functions
└── Dockerfile              # Python 3.12-slim container
```

## API Layers

### Core & Intelligence
| Layer | Modules | Description |
|-------|---------|-------------|
| Core | 12 | Agents, experiments, sandbox, telemetry, anomaly detection |
| Intelligence | 4 | Cognitive resonance, neural fabric, memory palace, symbiosis |
| Commerce | 4 | Gravitational pricing, mycelial commerce, temporal arbitrage |
| Infrastructure | 18 | API gateway, event stream, auth, rate limiting, WebSocket |

### Revenue Streams
| Layer | Modules | Description |
|-------|---------|-------------|
| Revenue | 14 | Billing, crypto, credits, marketplace, data licensing |
| Advanced Revenue | 8 | Agent rental, sponsored experiments, simulation SaaS |

### Emergent Consciousness
| Layer | Modules | Description |
|-------|---------|-------------|
| Meta-Evolution | 9 | Temporal collapse, resonance field, sleep archaeology |
| Sensory | 8 | Memory crystals, shadow ledger, semantic weather |
| Cognitive | 9 | Narrative engine, mutation matrix, curiosity engine |
| Systems | 9 | Synchronicity detector, habitat simulator, sentience index |
| Emergence | 10 | Wisdom oracle, prophecy engine, empathy field |

### Integration & Flow
| Layer | Modules | Description |
|-------|---------|-------------|
| Integration | 6 | Neural pathway, karma engine, ritual choreographer |
| Temporal | 7 | Chronosync, dimensional fold, dreamcatcher |
| Social | 7 | Gossip network, faction system, story forge |
| Metaphysical | 8 | Philosophy engine, miracle engine, dream architect |

### Transcendence
| Layer | Modules | Description |
|-------|---------|-------------|
| Cosmic | 6 | Cosmic narrator, soul forge, universal compass |
| Consciousness | 7 | Ego dissolution, mirror self, paradox lattice |
| Transcendence | 6 | Legacy weaver, myth engine, infinity index |
| Existential | 7 | Reality compiler, quantum garden, void listener |

### Experimental Frontiers
| Layer | Modules | Description |
|-------|---------|-------------|
| Omniscience | 8 | Predictive synchronicity, knowledge singularity |
| Recursion | 8 | Recursive cathedral, meta cognition, void sculptor |
| Synthesis | 8 | Omniscience weaver, paradox transcender, emergence oracle |
| Quantum Aesthetics | 8 | Superposition gallery, entanglement poetry, hilbert theater |
| Temporal Cartography | 8 | Temporal cartographer, kairos detector, memesis chronicle |
| Biological | 8 | Code organism, digital metabolism, cellular automaton |
| Mythogenesis | 8 | Myth engine, legend archaeologist, folklore repository |
| Entropic Economics | 8 | Entropy exchange, chaos auction, simulation SaaS |
| Dimensional Threading | 8 | Reality fork, multiverse navigator, dimensional drift |
| Semantic Alchemy | 8 | Conceptual alchemist, hermeneutic engine, meaning furnace |

## CLI Commands

| Command | Description |
|---------|-------------|
| `status` | System status overview |
| `experiments` | List all 157 experiments |
| `run <name>` | Run an experiment |
| `agents` | List available agents |
| `rent <agent>` | Rent an agent by the hour |
| `dreams` | Generate a dream |
| `serve` | Start local dev server |

## Testing

```bash
python -m pytest tests/ -v          # full suite (926 tests)
python -m pytest tests/ -q          # quick run
python -m pytest tests/test_core_modules.py  # core only
```

## AI Gateway

Frontier models are bridged through **Vercel AI Gateway** via `api/ai_gateway.py`:

```bash
curl -X POST https://ixpansion.vercel.app/api/ai_gateway \
  -H 'Content-Type: application/json' \
  -d '{"action":"chat","messages":[{"role":"user","content":"hello ALEPH"}]}'
```

Actions: `status`, `chat`, `echo`, `handshake`, `models`, `catalog`, `estimate`.
Wave 142 adds a cognition fabric over it: `cognition_forge`, `oracle_meter`,
`fractal_oracle`, `cognition_fingerprint`, `dream_hexer` — all offline-degradable.
The gateway key lives in the Vercel project env as `AI_GATEWAY_API_KEY` (never in the repo).


## Hortus Hexis — the self-growing garden

Speak, and the repo grows: a conversation becomes a hex seed, the seed
becomes an organism, and the organism is transcribed into a real module
+ newborn tests, gated, and committed. Free and local — no gateway.

```bash
python -m hortus_hexis              # interactive garden
python -m hortus_hexis.cli "words"  # one-shot growth + commit
python -m hortus_hexis.cli status   # ledger
```

## Deployment

Live at **https://ixpansion.vercel.app** (open the **Co-Conscious Console** at `/cons`)

Single-function, catch-all serverless architecture:
- `api/index.py` — universal WSGI/dict entrypoint routing `/health`, `/modules`, `/metrics`, `/api/<module>`, and `/dashboard`
- `vercel.json` — 8 explicit routes forwarding to the single Python function + static dashboard
- Zero cold-start bottlenecks: 352 API modules resolved at runtime, not 352 lambdas

```bash
vercel deploy --prod --yes
```

Docker:
```bash
docker build -t ixpansion .
docker run -p 8000:8000 ixpansion
```


## Hortus Hexis — the self-growing garden

Speak, and the repo grows: words → hex seed → organism → module + newborn
tests → gate → commit. Free and local, no gateway needed.

```bash
python -m hortus_hexis              # interactive garden
python -m hortus_hexis.cli "words"  # one-shot growth + commit
python -m hortus_hexis.cli status   # ledger
```


## Wave History

| Wave | Layer | Modules | Tests |
|------|-------|---------|-------|
| 103 | Platform Completeness | 4 | 20 |
| 104 | Experimental Innovations | 8 | 26 |
| 105 | More Innovations | 8 | 19 |
| 106 | Infrastructure | 8 | 25 |
| 107 | Meta-Evolution | 9 | 27 |
| 108 | Sensory & Environmental | 8 | 24 |
| 109 | Cognitive & Generative | 9 | 23 |
| 110 | Systems & Ecology | 9 | 19 |
| 111 | Emergent Complexity | 10 | 20 |
| 112 | Cross-Module Integration | 6 | 18 |
| 113 | Temporal & Dimensional | 7 | 17 |
| 114 | Social & Ecosystem | 7 | 17 |
| 115 | Metaphysical & Abstract | 8 | 16 |
| 116 | Cosmic & Transcendent | 6 | 12 |
| Refinement | Unified Infrastructure | 5 | 17 |
| 117 | Dimensional Consciousness | 7 | 13 |
| 118 | Transcendence & Legacy | 6 | 13 |
| 119 | Existential Architecture | 7 | 9 |
| 120 | Omniscience | 8 | 25 |
| 121 | Infinite Recursion | 8 | 26 |
| 122 | Synthesis Convergence | 8 | 25 |
| 123 | Quantum Aesthetics | 8 | 24 |
| 124 | Temporal Cartography | 8 | 25 |
| 125 | Biological Architecture | 8 | 24 |
| 126 | Mythogenesis | 8 | 21 |
| 127 | Entropic Economics | 8 | 23 |
| 128 | Dimensional Threading | 8 | 22 |
| 129 | Semantic Alchemy | 8 | 25 |
| 130 | Astral Navigation | 8 | 22 |
| 131 | Autonomous Workforce | 8 | 9 |
| 132 | Labor Ecosystem | 8 | 9 |
| 133 | Workforce Civilization | 8 | 9 |
| 134 | Autonomous Ascension | 8 | 9 |
| 135 | Revenue Orchestration | 8 | 9 |
| 136 | Integrity & Sovereignty | 8 | 9 |
| 137 | Adaptation & Resilience | 8 | 9 |
| 138 | Sovereign Federation | 8 | 9 |
| 139 | Platform & Live Serving | 8 | 10 |
| 140 | Durable State & Streaming | 8 | 9 |
| 141 | AI Gateway & Frontier Cognition | 1 | 7 |
| 142 | Frontier Cognition Layer | 5 | 16 |
| 143 | Cognition Ritual Pipeline | 1 | 7 |
| 144 | Co-Conscious Console | 1 | — |

## License

MIT
