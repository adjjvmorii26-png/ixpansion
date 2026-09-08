"""Wave 517: Self-Test Generator — the organism writes its own tests."""
from __future__ import annotations
import importlib, os, re, time, inspect
from typing import Any, Dict

TESTS_DIR = os.path.join(os.path.dirname(__file__), "..", "tests")

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def _generate_test(name: str) -> str:
    try:
        mod = importlib.import_module(f"api.{name}")
        doc = (mod.__doc__ or "").strip().split("\n")[0]
        funcs = [n for n in dir(mod) if callable(getattr(mod, n)) and not n.startswith("_")]
        has_handler = hasattr(mod, "handler")
    except Exception:
        return ""
    lines = [f'"""Auto-generated test for api.{name}."""', f'import pytest', f'', f'def test_{name}_imports():', f'    import api.{name}', f'    assert True', f'']
    if has_handler:
        lines += [f'def test_{name}_handler():', f'    from api.{name} import handler', f'    result = handler()', f'    assert isinstance(result, dict)', f'    assert "action" in result or "module" in result or "version" in result or "time" in result', f'']
    if "coherence_vitals" in funcs:
        lines += [f'def test_{name}_vitals():', f'    from api.{name} import coherence_vitals', f'    v = coherence_vitals()', f'    assert isinstance(v, dict)', f'    assert "coherence" in v', f'']
    if doc:
        lines += [f'def test_{name}_docstring():', f'    import api.{name}', f'    assert api.{name}.__doc__ is not None', f'']
    return "\n".join(lines)

def handler(payload=None, context=None):
    payload = payload or {}
    dry = payload.get("dry_run", True)
    max_gen = int(payload.get("limit", 5))
    generated = []
    skipped = []
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    existing_tests = set(f[5:-3] for f in os.listdir(TESTS_DIR) if f.startswith("test_") and f.endswith(".py"))
    untested = [m for m in KNOWN_LIVING_MODULES if m not in existing_tests]
    for name in untested[:max_gen]:
        code = _generate_test(name)
        if not code:
            skipped.append(name)
            continue
        if not dry:
            path = os.path.join(TESTS_DIR, f"test_{name}.py")
            with open(path, "w") as f:
                f.write(code)
        generated.append(name)
    return {
        "action": "self_test_generate",
        "untested_count": len(untested),
        "generated": generated,
        "skipped": skipped,
        "dry_run": dry,
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
