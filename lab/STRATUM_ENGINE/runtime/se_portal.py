#!/usr/bin/env python3
"""STRATUM_ENGINE portal."""
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SE = ROOT.parent
LAYERS = {
    "foundation": [SE / "FOUNDATION_LAYER" / "core_algorithms" / "state_estimator.py", SE / "FOUNDATION_LAYER" / "safety_guards" / "constraint_engine.py"],
    "adaptive": [SE / "ADAPTIVE_LAYER" / "pattern_recognition" / "anomaly_detector.py", SE / "ADAPTIVE_LAYER" / "optimization_loops" / "adaptive_optimizer.py"],
    "emergent": [SE / "EMERGENT_LAYER" / "synthesis_engine" / "synthesis_core.py", SE / "EMERGENT_LAYER" / "decision_maker" / "decision_engine.py"],
    "interface": [SE / "INTERFACE_LAYER" / "api_gateway" / "gateway.py", SE / "INTERFACE_LAYER" / "ingestion_pipelines" / "ingest_satellite.py"],
}
def main() -> int:
    act = (sys.argv[1] if len(sys.argv) > 1 else "help").lower()
    if act in ("help", "-h", "--help"):
        print(json.dumps({"acts": ["foundation", "adaptive", "emergent", "interface", "pipeline", "boot", "ethics"]}, indent=2))
        return 0
    if act == "ethics":
        g = subprocess.run([sys.executable, str(SE / "FOUNDATION_LAYER" / "safety_guards" / "constraint_engine.py")], capture_output=True, text=True)
        data = json.loads(g.stdout or "{}")
        print(json.dumps({"ok": data.get("ok", False), "mandatory": True, "guard": data}, indent=2))
        return 0 if data.get("ok") else 1
    if act == "pipeline":
        r = subprocess.run([sys.executable, str(ROOT / "pipeline.py")] + sys.argv[2:], capture_output=True, text=True)
        print(r.stdout or r.stderr)
        return r.returncode
    if act in LAYERS:
        results, ok = [], True
        for script in LAYERS[act]:
            r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
            results.append({"script": script.name, "ok": r.returncode == 0})
            ok &= r.returncode == 0
        print(json.dumps({"layer": act, "ok": ok, "results": results}, indent=2))
        return 0 if ok else 1
    if act == "boot":
        steps, ok = [], True
        for name in ("ethics", "foundation", "adaptive", "emergent", "pipeline"):
            r = subprocess.run([sys.executable, str(ROOT / "se_portal.py"), name], capture_output=True, text=True)
            steps.append({"step": name, "ok": r.returncode == 0})
            ok &= r.returncode == 0
        print(json.dumps({"boot": True, "ok": ok, "steps": steps}, indent=2))
        return 0 if ok else 1
    print(json.dumps({"ok": False, "err": "unknown"}))
    return 1
if __name__ == "__main__":
    raise SystemExit(main())
