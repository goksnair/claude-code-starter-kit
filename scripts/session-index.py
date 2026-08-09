#!/usr/bin/env python3
"""
session-index.py — FTS5 full-text index over Claude Code session transcripts.

Usage:
  python3 session-index.py build          # index all projects
  python3 session-index.py build myproject # index one project only
  python3 session-index.py search "query"
  python3 session-index.py search "query" --project myproject --limit 10

Index lives at: ~/.claude/session-index.db
Run manually after heavy sessions or nightly via cron.
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

CLAUDE_DIR = Path.home() / ".claude" / "projects"
DB_PATH = Path.home() / ".claude" / "session-index.db"

# Projects excluded from indexing
SKIP_PROJECTS = {"root"}


def dir_to_friendly(dir_name: str) -> str:
    """Convert a Claude project dir name (e.g. -Users-jane-my-project) to a friendly name."""
    # Strip leading dash, split on remaining dashes, take last 1-2 meaningful segments
    parts = dir_name.lstrip("-").split("-")
    # Skip home dir segments (Users, username) — keep last 1-2 path segments
    meaningful = [p for p in parts if p and len(p) > 1 and p.lower() not in ("users",)]
    if len(meaningful) >= 2:
        return "-".join(meaningful[-2:]).lower()
    elif meaningful:
        return meaningful[-1].lower()
    return dir_name


# Build reverse map dynamically at search time from indexed project names
def get_project_names(db):
    rows = db.execute("SELECT DISTINCT project FROM sessions").fetchall()
    return {r[0] for r in rows}


def get_db():
    db = sqlite3.connect(DB_PATH)
    db.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS sessions USING fts5(
            session_id,
            project,
            timestamp,
            role,
            content,
            tokenize='porter ascii'
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS indexed_files (
            path TEXT PRIMARY KEY,
            indexed_at TEXT,
            entry_count INTEGER
        )
    """)
    db.commit()
    return db


def extract_text(content):
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", "").strip())
        return " ".join(parts)
    return ""


