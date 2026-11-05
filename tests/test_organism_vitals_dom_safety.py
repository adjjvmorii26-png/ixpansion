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
