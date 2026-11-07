"""Contract tests for the repository's reusable skill library."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
INDEX = SKILLS_ROOT / "README.md"


def _frontmatter_value(text: str, key: str) -> str | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end < 0:
        return None
    match = re.search(rf"^{re.escape(key)}:\s*(.+?)\s*$", text[4:end], re.MULTILINE)
    return match.group(1).strip().strip("\"'") if match else None


def test_skill_directories_have_unique_names_and_descriptions():
    skill_files = sorted(SKILLS_ROOT.rglob("SKILL.md"))
    assert skill_files, "no skill definitions found"

    names = []
    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        name = _frontmatter_value(text, "name")
        description = _frontmatter_value(text, "description")
        assert name, f"{path.relative_to(ROOT)} is missing a frontmatter name"
        assert description, f"{path.relative_to(ROOT)} is missing a frontmatter description"
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name), f"invalid skill name: {name}"
        names.append(name)

    assert len(names) == len(set(names)), f"duplicate skill names: {names}"


def test_skill_index_links_resolve_to_skill_files():
    assert INDEX.is_file(), "skills/README.md index is missing"
    text = INDEX.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)#]+\.md)(?:#[^)]+)?\)", text)
    assert links, "skill index contains no local Markdown links"

    missing = [
        link for link in links
        if not (INDEX.parent / link).resolve().is_file()
    ]
    assert not missing, f"broken skill index links: {missing}"

    discovered = {
        path.relative_to(SKILLS_ROOT).as_posix()
        for path in SKILLS_ROOT.rglob("SKILL.md")
    }
    indexed = {
        (INDEX.parent / link).resolve().relative_to(SKILLS_ROOT.resolve()).as_posix()
        for link in links
    }
    assert indexed == discovered, (
        f"skill index drift: unindexed={sorted(discovered - indexed)}, "
        f"stale={sorted(indexed - discovered)}"
    )


def test_core_skills_reference_their_intended_scope():
    refinement = (SKILLS_ROOT / "verified-repo-refinement" / "SKILL.md").read_text(encoding="utf-8")
    evolution = (SKILLS_ROOT / "skill-evolution" / "SKILL.md").read_text(encoding="utf-8")
    assert "source-to-sink" in refinement
    assert "approval" in refinement.lower()
    assert "Skill lifecycle" in evolution
    assert "Stop conditions" in evolution
