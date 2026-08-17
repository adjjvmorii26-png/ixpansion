# IXPANSION Agents & Workforce

Comprehensive multi-agent coordination system for IXPANSION. Implements a hierarchy of specialist agents with role-based delegation, task queuing, and mission-driven execution.

## Architecture

```
                    Mission Director
                   (top-level coordinator)
                            |
         +------------------+------------------+
         |                  |                  |
      Orchestrator       Builder            Verifier
      (cross-layer)   (implementation)    (validation)
         |                  |                  |
      +--+--+            +--+--+            +--+--+
      |     |            |     |            |     |
    ...   ...          ...   ...          ...   ...
```

## Agent Roles

### Mission Director
**Role:** Top-level coordinator for complex, multi-layer requests.

- **Tier:** Director
- **Primary Skills:** Orchestration, delegation, sequencing
- **Key Responsibilities:**
  - Frame missions with acceptance criteria and constraints
  - Inspect context and repository state
  - Delegate to specialists with clear task boundaries
  - Integrate evidence and close the loop
  - Report limitations and blockers

**When to use:** For complex, cross-module, user-facing, or security-sensitive work.

### Orchestrator
**Role:** End-to-end capability implementation across layers.

- **Tier:** Specialist
- **Primary Skills:** Cross-layer implementation, code review, sequencing
- **Affected Layers:** Agent, lattice, trust, safety, API, CLI, federation, workflows
- **Key Responsibilities:**
  - Map affected layers and dependencies
  - Implement smallest vertical slices
  - Preserve offline defaults
  - Bound autonomy with budgets, retries, thresholds
  - Run focused validation before broader checks

**When to use:** For changes spanning agent, lattice, trust, safety, API, CLI, or federation layers.

### Builder
**Role:** Python implementation and testing.

- **Tier:** Specialist
- **Primary Skills:** Code generation, refactoring, unit testing, regression testing
- **Key Responsibilities:**
  - Locate owning function/class/route
  - Read implementation and tests
  - Make smallest root-cause edits
  - Add focused unit and boundary tests
  - Preserve public APIs and offline behavior

**When to use:** For Python code changes, bug fixes, and test-backed features.

### Verifier
**Role:** Validation and quality gates.

- **Tier:** Specialist
- **Primary Skills:** Unit testing, integration testing, contract testing, security audit
- **Validation Areas:** Tests, contracts, security, dependencies, compose, release readiness
- **Key Responsibilities:**
  - Check test coverage and contract compliance
  - Audit dependencies for security and conflicts
  - Validate Docker Compose configuration
  - Verify release readiness
  - Report test results and unmet criteria

**When to use:** For test validation, contract checking, dependency auditing, or release gates.

### Runtime Operator
**Role:** Runtime testing and integration validation.

- **Tier:** Specialist
- **Primary Skills:** Runtime diagnosis, CLI testing, integration testing, health monitoring
- **Key Responsibilities:**
  - Run commands and smoke-test routes
  - Exercise CLI/dashboard interactively
  - Reproduce runtime symptoms
  - Test end-to-end workflows
  - Provide integration testing results

**When to use:** For runtime issues, CLI validation, or integration testing.

### Contract Engineer
**Role:** API, CLI, and documentation contracts.

- **Tier:** Specialist
- **Primary Skills:** API documentation, CLI contract, README sync, contract testing
- **Managed Contracts:** FastAPI routes, CLI options, dashboard, API schema, README
- **Key Responsibilities:**
  - Maintain FastAPI route definitions and OpenAPI schema
  - Manage CLI argument parsing and validation
  - Keep README aligned with code and tests
  - Update dashboard layouts and displays
  - Write contract tests for routes and CLI

**When to use:** For API route changes, CLI option additions, or documentation updates.

### Security Guardian
**Role:** Security and trust boundary validation.

- **Tier:** Specialist
- **Primary Skills:** Security audit, dependency audit, secret detection, authorization check
- **Audit Areas:** Secrets, dependencies, trust gates, audit logging, CI/security
- **Key Responsibilities:**
  - Detect and prevent secret exposure
  - Audit dependency security
  - Verify authorization and trust boundaries
  - Check human gates and approval flows
  - Review release-security concerns

**When to use:** For secrets management, dependency updates, auth changes, or security reviews.

### Cookie Eater
**Role:** Browser authentication and session management.

- **Tier:** Specialist
- **Primary Skills:** Security audit, contract testing, authentication handling, bug fixes
- **Focus Areas:** Cookies, sessions, CSRF protection, auth state, privacy
- **Key Responsibilities:**
  - Manage session and cookie contracts
  - Test CSRF protection
  - Verify authentication state handling
  - Audit privacy and data minimization
  - Write cookie-specific tests

**When to use:** For auth state changes, session handling, or cookie-related bugs.

## Capabilities

The system defines fine-grained capabilities that map to concrete skills:

### Coordination
- `ORCHESTRATION` - End-to-end capability coordination
- `DELEGATION` - Assigning work to agents
- `SEQUENCING` - Ordering dependent tasks

### Implementation
- `CODE_GENERATION` - Writing new code
- `CODE_REVIEW` - Reviewing changes
- `REFACTORING` - Improving existing code
- `BUG_FIX` - Fixing bugs

### Testing
- `UNIT_TESTING` - Writing unit tests
- `INTEGRATION_TESTING` - Integration tests
- `REGRESSION_TESTING` - Regression test coverage
- `CONTRACT_TESTING` - API/CLI contract tests

### Safety & Security
- `SECURITY_AUDIT` - Security review
- `DEPENDENCY_AUDIT` - Dependency checking
- `SECRET_DETECTION` - Finding exposed secrets
- `AUTHORIZATION_CHECK` - Auth boundary validation

