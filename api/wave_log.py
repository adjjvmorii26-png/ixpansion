"""Wave Log API — reconstruct evolution timeline from git history."""
from __future__ import annotations
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def get_wave_log():
    """Extract wave-related commits from git log."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "--all", "-100"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=10
        )
        lines = result.stdout.strip().splitlines()
    except Exception:
        lines = []

    waves = []
    other = []
    for line in lines:
        parts = line.split(" ", 1)
        if len(parts) < 2:
            continue
        sha = parts[0]
        msg = parts[1]
        if "wave" in msg.lower():
            # Extract wave number if present
            wave_num = ""
            for token in msg.split():
                if token.lower().startswith("wave"):
                    continue
                if token.isdigit():
                    wave_num = token
                    break
                if token.startswith("#"):
                    break
            waves.append({"sha": sha, "message": msg, "wave": wave_num})
        else:
            other.append({"sha": sha, "message": msg})

    # Also count files per subsystem
    subsystem_counts = {}
    for d in ["lab", "bridges", "constellation", "mycelium", "api", "dashboard"]:
        p = ROOT / d
        if p.exists():
            subsystem_counts[d] = len(list(p.rglob("*.py")))

    return {
        "waves": waves,
        "other_commits": other[:20],
        "wave_count": len(waves),
        "subsystem_file_counts": subsystem_counts,
        "total_commits": len(lines),
    }


def handler(request, response):
    return get_wave_log()


if __name__ == "__main__":
    print(json.dumps(handler(None, None), indent=2))
