from abc import abstractmethod
from typing import Any

from core.interfaces.agent_interface import AgentInterface
from core.utils.logging import get_logger


class BaseAgent(AgentInterface):
    """Base class with common agent lifecycle."""

    def __init__(self, agent_id: str, name: str = "") -> None:
        self.agent_id = agent_id
        self.name = name or type(self).__name__
        self.logger = get_logger(f"agent.{self.name}")
        self._config: dict[str, Any] = {}
        self._observation: dict[str, Any] = {}

    def initialize(self, config: dict[str, Any]) -> None:
        self._config = config
        self.logger.info("initialized")

    def perceive(self, observation: dict[str, Any]) -> None:
        self._observation = observation

    @abstractmethod
    def decide(self) -> dict[str, Any]:
        """Return an action dict."""

    def act(self, action: dict[str, Any]) -> dict[str, Any]:
        self.logger.debug("acting: %s", action)
        return {"status": "ok", "action": action}
