"""Wave 736 Silent Broadcast Lattice — cross-repo caption relay without audio APIs."""
from __future__ import annotations
import json, time
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
ROOT = Path(__file__).parent.parent
BROADCAST = ROOT / "content_output" / "broadcast"
STATE_FILE = DATA / "wave736_silent_broadcast_lattice.json"
DEFAULT = {"module": "wave736_silent_broadcast_lattice", "wave": 736, "emits": 0}


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


def emit(target: str, lines: list, *, channel: str = "@CoodingLooop") -> dict:
    BROADCAST.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in target)[:48]
    frames = [{"t": i * 2, "text": str(line)[:120]} for i, line in enumerate(lines[:12])]
    package = {
        "target_repo": target, "channel": channel, "style": "silent_caption_only",
        "frames": frames, "ts": datetime.now(timezone.utc).isoformat(),
    }
    path = BROADCAST / f"{safe}_{int(time.time())}.json"
    path.write_text(json.dumps(package, indent=2) + "\n")
    return {"path": str(path.relative_to(ROOT)), "frames": len(frames), "target": target}


def coherence_vitals():
    st = _load()
    return {"wave": 736, "module": "wave736_silent_broadcast_lattice", "ok": True, "emits": st.get("emits", 0)}


def resonates_with():
    return ["wave710_dream_choir", "wave707_ix_kernel", "wave734_constellation_gravity"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "emit":
        target = str(req.get("target") or req.get("repo") or "ixpansion")
        lines = req.get("lines") or req.get("frames")
        if isinstance(lines, str): lines = [lines]
        if not lines: lines = ["SILENT LATTICE", target, "@CoodingLooop"]
        result = emit(target, list(lines))
        st["emits"] = int(st.get("emits") or 0) + 1
        st["last_target"] = target
        st["last_path"] = result.get("path")
        _save(st)
        return {"status": "emitted", **result, **coherence_vitals()}
    if action == "list":
        BROADCAST.mkdir(parents=True, exist_ok=True)
        files = sorted(BROADCAST.glob("*.json"))[-20:]
        return {"status": "list", "files": [str(f.relative_to(ROOT)) for f in files], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "emit", "target": "interstice", "lines": ["BRIDGE OPEN", "silent lattice"]}), indent=2))
