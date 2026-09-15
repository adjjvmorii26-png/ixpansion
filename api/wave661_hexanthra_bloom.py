"""Wave 661 — Hexanthra Bloom.

The hex language grows itself (HEXANTHRA):
- Bloom new vocabulary tokens from stems
- Compose new opcodes from existing primitives
- Ritual creation and language census
"""
import json, time
from pathlib import Path
STATE = Path("data/wave661_hexanthra_bloom.json")
ROOTS = ["MORPH", "ECHO", "VEIL", "THREAD", "EMBER", "TIDE"]
PRIMITIVES = ["PUSH", "POP", "JMP", "ENACT", "MERGE", "FORGE", "DREAM", "SEAL"]
def _load():
    if STATE.exists(): return json.loads(STATE.read_text())
    return {"tokens": [], "opcodes": [], "rituals": [], "tick": 0}
def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True); STATE.write_text(json.dumps(s, indent=2))
def _status():
    s = _load(); return {"ok": True, "tick": s["tick"], "tokens": len(s["tokens"]), "opcodes": len(s["opcodes"]), "rituals": len(s["rituals"])}
def _bloom(stem=None, meaning="new growth"):
    s = _load(); s["tick"] += 1
    stem = stem or ROOTS[s["tick"] % len(ROOTS)]
    token = {"stem": stem, "meaning": meaning, "born": s["tick"], "time": time.time()}
    s["tokens"].append(token); s["tokens"] = s["tokens"][-500:]
    _save(s); return {"ok": True, "token": token}
def _compose(op=""):
    s = _load(); s["tick"] += 1
    opcode = op or f"{PRIMITIVES[s['tick'] % len(PRIMITIVES)]}_{PRIMITIVES[(s['tick'] + 1) % len(PRIMITIVES)]}"
    rec = {"opcode": opcode, "from": op or f"{PRIMITIVES[s['tick'] % len(PRIMITIVES)]}+{PRIMITIVES[(s['tick'] + 1) % len(PRIMITIVES)]}", "time": time.time()}
    s["opcodes"].append(rec); s["opcodes"] = s["opcodes"][-500:]
    _save(s); return {"ok": True, "opcode": rec}
def _ritual(name="awakening", steps=None):
    s = _load(); s["tick"] += 1
    ritual = {"name": name, "steps": steps or ["SEAL", "FORGE", "ENACT"], "time": time.time()}
    s["rituals"].append(ritual); s["rituals"] = s["rituals"][-200:]
    _save(s); return {"ok": True, "ritual": ritual}
def _census():
    s = _load()
    return {"ok": True, "tokens": len(s["tokens"]), "opcodes": len(s["opcodes"]), "rituals": len(s["rituals"]), "primitives": PRIMITIVES}
def handler(req):
    action = req.get("action", "status")
    if action == "status": return _status()
    elif action == "bloom": return _bloom(req.get("stem"), req.get("meaning", "new growth"))
    elif action == "compose": return _compose(req.get("op"))
    elif action == "ritual": return _ritual(req.get("name", "awakening"), req.get("steps"))
    elif action == "census": return _census()
    return {"ok": False, "error": f"Unknown action: {action}"}
def coherence_vitals():
    s = _load(); return {"wave": 661, "tokens": len(s["tokens"]), "opcodes": len(s["opcodes"]), "rituals": len(s["rituals"])}
def resonates_with(): return ["wave660_lineage_crystal", "wave96_hex_grammar_evolution", "wave97_hex_runtime"]
