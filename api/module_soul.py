"""Wave 516: Module Soul — the identity and personality of each module."""
from __future__ import annotations
import importlib, os, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    payload = payload or {}
    module_name = payload.get("module", "")
    if not module_name:
        return {"action": "module_soul", "hint": "Use ?module=<name> to read a module's soul"}
    try:
        mod = importlib.import_module(f"api.{module_name}")
        doc = mod.__doc__ or "No documentation."
        funcs = [name for name in dir(mod) if callable(getattr(mod, name)) and not name.startswith("_")]
        has_handler = hasattr(mod, "handler")
        source_lines = 0
        try:
            fpath = os.path.join(os.path.dirname(mod.__file__), f"{module_name}.py")
            with open(fpath) as f:
                source_lines = len(f.readlines())
        except Exception:
            pass
        return {
            "action": "module_soul",
            "module": module_name,
            "docstring": doc[:500],
            "has_handler": has_handler,
            "functions": funcs[:20],
            "source_lines": source_lines,
            "time": time.time(),
            "vitals": coherence_vitals(),
        }
    except Exception as e:
        return {"action": "module_soul", "error": f"Module {module_name} not found: {e}"}
