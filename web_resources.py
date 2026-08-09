"""Bounded, cookie-free collection of public web page resources."""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Iterable, Optional
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from security_controls import URLPolicy


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.title = ""
        self._in_title = False
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, Optional[str]]]) -> None:
        normalized = tag.casefold()
        if normalized in {"script", "style", "noscript", "template"}:
            self._ignored_depth += 1
        if normalized == "title":
            self._in_title = True
        if normalized == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)

    def handle_endtag(self, tag: str) -> None:
        normalized = tag.casefold()
        if normalized == "title":
            self._in_title = False
        if normalized in {"script", "style", "noscript", "template"} and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._ignored_depth:
            return
        cleaned = " ".join(data.split())
        if not cleaned:
            return
        if self._in_title:
            self.title = f"{self.title} {cleaned}".strip()
        self.parts.append(cleaned)


class PublicResourceCollector:
    """Fetch allowlisted public pages without sending browser credentials."""

    def __init__(
        self,
        policy: URLPolicy,
        *,
        timeout: float = 10.0,
        max_bytes: int = 1_000_000,
    ) -> None:
        if timeout <= 0 or max_bytes <= 0:
            raise ValueError("timeout and max_bytes must be positive")
        self.policy = policy
        self.timeout = timeout
        self.max_bytes = max_bytes

    def collect(self, url: str) -> dict[str, object]:
        self.policy.validate(url)
        request = Request(
            url,
            headers={"Accept": "text/html,text/plain;q=0.9", "User-Agent": "IXPANSION-resource-collector/1.0"},
        )
        opener = build_opener(_NoRedirectHandler)
        with opener.open(request, timeout=self.timeout) as response:
            final_url = response.geturl()
            self.policy.validate(final_url)
            content_type = response.headers.get_content_type()
            if content_type not in {"text/html", "text/plain"}:
                raise ValueError("resource must be HTML or plain text")
            payload = response.read(self.max_bytes + 1)
        if len(payload) > self.max_bytes:
            raise ValueError(f"resource exceeds {self.max_bytes} bytes")
        text = payload.decode("utf-8", errors="replace")
        if content_type == "text/html":
            parser = _PageParser()
            parser.feed(text)
            body = "\n".join(parser.parts)
            links = _absolute_links(final_url, parser.links)
            title = parser.title
        else:
            body = " ".join(text.split())
            links = []
            title = ""
        if not body:
            raise ValueError("resource contains no readable text")
        return {
            "url": final_url,
            "title": title,
            "text": body,
            "links": links,
            "bytes": len(payload),
        }


class _NoRedirectHandler(HTTPRedirectHandler):
    def redirect_request(self, request, file, code, msg, headers, newurl):
        raise ValueError("redirects are not allowed for resource collection")


def _absolute_links(base_url: str, links: Iterable[str]) -> list[str]:
    result = []
    for link in links:
        absolute = urljoin(base_url, link)
        parsed = urlparse(absolute)
        if parsed.scheme in {"http", "https"} and parsed.hostname and absolute not in result:
            result.append(absolute)
    return result