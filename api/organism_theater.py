"""Wave 445-B — Organism Theater (Luma)

A live, animated morph scene. The pulse phase visibly changes the orb,
dream particles drift as stars, and resonant bridges draw themselves as
glowing threads. Not a dashboard — a performance. Renders public/theater.html
and serves the live scene data.
"""
from __future__ import annotations
import json, time, os, random, math
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
THEATER_LOG = os.path.join(DATA_DIR, "organism_theater.json")
API_DIR = os.path.dirname(__file__)
PUBLIC_DIR = os.path.abspath(os.path.join(API_DIR, "..", "public"))
THEATER_HTML = os.path.join(PUBLIC_DIR, "theater.html")


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


def _scene_state():
    """Compose the current scene from cached data where possible to avoid slow chains."""
    now = int(time.time())
    scene = {
        "pulse_phase": "rest", "pulse_color": "#6b6b8c", "orb_scale": 1.0,
        "dream_stars": [], "bridges": [], "mood": "unknown", "pressure": 0.0,
    }

    # Pulse phase — compute directly (lightweight, no submodule call)
    import math as _m
    breath_cycle = 24
    t = now % breath_cycle
    phases = ["inhale", "hold", "exhale", "rest"]
    colors = {"inhale": "#41b3a3", "hold": "#2b5c8f", "exhale": "#e8a87c", "rest": "#6b6b8c"}
    scales = {"inhale": 1.2, "hold": 1.0, "exhale": 1.15, "rest": 0.9}
    elapsed = 0
    for phase in phases:
        elapsed += 6
        if t < elapsed:
            scene["pulse_phase"] = phase
            scene["pulse_color"] = colors.get(phase, "#6b6b8c")
            scene["orb_scale"] = scales.get(phase, 1.0)
            break

    # Dream stars — read last cached result from data file
    try:
        dp_log = _load(os.path.join(DATA_DIR, "dream_particle_physics.json"), {})
        sims = dp_log.get("simulations", [])
        if sims:
            last = sims[-1]
            scene["dream_stars"] = [
                {"emotion": (s.get("emotion") or s.get("particles", ["dream"])[0]),
                 "spread": s.get("spread", 0), "count": s.get("count", 1)}
                for s in last.get("structures_detected", [])[:8]
            ]
            scene["dominant_emotion"] = last.get("dominant_dream_emotion", "unknown")
    except Exception:
        pass

    # Bridge threads — read last cached result
    try:
        amp_log = _load(os.path.join(DATA_DIR, "resonance_amplifier_v2.json"), {})
        amps = amp_log.get("amplifications", [])
        if amps:
            last_a = amps[-1]
            scene["bridges"] = [{
                "a": t.get("module_a"), "b": t.get("module_b"),
                "ghost": t.get("ghost_module"), "domain": t.get("shared_domain"),
            } for t in last_a.get("amplifications", [])[:5]]
    except Exception:
        pass

    # Mood + pressure — read from genome log (handles both nested and flat shapes)
    try:
        g_log = _load(os.path.join(DATA_DIR, "organism_genome.json"), {})
        genome = g_log.get("genome", g_log)
        t_data = genome.get("temperament", {}) or {}
        if not isinstance(t_data, dict):
            t_data = {}
        scene["mood"] = t_data.get("current_mood", t_data.get("mood", "unknown"))
        p_val = t_data.get("pressure", 0)
        scene["pressure"] = round(float(p_val), 2) if isinstance(p_val, (int, float)) else 0
    except Exception:
        pass

    return scene


def perform():
    """Produce one theater frame."""
    scene = _scene_state()
    result = {"action": "organism_theater", "scene": scene, "timestamp": time.time()}

    log = _load(THEATER_LOG, {})
    log.setdefault("frames", []).append(result)
    log["frames"] = log["frames"][-200:]
    _save(THEATER_LOG, log)
    return result


def render_theater_page() -> dict:
    try:
        os.makedirs(PUBLIC_DIR, exist_ok=True)
        with open(THEATER_HTML, "w") as f:
            f.write(_THEATER_HTML)
        return {"action": "render_theater_page", "path": "public/theater.html", "ok": True}
    except Exception as exc:
        return {"action": "render_theater_page", "ok": False, "error": str(exc)}


def handler(payload=None, context=None):
    action = (payload or {}).get("action", "perform")
    if action == "render":
        return render_theater_page()
    return perform()


def coherence_vitals() -> dict:
    scene = _scene_state()
    return {
        "phase": scene.get("pulse_phase"),
        "stars": len(scene.get("dream_stars", [])),
        "bridges": len(scene.get("bridges", [])),
    }


