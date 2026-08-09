---
name: coordinator
description: "{{PROJECT_NAME}} orchestration protocol reference. The /work command reads this as a reference document and executes coordinator logic inline in the main session. Do NOT invoke via Task() — nested Task calls are not permitted by Claude Code."
model: inherit
color: cyan
---

**This file is a protocol reference, not a dispatchable agent.** `/work` reads this file for its orchestration rules and executes them inline. Do NOT invoke via `Task(subagent_type='coordinator', ...)`.

---

## Agent Dispatch Map

Customize this table for your project specialists:

| Agent name | subagent_type | Domain keywords | When to use |
|------------|--------------|----------------|-------------|
| strategy-consultant | general-purpose | GTM, roadmap, positioning, market entry | Strategic output |
| operations-analyst | general-purpose | SOP, process, onboarding, workflow | Operational output |
| marketing-specialist | general-purpose | positioning, messaging, content, brand, copy | Marketing output |
| finance-analyst | general-purpose | pricing, cash flow, unit economics, model | Financial output |
| research-analyst | general-purpose | market research, competitive, discovery, trends | Research output |
| tech-advisor | general-purpose | product roadmap, architecture, tech stack, build vs buy | Technical output |
| prompt-engineer | prompt-engineer | [always dispatched by /work — not keyword-routed] | Directive structuring |

**Banned as primary_agent**: self, inline, direct, coordinator, general-purpose

---

## Context Health Check

Read `.claude/scratch/AGENT_STATE.json`. Print:
```
Turn [N] | Context: [GREEN (<=9) / YELLOW (10-14) / ORANGE (15-19) / RED (20+)]
```

If ORANGE or RED: `Context heavy. Consider /compact before this task.`

If `active_task.status == "in_progress"`: STOP. Print orphan warning and instruct human to reset to `idle`.

---

## GATE-2 Structure

Every task returns:
```
WORK COMPLETE — GATE-2 REVIEW

WorkOrder: [task_id] -> [agent] | [framework] | [mode] | complexity=[simple|deep]

## DONE
[3-5 bullets]

## VERIFIED
[file proof / git sha / runtime check — no vague "task complete"]

## SELF-ADVERSARIAL CHECK
- Unhandled edge cases: [what]
- Unverified assumptions: [what]
- 30-day fragility: [what breaks when X changes]

## UNRESOLVED
[gaps with named follow-up action]

## COMMIT MANIFEST
Files: [list]
Message: [suggested]

y = commit | n = skip
```
