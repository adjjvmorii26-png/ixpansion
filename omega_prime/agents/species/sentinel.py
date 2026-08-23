from typing import Any

from ..base.agent_base import AgentBase
from ..cognition.inference import InferenceEngine


class Sentinel(AgentBase):
    """Guardian species: monitors for threats, raises alerts."""

    def __init__(self, agent_id: str) -> None:
        super().__init__(agent_id, species="sentinel")
        self._engine = InferenceEngine()
        self._engine.add_rule(lambda f: f.get("threat_level", 0) > 5, "raise_alarm")

    def deliberate(self) -> dict[str, Any]:
        conclusions = self._engine.fire(self._stimulus)
        if "raise_alarm" in conclusions:
            return {"intent": "alert", "urgency": "high"}
        return {"intent": "patrol"}
