from __future__ import annotations
"""Network harmony — tracks harmony states across all fused repositories."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_NETWORK_HARMONY_PATH = Path(__file__).resolve().parent.parent / "data" / "network_harmony.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Record network harmony across fused repos."""
    state = _load_state()
    if payload and "repo_harmonies" in payload:
        # Merge repo harmonies into network state
        for repo, harmony in payload["repo_harmonies"].items():
            state["repos"][repo] = harmony
        
        # Calculate network-wide metrics
        state["network_average"] = _calculate_network_average(state["repos"])
        state["network_peak"] = _calculate_network_peak(state["repos"])
        state["last_updated"] = time.time()
        _save_state(state)
    return {"network_average": state.get("network_average"), "network_peak": state.get("network_peak"), "repos_tracked": len(state.get("repos", {}))}

def _calculate_network_average(repos: Dict[str, Any]) -> float:
    """Calculate average harmony across all repos."""
    if not repos:
        return 0.0
    scores = []
    for repo, harmony in repos.items():
        if isinstance(harmony, dict) and "harmony_score" in harmony:
            scores.append(harmony["harmony_score"])
    return round(sum(scores) / len(scores), 4) if scores else 0.0

def _calculate_network_peak(repos: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate peak harmony repo."""
    best_repo = None
    best_score = -1
    for repo, harmony in repos.items():
        if isinstance(harmony, dict) and "harmony_score" in harmony:
            if harmony["harmony_score"] > best_score:
                best_score = harmony["harmony_score"]
                best_repo = repo
    return {"repo": best_repo, "score": best_score if best_repo else 0}

def _load_state() -> Dict[str, Any]:
    try:
        return json.load(open(_NETWORK_HARMONY_PATH, encoding="utf-8"))
    except Exception:
        return {"repos": {}, "network_average": 0.0, "network_peak": {"repo": None, "score": 0}, "last_updated": None}

def _save_state(state: Dict[str, Any]) -> None:
    _NETWORK_HARMONY_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False))
