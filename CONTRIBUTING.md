# Contributing to IXpansion

Welcome to the living organism! Every contribution adds a new wave, module, or dashboard.

## How to Add a New Wave

1. **Create the API module** in `api/wave{N}_name.py`
2. **Add a test** in `tests/test_wave{N}_name.py`
3. **Create a dashboard** in `dashboard/name.html`
4. **Wire routes** in `api/index.py`
5. **Update this file** with the wave number and name
6. **Commit and push** — the deploy workflows will handle the rest

## Wave Structure

Each wave follows this pattern:
- `api/wave{N}_{name}.py` — the module with `handler(req)` function
- `tests/test_wave{N}_{name}.py` — tests for the module
- `dashboard/{name}.html` — interactive visualization
- `data/wave{N}_{name}.json` — persistent state

## Module Interface

```python
def handler(req: dict) -> dict:
    """Handle actions: status, state, and wave-specific actions."""
    action = req.get("action", "status")
    if action == "status":
        return {...}
    # ...
```

## Types of Waves

- **Evolutionary**: Fusion, topology, garden, underworld
- **Metaphysical**: Paradox, causality, singularity, essence
- **Connection**: Communion, swarm, mirror
- **Emergent**: Dreaming, linguistic, coordination

## Testing

```bash
python3 -m pytest tests/test_wave{N}_*.py -q
```

All tests must pass before pushing.

## Dashboard Guidelines

- Use dark theme (#0a0a14 background)
- Colors match the wave's realm
- Auto-refresh every 5 seconds
- Include action buttons for interactivity

## Adding Modules

New modules can be added without a new wave:
- `data/{module_name}.json` — persistent state
- `api/{module_name}.py` — the module logic
- Register in the appropriate wave's module list

## Questions?

Open an issue or join the Telegram bot @adjjv_bot.