def index_file(db, jsonl_path: Path, project: str):
    path_str = str(jsonl_path)
    already = db.execute(
        "SELECT indexed_at FROM indexed_files WHERE path = ?", (path_str,)
    ).fetchone()

    mtime = datetime.fromtimestamp(jsonl_path.stat().st_mtime).isoformat()
    if already and already[0] >= mtime:
        return 0  # up to date

    # Remove stale entries for this file
    session_id = jsonl_path.stem
    db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    count = 0
    try:
        with open(jsonl_path, encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue

                role = obj.get("type")
                if role not in ("user", "assistant"):
                    continue

                msg = obj.get("message", {})
                if not isinstance(msg, dict):
                    continue

                text = extract_text(msg.get("content", ""))
                if not text or len(text) < 20:
                    continue

                ts = obj.get("timestamp", "")
                db.execute(
                    "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
                    (session_id, project, ts, role, text),
                )
                count += 1
    except Exception as e:
        print(f"  WARN: {jsonl_path.name} — {e}", file=sys.stderr)
        return 0

    db.execute(
        "INSERT OR REPLACE INTO indexed_files VALUES (?, ?, ?)",
        (path_str, mtime, count),
    )
    db.commit()
    return count


def index_session_record(db, md_path: Path, project: str):
    """Index an immutable session record (.md) written by /end."""
    path_str = str(md_path)
    already = db.execute(
        "SELECT indexed_at FROM indexed_files WHERE path = ?", (path_str,)
    ).fetchone()

    mtime = datetime.fromtimestamp(md_path.stat().st_mtime).isoformat()
    if already and already[0] >= mtime:
        return 0

    # Session records are named YYYY-MM-DD-<suffix>.md — use stem as session_id
    session_id = md_path.stem
    db.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    count = 0
    try:
        text = md_path.read_text(encoding="utf-8", errors="replace").strip()
        if not text or len(text) < 20:
            return 0
        # Extract date from filename for timestamp
        ts = session_id[:10] + "T00:00:00"
        db.execute(
            "INSERT INTO sessions VALUES (?, ?, ?, ?, ?)",
            (session_id, project, ts, "session-record", text),
        )
        count = 1
    except Exception as e:
        print(f"  WARN: {md_path.name} — {e}", file=sys.stderr)
        return 0

    db.execute(
        "INSERT OR REPLACE INTO indexed_files VALUES (?, ?, ?)",
        (path_str, mtime, count),
    )
    db.commit()
    return count


def build(project_filter=None):
    db = get_db()
    total_files = 0
    total_entries = 0

    projects = list(CLAUDE_DIR.iterdir()) if CLAUDE_DIR.exists() else []

    for proj_dir in sorted(projects):
        if not proj_dir.is_dir():
            continue

        # Resolve project name — auto-derive friendly name from dir structure
        proj_name = proj_dir.name
        friendly = dir_to_friendly(proj_name)

        if friendly in SKIP_PROJECTS:
            continue

        if project_filter and friendly != project_filter and proj_name != project_filter:
            continue

        jsonl_files = list(proj_dir.glob("*.jsonl"))
        if jsonl_files:
            print(f"Indexing {friendly} ({len(jsonl_files)} files)...")
            for jf in jsonl_files:
                n = index_file(db, jf, friendly)
                if n:
                    total_entries += n
                    total_files += 1

        # Also index immutable session records written by /end
        sessions_dir = proj_dir / "sessions"
        if sessions_dir.is_dir():
            md_files = list(sessions_dir.glob("*.md"))
            if md_files:
                print(f"Indexing {friendly} session records ({len(md_files)} records)...")
                for mf in md_files:
                    n = index_session_record(db, mf, friendly)
                    if n:
                        total_entries += n
                        total_files += 1

    row = db.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
    print(f"\n✓ Index updated — {total_files} files processed, {total_entries} new entries")
    print(f"  Total indexed: {row} entries in {DB_PATH}")
    db.close()


def fts_query(raw: str) -> str:
    """Convert a plain-language query to an FTS5 query string.
    Multi-word input becomes an AND of individual terms so all words must appear.
    Quoted phrases are passed through as-is.
    """
    raw = raw.strip()
    if '"' in raw:
        return raw  # user supplied explicit FTS5 syntax
    terms = raw.split()
    if len(terms) == 1:
        return terms[0]
    return " AND ".join(terms)


def search(query, project=None, limit=8):
    if not DB_PATH.exists():
        print("Index not built yet. Run: python3 session-index.py build")
        sys.exit(1)

    db = get_db()
    fts = fts_query(query)

    if project:
        # stored values are friendly names derived from dir structure
        friendly = project
        rows = db.execute(
            """
            SELECT session_id, project, timestamp, role,
                   snippet(sessions, 4, '[', ']', '...', 32) as excerpt
            FROM sessions
            WHERE sessions MATCH ? AND project = ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts, friendly, limit),
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT session_id, project, timestamp, role,
                   snippet(sessions, 4, '[', ']', '...', 32) as excerpt
            FROM sessions
            WHERE sessions MATCH ?
            ORDER BY rank
            LIMIT ?
            """,
            (fts, limit),
        ).fetchall()

    db.close()

    if not rows:
        print(f"No results for: {query}")
        return

    print(f"\n── Session search: '{query}' ── {len(rows)} results ──\n")
    seen_sessions = {}
    for session_id, project, ts, role, excerpt in rows:
        date = ts[:10] if ts else "unknown"
        if session_id not in seen_sessions:
            seen_sessions[session_id] = date
            print(f"📅 {date}  [{project}]  session: {session_id[:8]}...")
        prefix = "  you: " if role == "user" else "  ai:  "
        print(f"{prefix}{excerpt.strip()}")
        print()


def main():
    args = sys.argv[1:]
    if not args or args[0] == "build":
        project_filter = args[1] if len(args) > 1 else None
        build(project_filter)
    elif args[0] == "search":
        if len(args) < 2:
            print("Usage: session-index.py search 'query' [--project name] [--limit N]")
            sys.exit(1)
        query = args[1]
        project = None
        limit = 8
        i = 2
        while i < len(args):
            if args[i] == "--project" and i + 1 < len(args):
                project = args[i + 1]
                i += 2
            elif args[i] == "--limit" and i + 1 < len(args):
                limit = int(args[i + 1])
                i += 2
            else:
                i += 1
        search(query, project, limit)
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
