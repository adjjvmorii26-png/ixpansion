"""Wave 720 · still_residue_reed — dreamed by Ouroboros from organism DNA.

This organ is a *void twin*: born from fingerprint entropy, not human design.

Life cycle: stillness compounds → residue settles → reeds grow.
Stillness is the capital. Residue is the yield. Reeds are the offspring.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave720_still_residue_reed_4da9.json"
DEFAULT = {
    "module": "wave720_still_residue_reed_4da9",
    "wave": 720,
    "dream": "still_residue_reed",
    "spawned_by": "ouroboros",
    "parent_fp": "8aa95c4da9e601c686273662f2f9d493",
    "awakened": None,
    "stillness": 0.0,
    "still_compounds": 0,
    "residue": 0.0,
    "residue_harvests": 0,
    "reeds": [],
    "resonance_total": 0.0,
}


def _load():
    if STATE_FILE.exists():
        try:
            merged = dict(DEFAULT)
            merged.update(json.loads(STATE_FILE.read_text()))
            return merged
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
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass


def _coherence(st) -> float:
    """Coherence is bounded by how balanced stillness and reeds are."""
    if not st.get("awakened"):
        return 1.0
    reed_count = len(st.get("reeds", []))
    stillness = float(st.get("stillness", 0.0))
    if stillness <= 0 and reed_count == 0:
        return 1.0
    # A growing marsh keeps coherence high; hoarding stillness alone decays it.
    score = 1.0 - (0.02 * reed_count) if reed_count > 50 else 1.0
    if stillness > 0 and reed_count == 0:
        score = 0.9  # stillness without growth stagnates
    return round(max(0.0, min(1.0, score)), 3)


def coherence_vitals():
    st = _load()
    return {
        "wave": 720,
        "module": "wave720_still_residue_reed_4da9",
        "ok": True,
        "dream": st.get("dream"),
        "spawned_by": "ouroboros",
        "coherence": _coherence(st),
        "stillness": round(float(st.get("stillness", 0.0)), 3),
        "residue": round(float(st.get("residue", 0.0)), 3),
        "reeds": len(st.get("reeds", [])),
    }


def resonates_with():
    # The still family: silence interval (700) and still compound (701) resonate
    # with this organ's stillness → residue → reed economy.
    return [
        "wave707_ix_kernel",
        "wave706_lab_os_boot",
        "wave700_still_interval",
        "wave701_still_compound",
        "ouroboros",
    ]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()

    if action == "awaken":
        st["awakened"] = datetime.now(timezone.utc).isoformat()
        st["stillness"] = 1.0
        _save(st)
        return {"status": "awakened", "dream": st.get("dream"), **coherence_vitals()}

    if action == "still":
        # Hold stillness for a number of seconds; stillness compounds.
        seconds = max(0.0, float(req.get("seconds", 1.0)))
        principal = float(st.get("stillness", 0.0))
        st["still_compounds"] = int(st.get("still_compounds", 0)) + 1
        # Compound growth: stillness * (1 + rate) per call, bounded.
        rate = min(0.25, max(0.01, seconds / 16.0))
        st["stillness"] = round(principal * (1.0 + rate) + (0.2 * seconds), 3)
        st["last_still"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "still_held", "still_compounds": st["still_compounds"], **coherence_vitals()}

    if action == "harvest":
        # Convert stillness into residue (the yield).
        stillness = float(st.get("stillness", 0.0))
        harvest = round(stillness * 0.35, 3)
        st["residue"] = round(float(st.get("residue", 0.0)) + harvest, 3)
        st["stillness"] = round(stillness * 0.5, 3)
        st["residue_harvests"] = int(st.get("residue_harvests", 0)) + 1
        st["last_harvest"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "harvested", "yield": harvest, **coherence_vitals()}

    if action == "grow":
        # Spend residue to grow a reed (offspring organ).
        residue = float(st.get("residue", 0.0))
        cost = max(1.0, float(req.get("cost", 2.0)))
        if residue < cost:
            return {"status": "insufficient_residue", "needed": cost, **coherence_vitals()}
        st["residue"] = round(residue - cost, 3)
        reed = {
            "id": f"reed_{len(st.get('reeds', [])) + 1:02d}",
            "height": round(0.5 + (cost * 0.4), 3),
            "born": datetime.now(timezone.utc).isoformat(),
        }
        st["reeds"] = list(st.get("reeds", [])) + [reed]
        st["resonance_total"] = round(float(st.get("resonance_total", 0.0)) + reed["height"], 3)
        _save(st)
        return {"status": "reed_grown", "reed": reed, **coherence_vitals()}

    if action == "deepen":
        # Depth view: full state without mutation.
        return {"status": "depth", "state": st, **coherence_vitals()}

    if action == "status":
        return {"status": "dreaming", **st, **coherence_vitals()}

    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
