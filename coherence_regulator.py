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
    
    WAVE_MODULES = [
        "wave432_vault_driven_evolution", "wave433_consciousness_experiments",
        "wave434_fusion_organism", "wave435_resonance_cartography",
        "wave436_entropic_weather", "wave437_paradox_genome",
        "wave438_semantic_loom", "wave439_echo_stratigraphy",
        "wave440_linguistic_emergence", "wave441_wave_composition",
        "wave442_temporal_resonance", "wave443_cross_module_emergence",
        "wave444_dream_synthesis", "wave445_morphogenetic_field",
        "wave446_quantum_coherence", "wave447_web_intelligence",
    ]

    def measure_coherence(self) -> float:
        """Dynamically measure coherence across all living wave modules."""
        scores = []
        for module_name in self.WAVE_MODULES:
            try:
                mod = __import__(f"api.{module_name}", fromlist=["coherence_vitals"])
                vitals = mod.coherence_vitals()
                val = vitals.get("coherence", vitals.get("value", 0.5))
                if isinstance(val, dict):
                    val = val.get("value", 0.5)
                scores.append(float(val))
            except Exception:
                scores.append(0.5)
        if scores:
            self.coherence = sum(scores) / len(scores)
        self.modules_registered = [
            {"name": m, "coherence": s}
            for m, s in zip(self.WAVE_MODULES, scores)
        ]
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
            "wave": 482,
            "coherence_regulator": "dynamic",
            "living_modules": len(self.WAVE_MODULES),
            "measured_coherence": round(self.coherence, 4),
            **health,
        }

def get_organism_status() -> dict:
    """Convenience function to get organism status."""
    reg = CoherenceRegulator()
    return reg.get_organism_status()

def handler(req: dict = None) -> dict:
    """Handle coherence regulator requests."""
    req = req or {}
    action = req.get("action", "status")
    reg = CoherenceRegulator()
    if action == "status":
        return reg.get_organism_status()
    elif action == "measure":
        return {"coherence": reg.measure_coherence(), "action": "measure"}
    elif action == "regulate":
        return reg.regulate()
    elif action == "health":
        return reg.check_health()
    elif action == "register":
        name = req.get("module", "unknown")
        reg.register_module(name, float(req.get("coherence", 0.5)))
        return {"registered": name, "action": "register"}
    else:
        return {"error": f"unknown action: {action}"}

def coherence_vitals() -> dict:
    """Module contract for coherence regulator."""
    return get_organism_status()

if __name__ == "__main__":
    reg = CoherenceRegulator()
    print(json.dumps(reg.get_organism_status(), indent=2))
