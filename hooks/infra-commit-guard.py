#!/usr/bin/env python3
"""
PostToolUse hook on Bash — [infra] commit prompt.
When a git commit is detected AND staged files include .claude/ paths:
prints a non-blocking prompt to add [infra] tag if template-relevant.
"""
import json
import re
import subprocess
import sys

def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    # Only fire on Bash tool
    if hook_input.get("tool_name") != "Bash":
        sys.exit(0)

    tool_input = hook_input.get("tool_input", {})
    command = tool_input.get("command", "")

    # Only fire when git commit is in the command
    if "git commit" not in command:
        sys.exit(0)

    # Skip if [infra] already in the command
    if "[infra]" in command:
        sys.exit(0)

    # Check if any staged files include .claude/ paths
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5
        )
        staged_files = result.stdout.strip().splitlines()
    except Exception:
        sys.exit(0)

    claude_files = [f for f in staged_files if ".claude/" in f]

    if claude_files:
        print(
            f"\n⚡ .claude/ files in this commit ({len(claude_files)} file(s)):\n"
            + "\n".join(f"   {f}" for f in claude_files[:5])
            + ("\n   ..." if len(claude_files) > 5 else "")
            + "\nIs this template-relevant? If yes, add [infra] to your commit message."
        )

    sys.exit(0)

if __name__ == "__main__":
    main()
