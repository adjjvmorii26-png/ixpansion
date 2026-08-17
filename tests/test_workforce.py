"""Tests for IXPANSION agents, workforce coordination, and mission direction."""

import unittest

from agents import (
    AgentCapability,
    AgentRole,
    AgentTier,
    can_chain_delegation,
    get_agent_spec,
    get_agents_by_capability,
    get_agents_by_tier,
)
from mission_director import MissionDirector, get_mission_director, reset_mission_director
from workforce import (
    DelegationStrategy,
    Task,
    TaskStatus,
    Workforce,
    get_workforce,
    reset_workforce,
)


class TestAgentSpecifications(unittest.TestCase):
    """Test agent role specifications and capabilities."""

    def test_mission_director_exists(self):
        """Mission Director should be defined."""
        spec = get_agent_spec(AgentRole.MISSION_DIRECTOR)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.role, AgentRole.MISSION_DIRECTOR)
        self.assertEqual(spec.tier, AgentTier.DIRECTOR)

    def test_specialist_agents_exist(self):
        """All specialist agents should be defined."""
        specialist_roles = {
            AgentRole.ORCHESTRATOR,
            AgentRole.BUILDER,
            AgentRole.VERIFIER,
            AgentRole.OPERATOR,
            AgentRole.CONTRACT_ENGINEER,
            AgentRole.SECURITY,
            AgentRole.COOKIE_HANDLER,
        }
        for role in specialist_roles:
            spec = get_agent_spec(role)
            self.assertIsNotNone(spec)
            self.assertEqual(spec.tier, AgentTier.SPECIALIST)

    def test_agent_has_capabilities(self):
        """Agents should have relevant capabilities."""
        spec = get_agent_spec(AgentRole.BUILDER)
        self.assertIsNotNone(spec)
        self.assertTrue(spec.has_capability(AgentCapability.CODE_GENERATION))
        self.assertTrue(spec.has_capability(AgentCapability.UNIT_TESTING))

    def test_agents_by_capability(self):
        """Should find agents with specific capability."""
        agents = get_agents_by_capability(AgentCapability.CODE_GENERATION)
        self.assertGreater(len(agents), 0)
        # Should include Builder and Contract Engineer
        roles = {a.role for a in agents}
        self.assertIn(AgentRole.BUILDER, roles)
        self.assertIn(AgentRole.CONTRACT_ENGINEER, roles)

    def test_agents_by_tier(self):
        """Should find agents by coordination tier."""
        directors = get_agents_by_tier(AgentTier.DIRECTOR)
        self.assertEqual(len(directors), 1)
        self.assertEqual(directors[0].role, AgentRole.MISSION_DIRECTOR)

        specialists = get_agents_by_tier(AgentTier.SPECIALIST)
        self.assertGreater(len(specialists), 5)

    def test_delegation_chain(self):
        """Should support valid delegation chains."""
        # Mission Director can delegate to Orchestrator
        self.assertTrue(
            can_chain_delegation(
                AgentRole.MISSION_DIRECTOR, AgentRole.ORCHESTRATOR
            )
        )

        # Orchestrator can delegate to Builder
        self.assertTrue(
            can_chain_delegation(AgentRole.ORCHESTRATOR, AgentRole.BUILDER)
        )

        # Builder cannot delegate to Orchestrator (invalid)
        self.assertFalse(
            can_chain_delegation(AgentRole.BUILDER, AgentRole.ORCHESTRATOR)
        )


