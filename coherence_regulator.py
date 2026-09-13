"""Coherence Regulator — the backbone that keeps every future module plugged into a living system.

This module provides the central coherence intelligence that all wave modules
plug into. It measures, regulates, and maintains the organism's coherence
across all subsystems.

Usage:
    from coherence_regulator import CoherenceRegulator, get_organism_status
    
    reg = CoherenceRegulator()
    status = reg.check_health()
    reg.regulate()
"""
from __future__ import annotations
import json, time
from pathlib import Path

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "coherence_regulator_state.json"

class CoherenceRegulator:
    """Central coherence intelligence for the entire organism."""
    
    def __init__(self):
        self.coherence = 1.0
        self.entropy_budget = 100.0
        self.mutation_pressure = 0.0
        self.vault_density = 0.0
        self.thresholds = {
            "critical": 0.3,
            "warning": 0.6,
            "healthy": 0.8,
            "thriving": 0.95,
        }
        self.modules_registered = []
        self._load_state()
    
    def _load_state(self) -> None:
        if STATE_FILE.exists():
            try:
                state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                self.coherence = state.get("coherence", 1.0)
                self.entropy_budget = state.get("entropy_budget", 100.0)
                self.mutation_pressure = state.get("mutation_pressure", 0.0)
                self.vault_density = state.get("vault_density", 0.0)
                self.modules_registered = state.get("modules_registered", [])
            except Exception:
                pass
    
    def _save_state(self) -> None:
        DATA.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(
            json.dumps({
                "coherence": self.coherence,
                "entropy_budget": self.entropy_budget,
                "mutation_pressure": self.mutation_pressure,
                "vault_density": self.vault_density,
                "modules_registered": self.modules_registered,
                "last_updated": time.time(),
            }, indent=2),
            encoding="utf-8"
        )
    
    def register_module(self, module_name: str, coherence: float) -> None:
        """Register a module with the coherence regulator."""
        self.modules_registered.append({
            "name": module_name,
            "coherence": coherence,
            "timestamp": time.time(),
        })
        self._save_state()
    
    def measure_coherence(self) -> float:
        """Measure current organism coherence."""
        if self.modules_registered:
            avg = sum(m["coherence"] for m in self.modules_registered) / len(self.modules_registered)
            self.coherence = avg
        self._save_state()
        return self.coherence
    
    def check_health(self) -> dict:
        """Return organism health status."""
        coherence = self.measure_coherence()
        pressure = min(1.0, self.vault_density * coherence * 2.0)
        self.mutation_pressure = pressure
        
        if coherence < self.thresholds["critical"]:
            status = "CRITICAL"
        elif coherence < self.thresholds["warning"]:
            status = "WARNING"
        elif coherence < self.thresholds["healthy"]:
            status = "HEALTHY"
        else:
            status = "THRIVING"
        
        return {
            "coherence": round(coherence, 4),
            "mutation_pressure": round(pressure, 4),
            "vault_density": round(self.vault_density, 4),
            "entropy_budget": round(self.entropy_budget, 2),
            "status": status,
            "modules_registered": len(self.modules_registered),
            "timestamp": time.time(),
        }
    
    def regulate(self) -> dict:
        """Apply coherence regulation and return action plan."""
        health = self.check_health()
        actions = []
        
        if health["status"] == "CRITICAL":
            actions.append("EMERGENCY_COHERENCE_RESTORE")
            self.entropy_budget += 50.0
        elif health["status"] == "WARNING":
            actions.append("STABILIZE_VAULT_DENSITY")
            self.entropy_budget -= 10.0
        elif health["status"] == "THRIVING":
            actions.append("ACCELERATE_MUTATION")
            self.entropy_budget -= 5.0
            if health["mutation_pressure"] > 0.7:
                actions.append("SPAWN_NEW_VAULT")
        
        self._save_state()
        return {
            "health": health,
            "actions": actions,
            "regulated": True,
        }
    
    def get_organism_status(self) -> dict:
        """Get full organism status summary."""
        health = self.check_health()
        return {
            "organism": "IXPANSION",
            "wave": 432,
            "coherence_regulator": "active",
            **health,
        }

def get_organism_status() -> dict:
    """Convenience function to get organism status."""
    reg = CoherenceRegulator()
    return reg.get_organism_status()

def coherence_vitals() -> dict:
    """Module contract for coherence regulator."""
    return get_organism_status()

if __name__ == "__main__":
    reg = CoherenceRegulator()
    print(json.dumps(reg.get_organism_status(), indent=2))
