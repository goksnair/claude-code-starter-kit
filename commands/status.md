---
description: "Full project status dashboard — decisions, deadlines, and open items at a glance."
argument-hint: "(no arguments)"
---

# /status — Project Dashboard

Run any time to re-orient without opening each file individually.
Data comes from live files — not memory.

---

## Step 1 — Load data sources (parallel reads)

Read simultaneously:
1. `.claude/memory/STATUS.md` — active decisions + deadlines
2. `.claude/memory/goals.md` — milestone status
3. `.claude/status/SESSION_HANDOFF.md` — OPEN ITEMS + IMMEDIATE NEXT TASK

If a file is unreadable, show "⚠️ unreadable" for that section — do not error.

---

## Step 2 — Compute deadlines

For each active decision or deadline:
- Calculate days remaining (negative = past due → flag 🔴 OVERDUE)
- Flag as: 🔴 (≤7 days), 🟡 (≤21 days), 🟢 (>21 days)

---

## Step 3 — Print status dashboard

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STATUS DASHBOARD — [YYYY-MM-DD]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🗂  OPEN DECISIONS
  [emoji] [N days] — [decision label] — [status]
  ...

📦 MILESTONE PROGRESS
  [milestone] — [status] — [next action]
  ...

📋 TOP OPEN ITEMS
  [item] — [priority]
  ...

⚡ TOP ACTION RIGHT NOW
  [Single most urgent thing based on closest deadline or blocking issue]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Rules for this command

- Compute everything live from files — never from memory or assumptions
- Staleness: ✅ = 0–2 days, 🟡 = 3–6 days, 🔴 = 7+ days
- Keep the output tight — no preamble, no commentary beyond what's in the template
- Offer next step after printing: "Want to dive into any of these?"