class TestWorkforce(unittest.TestCase):
    """Test workforce coordination and task management."""

    def setUp(self):
        """Reset workforce before each test."""
        reset_workforce()

    def test_workforce_initialization(self):
        """Workforce should initialize with default agents."""
        workforce = get_workforce()
        self.assertGreater(len(workforce.agents), 0)

        # Should have at least one instance per role
        for role in AgentRole:
            self.assertIn(role, workforce.agents)
            self.assertGreater(len(workforce.agents[role]), 0)

    def test_create_task(self):
        """Should create tasks with dependencies."""
        workforce = get_workforce()
        task_id = workforce.create_task(
            "Test task",
            AgentCapability.CODE_GENERATION,
            priority=8,
        )
        self.assertIsNotNone(task_id)

        task = workforce.tasks.get(task_id)
        self.assertEqual(task.status, TaskStatus.PENDING)
        self.assertEqual(task.priority, 8)

    def test_task_with_dependencies(self):
        """Tasks should track dependencies."""
        workforce = get_workforce()
        task1_id = workforce.create_task(
            "Task 1", AgentCapability.CODE_GENERATION
        )
        task2_id = workforce.create_task(
            "Task 2",
            AgentCapability.UNIT_TESTING,
            dependencies=[task1_id],
        )

        task2 = workforce.tasks.get(task2_id)
        self.assertEqual(task2.dependencies, [task1_id])

    def test_task_ready_check(self):
        """Should check if task dependencies are satisfied."""
        workforce = get_workforce()
        task1_id = workforce.create_task(
            "Task 1", AgentCapability.CODE_GENERATION
        )
        task2_id = workforce.create_task(
            "Task 2",
            AgentCapability.UNIT_TESTING,
            dependencies=[task1_id],
        )

        task2 = workforce.tasks.get(task2_id)

        # Should not be ready (task1 not complete)
        self.assertFalse(task2.is_ready(workforce.completed_task_ids))

        # Complete task1
        workforce.complete_task(task1_id, {"status": "done"})

        # Now should be ready
        self.assertTrue(task2.is_ready(workforce.completed_task_ids))

    def test_assign_task_to_capable_agent(self):
        """Should assign task to agent with capability."""
        workforce = get_workforce()
        task_id = workforce.create_task(
            "Write code",
            AgentCapability.CODE_GENERATION,
        )

        # Assign to capable agent
        success = workforce.assign_task(task_id, AgentRole.BUILDER)
        self.assertTrue(success)

        task = workforce.tasks.get(task_id)
        self.assertEqual(task.assigned_agent, AgentRole.BUILDER)
        self.assertEqual(task.status, TaskStatus.ASSIGNED)

    def test_route_task_to_best_fit(self):
        """Should route task to best-fit agent by workload."""
        workforce = get_workforce()
        task_id = workforce.create_task(
            "Implement feature",
            AgentCapability.CODE_GENERATION,
        )

        # Route to best fit
        agent_role = workforce.route_task_to_capable_agent(task_id)
        self.assertIsNotNone(agent_role)
        self.assertIn(agent_role, {AgentRole.BUILDER, AgentRole.CONTRACT_ENGINEER})

    def test_task_completion(self):
        """Should mark tasks complete with results."""
        workforce = get_workforce()
        task_id = workforce.create_task(
            "Test task",
            AgentCapability.CODE_GENERATION,
        )

        result = {"status": "success", "output": "task completed"}
        workforce.complete_task(task_id, result)

        task = workforce.tasks.get(task_id)
        self.assertEqual(task.status, TaskStatus.COMPLETE)
        self.assertEqual(task.result, result)
        self.assertIn(task_id, workforce.completed_task_ids)

    def test_task_failure(self):
        """Should mark tasks as failed with error."""
        workforce = get_workforce()
        task_id = workforce.create_task(
            "Failing task",
            AgentCapability.CODE_GENERATION,
        )

        error_msg = "Agent timeout"
        workforce.fail_task(task_id, error_msg)

        task = workforce.tasks.get(task_id)
        self.assertEqual(task.status, TaskStatus.FAILED)
        self.assertEqual(task.error, error_msg)

    def test_delegation_chain(self):
        """Should delegate tasks between agents."""
        workforce = get_workforce()
        task_id = workforce.create_task(
            "Complex task",
            AgentCapability.CODE_GENERATION,
        )

        # Delegate from Builder to Verifier
        success = workforce.delegate_task(
            task_id,
            AgentRole.BUILDER,
            AgentRole.VERIFIER,
        )
        # Verifier doesn't have CODE_GENERATION, so this should fail
        self.assertFalse(success)

        # But Orchestrator can delegate to Builder
        task2_id = workforce.create_task(
            "Orchestrate",
            AgentCapability.CODE_GENERATION,
        )
        success = workforce.delegate_task(
            task2_id,
            AgentRole.ORCHESTRATOR,
            AgentRole.BUILDER,
        )
        self.assertTrue(success)

    def test_mission_creation(self):
        """Should create mission contexts."""
        workforce = get_workforce()
        mission_id = workforce.create_mission(
            "Implement feature X",
            ["Must have tests", "Must be offline-safe"],
            {"agent", "lattice"},
        )
        self.assertIsNotNone(mission_id)

        mission = workforce.missions.get(mission_id)
        self.assertEqual(mission.description, "Implement feature X")

    def test_workforce_status_report(self):
        """Should generate comprehensive status report."""
        workforce = get_workforce()

        # Create some tasks
        for i in range(5):
            workforce.create_task(
                f"Task {i}",
                AgentCapability.CODE_GENERATION,
            )

        status = workforce.report_workforce_status()
        self.assertEqual(status["total_tasks"], 5)
        self.assertEqual(status["pending_tasks"], 5)
        self.assertGreater(status["total_agents"], 0)

    def test_get_ready_tasks(self):
        """Should identify tasks ready for execution."""
        workforce = get_workforce()

        task1_id = workforce.create_task(
            "Task 1",
            AgentCapability.CODE_GENERATION,
        )
        task2_id = workforce.create_task(
            "Task 2",
            AgentCapability.UNIT_TESTING,
            dependencies=[task1_id],
        )

        # Only task1 should be ready
        ready = workforce.get_ready_tasks()
        self.assertEqual(len(ready), 1)
        self.assertEqual(ready[0].task_id, task1_id)

        # Complete task1
        workforce.complete_task(task1_id, {})

        # Now task2 should be ready
        ready = workforce.get_ready_tasks()
        task_ids = [t.task_id for t in ready]
        self.assertIn(task2_id, task_ids)


