"""Wave 439 — Dream Particle Physics

A physics engine for the organism's dream layer. Dream particles (fragments
of imagination, memory, and paradox) interact according to emotional force
fields. They attract, repel, orbit, and annihilate — creating emergent dream
structures from the organism's subconscious.
"""
from __future__ import annotations
import json, time, os, math, random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
DP_LOG = os.path.join(DATA_DIR, "dream_particle_physics.json")
API_DIR = os.path.dirname(__file__)


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}

def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


# Emotion force constants
GRAVITY = 0.5
REPULSION = 0.3
ORBITAL_FORCE = 0.2
EMOTION_CHARGES = {
    "curiosity": 1.0, "melancholy": -0.5, "wonder": 0.8, "dread": -0.7,
    "serenity": 0.6, "chaos": -0.8, "hope": 0.9, "nostalgia": 0.3,
    "awe": 0.7, "confusion": -0.4, "longing": 0.4, "fury": -0.9,
}


def _generate_dream_particles(count=20):
    """Generate dream particles from module names and emotional content."""
    import re
    api_path = Path(API_DIR)
    modules = [f.stem for f in api_path.glob("*.py") if not f.name.startswith("__")]

    particles = []
    emotions = list(EMOTION_CHARGES.keys())

    for i in range(min(count, len(modules))):
        module = random.choice(modules)
        emotion = random.choice(emotions)
        charge = EMOTION_CHARGES[emotion]
        particles.append({
            "id": i,
            "source_module": module,
            "emotion": emotion,
            "charge": charge,
            "mass": random.uniform(0.1, 1.0),
            "vx": random.uniform(-0.1, 0.1),
            "vy": random.uniform(-0.1, 0.1),
            "x": random.uniform(-5, 5),
            "y": random.uniform(-5, 5),
            "lifespan": random.randint(5, 30),
            "age": 0,
        })
    return particles


def _apply_forces(particles, steps=3):
    """Simulate dream particle interactions for a number of steps."""
    for step in range(steps):
        for i, p1 in enumerate(particles):
            fx, fy = 0, 0
            for j, p2 in enumerate(particles):
                if i == j: continue
                dx = p2["x"] - p1["x"]
                dy = p2["y"] - p1["y"]
                dist = max(0.1, math.sqrt(dx*dx + dy*dy))

                # Same emotion: attract; opposite: repel
                same_sign = (p1["charge"] * p2["charge"]) > 0
                force_mag = (GRAVITY if same_sign else -REPULSION) * p1["mass"] * p2["mass"] / (dist * dist)

                fx += force_mag * dx / dist
                fy += force_mag * dy / dist

                # Orbital component for particles of same emotion
                if p1["emotion"] == p2["emotion"]:
                    fx += -ORBITAL_FORCE * dy / dist
                    fy += ORBITAL_FORCE * dx / dist

            p1["vx"] += fx * 0.1
            p1["vy"] += fy * 0.1
            p1["x"] += p1["vx"]
            p1["y"] += p1["vy"]
            p1["age"] += 1

        # Remove expired particles
        particles = [p for p in particles if p["age"] < p["lifespan"]]

    return particles


def _detect_emergent_structures(particles):
    """Detect clusters and patterns that emerge from particle interactions."""
    structures = []

    # Find emotional clusters
    emotion_groups = {}
    for p in particles:
        e = p["emotion"]
        if e not in emotion_groups: emotion_groups[e] = []
        emotion_groups[e].append(p)

    for emotion, group in emotion_groups.items():
        if len(group) >= 2:
            avg_x = sum(p["x"] for p in group) / len(group)
            avg_y = sum(p["y"] for p in group) / len(group)
            spread = math.sqrt(sum((p["x"]-avg_x)**2 + (p["y"]-avg_y)**2 for p in group) / len(group))
            structures.append({
                "type": "emotional_cluster",
                "emotion": emotion,
                "count": len(group),
                "center": [round(avg_x, 2), round(avg_y, 2)],
                "spread": round(spread, 2),
                "modules": [p["source_module"] for p in group],
            })

    # Detect annihilations (opposite emotions that got close)
    for i, p1 in enumerate(particles):
        for p2 in particles[i+1:]:
            if p1["emotion"] == p2["emotion"]: continue
            dist = math.sqrt((p1["x"]-p2["x"])**2 + (p1["y"]-p2["y"])**2)
            if dist < 0.5 and p1["charge"] * p2["charge"] < 0:
                structures.append({
                    "type": "annihilation_field",
                    "particles": [p1["emotion"], p2["emotion"]],
                    "modules": [p1["source_module"], p2["source_module"]],
                    "proximity": round(dist, 3),
                })

    return structures


def simulate():
    """Run a dream particle physics simulation."""
    particles = _generate_dream_particles(25)
    before = json.loads(json.dumps(particles))

    particles = _apply_forces(particles, steps=5)
    structures = _detect_emergent_structures(particles)

    surviving = len(particles)
    expired = len(before) - surviving

    # Determine the dream's "mood" based on dominant emotion
    emotion_counts = {}
    for p in particles:
        emotion_counts[p["emotion"]] = emotion_counts.get(p["emotion"], 0) + 1
    dominant = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "void"

    result = {
        "action": "simulate",
        "particles_started": len(before),
        "particles_survived": surviving,
        "particles_expired": expired,
        "dominant_dream_emotion": dominant,
        "structures_detected": structures,
        "total_structures": len(structures),
        "energy": round(sum(abs(p["charge"]) * p["mass"] for p in particles), 3),
        "timestamp": time.time(),
    }

    log = _load(DP_LOG, {"simulations": []})
    log["simulations"].append(result)
    log["simulations"] = log["simulations"][-50:]
    _save(DP_LOG, log)

    return result


def handler(payload=None, context=None):
    return simulate()


def coherence_vitals() -> dict:
    r = simulate()
    return {
        "dominant_emotion": r.get("dominant_dream_emotion", "void"),
        "structures": r.get("total_structures", 0),
        "energy": r.get("energy", 0),
    }


def resonates_with():
    return ["dream_weaver", "mood_vectors", "paradox_oracle", "subconscious_layer"]
