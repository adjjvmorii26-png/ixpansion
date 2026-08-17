# IXPANSION Development Guide

Complete guide for developing, testing, and contributing to IXPANSION.

## Quick Setup

### Prerequisites
- Python 3.12+
- pip
- Docker & Docker Compose (for full stack demo)

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/adjjvmorii26-png/ixpansion.git
cd ixpansion

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests to verify setup
make verify
```

### Optional: TokenRouter Integration

For premium model support:

```bash
# Copy the example env file
cp .env.example .env

# Add your API key to .env
# TOKENROUTER_API_KEY=your_key_here

# Test the connection
python -c "from agent import Agent; a = Agent(); print(a.ask('Hello'))"
```

## Project Structure

```
ixpansion/
├── agents.py                 # Agent roles and specifications
├── agent.py                  # Core Agent class with skills
├── workforce.py              # Multi-agent coordination
├── mission_director.py        # Mission planning and execution
├── aether_lattice.py         # Foundation layer coordinator
├── lattice_stack.py          # Machine lattice and trust
├── federated_stack.py        # Federation and PSO
├── security_controls.py      # Trust and audit controls
├── resource_*.py             # Resource management
├── api/
│   ├── __init__.py
│   └── main.py               # FastAPI REST endpoints
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_api.py
│   ├── test_workforce.py
│   └── ...
├── .github/
│   ├── agents/               # Agent definitions
│   ├── skills/               # Skill documentation
│   ├── workflows/            # Workflow templates
│   └── copilot-instructions.md
├── Makefile                  # Common commands
├── requirements.txt          # Python dependencies
├── pytest.ini                # Pytest configuration
├── docker-compose.yml        # Local swarm demo
├── Dockerfile                # Container image
├── README.md                 # Main documentation
├── AGENTS.md                 # Agent reference
├── API.md                    # API reference
├── DEVELOPMENT.md            # This file
└── AGENTS_QUICK_START.md    # Quick reference
```

## Common Commands

### Testing

```bash
# Run all tests
make verify

# Run just agent tests
make test

# Run just workforce tests
make workforce-test

# Run specific test file
python -m unittest tests.test_agent -v

# Run specific test class
python -m unittest tests.test_agent.TestAgent -v

# Run specific test method
python -m unittest tests.test_agent.TestAgent.test_list_skills -v
```

### Compilation & Linting

```bash
# Compile all Python files
make compile

# Check just agent modules
make workforce-lint

# Show compilation errors
python -m py_compile agents.py workforce.py
```

### Running the Application

```bash
# Run CLI agent
python run_agent.py --goal "Explore the mesh"

# Run with options
python run_agent.py \
  --name "explorer" \
  --goal "Inspect the API" \
  --dashboard

# Run API server
python -m uvicorn api.main:app --reload

# Run full stack (requires Docker)
docker-compose up
```

### Development Commands

```bash
# Check workforce status
make workforce-status

# Run interactive demo
python demo_workforce.py

# Format with editorconfig
# (your editor should auto-format on save)

# Check gitattributes are applied
git attributes
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Use conventional branch names:
- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation only
- `refactor/description` - Code improvements
- `test/description` - Test additions

### 2. Make Your Changes

Follow these patterns:

**Python Code:**
```python
def my_function(arg: str) -> str:
    """One-line description of what it does.
    
    Longer explanation if needed, including:
    - Side effects
    - Network or credential requirements
    - Guarantees (e.g., offline-safe, deterministic)
    """
    # Implementation
    return result
```

**Safety Checklist:**
- [ ] No secrets in code, tests, or documentation
- [ ] Type hints on all function parameters and returns
- [ ] Docstring for all public functions and classes
- [ ] Tests for new behavior
- [ ] Offline-safe by default (no required network)
- [ ] Bounded execution (no infinite loops)

### 3. Test Your Changes

```bash
# Run relevant tests
make workforce-test  # If you modified agents/workforce
make test           # For all tests

# Check type hints
python -m py_compile your_file.py

# Run the demo if you added new features
python demo_workforce.py
```

### 4. Commit with Conventional Messages

```bash
git add .
git commit -m "feat(agents): add new capability routing

- Add capability-based agent discovery
- Implement workload balancing algorithm
- Add tests for routing edge cases"
```

**Commit types:**
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `test:` - Test additions
- `refactor:` - Code improvement
- `chore:` - Build, deps, tooling

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a pull request with:
- Clear description of changes
- Why the change is needed
- How to test it
- Any affected layers or systems

## Testing Guidelines

### Unit Tests

Test individual functions in isolation:

```python
import unittest
from agents import get_agent_spec, AgentRole

class TestAgentRegistry(unittest.TestCase):
    def test_builder_has_code_generation(self):
        spec = get_agent_spec(AgentRole.BUILDER)
        self.assertTrue(spec.has_capability(AgentCapability.CODE_GENERATION))

if __name__ == "__main__":
    unittest.main()
```

### Integration Tests

Test multiple components working together:

```python
def test_mission_execution_with_real_agents(self):
    """Test end-to-end mission execution."""
    director = get_mission_director()
    
    # Create and execute mission
    mission_id = director.frame_mission(...)
    plan = director.plan_mission(...)
    result = director.execute_mission(mission_id, auto_approve=True)
    
    # Verify result
    self.assertEqual(result['status'], 'success')
```

### Test Coverage Areas

Required for merge:
- **Happy path** - Normal operation with valid input
- **Boundary cases** - Edge values (empty, zero, max)
- **Error handling** - Invalid input, timeouts, failures
- **State changes** - Task lifecycle, agent state
- **Dependencies** - Multi-step workflows

### Running with Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run -m unittest discover -s tests

# Generate report
coverage report
coverage html  # Creates htmlcov/index.html
```

## Code Quality Standards

### Type Hints

All public functions must have complete type hints:

```python
# ✅ Good
def route_task(task_id: str, role: AgentRole) -> Optional[AgentRole]:
    """Route a task to an agent."""
    ...

# ❌ Bad (missing types)
def route_task(task_id, role):
    ...
```

### Docstrings

All public classes and functions need docstrings:

```python
# ✅ Good
def complete_task(self, task_id: str, result: Dict[str, Any]) -> None:
    """Mark a task as complete with its result.
    
    Args:
        task_id: The task identifier.
        result: The task's output dictionary.
    """
    ...

# ❌ Bad (no docstring)
def complete_task(self, task_id, result):
    self.tasks[task_id].status = TaskStatus.COMPLETE
    ...
```

### Naming Conventions

- Classes: `PascalCase` (e.g., `AgentInstance`)
- Functions/methods: `snake_case` (e.g., `route_task`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `AGENT_REGISTRY`)
- Private methods: prefix with `_` (e.g., `_timestamp()`)

### Line Length

Max line length: 100 characters (enforced by `.editorconfig`)

### Imports

Order imports as:
1. Standard library
2. Third-party packages
3. Local modules

```python
import os
import json
from dataclasses import dataclass
from typing import Any, Dict

from fastapi import FastAPI

from agent import Agent
from workforce import get_workforce
```

## Debugging

### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now logs will show detailed information
```

### Run Single Test with Print

```bash
python -m unittest tests.test_agent.TestAgent.test_list_skills -v
```

### Use Python Debugger

```python
import pdb; pdb.set_trace()  # Stop here
# or
breakpoint()  # Python 3.7+
```

### Check Agent State

```python
from agents import get_agent_spec
from workforce import get_workforce

workforce = get_workforce()
spec = get_agent_spec(AgentRole.BUILDER)
print(spec.skills)
print(workforce.report_workforce_status())
```

## Performance Optimization

### Profiling

```bash
python -m cProfile -s cumulative run_agent.py --goal "test" | head -20
```

### Memory Usage

```python
import tracemalloc
tracemalloc.start()
# Your code
current, peak = tracemalloc.get_traced_memory()
print(f"Current: {current / 1024}KB; Peak: {peak / 1024}KB")
```

## Documentation Updates

When adding features, update:
1. **Docstrings** in code (must-have)
2. **AGENTS.md** if adding agent roles/capabilities
3. **API.md** if adding API endpoints
4. **README.md** if it affects quick start
5. **AGENTS_QUICK_START.md** if it affects common usage

## Security Checklist

Before submitting any change:

- [ ] No credentials in code or examples
- [ ] No `except:` bare clauses (catch specific exceptions)
- [ ] No `eval()` or `exec()`
- [ ] No `import *`
- [ ] SQL/template injection prevention
- [ ] Input validation for all user input
- [ ] No sensitive data in logs
- [ ] Authorization checks in place
- [ ] Rate limiting for APIs (if applicable)
- [ ] Secrets stored in environment, not files

## Troubleshooting

### ImportError: No module named 'xyz'

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
python -c "import xyz; print(xyz.__file__)"
```

### Test failures after environment changes

```bash
# Clear Python cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Reinstall
pip install --upgrade -r requirements.txt

# Re-run tests
make verify
```

### Docker Compose issues

```bash
# Rebuild images
docker-compose build --no-cache

# Check configuration
make swarm-config

# View logs
docker-compose logs -f
```

## Contributing

See `.github/copilot-instructions.md` for the IXPANSION workflow and safety boundaries.

Key points:
1. Preserve user changes in dirty worktrees
2. Never commit/push without explicit request
3. Establish behavior before editing
4. Keep offline paths deterministic
5. Bound retries, budgets, external effects
6. Report evidence, limitations, simulated behavior

## Resources

- [README.md](README.md) - Architecture and design
- [AGENTS.md](AGENTS.md) - Agent roles and workforce
- [API.md](API.md) - API endpoints and examples
- [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) - Quick reference
- [tests/](tests/) - Test examples
- [.github/skills/](github/skills/) - Skill documentation

---

**Questions?** Check the documentation or ask in the repository discussions.
