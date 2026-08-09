#!/usr/bin/env python3
"""
content-output-guard.py — Stop hook

Scans the session transcript AND recent subagent output files for customer-facing
content (emails, social posts, proposals, SMS, website copy) generated WITHOUT
a /copy-check run in the same session.

Why: copy-quality-guard.py fires on Write/Edit to files. Most inline content
bypasses the file-path hook. Subagents dispatched via Task() write to separate
transcripts that the main Stop hook can't see — but their output lands in known
locations (.claude/scratch/, project outputs/) which we can scan here.

Non-blocking (warns, does not exit 2) — we can't block content already shown.

Hook type: Stop
Matcher: (none — fires on all Stop events)
"""

import json
import os
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = os.environ.get("PROJECT_ROOT", os.getcwd())

# Signals in assistant text that suggest customer-facing content was generated
CONTENT_SIGNALS = [
    # Email signals
    r"subject\s*:\s*\S",
    r"dear\s+\w+",
    r"hi\s+\w+,",
    r"hello\s+\w+,",
    r"best\s+regards",
    r"warm\s+regards",
    r"kind\s+regards",
    r"looking\s+forward",
    r"please\s+find\s+attached",
    r"i\s+hope\s+this\s+(email|message|note)\s+finds",
    # Social post signals
    r"#\w{3,}",                          # hashtags
    r"\[caption\]",
    r"\[hook\]",
    r"\[cta\]",
    r"thread\s*\d+/\d+",                 # "1/5" style thread markers
    r"(?:instagram|linkedin|twitter|x\.com)\s+(?:post|caption|copy)",
    # Proposal/pitch signals
    r"executive\s+summary",
    r"scope\s+of\s+work",
    r"deliverable[s]?\s*:",
    r"proposed\s+(timeline|budget|solution)",
    # Website/landing page signals
    r"above\s+the\s+fold",
    r"hero\s+(headline|copy|text)",
    r"cta\s*(button|text|copy)",
    r"value\s+proposition",
    # SMS/WhatsApp signals
    r"(?:sms|whatsapp)\s+(?:message|copy|text)",
    r"(?:text|message)\s+to\s+(?:send|share)",
]

CONTENT_RE = re.compile(
    "|".join(CONTENT_SIGNALS),
    re.IGNORECASE,
)

# Signals that /copy-check was run this session
COPY_CHECK_SIGNALS = [
    r"/copy-check",
    r"copy.check",
    r"copy_check",
    r"PASS.*FAIL",              # copy-check output format
    r"\d+\s+PASS.*\d+\s+FAIL",
]
COPY_CHECK_RE = re.compile("|".join(COPY_CHECK_SIGNALS), re.IGNORECASE)

# Subagent output directories to scan for recently-written .md files
SUBAGENT_OUTPUT_DIRS = [
    os.path.join(PROJECT_ROOT, ".claude", "scratch"),
]

# Subagent output files to always skip (infra, not content)
SUBAGENT_SKIP_FILES = {
    "SCRATCHPAD.md", "AGENT_STATE.json", "PE_OUTPUT.md",
    "CURRENT_STATE.md", "SESSION_HANDOFF.md",
}

# Only scan subagent files modified in the last N seconds (current session window)
SUBAGENT_MAX_AGE_SECONDS = 4 * 3600  # 4 hours


def load_transcript(path: str) -> list[dict]:
    entries = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    except Exception:
        pass
    return entries


def extract_assistant_text(entries: list[dict]) -> str:
    """Collect all assistant text output from the transcript."""
    parts = []
    for entry in entries:
        msg = entry.get("message", {})
        if msg.get("role") != "assistant":
            continue
        content = msg.get("content", [])
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "text":
                    parts.append(block.get("text", ""))
    return "\n".join(parts)


def copy_check_ran(entries: list[dict]) -> bool:
    """Check if /copy-check was invoked or its output appeared this session."""
    for entry in entries:
        msg = entry.get("message", {})
        content = msg.get("content", [])
        if isinstance(content, str):
            if COPY_CHECK_RE.search(content):
                return True
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text", "") or block.get("input", {}).get("command", "")
                    if text and COPY_CHECK_RE.search(text):
                        return True
    return False


def content_generated(text: str) -> list[str]:
    """Return list of matched signal descriptions if customer-facing content found."""
    matches = []
    for signal in CONTENT_SIGNALS:
        if re.search(signal, text, re.IGNORECASE):
            label = signal.replace(r"\s*", " ").replace(r"\s+", " ").replace(r"\S", "…").replace(r"\w+", "…").replace("(?:", "").replace(")", "").split("|")[0][:50]
            matches.append(label.strip())
    return matches[:3]  # cap at 3 signal examples


def scan_subagent_outputs() -> tuple[str, list[str]]:
    """
    Scan recent subagent output .md files for content signals.
    Returns (combined_text, list_of_flagged_filenames).
    """
    now = time.time()
    flagged_files = []
    all_text_parts = []

    for dir_path in SUBAGENT_OUTPUT_DIRS:
        d = Path(dir_path)
        if not d.exists():
            continue
        for f in d.glob("*.md"):
            if f.name in SUBAGENT_SKIP_FILES:
                continue
            try:
                age = now - f.stat().st_mtime
                if age > SUBAGENT_MAX_AGE_SECONDS:
                    continue
                text = f.read_text(encoding="utf-8", errors="ignore")
                if CONTENT_RE.search(text):
                    flagged_files.append(f.name)
                    all_text_parts.append(text)
            except Exception:
                continue

    return "\n".join(all_text_parts), flagged_files


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    transcript_path = data.get("transcript_path", "")
    entries = []
    if transcript_path and os.path.exists(transcript_path):
        entries = load_transcript(transcript_path)

    # If copy-check already ran in main transcript, no need to warn
    if entries and copy_check_ran(entries):
        sys.exit(0)

    # --- Check 1: main transcript assistant text ---
    transcript_signals = []
    if entries:
        assistant_text = extract_assistant_text(entries)
        if assistant_text:
            transcript_signals = content_generated(assistant_text)

    # --- Check 2: subagent output files ---
    subagent_text, flagged_files = scan_subagent_outputs()
    subagent_signals = content_generated(subagent_text) if subagent_text else []

    # Nothing found in either place
    if not transcript_signals and not subagent_signals:
        sys.exit(0)

    # Build warning message
    parts = ["⚠️  CONTENT OUTPUT GUARD — customer-facing content detected in this session"]

    if transcript_signals:
        sig_list = "\n".join(f"   • {s}" for s in transcript_signals)
        parts.append(f"Inline output signals:\n{sig_list}")

    if flagged_files:
        file_list = ", ".join(flagged_files)
        parts.append(f"Subagent output files with content signals: {file_list}")
        if subagent_signals:
            sub_list = "\n".join(f"   • {s}" for s in subagent_signals[:3])
            parts.append(f"Signal examples:\n{sub_list}")

    parts.append(
        "If any of this content will be shared externally (email, social, website, proposal):\n"
        "1. Run /no-ai-slop [paste the content] — strip AI patterns\n"
        "2. Run /copy-check — must score ≥22 PASS, 0 FAIL before sending\n\n"
        "If this was internal/scratchpad content only, ignore this warning."
    )

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": "\n\n".join(parts),
        }
    }))
    sys.exit(0)


if __name__ == "__main__":
    main()
