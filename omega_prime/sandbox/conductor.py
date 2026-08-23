from typing import Any

from .realms.continuum_realm import ContinuumRealm
from .realms.lattice_realm import LatticeRealm
from .realms.void_realm import VoidRealm
from ..nucleus.interfaces.sandbox_port import SandboxPort
from ..nucleus.utilities.exception_map import RealmError
from ..nucleus.utilities.diagnostics import Diagnostics


_REALM_MAP: dict[str, type[SandboxPort]] = {
    "void": VoidRealm,
    "lattice": LatticeRealm,
    "continuum": ContinuumRealm,
}


class Conductor:
    """Orchestrates realm lifecycle and agent-realm interactions."""

    def __init__(self) -> None:
        self._realm: SandboxPort | None = None
        self.diag = Diagnostics()

    def enter(self, realm_name: str, config: dict[str, Any] | None = None) -> None:
        cls = _REALM_MAP.get(realm_name)
        if not cls:
            raise RealmError(f"Unknown realm: '{realm_name}'. Available: {list(_REALM_MAP.keys())}")
        self._realm = cls()
        self._realm.materialize(config or {})
        self.diag.increment("realm.entered")

    def pulse(self, intents: list[dict[str, Any]]) -> dict[str, Any]:
        if not self._realm:
            raise RealmError("No realm is active")
        return self._realm.advance(intents)

    @property
    def observation(self) -> dict[str, Any]:
        if not self._realm:
            return {}
        if hasattr(self._realm, 'observation'):
            return self._realm.observation  # type: ignore[attr-defined]
        return {}

    def exit(self) -> None:
        if self._realm:
            self._realm.dissolve()
            self._realm = None
