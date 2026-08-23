from __future__ import annotations
from typing import Any

from core.runtime import IxpansionRuntime


def run_scene(scene: str = "hex_storm", topology: str = "star", ticks: int = 1) -> list[dict[str, Any]]:
    return IxpansionRuntime(scene, topology).run(ticks)


def status() -> dict[str, str]:
    return {"status": "ready", "engine": "ixpansion-genesis"}
