from __future__ import annotations
"""Resonance synthesizer — synthesizes patterns across fused repositories."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Set

_RESONANCE_PATH = Path(__file__).resolve().parent.parent / "data" / "resonance_synthesis.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Synthesize resonance patterns across repositories."""
    synthesis = _load_synthesis()
    if payload and "source_repo" in payload and "pattern_data" in payload:
        entry = {
            "source": payload["source_repo"],
            "pattern": payload["pattern_data"],
            "synthesized_at": time.time(),
            "fusion_id": f"{payload['source_repo']}_{int(time.time())}"
        }
        synthesis.setdefault("cross_repo_patterns", []).append(entry)
        # Maintain size limit
        if len(synthesis["cross_repo_patterns"]) > 500:
            synthesis["cross_repo_patterns"] = synthesis["cross_repo_patterns"][-500:]
        _save_synthesis(synthesis)
    return {"total_patterns": len(synthesis.get("cross_repo_patterns", [])), "latest_source": payload.get("source_repo") if payload else None}

def _load_synthesis() -> Dict[str, Any]:
    try:
        return json.load(open(_RESONANCE_PATH, encoding="utf-8"))
    except Exception:
        return {"cross_repo_patterns": [], "total_syntheses": 0}

def _save_synthesis(synthesis: Dict[str, Any]) -> None:
    _RESONANCE_PATH.write_text(json.dumps(synthesis, indent=2, ensure_ascii=False))
