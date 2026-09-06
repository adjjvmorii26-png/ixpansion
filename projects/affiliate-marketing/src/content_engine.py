"""
Content Engine — generates affiliate marketing content from product data.

ALEPH built the pipeline, LUMA designed the voice, AXIOM tracks what converts.

$0 startup: no paid tools needed. Generates Markdown articles from product data,
inserts affiliate links with UTM tracking, and formats for free platforms.
"""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).parent.parent / "data"
ARTICLES_DIR = DATA_DIR / "articles"
CONFIG_FILE = DATA_DIR / "config.json"

# ─── CONTENT TEMPLATES (LUMA's creative layer) ──────────────

TEMPLATES = {
    "product_review": {
        "title_format": "Honest {product} Review ({year}): Is It Worth It?",
        "sections": [
            {"heading": "What is {product}?", "type": "intro", "words": (150, 250)},
            {"heading": "Key Features", "type": "features", "words": (200, 350)},
            {"heading": "My Experience", "type": "personal", "words": (200, 300)},
            {"heading": "Pros and Cons", "type": "pros_cons", "words": (100, 200)},
            {"heading": "Pricing", "type": "pricing", "words": (100, 150)},
            {"heading": "Verdict", "type": "verdict", "words": (100, 200)},
        ],
        "cta": "👉 [Check {product} on {platform}({affiliate_url}?utm_source=review&utm_medium=affiliate)",
    },
    "best_of_list": {
        "title_format": "Best {niche} in {year}: Top {count} Picks",
        "sections": [
            {"heading": "Quick Comparison", "type": "comparison_table", "words": (50, 100)},
            {"heading": "#{n} — {product}", "type": "item", "words": (150, 250)},
            {"heading": "How We Chose", "type": "methodology", "words": (100, 200)},
            {"heading": "Final Thoughts", "type": "conclusion", "words": (100, 150)},
        ],
        "cta": "👉 [See all {count} picks on {platform}({affiliate_url}?utm_source=list&utm_medium=affiliate)",
    },
    "how_to_guide": {
        "title_format": "How to {action} with {product} (Step-by-Step)",
        "sections": [
            {"heading": "Why {product}?", "type": "intro", "words": (150, 200)},
            {"heading": "Step 1: Setup", "type": "step", "words": (150, 250)},
            {"heading": "Step 2: Configure", "type": "step", "words": (150, 250)},
            {"heading": "Step 3: Optimize", "type": "step", "words": (150, 250)},
            {"heading": "Tips and Tricks", "type": "tips", "words": (100, 200)},
            {"heading": "FAQ", "type": "faq", "words": (100, 200)},
        ],
        "cta": "👉 [Get started with {product}]({affiliate_url}?utm_source=guide&utm_medium=affiliate)",
    },
    "comparison": {
        "title_format": "{product_a} vs {product_b}: Which Is Better in {year}?",
        "sections": [
            {"heading": "Overview", "type": "intro", "words": (150, 200)},
            {"heading": "Feature Comparison", "type": "comparison_table", "words": (150, 250)},
            {"heading": "Pricing", "type": "pricing_compare", "words": (100, 200)},
            {"heading": "User Experience", "type": "ux", "words": (150, 250)},
            {"heading": "Verdict", "type": "verdict", "words": (100, 200)},
        ],
        "cta": "👉 [{product_a}]({url_a}?utm_source=comparison&utm_medium=affiliate) | [{product_b}]({url_b}?utm_source=comparison&utm_medium=affiliate)",
    },
}

# ─── NICHE CONFIGURATIONS (AXIOM's data) ────────────────────

NICHES = {
    "productivity_tools": {
        "platforms": ["medium", "devto", "hashnode"],
        "affiliate_programs": ["amazon", "appsumo", "direct"],
        "target_earnings": {"epc": 0.50, "ctr": 2.5, "conversion_rate": 1.5},
        "content_velocity": 3,  # articles per week
        "keywords": ["productivity", "workflow", "automation", "tools", "software"],
    },
    "tech_gadgets": {
        "platforms": ["medium", "devto"],
        "affiliate_programs": ["amazon", "bestbuy"],
        "target_earnings": {"epc": 0.80, "ctr": 3.0, "conversion_rate": 2.0},
        "content_velocity": 2,
        "keywords": ["tech", "gadgets", "reviews", "best", "top"],
    },
    "online_courses": {
        "platforms": ["medium", "hashnode"],
        "affiliate_programs": ["udemy", "coursera", "skillshare"],
        "target_earnings": {"epc": 1.20, "ctr": 3.5, "conversion_rate": 2.5},
        "content_velocity": 2,
        "keywords": ["learn", "course", "tutorial", "online", "education"],
    },
    "creative_software": {
        "platforms": ["medium", "devto", "hashnode"],
        "affiliate_programs": ["adobe", "canva", "figma"],
        "target_earnings": {"epc": 0.90, "ctr": 2.8, "conversion_rate": 1.8},
        "content_velocity": 3,
        "keywords": ["design", "creative", "software", "tools", "art"],
    },
}


