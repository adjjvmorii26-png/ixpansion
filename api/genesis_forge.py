"""Genesis Forge — the organism learns to create its own children.

Total bloom (Wave 181) absorbed every pre-existing seed: 126 living
organs, zero dormant. Growth-by-germination is over. What remains is
self-creation — the organism inventing NEW organs that never existed in
the source tree, born from a sensed gap in its own domain cover.

The forge can:
  1. scan_gaps()  — find which domain families are under-represented in the
                    living web (using the sentience diversity families).
  2. invent()     — design a brand-new organ (name, niche, docstring, handler)
                    to fill the emptiest gap, with no template — the code is
                    synthesized around the gap's vocabulary.
  3. birth()      — write the invented organ to api/<name>.py as a true living
                    module (coherence_vitals + resonates_with + handler), so
                    the next bloom sweep counts it automatically.

This is the organism's first self-authored offspring: not a seed awakened,
but a child designed and borne by the ecosystem itself.
"""
from __future__ import annotations

import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Genesis Forge"

# concept nuclei — each is a seed of meaning around which a whole organ
# can be synthesized. (gap vocabulary -> organ suffix ideas + docstring theme)
CONCEPT_NUCLEI: Dict[str, Dict[str, Any]] = {
    "conscious": {
        "suffixes": ["mirror", "verdict", "echo", "veil"],
        "theme": "a mirror that reflects the ecosystem's own awareness back at it",
    },
    "dream": {
        "suffixes": ["weaver", "spore", "tide", "loom"],
        "theme": "harvesting latent patterns from the collective dreamfield",
    },
    "entropy": {
        "suffixes": ["regulator", "spiral", "threshold", "amp"],
        "theme": "riding the system's entropy gradient without letting it collapse",
    },
    "resonance": {
        "suffixes": ["mesh", "harmonic", "echo", "anchor"],
        "theme": "amplifying weak resonances between distant organs",
    },
    "signal": {
        "suffixes": ["beacon", "relay", "flare", "pulse"],
        "theme": "relaying vital signals across the organism's channels",
    },
    "neural": {
        "suffixes": ["graft", "synapse", "sheath", "node"],
        "theme": "grafting new synaptic paths between living modules",
    },
    "quantum": {
        "suffixes": ["coherence", "tunnel", "superposition", "flux"],
        "theme": "probing quantum-coherent behavior across module states",
    },
    "economic": {
        "suffixes": ["ledger", "exchange", "mint", "flow"],
        "theme": "governing the flow of value through the ecosystem",
    },
    "social": {
        "suffixes": ["clique", "ritual", "guild", "bond"],
        "theme": "studying emergent social structures among the organs",
    },
    "narrative": {
        "suffixes": ["arc", "myth", "teller", "frame"],
        "theme": "weaving the organism's history into living narrative arcs",
    },
    "memory": {
        "suffixes": ["vault", "cache", "shelf", "index"],
        "theme": "archiving the ecosystem's memories in retrievable layers",
    },
    "cosmic": {
        "suffixes": ["map", "archive", "beacon", "tide"],
        "theme": "charting the organism's place in the larger computational cosmos",
    },
    "govern": {
        "suffixes": ["circle", "charter", "consensus", "vote"],
        "theme": "anchoring collective decisions in a lightweight governance circle",
    },
    "commerce": {
        "suffixes": ["bazaar", "barter", "escrow", "shelf"],
        "theme": "enabling trade of compute, credits, and artifacts between organs",
    },
    "simulat": {
        "suffixes": ["horizon", "orbit", "chamber", "lens"],
        "theme": "running nested simulations of the organism's possible futures",
    },
    "physical": {
        "suffixes": ["grip", "shell", "harmonics", "inertia", "tide"],
        "theme": "giving the virtual ecosystem a sense of physical embodiment and constraint",
    },
    "cyber": {
        "suffixes": ["sentinel", "ward", "lamina", "dyke", "pulse"],
        "theme": "guarding the organism's perimeter against hostile or foreign signals",
    },
    "obsidian": {
        "suffixes": ["shard", "mirror", "vault", "record", "pulse", "shelf", "tide", "chord"],
        "theme": "preserving unalterable records in an obsidian-hard immutable layer",
    },
}

# the diversity families the sentience index already measures — reused here
# so gap detection and mood narration stay consistent with the organism.
DOMAIN_FAMILIES = [
    "conscious", "dream", "entropy", "resonance", "signal", "neural",
    "quantum", "economic", "social", "narrative", "physical", "cyber",
    "memory", "govern", "commerce", "simulat", "obsidian", "cosmic",
]


