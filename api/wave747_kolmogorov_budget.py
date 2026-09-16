"""Wave 747 Kolmogorov Budget — zlib compressibility proxy for module novelty."""
from __future__ import annotations
import json, zlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
API = Path(__file__).parent
STATE_FILE = DATA / "wave747_kolmogorov_budget.json"
DEFAULT = {"module": "wave747_kolmogorov_budget", "wave": 747, "scans": 0}


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


def complexity_ratio(text: str) -> float:
    raw = text.encode("utf-8", errors="ignore")
    if not raw: return 0.0
    norm = " ".join(text.split()).encode("utf-8")
    if not norm: return 0.0
    c = zlib.compress(norm, level=9)
    return round(len(c) / len(norm), 4)


def scan_modules(limit: int = 20) -> list:
    rows = []
    for p in sorted(API.glob("wave*.py"))[:80]:
        try: text = p.read_text(encoding="utf-8", errors="ignore")
        except OSError: continue
        rows.append({"module": p.stem, "ratio": complexity_ratio(text), "bytes": len(text)})
    rows.sort(key=lambda x: -x["ratio"])
    return rows[:limit]


def coherence_vitals():
    st = _load()
    return {"wave": 747, "module": "wave747_kolmogorov_budget", "ok": True, "scans": st.get("scans", 0)}


def resonates_with():
    return ["wave735_antimeme_vaccine", "wave737_paradox_debt_ledger", "wave703_proof_delta"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "scan":
        rows = scan_modules(int(req.get("limit") or 15))
        st["scans"] = int(st.get("scans") or 0) + 1
        st["top"] = rows[0]["module"] if rows else None
        st["ts"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "scanned", "ranking": rows, **coherence_vitals()}
    if action == "score":
        return {"status": "scored", "ratio": complexity_ratio(str(req.get("text") or "")), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "scan", "limit": 5}), indent=2))
