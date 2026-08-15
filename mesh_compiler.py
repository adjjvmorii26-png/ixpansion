#!/usr/bin/env python3
"""
Production intent→primitive compiler runtime
AST/IR · dynamic gas · HMAC receipts · CoW shadow · policy rotation · negative tests
"""
from __future__ import annotations
import hashlib
import hmac
import json
import os
import re
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

SCHEMA_VERSION = "2.1.0"
POLICY_RULES: Dict[str, Any] = {
    "schema_version": SCHEMA_VERSION,
    "max_gas": 50_000,
    "max_text": 8_000,
    "max_delta_keys": 64,
    "max_entropy_shift": 0.85,
    "allowed_primitives": [
        "lattice_run", "genetic_evolve", "crdt_put", "gcode_emit",
        "verify_transcript", "publish_bundle", "dag_submit",
    ],
}


def policy_hash(rules=None) -> str:
    r = rules or POLICY_RULES
    return hashlib.sha256(
        json.dumps(r, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:32]


POLICY_HASH = policy_hash()
POLICY_HISTORY: List[Tuple[str, float]] = [(POLICY_HASH, time.time())]
MAX_POLICY_DRIFT_SEC = float(os.environ.get("MESH_MAX_POLICY_DRIFT_SEC", "300"))
CLUSTER_SECRET = os.environ.get(
    "MESH_CLUSTER_SECRET", "ixpansion-dev-secret-change-me"
).encode()


def rotate_policy(new_rules: dict = None) -> str:
    global POLICY_HASH, POLICY_HISTORY
    if new_rules:
        POLICY_RULES.update(new_rules)
    POLICY_HASH = policy_hash(POLICY_RULES)
    POLICY_HISTORY.append((POLICY_HASH, time.time()))
    POLICY_HISTORY[:] = POLICY_HISTORY[-8:]
    return POLICY_HASH


def policy_acceptable(receipt_hash: str, now: float = None) -> Tuple[bool, str]:
    now = time.time() if now is None else now
    if receipt_hash == POLICY_HASH:
        return True, "current"
    for i, (h, activated) in enumerate(POLICY_HISTORY):
        if h != receipt_hash:
            continue
        superseded_at = None
        for h2, t2 in POLICY_HISTORY[i + 1 :]:
            if h2 != h:
                superseded_at = t2
                break
        if superseded_at is None:
            return True, "still_active"
        if now - superseded_at <= MAX_POLICY_DRIFT_SEC:
            return True, "grace_window"
        return False, "policy_expired"
    return False, "policy_unknown"


# ─── IR ───────────────────────────────────────────────────────────────────
@dataclass
class IntentNode:
    kind: str
    raw: str
    params: Dict[str, Any] = field(default_factory=dict)
    children: List["IntentNode"] = field(default_factory=list)


@dataclass
class MeshOp:
    op: str
    args: Dict[str, Any]
    gas_budget: int = 5_000
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MeshIR:
    version: str
    policy_hash: str
    ops: List[MeshOp]
    source_intent: str

    def to_dict(self):
        return {
            "version": self.version,
            "policy_hash": self.policy_hash,
            "source_intent": self.source_intent,
            "ops": [
                {
                    "op": o.op,
                    "args": o.args,
                    "gas_budget": o.gas_budget,
                    "meta": o.meta,
                }
                for o in self.ops
            ],
        }


STAGE_PATTERNS = [
    ("simulate", re.compile(r"simulat|lattice|oscillator|ixpansion|child universe|sandbox", re.I)),
    ("evolve", re.compile(r"evolv|mutat|genetic|kernel|morphogenetic", re.I)),
    ("verify", re.compile(r"verif|zk|transcript|proof|stability", re.I)),
    ("publish", re.compile(r"publish|youtube|adjjv|whitepaper|syndicate|arweave", re.I)),
    ("fabricate", re.compile(r"g-?code|cnc|microfluidic|actuator|fabricat|load-bearing", re.I)),
    ("research", re.compile(r"research|paper|ingest", re.I)),
    ("consensus", re.compile(r"raft|partition|consensus|quorum", re.I)),
]


def parse_intent_ast(text: str) -> IntentNode:
    if len(text) > POLICY_RULES["max_text"]:
        raise ValueError("intent exceeds max_text")
    root = IntentNode(kind="root", raw=text[:500])
    for kind, pat in STAGE_PATTERNS:
        if pat.search(text):
            params = {}
            m = re.search(r"\bN\s*=\s*(\d+)", text, re.I)
            if m:
                params["n"] = min(64, int(m.group(1)))
            root.children.append(IntentNode(kind=kind, raw=kind, params=params))
    if not root.children:
        root.children.append(IntentNode(kind="simulate", raw="default", params={}))
    return root


def lower_to_ir(ast_root: IntentNode, intent_text: str) -> MeshIR:
    ops: List[MeshOp] = []
    for node in ast_root.children:
        if node.kind == "simulate":
            args = {"n": node.params.get("n", 16), "steps": 12, "seed": 0.42}
            ops.append(MeshOp("lattice_run", args, dynamic_gas_cost("lattice_run", args)))
        elif node.kind == "evolve":
            args = {"generations": 3, "population": 5}
            ops.append(MeshOp("genetic_evolve", args, dynamic_gas_cost("genetic_evolve", args)))
        elif node.kind == "verify":
            ops.append(MeshOp("verify_transcript", {"require": True}, dynamic_gas_cost("verify_transcript", {})))
        elif node.kind == "publish":
            ops.append(MeshOp("publish_bundle", {"channel": "@adjjv"}, dynamic_gas_cost("publish_bundle", {})))
        elif node.kind == "fabricate":
            args = {"n": node.params.get("n", 12)}
            ops.append(MeshOp("gcode_emit", args, dynamic_gas_cost("gcode_emit", args)))
        elif node.kind == "research":
            ops.append(MeshOp("dag_submit", {"stage": "research"}, dynamic_gas_cost("dag_submit", {})))
        elif node.kind == "consensus":
            ops.append(MeshOp("crdt_put", {"key": "consensus_probe", "value": "ok"}, dynamic_gas_cost("crdt_put", {})))
    return MeshIR(SCHEMA_VERSION, POLICY_HASH, ops, intent_text[:300])


def optimize_ir(ir: MeshIR) -> MeshIR:
    seen = set()
    out = []
    for op in ir.ops:
        key = (op.op, json.dumps(op.args, sort_keys=True))
        if key in seen and op.op in ("lattice_run", "crdt_put"):
            continue
        seen.add(key)
        out.append(op)
    merged: List[MeshOp] = []
    for op in out:
        if merged and merged[-1].op == op.op == "genetic_evolve":
            a, b = merged[-1].args, op.args
            merged[-1].args = {
                "generations": max(a.get("generations", 1), b.get("generations", 1)),
                "population": max(a.get("population", 1), b.get("population", 1)),
            }
            merged[-1].gas_budget = dynamic_gas_cost("genetic_evolve", merged[-1].args)
        else:
            merged.append(op)
    ir.ops = merged
    return ir


# ─── Gas ──────────────────────────────────────────────────────────────────
class GasMeter:
    def __init__(self, budget: int):
        self.budget = budget
        self.used = 0

    def charge(self, units: int, label: str = ""):
        self.used += units
        if self.used > self.budget:
            raise RuntimeError(
                f"gas_exhausted used={self.used} budget={self.budget} at {label}"
            )

    def remaining(self) -> int:
        return max(0, self.budget - self.used)


def dynamic_gas_cost(op: str, args: dict) -> int:
    base = {
        "lattice_run": 100,
        "genetic_evolve": 500,
        "verify_transcript": 40,
        "publish_bundle": 80,
        "gcode_emit": 60,
        "crdt_put": 15,
        "dag_submit": 25,
    }.get(op, 50)
    n = int(args.get("n", 1) or 1)
    steps = int(args.get("steps", 1) or 1)
    gens = int(args.get("generations", 1) or 1)
    pop = int(args.get("population", 1) or 1)
    if op == "lattice_run":
        return base + (n * n * steps) // 4
    if op == "genetic_evolve":
        return base + gens * pop * 80
    if op == "gcode_emit":
        return base + n * 8
    return base


# ─── Receipts ─────────────────────────────────────────────────────────────
def compile_receipt(ir_dict: dict, secret: bytes = CLUSTER_SECRET) -> dict:
    body = json.dumps(ir_dict, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema_version": SCHEMA_VERSION,
        "policy_hash": ir_dict.get("policy_hash"),
        "ir_commit": hashlib.sha256(body).hexdigest(),
        "hmac": hmac.new(secret, body, hashlib.sha256).hexdigest(),
        "ts": time.time(),
    }


def verify_receipt(
    ir_dict: dict, receipt: dict, secret: bytes = CLUSTER_SECRET
) -> Tuple[bool, str]:
    ok_p, reason_p = policy_acceptable(receipt.get("policy_hash") or "")
    if not ok_p:
        return False, f"policy_hash_mismatch:{reason_p}"
    if receipt.get("schema_version") != SCHEMA_VERSION:
        return False, "schema_version_mismatch"
    body = json.dumps(ir_dict, sort_keys=True, separators=(",", ":")).encode()
    if hashlib.sha256(body).hexdigest() != receipt.get("ir_commit"):
        return False, "ir_commit_mismatch"
    expect = hmac.new(secret, body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expect, receipt.get("hmac", "")):
        return False, "hmac_invalid"
    return True, "ok"


def guard_ir(ir: MeshIR) -> Tuple[bool, List[str]]:
    errs = []
    if ir.version != SCHEMA_VERSION:
        errs.append("schema_version")
    if ir.policy_hash != POLICY_HASH:
        # allow grace-window hashes
        ok_p, _ = policy_acceptable(ir.policy_hash)
        if not ok_p:
            errs.append("policy_hash")
    total_gas = sum(o.gas_budget for o in ir.ops)
    if total_gas > POLICY_RULES["max_gas"]:
        errs.append(f"total_gas {total_gas} > max")
    for o in ir.ops:
        if o.op not in POLICY_RULES["allowed_primitives"]:
            errs.append(f"primitive_forbidden:{o.op}")
    return (len(errs) == 0), errs


# ─── Shadow CoW sandbox ───────────────────────────────────────────────────
class ShadowSandbox:
    def __init__(self):
        self.state = {
            "keys": {},
            "energy": None,
            "expr": None,
            "published": False,
        }
        self.tmpdir = tempfile.mkdtemp(prefix="shadow_ixp_")
        self.files: List[str] = []

    def write_staged(self, name: str, content: str) -> str:
        path = str(Path(self.tmpdir) / name)
        Path(path).write_text(content)
        self.files.append(path)
        return path

    def purge(self):
        try:
            shutil.rmtree(self.tmpdir, ignore_errors=True)
        except Exception:
            pass


def shadow_execute(ir: MeshIR, verify_only: bool = True) -> dict:
    box = ShadowSandbox()
    total_budget = sum(dynamic_gas_cost(o.op, o.args) for o in ir.ops) or 1
    total_budget = min(total_budget, POLICY_RULES["max_gas"])
    meter = GasMeter(total_budget)
    logs = []
    try:
        for op in ir.ops:
            cost = dynamic_gas_cost(op.op, op.args)
            meter.charge(cost, op.op)
            if op.op == "lattice_run":
                from spatial_shard import run_adaptive

                n = min(24, int(op.args.get("n", 12)))
                steps = min(20, int(op.args.get("steps", 8)))
                r = run_adaptive(
                    n=n,
                    steps=steps,
                    seed=float(op.args.get("seed", 0.4)),
                    worker_loads={"shadow": 0.2},
                )
                box.state["energy"] = r.get("final_energy")
                box.state["keys"]["lattice"] = {
                    "energy": box.state["energy"],
                    "engine": r.get("engine"),
                }
                logs.append({"op": op.op, "ok": True, "gas": cost})
            elif op.op == "genetic_evolve":
                from closed_loop_physics import closed_loop

                r = closed_loop(
                    generations=min(3, int(op.args.get("generations", 2))),
                    population=min(5, int(op.args.get("population", 4))),
                )
                box.state["expr"] = r.get("evolved_expr")
                box.state["keys"]["genetic"] = {
                    "expr": box.state["expr"],
                    "fitness": r.get("evolved_fitness"),
                }
                logs.append({"op": op.op, "ok": True, "gas": cost})
            elif op.op == "verify_transcript":
                if box.state.get("energy") is not None:
                    from task_verifiability import prove_lattice_run, verify_transcript

                    p = prove_lattice_run(
                        "shadow",
                        {"n": 8},
                        {"final_energy": box.state["energy"], "engine": "shadow"},
                    )
                    ok, reason = verify_transcript(p)
                    box.state["keys"]["verify"] = {"ok": ok, "reason": reason}
                    logs.append({"op": op.op, "ok": ok, "gas": cost})
                else:
                    logs.append({"op": op.op, "ok": True, "skipped": True, "gas": cost})
            elif op.op == "crdt_put":
                box.state["keys"][op.args.get("key", "k")] = op.args.get("value")
                logs.append({"op": op.op, "ok": True, "gas": cost})
            elif op.op == "gcode_emit":
                lines = ["; shadow gcode", "G21", "G90"]
                n = int(op.args.get("n", 8))
                for i in range(min(n, 20)):
                    lines.append(f"G0 X{i} Y{i}")
                path = box.write_staged("candidate.gcode", "\n".join(lines))
                box.state["keys"]["gcode_lines"] = len(lines)
                box.state["keys"]["gcode_staged"] = path
                logs.append({"op": op.op, "ok": True, "gas": cost, "staged": True})
            elif op.op == "publish_bundle":
                box.state["published"] = True
                box.state["keys"]["channel"] = op.args.get("channel", "@adjjv")
                logs.append({"op": op.op, "ok": True, "shadow": verify_only, "gas": cost})
            elif op.op == "dag_submit":
                box.state["keys"]["dag"] = op.args
                logs.append({"op": op.op, "ok": True, "gas": cost})
            else:
                logs.append({"op": op.op, "ok": False, "error": "unknown"})
        delta = {
            "keys": dict(box.state["keys"]),
            "energy": box.state["energy"],
            "expr": box.state["expr"],
            "published": box.state["published"],
        }
        return {
            "delta": delta,
            "logs": logs,
            "gas_used": meter.used,
            "gas_remaining": meter.remaining(),
            "gas_budget": total_budget,
            "_sandbox": box,
        }
    except Exception:
        box.purge()
        raise


def delta_invariant_ok(delta: dict) -> Tuple[bool, str]:
    keys = delta.get("keys") or {}
    if len(keys) > POLICY_RULES["max_delta_keys"]:
        return False, "too_many_delta_keys"
    e = delta.get("energy")
    if e is not None:
        try:
            if abs(float(e)) > 1e12:
                return False, "energy_divergent"
        except Exception:
            return False, "energy_invalid"
    return True, "ok"


def two_phase_commit(ir: MeshIR, propose_raft: bool = True) -> dict:
    shadow = shadow_execute(ir, verify_only=True)
    box = shadow.pop("_sandbox", None)
    ok, reason = delta_invariant_ok(shadow["delta"])
    result = {
        "shadow": shadow,
        "invariant_ok": ok,
        "invariant_reason": reason,
        "raft": None,
    }
    if not ok:
        if box:
            box.purge()
        result["aborted"] = True
        return result
    if propose_raft:
        try:
            from swarm_merkle_crdt import MerkleCRDT

            m = MerkleCRDT("compiler-commit")
            durable = dict(shadow["delta"])
            keys = dict(durable.get("keys") or {})
            keys.pop("gcode_staged", None)
            durable["keys"] = keys
            m.put_register(f"delta:{int(time.time())}", durable)
            result["raft"] = {"mode": "local_merkle_commit", "root": m.root()}
        except Exception as e:
            result["raft"] = {"error": str(e)}
    if box:
        box.purge()
    result["aborted"] = False
    return result


def compile_intent(text: str) -> dict:
    ast = parse_intent_ast(text)
    ir = optimize_ir(lower_to_ir(ast, text))
    ok, errs = guard_ir(ir)
    if not ok:
        return {"ok": False, "errors": errs, "ir": ir.to_dict()}
    ir_dict = ir.to_dict()
    receipt = compile_receipt(ir_dict)
    v_ok, v_reason = verify_receipt(ir_dict, receipt)
    phase = two_phase_commit(ir, propose_raft=True)
    return {
        "ok": bool(v_ok and not phase.get("aborted")),
        "schema_version": SCHEMA_VERSION,
        "policy_hash": POLICY_HASH,
        "ast_kinds": [c.kind for c in ast.children],
        "ir": ir_dict,
        "receipt": receipt,
        "receipt_verified": v_ok,
        "receipt_reason": v_reason,
        "execution": phase,
    }


def negative_test_suite() -> dict:
    results: Dict[str, Any] = {}

    # Receipt forgery
    ir = optimize_ir(lower_to_ir(parse_intent_ast("simulate lattice"), "simulate lattice"))
    d = ir.to_dict()
    receipt = compile_receipt(d)
    forged = json.loads(json.dumps(d))
    forged["ops"][0]["args"]["n"] = 999
    ok, reason = verify_receipt(forged, receipt)
    results["receipt_forgery"] = {"dropped": not ok, "reason": reason}

    # Gas exhaustion
    try:
        meter = GasMeter(100)
        meter.charge(50, "a")
        meter.charge(60, "b")
        results["gas_exhaustion"] = {"trapped": False}
    except RuntimeError as e:
        results["gas_exhaustion"] = {"trapped": True, "error": str(e)}

    # Dynamic gas scales
    cost = dynamic_gas_cost("lattice_run", {"n": 64, "steps": 100})
    results["dynamic_gas"] = {
        "lattice_64_100": cost,
        "genetic_heavy": dynamic_gas_cost(
            "genetic_evolve", {"generations": 5, "population": 10}
        ),
    }

    # Invariant violation
    ok_i, reason_i = delta_invariant_ok({"keys": {}, "energy": 1e15})
    results["invariant_energy"] = {"rejected": not ok_i, "reason": reason_i}

    # Policy rotation grace
    old = POLICY_HASH
    rotate_policy({"note": "rotated_for_test"})
    ok_old, r_old = policy_acceptable(old)
    results["policy_grace"] = {
        "old_hash_accepted": ok_old,
        "reason": r_old,
        "drift_sec": MAX_POLICY_DRIFT_SEC,
    }

    # Shadow purge
    ir2 = optimize_ir(lower_to_ir(parse_intent_ast("fabricate gcode CNC"), "fabricate"))
    sh = shadow_execute(ir2)
    box = sh.pop("_sandbox", None)
    staged = (sh.get("delta") or {}).get("keys", {}).get("gcode_staged")
    exists_before = bool(staged and Path(staged).exists())
    if box:
        box.purge()
    exists_after = bool(staged and Path(staged).exists())
    results["shadow_purge"] = {
        "staged_during_run": exists_before,
        "purged_after": not exists_after,
    }

    return results


if __name__ == "__main__":
    intent = (
        "Simulate lattice N=16, evolve physics kernel, verify via ZK transcript, "
        "emit CNC gcode for load-bearing structure, and publish for @adjjv"
    )
    result = compile_intent(intent)
    print("=== compile_intent ===")
    print(
        json.dumps(
            {k: result[k] for k in result if k != "execution"},
            indent=2,
            default=str,
        )
    )
    ex = result.get("execution") or {}
    print("aborted", ex.get("aborted"), "gas", (ex.get("shadow") or {}).get("gas_used"))
    print("\n=== negative_test_suite ===")
    print(json.dumps(negative_test_suite(), indent=2, default=str))
