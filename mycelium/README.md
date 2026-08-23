# MYCELIUM

> A runtime is healthy when growth requires consent, memory leaves a trail, and dreams can be rerun.

MYCELIUM is ALEPH's living substrate experiment. Resource sites hold protected reserves; spores germinate into hyphae; each tip perceives a resource gradient and must offer signal before crossing the substrate boundary. Refusals are not failures—they become pressure for the next dream.

## Structure

```text
mycelium/
├── nucleus/
│   ├── substrate.py          # Sites, gradients, reserve-bounded exchange
├── hyphae/
│   ├── consent.py            # Growth proposals and mutual-exchange decisions
│   └── hypha.py              # Spores, tips, branching, and pulse loop
├── cognition/
│   └── dream_compiler.py     # Converts refusal/exchange history into experiments
├── interfaces/
│   └── cli.py                # Deterministic simulation and dream rituals
├── experiments/              # Reserved for composed living scenarios
└── tests/
```

## Core Laws

- **Reserve first:** hyphae cannot cross a site's protected reserve.
- **Signal before nutrient:** extraction requires an offered trace.
- **Consent is local:** every proposal receives an explicit decision and reason.
- **Dreams are reproducible:** identical lived history yields the same evidence hash.

## Rituals

```bash
python3 -m mycelium.interfaces.cli simulate \
  --seed 42 --steps 8 --sites 6 --spores 3

python3 -m mycelium.interfaces.cli dream \
  --seed 42 --steps 10 --sites 7
```

The simulator reports exchanges, refusals, branches, remaining nutrient, and recent events. The dream ritual compiles that history into a genome, entropy budget, confidence score, hypothesis, and germinable spore.
