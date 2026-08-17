# IXPANSION Documentation Index

Complete navigation guide for all IXPANSION documentation.

## Getting Started

**Start here if you're new to IXPANSION:**

1. **[README.md](README.md)** — Architecture overview, design principles, quick start
   - 5-layer system architecture
   - Current implementation status
   - Design principles (deterministic degradation, trust-aware scheduling, etc.)
   - Quick start: CLI and API
   - Development checks

2. **[AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)** — Agent system in 30 seconds
   - Quick overview with code example
   - 8 agents in table format
   - Common task patterns
   - Key concepts (Tasks, Missions, Delegation)
   - Try it now commands

## Core Documentation

### Architecture & Design

- **[README.md](README.md)** — Full system architecture
  - 5-layer design (Operators, Forge, Trust, Fabric, SI)
  - Current implementation status table
  - Design principles
  - Quick start and examples

### Agents & Workforce

- **[AGENTS.md](AGENTS.md)** — Complete agent reference (use this most)
  - All 8 agent roles with responsibilities
  - 17 capabilities across domains
  - Task model and lifecycle
  - Mission model and strategies
  - Delegation rules and validation
  - Usage examples (simple and complex)
  - Safety boundaries
  - Testing instructions
  - Future extensions

- **[AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)** — Quick reference
  - 30-second overview
  - Common patterns with code
  - Key concepts
  - Quick commands

- **[WORKFORCE_SUMMARY.md](WORKFORCE_SUMMARY.md)** — Implementation details
  - What was created
  - Component breakdown (agents.py, workforce.py, etc.)
  - Statistics and coverage
  - Usage examples
  - Safety & governance
  - Next steps

### API Reference

- **[API.md](API.md)** — Complete REST API documentation
  - 25+ endpoints with request/response examples
  - Agent skills (23 available)
  - Aether Lattice endpoints
  - Resource management
  - Lattice & heartbeat
  - Error responses
  - Rate limiting & timeouts
  - 3 complete usage examples
  - Environment variables

## Development & Operations

### Development

- **[DEVELOPMENT.md](DEVELOPMENT.md)** — Developer guide
  - Quick setup (Python 3.12+, venv, dependencies)
  - Project structure overview
  - Common commands
  - Development workflow (branching, committing, pushing)
  - Code standards (type hints, docstrings, naming)
  - Testing guidelines (unit, integration, coverage)
  - Debugging techniques
  - Performance optimization
  - Security checklist
  - Troubleshooting

### Deployment & CI/CD

- **[CI_CD.md](CI_CD.md)** — Deployment and release guide
  - GitHub Actions pipeline (5 stages)
  - Docker image building
  - Environment configuration (dev, prod)
  - Deployment scenarios (local, container, K8s)
  - Version management & release process
  - Monitoring & observability
  - Rollback procedures
  - Backup & disaster recovery
  - Performance tuning
  - Security hardening

### Troubleshooting

- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** — Problem solving guide
  - Setup issues (Python, dependencies, imports)
  - Test failures
  - API issues (startup, errors, performance)
  - Agent & Workforce problems
  - Docker issues
  - Database problems
  - Network issues
  - Memory & performance
  - Debugging techniques
  - When to ask for help

## Decision Trees

### "I need to..."

#### Add a new feature
1. Read [DEVELOPMENT.md](DEVELOPMENT.md) — Development workflow section
2. Check [AGENTS.md](AGENTS.md) — See if it involves agents
3. Check [API.md](API.md) — See if it involves API endpoints
4. Run `make verify` to validate

#### Fix a bug
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Find your error
2. Read relevant code file (agent.py, workforce.py, etc.)
3. Write a test case in tests/
4. Fix the code
5. Run `make verify`

#### Deploy to production
1. Read [CI_CD.md](CI_CD.md) — Full deployment guide
2. Check environment configuration section
3. Follow release checklist
4. Run security hardening steps

#### Understand the system
1. Start with [README.md](README.md) — Architecture
2. Move to [AGENTS.md](AGENTS.md) — Agent details
3. Read [API.md](API.md) — Endpoints
4. Check specific implementation files (agent.py, etc.)

#### Debug a problem
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Error category
2. Follow suggested solutions
3. Use debugging techniques section
4. Reference [DEVELOPMENT.md](DEVELOPMENT.md) — Logging and inspection

## File Structure

```
Documentation files (this directory):
├── README.md                    # Architecture & quick start
├── AGENTS.md                    # Agent reference (primary)
├── AGENTS_QUICK_START.md        # Quick reference
├── WORKFORCE_SUMMARY.md         # Implementation details
├── API.md                       # REST API reference
├── DEVELOPMENT.md               # Developer guide
├── CI_CD.md                     # Deployment guide
├── TROUBLESHOOTING.md           # Problem solving
├── DOCUMENTATION.md             # This file

Source code (alphabetical):
├── agents.py                    # Agent specifications (391 lines)
├── agent.py                     # Core Agent class (491 lines)
├── workforce.py                 # Multi-agent coordination (380 lines)
├── mission_director.py          # Mission orchestration (317 lines)
├── aether_lattice.py            # Foundation layer
├── lattice_stack.py             # Machine lattice
├── federated_stack.py           # Federation & PSO
├── security_controls.py         # Trust & audit
├── resource_*.py                # Resource management
├── api/main.py                  # FastAPI endpoints (403 lines)
├── run_agent.py                 # CLI entry point
├── swarm_runtime.py             # Swarm coordinator

Tests:
├── tests/__init__.py
├── tests/test_*.py              # 10 test files
└── tests/test_workforce.py      # Agent/workforce tests (395 lines)

Configuration:
├── Makefile                     # Build/test targets
├── requirements.txt             # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .editorconfig                # Editor settings
├── .gitattributes               # Git configuration
├── Dockerfile                   # Container image
└── docker-compose.yml           # Local swarm demo

GitHub:
├── .github/agents/              # Agent definitions (8 files)
├── .github/skills/              # Skill documentation (22 folders)
└── .github/workflows/           # CI/CD (ci.yml)
```

