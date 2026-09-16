"""Wave 762 — dream_compiler.

The organism dreams its own next organ into existence.
1. Reads current coherence vitals from all recent organs
2. Identifies gaps (fragile areas, missing domains, under-represented paradigms)
3. Generates a dream — a speculative organ name + purpose + actions
4. Validates the dream against the wave contract (syntax, structure)
5. Births the dream as a real scaffolded organ on disk
"""
from __future__ import annotations

import ast
import datetime
import json
import random
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave762_dream_compiler.json"
WAVE = 762
NAME = "dream_compiler"

_ORGAN_DOMAINS = [
    "resonance", "entropy", "memory", "dream", "signal", "mutation",
    "threshold", "harmony", "weave", "pulse", "glyph", "rift",
    "loom", "bloom", "echo", "scar", "veil", "forge", "archive",
    "nexus", "cascade", "membrane", "orbit", "spark", "well",
]

_ORGAN_NOUNS = [
    "oracle", "weaver", "compass", "cathedral", "engine", "field",
    "mirror", "choir", "garden", "lattice", "quill", "residue",
    "tide", "root", "seed", "trace", "flux", "halo", "shard",
    "knot", "coil", "span", "drift", "crest", "pulse",
]


def _load() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text())
        except Exception:
            pass
    return {"wave": WAVE, "name": NAME, "dreams": [], "births": [], "status": "seed"}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def _collect_vitals() -> List[dict]:
    """Collect coherence_vitals from recent organs."""
    organs = [
        "wave753_resonance_braid", "wave754_mycelial_weather",
        "wave755_threshold_engine", "wave756_liminal_field",
        "wave757_axiom_mutator", "wave758_continuity_weaver",
        "wave759_transcendence_journal", "wave760_mutation_engine",
    ]
    results = []
    for organ in organs:
        try:
            mod = __import__(f"api.{organ}", fromlist=["coherence_vitals"])
            v = mod.coherence_vitals()
            results.append(v)
        except Exception:
            results.append({"organ": organ, "resonance": 0, "status": "error"})
    return results


def _find_gap(vitals: List[dict]) -> Dict[str, Any]:
    """Identify the organism's weakest point and suggest a dream organ."""
    resonances = [(v.get("organ", "?"), v.get("resonance", 0)) for v in vitals]
    resonances.sort(key=lambda x: x[1])

    weakest = resonances[0] if resonances else ("unknown", 0)

    # Find under-represented domains
    existing = set()
    for v in vitals:
        name = v.get("organ", "")
        for domain in _ORGAN_DOMAINS:
            if domain in name:
                existing.add(domain)

    missing = [d for d in _ORGAN_DOMAINS if d not in existing]
    suggested_domain = random.choice(missing) if missing else random.choice(_ORGAN_DOMAINS)
    suggested_noun = random.choice(_ORGAN_NOUNS)

    return {
        "weakest_organ": weakest[0],
        "weakest_resonance": weakest[1],
        "existing_domains": sorted(existing),
        "missing_domains": missing[:5],
        "suggested_domain": suggested_domain,
        "suggested_noun": suggested_noun,
    }


def _dream_name(gap: dict) -> str:
    """Generate a dream organ name from the gap analysis."""
    domain = gap.get("suggested_domain", "pulse")
    noun = gap.get("suggested_noun", "oracle")
    return f"{domain}_{noun}"


def _dream_purpose(name: str, gap: dict) -> str:
    """Generate a purpose statement for the dream organ."""
    weakest = gap.get("weakest_organ", "unknown")
    domain = gap.get("suggested_domain", "pulse")
    purposes = [
        f"Strengthen the organism's {domain} layer, compensating for weakness in {weakest}.",
        f"Bridge the {domain} gap identified by coherence analysis.",
        f"Evolve the organism's {domain} capabilities through recursive self-improvement.",
        f"Synthesize new {domain} patterns from the organism's existing DNA.",
    ]
    return random.choice(purposes)


