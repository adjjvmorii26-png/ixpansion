"""Wave 763 — silence_capacitor.

Silence is the product surface. Unsaid pulses accumulate as charge;
compression folds them into memory tokens; discharge emits a caption
only — never audio. Lab gates stay off the ALEPH CI path.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
STATE_FILE = DATA / "wave763_silence_capacitor.json"
WAVE = 763
NAME = "silence_capacitor"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "holds": [],
    "tokens": [],
    "captions": [],
    "charge": 0.0,
    "status": "quiet",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st: dict) -> None:
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


def _compress(text: str) -> str:
    """Compression is memory: fold utterance into a short token."""
    words = [w for w in text.split() if w]
    if not words:
        return "·"
    head = words[0][:12]
    digest = hashlib.sha256(text.encode()).hexdigest()[:8]
    return f"{head}·{len(words)}·{digest}"


def coherence_vitals() -> dict:
    st = _load()
    charge = float(st.get("charge") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave763_silence_capacitor",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "quiet"),
        "resonance": round(min(1.0, 0.42 + charge * 0.08), 4),
        "holds": len(st.get("holds") or []),
        "tokens": len(st.get("tokens") or []),
        "captions": len(st.get("captions") or []),
        "charge": charge,
    }


def resonates_with() -> list:
    return [
        "wave736_silent_broadcast_lattice",
        "wave762_dream_compiler",
        "wave672_root_archive",
        "wave674_dawn_ledger",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()
    holds = st.setdefault("holds", [])
    tokens = st.setdefault("tokens", [])
    captions = st.setdefault("captions", [])

    if action == "status":
        return {"status": "quiet", **coherence_vitals()}

    if action == "hold":
        text = str(req.get("text") or req.get("pulse") or "")[:280]
        if not text.strip():
            return {"status": "empty", **coherence_vitals()}
        hid = hashlib.sha256(f"{text}:{_now()}".encode()).hexdigest()[:12]
        holds.append({"id": hid, "text": text, "ts": _now()})
        holds[:] = holds[-64:]
        st["charge"] = round(float(st.get("charge") or 0) + 0.15, 4)
        st["status"] = "holding"
        _save(st)
        return {"status": "held", "id": hid, "charge": st["charge"], **coherence_vitals()}

    if action == "compress":
        if not holds:
            return {"status": "nothing_to_fold", **coherence_vitals()}
        batch = holds[-4:]
        folded = []
        for item in batch:
            token = _compress(item.get("text") or "")
            tid = hashlib.sha256(token.encode()).hexdigest()[:12]
            folded.append({"id": tid, "token": token, "source": item.get("id"), "ts": _now()})
        tokens.extend(folded)
        tokens[:] = tokens[-48:]
        used = {i.get("id") for i in batch}
        holds[:] = [h for h in holds if h.get("id") not in used]
        st["charge"] = max(0.0, round(float(st.get("charge") or 0) * 0.6, 4))
        st["status"] = "compressed"
        _save(st)
        return {
            "status": "compressed",
            "folded": len(folded),
            "tokens": [f["token"] for f in folded],
            **coherence_vitals(),
        }

    if action == "discharge":
        if not tokens:
            return {"status": "silence", "caption": "", **coherence_vitals()}
        last = tokens[-1]
        caption = last.get("token") or ""
        captions.append({"caption": caption, "token_id": last.get("id"), "ts": _now()})
        captions[:] = captions[-24:]
        tokens[:] = tokens[:-1]
        st["charge"] = max(0.0, round(float(st.get("charge") or 0) - 0.1, 4))
        st["status"] = "quiet"
        _save(st)
        return {
            "status": "discharged",
            "caption": caption,
            "audio": False,
            **coherence_vitals(),
        }

    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
