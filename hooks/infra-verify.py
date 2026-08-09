#!/usr/bin/env python3
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_PATH_FRAGMENTS = [
    "node_modules/",
    ".git/",
    "graphify-out/",
    "archive/",
    "/tmp/",
]

PLIST_REQUIRED_KEYS = ["Label", "ProgramArguments"]

AGENT_REQUIRED_FIELDS = ["name", "description", "tools"]

MEMORY_REQUIRED_FIELDS = ["last_updated"]

AGENT_PATH_MARKERS = [".claude/agents/", ".claude/personas/"]

MEMORY_PATH_MARKERS = [".claude/memory/"]


def should_skip(file_path: str) -> bool:
    for fragment in SKIP_PATH_FRAGMENTS:
        if fragment in file_path:
            return True
    return False


def check_bash(file_path: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["bash", "-n", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False, result.stderr.strip()
    return True, "bash -n passed"


def check_python(file_path: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["python3", "-m", "py_compile", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False, result.stderr.strip()

    try:
        content = Path(file_path).read_text(encoding="utf-8")
        imports = re.findall(r"^(?:import|from)\s+(\S+)", content, re.MULTILINE)
        stdlib = {
            "json", "os", "sys", "re", "subprocess", "pathlib", "datetime",
            "time", "math", "random", "string", "collections", "itertools",
            "functools", "typing", "io", "hashlib", "hmac", "base64",
            "urllib", "http", "shutil", "tempfile", "glob", "fnmatch",
            "logging", "warnings", "traceback", "inspect", "copy", "enum",
        }
        unknown = [m.split(".")[0] for m in imports if m.split(".")[0] not in stdlib]
        if unknown:
            return True, f"py_compile passed (unverified imports: {', '.join(set(unknown))} — confirm installed)"
    except Exception:
        pass

    return True, "py_compile passed"


def check_plist(file_path: str) -> tuple[bool, str]:
    result = subprocess.run(
        ["plutil", "-lint", file_path],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return False, result.stderr.strip()

    try:
        content = Path(file_path).read_text(encoding="utf-8")
        missing_keys = [k for k in PLIST_REQUIRED_KEYS if f"<key>{k}</key>" not in content]
        if missing_keys:
            return False, f"plutil passed but missing required keys: {', '.join(missing_keys)}"
        weekday_match = re.search(r"<key>Weekday</key>\s*<integer>(\d+)</integer>", content)
        if weekday_match:
            weekday = int(weekday_match.group(1))
            if weekday < 0 or weekday > 7:
                return False, f"Invalid Weekday value {weekday} (must be 0-7)"
        if "<key>ProgramArguments</key>" in content:
            args_match = re.search(
                r"<key>ProgramArguments</key>\s*<array>(.*?)</array>",
                content, re.DOTALL
            )
            if args_match:
                args_block = args_match.group(1)
                strings = re.findall(r"<string>(.*?)</string>", args_block)
                if len(strings) < 1:
                    return False, "ProgramArguments array is empty"
    except Exception as e:
        return False, f"plist key check error: {e}"

    return True, "plutil -lint passed + required keys present"


def check_json(file_path: str) -> tuple[bool, str]:
    try:
        content = Path(file_path).read_text(encoding="utf-8")
        json.loads(content)
        return True, "JSON parse passed"
    except json.JSONDecodeError as e:
        return False, f"JSON parse error: {e}"


def parse_frontmatter(content: str) -> dict | None:
    if not content.startswith("---"):
        return None
    end = content.find("\n---", 3)
    if end == -1:
        return None
    block = content[3:end].strip()
    result = {}
    for line in block.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip()
    return result


def check_agent_md(file_path: str) -> tuple[bool, str]:
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Could not read file: {e}"

    fm = parse_frontmatter(content)
    if fm is None:
        return False, "Missing or malformed frontmatter (must start with ---)"

    fields_to_check = [f for f in AGENT_REQUIRED_FIELDS if f != "tools"]
    missing = [f for f in fields_to_check if f not in fm or not fm[f]]
    if "tools:" not in content:
        missing.append("tools")
    if missing:
        return False, f"Agent frontmatter missing required fields: {', '.join(missing)}"

    return True, f"agent frontmatter valid (name={fm.get('name', '?')})"


def check_memory_md(file_path: str) -> tuple[bool, str]:
    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        return False, f"Could not read file: {e}"

    fm = parse_frontmatter(content)
    if fm is None:
        return False, "Missing or malformed frontmatter (must start with ---)"

    missing = [f for f in MEMORY_REQUIRED_FIELDS if f not in fm or not fm[f]]
    if missing:
        return False, f"Memory file missing required frontmatter fields: {', '.join(missing)}"

    last_updated = fm.get("last_updated", "")
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", last_updated):
        return False, f"last_updated '{last_updated}' is not a valid YYYY-MM-DD date"

    return True, f"memory frontmatter valid (last_updated={last_updated})"


def route(file_path: str) -> tuple[callable, str] | tuple[None, None]:
    ext = Path(file_path).suffix.lower()

    if ext == ".sh":
        return check_bash, "sh"
    if ext == ".py":
        return check_python, "py"
    if ext == ".plist":
        return check_plist, "plist"
    if ext == ".json":
        return check_json, "json"
    if ext == ".md":
        for marker in AGENT_PATH_MARKERS:
            if marker in file_path:
                return check_agent_md, "agent-md"
        for marker in MEMORY_PATH_MARKERS:
            if marker in file_path:
                return check_memory_md, "memory-md"

    return None, None


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
    except Exception:
        data = {}

    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")

    if not file_path:
        sys.exit(0)

    if should_skip(file_path):
        sys.exit(0)

    checker, file_type = route(file_path)
    if checker is None:
        sys.exit(0)

    passed, detail = checker(file_path)
    short_path = file_path.replace(os.path.expanduser("~"), "~")

    if passed:
        output = {"hookSpecificOutput": f"infra-verify [{file_type}]: {short_path} — {detail}"}
        sys.stdout.write(json.dumps(output))
        sys.exit(0)
    else:
        output = {
            "hookSpecificOutput": (
                f"infra-verify FAILED [{file_type}]: {short_path}\n"
                f"Error: {detail}\n"
                f"Fix before proceeding — do not commit this file."
            )
        }
        sys.stdout.write(json.dumps(output))
        sys.exit(2)


if __name__ == "__main__":
    main()
