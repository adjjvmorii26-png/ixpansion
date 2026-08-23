from typing import Any

from .base_agent import BaseAgent
from core.utils.logging import get_logger

logger = get_logger(__name__)


class AgentRegistry:
    _agents: dict[str, BaseAgent] = {}
    _types: dict[str, type[BaseAgent]] = {}

    @classmethod
    def register_type(cls, name: str, agent_cls: type[BaseAgent]) -> None:
        cls._types[name] = agent_cls
        logger.debug("registered agent type '%s'", name)

    @classmethod
    def spawn(cls, agent_id: str, type_name: str, config: dict[str, Any] | None = None) -> BaseAgent:
        if type_name not in cls._types:
            raise KeyError(f"Unknown agent type: {type_name}")
        agent = cls._types[type_name](agent_id=agent_id)
        agent.initialize(config or {})
        cls._agents[agent_id] = agent
        logger.info("spawned agent '%s' (%s)", agent_id, type_name)
        return agent

    @classmethod
    def get(cls, agent_id: str) -> BaseAgent | None:
        return cls._agents.get(agent_id)

    @classmethod
    def list_agents(cls) -> list[str]:
        return list(cls._agents.keys())