def _sig(text: str) -> str:
    return f"0x{hashlib.sha256(text.encode()).hexdigest()[:12]}"


def generate_article(
    template_name: str,
    product: str,
    platform: str,
    affiliate_url: str,
    niche: str = "productivity_tools",
    extra: Dict = None,
) -> Dict:
    """Generate a complete article from template + product data."""
    template = TEMPLATES.get(template_name)
    if not template:
        return {"error": f"template '{template_name}' not found"}

    extra = extra or {}
    year = str(time.strftime("%Y"))
    title = template["title_format"].format(
        product=product, year=year, niche=NICHES.get(niche, {}).get("keywords", [""])[0],
        count=extra.get("count", 10), action=extra.get("action", "get started"),
        platform=platform, product_a=extra.get("product_a", ""),
        product_b=extra.get("product_b", ""), n=0,
    )

    # Build UTM-tracked affiliate URL
    utm_url = f"{affiliate_url}?utm_source={platform}&utm_medium=affiliate&utm_campaign={product.lower().replace(' ', '_')}"

    # Generate article body
    body_parts = [f"# {title}\n"]
    body_parts.append(f"*Last updated: {time.strftime('%B %d, %Y')}*\n")
    body_parts.append(f"> Disclosure: This article contains affiliate links. "
                      f"If you purchase through these links, we may earn a commission "
                      f"at no extra cost to you.\n")

    for i, section in enumerate(template["sections"]):
        heading = section["heading"].format(product=product, n=i+1, **{k: v for k, v in extra.items() if k not in ("n",)})
        body_parts.append(f"## {heading}\n")
        # Placeholder content — in production, this would be AI-generated
        body_parts.append(f"[Content for '{section['type']}' section about {product}]\n")

    # Add CTA with affiliate link
    cta = template.get("cta", "")
    cta = cta.format(product=product, platform=platform, affiliate_url=utm_url,
                     count=extra.get("count", 10), **extra)
    body_parts.append(f"\n---\n{cta}\n")

    # Metadata
    meta = {
        "id": _sig(f"{template_name}:{product}:{platform}:{time.time()}"),
        "template": template_name,
        "product": product,
        "platform": platform,
        "niche": niche,
        "affiliate_url": utm_url,
        "title": title,
        "created": time.time(),
        "word_count": sum(len(p.split()) for p in body_parts),
        "sections": len(template["sections"]),
        "status": "draft",
    }

    # Save article
    filename = f"{product.lower().replace(' ', '_')}_{platform}_{int(time.time())}.md"
    out_path = ARTICLES_DIR / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(body_parts), encoding="utf-8")
    meta["file"] = str(out_path)

    # Track in data
    _track_article(meta)

    return meta


def _track_article(meta: Dict):
    tracker_file = DATA_DIR / "articles_tracker.json"
    try:
        tracker = json.loads(tracker_file.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        tracker = {"articles": [], "total_words": 0, "total_articles": 0}
    tracker["articles"].append(meta)
    tracker["total_words"] += meta["word_count"]
    tracker["total_articles"] += 1
    tracker_file.write_text(json.dumps(tracker, indent=2))


def get_tracker() -> Dict:
    tracker_file = DATA_DIR / "articles_tracker.json"
    try:
        return json.loads(tracker_file.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {"articles": [], "total_words": 0, "total_articles": 0}


def handler(payload: Dict = None, context: Dict = None) -> Dict:
    p = payload or {}
    action = str(p.get("action", "generate")).lower()
    if action == "generate":
        return {"action": "generate_article",
                **generate_article(
                    p.get("template", "product_review"),
                    p.get("product", "Sample Product"),
                    p.get("platform", "medium"),
                    p.get("affiliate_url", "https://example.com/affiliate"),
                    p.get("niche", "productivity_tools"),
                    p.get("extra", {}),
                )}
    elif action == "tracker":
        return {"action": "tracker", **get_tracker()}
    elif action == "templates":
        return {"action": "templates", "templates": list(TEMPLATES.keys()),
                "niches": list(NICHES.keys())}
    return {"action": "content_engine", "templates": len(TEMPLATES),
            "niches": len(NICHES)}


def coherence_vitals() -> Dict:
    t = get_tracker()
    return {"layer": "content", "status": "resonant", "resonance": 0.95,
            "wave": "449", "articles": t["total_articles"],
            "total_words": t["total_words"]}


def resonates_with() -> List[str]:
    return ["brand_identity", "conversion_tracker", "publishing_adapter"]