### Operation
- `RUNTIME_DIAGNOSIS` - Debugging runtime issues
- `CLI_TESTING` - CLI command validation
- `CONTAINER_ORCHESTRATION` - Docker/Compose management
- `HEALTH_MONITORING` - System health checks

### Documentation
- `API_DOCUMENTATION` - API documentation
- `README_SYNC` - README and guides
- `ARCHITECTURE_DOCUMENTATION` - Architecture docs

## Task Model

Tasks represent discrete units of work that can be assigned to agents:

```python
Task(
    task_id="task-xyz123",
    description="Implement OAuth2 flow",
    required_capability=AgentCapability.CODE_GENERATION,
    status=TaskStatus.PENDING,
    priority=8,  # 1-10, higher = urgent
    dependencies=["task-abc789"],  # tasks that must complete first
)
```

### Task Lifecycle

```
PENDING -> ASSIGNED -> IN_PROGRESS -> COMPLETE
                                   \-> FAILED
```

Tasks can also be `DELEGATED` to another agent if the initial assignment can't handle it.

## Mission Model

Missions are high-level outcomes that decompose into task sequences:

```python
mission = director.frame_mission(
    description="Add OAuth2 authentication",
    acceptance_criteria=["Tests pass", "Offline-safe", "Secure"],
    affected_layers={"api", "security", "agent"},
)
```

Missions are then planned into task sequences and executed with strategies:
- `SEQUENTIAL` - Execute tasks one by one
- `PARALLEL` - Execute independent tasks concurrently
- `PRIORITIZED` - Execute highest-priority tasks first

## Delegation Rules

Agents have well-defined delegation boundaries:

```
Mission Director can delegate to:
  • Orchestrator (architecture & implementation)
  • Builder (Python code)
  • Verifier (testing & validation)
  • Operator (runtime & CLI)
  • Contract Engineer (APIs & contracts)
  • Security Guardian (security audit)
  • Cookie Eater (auth & sessions)

Orchestrator can delegate to:
  • Builder
  • Verifier
  • Operator

Builder can delegate to:
  • Verifier

(Other agents delegate only up, not sideways)
```

Invalid delegations are rejected at the workforce level.

## Usage Examples

### Quick Task Assignment

```python
from workforce import get_workforce
from agents import AgentCapability

workforce = get_workforce()

# Create a simple task
task_id = workforce.create_task(
    "Write unit tests for payment module",
    AgentCapability.UNIT_TESTING,
)

# Route to best-fit agent
agent_role = workforce.route_task_to_capable_agent(task_id)
print(f"Task assigned to: {agent_role.value}")

# Complete the task
workforce.complete_task(task_id, {"tests_written": 24, "coverage": 0.95})
```

### Mission Execution

```python
from mission_director import get_mission_director
from workforce import DelegationStrategy
from agents import AgentRole, AgentCapability

director = get_mission_director()

# Frame the mission
mission_id = director.frame_mission(
    description="Add two-factor authentication",
    acceptance_criteria=[
        "Must support TOTP",
        "Must have tests",
        "Must be offline-safe",
    ],
    affected_layers={"security", "api"},
)

# Plan the mission
plan = director.plan_mission(
    mission_id,
    task_sequence=[
        ("Design 2FA flow", AgentRole.ORCHESTRATOR, AgentCapability.ORCHESTRATION),
        ("Implement TOTP", AgentRole.BUILDER, AgentCapability.CODE_GENERATION),
        ("Write tests", AgentRole.VERIFIER, AgentCapability.INTEGRATION_TESTING),
        ("Security audit", AgentRole.SECURITY, AgentCapability.SECURITY_AUDIT),
    ],
    strategy=DelegationStrategy.SEQUENTIAL,
)

# Execute the mission
result = director.execute_mission(mission_id, auto_approve=True)

# Close and report
report = director.close_mission(mission_id)
print(f"Mission status: {report['mission_summary']}")
```

### Capability-Based Routing

```python
from agents import AgentCapability, get_agents_by_capability

# Find all agents that can do code reviews
code_reviewers = get_agents_by_capability(AgentCapability.CODE_REVIEW)
for agent_spec in code_reviewers:
    print(f"{agent_spec.name} can perform code reviews")
```

## Testing

Run workforce tests:

```bash
make workforce-test
```

Run all tests including workforce:

```bash
make verify
```

Run the demo:

```bash
python demo_workforce.py
```

## Files

- `agents.py` - Agent specifications, roles, capabilities, registry
- `workforce.py` - Task queuing, agent management, mission coordination
- `mission_director.py` - Mission framing, planning, execution, reporting
- `demo_workforce.py` - Interactive demonstration of agents & workflows
- `tests/test_workforce.py` - Comprehensive test suite

## Safety Boundaries

The workforce system enforces several safety boundaries:

1. **No secret exposure** - Agents must not include credentials in tasks or results
2. **No unauthorized delegation** - Invalid delegation chains are rejected
3. **Deterministic offline** - Default behavior must work without credentials or network
4. **Bounded autonomy** - Retries, budgets, timeouts are explicit
5. **Test coverage required** - Most agents require test coverage for changes
6. **Human approval gates** - Security-sensitive actions may require explicit approval

## Future Extensions

- **Async execution** - Non-blocking task execution with callbacks
- **Machine learning** - Learn optimal agent routing based on task history
- **Resource budgets** - Track and enforce computation/API quotas
- **Distributed workforce** - Multi-host agent coordination
- **Custom agents** - User-defined agent roles and capabilities
- **Audit trail** - Complete record of all delegations and decisions

---

**See also:** [IXPANSION Architecture](README.md#architecture-map) | [Skills Registry](.github/skills/README.md)
