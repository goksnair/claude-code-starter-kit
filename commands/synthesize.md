---
description: "Cross-domain synthesis — surfaces conflicts, leverage points, and decisions that span multiple work streams. Run weekly or before major decisions."
---

# /synthesize — Cross-Domain Weekly Synthesis

Chief-of-staff view across all active work streams. Surfaces conflicts, leverage points,
and decisions that span domains. Run weekly or before major decisions.

---

## Step 1 — Load all memory files

Read simultaneously:
- `.claude/memory/STATUS.md` — active decisions, deadlines, blockers
- `.claude/memory/goals.md` — targets and milestones
- Relevant domain knowledge files

## Step 2 — Cross-stream conflict scan

For each pair of active work streams, check:
- Are they competing for the same time block or resource?
- Is one stream's decision blocking another?
- Is there a resource (time, money, attention) being pulled in two directions?

Flag any conflicts explicitly.

## Step 3 — Leverage scan

Look for actions that advance 2+ goals simultaneously:
- Examples: closing one task unblocks another, a decision in stream A resolves stream B's open question
- Surface the top 2 leverage moves this week.

## Step 4 — Decision dashboard update

Print all active decisions with current status and updated countdowns:

```
DECISION DASHBOARD — [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━
[Decision 1]  | [X] days | [status update]
[Decision 2]  | [X] days | [status update]
[Decision 3]  | [X] days | [status update]
━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Step 5 — Weekly output

Print synthesis block:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEKLY SYNTHESIS — [YYYY-MM-DD]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CROSS-STREAM CONFLICTS
  [list any, or "none detected"]

TOP LEVERAGE MOVES THIS WEEK
  1. [action] → advances [goal A] + [goal B]
  2. [action] → advances [goal A] + [goal B]

DECISION DASHBOARD
  [from Step 4]

NEXT WEEK TOP 3
  1. [most important action]
  2.
  3.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Save to: `knowledge/sessions/weekly-[YYYY-WW].md`
