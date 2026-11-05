from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "organism-vitals.html"

# Source-to-sink map
#   GET /api/{module}?action=status
#     d.wave              -> .wave textContent via String()
#     d.coherence_score   -> .coherence textContent after Number() clamp
#     d.message           -> results.error only; renderCard never reads it
#   local scan strings    -> log row via createElement + createTextNode
# Hostile values that used to become markup:
#   wave: <img src=x onerror="alert(1)">
#   message: <script>alert(1)</script>


def read_page():
    assert PAGE.is_file(), "organism vitals page is missing"
    return PAGE.read_text(encoding="utf-8")


def slice_between(html, start, end):
    return html[html.index(start) : html.index(end)]


def test_organism_vitals_has_no_html_injection_sink():
    html = read_page()
    assert "innerHTML" not in html
    assert "insertAdjacentHTML" not in html
    assert "document.write" not in html
    assert "outerHTML" not in html


def test_organism_vitals_card_writes_api_fields_as_text():
    html = read_page()
    card = slice_between(html, "function renderCard", "async function startScan")
    assert "`" not in card
    assert "String(r.wave)" in card
    assert "Number(r.coherence)" in card
    assert "textNode(" in card
    assert "d.message" not in card
    assert "r.message" not in card
    assert "r.error" not in card


def test_organism_vitals_log_appends_text_nodes():
    html = read_page()
    log = slice_between(html, "function addLog", "async function scanModule")
    assert "`" not in log
    assert "createTextNode" in log
    assert "textContent" in log
