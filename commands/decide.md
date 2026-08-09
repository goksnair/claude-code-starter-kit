---
description: "High-stakes decision simulation. Runs a multi-perspective analysis for decisions that matter. Use when you need more than one viewpoint before committing."
argument-hint: "[decision statement]"
---

# /decide — High-Stakes Decision Simulation

Runs a multi-perspective simulation for decisions that matter.
Use when you need more than your own perspective before committing.

**Trigger**: any irreversible decision — shutting something down, major pivot, accepting a significant commitment.

---

## Step 1 — Collect the decision

Ask:

> "What's the decision you're facing? Give me:
> 1. The options (A vs B, or list them)
> 2. What can't be undone once you choose
> 3. When you need to decide by
> 4. What good looks like in 12 months
> 5. What failure looks like in 12 months"

If all 5 are provided upfront: skip to Step 2.

---

## Step 2 — Load context

Read simultaneously:
- `.claude/memory/STATUS.md` — current decisions, active constraints
- `.claude/memory/goals.md` — project goals and milestones
- Any relevant domain knowledge file

---

## Step 3 — Run simulation

Run all 5 perspectives in sequence:

1. **Operator** — execution reality: what does this actually require to execute? What will break?
2. **Financial Realist** — resource impact: what does this cost? What does it protect?
3. **Contrarian** — devil's advocate: what's the strongest case against the leading option?
4. **Future Self** — 12-month view: which choice minimizes regret? Which compounds?
5. **Trusted Advisor** — objective outsider: what would a smart friend who isn't emotionally involved say?

Each perspective gets 3-5 sentences. Don't summarize — actually argue the position.

---

## Step 4 — Synthesize and recommend

State explicitly:
- Where 3+ perspectives agreed (the signal)
- Where they conflicted (the risk to investigate further)
- A specific recommendation — not "it depends"
- Confidence level: low / medium / high
- Recovery plan if the recommendation is wrong

---

## Step 5 — Decision log

Offer to log the decision:
> "Want me to log this decision and your choice to STATUS.md or the relevant knowledge file? It'll be useful context when you review it in 3 months."

If yes: append to `.claude/memory/STATUS.md` active decisions section or the relevant knowledge file.
