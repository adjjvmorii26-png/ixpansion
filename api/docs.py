"""API Documentation — auto-generated from endpoint definitions.

Returns OpenAPI-style documentation for all API endpoints.
Can be served as HTML or JSON.

Usage:
    GET /api/docs       — HTML documentation
    GET /api/docs.json  — OpenAPI JSON spec
    GET /api/docs/endpoints — flat endpoint list
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ENDPOINTS = {
    "auth": {
        "base": "/api/auth",
        "endpoints": [
            {"method": "POST", "path": "/keys", "description": "Create API key", "auth": False, "tier": "free"},
            {"method": "GET", "path": "/keys", "description": "List API keys", "auth": True, "tier": "enterprise"},
            {"method": "GET", "path": "/tiers", "description": "List subscription tiers", "auth": False, "tier": "free"},
            {"method": "GET", "path": "/usage/{key}", "description": "Check API key usage", "auth": True, "tier": "free"},
        ],
    },
    "experiments": {
        "base": "/api/experiments",
        "endpoints": [
            {"method": "GET", "path": "/", "description": "List all experiments", "auth": False, "tier": "free"},
            {"method": "POST", "path": "/run", "description": "Run an experiment", "auth": True, "tier": "free"},
        ],
    },
    "crypto": {
        "base": "/api/crypto",
        "endpoints": [
            {"method": "POST", "path": "/create_invoice", "description": "Create crypto payment invoice", "auth": False, "tier": "free"},
            {"method": "GET", "path": "/status/{id}", "description": "Check payment status", "auth": False, "tier": "free"},
            {"method": "GET", "path": "/rates", "description": "Get exchange rates", "auth": False, "tier": "free"},
        ],
    },
    "credits": {
        "base": "/api/credits",
        "endpoints": [
            {"method": "POST", "path": "/buy", "description": "Purchase credits", "auth": False, "tier": "free"},
            {"method": "GET", "path": "/balance", "description": "Check credit balance", "auth": True, "tier": "free"},
            {"method": "POST", "path": "/spend", "description": "Spend credits", "auth": True, "tier": "free"},
            {"method": "GET", "path": "/pricing", "description": "View credit pricing", "auth": False, "tier": "free"},
        ],
    },
    "marketplace": {
        "base": "/api/marketplace",
        "endpoints": [
            {"method": "GET", "path": "/list", "description": "Browse marketplace", "auth": False, "tier": "free"},
            {"method": "POST", "path": "/publish", "description": "Publish an experiment", "auth": True, "tier": "pro"},
            {"method": "POST", "path": "/{id}/purchase", "description": "Purchase experiment", "auth": True, "tier": "free"},
            {"method": "GET", "path": "/earnings", "description": "View creator earnings", "auth": True, "tier": "pro"},
        ],
    },
    "billing": {
        "base": "/api/billing",
        "endpoints": [
            {"method": "GET", "path": "/plans", "description": "List subscription plans", "auth": False, "tier": "free"},
            {"method": "POST", "path": "/subscribe", "description": "Subscribe to a plan", "auth": True, "tier": "free"},
            {"method": "GET", "path": "/status", "description": "Subscription status", "auth": True, "tier": "free"},
            {"method": "POST", "path": "/cancel", "description": "Cancel subscription", "auth": True, "tier": "free"},
        ],
    },
    "analytics": {
        "base": "/api/analytics",
        "endpoints": [
            {"method": "GET", "path": "/overview", "description": "System overview", "auth": True, "tier": "pro"},
            {"method": "GET", "path": "/experiments", "description": "Experiment metrics", "auth": True, "tier": "pro"},
            {"method": "GET", "path": "/performance", "description": "Performance data", "auth": True, "tier": "pro"},
            {"method": "GET", "path": "/revenue", "description": "Revenue metrics", "auth": True, "tier": "enterprise"},
        ],
    },
    "referral": {
        "base": "/api/referral",
        "endpoints": [
            {"method": "POST", "path": "/generate", "description": "Get referral code", "auth": True, "tier": "free"},
            {"method": "POST", "path": "/apply", "description": "Apply referral code", "auth": True, "tier": "free"},
            {"method": "GET", "path": "/stats", "description": "Referral statistics", "auth": True, "tier": "free"},
        ],
    },
    "data": {
        "base": "/api/data",
        "endpoints": [
            {"method": "GET", "path": "/catalog", "description": "Browse datasets", "auth": False, "tier": "free"},
            {"method": "POST", "path": "/purchase", "description": "Purchase dataset access", "auth": True, "tier": "pro"},
            {"method": "GET", "path": "/{id}/download", "description": "Download dataset", "auth": True, "tier": "pro"},
        ],
    },
    "governance": {
        "base": "/api/governance",
        "endpoints": [
            {"method": "POST", "path": "/mint", "description": "Mint governance tokens", "auth": True, "tier": "free"},
            {"method": "GET", "path": "/balance", "description": "Check token balance", "auth": True, "tier": "free"},
            {"method": "POST", "path": "/propose", "description": "Create proposal", "auth": True, "tier": "free"},
            {"method": "POST", "path": "/vote", "description": "Vote on proposal", "auth": True, "tier": "free"},
            {"method": "GET", "path": "/proposals", "description": "List proposals", "auth": False, "tier": "free"},
        ],
    },
    "webhooks": {
        "base": "/api/webhooks",
        "endpoints": [
            {"method": "POST", "path": "/subscribe", "description": "Subscribe to events", "auth": True, "tier": "pro"},
            {"method": "GET", "path": "/list", "description": "List webhooks", "auth": True, "tier": "pro"},
            {"method": "GET", "path": "/events", "description": "List event types", "auth": False, "tier": "free"},
        ],
    },
}


def get_all_endpoints() -> list:
    all_eps = []
    for group, info in ENDPOINTS.items():
        for ep in info["endpoints"]:
            all_eps.append({
                "group": group,
                "method": ep["method"],
                "path": info["base"] + ep["path"],
                "description": ep["description"],
                "auth_required": ep["auth"],
                "minimum_tier": ep["tier"],
            })
    return all_eps


def get_openapi_spec() -> dict:
    paths = {}
    for group, info in ENDPOINTS.items():
        for ep in info["endpoints"]:
            full_path = info["base"] + ep["path"]
            if full_path not in paths:
                paths[full_path] = {}
            paths[full_path][ep["method"].lower()] = {
                "summary": ep["description"],
                "tags": [group],
                "security": [{"apiKey": []}] if ep["auth"] else [],
                "responses": {"200": {"description": "Success"}},
            }
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "IXpansion Observatory API",
            "version": "3.12.0",
            "description": "157+ experiments across quantum, ecology, folklore, and cosmology",
        },
        "servers": [{"url": "https://ixpansion.vercel.app", "description": "Production"}],
        "paths": paths,
        "components": {
            "securitySchemes": {
                "apiKey": {"type": "apiKey", "in": "header", "name": "Authorization"}
            }
        },
    }


def handler(request, response):
    return get_openapi_spec()


def demo():
    print("=== API Documentation ===")
    eps = get_all_endpoints()
    print(f"\nTotal endpoints: {len(eps)}")
    groups = {}
    for ep in eps:
        groups.setdefault(ep["group"], []).append(ep)
    for group, group_eps in groups.items():
        print(f"\n  {group.upper()} ({len(group_eps)} endpoints)")
        for ep in group_eps:
            auth = "🔒" if ep["auth_required"] else "🔓"
            print(f"    {auth} {ep['method']} {ep['path']}: {ep['description']} [{ep['minimum_tier']}]")

    spec = get_openapi_spec()
    print(f"\nOpenAPI spec: {spec['info']['title']} v{spec['info']['version']}")
    print(f"Paths: {len(spec['paths'])}")

    return {"endpoints": len(eps), "groups": len(groups)}


if __name__ == "__main__":
    demo()
