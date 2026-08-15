#!/usr/bin/env python3
"""
Autonomous YouTube Publishing Pipeline for @adjjv
Prepares upload bundle from auto_content_engine; API stubs for upload.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from auto_content_engine import produce_auto_package

PUB = Path("/home/workdir/artifacts/content_output/youtube_publish")
PUB.mkdir(parents=True, exist_ok=True)


def build_upload_bundle(title: Optional[str] = None) -> dict:
    demo = produce_auto_package(title=title or "IXPANSION Autonomous Swarm Demo")
    bundle = {
        "channel": "@adjjv",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "snippet": {
            "title": demo["title"][:100],
            "description": "\n".join(demo["voiceover_lines"]) + "\n\n#AI #Swarm #IXPANSION #Simulation",
            "tags": ["AI agents", "swarm", "IXPANSION", "lattice", "autonomous systems", "adjjv"],
            "categoryId": "28",  # Science & Technology
        },
        "status": {
            "privacyStatus": "private",  # safe default until manual go-live
            "selfDeclaredMadeForKids": False,
        },
        "storyboard": demo["storyboard"],
        "voiceover_script": demo["voiceover_script"],
        "assets": demo["assets"],
        "render_hints": demo["render_hints"],
        "upload_api": {
            "provider": "youtube_data_api_v3",
            "endpoint": "https://www.googleapis.com/upload/youtube/v3/videos",
            "auth": "OAUTH2_CLIENT_SECRETS — set YT_CLIENT_SECRETS env",
            "steps": [
                "Render mp4 from WebGL panel + lattice heatmap (headless Chromium/OBS)",
                "TTS voiceover from voiceover_script",
                "videos.insert metadata + media",
                "thumbnails.set from Canva asset",
            ],
        },
        "ready_for_upload": False,
        "notes": "Bundle prepared offline; set ready_for_upload true after local render exists",
    }
    bid = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = PUB / f"{bid}_upload_bundle.json"
    path.write_text(json.dumps(bundle, indent=2, default=str))
    md = PUB / f"{bid}_UPLOAD.md"
    md.write_text(
        f"# YouTube Upload Bundle\n\nTitle: {bundle['snippet']['title']}\n\n"
        f"Privacy: {bundle['status']['privacyStatus']}\n\n"
        f"## Description\n\n{bundle['snippet']['description'][:500]}\n\n"
        f"## Steps\n" + "\n".join(f"- {s}" for s in bundle["upload_api"]["steps"])
    )
    print(f"[YT] bundle → {path}")
    return bundle


if __name__ == "__main__":
    b = build_upload_bundle()
    print(b["snippet"]["title"])
  
