"""Wave 516: Dependency Map — discover inter-module dependencies."""
from __future__ import annotations
import importlib, os, re, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    api_dir = os.path.join(os.path.dirname(__file__))
    module_set = set(KNOWN_LIVING_MODULES)
    deps = {}
    for name in KNOWN_LIVING_MODULES:
        fpath = os.path.join(api_dir, f"{name}.py")
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath) as f:
                content = f.read()
            imports = set()
            for m in re.finditer(r"from api\.(\w+)|import api\.(\w+)", content):
                dep = m.group(1) or m.group(2)
                if dep and dep != name and dep in module_set:
                    imports.add(dep)
            if imports:
                deps[name] = sorted(imports)
        except Exception:
            pass
    # Find most-connected modules
    inbound = {}
    for src, targets in deps.items():
        for t in targets:
            inbound.setdefault(t, []).append(src)
    hub_modules = sorted(inbound.items(), key=lambda x: len(x[1]), reverse=True)[:15]
    return {
        "action": "dependency_map",
        "total_modules": len(KNOWN_LIVING_MODULES),
        "modules_with_deps": len(deps),
        "hub_modules": [{"module": m, "depended_by": d} for m, d in hub_modules],
        "top_deps": {k: v for k, v in list(deps.items())[:20]},
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
