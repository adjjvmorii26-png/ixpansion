#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json
from typing import Any, Dict, List, Optional
from swarm_crdt import CRDTBlackboard, LWWRegister

def cid(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()[:16]

def encode(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str).encode()

class MerkleNode:
    def __init__(self, data: Any, children: Optional[List[str]] = None):
        self.data = data
        self.children = children or []
        self.cid = cid(encode({"data": data, "children": self.children}))
    def to_dict(self) -> dict:
        return {"cid": self.cid, "data": self.data, "children": self.children}

class MerkleCRDT:
    def __init__(self, node_id: str = "local"):
        self.node_id = node_id
        self.store: Dict[str, MerkleNode] = {}
        self.leaves: Dict[str, str] = {}
        self.bb = CRDTBlackboard(node_id)
    def _leaf_payload(self, key: str, reg: LWWRegister) -> dict:
        return {"key": key, "reg": reg.to_dict()}
    def put_register(self, key: str, value: Any):
        self.bb.set(key, value)
        reg = self.bb.registers[key]
        node = MerkleNode(self._leaf_payload(key, reg))
        self.store[node.cid] = node
        self.leaves[key] = node.cid
    def root(self) -> str:
        layer = sorted(self.leaves.values())
        if not layer:
            return cid(b"empty")
        while len(layer) > 1:
            nxt = []
            for i in range(0, len(layer), 2):
                if i + 1 < len(layer):
                    h = cid(encode({"l": layer[i], "r": layer[i + 1]}))
                    self.store[h] = MerkleNode({"l": layer[i], "r": layer[i + 1]}, [layer[i], layer[i + 1]])
                    nxt.append(h)
                else:
                    nxt.append(layer[i])
            layer = nxt
        return layer[0]
    def missing_cids(self, remote_leaves: Dict[str, str]) -> List[str]:
        have = set(self.store.keys())
        return [rcid for rcid in remote_leaves.values() if rcid not in have]
    def ingest_nodes(self, nodes: Dict[str, dict], remote_leaves: Dict[str, str]):
        for c, nd in nodes.items():
            mn = MerkleNode(nd.get("data"), nd.get("children") or [])
            mn.cid = c
            self.store[c] = mn
        for key, rcid in remote_leaves.items():
            if rcid not in self.store:
                continue
            data = self.store[rcid].data
            if isinstance(data, dict) and "reg" in data:
                reg = LWWRegister.from_dict(data["reg"])
                local = self.bb.registers.get(key, LWWRegister())
                local.merge(reg)
                self.bb.registers[key] = local
                node = MerkleNode(self._leaf_payload(key, local))
                self.store[node.cid] = node
                self.leaves[key] = node.cid
    def sync_with(self, remote: "MerkleCRDT") -> dict:
        my_root, their_root = self.root(), remote.root()
        if my_root == their_root:
            return {"status": "equal", "root": my_root, "transferred": 0}
        need = self.missing_cids(remote.leaves)
        subset = {c: remote.store[c].to_dict() for c in need if c in remote.store}
        self.ingest_nodes(subset, remote.leaves)
        self.bb.merge(remote.bb)
        for k, reg in self.bb.registers.items():
            node = MerkleNode(self._leaf_payload(k, reg))
            self.store[node.cid] = node
            self.leaves[k] = node.cid
        return {"status": "merged", "root_before": my_root, "root_after": self.root(), "transferred": len(subset)}

if __name__ == "__main__":
    a, b = MerkleCRDT("m-a"), MerkleCRDT("m-b")
    a.put_register("phase", "merkle")
    b.put_register("phase", "merkle-sync")
    b.put_register("docs", 3)
    print(a.sync_with(b))
    print(a.bb.get("phase"), a.bb.get("docs"))
  
