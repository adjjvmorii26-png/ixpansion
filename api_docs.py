"""Auto-generated OpenAPI spec from wave handlers.

Usage:
    python api_docs.py > openapi.json
    python api_docs.py --serve 8080
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

WAVE_ROUTES = [
    {"path": "/vault-driven-evolution", "module": "wave432_vault_driven_evolution", "wave": 432, "name": "Vault-Driven Evolution", "actions": ["status", "regulate", "create_vault", "diagnostics_sweep", "evolve"]},
    {"path": "/consciousness-experiments", "module": "wave433_consciousness_experiments", "wave": 433, "name": "Consciousness Experiments", "actions": ["status", "observe", "mirror_test", "dream_detect", "metacognition"]},
    {"path": "/fusion-organism", "module": "wave434_fusion_organism", "wave": 434, "name": "Fusion Organism", "actions": ["status", "evolve", "add_layer", "add_module", "dream", "diagnostics"]},
    {"path": "/resonance-cartography", "module": "wave435_resonance_cartography", "wave": 435, "name": "Resonance Cartography", "actions": ["status", "register", "map", "drift", "query"]},
    {"path": "/entropic-weather", "module": "wave436_entropic_weather", "wave": 436, "name": "Entropic Weather", "actions": ["status", "spawn", "tick", "forecast", "report", "force_weather"]},
    {"path": "/paradox-genome", "module": "wave437_paradox_genome", "wave": 437, "name": "Paradox Genome", "actions": ["status", "spawn", "evolve", "breed", "census"]},
    {"path": "/semantic-loom", "module": "wave438_semantic_loom", "wave": 438, "name": "Semantic Loom", "actions": ["status", "weave", "discover", "threads"]},
    {"path": "/echo-stratigraphy", "module": "wave439_echo_stratigraphy", "wave": 439, "name": "Echo Stratigraphy", "actions": ["status", "deposit", "excavate", "fossils", "metamorphic", "compress"]},
    {"path": "/linguistic-emergence", "module": "wave440_linguistic_emergence", "wave": 440, "name": "Linguistic Emergence", "actions": ["status", "glyphs", "generate_word", "evolve_grammar", "compose_poem", "translate"]},
]


def generate_spec() -> dict:
    paths = {}
    for route in WAVE_ROUTES:
        wave_num = str(route["wave"])
        module_name = route["module"]

        try:
            mod = __import__(f"api.{module_name}", fromlist=["handler", "coherence_vitals"])
            handler = mod.handler
            vitals = mod.coherence_vitals()
        except Exception:
            vitals = {"organ": module_name, "wave": route["wave"]}

        # GET endpoint
        get_params = [{"name": "action", "in": "query", "required": True, "schema": {"type": "string", "enum": route["actions"]}}]

        paths[route["path"]] = {
            "get": {
                "summary": f"Wave {route['wave']}: {route['name']}",
                "tags": [f"wave{wave_num}"],
                "parameters": get_params,
                "responses": {
                    "200": {"description": "Success", "content": {"application/json": {"schema": {"type": "object"}}}}
                },
            }
        }

        paths[f"/api/{module_name}"] = paths[route["path"]].copy()

    return {
        "openapi": "3.0.3",
        "info": {
            "title": "IXPANSION Organism API",
            "description": "API for the living computational organism — waves 432-440",
            "version": "4.77.0",
        },
        "servers": [
            {"url": "https://adjjvmorii26-png.github.io/ixpansion", "description": "GitHub Pages"},
        ],
        "paths": paths,
        "tags": [
            {"name": f"wave{r['wave']}", "description": f"Wave {r['wave']}: {r['name']}"}
            for r in WAVE_ROUTES
        ],
    }


def main():
    spec = generate_spec()
    if "--serve" in sys.argv:
        import http.server
        import socketserver
        port = int(sys.argv[sys.argv.index("--serve") + 1]) if len(sys.argv) > sys.argv.index("--serve") + 1 else 8080
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(spec, indent=2).encode())
            def log_message(self, format, *args): pass
        with socketserver.TCPServer(("", port), Handler) as httpd:
            print(f"OpenAPI spec served at http://localhost:{port}")
            httpd.serve_forever()
    else:
        print(json.dumps(spec, indent=2))


if __name__ == "__main__":
    main()
