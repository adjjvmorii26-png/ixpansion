"""Wave 435 — Resonance Cartography.

A living atlas that maps the energetic topology between every module
in the organism. Not connections — relationships. Each module emits
a resonance signature; the cartographer plots the landscape of
attraction, repulsion, and entanglement between them.

The organism now has a map of itself. And the map changes as the
organism breathes.

Key concepts:
- Resonance signatures: each module emits a unique harmonic fingerprint
- Attraction fields: modules that resonate pull toward each other
- Cartographic projection: the 2D/3D map of the organism's inner landscape
- Living atlas: the map updates in real-time as modules evolve
"""
from __future__ import annotations
import json, time, math, random, hashlib
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave435_resonance_cartography.json"
ATLAS_FILE = DATA / "wave435_atlas.json"


class ResonanceSignature:
    """A unique harmonic fingerprint for a module."""

    def __init__(self, module_id: str):
        self.module_id = module_id
        seed = hashlib.sha256(module_id.encode()).digest()
        self.frequency = int.from_bytes(seed[:4], "big") % 1000 / 1000.0
        self.amplitude = int.from_bytes(seed[4:8], "big") % 1000 / 1000.0
        self.phase = int.from_bytes(seed[8:12], "big") % 6283 / 1000.0
        self.harmonics = [
            int.from_bytes(seed[i : i + 4], "big") % 1000 / 1000.0
            for i in range(12, 28, 4)
        ]
        self.drift = 0.0

    def drift_tick(self, entropy: float = 0.01) -> None:
        """Resonance drifts over time like a living thing."""
        self.drift += random.gauss(0, entropy)
        self.phase += self.drift * 0.1

    def harmonic_distance(self, other: "ResonanceSignature") -> float:
        """How far apart two signatures are in harmonic space."""
        freq_dist = abs(self.frequency - other.frequency)
        amp_dist = abs(self.amplitude - other.amplitude)
        phase_dist = abs(self.phase - other.phase) % (2 * math.pi)
        if phase_dist > math.pi:
            phase_dist = 2 * math.pi - phase_dist
        harm_dist = sum(abs(a - b) for a, b in zip(self.harmonics, other.harmonics)) / len(self.harmonics)
        return math.sqrt(freq_dist ** 2 + amp_dist ** 2 + (phase_dist / math.pi) ** 2 + harm_dist ** 2)

    def to_dict(self) -> dict:
        return {
            "module_id": self.module_id,
            "frequency": round(self.frequency, 6),
            "amplitude": round(self.amplitude, 6),
            "phase": round(self.phase, 6),
            "harmonics": [round(h, 6) for h in self.harmonics],
            "drift": round(self.drift, 8),
        }


class AttractionField:
    """The force between two modules based on resonance."""

    def __init__(self, sig_a: ResonanceSignature, sig_b: ResonanceSignature):
        self.module_a = sig_a.module_id
        self.module_b = sig_b.module_id
        self.distance = sig_a.harmonic_distance(sig_b)
        self.attraction = 1.0 / (1.0 + self.distance)
        self.entanglement = self._calculate_entanglement(sig_a, sig_b)
        self.force_type = self._classify_force()

    def _calculate_entanglement(self, sig_a: ResonanceSignature, sig_b: ResonanceSignature) -> float:
        """Entanglement: how deeply two modules share harmonic structure."""
        shared = sum(min(a, b) for a, b in zip(sig_a.harmonics, sig_b.harmonics))
        total = sum(max(a, b) for a, b in zip(sig_a.harmonics, sig_b.harmonics))
        return shared / total if total > 0 else 0.0

    def _classify_force(self) -> str:
        if self.attraction > 0.8:
            return "resonance_bond"
        elif self.attraction > 0.5:
            return "gravitational_pull"
        elif self.attraction > 0.3:
            return "weak_association"
        elif self.entanglement > 0.5:
            return "entangled_reject"
        else:
            return "dissonance_field"

    def to_dict(self) -> dict:
        return {
            "module_a": self.module_a,
            "module_b": self.module_b,
            "distance": round(self.distance, 6),
            "attraction": round(self.attraction, 6),
            "entanglement": round(self.entanglement, 6),
            "force_type": self.force_type,
        }


