---
description: "On-demand topic research across Reddit, X, YouTube, HN, and GitHub. Dispatches the research-agent and synthesizes a structured signal report."
argument-hint: "[topic to research]"
---

# /research [topic] — On-demand Signal Research

Fires the research-agent for a specific topic. Runs a data pipeline across social sources, then synthesizes a structured report: pain points with real quotes, existing tools, gaps, and trending repos.

Not a scheduled loop — fires on demand, takes 2–4 minutes.

## Usage

```text
/research B2B automation tools 2026
/research Claude Code productivity
/research solo founder ops systems
/research MCP server frameworks
```

## Step 1 — Parse Topic

Extract everything after `/research` as the TOPIC string. If no topic provided, print usage and stop.

## Step 2 — Print Start Banner

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESEARCHING: [TOPIC]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sources: Reddit · X · YouTube · HN · GitHub
ETA: 2–4 minutes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 3 — Dispatch Research Agent

```python
Agent(
  subagent_type="research-agent",
  description="Research: [TOPIC]",
  prompt="""
Topic to research: [TOPIC]

Run the last30days research script if available:
  python3 {{PROJECT_PATH}}/.claude/scripts/research.py "[TOPIC]" --days 7 --emit json --save-dir ~/Documents/Research

Parse the JSON output, synthesize the structured report, and return it as your response.
Working directory: {{PROJECT_PATH}}
"""
)
```

Wait for completion and display the full report inline.

## Step 4 — Ask to Save

After displaying the report:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Save qualifying entries to signal-inbox.md? (y/n)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If y: agent extracts qualifying entries and appends to `knowledge/indie/signal-inbox.md` (or your project's equivalent inbox file). Print count of entries saved.
If n: exit cleanly.
