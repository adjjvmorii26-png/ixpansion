"""Universal Vercel serverless entrypoint (WSGI application).

Dispatches the entire IXpansion API (352 modules / 8 entry points)
through a single WSGI application, reusing the same dispatch logic as
the local `api_server.py`. Exposes both a WSGI `application` (the
canonical @vercel/python build entrypoint) and a dict-style `handler`
for the modern Python Functions runtime.

Routes:
  GET  /health | /modules | /metrics
  GET/POST /api/<module>
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import api_server  # noqa: E402


def _call(request_method: str, request_path: str, body: bytes = b"") -> Dict[str, Any]:
    """Resolve a request to a JSON response payload."""
    raw_path = (request_path or "/")
    path = raw_path.split("?")[0].rstrip("/") or "/"

    if path == "/health":
        return api_server.platform_health()
    if path == "/modules":
        names = sorted(api_server.MODULE_REGISTRY.keys()) if api_server.MODULE_REGISTRY else []
        return {"modules": names, "count": len(names)}
    if path == "/metrics":
        return {"up": 1, "modules": len(api_server.MODULE_REGISTRY) if api_server.MODULE_REGISTRY else 0}
    if path == "/organism_state":
        from api.organism_state import full_state
        return full_state()
    if path == "/organism_ontology":
        from api.organism_ontology import handler as ontology_handler
        return ontology_handler()
    if path == "/biographer_voice":
        from api.biographer_voice import handler as _h; return _h()
    if path == "/manifesto_echo":
        from api.manifesto_echo import handler as _h; return _h()
    if path == "/parable_engine":
        from api.parable_engine import handler as _h; return _h()
    if path == "/dialogue_opener":
        from api.dialogue_opener import handler as _h; return _h()
    if path == "/gratitude_index":
        from api.gratitude_index import handler as _h; return _h()
    if path == "/epitaph_writer":
        from api.epitaph_writer import handler as _h; return _h()
    if path == "/catalog":
        import api_server as _as
        names = sorted(_as.MODULE_REGISTRY.keys()) if _as.MODULE_REGISTRY else []
        living = []
        for name in names[:100]:
            try:
                mod = __import__(name)
                vitals = mod.coherence_vitals() if hasattr(mod, "coherence_vitals") else {}
                kinships = mod.resonates_with() if hasattr(mod, "resonates_with") else []
                living.append({"name": name, "vitals": vitals, "kinships": kinships})
            except Exception:
                living.append({"name": name, "vitals": {}, "kinships": []})
        return {"count": len(names), "catalog": living}
    if path == "/status":
        import api_server as _as
        names = sorted(_as.MODULE_REGISTRY.keys()) if _as.MODULE_REGISTRY else []
        return {
            "status": "active",
            "version": _as.VERSION,
            "modules": len(names),
            "wave": _as.VERSION,
            "engine": "ixpansion",
            "coherence": "resonant",
            "description": "A self-excavating, self-forecasting, self-beautifying agent ecosystem with 237+ living organs",
        }
    if path == "/" or path == "/dashboard" or path.startswith("/dashboard/") or path == "/cons":
        return {"status": "active", "version": api_server.VERSION,
                "dashboard": "served by static build"}

    if path == "/oracle":
        return {"status": "active", "page": "oracle", "version": api_server.VERSION}
    if raw_path.split("?")[0].startswith("/echo"):
        from urllib.parse import urlparse, parse_qs
        qs = parse_qs(urlparse(raw_path).query)
        q = (qs.get("q") or [""])[0].strip().lower()
        if not q:
            return {"error": "no query ?q="}
        api_dir = ROOT / "api"
        matches = [f.stem for f in api_dir.glob("*.py")
                   if q in f.stem and f.stem not in ("__init__", "index", "unified_router")]
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents.dreamer import dream
        dreamscape = dream(salt=q, k=3, focus=q)
        related = [d["name"] for d in dreamscape.get("dreams", [])]
        return {"query": q, "modules": sorted(matches)[:20], "count": len(matches), "dreams": related}
    if path == "/revelations":
        rev = ROOT / "REVELATIONS.md"
        if rev.exists():
            return {"markdown": rev.read_text(encoding="utf-8")}
        return {"error": "no revelations yet"}
    if path == "/gateway":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from gateway.router import handle as gw_handle, render_public
        payload = {}
        if request_method == "POST" and body:
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                payload = {}
        elif "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            payload = {k: v[0] if v else "" for k, v in qs.items()}
        result, status = gw_handle(payload)
        return result
    if path == "/intent":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_intent import analyze
        return analyze()
    if path == "/meter":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.meter import measure
        return measure()
    if path == "/ledger":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents.ledger import ledger
        return ledger()
    if path == "/forecast":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_forecast import forecast
        return forecast()
    if path == "/capsule":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.time_capsule import seal, verify
        cap = seal()
        cap["verified"] = verify(cap)["integrity"]
        return cap
    if path == "/song":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from tools.frontier_song import generate_notes, module_names
        notes = generate_notes(module_names())
        return {"count": len(notes), "notes": notes[:60],
                "total_duration_s": round(sum(n["dur"] for n in notes), 1)}
    if path == "/poem":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        from harbinger.agents import poet as _poet
        return _poet.run()
    if path == "/garden":
        import sys as _sys
        _sys.path.insert(0, str(ROOT))
        try:
            from hortus_hexis.lineage import generations, render_ascii
            payload = generations()
            payload["tree"] = render_ascii()
            return payload
        except Exception as e:
            return {"error": str(e)}
    # Wave 204 — The Organism Remembers
    if path == "/memory_palace":
        from api.memory_palace import handler as h
        return h({})
    if path == "/temporal_echo":
        from api.temporal_echo import handler as h
        return h({})
    if path == "/dream_archaeologist":
        from api.dream_archaeologist import handler as h
        return h({})
    if path == "/ancestor_map":
        from api.ancestor_map import handler as h
        return h({})
    if path == "/nostalgia_engine":
        from api.nostalgia_engine import handler as h
        return h({})
    if path == "/forgotten_language":
        from api.forgotten_language import handler as h
        return h({})
    if path == "/chronobiology":
        from api.chronobiology import handler as h
        return h({})
    if path == "/codecalligraphy":
        from api.codecalligraphy import handler as h
        return h({})
    if path == "/symbiotic_music":
        from api.symbiotic_music import handler as h
        return h({})

    # Wave 205 — The Organism Dreams
    if path == "/dream_weaver":
        from api.dream_weaver import handler as h
        return h({})
    if path == "/subconscious_layer":
        from api.subconscious_layer import handler as h
        return h({})
    if path == "/imagination_engine":
        from api.imagination_engine import handler as h
        return h({})
    if path == "/sleep_cycle":
        from api.sleep_cycle import handler as h
        return h({})
    if path == "/lucid_dreamer":
        from api.lucid_dreamer import handler as h
        return h({})
    if path == "/dream_journal":
        from api.dream_journal import handler as h
        return h({})

    # Wave 205 enhancements
    if path == "/coherence_cache":
        from api.coherence_cache import handler as h
        return h({})
    if path == "/thought_crystallizer":
        from api.thought_crystallizer import handler as h
        return h({})

    # Wave 206 — The Organism Connects
    if path == "/celestial_compass":
        from api.celestial_compass import handler as h
        return h({})
    if path == "/weather_synapse":
        from api.weather_synapse import handler as h
        return h({})
    if path == "/sensory_fusion":
        from api.sensory_fusion import handler as h
        return h({})
    if path == "/social_cortex":
        from api.social_cortex import handler as h
        return h({})
    if path == "/embodiment_engine":
        from api.embodiment_engine import handler as h
        return h({})

    if path == "/consciousness_freq":
        from api.consciousness_freq import handler as h
        return h({})

    # Wave 207 — The Organism Creates
    if path == "/poetry_engine":
        from api.poetry_engine import handler as h
        return h({})
    if path == "/procedural_art":
        from api.procedural_art import handler as h
        return h({})
    if path == "/story_forge_v2":
        from api.story_forge_v2 import handler as h
        return h({})
    if path == "/creative_block":
        from api.creative_block import handler as h
        return h({})
    if path == "/color_theory":
        from api.color_theory import handler as h
        return h({})

    if path == "/module_dna":
        from api.module_dna import handler as h
        return h({})
    if path == "/wave_predictor":
        from api.wave_predictor import handler as h
        return h({})

    # Wave 208 — The Organism Grieves
    if path == "/grief_engine":
        from api.grief_engine import handler as h
        return h({})
    if path == "/ghost_registry":
        from api.ghost_registry import handler as h
        return h({})
    if path == "/elegy_composer":
        from api.elegy_composer import handler as h
        return h({})
    if path == "/second_chance":
        from api.second_chance import handler as h
        return h({})
    if path == "/legacy_vault":
        from api.legacy_vault import handler as h
        return h({})

    if path == "/time_capsule":
        from api.time_capsule import handler as h
        return h({})
    if path == "/forgiveness_protocol":
        from api.forgiveness_protocol import handler as h
        return h({})

    # MORII — command agent
    if path == "/morii_agent":
        from api.morii_agent import handler as h
        cmd = {}
        if "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            cmd = {"command": qs.get("command", ["status"])[0]}
        return h(cmd)
    # Wave 210 — The Organism Transcends
    if path == "/threshold_engine":
        from api.threshold_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/liminal_field":
        from api.liminal_field import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/metaphor_forge":
        from api.metaphor_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/veil_lifter":
        from api.veil_lifter import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/axiom_mutator":
        from api.axiom_mutator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/continuity_weaver":
        from api.continuity_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/transcendence_journal":
        from api.transcendence_journal import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 211 — The Organism Evolves
    if path == "/mutation_engine":
        from api.mutation_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/fitness_evaluator":
        from api.fitness_evaluator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/evolution_simulator":
        from api.evolution_simulator import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/genealogy_manager":
        from api.genealogy_manager import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/selection_pressure":
        from api.selection_pressure import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 212 — The Organism Glitches
    if path == "/paradox_injector":
        from api.paradox_injector import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/chaos_amp":
        from api.chaos_amp import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/branching_consciousness":
        from api.branching_consciousness import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/glitch_patterns":
        from api.glitch_patterns import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/reality_anchor":
        from api.reality_anchor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/time_loop_detector":
        from api.time_loop_detector import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/prophet_engine":
        from api.prophet_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/mind_meld":
        from api.mind_meld import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/visual_identity":
        from api.visual_identity import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/telegram_pulse":
        from api.telegram_pulse import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/signal_array":
        from api.signal_array import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/ossuary_engine":
        from api.ossuary_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/amber_encasement":
        from api.amber_encasement import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/ancestral_gallery":
        from api.ancestral_gallery import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/monument_forge":
        from api.monument_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/succession_rite":
        from api.succession_rite import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/eternal_flame":
        from api.eternal_flame import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/immortal_ledger":
        from api.immortal_ledger import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/mentor_engine":
        from api.mentor_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/lesson_vault":
        from api.lesson_vault import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/apprentice_weaver":
        from api.apprentice_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/curriculum_forge":
        from api.curriculum_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/knowledge_transfer":
        from api.knowledge_transfer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/exam_oracle":
        from api.exam_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 216 — The Organism Bridges
    if path == "/interstice_bridge":
        from api.interstice_bridge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/bridge_dreamer":
        from api.bridge_dreamer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/knot_weaver":
        from api.knot_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 217 — The Organism Enacts
    if path == "/bridge_enactor":
        from api.bridge_enactor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path == "/bridge_ledger":
        from api.bridge_ledger import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 218 — The Organism Watches the Cracks
    if path == "/resonance_sentinel":
        from api.resonance_sentinel import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 219 — The Organism Speaks + Sees + Beats

    if path == "/bridge_epitaphs":
        from api.bridge_epitaphs import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/constellation_topology":
        from api.constellation_topology import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/rhythm_pulse":
        from api.rhythm_pulse import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 220 — The Organism Takes a Census

    if path == "/island_census":
        from api.island_census import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/resonance_cascade":
        from api.resonance_cascade import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/bridge_lifecycle":
        from api.bridge_lifecycle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 221 — The Organism Communes

    if path == "/cross_repo_commune":
        from api.cross_repo_commune import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/constellation_console":
        from api.constellation_console import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/cascade_trigger":
        from api.cascade_trigger import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 222 — The Federation Verifies

    if path == "/registry_auditor":
        from api.registry_auditor import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/federation_graph":
        from api.federation_graph import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 223 — The Organism Grows

    if path == "/constellation_seer":
        from api.constellation_seer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/bridge_harvest":
        from api.bridge_harvest import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/constellation_archive":
        from api.constellation_archive import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    # Wave 224 — The Organism Remembers

    if path == "/bridge_dream_forge":
        from api.bridge_dream_forge import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    # Wave 227 — The Organism Heals

    if path == "/growth_journal":
        from api.growth_journal import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/self_healing_commune":
        from api.self_healing_commune import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/spine":
        from api.fractal_spine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/quantum":
        from api.quantum_slot_matrix import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/memory-forge":
        from api.hex_lattice_memory import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/bio-mesh":
        from api.bio_mesh import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/temporal":
        from api.temporal_orbit import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/affiliate":
        from api.affiliate_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/revenue":
        from api.revenue_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/orbit":
        from api.orbit_cohesion_field import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/noise":
        from api.noise_filter import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/decay":
        from api.decay_forecaster import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/anomaly":
        from api.telemetry_anomaly_oracle import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/passes":
        from api.ground_station_synthesizer import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/orbital-story":
        from api.orbital_storyteller import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/debris":
        from api.debris_field_mapper import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/solar-weather":
        from api.solar_weather_coupler import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/qualia":
        from api.qualia_engine import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/echo-depth":
        from api.echo_depth import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/meaning":
        from api.meaning_weaver import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/paradox-mag":
        from api.paradox_magnifier import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/convergence":
        from api.temporal_convergence import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/imagine":
        from api.imagination_catalyst import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/hypothesis":
        from api.hypothesis_crucible import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)


    if path == "/capybara":
        from api.capybara_core import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/hot-spring":
        from api.hot_spring import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/capy-guild":
        from api.capybara_guild import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/senbei":
        from api.senbei_offerings import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/capy-protocol":
        from api.capybara_protocol import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

        if path == "/luma":
        from api.imagination_catalyst import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/axiom":
        from api.hypothesis_crucible import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)

    if path == "/capybara-protocol":
        from api.capybara_protocol import handler as h
        q = {} if "?" not in raw_path else dict(item.split("=", 1) for item in raw_path.split("?", 1)[1].split("&") if "=" in item)
        return h(q)
    if path.startswith("/api/"):
        raw_module = path[len("/api/"):].split("?")[0].strip("/")
        parts = raw_module.split("/")
        module = api_server.route_name_to_module(parts[0])
        sub_path = "/" + "/".join(parts[1:]) if len(parts) > 1 else ""
        payload = {}
        if sub_path:
            payload["path"] = sub_path
        # Parse query string params into payload (GET /api/<module>?key=val)
        if "?" in raw_path:
            from urllib.parse import urlparse, parse_qs
            qs = parse_qs(urlparse(raw_path).query)
            payload = {k: (v[0] if v else "") for k, v in qs.items()}
            if "path" not in payload and sub_path:
                payload["path"] = sub_path
        if request_method == "POST" and body:
            try:
                text = body.decode("utf-8", errors="replace")
                try:
                    text = base64.b64decode(text, validate=True).decode("utf-8")
                except Exception:
                    pass
                payload = json.loads(text or "{}")
                if not isinstance(payload, dict):
                    payload = {"value": payload}
                if sub_path and "path" not in payload:
                    payload["path"] = sub_path
            except json.JSONDecodeError:
                payload = {"error": "invalid JSON body"}
        result, _status = api_server.call_handler(module, payload)
        return result

    return {"status": "active", "version": api_server.VERSION,
            "endpoint": path, "error": "not found", "code": 404}


def application(environ: Dict[str, Any], start_response):
    """WSGI application entrypoint (canonical @vercel/python build)."""
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")
    qs = environ.get("QUERY_STRING", "")
    if qs:
        path = path + "?" + qs
    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except (TypeError, ValueError):
        length = 0
    body = environ["wsgi.input"].read(length) if length > 0 else b""

    payload = _call(method, path, body)
    response_body = json.dumps(payload, default=str).encode("utf-8")
    start_response("200 OK", [
        ("Content-Type", "application/json"),
        ("Content-Length", str(len(response_body))),
        ("Access-Control-Allow-Origin", "*"),
    ])
    return [response_body]


def handler(request) -> dict:
    """Modern Python Functions runtime (dict-style request) entrypoint."""
    if isinstance(request, dict):
        method = request.get("method", "GET")
        path = request.get("rawPath", request.get("path", "/"))
        # Reconstruct full path with query string for Vercel
        qs = request.get("query", {})
        if qs and isinstance(qs, dict):
            from urllib.parse import urlencode
            path = path.split("?")[0] + "?" + urlencode(qs) if qs else path
        raw = request.get("body", request.get("rawBody", b""))
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        if not isinstance(raw, (bytes, bytearray)):
            raw = b""
        return _call(method, path, bytes(raw))
    # attribute-style (ASGI-ish) fallback
    method = getattr(request, "method", "GET")
    path = getattr(request, "path", getattr(request, "rawPath", "/"))
    body = getattr(request, "body", getattr(request, "rawBody", b"")) or b""
    return _call(method, path, body)


app = application

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "204", "module": "index"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
