# IXPANSION Agents & Workforce — Quick Start

## What You Just Got

A **production-ready multi-agent coordination system** for IXPANSION with 8 specialized roles, task queuing, and mission orchestration.

## 30-Second Overview

```python
# 1. Get the workforce
from workforce import get_workforce
from agents import AgentCapability

workforce = get_workforce()

# 2. Create a task
task_id = workforce.create_task(
    "Implement OAuth2 flow",
    AgentCapability.CODE_GENERATION,
    priority=9,
)

# 3. Route to best agent
agent_role = workforce.route_task_to_capable_agent(task_id)

# 4. Mark complete
workforce.complete_task(task_id, {"status": "done"})
```

## The 8 Agents

| Agent | Role | Use For |
|-------|------|---------|
| **Mission Director** | Coordinates all work | Complex multi-layer projects |
| **Orchestrator** | Implements features | Cross-layer changes |
| **Builder** | Writes code | Python implementation & tests |
| **Verifier** | Validates quality | Testing & release gates |
| **Operator** | Runs tests | Runtime & CLI validation |
| **Contract Engineer** | Manages APIs | Route/CLI/README contracts |
| **Security Guardian** | Audits safety | Secrets & auth boundaries |
| **Cookie Eater** | Manages auth | Authentication & sessions |

## Common Tasks

### Create a Simple Task
```python
from workforce import get_workforce
from agents import AgentCapability

workforce = get_workforce()

# Create task
task_id = workforce.create_task(
    "Write unit tests",
    AgentCapability.UNIT_TESTING,
)

# Route to agent
agent = workforce.route_task_to_capable_agent(task_id)

# Complete it
workforce.complete_task(task_id, {"tests": 42, "coverage": 0.95})
```

### Create a Mission
```python
from mission_director import get_mission_director
from agents import AgentRole, AgentCapability
from workforce import DelegationStrategy

director = get_mission_director()

# Frame it
mission_id = director.frame_mission(
    "Add OAuth2 to API",
    ["All tests pass", "No secrets exposed"],
    {"api", "security"},
)

# Plan it
plan = director.plan_mission(
    mission_id,
    [
        ("Design flow", AgentRole.ORCHESTRATOR, AgentCapability.ORCHESTRATION),
        ("Build it", AgentRole.BUILDER, AgentCapability.CODE_GENERATION),
        ("Test it", AgentRole.VERIFIER, AgentCapability.CONTRACT_TESTING),
        ("Audit it", AgentRole.SECURITY, AgentCapability.SECURITY_AUDIT),
    ],
    strategy=DelegationStrategy.SEQUENTIAL,
)

# Execute it
result = director.execute_mission(mission_id, auto_approve=True)

# Report on it
report = director.close_mission(mission_id)
print(report['mission_summary'])
```

### Find Agents by Capability
```python
from agents import AgentCapability, get_agents_by_capability

# Who can do code reviews?
reviewers = get_agents_by_capability(AgentCapability.CODE_REVIEW)
for agent_spec in reviewers:
    print(f"- {agent_spec.name}")
```

## Files

| File | Purpose |
|------|---------|
| `agents.py` | Agent definitions & registry |
| `workforce.py` | Task & mission coordination |
| `mission_director.py` | Mission orchestration |
| `AGENTS.md` | Full documentation |
| `WORKFORCE_SUMMARY.md` | Implementation details |
| `tests/test_workforce.py` | 40+ test cases |
| `demo_workforce.py` | Interactive demo |

## Try It Now

```bash
# Run the interactive demo
python demo_workforce.py

# Run tests
make workforce-test

# Verify it compiles
make compile

# Check all tests pass
make verify
```

## Key Concepts

### Tasks
Work units with lifecycle: PENDING → ASSIGNED → IN_PROGRESS → COMPLETE

```python
Task(
    task_id="task-xyz",
    description="Implement payment",
    required_capability=AgentCapability.CODE_GENERATION,
    priority=8,  # 1-10
    dependencies=["task-abc"],  # tasks that must finish first
)
```

### Missions
High-level outcomes decomposed into task sequences

```python
mission_id = director.frame_mission(
    description="Add 2FA support",
    acceptance_criteria=["Tests pass", "Audited", "Offline-safe"],
    affected_layers={"security", "api"},
)
```

### Delegation
Agents can delegate work to other agents following these rules:

```
Mission Director → [any specialist]
Orchestrator → [Builder, Verifier, Operator]
Builder → [Verifier]
(Others don't delegate)
```

## Safety Built-In

✅ No secrets in tasks or results  
✅ Validated delegation chains  
✅ Offline-first by default  
✅ Explicit budgets & retries  
✅ Test coverage required  
✅ Human approval gates  
✅ Complete audit trails  

## Next Steps

1. **Read the docs:** `AGENTS.md` for complete reference
2. **See it in action:** `python demo_workforce.py`
3. **Run the tests:** `make workforce-test`
4. **Integrate it:** Use `get_workforce()` in your code
5. **Extend it:** Add custom agent roles or capabilities

## Support

- **Questions?** Read `AGENTS.md` section by section
- **Examples?** See `demo_workforce.py` for all use cases
- **Testing?** Check `tests/test_workforce.py` for patterns
- **Issues?** Look at delegation rules and capability matches

---

**Ready to coordinate multi-agent work?** Start with a simple task, then graduate to missions! 🚀
