---
description: "Record the result of a task, application, experiment, or project milestone. Updates tracking state and archives materials."
argument-hint: "[item name or leave blank to list open items]"
---

# /outcome — Record Results

You are recording what happened to a tracked item: progress updates and final resolutions. The data lands in two places:

- The tracking file (status column for dedup and future reference)
- The per-item archive (posted content, submitted drafts, outcome notes)

Follow these steps in order.

---

## Step 0: Parse Input

`$ARGUMENTS` may contain:
- Nothing → list open items and ask which to update
- An item name → target that item
- `followup` → enter the follow-up branch for quiet open items

---

## Step 1: Load State and Identify the Item

1. Read the tracking file. If missing, create it with the standard header for your domain.
2. With an argument: match rows case-insensitively on item name. One match → proceed. Several → list and ask. None → collect details from user and add a row.
3. Without an argument: list all rows whose status is not final as a numbered table and ask which to update.
4. Derive the archive folder: `[archive-dir]/[item-name]/` — lowercase, underscores for spaces.

---

## Step 2: Collect What Happened

Ask the user what happened, then classify:

**Progress updates** (item still open):
- A stage reached or completed
- A response received
- A milestone hit (not yet final)

**Resolutions** (item closed):
- `completed` — successful completion
- `declined` — explicitly turned down
- `rejected` — external rejection
- `no_response` — no reply after reasonable time
- `paused` — deliberately paused, not abandoned

Also collect without interrogating:
- Dates for stages reached
- Any feedback received, verbatim where remembered
- What to do differently next time

---

## Step 3: Archive Materials

Create or update `[archive-dir]/[item-name]/`. All content here is tracked per-item.

1. Copy (never move) any submitted/created files to the archive if not already there.
2. Write or update `outcome.md`:

```markdown
# Outcome: [Item Name]

**Status:** in_progress | completed | declined | rejected | no_response | paused

**Date resolved:** YYYY-MM-DD   <- only when resolved; omit while in_progress

## Stages reached
- [x] [Stage 1] (YYYY-MM-DD)
- [ ] [Stage 2]

## Notes
<feedback, learnings, signals about what worked — appended per update with a date, never overwritten>
```

Update rules: tick stage checkboxes as they are reached, append dated entries to Notes, change Status only on resolution. Re-running `/outcome` on the same item appends new information, never duplicates history.

---

## Step 4: Update the Tracker

Update the matched row's `status` column and append a short dated note. Never restructure the tracking file, reorder rows, or touch other rows.

---

## Step 5: Calibration Handoff

If 3 or more items are resolved (or 2+ share a pattern), suggest:
> "You now have [N] resolved items on record. Consider reviewing patterns to calibrate your scoring framework."

---

## Step 6: Confirm

Summarize what was recorded:

> **Outcome recorded for [Item Name].**
>
> - `[archive-dir]/[item-name]/outcome.md` — status: [status], [what changed]
> - Tracker: status → [new status]

---

## Important Rules

1. **Write data, don't interpret it.** The archive and tracker are the outputs; pattern analysis belongs to a separate review.
2. **The archived version is the submitted version.** Existing files in the archive are never overwritten.
3. **Never fabricate.** Missing data gets an explicit "unavailable" stub.
4. **Idempotent updates.** Re-running on the same item appends new stages and notes; never duplicates.