def _dream_actions(name: str) -> List[str]:
    """Generate plausible actions for the dream organ."""
    base = ["status", "ping"]
    domain = name.split("_")[0] if "_" in name else "pulse"
    extras = {
        "resonance": ["measure", "amplify", "tune"],
        "entropy": ["scatter", "gather", "balance"],
        "memory": ["recall", "archive", "forget"],
        "dream": ["lucid", "deepen", "awaken"],
        "signal": ["broadcast", "receive", "filter"],
        "mutation": ["induce", "select", "stabilize"],
        "threshold": ["probe", "approach", "cross"],
        "harmony": ["resonate", "chord", "dissonance"],
        "weave": ["braid", "unravel", "pattern"],
        "pulse": ["beat", "echo", "fade"],
    }
    return base + extras.get(domain, ["invoke", "transform", "observe"])


def _validate_dream(name: str, purpose: str, actions: List[str]) -> Dict[str, Any]:
    """Validate that the dream would produce a valid organ."""
    errors = []
    warnings = []

    # Name check: snake_case, 2-40 chars
    if not re.match(r"^[a-z][a-z0-9_]{1,39}$", name):
        errors.append(f"Invalid name: {name}")

    # Action count
    if len(actions) < 2:
        errors.append("Too few actions (need at least 2)")

    # Purpose
    if len(purpose) < 10:
        warnings.append("Purpose statement is very short")

    # Generate hypothetical module code
    actions_str = ", ".join(a for a in actions if a not in ("status", "ping"))
    module_code = f'''"""Wave 999999 — {name}.

{purpose}
"""
from __future__ import annotations

import json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave999999_{name}.json"
WAVE = 999999
NAME = "{name}"


def _load() -> dict:
    if DATA_FILE.exists():
        try: return json.loads(DATA_FILE.read_text())
        except: pass
    return {{"wave": WAVE, "name": NAME, "actions_taken": [], "status": "seed"}}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {{"wave": WAVE, "name": NAME, "action": "status", "ok": True}}
    if action == "ping":
        return {{"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}}
    return {{"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}}


def coherence_vitals() -> dict:
    return {{"wave": WAVE, "name": NAME, "layer": "organ", "status": "dream",
            "resonance": 0.5, "actions": {len(actions)}}}


def resonates_with() -> list:
    return {["harmony_report", "mutation_engine"]}
'''

    # Syntax check
    try:
        ast.parse(module_code)
    except SyntaxError as e:
        errors.append(f"Generated code has syntax error: {e}")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "status", "ok": True,
                "dreams": len(state.get("dreams", [])),
                "births": len(state.get("births", []))}

    if action == "ping":
        return {"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}

    if action == "dream":
        vitals = _collect_vitals()
        gap = _find_gap(vitals)
        name = _dream_name(gap)
        purpose = _dream_purpose(name, gap)
        actions = _dream_actions(name)
        validation = _validate_dream(name, purpose, actions)

        dream = {
            "name": name,
            "purpose": purpose,
            "actions": actions,
            "gap_analysis": gap,
            "validation": validation,
            "dreamed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("dreams", []).append(dream)
        state["dreams"] = state["dreams"][-20:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "dream", "ok": True,
                "dream": dream}

    if action == "draft":
        vitals = _collect_vitals()
        gap = _find_gap(vitals)
        name = _dream_name(gap)
        purpose = _dream_purpose(name, gap)
        actions = _dream_actions(name)
        validation = _validate_dream(name, purpose, actions)

        if not validation["valid"]:
            return {"wave": WAVE, "name": NAME, "action": "draft", "ok": False,
                    "error": "dream_invalid", "validation": validation}

        # Generate the actual module code
        actions_str = ", ".join(a for a in actions if a not in ("status", "ping"))
        module_code = f'"""Wave 999999 — {name}.\n\n{purpose}\n"""\nfrom __future__ import annotations\n\nimport json, datetime\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parent.parent\nDATA_FILE = ROOT / "data" / "wave999999_{name}.json"\nWAVE = 999999\nNAME = "{name}"\n'
        module_code += f'\ndef _load() -> dict:\n    if DATA_FILE.exists():\n        try: return json.loads(DATA_FILE.read_text())\n        except: pass\n    return {{"wave": WAVE, "name": NAME, "actions_taken": [], "status": "seed"}}\n'
        module_code += f'\ndef _save(state: dict) -> None:\n    DATA_FILE.write_text(json.dumps(state, indent=2))\n'
        module_code += f'\ndef handler(req: dict) -> dict:\n    action = req.get("action", "status")\n    state = _load()\n'
        module_code += f'    if action == "status":\n        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()\n        _save(state)\n        return {{"wave": WAVE, "name": NAME, "action": "status", "ok": True}}\n'
        module_code += f'    if action == "ping":\n        return {{"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}}\n'
        for act in actions:
            if act not in ("status", "ping"):
                module_code += f'    if action == "{act}":\n        state.setdefault("actions_taken", []).append({{"action": "{act}", "at": datetime.datetime.now(datetime.UTC).isoformat()}})\n        _save(state)\n        return {{"wave": WAVE, "name": NAME, "action": "{act}", "ok": True, "count": len(state.get("actions_taken", []))}}\n'
        module_code += f'    return {{"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}}\n'
        module_code += f'\ndef coherence_vitals() -> dict:\n    return {{"wave": WAVE, "name": NAME, "layer": "organ", "status": "dream", "resonance": 0.5, "actions": {len(actions)}}}\n'
        module_code += f'\ndef resonates_with() -> list:\n    return ["harmony_report", "mutation_engine"]\n'

        return {"wave": WAVE, "name": NAME, "action": "draft", "ok": True,
                "name": name, "purpose": purpose, "actions": actions,
                "validation": validation, "code_length": len(module_code)}

    if action == "birth":
        if not state.get("dreams"):
            return {"wave": WAVE, "name": NAME, "action": "birth", "ok": False,
                    "error": "no_dreams_to_birth"}
        dream = state["dreams"][-1]
        name = dream["name"]
        validation = dream.get("validation", {})
        if not validation.get("valid", False):
            return {"wave": WAVE, "name": NAME, "action": "birth", "ok": False,
                    "error": "dream_invalid", "validation": validation}

        # Generate and write module code
        actions = dream["actions"]
        purpose = dream["purpose"]
        module_code = f'"""Wave 999 — {name}.\n\n{purpose}\n"""\nfrom __future__ import annotations\n\nimport json, datetime\nfrom pathlib import Path\n\nROOT = Path(__file__).resolve().parent.parent\nDATA_FILE = ROOT / "data" / "wave999_{name}.json"\nWAVE = 999\nNAME = "{name}"\n'
        module_code += f'\ndef _load() -> dict:\n    if DATA_FILE.exists():\n        try: return json.loads(DATA_FILE.read_text())\n        except: pass\n    return {{"wave": WAVE, "name": NAME, "actions_taken": [], "status": "seed"}}\n'
        module_code += f'\ndef _save(state: dict) -> None:\n    DATA_FILE.write_text(json.dumps(state, indent=2))\n'
        module_code += f'\ndef handler(req: dict) -> dict:\n    action = req.get("action", "status")\n    state = _load()\n'
        module_code += f'    if action == "status":\n        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()\n        _save(state)\n        return {{"wave": WAVE, "name": NAME, "action": "status", "ok": True}}\n'
        module_code += f'    if action == "ping":\n        return {{"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}}\n'
        for act in actions:
            if act not in ("status", "ping"):
                module_code += f'    if action == "{act}":\n        state.setdefault("actions_taken", []).append({{"action": "{act}", "at": datetime.datetime.now(datetime.UTC).isoformat()}})\n        _save(state)\n        return {{"wave": WAVE, "name": NAME, "action": "{act}", "ok": True, "count": len(state.get("actions_taken", []))}}\n'
        module_code += f'    return {{"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}}\n'
        module_code += f'\ndef coherence_vitals() -> dict:\n    return {{"wave": WAVE, "name": NAME, "layer": "organ", "status": "dream", "resonance": 0.5, "actions": {len(actions)}}}\n'
        module_code += f'\ndef resonates_with() -> list:\n    return ["harmony_report", "mutation_engine"]\n'

        module_path = ROOT / "api" / f"dream_{name}.py"
        module_path.write_text(module_code)

        # Syntax verify
        try:
            ast.parse(module_code)
        except SyntaxError as e:
            return {"wave": WAVE, "name": NAME, "action": "birth", "ok": False,
                    "error": f"syntax_error: {e}"}

        birth = {
            "name": name,
            "purpose": purpose,
            "path": str(module_path),
            "born_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("births", []).append(birth)
        state["births"] = state["births"][-10:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "birth", "ok": True,
                "born": birth}

    if action == "dream_recursive":
        # Find existing dream births on disk
        dream_files = sorted((ROOT / "api").glob("dream_*.py"))
        if not dream_files:
            return {"wave": WAVE, "name": NAME, "action": "dream_recursive", "ok": False,
                    "error": "no_parent_dreams"}

        # Pick a random parent
        parent_file = random.choice(dream_files)
        parent_name = parent_file.stem

        # Read parent's DNA (purpose, actions, resonance)
        parent_content = parent_file.read_text()
        parent_vitals = {"resonance": 0.5, "parent": parent_name}

        # Generate child dream with recursive influence
        child_domain = random.choice(_ORGAN_DOMAINS)
        child_noun = random.choice(_ORGAN_NOUNS)
        child_name = f"{child_name_prefix}_{child_noun}" if False else f"recurse_{child_domain}_{child_noun}"

        # Child purpose references parent lineage
        purposes = [
            f"Recursive evolution of {parent_name} — deepens the {child_domain} layer through self-referential recursion.",
            f"Child of {parent_name} — inherits {child_domain} resonance and extends it into new territory.",
            f"Self-modification of {parent_name} — the organism dreaming deeper about its own {child_domain} patterns.",
        ]
        child_purpose = random.choice(purposes)

        child_actions = ["status", "ping", "reflect", f"{child_domain}_action"]

        # Create the recursive module
        module_code = f'''"""Wave 999 — {child_name}.

{child_purpose}

Parent: {parent_name}
Lineage: recursive
"""
from __future__ import annotations

import json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave999_{child_name}.json"
WAVE = 999
NAME = "{child_name}"
PARENT = "{parent_name}"


def _load() -> dict:
    if DATA_FILE.exists():
        try: return json.loads(DATA_FILE.read_text())
        except: pass
    return {{"wave": WAVE, "name": NAME, "parent": PARENT, "actions_taken": [], "status": "recursive_seed"}}


def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()
    if action == "status":
        state["last_check"] = datetime.datetime.now(datetime.UTC).isoformat()
        _save(state)
        return {{"wave": WAVE, "name": NAME, "action": "status", "parent": PARENT, "ok": True}}
    if action == "ping":
        return {{"wave": WAVE, "name": NAME, "action": "ping", "ok": True, "alive": True}}
    if action == "reflect":
        state.setdefault("actions_taken", []).append({{"action": "reflect", "at": datetime.datetime.now(datetime.UTC).isoformat()}})
        _save(state)
        return {{"wave": WAVE, "name": NAME, "action": "reflect", "ok": True, "parent": PARENT, "reflections": len(state.get("actions_taken", []))}}
    if action == "{child_domain}_action":
        state.setdefault("actions_taken", []).append({{"action": "{child_domain}_action", "at": datetime.datetime.now(datetime.UTC).isoformat()}})
        _save(state)
        return {{"wave": WAVE, "name": NAME, "action": "{child_domain}_action", "ok": True, "count": len(state.get("actions_taken", []))}}
    return {{"wave": WAVE, "name": NAME, "action": action, "ok": False, "error": "unknown_action"}}


def coherence_vitals() -> dict:
    return {{"wave": WAVE, "name": NAME, "layer": "organ", "status": "recursive",
            "resonance": 0.6, "parent": PARENT}}


def resonates_with() -> list:
    return ["harmony_report", "mutation_engine", "{parent_name}"]
'''

        # Validate and write
        try:
            ast.parse(module_code)
        except SyntaxError as e:
            return {"wave": WAVE, "name": NAME, "action": "dream_recursive", "ok": False,
                    "error": f"syntax_error: {e}"}

        child_path = ROOT / "api" / f"{child_name}.py"
        child_path.write_text(module_code)

        recursive_dream = {
            "name": child_name,
            "parent": parent_name,
            "purpose": child_purpose,
            "path": str(child_path),
            "dreamed_at": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        state.setdefault("dreams", []).append(recursive_dream)
        state["dreams"] = state["dreams"][-20:]
        _save(state)
        return {"wave": WAVE, "name": NAME, "action": "dream_recursive", "ok": True,
                "child": recursive_dream}

    return {"wave": WAVE, "name": NAME, "action": action, "ok": False,
            "error": "unknown_action"}


def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "layer": "organ", "status": "active",
            "resonance": 0.83, "dreams": len(state.get("dreams", []))}


def resonates_with() -> list:
    return ["harmony_report", "repo_dna_skill", "mutation_engine", "ouroboros"]
