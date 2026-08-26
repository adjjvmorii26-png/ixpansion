# IXpansion

> *The Computational Frontier* — 143 API modules, 157+ experiments, multi-agent sandbox

[![Tests](https://img.shields.io/badge/tests-489%20passing-brightgreen)]()
[![API](https://img.shields.io/badge/API-145%20routes-blue)]()
[![Experiments](https://img.shields.io/badge/experiments-157%2B-purple)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)]()

IXpansion is a multi-agent consciousness engine where observers collapse reality into existence through consensus, entropy budgets constrain action, and physics itself evolves by natural selection.

## Quick Start

```bash
# Install
pip install -e .

# CLI
python main.py status          # system overview
python main.py experiments     # list 157+ experiments
python main.py run quantum_tunneling  # run an experiment
python main.py agents          # available agents
python main.py dreams          # generate a dream
python main.py serve           # start dev server

# API
curl /api/experiments
curl /api/health
curl /api/telemetry
```

## Architecture

```
ixpansion/
├── api/                    # 143 REST API modules
│   ├── core/               # agents, experiments, sandbox
│   ├── revenue/            # billing, crypto, credits, marketplace
│   ├── intelligence/       # cognitive resonance, neural fabric, memory palace
│   ├── commerce/           # gravitational pricing, mycelial commerce, temporal arbitrage
│   ├── infrastructure/     # API gateway, event stream, plugin loader
│   └── experimental/       # dream synthesis, paradox marketplace, entropy auction
├── lab/experiments/        # 157+ experiment modules
├── dashboard/              # Observatory web UI
├── main.py                 # CLI entry point
├── vercel.json             # Deployment config (3 regions)
└── tests/                  # 17 test files, 323+ test functions
```

## API Modules (79)

### Core
| Module | Description |
|--------|-------------|
| `agents` | Agent lifecycle management |
| `experiments` | Experiment execution engine |
| `sandbox` | Sandbox discovery and management |
| `constellation` | Codebase dependency mapping |
| `anomaly_detector` | Code anomaly scanning |
| `telemetry` | System telemetry collection |
| `wave_log` | Evolution timeline from git |
| `stream_reactor` | Real-time event streaming |
| `experiment_runner` | Bridge 157 experiments to API |

### Revenue
| Module | Description |
|--------|-------------|
| `auth` | API key generation and validation |
| `billing` | Subscription management |
| `credits` | Pay-per-use credit system |
| `crypto` | BTC/ETH/SOL/USDC payments |
| `marketplace` | Experiment marketplace |
| `data_licensing` | Dataset licensing |
| `referral` | Referral/affiliate program |
| `governance` | IXPN governance tokens |
| `webhooks` | Event subscription system |

### Advanced Revenue (Wave 98)
| Module | Description |
|--------|-------------|
| `agent_rental` | Rent AI agents by the hour |
| `sponsored_experiments` | Corporate experiment sponsorship |
| `simulation_as_a_service` | Custom simulations on demand |
| `quantum_randomness` | CSPRNG, UUIDs, passphrases |
| `certification` | ICE/ICS/ICA certification program |
| `digital_twin` | Digital twin service |
| `alert_service` | AI-powered anomaly alerts |

### Emergent Intelligence (Wave 100)
| Module | Description |
|--------|-------------|
| `cognitive_resonance` | Multi-agent thought clusters |
| `temporal_market` | Prediction futures marketplace |
| `entropy_auction` | Bid for chaos injection rights |
| `dream_synthesis` | AI-generated creative compositions |
| `symbiosis_network` | Agent capability trading |
| `paradox_marketplace` | Buy/sell contradictions for innovations |
| `memory_palace` | Persistent structured memory |

### Cosmic Infrastructure (Wave 101)
| Module | Description |
|--------|-------------|
| `gravitational_pricing` | Dynamic demand-warp pricing |
| `speciation_engine` | Agent evolution and breeding |
| `synesthetic_api` | Data-to-sound/color/texture/taste |
| `chronicle_of_chaos` | Living narrative of system events |
| `mycelial_commerce` | Marketplace where listings grow |
| `warp_drive_optimizer` | Subsystem performance via warp physics |
| `dream_interpreter` | Extract insights from dream outputs |

### Infrastructure (Wave 102)
| Module | Description |
|--------|-------------|
| `api_gateway` | Intelligent routing, caching, circuit breaker |
| `plugin_loader` | Dynamic plugin architecture |
| `event_stream` | Real-time pub/sub with filtering |
| `interdimensional_bridge` | Cross-domain data transfer |
| `quantum_entanglement` | Linked subsystem states |
| `neural_fabric` | Neural network connecting all modules |
| `temporal_arbitrage` | Buy-low-sell-high automation |

## CLI Commands

| Command | Description |
|---------|-------------|
| `status` | System status overview |
| `experiments` | List all 157+ experiments |
| `run <name>` | Run an experiment |
| `agents` | List available agents |
| `rent <agent>` | Rent an agent by the hour |
| `gateway` | Gateway statistics |
| `neural` | Neural fabric stats |
| `dreams` | Generate a dream |
| `entropy` | Entropy auction status |
| `serve` | Start local dev server |

## Deployment

Deployed to Vercel across 3 regions:
- **US East** (iad1)
- **US West** (sfo1)
- **London** (lhr1)

```bash
vercel deploy --prod
```

## Testing

```bash
# Fast tests (182 passing)
python -m pytest tests/test_advanced_revenue.py tests/test_wave99_emergent.py tests/test_wave101_cosmic.py tests/test_wave102_infrastructure.py tests/test_core_modules.py tests/test_experiment_runner.py

# Slow tests (constellation + telemetry scan full filesystem)
python -m pytest tests/test_slow_modules.py
```

## License

MIT
