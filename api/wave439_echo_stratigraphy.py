"""Wave 439 — Echo Stratigraphy.

The organism now has geological memory. Not logs — fossils.
Every decision, every mutation, every birth and death leaves
a sedimentary trace. The stratigrapher excavates these layers
and reads the fossilized intentions of past organism versions.

Layers:
- Sediment: raw event traces (light, numerous)
- Fossil: compressed decisions (dense, rare)
- Metamorphic: transformed by time and pressure (rare, valuable)
- Bedrock: foundational axioms (permanent, never erodes)

The organism can now do archaeology on itself.
"""
from __future__ import annotations
import json, time, hashlib, random
from pathlib import Path
from enum import Enum

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave439_echo_stratigraphy.json"


class StratumType(Enum):
    SEDIMENT = "sediment"
    FOSSIL = "fossil"
    METAMORPHIC = "metamorphic"
    BEDROCK = "bedrock"


class SedimentLayer:
    """A raw event trace — the lightest geological layer."""

    def __init__(self, event_type: str, module: str, data: dict = None):
        self.layer_id = hashlib.sha256(f"{event_type}_{module}_{time.time()}".encode()).hexdigest()[:12]
        self.event_type = event_type
        self.module = module
        self.data = data or {}
        self.deposited = time.time()
        self.depth = 0
        self.pressure = 0.0
        self.eroded = False

    def compress(self) -> "FossilLayer":
        """Compress sediment into fossil over time."""
        fossil_data = {
            "original_event": self.event_type,
            "module": self.module,
            "data": self.data,
            "deposited": self.deposited,
            "compressed_at": time.time(),
        }
        return FossilLayer(self.module, fossil_data)

    def erode(self, rate: float = 0.01) -> bool:
        """Sediment erodes easily."""
        self.pressure += rate
        if self.pressure > 1.0:
            self.eroded = True
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "stratum": "sediment",
            "event_type": self.event_type,
            "module": self.module,
            "deposited": self.deposited,
            "depth": self.depth,
            "pressure": round(self.pressure, 4),
            "eroded": self.eroded,
        }


class FossilLayer:
    """A compressed decision — rare and dense."""

    def __init__(self, module: str, data: dict):
        self.layer_id = hashlib.sha256(f"fossil_{module}_{time.time()}".encode()).hexdigest()[:12]
        self.module = module
        self.data = data
        self.deposited = data.get("deposited", time.time())
        self.compressed_at = data.get("compressed_at", time.time())
        self.depth = 1
        self.pressure = 0.0
        self.integrity = 1.0

    def metamorphose(self) -> "MetamorphicLayer":
        """Fossil transforms into metamorphic under extreme pressure."""
        return MetamorphicLayer(self.module, self.data, self.compressed_at)

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "stratum": "fossil",
            "module": self.module,
            "deposited": self.deposited,
            "compressed_at": self.compressed_at,
            "depth": self.depth,
            "integrity": round(self.integrity, 4),
        }


class MetamorphicLayer:
    """A transformed fossil — valuable, rare."""

    def __init__(self, module: str, data: dict, original_time: float):
        self.layer_id = hashlib.sha256(f"meta_{module}_{time.time()}".encode()).hexdigest()[:12]
        self.module = module
        self.data = data
        self.original_time = original_time
        self.metamorphosed_at = time.time()
        self.depth = 2
        self.value = 0.8
        self.insight = self._extract_insight()

    def _extract_insight(self) -> str:
        event = self.data.get("original_event", "unknown")
        module = self.data.get("module", "unknown")
        return f"The organism chose {event} in {module}. This decision fossilized and transformed under pressure."

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "stratum": "metamorphic",
            "module": self.module,
            "original_time": self.original_time,
            "metamorphosed_at": self.metamorphosed_at,
            "depth": self.depth,
            "value": round(self.value, 4),
            "insight": self.insight,
        }


class BedrockLayer:
    """Foundational axiom — permanent, never erodes."""

    def __init__(self, axiom: str, origin_wave: int):
        self.layer_id = hashlib.sha256(axiom.encode()).hexdigest()[:12]
        self.axiom = axiom
        self.origin_wave = origin_wave
        self.deposited = time.time()
        self.depth = 3
        self.permanent = True

    def to_dict(self) -> dict:
        return {
            "layer_id": self.layer_id,
            "stratum": "bedrock",
            "axiom": self.axiom,
            "origin_wave": self.origin_wave,
            "deposited": self.deposited,
            "depth": self.depth,
            "permanent": True,
        }