## Statistics

### Documentation
- **Total docs:** 9 comprehensive markdown files
- **Total lines:** ~4,500 lines of documentation
- **Topics:** 25+ major sections

### Code
- **Modules:** 25+ Python files
- **Core workforce modules:** 3 (agents.py, workforce.py, mission_director.py)
- **Lines of code:** ~3,800 (core modules)
- **Test coverage:** 40+ test cases
- **Docstrings:** 100% on public APIs

### Components
- **Agent roles:** 8 types
- **Capabilities:** 17 fine-grained skills
- **API endpoints:** 25+ routes
- **Agent skills:** 23 built-in skills

## Search by Topic

### Agent System
- [AGENTS.md](AGENTS.md) — Complete reference
- [AGENTS_QUICK_START.md](AGENTS_QUICK_START.md) — Quick guide
- [WORKFORCE_SUMMARY.md](WORKFORCE_SUMMARY.md) — Implementation
- [agents.py](agents.py) — Source code
- [workforce.py](workforce.py) — Source code
- [mission_director.py](mission_director.py) — Source code

### API & Integration
- [API.md](API.md) — Endpoint reference
- [api/main.py](api/main.py) — Implementation
- [DEVELOPMENT.md](DEVELOPMENT.md) — Development guide
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Common issues

### Deployment & Operations
- [CI_CD.md](CI_CD.md) — Deployment guide
- [Dockerfile](Dockerfile) — Container image
- [docker-compose.yml](docker-compose.yml) — Local swarm
- [DEVELOPMENT.md](DEVELOPMENT.md) — Commands

### Testing
- [DEVELOPMENT.md](DEVELOPMENT.md) — Testing guidelines
- [tests/test_workforce.py](tests/test_workforce.py) — Example tests
- [Makefile](Makefile) — Test commands
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Test issues

### Troubleshooting
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Problem solving
- [DEVELOPMENT.md](DEVELOPMENT.md) — Debugging section
- [CI_CD.md](CI_CD.md) — Deployment issues

## Learning Path

### Beginner (Understand the system)
1. **[README.md](README.md)** — Architecture (20 min)
2. **[AGENTS_QUICK_START.md](AGENTS_QUICK_START.md)** — Quick overview (5 min)
3. **Run demo:** `python demo_workforce.py` (5 min)
4. **[AGENTS.md](AGENTS.md)** Roles section (15 min)

### Intermediate (Build with IXPANSION)
1. **[API.md](API.md)** — Endpoints (30 min)
2. **[AGENTS.md](AGENTS.md)** — Usage examples (15 min)
3. **[DEVELOPMENT.md](DEVELOPMENT.md)** — Setup (15 min)
4. Write a simple task or mission

### Advanced (Contribute to IXPANSION)
1. **[DEVELOPMENT.md](DEVELOPMENT.md)** — Full guide (45 min)
2. **[AGENTS.md](AGENTS.md)** — Deep dive (30 min)
3. **[CI_CD.md](CI_CD.md)** — Deployment (30 min)
4. Implement a new feature with tests

### Expert (Master all aspects)
1. Read all documentation in order
2. Read all source files top-to-bottom
3. Run full test suite and demos
4. Deploy to multiple environments
5. Contribute new agent roles or capabilities

## Quick Reference

### Most Used Commands
```bash
make verify                 # Run all tests
make workforce-test         # Test agents only
make compile               # Check syntax
python demo_workforce.py   # See agents in action
python -m uvicorn api.main:app --reload  # Run API
```

### Most Used Documentation
- [AGENTS.md](AGENTS.md) — Agent capabilities and usage
- [API.md](API.md) — API endpoints
- [DEVELOPMENT.md](DEVELOPMENT.md) — Development workflow
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) — Problem solving

## Contributing

When contributing, update:
1. **Code files** — Add docstrings, type hints
2. **Relevant docs** — Update if behavior changes
3. **Tests** — Add test for new behavior
4. **This index** — If adding new doc files

See [.github/copilot-instructions.md](.github/copilot-instructions.md) for workflow.

## Version Information

- **Python:** 3.12+
- **FastAPI:** 0.115.0
- **Uvicorn:** 0.32.0
- **Current version:** 1.2.0-rc3

## Getting Help

1. **Question about feature?** → Check [AGENTS.md](AGENTS.md) or [API.md](API.md)
2. **Problem with setup?** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
3. **How do I develop?** → Read [DEVELOPMENT.md](DEVELOPMENT.md)
4. **Deploy question?** → Check [CI_CD.md](CI_CD.md)
5. **Still stuck?** → Open issue with details from [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Note:** This documentation is comprehensive and always up-to-date with the code. If you find something incorrect or unclear, open an issue or improve it directly!
