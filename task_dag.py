#!/usr/bin/env python3
"""
DAG Task Hand-offs for compound intents
Parse multi-stage goals into an execution DAG on the Merkle/CRDT blackboard.
"""
from __future__ import annotations
import re
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from swarm_crdt import CRDTBlackboard
from swarm_merkle_crdt import MerkleCRDT
from neural_symbolic_core import NeuralSymbolicCore


# Stage templates: keyword patterns -> capability
STAGE_PATTERNS = [
    ("simulate", re.compile(r"simulat|lattice|oscillator|ixpansion|physics\s+grid|high-resolution", re.I), "ixpansion"),
    ("evolve", re.compile(r"evolv|mutat|genetic|kernel|optimize\s+physics", re.I), "tool_generation"),
    ("verify", re.compile(r"verif|zk|transcript|proof|commit", re.I), "get_stats"),  # verifiability is local
    ("publish", re.compile(r"publish|youtube|adjjv|synthesize\s+a?\s*release|content\s+package", re.I), "synthesize"),
    ("research", re.compile(r"research|paper|ingest|document", re.I), "research_search"),
    ("search", re.compile(r"search|index|codebase", re.I), "search"),
]

# Default dependency order when multiple stages present
DEFAULT_ORDER = ["research", "simulate", "evolve", "verify", "publish", "search"]


@dataclass
class DAGNode:
    id: str
    stage: str
    capability: str
    description: str
    depends_on: List[str] = field(default_factory=list)
    status: str = "pending"  # pending|ready|running|done|failed
    result: Optional[dict] = None


@dataclass
class TaskDAG:
    id: str
    nodes: Dict[str, DAGNode]
    intent: str

    def ready(self) -> List[DAGNode]:
        done = {nid for nid, n in self.nodes.items() if n.status == "done"}
        out = []
        for n in self.nodes.values():
            if n.status in ("pending", "ready") and all(d in done for d in n.depends_on):
                if n.status == "pending":
                    n.status = "ready"
                out.append(n)
        return out

    def mark_done(self, node_id: str, result: Optional[dict] = None):
        n = self.nodes[node_id]
        n.status = "done"
        n.result = result

    def all_done(self) -> bool:
        return all(n.status == "done" for n in self.nodes.values())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "intent": self.intent,
            "nodes": {
                nid: {
                    "stage": n.stage,
                    "capability": n.capability,
                    "description": n.description,
                    "depends_on": n.depends_on,
                    "status": n.status,
                }
                for nid, n in self.nodes.items()
            },
        }


def parse_intent_to_dag(text: str) -> TaskDAG:
    """Build ordered DAG from compound natural language intent."""
    found = []
    for stage, pat, cap in STAGE_PATTERNS:
        if pat.search(text):
            found.append((stage, cap))
    # de-dupe preserving DEFAULT_ORDER
    order_idx = {s: i for i, s in enumerate(DEFAULT_ORDER)}
    found = sorted(dict(found).items(), key=lambda x: order_idx.get(x[0], 99))
    if not found:
        found = [("search", "search")]

    dag_id = str(uuid.uuid4())[:8]
    nodes: Dict[str, DAGNode] = {}
    prev_id = None
    for stage, cap in found:
        nid = f"{dag_id}-{stage}"
        nodes[nid] = DAGNode(
            id=nid,
            stage=stage,
            capability=cap,
            description=f"{stage}: {text[:120]}",
            depends_on=[prev_id] if prev_id else [],
        )
        prev_id = nid
    return TaskDAG(id=dag_id, nodes=nodes, intent=text)


class DAGOrchestrator:
    """Persist DAG on CRDT/Merkle blackboard; pull ready nodes."""

    def __init__(self, node_id: str = "dag-orch"):
        self.bb = CRDTBlackboard(node_id)
        self.merkle = MerkleCRDT(node_id)
        self.core = NeuralSymbolicCore()
        self.active: Dict[str, TaskDAG] = {}

    def submit_intent(self, text: str) -> TaskDAG:
        dag = parse_intent_to_dag(text)
        self.active[dag.id] = dag
        self.bb.set(f"dag:{dag.id}", dag.to_dict())
        self.merkle.put_register(f"dag:{dag.id}", dag.to_dict())
        return dag

    def next_tasks(self, dag_id: str) -> List[dict]:
        dag = self.active.get(dag_id)
        if not dag:
            return []
        return [
            {"id": n.id, "stage": n.stage, "capability": n.capability, "description": n.description}
            for n in dag.ready()
        ]

    def complete(self, dag_id: str, node_id: str, result: Optional[dict] = None) -> dict:
        dag = self.active[dag_id]
        dag.mark_done(node_id, result)
        self.bb.set(f"dag:{dag_id}", dag.to_dict())
        self.merkle.put_register(f"dag:{dag_id}", dag.to_dict())
        return {
            "dag_id": dag_id,
            "completed": node_id,
            "ready_next": self.next_tasks(dag_id),
            "all_done": dag.all_done(),
        }


if __name__ == "__main__":
    intent = (
        "Execute a high-resolution coupled-oscillator lattice simulation, "
        "evolve its physics kernel, verify via ZK transcript, and synthesize a release for @adjjv."
    )
    orch = DAGOrchestrator()
    dag = orch.submit_intent(intent)
    print("DAG nodes:", [(n.stage, n.capability, n.depends_on) for n in dag.nodes.values()])
    # simulate sequential completion
    while not dag.all_done():
        ready = orch.next_tasks(dag.id)
        print("ready:", ready)
        if not ready:
            break
        for t in ready:
            print(orch.complete(dag.id, t["id"], {"ok": True, "stage": t["stage"]}))
          
