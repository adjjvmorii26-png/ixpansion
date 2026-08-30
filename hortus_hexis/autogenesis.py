"""Autogenesis — the garden commits to the repo.

Every organism must pass its own newborn test before it is allowed
into the repo. If the gate opens, the garden plants the module,
the test, and the specimen in one commit.

The garden NEVER evaluates generated source. It writes template
files, runs the newborn test in a subprocess, and only then stages
the exact files it wrote.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
from typing import Dict, Optional

from .artifacts import safe_name, transcribe

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: list, cwd: Path = ROOT, timeout: int = 180) -> Dict:
    try:
        proc = subprocess.run(cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout)
        return {"returncode": proc.returncode, "stdout": proc.stdout[-1200:], "stderr": proc.stderr[-1200:]}
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "timeout"}
    except FileNotFoundError:
        return {"returncode": -2, "stdout": "", "stderr": "subprocess unavailable"}


def grow_and_gate(name: str, seed: str, words: str, stats: Dict,
                  commit: bool = True, verbose: bool = True,
                  parents: Optional[List[str]] = None) -> Dict:
    """Transcribe, gate, and (optionally) commit an organism."""
    name = safe_name(name)
    paths = transcribe(name, seed, words, stats, checked=0, parents=parents)
    module, test = Path(paths["module"]), Path(paths["test"])

    result: Dict = {
        "name": name, "paths": paths, "gate": "closed", "commit": None, "log": [],
    }

    gate = _run([sys.executable, "-m", "pytest", str(test), "-q", "-p", "no:cacheprovider"])
    if gate["returncode"] != 0:
        if verbose:
            print(f"  gate CLOSED for {name} — not planted:")
            print("  " + (gate["stderr"] or gate["stdout"]).strip().splitlines()[-3:][0] if (gate["stderr"] or gate["stdout"]).strip() else "")
        result["gate"] = "closed"
        return result

    specimen = json.loads(Path(paths["specimen"]).read_text())
    specimen["checked"] = 1
    Path(paths["specimen"]).write_text(json.dumps(specimen, indent=2))
    result["gate"] = "open"
    if verbose:
        print(f"  gate OPEN — {name} passed \u2713")

    if not commit:
        return result

    reg = ROOT / "hortus_hexis" / "registry.json"
    if not reg.exists():
        reg.write_text("[]\n")
    paths_to_stage = [paths["module"], paths["test"], paths["specimen"], str(reg)]
    cmds = [
        ["git", "add", *paths_to_stage],
        ["git", "commit", "-m", f"hortus: grow {name} from seed {seed[:10]}… (vitality {specimen['stats'].get('vitality', '?')})"],
    ]
    for cmd in cmds:
        rc = _run(cmd)
        result["log"].append({"cmd": cmd, "returncode": rc["returncode"], "out": rc["stdout"][-200:], "err": rc["stderr"][-300:]})
        if rc["returncode"] != 0:
            return result

    def _last_commit() -> Optional[str]:
        r = _run(["git", "rev-parse", "--short", "HEAD"])
        return (r.get("stdout") or "").strip() or None

    result["commit"] = _last_commit()
    if verbose:
        print(f"  planted as {result['commit']} ✔")
    return result