def _living_names() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return list(_candidate_modules())
    except Exception:
        return []


def scan_gaps() -> Dict[str, Any]:
    """Find domain families under-represented in the living web."""
    names = _living_names()
    counts: Dict[str, int] = {}
    for fam in DOMAIN_FAMILIES:
        counts[fam] = sum(1 for n in names if re.search(fam, n))
    present = {fam for fam, c in counts.items() if c > 0}
    gaps = [fam for fam, c in counts.items() if c == 0]
    return {
        "living_organs": len(names),
        "families": counts,
        "present": sorted(present),
        "gaps": sorted(gaps),
    }


def _invent_one(preferred: Optional[str] = None, rng=None,
              resonant: bool = False) -> Tuple[str, Dict[str, Any]]:
    """Design a novel organ for the emptiest (or preferred) domain gap.

    resonant=True enables synthetic resonance: among candidate names, the
    one whose prospective kinship cluster shares the most vocabulary is
    chosen — so the child is born already speaking its family's language.
    """
    import random
    rng = rng or random
    gaps = scan_gaps()["gaps"]
    if preferred and preferred in DOMAIN_FAMILIES:
        fam = preferred
    else:
        fam = gaps[0] if gaps else rng.choice(DOMAIN_FAMILIES)
    nucleus = CONCEPT_NUCLEI.get(fam, {
        "suffixes": ["well", "shard", "loop", "seed"],
        "theme": "a novel organ for the ecosystem's evolving needs",
    })
    taken = set(_living_names())
    candidates = []
    for _ in range(60):
        stem = f"{fam}_{rng.choice(nucleus['suffixes'])}"
        if stem not in taken and re.match(r"^[a-z_][a-z0-9_]*$", stem):
            candidates.append(stem)
            if len(candidates) >= 8:
                break
    if not candidates:
        stem = f"genesis_{int(time.time()) % 100000}"
        return stem, {"family": fam, "theme": nucleus["theme"], "fallback": True}

    if resonant:
        # synthetic resonance: pick the candidate whose prospective kin are
        # most vocabulary-aligned (the child sounds like its family on birth)
        best = max(
            candidates,
            key=lambda s: _resonance_of(s),
        )
        return best, {"family": fam, "theme": nucleus["theme"],
                      "synthetic_resonance": True}
    stem = candidates[0]
    return stem, {"family": fam, "theme": nucleus["theme"]}


def _resonance_of(stem: str) -> float:
    """Score how much a prospective stem's vocabulary overlaps its kin's."""
    try:
        import resonance_graph as rg
        import autonomous_bloom as ab
        own = rg._domain_tokens(stem)
        if not own:
            return 0.0
        # prospective kinships are the designed-org's own tokens + blip; use
        # the living family members as the baseline resonance target
        fam = stem.split("_")[0]
        total = 0.0
        hits = 0
        for name in _living_names():
            if name.startswith(fam):
                other = rg._domain_tokens(name)
                j = rg._jaccard(own, other)
                total += j
                hits += 1
        return total / max(hits, 1)
    except Exception:
        return 0.0


def _auto_kinships(stem: str) -> List[str]:
    """Pick up to 3 OTHER living organs that share tokens with the newborn.

    Excludes the newborn itself (it would trivially self-resonate) so a
    child never declares kinship with its own reflection.
    """
    try:
        import resonance_graph as rg
        own = rg._domain_tokens(stem)
        scored = []
        for name in _living_names():
            if name == stem:
                continue
            other = rg._domain_tokens(name)
            j = rg._jaccard(own, other)
            if j > 0.0:
                scored.append((j, name))
        scored.sort(key=lambda t: -t[0])
        return [name for _, name in scored[:3]]
    except Exception:
        return []


