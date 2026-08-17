#!/usr/bin/env python3
"""IXPANSION Mission Director: Top-level mission coordination and orchestration.

Implements the directing protocol for framing missions, inspecting context,
delegating to specialists, and closing the loop with integrated evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set

from agents import AgentCapability, AgentRole, get_agent_spec
from workforce import (
    DelegationStrategy,
    Task,
    TaskStatus,
    Workforce,
    get_workforce,
)


@dataclass
class MissionPlan:
    """Structured plan for mission execution."""

    mission_id: str
    description: str
    acceptance_criteria: List[str]
    affected_layers: Set[str]
    task_sequence: List[tuple[str, AgentRole, AgentCapability]]  # (step, agent, capability)
    dependencies: Dict[str, List[str]]  # task_id -> [dependency_ids]
    delegation_strategy: DelegationStrategy = DelegationStrategy.SEQUENTIAL
    estimated_duration_seconds: int = 300
    requires_human_approval: bool = False
    has_external_effects: bool = False


class MissionDirector:
    """Top-level coordinator for IXPANSION missions.

    Owns the outcome and keeps work coordinated. Frames missions, inspects
    context, delegates to specialists, and integrates results into one
    coherent change.
    """

    def __init__(self, workforce: Optional[Workforce] = None):
        """Initialize the Mission Director."""
        self.workforce = workforce or get_workforce()
        self.missions: Dict[str, MissionPlan] = {}

    def frame_mission(
        self,
        description: str,
        acceptance_criteria: List[str],
        affected_layers: Set[str],
        constraints: Optional[List[str]] = None,
    ) -> str:
        """Frame a mission with concrete outcome and acceptance criteria."""
        mission_id = self.workforce.create_mission(
            description=description,
            acceptance_criteria=acceptance_criteria,
            affected_layers=affected_layers,
            constraints=constraints or [],
        )
        return mission_id

    def plan_mission(
        self,
        mission_id: str,
        task_sequence: List[tuple[str, AgentRole, AgentCapability]],
        dependencies: Optional[Dict[str, List[str]]] = None,
        strategy: DelegationStrategy = DelegationStrategy.SEQUENTIAL,
    ) -> MissionPlan:
        """Create a detailed execution plan for a mission."""
        mission = self.workforce.missions.get(mission_id)
        if not mission:
            raise ValueError(f"Mission {mission_id} not found")

        plan = MissionPlan(
            mission_id=mission_id,
            description=mission.description,
            acceptance_criteria=mission.acceptance_criteria,
            affected_layers=mission.affected_layers,
            task_sequence=task_sequence,
            dependencies=dependencies or {},
            delegation_strategy=strategy,
            requires_human_approval=any(
                get_agent_spec(role).requires_human_approval
                for _, role, _ in task_sequence
            ),
            has_external_effects=mission.requires_external_effect,
        )
        self.missions[mission_id] = plan
        return plan

    def execute_mission(
        self, mission_id: str, auto_approve: bool = False
    ) -> Dict[str, Any]:
        """Execute a planned mission."""
        plan = self.missions.get(mission_id)
        if not plan:
            raise ValueError(f"No plan found for mission {mission_id}")

        # Check if human approval is needed
        if plan.requires_human_approval and not auto_approve:
            return {
                "status": "pending_approval",
                "mission_id": mission_id,
                "requires_human_approval": True,
                "message": "This mission requires human approval before execution.",
            }

        # Create tasks from plan
        task_ids = []
        task_id_map = {}

        for step_name, agent_role, capability in plan.task_sequence:
            task_id = self.workforce.create_task(
                description=step_name,
                required_capability=capability,
                mission_id=mission_id,
                context={"mission_id": mission_id, "step_name": step_name},
            )
            task_ids.append(task_id)
            task_id_map[step_name] = task_id

        # Update dependencies
        for task_id, deps in plan.dependencies.items():
            resolved_deps = [task_id_map.get(d) for d in deps if d in task_id_map]
            task = self.workforce.tasks.get(task_id)
            if task:
                task.dependencies = resolved_deps

        # Execute based on strategy
        if plan.delegation_strategy == DelegationStrategy.SEQUENTIAL:
            return self._execute_sequential(mission_id, task_ids)
        elif plan.delegation_strategy == DelegationStrategy.PARALLEL:
            return self._execute_parallel(mission_id, task_ids)
        else:  # PRIORITIZED
            return self._execute_prioritized(mission_id, task_ids)

    def delegate_to_specialist(
        self, task_id: str, from_role: AgentRole, to_role: AgentRole
    ) -> bool:
        """Delegate a task to a specialist agent."""
        return self.workforce.delegate_task(task_id, from_role, to_role)

    def integrate_evidence(self, mission_id: str) -> Dict[str, Any]:
        """Integrate evidence from completed tasks."""
        plan = self.missions.get(mission_id)
        if not plan:
            return {}

        mission_tasks = [
            t
            for t in self.workforce.tasks.values()
            if mission_id in (t.context.get("mission_id"),)
        ]

        evidence = {
            "mission_id": mission_id,
            "description": plan.description,
            "acceptance_criteria": plan.acceptance_criteria,
            "task_results": [],
            "failures": [],
            "delegations": [],
            "success": True,
        }

        for task in sorted(mission_tasks, key=lambda t: t.created_at):
            if task.status == TaskStatus.COMPLETE:
                evidence["task_results"].append(
                    {
                        "task_id": task.task_id,
                        "description": task.description,
                        "assigned_agent": task.assigned_agent.value
                        if task.assigned_agent
                        else None,
                        "result": task.result,
                    }
                )
            elif task.status == TaskStatus.FAILED:
                evidence["failures"].append(
                    {
                        "task_id": task.task_id,
                        "description": task.description,
                        "error": task.error,
                    }
                )
                evidence["success"] = False

        # Include delegation chain
        for task_id, role in self.workforce.delegation_chain:
            evidence["delegations"].append(
                {
                    "task_id": task_id,
                    "delegated_to": role.value,
                }
            )

        return evidence

    def close_mission(self, mission_id: str) -> Dict[str, Any]:
        """Close a mission and report results."""
        evidence = self.integrate_evidence(mission_id)
        status = self.workforce.get_mission_status(mission_id)

        return {
            "mission_summary": status,
            "evidence": evidence,
            "workforce_state": self.workforce.report_workforce_status(),
        }

    def _execute_sequential(
        self, mission_id: str, task_ids: List[str]
    ) -> Dict[str, Any]:
        """Execute tasks sequentially."""
        results = {
            "mission_id": mission_id,
            "strategy": "sequential",
            "executed_tasks": [],
            "pending_tasks": task_ids,
        }

        for task_id in task_ids:
            task = self.workforce.tasks.get(task_id)
            if not task:
                continue

            # Route to capable agent
            agent_role = self.workforce.route_task_to_capable_agent(task_id)
            if agent_role:
                task.status = TaskStatus.IN_PROGRESS
                # Simulate task execution
                self.workforce.complete_task(
                    task_id,
                    {
                        "agent": agent_role.value,
                        "status": "executed",
                        "description": task.description,
                    },
                )
                results["executed_tasks"].append(task_id)
            else:
                self.workforce.fail_task(task_id, f"No capable agent found")
                results["executed_tasks"].append(task_id)

        results["pending_tasks"] = []
        return results

    def _execute_parallel(
        self, mission_id: str, task_ids: List[str]
    ) -> Dict[str, Any]:
        """Execute tasks in parallel where dependencies allow."""
        results = {
            "mission_id": mission_id,
            "strategy": "parallel",
            "executed_tasks": [],
            "pending_tasks": task_ids,
        }

        # Route all ready tasks
        for task_id in self.workforce.get_ready_tasks():
            if task_id in task_ids:
                agent_role = self.workforce.route_task_to_capable_agent(task_id)
                if agent_role:
                    results["executed_tasks"].append(task_id)

        results["pending_tasks"] = [
            tid for tid in task_ids if tid not in results["executed_tasks"]
        ]
        return results

    def _execute_prioritized(
        self, mission_id: str, task_ids: List[str]
    ) -> Dict[str, Any]:
        """Execute tasks by priority (highest first)."""
        results = {
            "mission_id": mission_id,
            "strategy": "prioritized",
            "executed_tasks": [],
            "pending_tasks": task_ids,
        }

        # Sort by priority
        sorted_tasks = sorted(
            [self.workforce.tasks.get(tid) for tid in task_ids if tid],
            key=lambda t: -t.priority,
        )

        for task in sorted_tasks:
            if not task:
                continue
            agent_role = self.workforce.route_task_to_capable_agent(task.task_id)
            if agent_role:
                results["executed_tasks"].append(task.task_id)

        results["pending_tasks"] = [
            tid for tid in task_ids if tid not in results["executed_tasks"]
        ]
        return results


# Global Mission Director instance
_global_director: Optional[MissionDirector] = None


def get_mission_director() -> MissionDirector:
    """Get or create the global Mission Director."""
    global _global_director
    if _global_director is None:
        _global_director = MissionDirector()
    return _global_director


def reset_mission_director() -> None:
    """Reset the global Mission Director (for testing)."""
    global _global_director
    _global_director = None
