"""Cross-Module Orchestrator — chains multiple modules into complex workflows.

Instead of calling modules individually, the orchestrator creates workflows
that pass data between modules. A dream can trigger a prophecy, which
influences a faction decision, which changes territory control — all in
a single orchestrated flow.
"""
from __future__ import annotations

import hashlib
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Callable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.unified_router import UnifiedRouter

_router = UnifiedRouter()


class WorkflowStep:
    def __init__(self, module: str, action: str, input_mapping: Dict[str, str], output_key: str):
        self.module = module
        self.action = action
        self.input_mapping = input_mapping
        self.output_key = output_key


class Workflow:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.steps: List[WorkflowStep] = []
        self.created_at = time.time()
        self.id = hashlib.sha256(f"{name}:{self.created_at}".encode()).hexdigest()[:8]

    def add_step(self, module: str, action: str, input_mapping: Dict[str, str] = None, output_key: str = "") -> "Workflow":
        step = WorkflowStep(module, action, input_mapping or {}, output_key or f"step_{len(self.steps)}")
        self.steps.append(step)
        return self

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "steps": len(self.steps),
            "created_at": self.created_at,
        }


class CrossModuleOrchestrator:
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.execution_log: List[Dict[str, Any]] = []

    def create_workflow(self, name: str, description: str = "") -> Dict[str, Any]:
        workflow = Workflow(name, description)
        self.workflows[workflow.id] = workflow
        return {"workflow": workflow.to_dict()}

    def add_step(self, workflow_id: str, module: str, action: str,
                 input_mapping: Dict[str, str] = None, output_key: str = "") -> Dict[str, Any]:
        if workflow_id not in self.workflows:
            return {"error": "workflow not found"}
        self.workflows[workflow_id].add_step(module, action, input_mapping, output_key)
        return {"step_added": module, "workflow": self.workflows[workflow_id].to_dict()}

    def execute(self, workflow_id: str, initial_data: Dict[str, Any] = None) -> Dict[str, Any]:
        if workflow_id not in self.workflows:
            return {"error": "workflow not found"}
        workflow = self.workflows[workflow_id]
        context = dict(initial_data or {})
        results = []
        for i, step in enumerate(workflow.steps):
            payload = {"action": step.action}
            for param, source_key in step.input_mapping.items():
                if source_key.startswith("$"):
                    payload[param] = context.get(source_key[1:], "")
                else:
                    payload[param] = source_key
            result = _router.route(step.module, payload)
            context[step.output_key] = result
            context[f"step_{i}_result"] = result
            results.append({
                "step": i,
                "module": step.module,
                "action": step.action,
                "result_preview": str(result)[:100],
            })
        execution = {
            "workflow": workflow.name,
            "steps_executed": len(results),
            "results": results,
            "timestamp": time.time(),
        }
        self.execution_log.append(execution)
        return execution

    def list_workflows(self) -> List[Dict[str, Any]]:
        return [w.to_dict() for w in self.workflows.values()]

    def orchestrator_stats(self) -> Dict[str, Any]:
        return {
            "total_workflows": len(self.workflows),
            "total_executions": len(self.execution_log),
            "total_steps": sum(len(w.steps) for w in self.workflows.values()),
        }


_orchestrator = CrossModuleOrchestrator()


def cross_module_orchestrator_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "create":
        return _orchestrator.create_workflow(
            payload.get("name", "untitled_workflow"),
            payload.get("description", ""),
        )
    elif action == "add_step":
        return _orchestrator.add_step(
            payload.get("workflow_id", ""),
            payload.get("module", ""),
            payload.get("action", ""),
            payload.get("input_mapping"),
            payload.get("output_key", ""),
        )
    elif action == "execute":
        return _orchestrator.execute(
            payload.get("workflow_id", ""),
            payload.get("initial_data", {}),
        )
    elif action == "list":
        return {"workflows": _orchestrator.list_workflows()}
    return {"status": "active", **_orchestrator.orchestrator_stats()}
