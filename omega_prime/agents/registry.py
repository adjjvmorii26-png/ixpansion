from typing import Any

from .base.agent_base import AgentBase
from ..nucleus.utilities.exception_map import AgentSpawnError


class Registry:
    _species_map: dict[str, type[AgentBase]] = {}
    _active: dict[str, AgentBase] = {}

    @classmethod
    def register(cls, name: str, cls_agent: type[AgentBase]) -> None:
        cls._species_map[name] = cls_agent

    @classmethod
    def spawn(cls, agent_id: str, species_name: str, config: dict[str, Any] | None = None) -> AgentBase:
        cls_cls = cls._species_map.get(species_name)
        if not cls_cls:
            raise AgentSpawnError(f"Unknown species: '{species_name}'")
        instance = cls_cls(agent_id=agent_id)
        instance.awaken(config or {})
        cls._active[agent_id] = instance
        return instance

    @classmethod
    def get(cls, agent_id: str) -> AgentBase | None:
        return cls._active.get(agent_id)

    @classmethod
    def roster(cls) -> list[str]:
        return list(cls._active.keys())
