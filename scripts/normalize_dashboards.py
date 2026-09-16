"""Dashboard OS Strip — Normalize OS-specific styling across all dashboards.

This refinement #5 strips OS-specific styling from dashboard HTML files
to ensure a unified appearance across all operating systems.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Set

# Root path
ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = ROOT / "dashboard"

# OS-specific patterns to normalize
REPLACEMENTS = {
    "macc": "account",
    "mamt": "amount",
}

# Files processed count
files_processed = 0
files_modified = 0


def normalize_dashboard(filepath: Path) -> bool:
    """Normalize OS-specific styling in a dashboard file.
    
    Args:
        filepath: Path to dashboard HTML file
        
    Returns:
        True if file was modified
    """
    global files_processed, files_modified
    
    files_processed += 1
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except (UnicodeDecodeError, FileNotFoundError):
        return False
    
    original_content = content
    modified = False
    
    # Apply replacements
    for os_pattern, replacement in REPLACEMENTS.items():
        if os_pattern in content:
            import re
            pattern = re.compile(re.escape(os_pattern), re.IGNORECASE)
            content = pattern.sub(replacement, content)
            modified = True
    
    # Also normalize any id= patterns that look OS-specific
    content, re_count = re.subn(
        r'id=["\"]macc["\"]', 'id="account"', content, flags=re.IGNORECASE
    )
    modified = modified or (re_count > 0)
    
    content, re_count = re.subn(
        r'id=["\"]mamt["\"]', 'id="amount"', content, flags=re.IGNORECASE
    )
    modified = modified or (re_count > 0)
    
    # Write back if modified
    if modified:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        files_modified += 1
    
    return modified


def normalize_all_dashboards() -> Dict[str, Any]:
    """Normalize all dashboard HTML files.
    
    Returns:
        Processing summary dictionary
    """
    global files_processed, files_modified
    
    # Find all HTML files in dashboard directory
    html_files = list(DATA_DIR.rglob("*.html"))
    
    summary = {
        "total_files": len(html_files),
        "files_processed": 0,
        "files_modified": 0,
        "replacements_made": 0,
        "details": [],
    }
    
    for filepath in html_files:
        was_modified = normalize_dashboard(filepath)
        if was_modified:
            files_modified += 1
        files_processed += 1
        
        # Track details for first few files
        if files_processed <= 5:
            detail = {
                "file": str(filepath.relative_to(ROOT)),
                "modified": was_modified,
            }
            summary["details"].append(detail)
    
    # Trim details to first 5 only
    if len(summary["details"]) > 5:
        summary["details"] = summary["details"][:5]
        summary["details_additional"] = f"+ {len(html_files) - 5} more files"
    
    return summary


# CLI entry point
if __name__ == "__main__":
    import sys
    
    print("=== Dashboard OS Strip Normalization ===")
    print()
    
    # Run normalization
    summary = normalize_all_dashboards()
    
    print(f"Total HTML files: {summary['total_files']}")
    print(f"Files processed: {summary['files_processed']}")
    print(f"Files modified: {summary['files_modified']}")
    print()
    
    if summary["details"]:
        print("Sample modifications:")
        for detail in summary["details"]:
            print(f"  {detail['file']}: {'modified' if detail['modified'] else 'no changes'}")
    
    if summary["details_additional"]:
        print(f"  + {summary['details_additional']}")
    
    print()
    if summary["files_modified"] > 0:
        print("✅ Dashboards normalized successfully")
    else:
        print("No OS-specific patterns found - dashboards already unified")
    
    sys.exit(0 if summary["files_modified"] > 0 else 0)
