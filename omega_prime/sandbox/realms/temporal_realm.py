"""Temporal realm with time-dilation zones.

A lattice world where each zone operates at its own pulse multiplier.
Agents in "fast" zones age/act more frequently per global pulse;
"slow" zones preserve resources but delay actions. This creates
spatial-temporal strategy: agents must decide not only WHERE to go
but WHEN to be there.
"""
from __future__ import annotations

import random
from typing import Any

from ...nucleus.interfaces.sandbox_port import SandboxPort


class Zone:
    def __init__(self, name: str, dilation: float, terrain: str) -> None:
        self.name = name
        self.dilation = dilation  # >1 = fast, <1 = slow, 1.0 = normal
        self.terrain = terrain
        self.local_time: float = 0.0

    @property
    def effective_ticks(self) -> int:
        return int(self.local_time)


class TemporalRealm(SandboxPort):
    """Grid divided into temporal zones with varying dilation factors."""

    ZONE_TYPES = [
        ("chronos", 2.0, "golden"),
        ("normalis", 1.0, "plains"),
        ("tardus", 0.25, "crystal"),
        ("stasis", 0.0, "void"),
    ]

    def __init__(self) -> None:
        self._zones: dict[str, Zone] = {}
        self._agent_positions: dict[str, str] = {}  # agent_id -> zone_name
        self._global_tick = 0

    def materialize(self, config: dict[str, Any]) -> None:
        num_zones = config.get("zones", len(self.ZONE_TYPES))
        for i in range(num_zones):
            zt = self.ZONE_TYPES[i % len(self.ZONE_TYPES)]
            zone = Zone(name=zt[0], dilation=zt[1], terrain=zt[2])
            self._zones[zone.name] = zone

        # Place agents
        for agent_id in config.get("agents", []):
            zone_name = random.choice(list(self._zones.keys()))
            self._agent_positions[agent_id] = zone_name

        self._global_tick = 0

    def advance(self, intents: list[dict[str, Any]]) -> dict[str, Any]:
        self._global_tick += 1
        results = []

        # Advance local time per zone based on dilation
        for zone in self._zones.values():
            zone.local_time += zone.dilation

        # Process movement between zones
        for intent in intents:
            agent_id = intent.get("agent_id")
            target_zone = intent.get("target_zone")
            if agent_id and target_zone and target_zone in self._zones:
                old = self._agent_positions.get(agent_id)
                self._agent_positions[agent_id] = target_zone
                results.append({
                    "agent": agent_id,
                    "moved": f"{old}→{target_zone}",
                    "dilation_change": self._zones[target_zone].dilation,
                })

        return {
            "tick": self._global_tick,
            "zone_times": {z.name: round(z.local_time, 2) for z in self._zones.values()},
            "movements": results,
        }

    def move_agent(self, agent_id: str, target_zone: str) -> bool:
        if target_zone not in self._zones:
            return False
        self._agent_positions[agent_id] = target_zone
        return True

    @property
    def observation(self) -> dict[str, Any]:
        positions_by_zone: dict[str, list[str]] = {z: [] for z in self._zones}
        for aid, zone in self._agent_positions.items():
            if zone in positions_by_zone:
                positions_by_zone[zone].append(aid)
        return {
            "realm": "temporal",
            "tick": self._global_tick,
            "zones": {
                z.name: {"dilation": z.dilation, "local_t": round(z.local_time, 1), "agents": positions_by_zone.get(z.name, [])}
                for z in self._zones.values()
            },
        }

    def dissolve(self) -> None:
        self._zones.clear()
        self._agent_positions.clear()
