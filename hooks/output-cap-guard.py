#!/usr/bin/env python3
import json
import re
import sys

WORD_LIMIT = 500
FILE_PATH_PATTERNS = [
    r"\.md\b",
    r"\.json\b",
    r"\.txt\b",
    r"\.py\b",
    r"written to",
    r"saved to",
    r"output at",
    r"see file",
    r"full (?:report|output|detail)",
    r"\.claude/scratch/",
]

FILE_RE = re.compile("|".join(FILE_PATH_PATTERNS), re.IGNORECASE)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    if tool_name not in ("Task", "Agent"):
        sys.exit(0)

    response = payload.get("tool_response", {})
    content = ""
    if isinstance(response, dict):
        content = response.get("content", "") or ""
    elif isinstance(response, str):
        content = response

    if not content:
        sys.exit(0)

    word_count = len(content.split())
    if word_count <= WORD_LIMIT:
        sys.exit(0)

    has_file_ref = bool(FILE_RE.search(content))
    if has_file_ref:
        sys.exit(0)

    warning = {
        "additionalContext": (
            f"OUTPUT CAP EXCEEDED: Task response was {word_count} words "
            f"(limit: {WORD_LIMIT}). No output file path detected. "
            "Coordinator: for the next Task() dispatch, enforce the 500-word cap "
            "by requiring the specialist to write verbose output to a .md file "
            "and return only a 5-line summary. See execution rules for output discipline."
        )
    }
    print(json.dumps(warning))
    sys.exit(0)


if __name__ == "__main__":
    main()
