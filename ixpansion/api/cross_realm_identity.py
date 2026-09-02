from __future__ import annotations
"""Cross-realm identity — gives modules metaphysical identities across fused repositories."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

_IDENTITY_PATH = Path(__file__).resolve().parent.parent / "data" / "cross_realm_identity.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Assign or query cross-realm module identity."""
    identity = _load_identity()
    if payload and "module" in payload and "realms" in payload:
        identity["modules"][payload["module"]] = {
            "realms": payload["realms"],
            "assigned_at": time.time(),
            "fusion_tag": payload.get("fusion_tag", f"wave_{payload.get('wave', 'unknown')}")
        }
        _save_identity(identity)
    # Return identity for a module if specified
    module_name = payload.get("module") if payload else None
    mod_identity = identity["modules"].get(module_name) if module_name and module_name in identity["modules"] else None
    return {"identity": mod_identity, "all_modules": list(identity["modules"].keys())}

def _load_identity() -> Dict[str, Any]:
    try:
        return json.load(open(_IDENTITY_PATH, encoding="utf-8"))
    except Exception:
        return {"modules": {}, "total_assigned": 0}

def _save_identity(identity: Dict[str, Any]) -> None:
    _IDENTITY_PATH.write_text(json.dumps(identity, indent=2, ensure_ascii=False))
