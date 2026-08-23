from typing import Any

from ..base_agent import BaseAgent
from ..behaviors.reasoning import Reasoner


class AnalystAgent(BaseAgent):
    """Processes observations, identifies patterns, produces reports."""

    def __init__(self, agent_id: str, **kwargs: Any) -> None:
        super().__init__(agent_id, name="Analyst")
        self._reasoner = Reasoner()
        self._reasoner.add_rule(
            lambda ctx: ctx.get("anomaly_count", 0) > 0,
            "anomalies_detected",
        )

    def decide(self) -> dict[str, Any]:
        conclusions = self._reasoner.evaluate(self._observation)
        return {
            "action": "report",
            "conclusions": conclusions,
            "confidence": min(1.0, len(conclusions) / 5.0),
        }