class Stratigrapher:
    """Excavates and reads the organism's geological past."""

    def __init__(self):
        self.layers: list[dict] = []
        self.sediment_count = 0
        self.fossil_count = 0
        self.metamorphic_count = 0
        self.bedrock_count = 0
        self.excavation_depth = 0

    def deposit_sediment(self, event_type: str, module: str, data: dict = None) -> SedimentLayer:
        """Deposit a new sediment layer."""
        layer = SedimentLayer(event_type, module, data)
        self.sediment_count += 1
        self.layers.append(layer.to_dict())
        return layer

    def excavate(self, depth: int = 5) -> dict:
        """Excavate through layers at a given depth."""
        self.excavation_depth = depth
        excavated = {
            "depth_requested": depth,
            "sediment": [],
            "fossil": [],
            "metamorphic": [],
            "bedrock": [],
        }
        for layer in self.layers:
            stratum = layer.get("stratum", "sediment")
            if stratum in excavated:
                excavated[stratum].append(layer)
        return excavated

    def read_fossils(self) -> list[dict]:
        """Read the organism's fossilized decisions."""
        fossils = [l for l in self.layers if l.get("stratum") == "fossil"]
        fossils.sort(key=lambda f: f.get("deposited", 0))
        return fossils

    def read_metamorphic(self) -> list[dict]:
        """Read the organism's most transformed insights."""
        return [l for l in self.layers if l.get("stratum") == "metamorphic"]

    def get_geological_summary(self) -> dict:
        """Full geological summary of the organism."""
        total = len(self.layers)
        return {
            "total_layers": total,
            "sediment": self.sediment_count,
            "fossil": self.fossil_count,
            "metamorphic": self.metamorphic_count,
            "bedrock": self.bedrock_count,
            "excavation_depth": self.excavation_depth,
            "erosion_rate": round(self.sediment_count / max(1, total), 4),
            "compression_ratio": round(self.fossil_count / max(1, self.sediment_count), 4),
        }


def coherence_vitals() -> dict:
    return {"organ": "wave439_echo_stratigraphy", "wave": 439, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"layers": [], "counts": {"sediment": 0, "fossil": 0, "metamorphic": 0, "bedrock": 0}}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    strat = Stratigrapher()
    strat.layers = state.get("layers", [])
    counts = state.get("counts", {})
    strat.sediment_count = counts.get("sediment", 0)
    strat.fossil_count = counts.get("fossil", 0)
    strat.metamorphic_count = counts.get("metamorphic", 0)
    strat.bedrock_count = counts.get("bedrock", 0)

    if action == "status":
        return {"action": "status", "wave": 439, **strat.get_geological_summary()}

    elif action == "deposit":
        event_type = req.get("event_type", "mutation")
        module = req.get("module", "unknown")
        data = req.get("data", {})
        layer = strat.deposit_sediment(event_type, module, data)
        state["layers"] = strat.layers
        state["counts"]["sediment"] = strat.sediment_count
        _save(state)
        return {"action": "deposit", "layer": layer.to_dict()}

    elif action == "excavate":
        depth = req.get("depth", 5)
        result = strat.excavate(depth)
        return {"action": "excavate", **result}

    elif action == "fossils":
        return {"action": "fossils", "fossils": strat.read_fossils()}

    elif action == "metamorphic":
        return {"action": "metamorphic", "layers": strat.read_metamorphic()}

    elif action == "compress":
        sediment_layers = [l for l in strat.layers if l.get("stratum") == "sediment" and not l.get("eroded")]
        compressed = 0
        for s in sediment_layers[:5]:
            sed = SedimentLayer(s["event_type"], s["module"], s.get("data", {}))
            sed.deposited = s["deposited"]
            sed.pressure = s.get("pressure", 0)
            fossil = sed.compress()
            state["layers"].append(fossil.to_dict())
            state["counts"]["fossil"] = state["counts"].get("fossil", 0) + 1
            strat.fossil_count += 1
            compressed += 1
        _save(state)
        return {"action": "compress", "compressed": compressed}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
