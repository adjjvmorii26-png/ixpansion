from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "index.html"


class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.h1_count = 0
        self.nav_labels = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "nav" and attrs.get("aria-label"):
            self.nav_labels.append(attrs["aria-label"])


def read_page():
    assert PAGE.is_file(), "public homepage is missing"
    return PAGE.read_text(encoding="utf-8")


def test_homepage_has_language_title_and_description():
    html = read_page()
    assert re.search(r"<html\\s+lang=[\"']en[\"']", html, re.I)
    assert re.search(r"<title>[^<]+</title>", html, re.I)
    assert re.search(r'<meta\\s+name=[\"']description[\"']', html, re.I)


def test_homepage_has_one_heading_and_keyboard_entry_point():
    html = read_page()
    parser = PageLinks()
    parser.feed(html)
    assert parser.h1_count == 1
    assert 'href="#main-content"' in html
    assert '<main id="main-content" tabindex="-1">' in html
    assert parser.nav_labels


def test_homepage_does_not_publish_unverified_live_counts():
    html = read_page().lower()
    stale_claims = (
        "937 modules",
        "148 dashboards",
        "93 tests passing",
        "15 waves deep",
        "every dashboard is live",
        "organism alive",
        "coherence stable",
    )
    for claim in stale_claims:
        assert claim not in html


def test_homepage_local_links_resolve_to_repository_files():
    parser = PageLinks()
    parser.feed(read_page())
    missing = []
    for href in parser.links:
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        target = (ROOT / parsed.path).resolve()
        if ROOT not in target.parents and target != ROOT:
            missing.append(href)
        elif not target.is_file():
            missing.append(href)
    assert not missing, f"broken local homepage links: {missing}"


def test_homepage_respects_reduced_motion_preference():
    html = read_page()
    assert "prefers-reduced-motion:reduce" in html
