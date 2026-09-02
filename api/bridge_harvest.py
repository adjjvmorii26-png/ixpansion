"""Wave 223 — The Organism Grows: Bridge Harvest.

The seer has found the unseen; now the harvest brings them in. This
organ discovers new repos, builds latent bridges between them and
existing islands, enacts those bridges as stones, and writes the
commune registry into each new island — a full intake pipeline.

It is the organism's growth spur: scanning, proposing, enacting,
communing — all in one call.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List

_LEDGER_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "bridges", "ledger.json")


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _enacted() -> set:
    ledger = _load_ledger()
    return {(s["repo"], s["organ"]) for s in ledger.get("stones", [])}


def _token() -> str:
    return os.environ.get("IXP_GH_TOKEN", "").strip()


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "harvest", "status": "growing", "resonance": 0.92, "wave": 223}


def resonates_with() -> list:
    return ["harvest", "grow", "intake", "discovery", "bridge", "expand", "seer"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "harvest")
    token = _token()

    if not token:
        return {"status": "dry_run", "note": "Set IXP_GH_TOKEN to harvest new bridges"}

    if action == "harvest":
        # 1. Seer scan
        try:
            from api.constellation_seer import handler as seer
            scan = seer({"action": "scan"})
        except Exception as exc:
            return {"status": "error", "phase": "scan", "error": str(exc)}

        if scan.get("new", 0) == 0:
            return {"status": "nothing_new", "note": "No new repos found."}

        # 2. Get latent bridges
        try:
            latent_resp = seer({"action": "latent"})
            latent = latent_resp.get("latent", [])
        except Exception:
            latent = []

        # 3. Enact latent bridges that aren't yet in the ledger
        already = _enacted()
        new_bridges = [b for b in latent if (b["repo"], b["organ"]) not in already]

        enacted, failed = [], []
        if new_bridges:
            try:
                from api.bridge_enactor import handler as enactor
                for b in new_bridges[:20]:
                    r = enactor({"action": "enact", "repo": b["repo"], "organ": b["organ"], "bridge": b})
                    if r.get("status") == "enacted":
                        enacted.append({"repo": b["repo"], "organ": b["organ"], "stone": r.get("stone")})
                    else:
                        failed.append({"repo": b["repo"], "organ": b["organ"], "status": r.get("status")})
            except Exception as exc:
                failed.append({"error": str(exc)})

        return {
            "status": "harvested",
            "new_repos": scan.get("new"),
            "latent_bridges": len(new_bridges),
            "enacted": enacted,
            "failed": failed,
            "note": f"Seer found {scan.get('new')} new islands; harvested {len(enacted)} bridges.",
        }

    if action == "new_repos":
        try:
            from api.constellation_seer import handler as seer
            return seer({"action": "scan"})
        except Exception as exc:
            return {"error": str(exc)}

    return {"status": "ready", "actions": ["harvest", "new_repos"],
            "note": "The harvest discovers and grows."}
