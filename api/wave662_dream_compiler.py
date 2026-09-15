"""Wave 662 — Dream Compiler v2.

Compile dream residues into executable organ specs:
- Distill raw dream residue into motifs
- Compile motifs into executable organ blueprints
- Manifest compiled organs
"""
import json, time
from pathlib import Path
STATE = Path("data/wave662_dream_compiler.json")
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"residues": [], "organs": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "residues": len(s["residues"]), "organs": len(s["organs"])}
def _distill(residue="shimmer", source="unconscious"):
    s = _load(); s["tick"] += 1
    motif = {"residue": residue, "source": source, "tick": s["tick"], "time": time.time()}
    s["residues"].append(motif); s["residues"] = s["residues"][-500:]
    _save(s); return {"ok": True, "motif": motif}
def _compile(name=None, actions=None):
    s = _load(); s["tick"] += 1
    if not s["residues"]: return {"ok": False, "error": "no dream residues to compile"}
    residue = s["residues"][-1]["residue"]
    organ = {"name": name or f"dream_organ_{s['tick']}", "from_residue": residue, "actions": actions or ["sense", "dream", "seal"], "status": "compiled", "time": time.time()}
    s["organs"].append(organ); s["organs"] = s["organs"][-200:]
    _save(s); return {"ok": True, "organ": organ}
def _manifest():
    s = _load(); return {"ok": True, "organs": s["organs"][-20:]}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "distill": return _distill(req.get("residue", "shimmer"), req.get("source", "unconscious"))
    elif action == "compile": return _compile(req.get("name"), req.get("actions"))
    elif action == "manifest": return _manifest()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 662, "residues": len(s["residues"]), "organs": len(s["organs"])}
def resonates_with(): return ["wave663_resonance_ledger", "wave665_mycelial_network", "wave444_dream_synthesis"]
