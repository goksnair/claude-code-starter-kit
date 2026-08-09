#!/usr/bin/env python3
"""
bash-tool-guard.py — PreToolUse(Bash) hook

Fires before every Bash tool call. Detects shell aliases that have dedicated
Claude Code tool equivalents and injects a correction pointing to the right tool.

Enforces: ai-workflow.md § "Tool-to-Tool Mapping — NEVER use shell aliases"

Mapping enforced:
  cat / head / tail  → Read tool
  grep / rg          → Grep tool
  find               → Glob tool
  ls                 → Glob tool (or LS tool)
  sed / awk          → Edit tool

Hook type: PreToolUse
Matcher: Bash
Severity: non-blocking (warn + redirect — never block legitimate Bash usage)

Note: Only fires when the alias is the PRIMARY purpose of the command.
      Legitimate pipeline uses (e.g. git log | grep) are not flagged.
"""

import json
import os
import re
import sys

# Pattern: command starts with (or is) the alias, not buried in a pipeline
# Each entry: (compiled_regex, alias_name, preferred_tool, usage_hint)
ALIAS_RULES = [
    (
        re.compile(r'^\s*cat\s+\S', re.MULTILINE),
        "cat",
        "Read tool",
        "Read(file_path='<path>')",
    ),
    (
        re.compile(r'^\s*head\s+', re.MULTILINE),
        "head",
        "Read tool",
        "Read(file_path='<path>', limit=<n>)",
    ),
    (
        re.compile(r'^\s*tail\s+', re.MULTILINE),
        "tail",
        "Read tool",
        "Read(file_path='<path>', offset=<last_n_start>, limit=<n>)",
    ),
    (
        re.compile(r'^\s*grep\s+', re.MULTILINE),
        "grep",
        "Grep tool",
        "Grep(pattern='<regex>', path='<dir>')",
    ),
    (
        re.compile(r'^\s*rg\s+', re.MULTILINE),
        "rg",
        "Grep tool",
        "Grep(pattern='<regex>', path='<dir>')",
    ),
    (
        re.compile(r'^\s*find\s+', re.MULTILINE),
        "find",
        "Glob tool",
        "Glob(pattern='**/<name>')",
    ),
    (
        re.compile(r'^\s*ls\s*(?:\S|$)', re.MULTILINE),
        "ls",
        "Glob tool",
        "Glob(pattern='<dir>/*') or LS tool",
    ),
    (
        re.compile(r'^\s*sed\s+', re.MULTILINE),
        "sed",
        "Edit tool",
        "Edit(file_path='<path>', old_string='...', new_string='...')",
    ),
    (
        re.compile(r'^\s*awk\s+', re.MULTILINE),
        "awk",
        "Edit tool",
        "Edit(file_path='<path>', old_string='...', new_string='...')",
    ),
]

# Exceptions: legitimate Bash uses where these commands are acceptable
# (when they appear as part of a larger pipeline or git command)
EXCEPTION_PATTERNS = [
    re.compile(r'git\s+\S+.*\|\s*(grep|awk|sed)'),   # git log | grep etc
    re.compile(r'\|\s*(grep|awk|sed|head|tail)\s+'),  # pipeline context
    re.compile(r'(grep|sed|awk)\s+-[A-Za-z]*i\s+.*\.sh'),  # processing scripts
]


def is_exception(command: str) -> bool:
    return any(p.search(command) for p in EXCEPTION_PATTERNS)


def main() -> None:
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        sys.exit(0)

    command = data.get("tool_input", {}).get("command", "")
    if not command:
        sys.exit(0)

    if is_exception(command):
        sys.exit(0)

    violations = []
    for pattern, alias, preferred, hint in ALIAS_RULES:
        if pattern.search(command):
            violations.append(f"  `{alias}` → use **{preferred}**: `{hint}`")

    if not violations:
        sys.exit(0)

    message = (
        "TOOL DISCIPLINE REMINDER (ai-workflow.md):\n"
        "Shell aliases detected that have dedicated Claude Code tool equivalents:\n"
        + "\n".join(violations)
        + "\n\nUsing dedicated tools:\n"
        "  • Shows the user a clear, reviewable tool call (not a black-box shell command)\n"
        "  • Avoids shell permission prompts\n"
        "  • Preserves tool audit trail\n"
        "Proceeding with Bash anyway — this is a reminder, not a block."
    )

    output = {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": message
        }
    }
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