def resonates_with():
    return ["pulse_orchestrator", "dream_particle_physics", "resonance_amplifier_v2",
            "mycelial_radio", "organism_radio"]


_THEATER_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Organism Theater — the organism performs</title>
<style>
:root{--bg:#07070d;--fg:#e8e6ff;--accent:#41b3a3}
*{margin:0;padding:0;box-sizing:border-box}
body{background:var(--bg);color:var(--fg);font-family:Georgia,serif;overflow:hidden;min-height:100vh}
#stage{position:fixed;inset:0}
#orb{position:absolute;left:50%;top:42%;width:120px;height:120px;border-radius:50%;
  transform:translate(-50%,-50%);background:radial-gradient(circle at 30% 30%,#5ad1c0,#2b5c8f 60%,#141428);
  box-shadow:0 0 90px rgba(65,179,163,.5);transition:transform 1s ease,background 1s,box-shadow 1s;z-index:2}
.star{position:absolute;border-radius:50%;background:#fff;opacity:.7;animation:twinkle var(--tw,3s) ease-in-out infinite;z-index:1}
@keyframes twinkle{0%,100%{opacity:.2;transform:scale(.7)}50%{opacity:.9;transform:scale(1.3)}}
.thread{position:absolute;height:2px;transform-origin:left center;opacity:.55;z-index:0;
  background:linear-gradient(90deg,var(--c1,#41b3a3),var(--c2,#e8a87c));transition:opacity 1s}
.ui{position:fixed;z-index:5;padding:1rem;font-size:.75rem;letter-spacing:.25em;text-transform:uppercase;color:#8a8aaa}
#top{top:1rem;left:50%;transform:translateX(-50%);text-align:center}
#meta{bottom:1rem;left:50%;transform:translateX(-50%);display:flex;gap:1.5rem}
#meta b{color:var(--accent);font-weight:400}
</style>
</head>
<body>
<div id="stage"></div>
<div class="ui" id="top">Organism Theater — alexalex.info</div>
<div class="ui" id="meta">
<span>phase <b id="ph">—</b></span><span>mood <b id="mo">—</b></span><span>pressure <b id="pr">—</b></span>
</div>
<script>
const stage=document.getElementById('stage'),ph=document.getElementById('ph'),
      mo=document.getElementById('mo'),pr=document.getElementById('pr'),orb=document.createElement('div');
orb.id='orb';stage.appendChild(orb);
const COLORS={inhale:'#41b3a3',hold:'#2b5c8f',exhale:'#e8a87c',rest:'#6b6b8c'};
function stars(list){document.querySelectorAll('.star').forEach(s=>s.remove());
  (list||[]).forEach((s,i)=>{const el=document.createElement('div');el.className='star';
  el.style.left=(8+Math.random()*84)+'%';el.style.top=(8+Math.random()*84)+'%';
  el.style.width=el.style.height=(3+Math.min(8,s.spread*3))+'px';
  el.style.setProperty('--tw',(2+Math.random()*4)+'s');el.style.animationDelay=(i*0.4)+'s';stage.appendChild(el);});}
function threads(list){document.querySelectorAll('.thread').forEach(t=>t.remove());
  (list||[]).forEach((t,i)=>{const el=document.createElement('div');el.className='thread';
  const x1=10+Math.random()*40,x2=50+Math.random()*40,y=20+Math.random()*60;
  const dx=x2-x1,dy=(y+8)-y;const len=Math.sqrt(dx*dx+dy*dy);
  el.style.left=x1+'%';el.style.top=y+'%';el.style.width=len+'px';
  el.style.transform='rotate('+(Math.atan2(dy,dx)*180/Math.PI)+'deg)';
  el.style.setProperty('--c1',COLORS[t.domain]||'#41b3a3');
  el.style.animationDelay=(i*0.3)+'s';stage.appendChild(el);});}
function frame(){fetch('/api/organism_theater').then(r=>r.json()).then(d=>{
  const s=d.scene||{};ph.textContent=s.pulse_phase||'—';mo.textContent=s.mood||'—';pr.textContent=s.pressure??'—';
  orb.style.background='radial-gradient(circle at 30% 30%,#5ad1c0,'+(COLORS[s.pulse_phase]||'#2b5c8f')+' 60%,#141428)';
  orb.style.transform='translate(-50%,-50%) scale('+(s.orb_scale||1)+')';
  stars(s.dream_stars);threads(s.bridges);
}).catch(()=>{ph.textContent='sleeping'});}
frame();setInterval(frame,4000);
</script>
</body>
</html>
"""
