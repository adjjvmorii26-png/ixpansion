#!/usr/bin/env python3
"""Quick health of refined IXPANSION stack."""
from __future__ import annotations
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

def main():
    report = {"ok": True, "checks": []}
    def check(name, fn):
        try:
            detail = fn()
            report["checks"].append({"name": name, "ok": True, "detail": detail})
        except Exception as e:
            report["ok"] = False
            report["checks"].append({"name": name, "ok": False, "error": e.__class__.__name__, "msg": str(e)[:120]})

    def version():
        return Path("VERSION").read_text().strip()

    def mesh():
        from mesh_core import IXPANSIONMesh
        m = IXPANSIONMesh(2)
        return {"leader": m.leader_id, "nodes": len(m.nodes)}

    def workforce():
        from workforce_pipeline import WorkforcePipeline
        from vectra_hitl_gate import WorkforceTask
        r = WorkforcePipeline().submit(WorkforceTask(
            task_id="refine_probe", task_type="CODE_EXECUTION",
            agent_id="forge_agent", trust_score=0.9,
            payload={"avg_latency_ms": 40},
        ))
        return r.get("status")

    def lumen():
        from lumen_constellation import LumenProjector
        c = LumenProjector(1).project({"a": 0.9, "b": 0.5})
        return {"galaxy": c.name, "sig": c.signature}

    def sandbox():
        from sandbox.run_module import run_module
        r = run_module("idea_lab", "refine pass")
        return {"gens": r.get("generations"), "fitness": r.get("fitness")}

    def nexus_ui():
        p = Path("mesh_public/index.html")
        t = p.read_text()
        assert "IXPANSION" in t and "Worker" in t
        return {"bytes": p.stat().st_size}

    def vivarium():
        p = Path("mesh_public/vivarium.html")
        assert p.exists()
        return {"bytes": p.stat().st_size}

    for n, f in [
        ("version", version), ("mesh", mesh), ("workforce", workforce),
        ("lumen", lumen), ("sandbox_idea_lab", sandbox),
        ("nexus_ui", nexus_ui), ("vivarium_ui", vivarium),
    ]:
        check(n, f)

    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
