from typing import Any

from agents.registry import AgentRegistry
from sandbox.orchestrator import SandboxOrchestrator


class AgentController:
    @staticmethod
    def list() -> list[dict[str, str]]:
        return [{"id": aid, "name": AgentRegistry.get(aid).__class__.__name__}
                for aid in AgentRegistry.list_agents()]


class SandboxController:
    orchestrator = SandboxOrchestrator()

    @classmethod
    def status(cls) -> tuple[int, dict[str, Any]]:
        if cls.orchestrator._active:
            return 200, {"sandbox": "running"}
        return 200, {"sandbox": "stopped"}


class TelemetryController:
    _metrics: dict[str, float] = {}

    @classmethod
    def record(cls, name: str, value: float) -> None:
        cls._metrics[name] = value

    @classmethod
    def snapshot(cls) -> dict[str, Any]:
        return {"metrics": cls._metrics}
