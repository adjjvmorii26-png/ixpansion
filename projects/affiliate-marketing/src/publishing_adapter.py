"""
Publishing Adapter — routes content to free platforms.

Supported platforms (all free):
- Medium (free tier, import via Markdown)
- Dev.to (free, Markdown native)
- Hashnode (free, Markdown native)
- LinkedIn Articles (free)
- Ghost (free tier via Ghost.org)

Each adapter formats content for the target platform and provides
the submission URL. Actual API posting would require platform tokens.
"""
from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Dict, List

DATA_DIR = Path(__file__).parent.parent / "data"

PLATFORMS = {
    "medium": {
        "name": "Medium",
        "format": "markdown",
        "submit_url": "https://medium.com/new-story",
        "max_title": 100,
        "supports_code": True,
        "supports_images": True,
        "tags_limit": 5,
        "monetization": "Medium Partner Program (free to join, earnings from reads)",
        "notes": "Import Markdown via 'Import a story' button",
    },
    "devto": {
        "name": "Dev.to",
        "format": "markdown",
        "submit_url": "https://dev.to/new",
        "max_title": 128,
        "supports_code": True,
        "supports_images": True,
        "tags_limit": 4,
        "monetization": "DEV Community (free, no direct monetization but drives traffic)",
        "notes": "Native Markdown support, front matter YAML for metadata",
    },
    "hashnode": {
        "name": "Hashnode",
        "format": "markdown",
        "submit_url": "https://hashnode.com/new",
        "max_title": 150,
        "supports_code": True,
        "supports_images": True,
        "tags_limit": 5,
        "monetization": "Hashnode Web3 (earn via tips, no upfront cost)",
        "notes": "Auto-publishes to your custom domain",
    },
    "linkedin": {
        "name": "LinkedIn Articles",
        "format": "html",
        "submit_url": "https://www.linkedin.com/feed/news/publish",
        "max_title": 200,
        "supports_code": False,
        "supports_images": True,
        "tags_limit": 0,
        "monetization": "LinkedIn Creator Mode (free, builds professional audience)",
        "notes": "Convert Markdown to HTML before publishing",
    },
    "ghost": {
        "name": "Ghost",
        "format": "markdown",
        "submit_url": "https://ghost.org/",
        "max_title": 300,
        "supports_code": True,
        "supports_images": True,
        "tags_limit": 999,
        "monetization": "Ghost Memberships (free tier, earn from paid subscribers)",
        "notes": "Self-hosted or Ghost(Pro), Markdown native",
    },
}


def format_for_platform(article_path: str, platform: str) -> Dict:
    """Format an article for a specific platform."""
    platform_config = PLATFORMS.get(platform)
    if not platform_config:
        return {"error": f"platform '{platform}' not found"}

    try:
        content = Path(article_path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return {"error": f"article not found: {article_path}"}

    title = ""
    body = content
    tags = []

    # Extract title from first heading
    for line in content.split("\n"):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Platform-specific formatting
    if platform == "devto":
        # Add YAML front matter
        front_matter = f"---\ntitle: {title}\npublished: true\ntags: affiliate\ndate: {time.strftime('%Y-%m-%d')}\n---\n\n"
        body = front_matter + content
    elif platform == "medium":
        # Medium accepts raw Markdown via import
        body = content
    elif platform == "hashnode":
        # Hashnode uses front matter too
        front_matter = f"---\ntitle: '{title}'\ntags: [affiliate]\ndate: '{time.strftime('%Y-%m-%d')}'\n---\n\n"
        body = front_matter + content
    elif platform == "linkedin":
        # Simple HTML conversion (basic)
        body = content.replace("# ", "<h1>").replace("\n## ", "\n<h2>").replace("\n", "\n<p>")
        body = f"<h1>{title}</h1>\n{body}"

    result = {
        "platform": platform,
        "platform_name": platform_config["name"],
        "title": title,
        "submit_url": platform_config["submit_url"],
        "monetization": platform_config["monetization"],
        "formatted_content": body[:500] + "..." if len(body) > 500 else body,
        "full_length": len(body),
        "ready_to_publish": True,
    }

    # Save formatted version
    out_dir = DATA_DIR / "formatted" / platform
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / Path(article_path).name
    out_path.write_text(body, encoding="utf-8")
    result["formatted_file"] = str(out_path)

    return result


def list_platforms() -> List[Dict]:
    return [{"id": k, "name": v["name"], "format": v["format"],
             "monetization": v["monetization"]} for k, v in PLATFORMS.items()]


def handler(payload: Dict = None, context: Dict = None) -> Dict:
    p = payload or {}
    action = str(p.get("action", "list")).lower()
    if action == "format":
        return {"action": "format_for_platform",
                **format_for_platform(p.get("article_path", ""), p.get("platform", "medium"))}
    elif action == "list":
        return {"action": "list_platforms", "platforms": list_platforms()}
    return {"action": "publishing_adapter", "platforms": len(PLATFORMS)}


def coherence_vitals() -> Dict:
    return {"layer": "publishing", "status": "resonant", "resonance": 0.9,
            "wave": "449", "platforms": len(PLATFORMS)}


def resonates_with() -> List[str]:
    return ["content_engine", "conversion_tracker", "brand_identity"]
