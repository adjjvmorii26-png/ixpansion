#!/usr/bin/env python3
"""
Distributed CRDT Blackboard
State-based LWW-Register Map + OR-Set for lock-free multi-writer sync.
"""

from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Set, Tuple

CRDT_FILE = Path("/home/workdir/artifacts/.crdt_blackboard.json")


class LWWRegister:
    """Last-Write-Wins register with (timestamp, node_id) tie-break."""

    def __init__(self, value: Any = None, ts: float = 0.0, node: str = ""):
        self.value = value
        self.ts = ts
        self.node = node

    def set(self, value: Any, node: str, ts: Optional[float] = None):
        t = ts if ts is not None else time.time()
        if t > self.ts or (t == self.ts and node > self.node):
            self.value, self.ts, self.node = value, t, node

    def merge(self, other: "LWWRegister"):
        self.set(other.value, other.node, other.ts)

    def to_dict(self) -> dict:
        return {"value": self.value, "ts": self.ts, "node": self.node}

    @classmethod
    def from_dict(cls, d: dict) -> "LWWRegister":
        return cls(d.get("value"), d.get("ts", 0.0), d.get("node", ""))


class ORSet:
    """Observed-Remove Set: adds tagged with unique ids; removes tombstone tags."""

    def __init__(self):
        self.adds: Dict[str, Set[str]] = {}   # element -> set of unique tags
        self.removes: Set[str] = set()        # removed tags

    def add(self, element: str, tag: str):
        self.adds.setdefault(element, set()).add(tag)

    def remove(self, element: str):
        for tag in list(self.adds.get(element, [])):
            self.removes.add(tag)
        self.adds.pop(element, None)

    def merge(self, other: "ORSet"):
        for el, tags in other.adds.items():
            self.adds.setdefault(el, set()).update(tags)
        self.removes |= other.removes
        # GC: drop fully-removed elements
        for el in list(self.adds.keys()):
            self.adds[el] -= self.removes
            if not self.adds[el]:
                del self.adds[el]

    def values(self) -> Set[str]:
        return {el for el, tags in self.adds.items() if tags - self.removes}

    def to_dict(self) -> dict:
        return {
            "adds": {k: list(v) for k, v in self.adds.items()},
            "removes": list(self.removes),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ORSet":
        o = cls()
        for k, tags in d.get("adds", {}).items():
            o.adds[k] = set(tags)
        o.removes = set(d.get("removes", []))
        return o


class CRDTBlackboard:
    """
    Shared agent memory:
      - registers: LWW map for key/value knowledge
      - agents: OR-Set of known node/agent ids
    """

    def __init__(self, node_id: str = "local"):
        self.node_id = node_id
        self.registers: Dict[str, LWWRegister] = {}
        self.agents = ORSet()
        self._load()

    def set(self, key: str, value: Any):
        reg = self.registers.setdefault(key, LWWRegister())
        reg.set(value, self.node_id)
        self._save()

    def get(self, key: str, default=None) -> Any:
        reg = self.registers.get(key)
        return reg.value if reg else default

    def add_agent(self, agent_id: str):
        tag = f"{self.node_id}:{time.time()}:{agent_id}"
        self.agents.add(agent_id, tag)
        self._save()

    def remove_agent(self, agent_id: str):
        self.agents.remove(agent_id)
        self._save()

    def merge(self, other: "CRDTBlackboard"):
        for k, reg in other.registers.items():
            if k not in self.registers:
                self.registers[k] = LWWRegister()
            self.registers[k].merge(reg)
        self.agents.merge(other.agents)
        self._save()

    def merge_dict(self, data: dict):
        other = CRDTBlackboard.from_dict(data, node_id=data.get("node_id", "remote"))
        self.merge(other)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "registers": {k: v.to_dict() for k, v in self.registers.items()},
            "agents": self.agents.to_dict(),
            "ts": datetime.now(timezone.utc).isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict, node_id: str = "remote") -> "CRDTBlackboard":
        bb = cls(node_id=node_id)
        bb.registers = {
            k: LWWRegister.from_dict(v) for k, v in data.get("registers", {}).items()
        }
        bb.agents = ORSet.from_dict(data.get("agents", {}))
        return bb

    def _save(self):
        tmp = CRDT_FILE.with_suffix(".tmp")
        try:
            tmp.write_text(json.dumps(self.to_dict(), indent=2, default=str))
            tmp.replace(CRDT_FILE)
        except Exception:
            pass

    def _load(self):
        if CRDT_FILE.exists():
            try:
                data = json.loads(CRDT_FILE.read_text())
                # Inline hydrate — avoid from_dict recursion through __init__
                for k, v in data.get("registers", {}).items():
                    self.registers[k] = LWWRegister.from_dict(v)
                self.agents = ORSet.from_dict(data.get("agents", {}))
            except Exception:
                pass


if __name__ == "__main__":
    a = CRDTBlackboard("node-a")
    b = CRDTBlackboard("node-b")
    a.set("phase", "trinity")
    a.add_agent("indexer")
    time.sleep(0.01)
    b.set("phase", "gossip")
    b.add_agent("researcher")
    a.merge(b)
    b.merge(a)
    print("A phase:", a.get("phase"), "agents:", a.agents.values())
    print("B phase:", b.get("phase"), "agents:", b.agents.values())
      