class TestMissionDirector(unittest.TestCase):
    """Test Mission Director coordination."""

    def setUp(self):
        """Reset director and workforce before each test."""
        reset_mission_director()
        reset_workforce()

    def test_frame_mission(self):
        """Should frame missions with criteria."""
        director = get_mission_director()
        mission_id = director.frame_mission(
            "Implement authentication",
            ["Must be offline-safe", "Must pass tests"],
            {"security", "api"},
        )
        self.assertIsNotNone(mission_id)

    def test_plan_mission(self):
        """Should create mission execution plans."""
        director = get_mission_director()
        mission_id = director.frame_mission(
            "Build feature",
            ["Tests pass", "Secure"],
            {"agent"},
        )

        plan = director.plan_mission(
            mission_id,
            [
                ("Implement", AgentRole.BUILDER, AgentCapability.CODE_GENERATION),
                ("Test", AgentRole.VERIFIER, AgentCapability.UNIT_TESTING),
            ],
        )
        self.assertEqual(len(plan.task_sequence), 2)

    def test_execute_mission_sequential(self):
        """Should execute missions sequentially."""
        director = get_mission_director()
        mission_id = director.frame_mission(
            "Build feature",
            ["Tests pass"],
            {"agent"},
        )

        plan = director.plan_mission(
            mission_id,
            [
                ("Implement", AgentRole.BUILDER, AgentCapability.CODE_GENERATION),
                ("Test", AgentRole.VERIFIER, AgentCapability.UNIT_TESTING),
            ],
            strategy=DelegationStrategy.SEQUENTIAL,
        )

        result = director.execute_mission(mission_id, auto_approve=True)
        self.assertEqual(result["strategy"], "sequential")
        self.assertGreater(len(result["executed_tasks"]), 0)

    def test_close_mission(self):
        """Should close missions and report results."""
        director = get_mission_director()
        mission_id = director.frame_mission(
            "Quick task",
            ["Done"],
            {"agent"},
        )

        plan = director.plan_mission(
            mission_id,
            [
                ("Do work", AgentRole.BUILDER, AgentCapability.CODE_GENERATION),
            ],
        )

        director.execute_mission(mission_id, auto_approve=True)

        # Close and get report
        report = director.close_mission(mission_id)
        self.assertIn("mission_summary", report)
        self.assertIn("evidence", report)
        self.assertIn("workforce_state", report)


if __name__ == "__main__":
    unittest.main()