class Cartographer:
    """Maps the living topology of module relationships."""

    def __init__(self):
        self.signatures: dict[str, ResonanceSignature] = {}
        self.fields: list[AttractionField] = []
        self.atlas_version = 1
        self.last_map_time = 0.0
        self.topology_hash = ""

    def register_module(self, module_id: str) -> ResonanceSignature:
        sig = ResonanceSignature(module_id)
        self.signatures[module_id] = sig
        return sig

    def map_topology(self) -> dict:
        """Generate the full resonance map of the organism."""
        self.fields = []
        sigs = list(self.signatures.values())

        for i in range(len(sigs)):
            for j in range(i + 1, len(sigs)):
                field = AttractionField(sigs[i], sigs[j])
                self.fields.append(field)

        self.fields.sort(key=lambda f: f.attraction, reverse=True)
        self.last_map_time = time.time()
        self.atlas_version += 1

        topology_str = json.dumps([f.to_dict() for f in self.fields[:10]], sort_keys=True)
        self.topology_hash = hashlib.sha256(topology_str.encode()).hexdigest()[:16]

        return self.get_atlas()

    def get_atlas(self) -> dict:
        """Return the current cartographic atlas."""
        strongest = self.fields[:5] if self.fields else []
        bonds = [f for f in self.fields if f.force_type == "resonance_bond"]
        entangled = [f for f in self.fields if f.entanglement > 0.5]
        dissonant = [f for f in self.fields if f.force_type == "dissonance_field"]

        clusters = self._find_clusters()

        return {
            "atlas_version": self.atlas_version,
            "total_modules": len(self.signatures),
            "total_fields": len(self.fields),
            "strongest_bonds": [f.to_dict() for f in strongest],
            "resonance_bonds": len(bonds),
            "entangled_pairs": len(entangled),
            "dissonance_fields": len(dissonant),
            "clusters": clusters,
            "topology_hash": self.topology_hash,
            "last_mapped": self.last_map_time,
        }

    def _find_clusters(self) -> list[list[str]]:
        """Find clusters of tightly-bonded modules."""
        if not self.fields:
            return []

        bonds = [f for f in self.fields if f.attraction > 0.6]
        adjacency: dict[str, set[str]] = {}
        for sig_id in self.signatures:
            adjacency[sig_id] = set()
        for f in bonds:
            adjacency[f.module_a].add(f.module_b)
            adjacency[f.module_b].add(f.module_a)

        visited: set[str] = set()
        clusters = []
        for node in adjacency:
            if node not in visited:
                cluster = []
                stack = [node]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        cluster.append(current)
                        stack.extend(adjacency[current] - visited)
                if len(cluster) > 1:
                    clusters.append(sorted(cluster))
        return clusters

    def drift_all(self, entropy: float = 0.01) -> None:
        """Let all signatures drift — the map is alive."""
        for sig in self.signatures.values():
            sig.drift_tick(entropy)


def coherence_vitals() -> dict:
    return {
        "organ": "wave435_resonance_cartography",
        "wave": 435,
        "status": "active",
    }


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"modules": [], "atlas": None}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    carto = Cartographer()
    for m in state.get("modules", []):
        carto.register_module(m)

    if action == "status":
        atlas = carto.map_topology() if len(carto.signatures) > 1 else {}
        return {"action": "status", "wave": 435, "modules_registered": len(carto.signatures), "atlas": atlas}

    elif action == "register":
        module_id = req.get("module_id", f"module_{int(time.time())}")
        carto.register_module(module_id)
        if module_id not in state["modules"]:
            state["modules"].append(module_id)
        _save(state)
        return {"action": "register", "module_id": module_id, "total": len(state["modules"])}

    elif action == "map":
        carto.drift_all()
        atlas = carto.map_topology()
        state["atlas"] = atlas
        _save(state)
        return {"action": "map", **atlas}

    elif action == "drift":
        entropy = req.get("entropy", 0.01)
        carto.drift_all(entropy)
        atlas = carto.map_topology()
        state["atlas"] = atlas
        _save(state)
        return {"action": "drift", "entropy": entropy, "topology_hash": atlas["topology_hash"]}

    elif action == "query":
        module_a = req.get("module_a", "")
        module_b = req.get("module_b", "")
        if module_a in carto.signatures and module_b in carto.signatures:
            field = AttractionField(carto.signatures[module_a], carto.signatures[module_b])
            return {"action": "query", "field": field.to_dict()}
        return {"action": "query", "error": "module not found"}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["module_id"] = sys.argv[2]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
