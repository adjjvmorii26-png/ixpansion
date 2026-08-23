# Contributing to ALEPH

## Development Setup

```bash
git clone https://github.com/adjjvmorii26-png/ixpansion.git
cd ixpansion
pip install pytest pytest-asyncio
```

## Running Tests

```bash
python3 -m pytest omega_prime/tests/ -v
python3 -m pytest omega_fractal_engine/tests/ -v
```

## Adding a New Experimental System

1. Place the module in the appropriate directory (`agents/`, `nucleus/kernel/`, `sandbox/modules/`, or `protocols/`)
2. Write tests in `tests/<subsystem>/test_<module_name>.py`
3. All tests must pass: `pytest tests/ -q`
4. Submit a PR targeting `main`

## Code Style

- Python 3.11+, type hints on public functions
- Docstrings on every module explaining what makes it experimental
- No external dependencies in core (stdlib only)
- Tests use only `pytest` and `pytest-asyncio`

## Design Principles

- **Emergence over design**: systems should produce surprising behaviors from simple rules
- **Composition over monolith**: each system is independent; they combine through shared interfaces
- **Testable weirdness**: even the strangest mechanics must have deterministic unit tests
