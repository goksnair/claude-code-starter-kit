---
description: Given a situation description, recommend the right agent + command sequence
argument-hint: [situation description]
---

# /route — Situation-to-Capability Router

Maps any user situation to the correct agent and command sequence. Use when unsure which agent handles a task.

**Usage**: `/route [describe your situation]`

---

## Step 1 — Parse argument

If no argument provided, ask:
> "Describe your situation in one sentence — what are you trying to do or decide?"

Use the response as the situation description.

## Step 2 — Dispatch skill-router agent

```
Task(
  subagent_type="skill-router",
  description="Route situation to correct agent/command",
  prompt="""
Situation: [situation description verbatim]

Route this to the correct (agent, command) tuple.
Read the agents/ directory and CONTEXT.md before classifying.
Output the JSON routing block only.
"""
)
```

## Step 3 — Print result

Parse the JSON output and print in human-readable form:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ROUTE: [situation_summary]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Domain:  [domain]
Agent:   [agent]

Run this:
  [command_sequence line 1]

Why: [rationale]

Alternatives:
  [alt 1: agent — when]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Copy-paste the "Run this" block to activate. If the routing looks wrong, describe why and I'll re-route.
