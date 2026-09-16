"""Wave 735 Antimeme Vaccine — detect modules that want to be forgotten."""
from __future__ import annotations
import json, math, time
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter

DATA = Path(__file__).parent.parent / "data"
API = Path(__file__).parent
STATE_FILE = DATA / "wave735_antimeme_vaccine.json"
DEFAULT = {"module": "wave735_antimeme_vaccine", "wave": 735, "scans": 0, "pinned": []}


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


def _name_entropy(s: str) -> float:
    if not s: return 0.0
    c = Counter(s)
    n = len(s)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def scan_antimemes(limit: int = 20) -> list:
    now = time.time()
    rows = []
    for p in sorted(API.glob("wave*.py")):
        try: age_days = max(0.01, (now - p.stat().st_mtime) / 86400.0)
        except OSError: age_days = 1.0
        ent = _name_entropy(p.stem)
        score = round(ent * math.log1p(age_days), 4)
        rows.append({"module": p.stem, "entropy": round(ent, 4), "age_days": round(age_days, 3), "antimeme_score": score})
    rows.sort(key=lambda r: -r["antimeme_score"])
    return rows[:limit]


def coherence_vitals():
    st = _load()
    return {"wave": 735, "module": "wave735_antimeme_vaccine", "ok": True,
            "scans": st.get("scans", 0), "pinned_n": len(st.get("pinned") or [])}


def resonates_with():
    return ["wave708_ouroboros", "wave702_import_quarantine"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "scan":
        rows = scan_antimemes(int(req.get("limit") or 15))
        st["scans"] = int(st.get("scans") or 0) + 1
        st["last_top"] = rows[0]["module"] if rows else None
        st["ts"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "scanned", "antimemes": rows, **coherence_vitals()}
    if action == "pin":
        name = str(req.get("module") or "")[:80]
        pinned = st.setdefault("pinned", [])
        if name and name not in pinned:
            pinned.append(name)
            st["pinned"] = pinned[-64:]
            _save(st)
        return {"status": "pinned", "pinned": st.get("pinned"), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "scan"}), indent=2))
