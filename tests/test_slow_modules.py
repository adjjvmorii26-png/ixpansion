from __future__ import annotations
"""Slow module tests — constellation and telemetry scan the full filesystem."""
import sys
import os
import subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def _run_slow(func):
    """Run slow function in subprocess to avoid pytest timeout."""
    mod = func.__module__
    name = func.__name__
    result = subprocess.run(
        ['python3', '-c', f'import sys; sys.path.insert(0, "."); from {mod} import {name}; r = {name}(); import json; print(json.dumps({{"ok": True, "keys": list(r.keys()) if isinstance(r, dict) else len(r)}}))'],
        capture_output=True, text=True, timeout=30, cwd=str(os.path.join(os.path.dirname(__file__), ".."))
    )
    return result

def test_constellation():
    result = _run_slow(__import__('api.constellation', fromlist=['build_constellation']).build_constellation)
    assert result.returncode == 0
    assert "ok" in result.stdout

def test_telemetry():
    result = _run_slow(__import__('api.telemetry', fromlist=['collect_telemetry']).collect_telemetry)
    assert result.returncode == 0
    assert "ok" in result.stdout

def test_constellation_handler():
    result = subprocess.run(
        ['python3', '-c', 'import sys; sys.path.insert(0, "."); from api.constellation import handler; r = handler({}, {}); import json; print(json.dumps(list(r.keys())))'],
        capture_output=True, text=True, timeout=30,
        cwd=str(os.path.join(os.path.dirname(__file__), ".."))
    )
    assert result.returncode == 0

def test_telemetry_handler():
    result = subprocess.run(
        ['python3', '-c', 'import sys; sys.path.insert(0, "."); from api.telemetry import handler; r = handler({}, {}); import json; print(json.dumps(list(r.keys())))'],
        capture_output=True, text=True, timeout=30,
        cwd=str(os.path.join(os.path.dirname(__file__), ".."))
    )
    assert result.returncode == 0
