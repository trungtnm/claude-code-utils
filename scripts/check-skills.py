#!/usr/bin/env python3
"""Validate the plugin's skill frontmatter.

Both hosts resolve a workflow by its frontmatter `name`, and Claude Code
additionally requires that name to match the directory it lives in. Nothing
enforces either rule at install time, so check it here before committing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_ROOT = REPO_ROOT / "plugins" / "ccu" / "skills"


def frontmatter(path: Path) -> dict[str, str]:
    contents = path.read_text(encoding="utf-8")
    if not contents.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = contents.find("\n---", 4)
    if end == -1:
        raise ValueError("unclosed YAML frontmatter")
    fields = {}
    for match in re.finditer(r"^([A-Za-z-]+):\s*(.+?)\s*$", contents[4:end], re.MULTILINE):
        fields[match.group(1)] = match.group(2).strip().strip("\"'")
    return fields


def main() -> int:
    errors: list[str] = []
    skill_dirs = sorted(p for p in SKILLS_ROOT.iterdir() if p.is_dir())

    for skill_dir in skill_dirs:
        path = skill_dir / "SKILL.md"
        rel = path.relative_to(REPO_ROOT)
        if not path.is_file():
            errors.append(f"{skill_dir.relative_to(REPO_ROOT)}: no SKILL.md")
            continue
        try:
            fields = frontmatter(path)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        name = fields.get("name")
        if name is None:
            errors.append(f"{rel}: missing frontmatter name")
        elif name != skill_dir.name:
            errors.append(f"{rel}: name '{name}' does not match directory '{skill_dir.name}'")
        if not fields.get("description"):
            errors.append(f"{rel}: missing frontmatter description")

    for error in errors:
        print(error, file=sys.stderr)
    if errors:
        return 1

    print(f"checked {len(skill_dirs)} skills")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
