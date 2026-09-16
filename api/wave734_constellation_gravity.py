"""Wave 734 Constellation Gravity — repos as mass; tasks fall toward dense clusters."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave734_constellation_gravity.json"

CONSTELLATION = {
    "ixpansion": {"mass": 10.0, "tokens": ["agent", "wave", "consciousness", "entropy", "mesh"]},
    "interstice": {"mass": 6.0, "tokens": ["bridge", "portal", "gap", "between"]},
    "pentaxis-5d-engine": {"mass": 7.0, "tokens": ["5d", "space", "time", "mind", "meta", "game"]},
    "oracle-engine": {"mass": 5.0, "tokens": ["oracle", "consensus", "research", "perspective"]},
    "chronocrypt-orrery": {"mass": 5.0, "tokens": ["time", "cycle", "meridian", "gyre", "temporal"]},
    "luminant-reliquary": {"mass": 4.0, "tokens": ["crystal", "light", "memory", "prism", "ember"]},
    "antimemetic-architecton": {"mass": 5.0, "tokens": ["absence", "erase", "null", "paradox", "forget"]},
    "phaseshift-manifold": {"mass": 4.0, "tokens": ["phase", "solid", "liquid", "plasma", "matter"]},
    "polychron-atlas": {"mass": 4.0, "tokens": ["map", "paradox", "glyph", "atlas", "temporal"]},
    "echotide-engine": {"mass": 4.0, "tokens": ["tide", "wave", "reef", "abyss", "crest"]},
    "astral-forge": {"mass": 5.0, "tokens": ["forge", "lattice", "crystal", "choir", "agent"]},
    "nexus-observatory": {"mass": 6.0, "tokens": ["meta", "observe", "resonance", "consensus"]},
    "solid-organism": {"mass": 5.0, "tokens": ["pulse", "phoenix", "fractal", "lattice"]},
    "feature-1.3-mesh-hitl-si": {"mass": 3.0, "tokens": ["mesh", "human", "defense", "hitl"]},
}
DEFAULT = {"module": "wave734_constellation_gravity", "wave": 734, "pulls": 0}


def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass


def _tokens(text: str):
    return set(t.lower() for t in text.replace("-", " ").replace("_", " ").split() if t)


def gravity_pull(query: str) -> list:
    q = _tokens(query) or {"wave"}
    ranked = []
    for name, body in CONSTELLATION.items():
        overlap = len(q & set(body["tokens"]))
        force = body["mass"] * ((1 + overlap) ** 2)
        ranked.append({"repo": name, "force": round(force, 3), "overlap": overlap, "mass": body["mass"]})
    ranked.sort(key=lambda x: -x["force"])
    return ranked


def coherence_vitals():
    st = _load()
    return {"wave": 734, "module": "wave734_constellation_gravity", "ok": True,
            "bodies": len(CONSTELLATION), "pulls": st.get("pulls", 0)}


def resonates_with():
    return ["wave722_interstice_bridge", "wave721_coherence_bridge", "wave733_skill_builder"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "pull":
        q = str(req.get("query") or req.get("task") or "agent mesh wave")
        ranked = gravity_pull(q)
        st["pulls"] = int(st.get("pulls") or 0) + 1
        st["last_query"] = q
        st["last_top"] = ranked[0]["repo"] if ranked else None
        st["ts"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "pulled", "query": q, "ranking": ranked[:8], **coherence_vitals()}
    if action == "bodies":
        return {"status": "bodies", "constellation": list(CONSTELLATION.keys()), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "pull", "query": "temporal paradox crystal memory"}), indent=2))
