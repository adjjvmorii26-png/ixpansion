"""Anomaly Detector API — scan for code anomalies, dead code, and inconsistencies."""
from __future__ import annotations
import json
import sys
import re
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def scan_anomalies():
    """Scan the codebase for common anomalies."""
    anomalies = []
    warnings = []

    for py in ROOT.rglob("*.py"):
        rel = str(py.relative_to(ROOT))
        # Skip hidden/cache dirs
        if any(part.startswith(".") for part in py.parts):
            continue
        if "__pycache__" in str(py) or "backup" in rel:
            continue

        try:
            text = py.read_text(errors="replace")
        except Exception:
            continue

        lines = text.splitlines()

        # Check 1: bare except
        for i, ln in enumerate(lines, 1):
            if re.match(r"\s*except\s*:", ln):
                anomalies.append({
                    "type": "bare_except",
                    "file": rel,
                    "line": i,
                    "severity": "warning",
                    "detail": "Bare except clause — catches all exceptions including SystemExit",
                })

        # Check 2: print() in non-main/non-test code
        if "test_" not in py.name and py.name != "conftest.py":
            for i, ln in enumerate(lines, 1):
                stripped = ln.strip()
                if stripped.startswith("print(") and not stripped.startswith("#"):
                    if "if __name__" not in lines[max(0, i-5):i]:
                        warnings.append({
                            "type": "print_in_library",
                            "file": rel,
                            "line": i,
                        })

        # Check 3: TODO/FIXME/HACK
        for i, ln in enumerate(lines, 1):
            upper = ln.upper()
            if "TODO" in upper or "FIXME" in upper or "HACK" in upper:
                warnings.append({
                    "type": "todo_marker",
                    "file": rel,
                    "line": i,
                    "text": ln.strip()[:100],
                })

        # Check 4: very long functions (>100 lines)
        func_start = None
        func_name = None
        indent_level = 0
        for i, ln in enumerate(lines, 1):
            if re.match(r"    def \w+", ln) and func_start is None:
                func_start = i
                func_name = ln.strip().split("(")[0].replace("def ", "")
                indent_level = len(ln) - len(ln.lstrip())
            elif func_start and (not ln.strip() or (ln.strip() and len(ln) - len(ln.lstrip()) <= indent_level)):
                if ln.strip() and not ln.strip().startswith("#"):
                    func_len = i - func_start
                    if func_len > 100:
                        anomalies.append({
                            "type": "long_function",
                            "file": rel,
                            "function": func_name,
                            "start_line": func_start,
                            "length": func_len,
                            "severity": "info",
                        })
                    func_start = None
                    func_name = None

        # Check 5: duplicate imports
        imports = [ln.strip() for ln in lines if ln.strip().startswith(("import ", "from "))]
        seen_imports = set()
        for imp in imports:
            if imp in seen_imports:
                anomalies.append({
                    "type": "duplicate_import",
                    "file": rel,
                    "detail": imp[:100],
                    "severity": "warning",
                })
            seen_imports.add(imp)

    # Score
    anomaly_count = len(anomalies)
    warning_count = len(warnings)
    score = max(0, 100 - anomaly_count * 2 - warning_count)

    return {
        "anomalies": anomalies[:50],
        "warnings": warnings[:50],
        "summary": {
            "anomaly_count": anomaly_count,
            "warning_count": warning_count,
            "health_score": score,
        },
        "signature": hashlib.sha256(f"{anomaly_count}:{warning_count}".encode()).hexdigest()[:12],
    }


def handler(request, response):
    return scan_anomalies()


if __name__ == "__main__":
    result = handler(None, None)
    print(json.dumps(result, indent=2))


def coherence_vitals() -> dict:
    """anomaly_detector reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "anomaly_detector_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['pattern_recognizer', 'universal_compass', 'thought_meteorology']

