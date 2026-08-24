"""Constellation Atlas — compile the complete integration pipeline into one view."""
from __future__ import annotations

import math
from collections import defaultdict
from html import escape
from pathlib import Path
from typing import Any


CLASSIFICATION_COLORS = {
    "integrate_concept": "#38bdf8",
    "prototype_adapter": "#f59e0b",
    "preserve_reference": "#a3e635",
}


def _system_name(target: str) -> str:
    return target.split("/", 1)[0]


def compile_atlas(manifest: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run every Constellation stage and return a unified read-only model."""
    try:
        from .engine import canonical_hash, load_manifest, plan, resonance_graph
        from .loom import rehearse, weave
        from .recovery import recover
        from .treaties import negotiate
    except ImportError:
        from engine import canonical_hash, load_manifest, plan, resonance_graph
        from loom import rehearse, weave
        from recovery import recover
        from treaties import negotiate

    manifest = manifest or load_manifest()
    recommendations = plan(manifest)["recommendations"]
    graph = resonance_graph(manifest)
    ritual = weave(manifest)
    rehearsal = rehearse(ritual)
    recovery = recover(ritual, rehearsal)
    treaties = negotiate(recovery)

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in recommendations:
        grouped[_system_name(item["target"])].append(item)
    systems = [
        {
            "name": name,
            "concepts": len(items),
            "average_score": round(sum(item["score"] for item in items) / len(items), 2),
            "targets": sorted({item["target"] for item in items}),
        }
        for name, items in sorted(grouped.items())
    ]

    wave_views = []
    for wave in rehearsal["waves"]:
        wave_views.append({
            "phase": wave["phase"],
            "status": wave["status"],
            "passed": len(wave["passed"]),
            "rolled_back": len(wave["rolled_back"]),
            "quarantined": len(wave["quarantined"]),
        })

    treaty_by_pair = {
        tuple(party["thread"] for party in treaty["parties"]): treaty
        for treaty in treaties["treaties"]
    }
    braids = []
    for braid in recovery["braids"]:
        lane_names = [lane["thread"] for lane in braid["lanes"]]
        pair = tuple(sorted(lane_names))
        treaty = treaty_by_pair.get(pair)
        braids.append({
            "braid_id": braid["braid_id"],
            "shared_root": braid["shared_root"],
            "lanes": [
                {
                    "thread": lane["thread"],
                    "original_target": lane["original_target"],
                    "isolated_target": lane["isolated_target"],
                }
                for lane in braid["lanes"]
            ],
            "treaty_status": treaty["status"] if treaty else "unratified",
            "treaty_signature": treaty["signature"] if treaty else "",
        })

    source_hashes = {
        "corpus_hash": canonical_hash([item["name"] + item["version"] for item in manifest["repositories"]]),
        "graph_hash": graph["graph_hash"],
        "weave_hash": ritual["weave_hash"],
        "rehearsal_hash": rehearsal["rehearsal_hash"],
        "recovery_hash": recovery["recovery_hash"],
        "treaty_hash": treaties["treaty_hash"],
    }
    atlas_core = {
        "systems": systems,
        "recommendations": recommendations,
        "waves": wave_views,
        "braids": braids,
        "treaties": treaties["summary"],
        "rehearsal": rehearsal["summary"],
    }
    return {
        "schema": "aleph.constellation.atlas.v1",
        "experiment": "constellation-atlas",
        "source_hashes": source_hashes,
        "summaries": {
            "repositories": len(recommendations),
            "systems": len(systems),
            "threads": len(ritual["threads"]),
            "passed": rehearsal["summary"]["passed"],
            "rolled_back": rehearsal["summary"]["rolled_back"],
            "quarantined": rehearsal["summary"]["quarantined"],
            "braids": recovery["summary"]["braids"],
            "retry_orbits": recovery["summary"]["retry_orbits"],
            "treaties": treaties["summary"]["treaties"],
            "ratified_treaties": treaties["summary"]["ratified"],
        },
        **atlas_core,
        "atlas_hash": canonical_hash([source_hashes, atlas_core]),
    }


def _concept_points(recommendations: list[dict[str, Any]], width: int, height: int) -> list[dict[str, Any]]:
    center_x, center_y = width / 2, height / 2
    points = []
    total = len(recommendations)
    ordered = sorted(recommendations, key=lambda item: item["name"])
    for index, item in enumerate(ordered):
        angle = (index / total) * 6.283185307179586 - 1.5707963267948966
        orbit = 145 + (item["score"] % 5) * 4
        x = center_x + orbit * math.cos(angle)
        y = center_y + orbit * 0.72 * math.sin(angle)
        points.append({**item, "x": round(x, 2), "y": round(y, 2)})
    return points


def render_atlas(atlas: dict[str, Any]) -> str:
    """Render a dependency-free HTML/SVG mission atlas."""
    if atlas.get("schema") != "aleph.constellation.atlas.v1":
        raise ValueError("unsupported constellation atlas schema")

    width, height = 960, 520
    center_x, center_y = width / 2, height / 2
    points = _concept_points(atlas["recommendations"], width, height)
    metric_labels = (
        ("Repositories", "repositories"),
        ("Systems", "systems"),
        ("Passed", "passed"),
        ("Rolled Back", "rolled_back"),
        ("Quarantined", "quarantined"),
        ("Treaties", "ratified_treaties"),
    )

    metric_html = "".join(
        '<article class="metric"><span>{}</span><strong>{}</strong></article>'.format(
            escape(label), atlas["summaries"][key]
        )
        for label, key in metric_labels
    )
    edges = "".join(
        '<line class="edge" x1="{:.2f}" y1="{:.2f}" x2="{:.2f}" y2="{:.2f}" stroke-width="{:.2f}" stroke-opacity="{:.2f}" />'.format(
            center_x, center_y, point["x"], point["y"], max(0.5, point["score"] / 55), point["score"] / 130
        )
        for point in points
    )
    nodes = "".join(
        '<g class="concept"><circle class="concept-node" data-name="{name}" cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{color}" /><text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="{anchor}">{name}</text></g>'.format(
            name=escape(point["name"]),
            x=point["x"], y=point["y"], radius=max(2.5, point["score"] / 17),
            color=CLASSIFICATION_COLORS[point["classification"]],
            label_x=point["x"], label_y=point["y"] - (10 if point["y"] <= center_y else 16),
            anchor="middle",
        )
        for point in points
    )
    wave_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            wave["phase"], escape(wave["status"]), wave["passed"], wave["rolled_back"], wave["quarantined"]
        )
        for wave in atlas["waves"]
    )
    braid_cards = "".join(
        '<article class="braid"><header><h3>Braid {id}</h3><span class="{status}">{status}</span></header><p>Root: <code>{root}</code></p><ul>{lanes}</ul><footer>Treaty signature <code>{signature}</code></footer></article>'.format(
            id=escape(braid["braid_id"]), status=escape(braid["treaty_status"]),
            root=escape(braid["shared_root"]),
            lanes="".join("<li>{} → <code>{}</code></li>".format(escape(lane["thread"]), escape(lane["isolated_target"])) for lane in braid["lanes"]),
            signature=escape(braid["treaty_signature"]),
        )
        for braid in atlas["braids"]
    )
    hash_rows = "".join(
        "<tr><th>{}</th><td><code>{}</code></td></tr>".format(escape(key.replace("_", " ").title()), escape(value))
        for key, value in atlas["source_hashes"].items()
    )

    return """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Constellation Atlas</title>
<style>
:root{{color-scheme:dark;--ink:#dbeafe;--muted:#94a3b8;--panel:#0d1526;--line:#243b53;--accent:#38bdf8}}*{{box-sizing:border-box}}body{{margin:0;background:#050a14;color:var(--ink);font:14px/1.5 system-ui,sans-serif}}main{{max-width:1120px;margin:auto;padding:32px}}h1{{font-size:34px;margin:0}}h2{{margin-top:32px}}.lede,.muted{{color:var(--muted)}}.metrics{{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:10px;margin:22px 0}}.metric{{background:var(--panel);border:1px solid #21314c;border-radius:12px;padding:14px}}.metric span{{display:block;color:var(--muted);font-size:11px;text-transform:uppercase}}.metric strong{{font-size:23px}}svg,.panel{{width:100%;background:#071120;border:1px solid #20334f;border-radius:16px}}table{{width:100%;border-collapse:collapse;background:var(--panel);border-radius:12px;overflow:hidden}}th,td{{padding:9px;border-bottom:1px solid #1d2b41;text-align:left}}th{{color:var(--muted);font-weight:600}}.braids{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px}}.braid{{background:var(--panel);border:1px solid #223754;border-radius:13px;padding:15px}}.braid header{{display:flex;justify-content:space-between;align-items:center}}.braid h3{{margin:0;font-size:15px}}.ratified{{color:#67e8f9}}.rejected,.unratified{{color:#fb7185}}code{{color:#bae6fd}}footer{{margin-top:25px;color:var(--muted)}}
</style>
</head>
<body><main>
<header><p class="lede">ALEPH · deterministic merge-space observatory</p><h1>Constellation Atlas</h1><p class="lede">Every stage is replayable from its canonical hash.</p></header>
<section class="metrics" aria-label="Atlas summary">{metrics}</section>
<h2>Resonance Field</h2>
<svg viewBox="0 0 {width} {height}" role="img" aria-label="Radial resonance map of repository concepts">
<defs><radialGradient id="field"><stop offset="0" stop-color="#0c4a6e"/><stop offset="1" stop-color="#05101f"/></radialGradient></defs>
<rect width="{width}" height="{height}" fill="url(#field)" rx="18"/><circle cx="{cx:.2f}" cy="{cy:.2f}" r="58" fill="#082f49" stroke="#38bdf8"/><text x="{cx:.2f}" y="{cy:.2f}" text-anchor="middle" fill="#e0f2fe">IXpansion</text>{edges}{nodes}
</svg>
<p class="muted">Circle size encodes integration score; blue concepts are ready for contract fusion, amber require adapter prototypes.</p>
<h2>Shadow Waves</h2><div class="panel"><table><thead><tr><th>Phase</th><th>Status</th><th>Passed</th><th>Rolled back</th><th>Quarantined</th></tr></thead><tbody>{wave_rows}</tbody></table></div>
<h2>Recovery Braids &amp; Treaties</h2><div class="braids">{braids}</div>
<h2>Hash Chain</h2><div class="panel"><table><tbody>{hash_rows}<tr><th>Atlas Hash</th><td><code>{atlas_hash}</code></td></tr></tbody></table></div>
<footer>Generated deterministically by the Constellation Atlas · schema {schema}</footer>
</main></body></html>
""".format(
        metrics=metric_html, width=width, height=height, cx=center_x, cy=center_y,
        edges=edges, nodes=nodes, wave_rows=wave_rows, braids=braid_cards,
        hash_rows=hash_rows, atlas_hash=escape(atlas["atlas_hash"]), schema=escape(atlas["schema"]),
    )


def write_atlas(atlas: dict[str, Any], output: Path) -> dict[str, Any]:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(render_atlas(atlas), encoding="utf-8")
    return {"ok": True, "output": str(output), "atlas_hash": atlas["atlas_hash"]}
