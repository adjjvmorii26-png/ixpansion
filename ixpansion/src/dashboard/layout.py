from dashboard.views.glitch_view import render_glitches
from dashboard.views.mesh_view import render_mesh
from dashboard.views.timeline_view import render_timeline


def render_dashboard(timeline: list[dict]) -> str:
    latest = timeline[-1]
    return "\n".join((render_timeline(timeline), render_mesh(3), render_glitches(latest.get("anomalies", []))))
