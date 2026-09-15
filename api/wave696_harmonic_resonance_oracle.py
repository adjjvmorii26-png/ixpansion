"""Wave 696 Harmonic Resonance Oracle — detects and amplifies resonance patterns
across the organism's modules.

Each module emits a resonance frequency. The oracle maps constructive and
destructive interference patterns to predict emergent behaviors.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave696_harmonic_resonance_oracle.json"
DEFAULT = {
    "module": "wave696_harmonic_resonance_oracle",
    "wave": 696,
    "resonances": {},
    "interference_patterns": [],
    "constructive": 0,
    "destructive": 0,
    "harmony_score": 0.0,
    "total_scan": 0,
}


def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def coherence_vitals():
    st = _load()
    return {
        "wave": 696,
        "module": "wave696_harmonic_resonance_oracle",
        "ok": True,
        "harmony_score": st["harmony_score"],
        "constructive": st["constructive"],
        "destructive": st["destructive"],
        "total_scan": st["total_scan"],
    }


def resonates_with():
    return ["wave694_quantum_coherence_lattice", "wave695_memory_palace_reanimation", "wave697_neural_syntax_bridge"]


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "scan":
        modules = req.get("modules", [])
        if not modules:
            modules = ["organism_core", "wave_core"]
        for m in modules:
            freq = hashlib.sha256(m.encode()).hexdigest()[:8]
            resonance_val = (int(freq, 16) % 100) / 100.0
            st["resonances"][m] = {
                "frequency": freq,
                "resonance": resonance_val,
                "phase": "constructive" if resonance_val > 0.5 else "destructive",
            }
        st["total_scan"] += 1
        st["constructive"] = sum(1 for r in st["resonances"].values() if r["phase"] == "constructive")
        st["destructive"] = sum(1 for r in st["resonances"].values() if r["phase"] == "destructive")
        total = len(st["resonances"]) or 1
        st["harmony_score"] = round(st["constructive"] / total, 4)
        pattern = {
            "modules": len(modules),
            "constructive": st["constructive"],
            "destructive": st["destructive"],
            "harmony": st["harmony_score"],
            "scanned_at": datetime.now(timezone.utc).isoformat(),
        }
        st["interference_patterns"].append(pattern)
        _save(st)
        return {"status": "scanned", "modules": len(modules), "harmony_score": st["harmony_score"], "pattern": pattern, "wave": 696}

    if action == "resonance":
        module = req.get("module", "")
        r = st["resonances"].get(module)
        if not r:
            return {"status": "error", "message": f"module {module} not scanned"}
        return {"status": "resonance", "module": module, **r, "wave": 696}

    if action == "patterns":
        return {"status": "patterns", "count": len(st["interference_patterns"]), "patterns": st["interference_patterns"][-5:], "wave": 696}

    if action == "status":
        return {
            "status": "active",
            "module": "wave696_harmonic_resonance_oracle",
            "wave": 696,
            "harmony_score": st["harmony_score"],
            "constructive": st["constructive"],
            "destructive": st["destructive"],
            "total_scan": st["total_scan"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    import json as _j
    print(_j.dumps(handler({"action": "status"}), indent=2))
