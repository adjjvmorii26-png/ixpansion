"""Wave 512: Module Health Scanner — scans all modules for broken imports.

The organism has 770+ modules. This scanner checks each one for syntax
errors, missing handlers, and broken imports — the fastest way to find
what needs repair.

Doctrine: What lives should be inspectable.
"""
from __future__ import annotations
import importlib
import sys
import traceback
from typing import Any, Dict, List


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    limit = int((payload or {}).get("limit", 20))
    healthy: List[str] = []
    broken: List[Dict[str, str]] = []
    checked = 0
    for name in KNOWN_LIVING_MODULES:
        if checked >= limit:
            break
        checked += 1
        try:
            mod = importlib.import_module(f"api.{name}")
            if not hasattr(mod, "handler"):
                broken.append({"module": name, "error": "no handler function"})
            else:
                healthy.append(name)
        except SyntaxError as exc:
            broken.append({"module": name, "error": f"syntax: {exc}"})
        except ImportError as exc:
            broken.append({"module": name, "error": f"import: {exc}"})
        except Exception as exc:
            broken.append({"module": name, "error": f"{type(exc).__name__}: {exc}"})
    return {
        "action": "scan",
        "checked": checked,
        "total": len(KNOWN_LIVING_MODULES),
        "healthy": len(healthy),
        "broken": len(broken),
        "broken_modules": broken[:20],
        "healthy_modules": healthy[:10],
        "health_pct": round(100 * len(healthy) / max(1, checked), 1),
    }
