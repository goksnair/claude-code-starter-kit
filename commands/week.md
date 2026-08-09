---
description: "Weekly review — cross-session synthesis, goal alignment check, and next-week priorities."
---

Run the weekly synthesis. This is ANALYSIS across sessions, not a single session wrap-up.

## Workflow

### 1. Gather Week's Activity

Read simultaneously:
- `git log --since="7 days ago" --oneline` in the project repo
- All memory + knowledge files modified in the past 7 days
- `.claude/scratch/AGENT_STATE.json` → `persona_log` for this week's context switches
- `.claude/status/SESSION_HANDOFF.md` → what moved forward this week

### 2. Goal Alignment
Read `.claude/memory/goals.md` and compare actual activity to stated focus:
- Which milestones got attention this week?
- Silent goals: anything in STATUS.md with zero activity this week?
- Emerging drift: work patterns not mapping to any stated goal?

### 3. Cross-Week Patterns
Look across the week for:
- Recurring topics in multiple sessions
- Decisions that evolved across multiple conversations
- Anything that should be in STATUS.md but isn't

### 4. Forward Look
- Upcoming deadlines from STATUS.md
- Which area needs the most attention next week?
- Any blocking issues to resolve before Monday?

### 5. Present Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEK IN REVIEW — [week of YYYY-MM-DD]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📦 WHAT MOVED FORWARD
  [2-3 bullets: biggest things shipped or decided this week]

🎯 GOAL ALIGNMENT
  [honest 1-sentence read on whether this week served the stated goals]

⚠️  PATTERNS & GAPS
  [anything NOT happening that should be]
  [decisions drifting with no action]

📋 NEXT WEEK TOP 3
  1. [by deadline urgency]
  2. [by deadline urgency]
  3. [by deadline urgency]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Uncaptured check**: scan conversation for decisions/wins not yet written to memory or knowledge files. Offer to capture them.

Output is transient by default — don't create a file unless asked.
Keep tone direct. Surface what's NOT happening, not just what is.
