from typing import Any

from .environments.grid_world import GridWorld
from core.interfaces.sandbox_interface import SandboxInterface
from core.utils.logging import get_logger

logger = get_logger(__name__)

_ENVIRONMENTS: dict[str, type[SandboxInterface]] = {
    "grid_world": GridWorld,
}


class SandboxOrchestrator:
    """Manages lifecycle of one or more sandbox environments."""

    def __init__(self) -> None:
        self._active: SandboxInterface | None = None

    def launch(self, env_type: str, config: dict[str, Any] | None = None) -> None:
        cls = _ENVIRONMENTS.get(env_type)
        if not cls:
            raise ValueError(f"Unknown environment type: {env_type}")
        self._active = cls()
        self._active.setup(config or {})
        logger.info("sandbox '%s' launched", env_type)

    def step(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._active:
            raise RuntimeError("No sandbox is active")
        return self._active.step(actions)

    @property
    def observation(self) -> dict[str, Any]:
        if isinstance(self._active, GridWorld):
            return self._active.observation
        return {}

    def stop(self) -> None:
        if self._active:
            self._active.teardown()
            self._active = None
            logger.info("sandbox stopped")
