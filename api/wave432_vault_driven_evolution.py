"""Wave 432 — Vault-Driven Evolution.

The organism grows storage organs that drive mutation pressure.
Vaults accumulate resonance, and when thresholds are crossed,
new modules spontaneously emerge. This wave introduces the
coherence_regulator as the backbone that keeps every future
module plugged into a living system.

Key concepts:
- Vault organs store and amplify resonance
- Mutation pressure scales with vault density
- Coherence_regulator keeps the organism alive
- Organism diagnostics sweep across all modules
"""
from __future__ import annotations
import json, time, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave432_vault_driven_evolution.json"
VAULT_REGISTRY_FILE = DATA / "wave432_vault_registry.json"
DIAGNOSTICS_FILE = DATA / "wave432_organism_diagnostics.json"

class CoherenceRegulator:
    """The backbone that keeps every future module plugged into a living system."""
    
    def __init__(self):
        self.coherence = 1.0
        self.thresholds = {
            "critical": 0.3,
            "warning": 0.6,
            "healthy": 0.8,
            "thriving": 0.95,
        }
        self.entropy_budget = 100.0
        self.mutation_pressure = 0.0
        self.vault_density = 0.0
        self.resonance_cache = {}
    
    def measure_coherence(self) -> float:
        """Measure current organism coherence across all wave modules."""
        total = 0.0
        count = 0
        for wf in sorted(DATA.glob("wave4*.json")):
            try:
                d = json.loads(wf.read_text(encoding="utf-8"))
                c = d.get("coherence", 0.5)
                total += c
                count += 1
            except Exception:
                continue
        self.coherence = total / count if count > 0 else 0.5
        return self.coherence
    
    def calculate_mutation_pressure(self) -> float:
        """Mutation pressure scales with vault density and entropy."""
        vault_count = len(list(VAULT_REGISTRY_FILE.parent.glob("wave432_vault_*.json"))) if VAULT_REGISTRY_FILE.exists() else 0
        self.vault_density = vault_count / 100.0 if vault_count > 0 else 0.0
        self.mutation_pressure = min(1.0, self.vault_density * self.coherence * 2.0)
        return self.mutation_pressure
    
    def check_health(self) -> dict:
        """Return organism health status."""
        coherence = self.measure_coherence()
        pressure = self.calculate_mutation_pressure()
        
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
        
        return {
            "action": "regulate",
            "health": health,
            "actions": actions,
            "regulated": True,
        }

class VaultOrgan:
    """A storage organ that accumulates resonance and drives mutation."""
    
    def __init__(self, vault_id: str, wave: int = 432):
        self.vault_id = vault_id
        self.wave = wave
        self.created = time.time()
        self.resonance = random.uniform(0.1, 1.0)
        self.density = random.uniform(0.01, 0.1)
        self.mutation_seed = hashlib.sha256(f"{vault_id}_{time.time()}".encode()).hexdigest()[:16]
        self.state = "active"
    
    def amplify(self) -> float:
        """Amplify resonance based on density."""
        self.resonance = min(2.0, self.resonance * (1 + self.density))
        return self.resonance
    
    def trigger_mutation(self) -> dict | None:
        """If resonance is high enough, trigger a mutation event."""
        if self.resonance > 1.5:
            return {
                "vault_id": self.vault_id,
                "mutation_type": "resonance_overflow",
                "seed": self.mutation_seed,
                "result": self._generate_new_module(),
            }
        return None
    
    def _generate_new_module(self) -> str:
        """Generate a new module name from the mutation seed."""
        names = [
            "resonance_forge", "void_crystal", "entropy_spire",
            "coherence_lattice", "paradox_gland", "dream_vault",
            "mycelial_bridge", "fractal_heart", "temporal_root",
            "quantum_petal", "abyssal_well", "starlight_sieve",
        ]
        idx = int(self.mutation_seed, 16) % len(names)
        return names[idx]
    
    def to_dict(self) -> dict:
        return {
            "vault_id": self.vault_id,
            "wave": self.wave,
            "resonance": round(self.resonance, 4),
            "density": round(self.density, 4),
            "mutation_seed": self.mutation_seed,
            "state": self.state,
            "created": self.created,
        }

