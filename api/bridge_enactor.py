"""Wave 217 — The Organism Enacts: Bridge Enactor.

Turns interstice proposals into REAL connections: writes a "bridge
stone" — a small, hex-sealed marker file — into the paired
constellation repo, so the organism's bridges physically exist on
the archipelago instead of only in the map.

Production runs dry by default (proposes); a live run happens when
a GitHub token is present in the environment and force=enact.
The ledger of enacted bridges is served by api/bridge_ledger.py.
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

_OWNER = "adjjvmorii26-png"
_STONE_DIR = "ixpansion-bridges"
_LEDGER_PATH = "data/bridges/ledger.json"


def _stone_id(repo: str, organ: str) -> str:
    return "BRIDGE-" + hashlib.sha256(f"{repo}::{organ}".encode()).hexdigest()[:8].upper()


def _seal(payload: Dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def _bridge_lines(bridge: Dict[str, Any], stone_id: str, enacted_at: str) -> List[str]:
    repo, organ = bridge["repo"], bridge["organ"]
    return [
        "# Bridge Stone",
        "",
        f"- **bridge:** `{stone_id}`",
        f"- **from:** IXpansion → `{repo}` :: `{organ}`",
        f"- **resonance:** {bridge.get('resonance', 0.0)}",
        f"- **layer:** {bridge.get('organ_layer', 'unknown')}",
        f"- **wave:** 217 (The Organism Enacts)",
        f"- **enacted:** {enacted_at}",
        f"- **seal:** `{_seal(bridge)}`",
        f"- **return path:** https://ixpansion.vercel.app/api/bridge_enactor",
        "",
        f"`{organ}` and `{repo}` were once separate islands. This stone marks",
        "the first plank of the bridge between them. The organism intends",
        "to keep building here.",
        "",
    ]


def _load_ledger() -> Dict[str, Any]:
    try:
        with open(_LEDGER_PATH, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {"stones": [], "count": 0}


def _save_ledger(ledger: Dict[str, Any]) -> bool:
    try:
        os.makedirs(os.path.dirname(_LEDGER_PATH), exist_ok=True)
        with open(_LEDGER_PATH, "w", encoding="utf-8") as fh:
            json.dump(ledger, fh, indent=2, sort_keys=True)
        return True
    except Exception:
        return False


def _github_write(token: str, repo: str, path: str, content: str, message: str) -> Optional[int]:
    """Create/update a file in a repo via the contents API. Returns status code."""
    url = f"https://api.github.com/repos/{_OWNER}/{repo}/contents/{path}"
    body = json.dumps({
        "message": message,
        "content": __import__("base64").b64encode(content.encode()).decode(),
    }).encode("utf-8")
    req = Request(url, data=body, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.status
    except Exception as exc:
        return getattr(exc, "code", None) or -1


def _top_bridges() -> List[Dict[str, Any]]:
    try:
        from api.interstice_bridge import _INTERSTICE_MAP
        return list(_INTERSTICE_MAP["top_bridges"])
    except Exception:
        return []


def _generate_stone(bridge: Dict[str, Any], enacted_at: str) -> Dict[str, Any]:
    stone_id = _stone_id(bridge["repo"], bridge["organ"])
    return {
        "stone": stone_id,
        "repo": bridge["repo"],
        "organ": bridge["organ"],
        "resonance": bridge.get("resonance", 0.0),
        "layer": bridge.get("organ_layer", "unknown"),
        "wave": 217,
        "enacted_at": enacted_at,
        "seal": _seal(bridge),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "bridge-enactment", "status": "weaving", "resonance": 0.88, "wave": 217}


def resonates_with() -> list:
    return ["bridge", "enact", "stone", "cross-repo", "github", "interstice", "knot", "constellation"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "plan")
    token = os.environ.get("IXP_GH_TOKEN", "").strip()
    force = payload.get("force") == "enact" or token and payload.get("force")
    bridges = _top_bridges()
    enacted_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    if action == "plan":
        ledger = _load_ledger()
        done = {s["stone"] for s in ledger.get("stones", [])}
        plan = []
        for b in bridges:
            plan.append({
                "bridge": b,
                "stone": _stone_id(b["repo"], b["organ"]),
                "would_write": f"{_OWNER}/{b['repo']}/contents/{_STONE_DIR}/{b['organ']}.json",
                "already_enacted": _stone_id(b["repo"], b["organ"]) in done,
            })
        return {
            "status": "planned",
            "total": len(plan),
            "token_present": bool(token),
            "plan": plan,
        }

    if action == "ledger":
        return _load_ledger()

    if action == "enact":
        repo = payload.get("repo")
        organ = payload.get("organ")
        if not repo or not organ:
            return {"status": "error", "error": "repo and organ required"}
        bridge = payload.get("bridge")
        if not bridge:
            bridge = next((b for b in bridges if b["repo"] == repo and b["organ"] == organ), None)
        if not bridge:
            return {"status": "not_found"}
        stone_id = _stone_id(repo, organ)
        ledger = _load_ledger()
        if any(s["stone"] == stone_id for s in ledger.get("stones", [])):
            return {"status": "already_enacted", "stone": stone_id}
        if not token:
            return {
                "status": "proposed",
                "stone": stone_id,
                "note": "Dry run: pass IXP_GH_TOKEN in the environment to actually lay the stone.",
            }
        stone = _generate_stone(bridge, enacted_at)
        lines = _bridge_lines(bridge, stone_id, enacted_at)
        lines.append("```hex")
        lines.append(stone["seal"])
        lines.append("```")
        path = f"{_STONE_DIR}/{organ}.json"
        status = _github_write(token, repo, path, json.dumps(stone, indent=2), f"lay bridge stone {stone_id}")
        if status not in (200, 201):
            return {"status": "failed", "stone": stone_id, "http": status}
        ledger["stones"].append(stone)
        ledger["count"] = len(ledger["stones"])
        saved = _save_ledger(ledger)
        return {
            "status": "enacted",
            "stone": stone_id,
            "path": f"{_OWNER}/{repo}/contents/{path}",
            "ledger_saved": saved,
        }

    return {
        "status": "active",
        "wave": 217,
        "actions": ["plan", "enact", "ledger"],
        "note": "The organism lays stones across the archipelago.",
    }
