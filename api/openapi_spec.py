"""OpenAPI 3.0 Specification — auto-generated API documentation.

Returns the complete OpenAPI spec for all 51 modules.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MODULES = {
    "agent_rental": {"path": "/agents/rent", "methods": ["GET", "POST"], "tag": "Revenue"},
    "alert_service": {"path": "/alerts", "methods": ["GET", "POST"], "tag": "Revenue"},
    "analytics": {"path": "/analytics", "methods": ["GET"], "tag": "Core"},
    "anomaly_detector": {"path": "/anomalies", "methods": ["GET"], "tag": "Core"},
    "api_gateway": {"path": "/gateway", "methods": ["GET", "POST"], "tag": "Infrastructure"},
    "auth": {"path": "/auth", "methods": ["POST"], "tag": "Infrastructure"},
    "billing": {"path": "/billing", "methods": ["GET", "POST"], "tag": "Revenue"},
    "certification": {"path": "/cert", "methods": ["GET", "POST"], "tag": "Revenue"},
    "chronicle_of_chaos": {"path": "/chronicle", "methods": ["GET", "POST"], "tag": "Experimental"},
    "cognitive_resonance": {"path": "/resonance", "methods": ["GET", "POST"], "tag": "Intelligence"},
    "constellation": {"path": "/constellation", "methods": ["GET"], "tag": "Core"},
    "credits": {"path": "/credits", "methods": ["GET", "POST"], "tag": "Revenue"},
    "crypto": {"path": "/crypto", "methods": ["POST"], "tag": "Revenue"},
    "data_licensing": {"path": "/data", "methods": ["GET", "POST"], "tag": "Revenue"},
    "digital_twin": {"path": "/twin", "methods": ["GET", "POST"], "tag": "Revenue"},
    "docs": {"path": "/docs", "methods": ["GET"], "tag": "Infrastructure"},
    "dream_interpreter": {"path": "/dream_interpret", "methods": ["GET", "POST"], "tag": "Experimental"},
    "dream_synthesis": {"path": "/dreams", "methods": ["GET", "POST"], "tag": "Experimental"},
    "entropy_auction": {"path": "/entropy", "methods": ["GET", "POST"], "tag": "Experimental"},
    "event_stream": {"path": "/events", "methods": ["GET", "POST"], "tag": "Infrastructure"},
    "experiment_runner": {"path": "/experiments/run", "methods": ["GET", "POST"], "tag": "Core"},
    "experiments": {"path": "/experiments", "methods": ["GET"], "tag": "Core"},
    "governance": {"path": "/governance", "methods": ["GET", "POST"], "tag": "Revenue"},
    "gravitational_pricing": {"path": "/gravity", "methods": ["GET", "POST"], "tag": "Commerce"},
    "health": {"path": "/health", "methods": ["GET"], "tag": "Infrastructure"},
    "interdimensional_bridge": {"path": "/bridge", "methods": ["GET", "POST"], "tag": "Infrastructure"},
    "marketplace": {"path": "/marketplace", "methods": ["GET", "POST"], "tag": "Revenue"},
    "memory_palace": {"path": "/palace", "methods": ["GET", "POST"], "tag": "Intelligence"},
    "mycelial_commerce": {"path": "/mycelium", "methods": ["GET", "POST"], "tag": "Commerce"},
    "neural_fabric": {"path": "/neural", "methods": ["GET", "POST"], "tag": "Intelligence"},
    "paradox_marketplace": {"path": "/paradox", "methods": ["GET", "POST"], "tag": "Experimental"},
    "plugin_loader": {"path": "/plugins", "methods": ["GET", "POST"], "tag": "Infrastructure"},
    "quantum_entanglement": {"path": "/entangle", "methods": ["GET", "POST"], "tag": "Infrastructure"},
    "quantum_randomness": {"path": "/random", "methods": ["GET", "POST"], "tag": "Revenue"},
    "referral": {"path": "/referral", "methods": ["GET", "POST"], "tag": "Revenue"},
    "sandbox": {"path": "/sandbox", "methods": ["GET"], "tag": "Core"},
    "simulation_as_a_service": {"path": "/sim", "methods": ["GET", "POST"], "tag": "Revenue"},
    "speciation_engine": {"path": "/speciation", "methods": ["GET", "POST"], "tag": "Experimental"},
    "sponsored_experiments": {"path": "/sponsors", "methods": ["GET", "POST"], "tag": "Revenue"},
    "stream_reactor": {"path": "/reactor-stream", "methods": ["GET"], "tag": "Core"},
    "symbiosis_network": {"path": "/symbiosis", "methods": ["GET", "POST"], "tag": "Intelligence"},
    "synesthetic_api": {"path": "/synesthesia", "methods": ["GET", "POST"], "tag": "Experimental"},
    "telemetry": {"path": "/telemetry", "methods": ["GET"], "tag": "Core"},
    "temporal_arbitrage": {"path": "/arb", "methods": ["GET", "POST"], "tag": "Commerce"},
    "temporal_market": {"path": "/temporal", "methods": ["GET", "POST"], "tag": "Commerce"},
    "usage_dashboard": {"path": "/usage", "methods": ["GET"], "tag": "Revenue"},
    "warp_drive_optimizer": {"path": "/warp", "methods": ["GET", "POST"], "tag": "Infrastructure"},
    "wave_log": {"path": "/wave-log", "methods": ["GET"], "tag": "Core"},
    "webhooks": {"path": "/webhooks", "methods": ["GET", "POST"], "tag": "Revenue"},
    "agents": {"path": "/agents", "methods": ["GET"], "tag": "Core"},
}

TAGS = [
    {"name": "Core", "description": "Core system modules"},
    {"name": "Revenue", "description": "Revenue and billing modules"},
    {"name": "Intelligence", "description": "AI and cognitive modules"},
    {"name": "Commerce", "description": "Marketplace and pricing modules"},
    {"name": "Experimental", "description": "Creative and experimental modules"},
    {"name": "Infrastructure", "description": "Gateway, events, plugins"},
]


def generate_spec() -> dict:
    paths = {}
    for mod_name, mod_info in MODULES.items():
        path = mod_info["path"]
        if path not in paths:
            paths[path] = {}
        for method in mod_info["methods"]:
            method_lower = method.lower()
            paths[path][method_lower] = {
                "tags": [mod_info["tag"]],
                "summary": f"{mod_name.replace('_', ' ').title()} endpoint",
                "operationId": f"{mod_name}_{method_lower}",
                "responses": {
                    "200": {"description": "Success"},
                    "400": {"description": "Bad request"},
                    "500": {"description": "Server error"},
                },
            }
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "IXpansion API",
            "description": "The Computational Frontier — 51 modules, 157+ experiments, multi-agent sandbox",
            "version": "3.17.0",
        },
        "servers": [
            {"url": "https://ixpansion.vercel.app", "description": "Production"},
            {"url": "http://localhost:3000", "description": "Local dev"},
        ],
        "tags": TAGS,
        "paths": paths,
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "API Key",
                }
            }
        },
    }


def handler(request, response):
    return generate_spec()


def demo():
    spec = generate_spec()
    print(f"OpenAPI spec: {len(spec['paths'])} paths, {len(spec['tags'])} tags")
    for tag in spec["tags"]:
        count = sum(1 for p in spec["paths"].values() for m in p.values() if tag["name"] in m.get("tags", []))
        print(f"  {tag['name']}: {count} endpoints")
    return spec


if __name__ == "__main__":
    demo()