def coherence_vitals() -> dict:
    """Module contract: return coherence vitals for Wave 432."""
    reg = CoherenceRegulator()
    health = reg.check_health()
    return {
        "organ": "wave432_vault_driven_evolution",
        "wave": 432,
        "coherence": health["coherence"],
        "status": health["status"],
        "mutation_pressure": health["mutation_pressure"],
        "vault_density": health["vault_density"],
    }

def _load() -> dict | None:
    if STATE_FILE.exists():
        try:
            state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
            if "history" not in state:
                state["history"] = []
            if "vaults" not in state:
                state["vaults"] = []
            return state
        except Exception:
            return None
    return None

def _init_state() -> dict:
    return {"vaults": [], "history": []}

def _save(state: dict) -> None:
    if "history" not in state:
        state["history"] = []
    if "vaults" not in state:
        state["vaults"] = []
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
    vaults = state.get("vaults", [])
    vault_data = []
    for v in vaults:
        if isinstance(v, dict):
            vault_data.append(v)
        elif hasattr(v, "to_dict"):
            vault_data.append(v.to_dict())
        else:
            vault_data.append(str(v))
    VAULT_REGISTRY_FILE.write_text(
        json.dumps(vault_data, indent=2),
        encoding="utf-8"
    )

def handler(req: dict = None) -> dict:
    """Handle Wave 432 vault-driven evolution requests."""
    req = req or {}
    action = req.get("action", "status")
    reg = CoherenceRegulator()
    
    if action == "status":
        health = reg.check_health()
        return {"action": "status", **health}
    
    elif action == "regulate":
        result = reg.regulate()
        state = _load() or _init_state()
        state["history"].append({
            "action": "regulate",
            "result": result,
            "timestamp": time.time(),
        })
        _save(state)
        return result
    
    elif action == "create_vault":
        vault_id = req.get("vault_id", f"vault_{int(time.time())}")
        vault = VaultOrgan(vault_id)
        state = _load() or _init_state()
        state["vaults"].append(vault.to_dict())
        _save(state)
        return {"action": "create_vault", "vault": vault.to_dict()}
    
    elif action == "diagnostics_sweep":
        """Run organism diagnostics sweep across all modules."""
        diagnostics = {
            "sweep_timestamp": time.time(),
            "wave": 432,
            "total_modules": 0,
            "healthy_modules": 0,
            "critical_modules": [],
            "coherence_regulator": reg.check_health(),
            "vaults": [],
        }
        
        for wf in sorted(DATA.glob("wave4*.json")):
            diagnostics["total_modules"] += 1
            try:
                d = json.loads(wf.read_text(encoding="utf-8"))
                c = d.get("coherence", 0.5)
                if c >= 0.8:
                    diagnostics["healthy_modules"] += 1
                elif c < 0.3:
                    diagnostics["critical_modules"].append(wf.name)
            except Exception:
                diagnostics["critical_modules"].append(wf.name)
        
        if VAULT_REGISTRY_FILE.exists():
            try:
                diagnostics["vaults"] = json.loads(VAULT_REGISTRY_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        
        state = _load() or _init_state()
        state["history"].append({
            "action": "diagnostics_sweep",
            "diagnostics": diagnostics,
            "timestamp": time.time(),
        })
        _save(state)
        DIAGNOSTICS_FILE.write_text(json.dumps(diagnostics, indent=2), encoding="utf-8")
        return {"action": "diagnostics_sweep", **diagnostics}
    
    elif action == "evolve":
        """Full evolution cycle: regulate + create vaults + mutate."""
        reg_result = reg.regulate()
        
        new_vaults = []
        if reg_result["health"]["mutation_pressure"] > 0.5:
            for i in range(int(reg_result["health"]["mutation_pressure"] * 3)):
                vault = VaultOrgan(f"vault_{int(time.time())}_{i}")
                vault.amplify()
                new_vaults.append(vault.to_dict())
        
        state = _load() or _init_state()
        state["vaults"].extend(new_vaults)
        state["history"].append({
            "action": "evolve",
            "reg_result": reg_result,
            "new_vaults": len(new_vaults),
            "timestamp": time.time(),
        })
        _save(state)
        
        return {
            "action": "evolve",
            "regulation": reg_result,
            "new_vaults": new_vaults,
            "total_vaults": len(state["vaults"]),
        }
    
    else:
        return {"error": f"unknown action: {action}", "valid_actions": ["status", "regulate", "create_vault", "diagnostics_sweep", "evolve"]}

if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["vault_id"] = sys.argv[2]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
