"""
PK01_FRACTAL_RELAY_SPINE — Forward-Growth-By-Pressure

The central nervous system of the organism. Every signal passes through
the spine. It connects seeds, relays, and fractal branches. The spine
does not compute — it conducts.

ALEPH: Designed the pressure-growth algorithm
LUMA: Named the branches
AXIOM: Calibrated the decay fields
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).parent.parent / "data" / "fractal_spine"

# ─── IDENTITY ─────────────────────────────────────────────────
SUITE_ID = "0xF1AC7A11"
SUITE_SIG = "FRAC_SPIN_TRANSPORT"
CORE_PHILOSOPHY = "Forward-Growth-By-Pressure"

# ─── STATE ────────────────────────────────────────────────────
_spine_state: Dict = {
    "seed_count": 0,
    "relay_count": 0,
    "branch_count": 0,
    "total_pressure": 0.0,
    "birth_time": time.time(),
    "last_pulse": None,
    "decay_fields": {},
}


def _sig(text: str) -> int:
    return int(hashlib.sha256(f"spine:{text}".encode()).hexdigest()[:12], 16)


# ─── SEED NODES ───────────────────────────────────────────────
class SeedNode:
    def __init__(self, seed_id: str, payload: Dict, parent: Optional[str] = None):
        self.seed_id = seed_id
        self.payload = payload
        self.parent = parent
        self.born = time.time()
        self.pressure = 0.0
        self.children: List[str] = []
        self.alive = True
        self.sig = f"0x{_sig(seed_id):08X}"

    def absorb_pressure(self, amount: float):
        self.pressure += amount
        _spine_state["total_pressure"] += amount
        if self.pressure > 100.0:
            self.burst()

    def burst(self):
        """Pressure threshold reached — generate new branches."""
        self.alive = False
        new_count = max(2, int(self.pressure / 40))
        child_ids = []
        for i in range(new_count):
            cid = f"{self.seed_id}.b{i}"
            child_ids.append(cid)
        self.children = child_ids
        _spine_state["branch_count"] += new_count
        return child_ids

    def to_dict(self) -> Dict:
        return {
            "seed_id": self.seed_id,
            "sig": self.sig,
            "pressure": round(self.pressure, 3),
            "alive": self.alive,
            "children": self.children,
            "born": self.born,
        }


# ─── RELAY CHANNELS ──────────────────────────────────────────
class RelayChannel:
    def __init__(self, channel_id: str, src: str, dst: str):
        self.channel_id = channel_id
        self.src = src
        self.dst = dst
        self.messages = []
        self.latency_ms = 0.0
        self.created = time.time()
        _spine_state["relay_count"] += 1

    def transmit(self, message: Dict):
        entry = {"ts": time.time(), "msg": message}
        self.messages.append(entry)
        if len(self.messages) > 100:
            self.messages = self.messages[-50:]

    def to_dict(self) -> Dict:
        return {
            "channel_id": self.channel_id,
            "src": self.src,
            "dst": self.dst,
            "message_count": len(self.messages),
            "latency_ms": self.latency_ms,
        }


# ─── FRACTAL BRANCHES ───────────────────────────────────────
class FractalBranch:
    def __init__(self, branch_id: str, depth: int = 0, parent: Optional[str] = None):
        self.branch_id = branch_id
        self.depth = depth
        self.parent = parent
        self.leaves: List[str] = []
        self.resonance = 0.0
        self.created = time.time()

    def grow(self) -> Optional[str]:
        if self.depth >= 7:
            return None
        leaf_id = f"{self.branch_id}.l{len(self.leaves)}"
        self.leaves.append(leaf_id)
        return leaf_id

    def decay(self, amount: float):
        self.resonance = max(0.0, self.resonance - amount)

    def to_dict(self) -> Dict:
        return {
            "branch_id": self.branch_id,
            "depth": self.depth,
            "leaves": len(self.leaves),
            "resonance": round(self.resonance, 4),
        }


# ─── SPINE OPERATIONS ────────────────────────────────────────
_seeds: Dict[str, SeedNode] = {}
_relays: Dict[str, RelayChannel] = {}
_branches: Dict[str, FractalBranch] = {}


def plant_seed(seed_id: str, payload: Dict = None, parent: str = None) -> Dict:
    seed = SeedNode(seed_id, payload or {}, parent)
    _seeds[seed_id] = seed
    _spine_state["seed_count"] += 1
    _spine_state["last_pulse"] = time.time()
    return seed.to_dict()


def open_relay(channel_id: str, src: str, dst: str) -> Dict:
    relay = RelayChannel(channel_id, src, dst)
    _relays[channel_id] = relay
    return relay.to_dict()


def grow_branch(branch_id: str, depth: int = 0) -> Dict:
    branch = FractalBranch(branch_id, depth)
    _branches[branch_id] = branch
    leaf = branch.grow()
    return {"branch": branch.to_dict(), "first_leaf": leaf}


def pulse() -> Dict:
    """The spine's heartbeat — conducts pressure through the system."""
    now = time.time()
    _spine_state["last_pulse"] = now
    total_resonance = sum(b.resonance for b in _branches.values())
    alive_seeds = sum(1 for s in _seeds.values() if s.alive)
    return {
        "action": "spine_pulse",
        "timestamp": now,
        "alive_seeds": alive_seeds,
        "total_seeds": len(_seeds),
        "relays": len(_relays),
        "branches": len(_branches),
        "total_pressure": round(_spine_state["total_pressure"], 3),
        "total_resonance": round(total_resonance, 4),
    }


def handler(payload: Dict = None, context: Dict = None) -> Dict:
    p = payload or {}
    action = str(p.get("action", "pulse")).lower()
    if action == "seed":
        return {"action": "plant_seed", **plant_seed(
            p.get("seed_id", f"s{_spine_state['seed_count']+1}"),
            p.get("payload", {}), p.get("parent"))}
    elif action == "relay":
        return {"action": "open_relay", **open_relay(
            p.get("channel_id", f"r{len(_relays)+1}"),
            p.get("src", "origin"), p.get("dst", "target"))}
    elif action == "branch":
        return {"action": "grow_branch", **grow_branch(
            p.get("branch_id", f"b{_spine_state['branch_count']+1}"),
            p.get("depth", 0))}
    elif action == "state":
        return {"action": "spine_state", **_spine_state,
                "seeds": [s.to_dict() for s in _seeds.values()],
                "relays": [r.to_dict() for r in _relays.values()],
                "branches": [b.to_dict() for b in _branches.values()]}
    return pulse()


def coherence_vitals() -> Dict:
    return {
        "layer": "spine",
        "status": "resonant" if _spine_state["last_pulse"] else "dormant",
        "resonance": round(_spine_state["total_pressure"] / max(1, _spine_state["seed_count"]), 3),
        "wave": "449",
        "suite": SUITE_ID,
        "philosophy": CORE_PHILOSOPHY,
    }


def resonates_with() -> List[str]:
    return ["quantum_slot_matrix", "hex_lattice_memory_forge",
            "bio_synthetic_directory_mesh", "temporal_orbit_engine"]
