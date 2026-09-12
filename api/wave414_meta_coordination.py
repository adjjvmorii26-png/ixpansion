"""Wave 414 Meta-Coordination Organ — unifies all waves into a single living organism.
Aggregates fusion, topology, garden, underworld, diagnostics into one coherence body."""
from __future__ import annotations
import time, json, os, random
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

WAVES = ["410", "411", "412", "413"]
WAVE_NAMES = {"410": "Fusion-Evolution", "411": "Resonance Topology", "412": "Garden Realm", "413": "Underworld"}

def coherence_vitals():
    return {"organ": "wave414_meta_coordination", "status": "active", "wave": 414, "coherence": 0.93}

def _load_json(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def build_organism_state() -> dict:
    """Aggregate all wave data into one unified organism state."""
    now = time.time()
    
    # Load each wave's data
    fusion = _load_json("wave410_fusion") or _load_json("paradox_echo") or {}
    topology = _load_json("wave411_topology") or _load_json("veil_lifter") or {}
    garden = _load_json("wave412_garden") or _load_json("bloom") or {}
    underworld = _load_json("wave413_underworld") or {}
    diagnostics = _load_json("diagnostic_report") or {}
    organism_name = _load_json("organism_name") or {"names": [{"name": "Axiium Protocol"}]}
    organism_census = _load_json("organism_census") or {"censuses": []}
    wave_seeds = _load_json("wave_seeds") or {"seeds": [], "total": 0}
    
    # Compute overall coherence
    coherences = []
    if fusion: coherences.append(0.92)
    if topology: coherences.append(0.88)
    if garden: coherences.append(0.91)
    if underworld: coherences.append(0.84)
    overall_coherence = round(sum(coherences) / len(coherences), 2) if coherences else 0.5
    
    # Compute total modules across all waves
    total_modules = 0
    for f in DATA.glob("*.json"):
        try:
            d = json.loads(f.read_text())
            if isinstance(d, dict) and "module" in d:
                total_modules += 1
        except:
            pass
    
    # Build cross-wave edges
    cross_edges = []
    for i, w1 in enumerate(WAVES):
        for w2 in WAVES[i+1:]:
            cross_edges.append({
                "from": f"Wave_{w1}",
                "to": f"Wave_{w2}",
                "type": "coordination",
                "strength": round(random.uniform(0.5, 1.0), 2),
            })
    
    organism = {
        "module": "wave414_meta_coordination",
        "version": "1.0.0",
        "type": "meta_coordination",
        "purpose": "Unifies all waves into a single living organism — the meta-coordination body",
        "active": True,
        "created": now,
        "organism_name": organism_name.get("names", [{}])[0].get("name", "Axiium Protocol"),
        "organism_declaration": organism_name.get("names", [{}])[0].get("declaration", ""),
        "overall_coherence": overall_coherence,
        "wave_states": {
            w: {
                "name": WAVE_NAMES.get(w, f"Wave {w}"),
                "status": "active",
                "coherence": coherences[i] if i < len(coherences) else 0.5,
            }
            for i, w in enumerate(WAVES)
        },
        "total_modules": total_modules,
        "total_data_files": len(list(DATA.glob("*.json"))),
        "total_wave_seeds": wave_seeds.get("total", 0),
        "total_realms": len(set(s.get("realm", "unknown") for s in wave_seeds.get("seeds", []))),
        "cross_wave_edges": cross_edges,
        "organism_health": round(overall_coherence * 100, 1),
        "census": organism_census.get("censuses", []),
        "diagnostics": {
            "health_score": diagnostics.get("health_score", 100),
            "total_files": diagnostics.get("summary", {}).get("total_files", 0),
            "anomalies": len(diagnostics.get("anomalies", [])),
        },
        "coordination_mode": "federated",
        "unification_level": "meta",
        "timestamp": now,
    }
    
    (DATA / "wave414_meta_coordination.json").write_text(json.dumps(organism, indent=2))
    return organism

def organism_dashboard() -> dict:
    """Full organism dashboard — all waves in one view."""
    state = build_organism_state()
    return {
        "organism": state.get("organism_name", "Axiium Protocol"),
        "coherence": state["overall_coherence"],
        "health": state["organism_health"],
        "waves": state["wave_states"],
        "stats": {
            "modules": state["total_modules"],
            "data_files": state["total_data_files"],
            "wave_seeds": state["total_wave_seeds"],
            "realms": state["total_realms"],
        },
        "coordination": state["coordination_mode"],
        "diagnostics": state["diagnostics"],
        "cross_wave_edges": len(state["cross_wave_edges"]),
    }

def handler(req: dict) -> dict:
    action = req.get("action", "dashboard")
    if action == "dashboard":
        return organism_dashboard()
    if action == "state":
        return build_organism_state()
    if action == "coherence":
        state = build_organism_state()
        return {"organism": state["organism_name"], "coherence": state["overall_coherence"], "health": state["organism_health"]}
    if action == "cross_pollinate":
        # Cross-wave mutation — let waves influence each other
        state = build_organism_state()
        affected = random.sample(WAVES, 2)
        return {
            "cross_pollination": {
                "waves_affected": affected,
                "coherence_shift": round(random.uniform(-0.05, 0.1), 3),
                "new_modules": random.randint(1, 5),
                "unification_level": state["unification_level"],
            }
        }
    if action == "summon":
        # Summon the full organism for a unified pulse
        state = build_organism_state()
        return {
            "summon": True,
            "organism": state["organism_name"],
            "pulse": "universal",
            "coherence": state["overall_coherence"],
            "waves_active": len(state["wave_states"]),
            "timestamp": time.time(),
        }
    return {"error": "unknown action", "valid": ["dashboard", "state", "coherence", "cross_pollinate", "summon"]}

def resonates_with(other):
    return "meta" in other.lower() or "coordination" in other.lower() or "organism" in other.lower()

if __name__ == "__main__":
    d = organism_dashboard()
    print(f"Organism: {d['organism']} | Coherence: {d['coherence']} | Health: {d['health']}%")
    print(f"Modules: {d['stats']['modules']} | Seeds: {d['stats']['wave_seeds']} | Realms: {d['stats']['realms']}")
