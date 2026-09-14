"""Wave 641 — Fractal Garden.

Procedural art generated from the organism's module graph:
- Each module becomes a plant with fractal geometry
- Module resonance becomes garden proximity (neighbors bloom together)
- Coherence becomes color temperature
- Garden evolves each scan: plants grow, bloom, and seed new patterns
- Exports SVG "garden reports" — living art from living code
"""
import json, math, time, random, hashlib
from pathlib import Path

STATE = Path("data/wave641_fractal_garden.json")

def _load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {
        "garden": {},
        "artifacts": [],
        "season": "spring",
        "generations": 0,
        "tick": 0,
    }

def _save(s):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))

def _now():
    return time.time()

SEASONS = ["spring", "summer", "autumn", "winter"]

def _plant_seed(module_name, coherence=0.5, resonance=0):
    """Plant a module as a seed in the garden."""
    s = _load()
    seed_hash = int(hashlib.sha256(module_name.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed_hash)

    s["garden"][module_name] = {
        "plant_type": rng.choice(["fern", "blossom", "spiral", "coral", "lattice"]),
        "branches": rng.randint(3, 7),
        "depth": rng.randint(3, 6),
        "angle": rng.uniform(10, 30),
        "growth": 0.0,
        "coherence": coherence,
        "resonance": resonance,
        "planted_at": _now(),
        "season_born": s["season"],
    }
    _save(s)
    return {"ok": True, "module": module_name, "plant_type": s["garden"][module_name]["plant_type"]}

def _grow(iterations=10):
    """Grow all plants in the garden."""
    s = _load()
    s["tick"] += 1
    growths = []

    for name, plant in s["garden"].items():
        old = plant["growth"]
        # Growth speed tied to coherence
        plant["growth"] = min(1.0, plant["growth"] + (0.05 + plant["coherence"] * 0.08))
        if plant["growth"] > old:
            growths.append({"module": name, "growth": round(plant["growth"], 3), "type": plant["plant_type"]})

    # Season cycle
    if s["tick"] % 25 == 0:
        idx = SEASONS.index(s["season"]) if s["season"] in SEASONS else 0
        s["season"] = SEASONS[(idx + 1) % len(SEASONS)]

    _save(s)
    return {"ok": True, "tick": s["tick"], "season": s["season"], "grown": growths[:20], "total_plants": len(s["garden"])}

def _render_svg():
    """Render the garden as SVG art."""
    s = _load()
    plants = list(s["garden"].items())
    if not plants:
        # Seed a default plant for demo
        _plant_seed("wave641_fractal_garden", 0.8, 0)
        s = _load()
        plants = list(s["garden"].items())

    svg_parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">',
                 f'<rect width="1200" height="800" fill="#0a0a14"/>',
                 f'<text x="40" y="50" fill="#41b3a3" font-family="monospace" font-size="20">IXPANSION Fractal Garden — season: {s["season"]} — {len(plants)} plants</text>']

    for i, (name, p) in enumerate(plants):
        cols = 6
        row = i // cols
        col = i % cols
        cx = 150 + col * 180 + random.Random(i).uniform(-20, 20)
        cy = 150 + row * 220 + random.Random(i * 7).uniform(-20, 20)
        rng = random.Random(hashlib.sha256(name.encode()).hexdigest())

        # Color from coherence (cold blue → warm amber)
        coh = p.get("coherence", 0.5)
        r = int(40 + coh * 180)
        g = int(100 + (1 - coh) * 80)
        b = int(180 - coh * 100)

        # Trunk
        height = 30 + p["growth"] * 60
        svg_parts.append(f'<line x1="{cx}" y1="{cy}" x2="{cx}" y2="{cy - height}" stroke="rgb({r},{g},{b})" stroke-width="2"/>')

        # Branches (fractal recursion)
        def branch(x, y, angle_deg, length, depth):
            if depth <= 0 or length < 5:
                return
            ex = x + length * math.cos(math.radians(angle_deg))
            ey = y - length * math.sin(math.radians(angle_deg))
            svg_parts.append(f'<line x1="{x}" y1="{y}" x2="{ex}" y2="{ey}" stroke="rgb({r},{g},{b})" stroke-width="{max(1, depth)}"/>')
            spread = p.get("angle", 20)
            branch(ex, ey, angle_deg - spread, length * 0.7, depth - 1)
            branch(ex, ey, angle_deg + spread, length * 0.7, depth - 1)

        branch(cx, cy - height, 90, 40 * p["growth"], p.get("depth", 4))

        # Blossom at tip (if coherence high)
        if p["coherence"] > 0.6:
            tx = cx + 10 * math.cos(0.5)
            ty = cy - height - 30
            svg_parts.append(f'<circle cx="{tx}" cy="{ty}" r="4" fill="#ffcc66" opacity="0.8"/>')

    # Season overlay
    season_colors = {"spring": "#41d3a3", "summer": "#ffcc66", "autumn": "#e05a5a", "winter": "#6fa8dc"}
    svg_parts.append(f'<circle cx="1140" cy="40" r="12" fill="{season_colors.get(s["season"], "#41d3a3")}"/>')

    svg_parts.append('</svg>')
    svg = "\n".join(svg_parts)

    artifact = {
        "id": f"garden_{s['tick']}",
        "season": s["season"],
        "plants": len(plants),
        "generated_at": _now(),
        "svg_size": len(svg),
    }
    s["artifacts"].append(artifact)
    s["artifacts"] = s["artifacts"][-50:]
    s["generations"] += 1
    _save(s)

    return {"ok": True, "svg": svg, "artifact": artifact}

def _gallery():
    s = _load()
    return {"artifacts": s["artifacts"], "total": len(s["artifacts"]), "season": s["season"]}

def _status():
    s = _load()
    types = {}
    for p in s["garden"].values():
        types[p["plant_type"]] = types.get(p["plant_type"], 0) + 1
    return {
        "tick": s["tick"],
        "season": s["season"],
        "plants": len(s["garden"]),
        "plant_types": types,
        "artifacts": len(s["artifacts"]),
        "generations": s["generations"],
    }

def handler(req):
    action = req.get("action", "status")
    if action == "status":
        return {"ok": True, **_status()}
    elif action == "plant":
        return {"ok": True, **_plant_seed(req.get("module", "unnamed"), req.get("coherence", 0.5), req.get("resonance", 0))}
    elif action == "grow":
        return {"ok": True, **_grow(req.get("iterations", 10))}
    elif action == "render":
        return {"ok": True, **_render_svg()}
    elif action == "gallery":
        return {"ok": True, **_gallery()}
    return {"ok": False, "error": f"Unknown action: {action}"}

def coherence_vitals():
    s = _load()
    return {"wave": 641, "season": s["season"], "plants": len(s["garden"]), "artifacts": len(s["artifacts"])}

def resonates_with():
    return ["wave640_dependency_resolver", "wave635_coherence_gradient", "wave98_hex_cathedral"]
