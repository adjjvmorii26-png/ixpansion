from abc import abstractmethod
from typing import Any

from ...nucleus.interfaces.agent_port import AgentPort
from ...nucleus.utilities.diagnostics import Diagnostics


class AgentBase(AgentPort):
    def __init__(self, agent_id: str, species: str = "unknown") -> None:
        self.agent_id = agent_id
        self.species = species
        self.diag = Diagnostics()
        self._config: dict[str, Any] = {}
        self._stimulus: dict[str, Any] = {}

    def awaken(self, config: dict[str, Any]) -> None:
        self._config = config

    def observe(self, stimulus: dict[str, Any]) -> None:
        self._stimulus = stimulus

    @abstractmethod
    def deliberate(self) -> dict[str, Any]: ...

    def execute(self, intent: dict[str, Any]) -> dict[str, Any]:
        return {"status": "acknowledged", "intent": intent}
