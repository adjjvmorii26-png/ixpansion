"""Wave 787 — dual_track_pr_bot.

Classify changed paths as lab vs ALEPH (or mixed) so PR labels stay dual-track clean.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave787_dual_track_pr_bot.json"
WAVE = 787
NAME = "dual_track_pr_bot"

LAB_PREFIXES = (
    "lab/",
    "api/wave",
    "tests/test_wave",
    "dashboard/",
    "scripts/ix_",
    ".vscode/",
    ".devcontainer/",
)
CORE_PREFIXES = (
    ".github/workflows/",
    "requirements",
    "pyproject",
    "Makefile",
)

DEFAULT = {"wave": WAVE, "name": NAME, "classifications": 0, "status": "idle"}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                return raw
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


def _bucket(path: str) -> str:
    p = path.replace("\\", "/").lstrip("./")
    if any(p.startswith(x) or x.rstrip("/") in p for x in LAB_PREFIXES):
        return "lab"
    if any(p.startswith(x) for x in CORE_PREFIXES):
        return "core"
    return "aleph"


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave787_dual_track_pr_bot",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "classifications": int(st.get("classifications") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("classifications") or 0) * 0.01), 4),
        "surface": "silence",
        "labels": ["lab", "aleph", "core", "mixed"],
    }


def resonates_with() -> list:
    return [
        "wave776_merge_readiness_score",
        "wave773_ci_sentinel_bridge",
        "wave779_phaseshift_router",
        "wave770_copilot_council_pulse",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "classify":
        files = req.get("files") or req.get("paths") or []
        if isinstance(files, str):
            files = [files]
        files = [str(f) for f in files[:200]]
        buckets = {"lab": [], "aleph": [], "core": []}
        for f in files:
            b = _bucket(f)
            buckets[b].append(f)
        n_lab, n_aleph, n_core = len(buckets["lab"]), len(buckets["aleph"]), len(buckets["core"])
        if n_lab and not n_aleph and not n_core:
            track, label = "lab", "track:lab"
        elif n_aleph and not n_lab:
            track, label = "aleph", "track:aleph"
        elif n_core and not n_lab and not n_aleph:
            track, label = "core", "track:core"
        else:
            track, label = "mixed", "track:mixed"
        advice = {
            "lab": "Prefer path-filtered lab CI; keep ALEPH main unblocked",
            "aleph": "Full monorepo gates; seal carefully",
            "core": "CI/tooling — dual review",
            "mixed": "Split PR or accept longer ALEPH leg",
        }[track]
        st["classifications"] = int(st.get("classifications") or 0) + 1
        st["status"] = "classified"
        st["last_track"] = track
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "classified",
            "track": track,
            "label": label,
            "counts": {"lab": n_lab, "aleph": n_aleph, "core": n_core},
            "advice": advice,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("classifications") or 0)
        t = st.get("last_track") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"track bot {n} · last {t}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "classify", "files": ["api/wave780_x.py", "lab/ops/x.py"]}), indent=2))
