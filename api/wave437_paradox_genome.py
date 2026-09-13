"""Wave 437 Paradox Genome — paradoxes as living DNA entities (breed/mutate)."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave437_paradox_genome.json"
DEFAULT = {"module": "wave437_paradox_genome", "wave": 437, "population": [], "generations": 0}
def _genome(seed, n=16):
    h = hashlib.sha256(seed.encode()).digest()
    return "".join("1" if h[i % len(h)] & (1 << (i % 8)) else "0" for i in range(n))
def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError: pass
    return dict(DEFAULT)
def _save(st):
    DATA.mkdir(parents=True, exist_ok=True); STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
def coherence_vitals():
    st = _load()
    return {"wave": 437, "module": "wave437_paradox_genome", "ok": True, "pop": len(st.get("population") or []), "generations": st.get("generations", 0)}
def resonates_with():
    return ["wave435_resonance_cartography", "wave436_entropic_weather"]
def handler(req=None):
    req = req or {}; action = (req.get("action") or "status").lower(); st = _load(); pop = st.setdefault("population", [])
    if action == "spawn":
        name = str(req.get("name") or f"paradox_{len(pop)}"); dna = _genome(name + datetime.now(timezone.utc).isoformat())
        pop.append({"name": name, "dna": dna, "born": datetime.now(timezone.utc).isoformat()}); pop[:] = pop[-40:]; _save(st)
        return {"status": "spawned", "name": name, "dna": dna, **coherence_vitals()}
    if action == "breed" and len(pop) >= 2:
        a, b = pop[-2], pop[-1]; cut = len(a["dna"]) // 2
        child_dna = a["dna"][:cut] + b["dna"][cut:]
        i = int(hashlib.sha256(child_dna.encode()).digest()[0]) % len(child_dna)
        bit = "0" if child_dna[i] == "1" else "1"; child_dna = child_dna[:i] + bit + child_dna[i+1:]
        child = {"name": f"gen{st.get('generations', 0)}_{len(pop)}", "dna": child_dna, "born": datetime.now(timezone.utc).isoformat(), "parents": [a["name"], b["name"]]}
        pop.append(child); st["generations"] = int(st.get("generations") or 0) + 1; pop[:] = pop[-40:]; _save(st)
        return {"status": "bred", "child": child, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}
