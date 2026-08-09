---
description: "Session-start diagnostic — runs 7 health checks, prints GREEN/YELLOW/RED report"
argument-hint: ""
---

# /health

Run the system-health agent to check project state before domain work.

Dispatch the system-health agent via Task():

```
Task(
  subagent_type="general-purpose",
  description="Run system health check",
  prompt="""
Read the full agent instructions at: .claude/agents/system-health.md
Then read: .claude/agents/AGENT_SHARED_CONTEXT.md

Run all 7 health checks (SH-01 through SH-07) and produce HEALTH_REPORT.md.

Output to: .claude/scratch/HEALTH_REPORT.md
Working directory: [PROJECT_PATH]
AGENT_STATE: .claude/scratch/AGENT_STATE.json
"""
)
```

Wait for Task to complete, then print the HEALTH_REPORT.md summary.
