#!/usr/bin/env python3
"""Builds one ZIP per skill in dist/, for uploading a single skill to the
Claude app. Each ZIP holds the skill folder with its own copy of references/
and the scripts it needs, so it works on its own.

Usage: python3 scripts/build_zips.py
"""

from __future__ import annotations

import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> None:
    DIST.mkdir(exist_ok=True)
    skills = sorted(p for p in ROOT.iterdir() if (p / "SKILL.md").exists())
    for folder in skills:
        text = (folder / "SKILL.md").read_text(encoding="utf-8")
        scripts = sorted(set(re.findall(r"\.\./scripts/([a-z_]+\.py)", text)))
        if scripts:
            scripts.append("leakkit.py")
        out = DIST / f"{folder.name}.zip"
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr(f"{folder.name}/SKILL.md", text)
            for ref in (ROOT / "references").glob("*.md"):
                z.write(ref, f"{folder.name}/references/{ref.name}")
            if folder.name == "weekly-revenue-leak-readout":
                z.write(ROOT / "AGENTS.md", f"{folder.name}/AGENTS.md")
            for s in scripts:
                z.write(ROOT / "scripts" / s, f"{folder.name}/scripts/{s}")
        print(f"{out.relative_to(ROOT)}  ({len(scripts)} script files)")


if __name__ == "__main__":
    main()
