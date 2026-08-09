#!/usr/bin/env python3
"""
UserPromptSubmit hook — injects deadline warnings by reading them dynamically
from STATUS.md. Falls back to hardcoded dates only if file is unreadable.
Never goes stale as long as STATUS.md is kept current.
"""
import json, os, sys, re
from datetime import datetime, date
from pathlib import Path

PROJ = str(Path(__file__).parent.parent.parent)
STATUS_FILE = os.path.join(PROJ, ".claude/memory/STATUS.md")

# Fallback deadlines (only used if STATUS.md can't be read)
FALLBACK_DEADLINES = []  # Add project-specific deadlines here if career.md is unavailable

# Regex to find dates in career.md table rows
# Matches: **April 20, 2026** or April 20, 2026 or 2026-04-20
DATE_PATTERNS = [
    r"\*\*(\w+ \d+, \d{4})\*\*",   # **April 20, 2026**
    r"(\w+ \d+, \d{4})",            # April 20, 2026
    r"(\d{4}-\d{2}-\d{2})",         # 2026-04-20
]

def parse_dates_from_status(text):
    """Extract deadline rows from the Active Decisions table in STATUS.md."""
    deadlines = []
    in_table = False
    for line in text.splitlines():
        if "Active Decisions" in line or "HARD DEADLINE" in line:
            in_table = True
        if in_table and "|" in line and "---" not in line and "Decision" not in line:
            # Try to extract a date and label from the table row
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 2:
                label = cells[0].strip("*").strip()
                date_str = cells[1] if len(cells) > 1 else ""
                for pattern in DATE_PATTERNS:
                    m = re.search(pattern, date_str)
                    if m:
                        try:
                            raw = m.group(1)
                            if "-" in raw:
                                d = datetime.strptime(raw, "%Y-%m-%d").date()
                            else:
                                d = datetime.strptime(raw, "%B %d, %Y").date()
                            deadlines.append({"label": label, "date": d})
                            break
                        except ValueError:
                            pass
    return deadlines if deadlines else None


def check_memory_staleness():
    """Check all memory files for staleness and return warnings."""
    stale = []
    memory_dir = os.path.join(PROJ, ".claude/memory")
    today = date.today()

    for fname in os.listdir(memory_dir):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(memory_dir, fname)
        try:
            with open(fpath) as f:
                content = f.read()
            # Parse frontmatter
            lu_match = re.search(r"last_updated:\s*(\d{4}-\d{2}-\d{2})", content)
            thresh_match = re.search(r"staleness_threshold:\s*(\d+)_days", content)
            if lu_match and thresh_match:
                last_updated = datetime.strptime(lu_match.group(1), "%Y-%m-%d").date()
                threshold = int(thresh_match.group(1))
                age = (today - last_updated).days
                if age > threshold:
                    stale.append(f"{fname} ({age}d old, threshold {threshold}d)")
        except Exception:
            pass
    return stale


def main():
    try:
        json.load(sys.stdin)
    except Exception:
        pass

    today = date.today()

    # Load deadlines from STATUS.md dynamically
    deadlines = None
    try:
        with open(STATUS_FILE) as f:
            deadlines = parse_dates_from_status(f.read())
    except Exception:
        pass

    if not deadlines:
        deadlines = FALLBACK_DEADLINES

    # Build deadline warnings
    # context-load.py fires on EVERY prompt — only surface urgent (≤7d) and past deadlines.
    # Full decision dashboard lives in session-start.py (SessionStart, fires once per session).
    warnings = []
    for d in deadlines:
        days_left = (d["date"] - today).days
        if days_left < 0:
            warnings.append(f"  ⚫ PAST DUE: {d['label']} ({abs(days_left)}d ago — update STATUS.md)")
        elif days_left <= 7:
            warnings.append(f"  🔴 URGENT: {d['label']} — {days_left} day(s) remaining")

    # Check memory staleness
    stale_files = check_memory_staleness()

    lines = []
    if warnings:
        lines.append("**ACTIVE DEADLINES:**")
        lines.extend(warnings)

    if stale_files:
        lines.append("**⚠️ STALE MEMORY FILES (update before trusting advice):**")
        for f in stale_files:
            lines.append(f"  • {f}")

    if lines:
        print(json.dumps({"type": "text", "text": "\n".join(lines)}))


if __name__ == "__main__":
    main()
