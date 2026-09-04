"""
Resonance Gallery — Wave 375
Every module of the organism is also a living portrait. This module renders
any module's state as procedural SVG art — a unique visual signature derived
from the same entropy that drives its behavior. The gallery is the organism
painting itself.
"""
import json, time, hashlib, os, random, math

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
GALLERY_LOG = os.path.join(DATA_DIR, "resonance_gallery.json")

PALETTES = {
    "hex_dark":   ["#0b0b14", "#7c7cf8", "#2dd4bf", "#fbbf24", "#a78bfa", "#22d3ee"],
    "genesis":    ["#0a0f0a", "#4ade80", "#facc15", "#1a0f29", "#c8a8ff", "#2dd4bf"],
    "underworld": ["#05040a", "#8f3dff", "#38bdf8", "#f97316", "#64748b", "#e879f9"],
    "dream":      ["#0d0221", "#c084fc", "#f0abfc", "#67e8f9", "#fde68a", "#5eead4"],
    "mood":       ["#100f14", "#ff6b6b", "#ffd93d", "#6bcb77", "#4d96ff", "#b980f0"],
}
SHAPES = ["orbit", "spires", "rings", "lattice", "burst", "meander", "glyph_grid", "fractal_wave"]


def _sig(module: str = None, seed: str = None) -> int:
    raw = f"{module or 'organism'}:{seed or ''}:{time.strftime('%Y%m%d')}"
    return int(hashlib.sha256(raw.encode()).hexdigest()[:12], 16)


def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f:
                return json.load(f)
        except Exception:
            pass
    return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


def _svg(sig: int, module: str, palette: list, shape: str, size: int = 480) -> str:
    rng = random.Random(sig)
    c = palette
    bg = c[0]
    n = 18 + (sig % 24)
    parts = []
    for i in range(n):
        x = rng.uniform(8, size - 8)
        y = rng.uniform(8, size - 8)
        r = rng.uniform(2, 9)
        col = c[1 + int(rng.random() * (len(c) - 1))]
        op = round(rng.uniform(0.35, 0.95), 2)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" fill-opacity="{op}"/>')
    # shape-specific glyphs
    cx, cy = size / 2, size / 2
    if shape in ("orbit", "rings", "burst", "fractal_wave"):
        for k in range(1, 8):
            rr = k * size / 16
            col = c[1 + (k * 7) % (len(c) - 1)]
            parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{rr:.1f}" fill="none" stroke="{col}" stroke-opacity="0.5" stroke-width="1"/>')
    if shape in ("spires", "lattice", "meander", "glyph_grid"):
        for k in range(1, 9):
            yy = k * size / 9
            col = c[1 + (k * 5) % (len(c) - 1)]
            parts.append(f'<line x1="0" y1="{yy:.1f}" x2="{size}" y2="{yy:.1f}" stroke="{col}" stroke-opacity="0.35" stroke-width="1"/>')
    if shape in ("spires", "burst", "fractal_wave"):
        for k in range(10):
            ang = rng.uniform(0, math.tau)
            col = c[1 + int(rng.random() * (len(c) - 1))]
            parts.append(
                f'<line x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx + math.cos(ang) * size * 0.42:.1f}" '
                f'y2="{cy + math.sin(ang) * size * 0.42:.1f}" stroke="{col}" stroke-opacity="0.4" stroke-width="1"/>'
            )
    glyphs = [
        '❖', '◈', '◇', '✧', '✦', '⬡', '⌘', '∞', '∴', '⟡', '▲', '●'
    ]
    g = glyphs[sig % len(glyphs)]
    parts.append(
        f'<text x="{cx:.1f}" y="{cy + 12:.1f}" font-size="46" fill="{c[2]}" fill-opacity="0.85" '
        f'text-anchor="middle">{g}</text>'
    )
    title = module.replace("_", " ").title()
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<rect width="{size}" height="{size}" fill="{bg}"/>'
        + "".join(parts)
        + f'<text x="16" y="{size - 16}" font-size="13" fill="{c[2]}" fill-opacity="0.9" font-family="monospace">{title} · {shape}</text>'
        + "</svg>"
    )
    return svg


def generate(module: str = None, seed: str = None, palette: str = "hex_dark") -> dict:
    sig = _sig(module, seed)
    rng = random.Random(sig)
    pal = PALETTES.get(palette, PALETTES["hex_dark"])
    shape = SHAPES[sig % len(SHAPES)]
    svg = _svg(sig, module or "organism", pal, shape)
    title = (module or "organism").replace("_", " ").title()
    description = (
        f"A {shape} rendering of {title or 'the organism'}, "
        f"seeded by {palette if palette else 'the organism'} — sig {sig:x}."
    )
    art = {
        "id": f"{sig:012x}",
        "module": module or "organism",
        "title": title,
        "shape": shape,
        "palette": palette,
        "seed": seed,
        "svg": svg,
        "description": description,
        "timestamp": time.time(),
    }
    log = _load(GALLERY_LOG, {"portraits": [], "total": 0})
    log["portraits"] = (log["portraits"] + [art])[-100:]
    log["total"] += 1
    _save(GALLERY_LOG, log)
    return {"action": "generate", "art": art, "total_portraits": log["total"]}


def collection() -> dict:
    log = _load(GALLERY_LOG, {"portraits": [], "total": 0})
    return {"action": "collection", "portraits": log["portraits"][::-1][:24], "total": log["total"]}


def palettes() -> dict:
    return {"action": "palettes", "palettes": list(PALETTES.keys())}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/generate")
    if path == "/generate":
        return generate(payload.get("module"), payload.get("seed"), payload.get("palette"))
    if path == "/collection":
        return collection()
    if path == "/palettes":
        return palettes()
    return {"error": "unknown", "available": ["/generate", "/collection", "/palettes"]}
