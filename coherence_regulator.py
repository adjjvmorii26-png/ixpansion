"""Coherence Regulator — root-level bridge providing both APIs.

This file ensures that ``from coherence_regulator import …`` works
identically from the repo root (serverless / test runner / scripts)
regardless of what the caller expects.

• Module-level functions (_candidate_modules, regulate, KNOWN_LIVING_MODULES, etc.)
  come from api/coherence_regulator.py.
• Class-based API (CoherenceRegulator, get_organism_status, coherence_vitals,
  handler) is the legacy interface that tests and api/index.py depend on.
"""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path as _Path

# ── Re-export module-level API from the real module ─────────────────────
_api_dir = str(_Path(__file__).resolve().parent / "api")
if _api_dir not in sys.path:
    sys.path.insert(0, _api_dir)

import importlib as _il
_real = _il.import_module("api.coherence_regulator")

_candidate_modules   = _real._candidate_modules
_discover_living     = _real._discover_living
measure_coherence_fn = _real.measure_coherence    # avoid name clash
handler_module       = _real.handler
KNOWN_LIVING_MODULES = _real.KNOWN_LIVING_MODULES
living_modules       = _real.living_modules
regulate_fn          = _real.regulate              # avoid name clash


# ── Class-based API (legacy, used by test_coherence + api/index) ───────

_DATA   = _Path(__file__).parent / "data"
_STATE  = _DATA / "coherence_regulator_state.json"


class CoherenceRegulator:
    """Central coherence intelligence for the entire organism."""

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

    def __init__(self, root_path=None, wave_context: str = "unknown"):
        self.coherence = 1.0
        self.entropy_budget = 100.0
        self.mutation_pressure = 0.0
        self.vault_density = 0.0
        self.thresholds = {"critical": 0.3, "warning": 0.6, "healthy": 0.8, "thriving": 0.95}
        self.modules_registered = []
        self._load_state()

    def _load_state(self) -> None:
        if _STATE.exists():
            try:
                s = json.loads(_STATE.read_text(encoding="utf-8"))
                self.coherence      = s.get("coherence", 1.0)
                self.entropy_budget = s.get("entropy_budget", 100.0)
                self.mutation_pressure = s.get("mutation_pressure", 0.0)
                self.vault_density  = s.get("vault_density", 0.0)
                self.modules_registered = s.get("modules_registered", [])
            except Exception:
                pass

    def _save_state(self) -> None:
        _DATA.mkdir(parents=True, exist_ok=True)
        _STATE.write_text(json.dumps({
            "coherence": self.coherence,
            "entropy_budget": self.entropy_budget,
            "mutation_pressure": self.mutation_pressure,
            "vault_density": self.vault_density,
            "modules_registered": self.modules_registered,
            "last_updated": time.time(),
        }, indent=2), encoding="utf-8")

    def register_module(self, name: str, coherence: float) -> None:
        self.modules_registered.append({"name": name, "coherence": coherence, "timestamp": time.time()})
        self._save_state()

    def measure_coherence(self) -> float:
        scores = []
        for m in self.WAVE_MODULES:
            try:
                mod = __import__(f"api.{m}", fromlist=["coherence_vitals"])
                v = mod.coherence_vitals()
                val = v.get("coherence", v.get("value", 0.5))
                if isinstance(val, dict):
                    val = val.get("value", 0.5)
                scores.append(float(val))
            except Exception:
                scores.append(0.5)
        if scores:
            self.coherence = sum(scores) / len(scores)
        self.modules_registered = [{"name": m, "coherence": s} for m, s in zip(self.WAVE_MODULES, scores)]
        self._save_state()
        return self.coherence

    def check_health(self) -> dict:
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
        return {"health": health, "actions": actions, "regulated": True}

    def get_organism_status(self) -> dict:
        health = self.check_health()
        return {
            "organism": "IXPANSION",
            "wave": 482,
            "coherence_regulator": "dynamic",
            "living_modules": len(self.WAVE_MODULES),
            "measured_coherence": round(self.coherence, 4),
            **health,
        }


# ── Module-level convenience functions ──────────────────────────────────

def get_organism_status() -> dict:
    """Convenience function — returns organism status."""
    return CoherenceRegulator().get_organism_status()


def handler(req: dict = None) -> dict:
    """Dispatch: supports both legacy action map and module-contract queries."""
    req = req or {}
    # Module-contract path (used by api/index.py and test_tools)
    if req.get("modules"):
        return handler_module(req)
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
        return handler_module(req) if action else {"error": "unknown action"}


def coherence_vitals() -> dict:
    """Module contract — includes both legacy and module-contract keys."""
    status = CoherenceRegulator().get_organism_status()
    return {
        "module": "coherence_regulator",
        "ok": True,
        "status": "active",
        "coherence": status.get("measured_coherence", 1.0),
        "organism": "IXPANSION",
    }


def resonates_with():
    return ['organism_core', 'coherence_validator', 'consensus_bloom', 'council_oracle', 'causality_weave']
