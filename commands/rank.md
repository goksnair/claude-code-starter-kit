---
description: "Triage and rank a list of options (jobs, ideas, tasks, candidates) against a scoring framework. Returns a ranked shortlist with verdicts."
argument-hint: "[list of items to rank, or file path containing the list]"
---

# /rank — Triage and Rank Options

You are batch-scoring a list of options so the user can decide where to spend effort. `/rank` produces **triage scores**, not final evaluations. It scores from available data only — no deep research per item.

Follow these steps in order.

---

## Step 0: Parse Input

`$ARGUMENTS` may contain:
- Nothing → rank all items with status `new` in the default tracking file
- A focus area → rank only items matching the focus
- `--all` → re-rank every item including previously ranked ones
- `--top <N>` → shortlist size (default 5)

---

## Step 1: Load State

1. Read the tracking file for this domain (adapt path to your project structure).
2. Read the scoring framework and candidate profile relevant to this ranking task.
3. Select candidates: entries with status `new` (or all with `--all`), minus any already in a final state.
4. If no candidates remain, say so and stop.
5. State how many items will be ranked before proceeding.

---

## Step 2: Score

Score each item against the framework dimensions. For each:

- Apply the dimension weights defined in your scoring framework
- Identify strengths (2-3 bullets grounded in actual data)
- Identify gaps (1-3 honest bullets)
- Flag any deal-breakers that veto the score

Never score items from incomplete or unavailable data — mark them `unavailable` instead.

---

## Step 3: Aggregate and Rank

1. Compute the overall score using your framework's weights.
2. Map to verdict bands (customize for your domain).
3. Apply any hard vetoes (e.g. location, timeline, missing requirement).
4. Sort by score descending, urgency as tiebreaker.

---

## Step 4: Update State

Update the tracking file in place:
- Ranked items: set status `ranked`, add score and verdict
- Unavailable items: set status `unavailable`

---

## Step 5: Present the Shortlist

```
## Ranking — YYYY-MM-DD

Ranked <N> items (<X> shortlisted, <Y> below threshold, <Z> vetoed/unavailable).

### Shortlist

| # | Score | Verdict | Item | Notes |
|---|-------|---------|------|-------|

### Why these ranked highest
[2-3 strength bullets per shortlisted item, grounded in data]

### Below threshold
[Brief table of lower-scored items with one-line reason]

### Vetoed / Unavailable
[List with reason]
```

Rules:
- Every claim traces to actual data — no invented details
- State explicitly that these are triage scores, and deeper evaluation is needed before acting
- Then ask: "Want to go deeper on any of these?"
