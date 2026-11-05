from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dashboard" / "index.html"


class DashboardLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            href = dict(attrs).get("href")
            if href:
                self.hrefs.append(href)


def read_page():
    assert PAGE.is_file(), "dashboard entry page is missing"
    return PAGE.read_text(encoding="utf-8")


def test_dashboard_index_has_accessible_entry_landmarks():
    html = read_page()
    assert 'href="#main-content"' in html
    assert '<main id="main-content" tabindex="-1">' in html
    assert 'aria-label="Additional dashboard pages"' in html
    assert 'id="bgCanvas" aria-hidden="true"' in html


def test_dashboard_index_has_no_unverified_static_counters():
    html = read_page().lower()
    assert 'data-target="' not in html
    assert "wave 508" not in html
    assert "always free" not in html
    assert "coherence stable" not in html


def test_dashboard_index_motion_is_user_and_visibility_aware():
    html = read_page()
    assert "prefers-reduced-motion:reduce" in html
    assert "document.hidden" in html
    assert "visibilitychange" in html
    assert "cancelAnimationFrame" in html
    assert "distanceSquared" in html


def test_dashboard_index_local_links_resolve_to_repository_files():
    parser = DashboardLinks()
    parser.feed(read_page())
    missing = []
    for href in parser.hrefs:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        if parsed.path.startswith("/"):
            continue
        target = (PAGE.parent / parsed.path).resolve()
        if ROOT not in target.parents and target != ROOT:
            missing.append(href)
        elif not target.is_file():
            missing.append(href)
    assert not missing, f"broken dashboard links: {missing}"
