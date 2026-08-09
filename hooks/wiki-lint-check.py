#!/usr/bin/env python3
"""
PreCompact hook — wiki lint check.
Finds orphan pages (on disk, not in SCHEMA) and ghost pages (in SCHEMA, not on disk).
Updates 'Last lint' date in SCHEMA.md. Non-blocking — warns only, never fails.
"""
import os
import re
import sys
from datetime import datetime
from pathlib import Path


def find_wiki(project_root: Path) -> Path | None:
    """Search both common wiki locations."""
    candidates = [
        project_root / "knowledge" / "wiki",
        project_root / ".claude" / "knowledge" / "wiki",
    ]
    for c in candidates:
        if c.exists() and (c / "SCHEMA.md").exists():
            return c
    return None


def parse_registered_pages(schema_text: str) -> set[str]:
    """
    Extract real (on-disk) filenames from the Wiki Pages table.
    Handles aliases: `` `alias.md` → `real.md` `` — only the real file is registered.
    """
    registered = set()
    in_pages = False

    for line in schema_text.split("\n"):
        if "## Wiki Pages" in line:
            in_pages = True
            continue
        if in_pages and line.startswith("## "):
            break
        if not in_pages or "|" not in line or line.strip().startswith("|---"):
            continue

        cells = line.split("|")
        if len(cells) < 2:
            continue
        first_cell = cells[1]

        if "→" in first_cell:
            # Alias row — take filename after the arrow
            after_arrow = first_cell.split("→", 1)[1]
            files = re.findall(r"`([^`]+\.md)`", after_arrow)
        else:
            files = re.findall(r"`([^`]+\.md)`", first_cell)

        registered.update(files)

    return registered


def main():
    project_root = Path(os.environ.get("CLAUDE_PROJECT_DIR", "")) or Path(__file__).parent.parent.parent
    wiki_dir = find_wiki(project_root)

    if wiki_dir is None:
        sys.exit(0)  # No wiki in this project — nothing to lint

    schema_path = wiki_dir / "SCHEMA.md"
    today = datetime.now().strftime("%Y-%m-%d")

    schema_text = schema_path.read_text()

    # Files on disk (exclude SCHEMA.md and any raw/ subdir files)
    disk_pages = {f.name for f in wiki_dir.glob("*.md") if f.name != "SCHEMA.md"}

    registered = parse_registered_pages(schema_text)

    orphans = disk_pages - registered    # on disk, not registered
    ghosts = registered - disk_pages     # registered, not on disk

    # Update Last lint date in SCHEMA.md
    updated = re.sub(r"\*Last lint: [^\*]*\*", f"*Last lint: {today}*", schema_text)
    if updated != schema_text:
        schema_path.write_text(updated)

    issues = []
    if orphans:
        issues.append(f"  ⚠️  ORPHAN (on disk, not in SCHEMA): {', '.join(sorted(orphans))}")
        issues.append("     → Run /lint, then add to SCHEMA.md Wiki Pages table")
    if ghosts:
        issues.append(f"  ⚠️  GHOST (in SCHEMA, not on disk): {', '.join(sorted(ghosts))}")
        issues.append("     → Run /lint, then create the missing page or remove from SCHEMA")

    if issues:
        print(f"📚 Wiki lint [{wiki_dir.name}/] — issues found:")
        for line in issues:
            print(line)
    else:
        print(f"📚 Wiki lint [{wiki_dir.name}/]: ✅ clean — {len(disk_pages)} pages, no orphans/ghosts ({today})")

    sys.exit(0)


if __name__ == "__main__":
    main()
