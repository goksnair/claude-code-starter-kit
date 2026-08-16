#!/usr/bin/env python3
import json
import re
import sys

RESEARCH_SIGNALS = [
    "research", "investigate", "deep dive", "deep-dive",
    "find all", "compare", "scan", "analyze", "analyse", "map out",
    "survey", "benchmark", "look into", "dig into", "explore",
]

KNOWLEDGE_SIGNALS = [
    "wiki", "graphify", "/query", "what do we know", "what's in",
    "active decisions", "deferred", "knowledge",
    "what decisions", "open items", "system state",
]

EXCLUSIONS = [
    "copy-check", "copy check", "workflow", "parallel", "subagent",
]


def classify(message: str):
    lower = message.lower()
    if len(lower.split()) < 6:
        return None
    for excl in EXCLUSIONS:
        if excl in lower:
            return None
    for signal in KNOWLEDGE_SIGNALS:
        if signal in lower:
            return "knowledge"
    for signal in RESEARCH_SIGNALS:
        if signal in lower:
            return "research"
    return None


def main():
    try:
        hook_input = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    message = hook_input.get("prompt", "")
    kind = classify(message)

    if kind is None:
        sys.exit(0)

    if kind == "knowledge":
        hint = (
            "Knowledge hint: for questions about active decisions, deferred items, "
            "or system state — check STATUS.md and goals.md first before exploring files."
        )
    else:
        hint = "Workflow hint: research signals detected. Consider spawning parallel subagents for independent research tracks."

    result = {
        "hookSpecificOutput": {
            "hookType": "UserPromptSubmit",
            "toolName": "workflow-injector",
            "output": hint,
        }
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()
