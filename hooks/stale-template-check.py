#!/usr/bin/env python3
"""
stale-template-check.py — Compare infra/templates/ against .claude/ to detect
when source files are newer than their installed counterparts.

Usage:
  python3 infra/templates/hooks/stale-template-check.py

Prints a table of stale templates. Exit 0 always (informational only).
"""

import os
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())

TEMPLATES_DIR = Path(PROJECT_ROOT) / "infra" / "templates"
CLAUDE_DIR = Path(PROJECT_ROOT) / ".claude"

# Maps from template subdirectory → installed .claude/ subdirectory
DIR_MAP = {
    "commands": CLAUDE_DIR / "commands",
    "hooks": CLAUDE_DIR / "hooks",
    "agents": CLAUDE_DIR / "agents",
    "rules": CLAUDE_DIR / "rules",
    "config": CLAUDE_DIR,  # settings.json lives directly in .claude/
}

# File-level overrides: template file → installed path (relative to CLAUDE_DIR)
FILE_OVERRIDES = {
    "config/settings.json": CLAUDE_DIR / "settings.json",
    "config/infra-config.json": Path(PROJECT_ROOT) / "infra-config.json",
    "CLAUDE.md": Path(PROJECT_ROOT) / "CLAUDE.md",
    "weekly-health-checklist.md": Path(PROJECT_ROOT) / "weekly-health-checklist.md",
    "install.sh": Path(PROJECT_ROOT) / "infra" / "install.sh",
}


def mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except FileNotFoundError:
        return None


def fmt_age(seconds: float) -> str:
    days = int(seconds / 86400)
    hours = int((seconds % 86400) / 3600)
    if days > 0:
        return f"{days}d {hours}h"
    return f"{hours}h"


def check_dir(subdir: str, installed_dir: Path) -> list[dict]:
    results = []
    src_dir = TEMPLATES_DIR / subdir
    if not src_dir.exists():
        return results

    for src in src_dir.iterdir():
        if src.is_dir():
            continue
        installed = installed_dir / src.name
        t_src = mtime(src)
        t_dst = mtime(installed)

        if t_src is None:
            continue

        if t_dst is None:
            status = "NOT INSTALLED"
            staleness = None
        elif t_src > t_dst:
            status = "STALE"
            staleness = t_src - t_dst
        else:
            status = "OK"
            staleness = None

        results.append({
            "template": f"{subdir}/{src.name}",
            "installed": str(installed.relative_to(PROJECT_ROOT)) if installed.exists() else str(installed.relative_to(PROJECT_ROOT)) + " (missing)",
            "status": status,
            "staleness": staleness,
            "src_mtime": datetime.fromtimestamp(t_src).strftime("%Y-%m-%d %H:%M"),
        })

    return results


def check_file_overrides() -> list[dict]:
    results = []
    for rel_src, installed in FILE_OVERRIDES.items():
        src = TEMPLATES_DIR / rel_src
        t_src = mtime(src)
        t_dst = mtime(installed)

        if t_src is None:
            continue

        if t_dst is None:
            status = "NOT INSTALLED"
            staleness = None
        elif t_src > t_dst:
            status = "STALE"
            staleness = t_src - t_dst
        else:
            status = "OK"
            staleness = None

        try:
            display_installed = str(installed.relative_to(PROJECT_ROOT))
        except ValueError:
            display_installed = str(installed)

        results.append({
            "template": rel_src,
            "installed": display_installed,
            "status": status,
            "staleness": staleness,
            "src_mtime": datetime.fromtimestamp(t_src).strftime("%Y-%m-%d %H:%M"),
        })

    return results


def main():
    if not TEMPLATES_DIR.exists():
        print('no template dir, skipping')
        sys.exit(0)

    all_results = []

    for subdir, installed_dir in DIR_MAP.items():
        all_results.extend(check_dir(subdir, installed_dir))

    all_results.extend(check_file_overrides())

    stale = [r for r in all_results if r["status"] in ("STALE", "NOT INSTALLED")]
    ok = [r for r in all_results if r["status"] == "OK"]

    # Print header
    print()
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"STALE TEMPLATE CHECK — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Templates: {TEMPLATES_DIR}")
    print(f"Installed: {CLAUDE_DIR}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print()

    if not stale:
        print(f"✓ All {len(ok)} templates are current.")
        print()
        return

    # Print stale table
    col_w = [max(len(r["template"]) for r in stale) + 2,
             max(len(r["installed"]) for r in stale) + 2,
             14, 12]

    header = (
        f"{'Template':<{col_w[0]}}"
        f"{'Installed Path':<{col_w[1]}}"
        f"{'Status':<{col_w[2]}}"
        f"{'Template mtime':<{col_w[3]}}"
        f"  Staleness"
    )
    print(header)
    print("-" * (sum(col_w) + 10))

    for r in sorted(stale, key=lambda x: (x["status"], x["template"])):
        age_str = fmt_age(r["staleness"]) if r["staleness"] is not None else "—"
        print(
            f"{r['template']:<{col_w[0]}}"
            f"{r['installed']:<{col_w[1]}}"
            f"{r['status']:<{col_w[2]}}"
            f"{r['src_mtime']:<{col_w[3]}}"
            f"  {age_str}"
        )

    print()
    print(f"  {len(stale)} stale / not installed   {len(ok)} OK")
    print()
    print("To update: re-run install.sh or copy the template file and replace placeholders.")
    print()


if __name__ == "__main__":
    main()
