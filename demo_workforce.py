#!/usr/bin/env python3
"""Demo: IXPANSION Workforce in action.

Shows agent initialization, task creation, delegation, and mission execution.
Run with: python demo_workforce.py
"""

import json

from agents import AgentCapability, AgentRole, get_agent_spec, get_agents_by_capability
from mission_director import DelegationStrategy, get_mission_director
from workforce import get_workforce, reset_workforce


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def demo_agent_registry() -> None:
    """Demo: Agent registry and specifications."""
    print_section("Agent Registry")

    # Show all agent roles
    print("IXPANSION has 8 agent roles:\n")
    for role in AgentRole:
        spec = get_agent_spec(role)
        if spec:
            print(f"  • {spec.name:25} | Tier: {spec.tier.value:12}")
            print(f"    {spec.description[:60]}...")
            print()


def demo_workforce_initialization() -> None:
    """Demo: Workforce initialization."""
    print_section("Workforce Initialization")

    reset_workforce()
    workforce = get_workforce()

    print(f"Created workforce with:")
    print(f"  • {sum(len(agents) for agents in workforce.agents.values())} total agent instances")
    print(f"  • 1 instance per agent role")
    print()

    print("Agent instances by role:")
    for role, agents in workforce.agents.items():
        print(f"  • {role.value:25} -> {agents[0].spec.name:25}")


def demo_capability_routing() -> None:
    """Demo: Finding agents by capability."""
    print_section("Capability-Based Routing")

    capabilities = [
        AgentCapability.CODE_GENERATION,
        AgentCapability.SECURITY_AUDIT,
        AgentCapability.UNIT_TESTING,
    ]

    for capability in capabilities:
        agents = get_agents_by_capability(capability)
        agent_names = [a.name for a in agents]
        print(f"Agents with {capability.value}:")
        for name in agent_names:
            print(f"  • {name}")
        print()


def demo_task_execution() -> None:
    """Demo: Task creation and execution."""
    print_section("Task Creation & Execution")

    reset_workforce()
    workforce = get_workforce()

    # Create a simple task
    task_id = workforce.create_task(
        "Implement user authentication",
        AgentCapability.CODE_GENERATION,
        priority=8,
    )
    print(f"Created task: {task_id}")
    task = workforce.tasks[task_id]
    print(f"  Description: {task.description}")
    print(f"  Priority: {task.priority}/10")
    print(f"  Status: {task.status.value}")
    print()

    # Route to capable agent
    agent_role = workforce.route_task_to_capable_agent(task_id)
    print(f"Routed to agent: {agent_role.value}")
    print(f"  Task assigned to: {task.assigned_instance_id}")
    print()

    # Complete the task
    result = {"status": "success", "files_modified": ["auth.py"], "tests_passed": 42}
    workforce.complete_task(task_id, result)
    print(f"Task completed with result:")
    print(f"  {json.dumps(result, indent=4)}")


def demo_task_dependencies() -> None:
    """Demo: Task dependencies and sequencing."""
    print_section("Task Dependencies & Sequencing")

    reset_workforce()
    workforce = get_workforce()

    # Create dependent tasks
    implement_id = workforce.create_task(
        "Implement feature",
        AgentCapability.CODE_GENERATION,
    )
    test_id = workforce.create_task(
        "Write unit tests",
        AgentCapability.UNIT_TESTING,
        dependencies=[implement_id],
    )
    verify_id = workforce.create_task(
        "Verify security",
        AgentCapability.SECURITY_AUDIT,
        dependencies=[test_id],
    )

    print("Created task sequence:")
    print(f"  1. Implement feature ({implement_id[:12]}...)")
    print(f"  2. Write tests ({test_id[:12]}...) [depends on 1]")
    print(f"  3. Verify security ({verify_id[:12]}...) [depends on 2]")
    print()

    # Check readiness
    ready = workforce.get_ready_tasks()
    print(f"Initially, {len(ready)} task(s) ready for execution:")
    for task in ready:
        print(f"  • {task.description}")
    print()

    # Complete first task
    workforce.complete_task(implement_id, {"status": "done"})
    ready = workforce.get_ready_tasks()
    print(f"After completing step 1, {len(ready)} task(s) ready:")
    for task in ready:
        print(f"  • {task.description}")


def demo_mission_execution() -> None:
    """Demo: Mission framing and execution."""
    print_section("Mission Execution")

    reset_workforce()
    director = get_mission_director()

    # Frame a mission
    mission_id = director.frame_mission(
        description="Add two-factor authentication to the API",
        acceptance_criteria=[
            "Must support TOTP and backup codes",
            "Must have integration tests",
            "Must be offline-safe by default",
        ],
        affected_layers={"api", "security", "agent"},
    )
    print(f"Framed mission: {mission_id}")
    print(f"  Goal: Add two-factor authentication")
    print(f"  Affected layers: api, security, agent")
    print()

    # Plan the mission
    plan = director.plan_mission(
        mission_id,
        task_sequence=[
            (
                "Design 2FA architecture",
                AgentRole.ORCHESTRATOR,
                AgentCapability.ORCHESTRATION,
            ),
            (
                "Implement TOTP handler",
                AgentRole.BUILDER,
                AgentCapability.CODE_GENERATION,
            ),
            (
                "Write integration tests",
                AgentRole.VERIFIER,
                AgentCapability.INTEGRATION_TESTING,
            ),
            (
                "Security audit",
                AgentRole.SECURITY,
                AgentCapability.SECURITY_AUDIT,
            ),
        ],
        strategy=DelegationStrategy.SEQUENTIAL,
    )
    print(f"Created execution plan with {len(plan.task_sequence)} steps:")
    for i, (step, role, _) in enumerate(plan.task_sequence, 1):
        print(f"  {i}. {step} ({role.value})")
    print()

    # Execute the mission
    exec_result = director.execute_mission(mission_id, auto_approve=True)
    print(f"Executed mission:")
    print(f"  Strategy: {exec_result['strategy']}")
    print(f"  Executed tasks: {len(exec_result['executed_tasks'])}")
    print()

    # Close and report
    report = director.close_mission(mission_id)
    status = report["mission_summary"]
    print(f"Mission Summary:")
    print(f"  Total tasks: {status['total_tasks']}")
    print(f"  Completed: {status['completed_tasks']}")
    print(f"  Failed: {status['failed_tasks']}")


def demo_workforce_status() -> None:
    """Demo: Workforce status reporting."""
    print_section("Workforce Status Report")

    workforce = get_workforce()
    status = workforce.report_workforce_status()

    print(json.dumps(status, indent=2))


def main() -> None:
    """Run all demos."""
    print("\n" + "=" * 70)
    print("  IXPANSION AGENTS & WORKFORCE DEMO")
    print("  Comprehensive multi-agent coordination system")
    print("=" * 70)

    demo_agent_registry()
    demo_workforce_initialization()
    demo_capability_routing()
    demo_task_execution()
    demo_task_dependencies()
    demo_mission_execution()
    demo_workforce_status()

    print("\n" + "=" * 70)
    print("  Demo complete!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
