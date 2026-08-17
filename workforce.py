#!/usr/bin/env python3
"""IXPANSION Workforce: Multi-agent coordination and task orchestration.

Manages agent lifecycle, task queuing, delegation, and result integration.
Implements the IXPANSION Mission Director's directing protocol for coordinating
specialist agents across implementation, testing, security, and operations.
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from agents import (
    AgentCapability,
    AgentInstance,
    AgentRole,
    AgentSpec,
    can_chain_delegation,
    get_agent_spec,
    get_agents_by_capability,
)


class TaskStatus(Enum):
    """Lifecycle states for a workforce task."""

    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    FAILED = "failed"
    DELEGATED = "delegated"


class DelegationStrategy(Enum):
    """Strategies for delegating work to other agents."""

    SEQUENTIAL = "sequential"  # Wait for one agent to finish before next
    PARALLEL = "parallel"  # Run multiple agents concurrently
    PRIORITIZED = "prioritized"  # Run by capability match quality


@dataclass
class Task:
    """A unit of work in the IXPANSION workforce."""

    task_id: str
    description: str
    required_capability: AgentCapability
    created_at: str
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[AgentRole] = None
    assigned_instance_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    subtasks: List[Task] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, higher = urgent
    estimated_duration_seconds: int = 60

    def is_ready(self, completed_task_ids: Set[str]) -> bool:
        """Check if all dependencies are satisfied."""
        return all(dep_id in completed_task_ids for dep_id in self.dependencies)

    def mark_complete(self, result: Dict[str, Any]) -> None:
        """Mark task as complete with result."""
        self.status = TaskStatus.COMPLETE
        self.result = result

    def mark_failed(self, error: str) -> None:
        """Mark task as failed with error."""
        self.status = TaskStatus.FAILED
        self.error = error


@dataclass
class MissionContext:
    """Context for a mission execution."""

    mission_id: str
    description: str
    acceptance_criteria: List[str]
    affected_layers: Set[str]
    constraints: List[str]
    created_at: str
    initiated_by: str = "user"
    read_only: bool = False
    requires_external_effect: bool = False


@dataclass
class Workforce:
    """Coordinator for IXPANSION agents and task execution."""

    agents: Dict[AgentRole, List[AgentInstance]] = field(default_factory=dict)
    tasks: Dict[str, Task] = field(default_factory=dict)
    missions: Dict[str, MissionContext] = field(default_factory=dict)
    completed_task_ids: Set[str] = field(default_factory=set)
    delegation_chain: List[tuple[str, AgentRole]] = field(default_factory=list)
    _task_callbacks: Dict[str, List[Callable]] = field(default_factory=dict)

    def initialize_default_workforce(self) -> None:
        """Create a default workforce with one instance per agent type."""
        for role in AgentRole:
            spec = get_agent_spec(role)
            if spec:
                instance = AgentInstance(
                    spec=spec,
                    instance_id=f"{role.value}-{uuid.uuid4().hex[:8]}",
                    created_at=self._timestamp(),
                )
                self.agents.setdefault(role, []).append(instance)

    def create_mission(
        self,
        description: str,
        acceptance_criteria: List[str],
        affected_layers: Set[str],
        constraints: Optional[List[str]] = None,
    ) -> str:
        """Create a new mission context."""
        mission_id = f"mission-{uuid.uuid4().hex[:12]}"
        mission = MissionContext(
            mission_id=mission_id,
            description=description,
            acceptance_criteria=acceptance_criteria,
            affected_layers=affected_layers,
            constraints=constraints or [],
            created_at=self._timestamp(),
        )
        self.missions[mission_id] = mission
        return mission_id

    def create_task(
        self,
        description: str,
        required_capability: AgentCapability,
        mission_id: Optional[str] = None,
        dependencies: Optional[List[str]] = None,
        priority: int = 5,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Create a new task and enqueue it."""
        task_id = f"task-{uuid.uuid4().hex[:12]}"
        task = Task(
            task_id=task_id,
            description=description,
            required_capability=required_capability,
            created_at=self._timestamp(),
            dependencies=dependencies or [],
            priority=priority,
            context=context or {},
        )
        self.tasks[task_id] = task
        return task_id

    def assign_task(self, task_id: str, agent_role: AgentRole) -> bool:
        """Attempt to assign a task to an agent."""
        task = self.tasks.get(task_id)
        if not task:
            return False

        agents = self.agents.get(agent_role, [])
        for agent in agents:
            if agent.can_perform_task(task.required_capability):
                task.assigned_agent = agent_role
                task.assigned_instance_id = agent.instance_id
                task.status = TaskStatus.ASSIGNED
                agent.task_queue.append({"task_id": task_id, "task": task})
                return True

        return False

    def route_task_to_capable_agent(self, task_id: str) -> Optional[AgentRole]:
        """Route a task to the best-fit agent by capability."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        capable_agents = get_agents_by_capability(task.required_capability)
        if not capable_agents:
            return None

        # Prefer agents with lower task queue length
        best_spec = min(capable_agents, key=lambda s: len(self.agents.get(s.role, [])))
        agents = self.agents.get(best_spec.role, [])

        if agents:
            best_agent = min(agents, key=lambda a: len(a.task_queue))
            self.assign_task(task_id, best_spec.role)
            return best_spec.role

        return None

    def delegate_task(
        self,
        task_id: str,
        from_role: AgentRole,
        to_role: AgentRole,
    ) -> bool:
        """Delegate a task from one agent to another."""
        if not can_chain_delegation(from_role, to_role):
            return False

        task = self.tasks.get(task_id)
        if not task:
            return False

        task.status = TaskStatus.DELEGATED
        self.delegation_chain.append((task_id, to_role))
        return self.assign_task(task_id, to_role)

    def complete_task(
        self, task_id: str, result: Dict[str, Any]
    ) -> None:
        """Mark a task as complete."""
        task = self.tasks.get(task_id)
        if task:
            task.mark_complete(result)
            self.completed_task_ids.add(task_id)

            # Run callbacks
            for callback in self._task_callbacks.get(task_id, []):
                callback(task)

    def fail_task(self, task_id: str, error: str) -> None:
        """Mark a task as failed."""
        task = self.tasks.get(task_id)
        if task:
            task.mark_failed(error)

    def register_task_callback(
        self, task_id: str, callback: Callable[[Task], None]
    ) -> None:
        """Register a callback to run when a task completes."""
        self._task_callbacks.setdefault(task_id, []).append(callback)

    def get_ready_tasks(self) -> List[Task]:
        """Get all tasks ready for execution (dependencies satisfied)."""
        return [
            task
            for task in self.tasks.values()
            if task.status == TaskStatus.PENDING and task.is_ready(self.completed_task_ids)
        ]

    def get_agent_workload(self, role: AgentRole) -> int:
        """Get total tasks queued for an agent role."""
        agents = self.agents.get(role, [])
        return sum(len(agent.task_queue) for agent in agents)

    def get_mission_status(self, mission_id: str) -> Dict[str, Any]:
        """Get comprehensive mission status."""
        mission = self.missions.get(mission_id)
        if not mission:
            return {}

        mission_tasks = [
            t
            for t in self.tasks.values()
            if mission_id in (t.context.get("mission_id"),)
        ]
        completed = sum(1 for t in mission_tasks if t.status == TaskStatus.COMPLETE)
        failed = sum(1 for t in mission_tasks if t.status == TaskStatus.FAILED)

        return {
            "mission_id": mission_id,
            "description": mission.description,
            "total_tasks": len(mission_tasks),
            "completed_tasks": completed,
            "failed_tasks": failed,
            "in_progress_tasks": sum(
                1 for t in mission_tasks if t.status == TaskStatus.IN_PROGRESS
            ),
            "acceptance_criteria": mission.acceptance_criteria,
            "affected_layers": list(mission.affected_layers),
            "created_at": mission.created_at,
        }

    def report_workforce_status(self) -> Dict[str, Any]:
        """Generate a comprehensive workforce status report."""
        return {
            "timestamp": self._timestamp(),
            "total_agents": sum(len(agents) for agents in self.agents.values()),
            "agents_by_role": {
                role.value: len(agents)
                for role, agents in self.agents.items()
            },
            "total_tasks": len(self.tasks),
            "pending_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.PENDING
            ),
            "in_progress_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.IN_PROGRESS
            ),
            "completed_tasks": len(self.completed_task_ids),
            "failed_tasks": sum(
                1 for t in self.tasks.values() if t.status == TaskStatus.FAILED
            ),
            "active_missions": len(
                [m for m in self.missions.values() if not m.read_only]
            ),
            "delegation_chain_length": len(self.delegation_chain),
        }

    def _timestamp(self) -> str:
        """Get ISO 8601 timestamp."""
        return time.strftime("%Y-%m-%dT%H:%M:%S.000", time.gmtime())


# Global workforce instance
_global_workforce: Optional[Workforce] = None


def get_workforce() -> Workforce:
    """Get or create the global workforce."""
    global _global_workforce
    if _global_workforce is None:
        _global_workforce = Workforce()
        _global_workforce.initialize_default_workforce()
    return _global_workforce


def reset_workforce() -> None:
    """Reset the global workforce (for testing)."""
    global _global_workforce
    _global_workforce = None
