#!/usr/bin/env python3
"""
Task Verifiability Layer (ZKP-ready)
Lightweight commitments + execution transcripts.
Full zk-SNARK wiring can replace prove/verify later without API change.
"""
from __future__ import annotations
import hashlib
import json
import time
from typing import Any, Dict, Optional, Tuple


def _h(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def commit(payload: dict) -> str:
    return _h(json.dumps(payload, sort_keys=True, default=str).encode())


class ExecutionTranscript:
    """Records constrained steps for later audit / SNARK circuit."""

    def __init__(self, task_id: str, constraint: str):
        self.task_id = task_id
        self.constraint = constraint  # e.g. AST policy id, kernel expr
        self.steps: list = []
        self.started = time.time()

    def step(self, name: str, data: Any):
        entry = {
            "name": name,
            "data_commit": commit({"d": data} if not isinstance(data, dict) else data),
            "t": time.time() - self.started,
        }
        self.steps.append(entry)

    def finalize(self, result: dict) -> dict:
        body = {
            "task_id": self.task_id,
            "constraint": self.constraint,
            "steps": self.steps,
            "result_commit": commit(result),
            "result": result,
        }
        body["proof"] = {
            "type": "transcript_v1",  # upgrade path: "groth16" | "plonk"
            "root": commit({k: body[k] for k in ("task_id", "constraint", "steps", "result_commit")}),
            "note": "Replace with zk-SNARK proving key output for trustless verify",
        }
        return body


def verify_transcript(proof_bundle: dict, expected_constraint: Optional[str] = None) -> Tuple[bool, str]:
    if proof_bundle.get("proof", {}).get("type") not in ("transcript_v1", "groth16", "plonk"):
        return False, "unknown_proof_type"
    if expected_constraint and proof_bundle.get("constraint") != expected_constraint:
        return False, "constraint_mismatch"
    # recompute root
    body = {k: proof_bundle[k] for k in ("task_id", "constraint", "steps", "result_commit") if k in proof_bundle}
    root = commit(body)
    if root != proof_bundle.get("proof", {}).get("root"):
        return False, "root_mismatch"
    if commit(proof_bundle.get("result", {})) != proof_bundle.get("result_commit"):
        return False, "result_tamper"
    return True, "ok"


def prove_lattice_run(task_id: str, params: dict, result: dict) -> dict:
    tr = ExecutionTranscript(task_id, constraint=f"lattice:{params}")
    tr.step("params", params)
    tr.step("engine", result.get("engine"))
    tr.step("final_energy", result.get("final_energy"))
    return tr.finalize(result)


if __name__ == "__main__":
    from swarm_wasm_lattice import run_wasm_lattice
    params = {"n": 8, "steps": 10, "seed": 0.2}
    result = run_wasm_lattice(**params)
    bundle = prove_lattice_run("t1", params, result)
    ok, reason = verify_transcript(bundle)
    print("verify", ok, reason, "root", bundle["proof"]["root"][:16])
    # tamper
    bundle["result"]["final_energy"] = 999
    ok2, reason2 = verify_transcript(bundle)
    print("tampered", ok2, reason2)
  
