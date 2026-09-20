"""Wave 773 — ci_sentinel_bridge.

Maps AEGIS-style contract checks into a lightweight merge-readiness score
for lab PRs (organism gates > external scanner noise).

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave773_ci_sentinel_bridge.json"
WAVE = 773
NAME = "ci_sentinel_bridge"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "scans": 0,
    "last_score": None,
    "last_posture": "unknown",
    "status": "idle",
}


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


def _contract_checks() -> list:
    checks = []

    def ok(label: str, passed: bool, weight: float = 1.0, detail: str = "") -> None:
        checks.append({"check": label, "ok": bool(passed), "weight": weight, "detail": detail})

    ok("repo_root", ROOT.exists(), 1.0, str(ROOT))
    ok("api_dir", (ROOT / "api").is_dir(), 1.2)
    ok("tests_dir", (ROOT / "tests").is_dir(), 1.0)
    ok("github_workflows", (ROOT / ".github" / "workflows").is_dir(), 1.0)
    ok(
        "dual_track_doctrine",
        (ROOT / "docs" / "DUAL_TRACK.md").exists() or (ROOT / "docs" / "GITHUB_STATUS.md").exists(),
        0.8,
    )
    ok("council_module", (ROOT / "lab" / "ops" / "copilots" / "council.py").is_file(), 1.5)
    ok("lab_council_pulse_workflow", (ROOT / ".github" / "workflows" / "lab-council-pulse.yml").is_file(), 1.0)
    ok("chaos_monkey_workflow", (ROOT / ".github" / "workflows" / "chaos-monkey.yml").is_file(), 0.6)
    ok("wave770_present", (ROOT / "api" / "wave770_copilot_council_pulse.py").is_file(), 0.5)
    ok("wave771_present", (ROOT / "api" / "wave771_caption_pipeline_bridge.py").is_file(), 0.5)
    return checks


def _score(checks: list) -> tuple:
    total_w = sum(c["weight"] for c in checks) or 1.0
    earned = sum(c["weight"] for c in checks if c["ok"])
    ratio = earned / total_w
    if ratio >= 0.92:
        posture = "green"
    elif ratio >= 0.7:
        posture = "amber"
    else:
        posture = "red"
    return round(ratio, 4), posture


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave773_ci_sentinel_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "scans": int(st.get("scans") or 0),
        "last_score": st.get("last_score"),
        "last_posture": st.get("last_posture", "unknown"),
        "resonance": round(min(1.0, 0.54 + int(st.get("scans") or 0) * 0.008), 4),
        "surface": "silence",
        "gate_policy": "organism_over_ghas_noise",
    }


def resonates_with() -> list:
    return [
        "wave770_copilot_council_pulse",
        "wave772_afterimage_well",
        "lab.ops.copilots.aegis",
        "wave768_hush_compass",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "surface": "silence", "audio": False}

    if action == "scan":
        checks = _contract_checks()
        score, posture = _score(checks)
        failed = [c["check"] for c in checks if not c["ok"]]
        st["scans"] = int(st.get("scans") or 0) + 1
        st["last_score"] = score
        st["last_posture"] = posture
        st["status"] = "scanned"
        st["last_ts"] = _now()
        _save(st)
        advice = (
            "Merge lab PRs when organism gates green; ignore GHAS-only noise"
            if posture == "green"
            else ("Repair failed contracts before merge" if failed else "Hold")
        )
        return {
            **coherence_vitals(),
            "status": "scanned",
            "score": score,
            "posture": posture,
            "failed": failed,
            "advice": advice,
            "checks": checks,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        score = st.get("last_score")
        posture = st.get("last_posture") or "unknown"
        n = int(st.get("scans") or 0)
        cap = f"sentinel {posture}" + (f" · {score}" if score is not None else "") + f" · scans {n}"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": cap,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "scan"}), indent=2))
