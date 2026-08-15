#!/usr/bin/env python3
"""Ephemeral process/OCI sandbox for untrusted genetic kernels."""
from __future__ import annotations
import json, os, shutil, subprocess, tempfile
from pathlib import Path
from ast_sandbox import validate_source

def docker_available() -> bool:
    return shutil.which("docker") is not None

def run_in_process_sandbox(source: str, timeout: float = 5.0) -> dict:
    ok, issues = validate_source(source)
    if not ok:
        return {"ok": False, "error": "ast_blocked", "issues": issues}
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "kernel.py"
        mod.write_text(source + "\n\nif __name__ == '__main__':\n import json\n print(json.dumps(run()))\n")
        try:
            proc = subprocess.run(
                ["python3", str(mod)],
                capture_output=True, text=True, timeout=timeout,
                env={"PATH": os.environ.get("PATH", ""), "HOME": td, "PYTHONDONTWRITEBYTECODE": "1"},
                cwd=td,
            )
            if proc.returncode != 0:
                return {"ok": False, "error": (proc.stderr or "")[:400], "code": proc.returncode}
            return {"ok": True, "result": json.loads(proc.stdout or "{}"), "backend": "subprocess"}
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout"}
        except Exception as e:
            return {"ok": False, "error": str(e)}

def run_in_docker_sandbox(source: str, timeout: float = 15.0) -> dict:
    if not docker_available():
        return run_in_process_sandbox(source, timeout=min(timeout, 5))
    ok, issues = validate_source(source)
    if not ok:
        return {"ok": False, "error": "ast_blocked", "issues": issues}
    with tempfile.TemporaryDirectory() as td:
        mod = Path(td) / "kernel.py"
        mod.write_text(source + "\n\nif __name__ == '__main__':\n import json\n print(json.dumps(run()))\n")
        cmd = [
            "docker", "run", "--rm", "--network", "none",
            "--memory", "128m", "--cpus", "0.5",
            "-v", f"{td}:/work:ro", "-w", "/work",
            "python:3.12-slim", "python", "kernel.py",
        ]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            if proc.returncode != 0:
                return {"ok": False, "error": (proc.stderr or "")[:400], "backend": "docker"}
            return {"ok": True, "result": json.loads(proc.stdout or "{}"), "backend": "docker"}
        except Exception as e:
            return {"ok": False, "error": str(e), "backend": "docker"}

if __name__ == "__main__":
    safe = "def run(**kwargs):\n    return {\"sum\": 2+2}\n"
    print(run_in_process_sandbox(safe))
    bad = "def run(**kwargs):\n    import os\n    os.system(\"echo x\")\n    return {}\n"
    print(run_in_process_sandbox(bad))
  
