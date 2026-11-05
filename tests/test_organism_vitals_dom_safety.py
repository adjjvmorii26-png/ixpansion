from pathlib import Path


def test_organism_vitals_uses_safe_dom_rendering():
    page = Path(__file__).resolve().parents[1] / "dashboard" / "organism-vitals.html"
    source = page.read_text(encoding="utf-8")

    # API-controlled values must be inserted as text, never parsed as markup.
    assert "innerHTML" not in source
    assert "outerHTML" not in source
    assert "insertAdjacentHTML" not in source
    assert "document.write" not in source
    assert "waveNode.textContent" in source
    assert "entry.append(" in source
    assert "document.createTextNode(String(msg ?? ''))" in source


def test_organism_vitals_clamps_untrusted_numeric_values():
    page = Path(__file__).resolve().parents[1] / "dashboard" / "organism-vitals.html"
    source = page.read_text(encoding="utf-8")

    assert "Number.isFinite(rawScore)" in source
    assert "Math.min(1, Math.max(0, rawScore))" in source
    assert "fill.style.width = `${score * 100}%`" in source
    assert "fill.style.backgroundColor = color" in source


def test_organism_vitals_rebuilds_cards_with_dom_nodes():
    page = Path(__file__).resolve().parents[1] / "dashboard" / "organism-vitals.html"
    source = page.read_text(encoding="utf-8")

    assert "document.createElement('div')" in source
    assert "card.replaceChildren(nameNode, waveNode, coherenceNode, bar)" in source
    assert "nameNode.textContent = name" in source


def test_organism_vitals_bounds_network_requests_and_log_growth():
    page = Path(__file__).resolve().parents[1] / "dashboard" / "organism-vitals.html"
    source = page.read_text(encoding="utf-8")

    assert "AbortController()" in source
    assert "REQUEST_TIMEOUT_MS = 8000" in source
    assert "if (!response.ok)" in source
    assert "response.headers.get(\"content-type\")" in source
    assert "MAX_LOG_ENTRIES = 100" in source
    assert "while (el.children.length > MAX_LOG_ENTRIES)" in source


def test_organism_vitals_stop_does_not_release_scan_lock_early():
    page = Path(__file__).resolve().parents[1] / "dashboard" / "organism-vitals.html"
    source = page.read_text(encoding="utf-8")
    stop_body = source.split("function stopScan()", 1)[1].split("\n}", 1)[0]

    assert "stopFlag = true" in stop_body
    assert "scanning = false" not in stop_body
    assert "if (autoRefresh) stopAutoRefresh()" in stop_body


def test_organism_vitals_refresh_and_keyboard_controls_are_explicit():
    page = Path(__file__).resolve().parents[1] / "dashboard" / "organism-vitals.html"
    source = page.read_text(encoding="utf-8")

    assert 'id="btn-auto" onclick="toggleAutoRefresh()"' in source
    assert "function toggleAutoRefresh()" in source
    assert "target.isContentEditable" in source
    assert "!e.repeat && !e.altKey && !e.ctrlKey && !e.metaKey" in source
    assert "On-demand API status checks" in source
    assert "Response Rate" in source
