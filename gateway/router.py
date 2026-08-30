"""IXpansion Gateway Router — auth + intent → module dispatch.

This is the public interface. A client sends a natural-language query
with an API key; the router validates the key (tier-based rate limits),
matches intent, checks the route's access against the key's tier, and
returns the response from the live frontier.

    POST /gateway
    {
      "api_key": "ixp_free_...",
      "query": "what's the frontier's heartbeat?"
      // optional: "route": "/health"  (bypass intent, direct route)
    }
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

from gateway import keys as keys_mod
from gateway.intent import match_intent

# Routes that _call() handles directly (not via /api/).
_DIRECT_ROUTES = frozenset({
    "health", "modules", "metrics", "", "dashboard", "oracle",
    "echo", "revelations", "gateway", "intent", "meter",
    "ledger", "forecast", "capsule", "song", "poem", "garden",
})


def _dispatch(route: str, params: Optional[dict] = None) -> Tuple[Dict[str, Any], int]:
    """Dispatch an already-authorized route against the live frontier."""
    params = params or {}
    try:
        from api.index import _call
    except Exception:
        _call = None

    if _call is not None:
        strip = route.lstrip("/").split("?")[0]
        # If the route is handled explicitly by _call, dispatch directly.
        # Otherwise, proxy through /api/<module> for the unified router.
        if strip in _DIRECT_ROUTES:
            path = route
            if "q" in params:
                path = route + f"?q={params['q']}"
            if params.get("origin"):
                path = route + f"?origin={params['origin']}"
            result = _call("GET", path)
            return result, 200
        else:
            # Proxy through /api/<module>
            api_path = f"/api/{strip}"
            if "q" in params:
                api_path += f"?q={params['q']}"
            result = _call("GET", api_path)
            return result, 200

    return {"error": "dispatch backend unavailable", "route": route}, 503


def _route_allowed(route: str) -> str:
    """Map a dispatched route to the module name used for tier checks."""
    strip = route.lstrip("/").split("?")[0]
    # Explicit tier check names for known routes
    module_map = {
        "echo": "echo",
        "health": "health",
        "modules": "modules",
        "poem": "poem",
        "intent": "intent",
        "meter": "meter",
        "forecast": "forecast",
        "garden": "garden",
        "ledger": "ledger",
        "gossip_uptime": "gossip_uptime",
        "data_complexity": "data_complexity",
        "platform_failure": "platform_failure",
        "service_numinous": "service_numinous",
        "temperament_origin": "temperament_origin",
        "revelations": "revelations",
        "capsule": "capsule",
        "song": "song",
        "api/frontier_stream": "frontier_stream",
        "frontier_stream": "frontier_stream",
        "api/hex_tool": "hex_tool",
        "hex_tool": "hex_tool",
        "api/constellation_cartographer": "constellation_cartographer",
        "constellation_cartographer": "constellation_cartographer",
    }
    return module_map.get(strip, strip)


def handle(payload: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
    """Main gateway entry: validate key, match intent, dispatch."""
    api_key = payload.get("api_key", payload.get("key", ""))
    query = payload.get("query", "")
    explicit_route = payload.get("route")

    # signup: generate a new key
    if payload.get("signup") or payload.get("signup"):
        owner = payload.get("signup", "") or payload.get("owner", "anonymous")
        tier = payload.get("tier", "free")
        try:
            new_key = keys_mod.generate_key(owner, tier)
            return {
                "message": f"key generated for {owner} ({tier} tier)",
                "key": new_key["key"],
                "tier": tier,
                "limits": new_key["limits"],
                "hint": "Save this key — it is only shown once"
            }, 201
        except ValueError as e:
            return {"error": str(e)}, 400

    # 1. validate the key
    if not api_key:
        return {"error": "missing api_key; get one at /gateway/signup"}, 401
    key_data = keys_mod.validate_key(api_key)
    if not key_data:
        return {"error": "invalid api_key"}, 401

    tier = key_data.get("tier", "free")

    # 2. determine the target route
    if explicit_route:
        route = explicit_route if explicit_route.startswith("/") else "/" + explicit_route
        params = {}
    elif query:
        matched = match_intent(query)
        route = matched.get("route", "/health")
        params = {"q": matched["q"]} if matched.get("q") else {}
    else:
        return {"error": "provide a query or route"}, 400

    # 3. check tier access to this route
    module_name = _route_allowed(route)
    if not keys_mod.can_access(key_data, module_name):
        return {
            "error": f"tier '{tier}' lacks access to {module_name}",
            "route": route,
            "upgrade": "upgrade to growth or enterprise (see /gateway/pricing)",
        }, 403

    # 4. dispatch
    result, status = _dispatch(route, params)
    meta = {
        "route": route,
        "tier": tier,
        "owner": key_data.get("owner"),
        "echo_count": key_data.get("total_calls", 0),
        "remaining_daily": key_data.get("limits", {}).get("daily", 0) - key_data.get("daily_calls", 0),
    }
    if isinstance(result, dict):
        result["gateway"] = meta
    return result, status


def render_public(payload: Dict[str, Any]) -> Dict[str, Any]:
    result, status = handle(payload)
    result["http_status"] = status
    return result


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="IXpansion Gateway")
    ap.add_argument("--signup", help="owner name to create a free key")
    ap.add_argument("--route", help="explicit route to call")
    ap.add_argument("--key", help="api key (or set IXPANSION_KEY env)")
    ap.add_argument("--list", action="store_true", help="list all keys (admin)")
    ap.add_argument("query", nargs="?", default="", help="natural-language query")
    args = ap.parse_args()

    if args.signup:
        k = keys_mod.generate_key(args.signup, tier="free")
        print(json.dumps(k, indent=2))
        print("\nSAVE THIS KEY — it is shown only once:")
        print("  ", k["key"])
        raise SystemExit(0)

    if args.list:
        print(json.dumps(keys_mod.list_keys(), indent=2))
        raise SystemExit(0)

    api_key = args.key or ""
    payload = {"api_key": api_key, "query": args.query}
    if args.route:
        payload["route"] = args.route

    result, status = handle(payload)
    print(json.dumps(result, indent=2, default=str))
