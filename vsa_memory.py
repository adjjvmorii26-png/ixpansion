#!/usr/bin/env python3
"""
Vector Symbolic Architecture (VSA) Hyperdimensional Memory Grid
Bipolar HD vectors for binding, bundling, and associative recall.
"""
from __future__ import annotations
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Dict, List, Optional, Tuple

DIM = 1024  # practical default (scale to 10k in prod)
STORE = Path("/home/workdir/artifacts/.vsa_memory.json")


def _seed_from(name: str) -> int:
    return int(hashlib.sha256(name.encode()).hexdigest()[:16], 16)


def random_hv(dim: int = DIM, seed: Optional[int] = None) -> List[int]:
    rng = random.Random(seed)
    return [1 if rng.random() > 0.5 else -1 for _ in range(dim)]


def bind(a: List[int], b: List[int]) -> List[int]:
    """Element-wise multiply (XOR analogue for bipolar)."""
    return [x * y for x, y in zip(a, b)]


def unbind(a: List[int], b: List[int]) -> List[int]:
    return bind(a, b)  # self-inverse for bipolar multiply


def bundle(vectors: List[List[int]]) -> List[int]:
    """Majority sum / normalize to bipolar."""
    if not vectors:
        return random_hv()
    dim = len(vectors[0])
    acc = [0] * dim
    for v in vectors:
        for i, x in enumerate(v):
            acc[i] += x
    return [1 if s >= 0 else -1 for s in acc]


def cosine(a: List[int], b: List[int]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    return dot / len(a)


def hv_to_b64(v: List[int]) -> str:
    # pack bits: 1->1, -1->0
    bits = 0
    out = bytearray()
    for i, x in enumerate(v):
        if x > 0:
            bits |= 1 << (i % 8)
        if i % 8 == 7:
            out.append(bits)
            bits = 0
    if len(v) % 8:
        out.append(bits)
    import base64
    return base64.urlsafe_b64encode(bytes(out)).decode()


def b64_to_hv(s: str, dim: int = DIM) -> List[int]:
    import base64
    raw = base64.urlsafe_b64decode(s)
    v = []
    for i in range(dim):
        byte = raw[i // 8] if i // 8 < len(raw) else 0
        bit = (byte >> (i % 8)) & 1
        v.append(1 if bit else -1)
    return v


class VSAMemory:
    def __init__(self, dim: int = DIM):
        self.dim = dim
        self.item_memory: Dict[str, List[int]] = {}
        self.associative: List[Tuple[str, List[int]]] = []
        self._load()

    def atom(self, name: str) -> List[int]:
        if name not in self.item_memory:
            self.item_memory[name] = random_hv(self.dim, _seed_from(name))
        return self.item_memory[name]

    def encode_role_filler(self, role: str, filler: str) -> List[int]:
        return bind(self.atom(role), self.atom(filler))

    def store_record(self, record_id: str, roles: Dict[str, str]):
        parts = [self.encode_role_filler(r, f) for r, f in roles.items()]
        vec = bundle(parts)
        self.associative.append((record_id, vec))
        self._save()
        return vec

    def query(self, roles: Dict[str, str], top_k: int = 3) -> List[Tuple[str, float]]:
        q = bundle([self.encode_role_filler(r, f) for r, f in roles.items()])
        scored = [(rid, cosine(q, v)) for rid, v in self.associative]
        scored.sort(key=lambda x: -x[1])
        return scored[:top_k]

    def query_vector(self, vec: List[int], top_k: int = 3) -> List[Tuple[str, float]]:
        scored = [(rid, cosine(vec, v)) for rid, v in self.associative]
        scored.sort(key=lambda x: -x[1])
        return scored[:top_k]

    def _save(self):
        data = {
            "dim": self.dim,
            "items": {k: hv_to_b64(v) for k, v in self.item_memory.items()},
            "records": [{"id": rid, "hv": hv_to_b64(v)} for rid, v in self.associative[-200:]],
        }
        try:
            STORE.write_text(json.dumps(data))
        except Exception:
            pass

    def _load(self):
        if not STORE.exists():
            return
        try:
            data = json.loads(STORE.read_text())
            self.dim = data.get("dim", DIM)
            self.item_memory = {k: b64_to_hv(v, self.dim) for k, v in data.get("items", {}).items()}
            self.associative = [(r["id"], b64_to_hv(r["hv"], self.dim)) for r in data.get("records", [])]
        except Exception:
            pass



    def capacity_health(self, sample: int = 32) -> dict:
        """Estimate hypervector saturation / loss of orthogonality."""
        atoms = list(self.item_memory.values())
        if len(atoms) < 2:
            return {"status": "ok", "pairs": 0, "mean_abs_cosine": 0.0, "flag": False}
        import random
        idxs = list(range(len(atoms)))
        random.shuffle(idxs)
        pairs = 0
        acc = 0.0
        for i in range(min(sample, len(idxs) - 1)):
            a, b = atoms[idxs[i]], atoms[idxs[(i + 1) % len(idxs)]]
            acc += abs(cosine(a, b))
            pairs += 1
        mean_c = acc / max(pairs, 1)
        # random bipolar vectors ~0 expected; >0.15 suggests crowding
        flag = mean_c > 0.15 or len(self.item_memory) > self.dim // 4
        return {
            "status": "saturated" if flag else "ok",
            "pairs": pairs,
            "mean_abs_cosine": round(mean_c, 4),
            "item_count": len(self.item_memory),
            "dim": self.dim,
            "flag": flag,
        }

if __name__ == "__main__":
    m = VSAMemory()
    m.store_record("doc1", {"type": "research", "topic": "gossip", "status": "ingested"})
    m.store_record("doc2", {"type": "lattice", "topic": "ixpansion", "status": "computed"})
    m.store_record("doc3", {"type": "research", "topic": "crdt", "status": "ingested"})
    hits = m.query({"type": "research", "status": "ingested"})
    print("query research+ingested:", hits)
    print("bind self-inverse ok", cosine(m.atom("x"), unbind(bind(m.atom("x"), m.atom("y")), m.atom("y"))) > 0.9)
  
