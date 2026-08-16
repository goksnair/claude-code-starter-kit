#!/usr/bin/env python3
import json
import os
import re
import sys
from pathlib import Path

INFRA_EXTENSIONS = {".sh", ".py", ".plist", ".json"}
AGENT_PATH_MARKER = ".claude/agents/"
MEMORY_PATH_MARKER = ".claude/memory/"

TEST_PATTERNS = [
    r"bash\s+-[nx]",
    r"python3\s+-m\s+py_compile",
    r"plutil\s+-lint",
    r"python3\s+-m\s+json",
    r"json\.load",
    r"infra-verify\.py",
    r"bash\s+.+\.sh",
    r"python3\s+.+\.py",
]
TEST_RE = re.compile("|".join(TEST_PATTERNS), re.IGNORECASE)

SKIP_FRAGMENTS = [
    "node_modules/", ".git/", "graphify-out/", "archive/",
    "/tmp/", "SCRATCHPAD", "AGENT_STATE", "SESSION_HANDOFF",
    "CURRENT_STATE", "STATUS.md", "goals.md",
]


def should_skip(file_path: str) -> bool:
    for frag in SKIP_FRAGMENTS:
        if frag in file_path:
            return True
    return False


def is_infra_file(file_path: str) -> bool:
    ext = Path(file_path).suffix.lower()
    if ext in INFRA_EXTENSIONS:
        return True
    if ext == ".md" and AGENT_PATH_MARKER in file_path:
        return True
    return False


def extract_tool_sequence(entries: list[dict]) -> list[tuple[str, str, str]]:
    sequence = []
    for entry in entries:
        msg = entry.get("message", {})
        if not msg:
            continue
        content = msg.get("content", [])
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") != "tool_use":
                continue
            name = block.get("name", "")
            inp = block.get("input", {})
            tool_id = block.get("id", "")
            if name in ("Write", "Edit"):
                fp = inp.get("file_path", "")
                if fp:
                    sequence.append((name, fp, tool_id))
            elif name == "Bash":
                cmd = inp.get("command", "")
                if cmd:
                    sequence.append(("Bash", cmd, tool_id))
    return sequence


def find_untested_files(sequence: list[tuple[str, str, str]]) -> list[str]:
    write_positions = {}
    for i, (tool, value, tid) in enumerate(sequence):
        if tool in ("Write", "Edit") and is_infra_file(value) and not should_skip(value):
            write_positions[value] = i

    untested = []
    for file_path, write_pos in write_positions.items():
        tested = False
        file_name = Path(file_path).name
        for i, (tool, value, tid) in enumerate(sequence):
            if i <= write_pos:
                continue
            if tool == "Bash":
                if TEST_RE.search(value):
                    if (file_name in value
                            or file_path in value
                            or "infra-verify" in value
                            or "all" in value.lower()):
                        tested = True
                        break
                    if re.search(r"py_compile|bash\s+-[nx]|plutil", value) and file_name not in value:
                        if "infra-verify" in value:
                            tested = True
                            break
        if not tested:
            untested.append(file_path)

    return untested


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    transcript_path = data.get("transcript_path", "")
    if not transcript_path or not os.path.exists(transcript_path):
        sys.stdout.write(json.dumps(data) if data else "")
        sys.exit(0)

    entries = []
    try:
        with open(transcript_path, encoding="utf-8") as f:
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

    sequence = extract_tool_sequence(entries)

    if not sequence:
        sys.stdout.write(json.dumps(data) if data else "")
        sys.exit(0)

    untested = find_untested_files(sequence)

    if untested:
        short = [p.replace(os.path.expanduser("~"), "~") for p in untested]
        lines = [
            "implementation-audit: infra files written but NOT tested this session:",
        ]
        for f in short:
            lines.append(f"   - {f}")
        lines.append("Run infra-verify or a dry-run before ending session.")
        output = {"hookSpecificOutput": "\n".join(lines)}
        sys.stdout.write(json.dumps(output))
        sys.exit(0)

    sys.stdout.write(json.dumps(data) if data else "")
    sys.exit(0)


if __name__ == "__main__":
    main()
