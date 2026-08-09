#!/usr/bin/env python3
"""
PostToolUse hook — fires after every tool call.
When Write or Edit tool modifies a file, validates it's routed correctly.
Warns if knowledge-grade content is written to scratch or vice versa.
Also scans content for financial data (₹ amounts) in non-vault repo files.
"""

import json
import sys
import os
import re
from pathlib import Path

PROJ = str(Path(__file__).parent.parent.parent)
VAULT = os.path.expanduser("{{VAULT_PATH}}")

# Files that should NEVER receive permanent content
SCRATCH_PATHS = [".claude/scratch/", "SCRATCHPAD"]

# Correct home for each content type (content keyword → canonical path)
ROUTING_TABLE = {
    "income":      f"{VAULT}/finances.md",
    "portfolio":   f"{VAULT}/finances.md",
    "receivable":  f"{VAULT}/finances.md",
    "contact":     f"{VAULT}/contacts.md",
    "goal":        ".claude/memory/goals.md",
    "deadline":    ".claude/memory/STATUS.md",
    "decision":    ".claude/memory/STATUS.md",
    "persona":     ".claude/personas/",
    "skill":       "skills/",
    "venture":     "knowledge/ventures/",
    "idea":        "knowledge/indie/idea-vault.md",
}

# Rupee symbol defined via unicode code point — avoids literal character in source,
# which would falsely trigger the content-guard hook on this detector file itself.
_RUPEE = chr(0x20B9)

# Detection patterns — regex strings used to find financial data in content.
# These are detectors, not prices. Do not route to vault.
FINANCIAL_PATTERNS = [
    _RUPEE + r'\s*[\d,]+',       # matches amounts: <rupee>1,50,000 or <rupee> 90000
    _RUPEE + r'[\d,.]+[LlKk]',   # matches shorthand: <rupee>4L, <rupee>90K
]

# File path segments that indicate a non-vault repo file where ₹ amounts are forbidden
FINANCIAL_FORBIDDEN_PATHS = [
    "knowledge/ventures/",
    "knowledge/growth/",
    "knowledge/indie/",
    "knowledge/security/",
    "knowledge/finance/",
    ".claude/memory/STATUS.md",
    ".claude/memory/goals.md",
    ".claude/personas/",
]

def has_financial_content(text):
    """Return first matching financial pattern found in text, or None."""
    for pattern in FINANCIAL_PATTERNS:
        m = re.search(pattern, text)
        if m:
            return m.group(0)
    return None

def is_financial_forbidden_path(rel_path):
    """Return True if this repo path should never contain ₹ amounts."""
    for segment in FINANCIAL_FORBIDDEN_PATHS:
        if segment in rel_path:
            return True
    return False

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    if tool_name not in ("Write", "Edit"):
        return

    file_path = tool_input.get("file_path", "") or tool_input.get("path", "")
    if not file_path:
        return

    # Vault-existence guard — skip all enforcement if vault not configured or missing
    vault_path = Path(os.path.expanduser(VAULT)) if '{{' not in VAULT else None
    if vault_path is None or not vault_path.exists():
        print('[memory-validator] vault not found, skipping vault enforcement')
        return

    # Vault files are always safe — skip all checks
    if file_path.startswith(VAULT):
        return

    rel_path = file_path.replace(PROJ + "/", "").replace(os.path.expanduser("~") + "/" + Path(PROJ).name + "/", "")
    content = tool_input.get("content", "") or tool_input.get("new_string", "") or ""

    # Warn if knowledge-grade file is being written to scratch
    for scratch in SCRATCH_PATHS:
        if scratch in rel_path:
            if len(content) > 500:
                print(f"[memory-validator] ⚠️  Large write to scratch ({rel_path}). "
                      f"If this is decision-grade content, migrate to knowledge/ before session end.")
            return

    # --- Financial content guard ---
    # Scan content for rupee amounts in files where they don't belong
    if is_financial_forbidden_path(rel_path) and content:
        match = has_financial_content(content)
        if match:
            print(
                f"[memory-validator] 🔴  BLOCKED — FINANCIAL DATA IN REPO FILE\n"
                f"   File: {rel_path}\n"
                f"   Found: '{match}'\n"
                f"   Rule: financial amounts belong in {{VAULT_PATH}}/finances.md, not in venture/growth/memory files.\n"
                f"   Fix: replace the amount with: see {{VAULT_PATH}}/finances.md ([section])\n"
                f"   This write has been blocked. Update content and retry."
            )
            sys.exit(1)

    # Warn if repo finances.md or network.md stub is receiving real content
    if ".claude/memory/" in rel_path:
        basename = os.path.basename(rel_path)
        if basename == "finances.md":
            match = has_financial_content(content)
            if match:
                print(
                    f"[memory-validator] 🔴  FINANCIAL DATA IN REPO STUB\n"
                    f"   finances.md in the repo is a stub — real numbers go to {{VAULT_PATH}}/finances.md\n"
                    f"   Found: '{match}'"
                )
            else:
                print(f"[memory-validator] ✅  finances.md stub updated.")
        elif basename == "contacts.md":
            print(f"[memory-validator] ⚠️  contacts.md updated — ensure no sensitive contact details; those go to {{VAULT_PATH}}/contacts.md")

    # Confirm knowledge writes
    if "knowledge/" in rel_path:
        print(f"[memory-validator] ✅  Knowledge file updated: {rel_path}")

if __name__ == "__main__":
    main()
