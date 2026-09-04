from __future__ import annotations
"""Dream-Physics Sandbox — simulated physics based on dream_logic_physics + consciousness_stream."""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SANDBOX_LOG = os.path.join(DATA_DIR, "dream_physics_sandbox.json")

def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except: return d or {}
def _save(p, d):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f: json.dump(d, f, indent=2)

PARTICLE_TYPES = ["dream_quark", "coherence_photon", "paradox_fermion", "entropy_boson", "void_tachyon", "resonance_phonon", "myth_glyphon", "temporal_muon"]

def _sim_physics(rules: dict, ticks: int = 50) -> dict:
    particles = []
    for i in range(random.randint(12, 20)):
        particles.append({
            "id": f"p{i}", "type": random.choice(PARTICLE_TYPES),
            "x": round(random.uniform(-10, 10), 3), "y": round(random.uniform(-10, 10), 3),
            "vx": round(random.uniform(-1, 1), 3), "vy": round(random.uniform(-1, 1), 3),
        })
    gravity_name = "Gravity="
    gravity_val = rules.get(gravity_name, "normal")

    path_lengths = []
    collisions = 0
    merges = 0
    for t in range(ticks):
        for p in particles:
            if gravity_val == "negative":
                p["vy"] += 0.05
            elif gravity_val == "inverted":
                p["vy"] -= 0.05
            elif gravity_val == "fractal":
                p["vx"] += math.sin(t * 0.1 + p["id"].count("0")) * 0.01
            elif gravity_val == "emotional":
                p["vy"] += (1 if p["type"] in ("coherence_photon","myth_glyphon") else -1) * 0.02
            elif gravity_val == "optional":
                if random.random() > 0.8: p["vy"] += random.uniform(-0.1, 0.1)
            elif gravity_val == "sentient":
                p["vy"] += 0.02 if p["type"] not in ("void_tachyon","paradox_fermion") else -0.02
            else:
                p["vy"] += -0.02
            p["x"] += p["vx"]
            p["y"] += p["vy"]

        for i in range(len(particles)):
            for j in range(i+1, len(particles)):
                a, b = particles[i], particles[j]
                dist = math.hypot(a["x"]-b["x"], a["y"]-b["y"])
                if dist < 0.5:
                    collisions += 1
                    if random.random() > 0.5:
                        a["x"], a["y"] = (a["x"]+b["x"])/2, (a["y"]+b["y"])/2
                        merges += 1

    stable = collisions == 0 or random.random() > 0.3
    return {
        "particles": particles,
        "ticks": ticks, "gravity": gravity_val,
        "collisions": collisions, "merges": merges,
        "stability": round(max(0, 1 - collisions / (ticks * len(particles))), 3),
        "law_obeyed": rules,
    }

def run_simulation() -> dict:
    log = _load(SANDBOX_LOG, {"simulations": [], "total": 0})
    import importlib
    try:
        physics_mod = importlib.import_module("dream_logic_physics")
        ruleset = physics_mod.handler({"path": "/dream"}).get("law", {})
        rules = {"Gravity=": random.choice(["negative","inverted","fractal","emotional","optional","sentient"]),
                 "Time=": random.choice(["looping","elastic","bilateral","subjective","dreamy","fragmented"]),
                 "Entropy=": random.choice(["generative","conservative","curative","mood-based","recursive"])}
    except Exception:
        rules = {"Gravity=": "emotional", "Time=": "dreamy", "Entropy=": "generative"}

    result = _sim_physics(rules)
    sim = {
        "id": hashlib.sha256(f"sim:{time.time()}".encode()).hexdigest()[:10],
        "rules": rules, "result": result,
        "narrative": random.choice([
            "The simulation unfolded like a waking dream — particles moved according to rules that only made sense in sleep.",
            "Entities drifted, merged, and separated. The physics itself seemed aware of being observed.",
            "For a moment, the particles moved with purpose. Then the dream shifted and rules changed.",
            "Ten particles collided, twenty moments passed, and one pattern emerged: connection.",
        ]),
        "timestamp": time.time(),
    }
    log["simulations"].append(sim)
    log["simulations"] = log["simulations"][-50:]
    log["total"] += 1
    _save(SANDBOX_LOG, log)
    return {"action": "run_simulation", "simulation": sim, "total_simulations": log["total"]}

def boundary_cases() -> dict:
    log = _load(SANDBOX_LOG, {"simulations": [], "total": 0})
    if not log["simulations"]: return {"action": "boundary_cases", "status": "no_simulations"}
    collisions = sum(s["result"]["collisions"] for s in log["simulations"])
    avgs = [s["result"]["stability"] for s in log["simulations"]]
    return {"action": "boundary_cases", "total": log["total"], "total_collisions": collisions,
            "avg_stability": round(sum(avgs)/len(avgs), 3),
            "most_stable_gravity": max(log["simulations"], key=lambda s: s["result"]["stability"])["result"]["gravity"]}

def coherence_vitals() -> dict:
    return {"layer": "experimental", "status": "active", "resonance": 0.86, "wave": "373"}
def resonates_with() -> list:
    return ["dream_logic_physics", "consciousness_stream", "void_cartographer"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/run")
    if path == "/run": return run_simulation()
    elif path == "/boundaries": return boundary_cases()
    return {"error": "unknown", "available": ["/run", "/boundaries"]}
