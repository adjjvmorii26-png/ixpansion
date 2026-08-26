# Contributing to IXpansion

## Development Setup

```bash
git clone https://github.com/adjjvmorii26-png/ixpansion.git
cd ixpansion
pip install -e .
pip install pytest pytest-asyncio
```

## Running Tests

```bash
python3 -m pytest tests/ -q           # quick (813 tests)
python3 -m pytest tests/ -v           # verbose
python3 -m pytest tests/test_core_modules.py  # core only
```

## Adding a New Module

1. Create the module in `api/<module_name>.py`
2. Include a `handler(payload, context)` function for router compatibility
3. Add vercel route to `vercel.json`
4. Write tests in `tests/test_<wave>_<layer>.py`
5. Update `CHANGELOG.md` with the new module
6. All tests must pass before submitting

## Code Style

- Python 3.11+, type hints on public functions
- Docstrings on every module explaining what it does
- `from __future__ import annotations` must be the first import
- No external dependencies in core (stdlib only)
- Tests use only `pytest` and `pytest-asyncio`

## Design Principles

- **Emergence over design**: systems produce surprising behaviours from simple rules
- **Composition over monolith**: each module is independent; they combine through shared interfaces
- **Testable weirdness**: even the strangest mechanics must have deterministic unit tests
- **Backward compatibility**: new modules must not break existing tests
