#!/usr/bin/env python3
"""
Affiliate Marketing CLI — $0 startup, organism-powered.

Commands:
  python3 scripts/cli.py generate <template> <product> <platform> <affiliate_url>
  python3 scripts/cli.py list-templates
  python3 scripts/cli.py list-platforms
  python3 scripts/cli.py track-click <source> <product> [campaign]
  python3 scripts/cli.py track-conversion <click_id> <revenue> <commission>
  python3 scripts/cli.py dashboard
  python3 scripts/cli.py campaign <name> <products_csv> <platforms_csv>
  python3 scripts/cli.py format <article_path> <platform>
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from content_engine import handler as content_handler, TEMPLATES, NICHES
from publishing_adapter import handler as publish_handler, PLATFORMS
from conversion_tracker import handler as tracker_handler


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "generate":
        template = sys.argv[2] if len(sys.argv) > 2 else "product_review"
        product = sys.argv[3] if len(sys.argv) > 3 else "Sample Product"
        platform = sys.argv[4] if len(sys.argv) > 4 else "medium"
        affiliate_url = sys.argv[5] if len(sys.argv) > 5 else "https://example.com/affiliate"
        result = content_handler({"action": "generate", "template": template,
                                  "product": product, "platform": platform,
                                  "affiliate_url": affiliate_url})
        print(f"✅ Generated: {result.get('title', 'unknown')}")
        print(f"   File: {result.get('file', 'unknown')}")
        print(f"   Words: {result.get('word_count', 0)}")
        print(f"   URL: {result.get('affiliate_url', 'none')}")

    elif cmd == "list-templates":
        result = content_handler({"action": "templates"})
        print("📝 Available templates:")
        for t in result["templates"]:
            print(f"   - {t}")
        print(f"\n🏷 Available niches:")
        for n in result["niches"]:
            print(f"   - {n}")

    elif cmd == "list-platforms":
        result = publish_handler({"action": "list"})
        print("📢 Free platforms:")
        for p in result["platforms"]:
            print(f"   - {p['name']} ({p['format']}) — {p['monetization'][:60]}")

    elif cmd == "track-click":
        source = sys.argv[2] if len(sys.argv) > 2 else "cli"
        product = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        campaign = sys.argv[4] if len(sys.argv) > 4 else "default"
        result = tracker_handler({"action": "click", "source": source,
                                  "product": product, "campaign": campaign})
        print(f"📊 Click tracked: {result.get('source')} → {result.get('product')}")

    elif cmd == "track-conversion":
        click_id = sys.argv[2] if len(sys.argv) > 2 else ""
        revenue = sys.argv[3] if len(sys.argv) > 3 else "0"
        commission = sys.argv[4] if len(sys.argv) > 4 else "0"
        result = tracker_handler({"action": "conversion", "click_id": click_id,
                                  "revenue": revenue, "commission": commission})
        print(f"💰 Conversion: ${revenue} revenue, ${commission} commission")

    elif cmd == "dashboard":
        result = tracker_handler({"action": "dashboard"})
        print("═══ AFFILIATE DASHBOARD ═══")
        print(f"  Clicks: {result['total_clicks']}")
        print(f"  Conversions: {result['total_conversions']}")
        print(f"  Revenue: ${result['total_revenue']:.2f}")
        print(f"  Commission: ${result['total_commission']:.2f}")
        print(f"  Conversion rate: {result['conversion_rate']:.2%}")
        print(f"  EPC: ${result['epc']:.4f}")
        if result.get("clicks_by_source"):
            print(f"  By source: {result['clicks_by_source']}")

    elif cmd == "campaign":
        name = sys.argv[2] if len(sys.argv) > 2 else "default"
        products = sys.argv[3].split(",") if len(sys.argv) > 3 else []
        platforms = sys.argv[4].split(",") if len(sys.argv) > 4 else ["medium"]
        result = tracker_handler({"action": "campaign", "name": name,
                                  "products": products, "platforms": platforms})
        print(f"🚀 Campaign created: {result.get('name')}")

    elif cmd == "format":
        article = sys.argv[2] if len(sys.argv) > 2 else ""
        platform = sys.argv[3] if len(sys.argv) > 3 else "medium"
        result = publish_handler({"action": "format", "article_path": article,
                                  "platform": platform})
        if "error" in result:
            print(f"❌ {result['error']}")
        else:
            print(f"✅ Formatted for {result['platform_name']}")
            print(f"   File: {result.get('formatted_file', 'unknown')}")
            print(f"   Submit: {result.get('submit_url', 'unknown')}")

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
