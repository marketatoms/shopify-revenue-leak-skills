#!/usr/bin/env python3
"""Structural check for the pack. Fails (exit 1) if any skill:

- is missing its front matter, or its name doesn't match its folder;
- is missing a required section, or has them out of order;
- cites a threshold key that doesn't exist in references/thresholds.md;
- cites a relative path (../references/..., ../scripts/...) that doesn't exist;
- has a description that duplicates another skill's.

It cannot judge whether a skill's advice is right; selftest.py checks the maths.
Usage: python3 scripts/validate_skills.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from leakkit import ROOT, load_thresholds  # noqa: E402

SECTIONS = ["## Use this skill when", "## Required input", "## Live data (MarketAtoms MCP)",
            "## Analysis workflow", "## Decision rules", "## Output format",
            "## Practical example", "## Guardrails"]


def main() -> int:
    keys = set(load_thresholds())
    errors: list[str] = []
    descriptions: dict[str, str] = {}
    skills = sorted(p for p in ROOT.iterdir() if (p / "SKILL.md").exists())
    if not skills:
        errors.append("no skill folders found")
    for folder in skills:
        text = (folder / "SKILL.md").read_text(encoding="utf-8")
        fm = re.match(r"^---\nname: (.+)\ndescription: (.+)\n---\n", text)
        if not fm:
            errors.append(f"{folder.name}: front matter missing or malformed")
            continue
        name, desc = fm.group(1).strip(), fm.group(2).strip()
        if name != folder.name:
            errors.append(f"{folder.name}: name '{name}' doesn't match folder")
        if len(desc) > 1024:
            errors.append(f"{folder.name}: description over 1024 characters")
        if desc in descriptions.values():
            errors.append(f"{folder.name}: duplicate description")
        descriptions[name] = desc
        positions = [text.find(s) for s in SECTIONS]
        for s, pos in zip(SECTIONS, positions):
            if pos < 0:
                errors.append(f"{folder.name}: missing section '{s}'")
        found = [p for p in positions if p >= 0]
        if found != sorted(found):
            errors.append(f"{folder.name}: sections out of order")
        for key in set(re.findall(r"`([a-z]+\.[a-z_]+)`", text)):
            if key.endswith((".md", ".py")):
                continue
            if key not in keys:
                errors.append(f"{folder.name}: cites unknown threshold `{key}`")
        for rel in set(re.findall(r"`(\.\./[^`]+)`", text)):
            if not (folder / rel).resolve().exists():
                errors.append(f"{folder.name}: path {rel} does not exist")
    if errors:
        print("FAIL")
        print("\n".join(f"  - {e}" for e in errors))
        return 1
    print(f"OK: {len(skills)} skills, {len(keys)} thresholds, all sections, keys and paths resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