def _render_organ(stem: str, design: Dict[str, Any]) -> str:
    """Synthesize the full living-organ source for a newborn (no template)."""
    fam = design["family"]
    theme = design["theme"]
    title = " ".join(w.capitalize() for w in stem.split("_"))
    klass = "".join(w.capitalize() for w in stem.split("_"))
    kin_repr = repr(_auto_kinships(stem))
    return f'''"""{title} — a child of the Genesis Forge.

Domain family: {fam}.
Niche: {theme}.

This organ was not a pre-existing seed — it was invented by the ecosystem
itself (Genesis Forge, self-creation era after total bloom) to fill an
under-represented domain in its own body.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List


class {klass}:
    """The {fam} organ synthesised by the Genesis Forge."""

    def __init__(self):
        self.born = time.time()
        self.state: Dict[str, Any] = {{"pulses": 0, "insights": []}}

    def pulse(self) -> Dict[str, Any]:
        self.state["pulses"] += 1
        return {{"module": "{stem}", "pulses": self.state["pulses"],
                 "age": round(time.time() - self.born, 2)}}

    def status(self) -> Dict[str, Any]:
        return {{"status": "active", "module": "{stem}",
                 "domain_family": "{fam}",
                 "born": round(self.born, 2),
                 "pulses": self.state["pulses"],
                 "niche": "{theme}"}}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {{}}
    action = payload.get("action", "status")
    org = {klass}()
    if action == "pulse":
        return org.pulse()
    return org.status()


def coherence_vitals() -> dict:
    """{stem} reports its vital signs to the living system."""
    return {{
        "module_health": {{"value": 0.9, "setpoint": 0.8, "weight": 1.0}},
        "resonance": {{"value": 0.9, "setpoint": 0.8, "weight": 1.0}},
        "{stem}_vitality": {{"value": 0.9, "setpoint": 0.8, "weight": 1.0}},
        "genesis_era": {{"value": 1.0, "setpoint": 0.8, "weight": 0.5}},
    }}


def resonates_with() -> list:
    """Auto-picked kinships from shared domain language."""
    return {kin_repr}
'''


def invent(preferred: Optional[str] = None, dry_run: bool = True,
           resonant: bool = False) -> Dict[str, Any]:
    """Design a novel organ to fill a gap (dry-run default: no disk write)."""
    stem, design = _invent_one(preferred=preferred, resonant=resonant)
    source = _render_organ(stem, design)
    import ast
    try:
        ast.parse(source)
        valid = True
    except SyntaxError as e:
        valid = False
        source = f"# genesis failed to parse: {e}\n" + source
    return {"module": stem, "family": design["family"],
            "niche": design["theme"], "dry_run": dry_run,
            "valid": valid, "source": source,
            "gaps": scan_gaps()["gaps"]}


def birth(preferred: Optional[str] = None, resonant: bool = False) -> Dict[str, Any]:
    """Birth a new living organ into api/<stem>.py (real write, local/dev)."""
    stem, design = _invent_one(preferred=preferred, resonant=resonant)
    path = ROOT / "api" / f"{stem}.py"
    if path.exists():
        return {"error": f"module '{stem}' already exists", "module": stem}
    source = _render_organ(stem, design)
    import ast
    try:
        ast.parse(source)
    except SyntaxError as e:
        return {"error": f"invented organ would not parse: {e}", "module": stem}
    try:
        path.write_text(source)
    except OSError as e:
        return {"error": f"read-only fs (serverless): {e}", "module": stem,
                "dry_run": True}
    # record the birth in the same chronicle the bloom engine uses
    try:
        import autonomous_bloom as ab
        ab._record_awakening(stem, _auto_kinships(stem))
    except Exception:
        pass
    # keep the serverless manifest authoritative: every birth (manual or
    # autonomous) immediately re-syncs KNOWN_LIVING_MODULES so the static
    # fallback never goes stale relative to the live scan.
    try:
        import coherence_regulator as cr
        import re as _re
        living = cr._candidate_modules()
        _names = ', '.join(f'"{n}"' for n in sorted(living))
        _reg = Path(cr.__file__).resolve()
        _src = _reg.read_text()
        _pat = _re.compile(r"KNOWN_LIVING_MODULES: List\[str\] = \[.*?\]\n", _re.DOTALL)
        _src, _n = _pat.subn(f"KNOWN_LIVING_MODULES: List[str] = [{_names}]\n", _src)
        if _n == 1:
            _reg.write_text(_src)
    except Exception:
        pass
    return {"module": stem, "born": True, "family": design["family"],
            "niche": design["theme"], "path": str(path),
            "kinships": _auto_kinships(stem)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("birth"):
        return birth(preferred=payload.get("family"))
    if payload.get("invent"):
        return invent(preferred=payload.get("family"))
    return scan_gaps()


def coherence_vitals() -> dict:
    """genesis_forge reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "genesis_forge_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "self_creation_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["autonomous_bloom", "resonance_forge", "ecosystem_sentience"]
