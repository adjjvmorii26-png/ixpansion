"""Wave 406 — Vault Evolution Loop.

Storage organs drive persistent organism evolution through
iterative vault-to-module feedback cycles. Each cycle:
1. Reads vault state
2. Computes mutation pressure
3. Generates new module variants
4. Stores evolution results back to vault
5. Records lineage
"""
from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Dict, List, Optional


class VaultEvolutionLoop:
    """The core feedback loop between storage and organism evolution."""

    def __init__(self):
        self.cycles_completed = 0
        self.lineage: List[Dict] = []
        self.vault_state_snapshot: Optional[Dict] = None
        self.evolution_log: List[Dict] = []

    def execute_cycle(self, vault_data: Dict[str, Any], organism_state: Dict[str, Any]) -> Dict[str, Any]:
        """Run one complete evolution cycle."""
        cycle_id = f"cycle_{self.cycles_completed:04d}"
        timestamp = time.time()

        # Phase 1: Vault read
        self.vault_state_snapshot = vault_data
        entropy = vault_data.get("entropy", 0.0)
        volume = vault_data.get("volume", 0)

        # Phase 2: Compute evolution pressure
        pressure = min(1.0, (entropy * 0.5) + (volume * 0.001))

        # Phase 3: Generate evolution output
        if pressure >= 0.6:
            evolution_type = "MAJOR"
            new_traits = self._generate_traits(pressure)
        elif pressure >= 0.3:
            evolution_type = "MINOR"
            new_traits = self._generate_traits(pressure * 0.5)
        else:
            evolution_type = "STABLE"
            new_traits = {}

        # Phase 4: Store results back
        result = {
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "evolution_type": evolution_type,
            "pressure": pressure,
            "new_traits": new_traits,
            "lineage_entry": {
                "from": organism_state.get("state", "unknown"),
                "to": organism_state.get("evolved_state", "unknown"),
                "pressure": pressure,
            }
        }

        self.cycles_completed += 1
        self.evolution_log.append(result)
        self.lineage.append(result["lineage_entry"])

        return result

    def _generate_traits(self, pressure: float) -> Dict[str, Any]:
        """Generate new organism traits based on pressure."""
        import random
        traits = {}
        if pressure > 0.7:
            traits["new_organ"] = f"organ_{int(pressure * 1000)}"
            traits["mutation_depth"] = random.uniform(0.5, 1.0)
            traits["adaptive_capacity"] = random.uniform(0.6, 1.0)
        elif pressure > 0.4:
            traits["enhanced_parameter"] = random.uniform(0.3, 0.7)
        return traits

    def get_evolution_report(self) -> Dict[str, Any]:
        return {
            "cycles_completed": self.cycles_completed,
            "lineage_depth": len(self.lineage),
            "latest_cycle": self.evolution_log[-1] if self.evolution_log else None,
            "total_evolution_events": len([e for e in self.evolution_log if e["evolution_type"] != "STABLE"]),
        }


_engine = None

def get_loop() -> VaultEvolutionLoop:
    global _engine
    if _engine is None:
        _engine = VaultEvolutionLoop()
    return _engine

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    loop = get_loop()
    q = query or {}

    if "action" not in q:
        return {"module": "vault_evolution_loop", **loop.get_evolution_report()}

    action = q["action"]
    if action == "cycle":
        vault = json.loads(q.get("vault", "{}"))
        organism = json.loads(q.get("organism", "{}"))
        result = loop.execute_cycle(vault, organism)
        return {"cycle_result": result}
    elif action == "report":
        return loop.get_evolution_report()
    else:
        return {"error": f"unknown action: {action}"}
