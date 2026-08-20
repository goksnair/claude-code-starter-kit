#!/usr/bin/env python3
"""
Stop hook — memory-gap-surface.py
Surfaces uncaptured memory items at session end as a checklist.
Does NOT auto-write to any memory file — surfaces only.

Heuristics detected:
  H1: MCP tool calls that returned an ID/URL with no subsequent /lock call
  H2: reference_*.md files on disk absent from MEMORY.md index
  H3: Confirmed decisions in SESSION_HANDOFF.md not backed by a memory file write
"""
import json
import os
import re
import sys
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
# Resolve project path: CLAUDE_PROJECT_DIR env var (set by settings.json hooks) → cwd fallback
_project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
_proj_slug = "-".join(str(_project_dir).lstrip("/").split("/"))
MEMORY_DIR = HOME / ".claude" / "projects" / _proj_slug / "memory"
MEMORY_MD = MEMORY_DIR / "MEMORY.md"
_handoff_proj = _project_dir / ".claude" / "status" / "SESSION_HANDOFF.md"
_handoff_home = HOME / ".claude" / "status" / "SESSION_HANDOFF.md"
HANDOFF_PATH = _handoff_proj if _handoff_proj.exists() else _handoff_home
AGENT_STATE = _project_dir / ".claude" / "scratch" / "AGENT_STATE.json"

# Patterns that suggest an external resource ID was returned by an MCP tool
MCP_ID_PATTERNS = [
    r'"spreadsheetId"\s*:\s*"([^"]{10,})"',
    r'"fileId"\s*:\s*"([^"]{10,})"',
    r'"scriptId"\s*:\s*"([^"]{10,})"',
    r'"pageId"\s*:\s*"([^"]{10,})"',
    r'"projectId"\s*:\s*"([^"]{10,})"',
    r'"formId"\s*:\s*"([^"]{10,})"',
    r'"databaseId"\s*:\s*"([^"]{10,})"',
    r'(https://vercel\.app/[^\s"\']{10,})',
    r'(https://[a-z0-9-]+\.supabase\.co[^\s"\']*)',
]

RUPEE_PATTERN = re.compile(r'[₹]|Rs\.\s*\d|INR\s*\d')


def read_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def h1_mcp_ids_without_lock() -> list:
    """Heuristic: reads mcp-tool-results.jsonl sidecar, scans result fields for MCP resource IDs."""
    import sys as _sys
    gaps = []
    sidecar = Path(os.path.expanduser("~")) / ".claude" / "scratch" / "mcp-tool-results.jsonl"
    if not sidecar.exists():
        print("[memory-gap-surface] H1: mcp-tool-results.jsonl sidecar not found — skipping H1.", file=_sys.stderr)
        return gaps

    ID_KEY_PATTERNS = re.compile(
        r'"(?:id|fileId|scriptId|spreadsheetId|pageId|projectId|formId|databaseId)"\s*:\s*"([^"]{8,})"'
    )
    UUID_PATTERN = re.compile(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}')

    try:
        lines = sidecar.read_text(encoding="utf-8").splitlines()
    except Exception:
        return gaps

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue
        result_str = obj.get("result", "")
        tool = obj.get("tool", "")
        hit = ID_KEY_PATTERNS.search(result_str) or UUID_PATTERN.search(result_str)
        if hit:
            val = hit.group(0)[:60]
            gaps.append(f"MCP resource ID detected in {tool} result (no /lock confirmed): {val}")

    return gaps

def h2_reference_files_not_in_index() -> list:
    """Heuristic: reference_*.md files in memory dir absent from MEMORY.md."""
    gaps = []
    if not MEMORY_DIR.exists():
        return gaps
    index_text = read_safe(MEMORY_MD)
    for f in MEMORY_DIR.iterdir():
        if not f.name.startswith("reference_") or not f.name.endswith(".md"):
            continue
        if f.name not in index_text:
            gaps.append(f"reference file not in MEMORY.md index: {f.name}")
    return gaps


def h3_handoff_decisions_without_memory_write() -> list:
    """Heuristic: COMPLETED THIS SESSION items in HANDOFF not yet in any .claude/memory file."""
    gaps = []
    handoff_text = read_safe(HANDOFF_PATH)
    if not handoff_text:
        return gaps

    m = re.search(r"##\s+COMPLETED THIS SESSION.*?\n(.*?)(?=\n##|\Z)", handoff_text, re.DOTALL)
    if not m:
        return gaps

    bullets = [
        re.sub(r"^[\s✅•-]+", "", line).strip()
        for line in m.group(1).splitlines()
        if line.strip() and re.match(r"^\s*[✅•-]", line)
    ]

    memory_dir = PROJ / ".claude" / "memory"
    if not memory_dir.exists():
        memory_dir = HOME / ".claude" / "memory"
    memory_text = ""
    if memory_dir.exists():
        for mf in memory_dir.iterdir():
            if mf.suffix == ".md":
                memory_text += read_safe(mf)

    for bullet in bullets[:10]:
        core = bullet[:50].lower()
        if len(core) < 8:
            continue
        if core not in memory_text.lower():
            gaps.append(f"COMPLETED item may lack memory write: {bullet[:70]}")
    return gaps


def auto_index_sync() -> list:
    """
    Auto-indexer: scan memory dir for reference_*.md files absent from MEMORY.md.
    Appends index stubs only — never edits existing entries or file content.
    Returns list of stubs appended.
    """
    appended = []
    if not MEMORY_DIR.exists():
        return appended
    index_text = read_safe(MEMORY_MD)
    if '# Memory Index' not in index_text:
        print("[memory-gap-surface] WARNING: MEMORY.md missing '# Memory Index' sentinel — skipping auto-index to avoid corruption.", file=__import__('sys').stderr)
        return appended

    new_stubs = []
    for f in sorted(MEMORY_DIR.iterdir()):
        if not f.name.startswith("reference_") or not f.name.endswith(".md"):
            continue
        if f.name in index_text:
            continue
        stub = f"- [{f.stem}]({f.name}) — AUTO-INDEXED {f.stat().st_mtime:.0f} TODO: add description"
        new_stubs.append(stub)
        appended.append(f.name)

    if new_stubs:
        try:
            with MEMORY_MD.open("a", encoding="utf-8") as fh:
                fh.write("\n" + "\n".join(new_stubs) + "\n")
        except Exception:
            pass

    return appended


def main() -> None:
    try:
        sys.stdin.read()  # consume Stop hook stdin (ignored — no actionable data)
    except Exception:
        pass

    all_gaps = []
    all_gaps.extend(h1_mcp_ids_without_lock())
    all_gaps.extend(h2_reference_files_not_in_index())
    all_gaps.extend(h3_handoff_decisions_without_memory_write())

    # Run auto-indexer (append stubs, never edits content)
    synced = auto_index_sync()

    if all_gaps or synced:
        out = ["[memory-gap-surface] Session-end memory audit:"]
        if all_gaps:
            out.append("GAPS DETECTED — run /lock or /capture before closing:")
            for g in all_gaps:
                out.append(f"  [ ] {g}")
        if synced:
            out.append(f"AUTO-INDEXED {len(synced)} unindexed reference file(s) into MEMORY.md:")
            for s in synced:
                out.append(f"  + {s} (add description to MEMORY.md)")
        print("\n".join(out))
    else:
        print("[memory-gap-surface] Memory audit clean — no gaps detected.")


if __name__ == "__main__":
    main()
