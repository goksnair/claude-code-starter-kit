---
description: "Session end — COMMIT PREVIEW gate, updates SESSION_HANDOFF + CURRENT_STATE, commits"
argument-hint: ""
---

# /end

Session end sequence. Run this before closing Claude Code every session.

## Step 1 — Gather what happened this session (parallel reads)

Read simultaneously:
1. `.claude/scratch/SCRATCHPAD.md` (if exists — summarise findings)
2. `.claude/status/SESSION_HANDOFF.md` (current version to update)
3. `.claude/status/MILESTONE_REGISTRY.json`

Run simultaneously:
```bash
git diff --stat HEAD
git log --oneline -5
git status --short
```

## Step 1.5 — Scratch Audit (migration receipt before any commit)

Run:
```bash
ls .claude/scratch/*.md 2>/dev/null | grep -v SCRATCHPAD.md
```

**If no files found**: print `Scratch clean — no migration required.` and continue to Step 2.

**If files found**: print the following table and wait for the user to fill it in before proceeding:

```
SCRATCH AUDIT — confirm migration before purge

For each file below, state one of:
  MIGRATE -> [canonical file] [section]   (findings need to be absorbed first)
  DONE    -> [canonical file] [section]   (already migrated — safe to delete)
  KEEP    -> reason                       (action artifact, not yet published)
  PURGE   -> reason                       (no knowledge value — discard)

Files:
[list each .md file found, one per line, with a blank status column]
```

**Rules for this step:**
- NEVER delete a file marked MIGRATE until the migration edit is complete and confirmed
- DONE and PURGE files: delete after this step, before Step 6 COMMIT PREVIEW
- KEEP files: leave in scratch; they will appear again at next session's audit
- If unsure about a file's content: Read it first, classify, then decide

After user responds: execute migrations (MIGRATE items), then delete DONE + PURGE files. Update the stage list in Step 6 to include any files modified during migration.

## Step 2 — Ask for the next session's task

Print this question and wait for the user's answer:

```
IMMEDIATE NEXT TASK for next session:
What should a fresh Claude session do first?
(Be specific — file name, target value, expected output)
```

## Step 3 — Update SESSION_HANDOFF.md

1. Update `**Last updated**` date to today
2. Add a new `## COMPLETED THIS SESSION ([date])` block near the top
3. Replace `### IMMEDIATE NEXT TASK` with the user's answer from Step 2
4. Update the OPEN ITEMS / blockers list

## Step 4 — Update CURRENT_STATE.md

- Add `### Today ([date])` block at top of `## What Was Just Completed`
- Update `**Last Updated**` at the top

## Step 4b — Knowledge Capture Checkpoint (MANDATORY before closing)

**Pass 1 — live conversation scan**: Scan the current (uncompacted) conversation for any confirmed facts not yet written to the right file:
- Confirmed figures, prices, rates, deadlines stated verbally
- Locked decisions (vendor approved, path chosen, enrollment done)
- Venture updates, client decisions, program intel

For each unwritten fact:
1. Identify the correct file (routing table in CLAUDE.md / memory-routing.md)
2. Write it there immediately using `/lock [fact]`
3. Print: `✓ Captured [fact] → [file]`

**Pass 2 — COMPLETED block scan**: Read the COMPLETED THIS SESSION block just written to SESSION_HANDOFF.md. Look for any confirmed facts (figures, rates, decisions, locked assumptions, timeline dates) mentioned there that do NOT already appear in a wiki or memory file. These are facts that survived to the handoff but were never propagated to the queryable knowledge layer.

For each such fact:
1. Identify the correct file (routing table in CLAUDE.md / memory-routing.md)
2. Write it there immediately using `/lock [fact]`
3. Print: `✓ Backfilled [fact] → [file] (from COMPLETED block)`

If nothing missed in either pass: print `✓ Knowledge capture: all session facts written`

**Why**: Pass 1 catches facts from the live context window. Pass 2 catches facts from any compaction that occurred mid-session — those are already lost from conversation but may still be named in the COMPLETED block. Together they close the gap.

## Step 4c — Persona staleness check

Scan the COMPLETED THIS SESSION block just written and the conversation for any events that would make a persona file's CONTEXT section factually wrong:

- A venture closed, concluded, or changed status → `founder.md`
- A client project ended or changed → `growth-consultant.md`
- A checkpoint date passed (May 15, June 30, etc.) → `indie-hacker.md` / `indie-developer.md`
- A new venture or stream added → `founder.md`
- A track allocation decision changed → any persona

For each stale item found:
1. Edit the specific line(s) in `.claude/personas/[name].md` — surgical changes only
2. Print: `✓ Persona updated: [persona] — [what changed]`

If no persona is stale: print `✓ Personas: all CONTEXT sections current`

**Rule**: Only update CONTEXT and CONSTRAINTS sections — never rewrite ROLE, TOOLS, or HANDOFF unless explicitly asked.

## Step 5 — Update MILESTONE_REGISTRY.json (conditional)

If any knowledge files or deliverables changed today: update relevant entry's `version`, `date`, `notes`, and `_metadata.lastUpdated`.

## Step 6 — COMMIT PREVIEW

```
COMMIT PREVIEW

Files to stage:
  .claude/status/SESSION_HANDOFF.md
  .claude/status/CURRENT_STATE.md
  .claude/status/MILESTONE_REGISTRY.json
  [any new/modified research or knowledge files]

Commit message:
  SESSION HANDOFF — read .claude/status/SESSION_HANDOFF.md to continue this work

y = commit | n = skip | add [file] = stage additional file
```

Wait for user response before committing.

## Step 7 — On approval (y)

```bash
git add \
  .claude/status/SESSION_HANDOFF.md \
  .claude/status/CURRENT_STATE.md \
  .claude/status/MILESTONE_REGISTRY.json

git commit -m "SESSION HANDOFF — read .claude/status/SESSION_HANDOFF.md to continue this work

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

Clean scratch (DONE + PURGE files from Step 1.5 audit, plus session temporaries):
```bash
rm -f .claude/scratch/SCRATCHPAD.md
rm -f .claude/scratch/PE_OUTPUT.md
# Also delete any files confirmed DONE or PURGE in Step 1.5 audit
# (list them explicitly — never use rm *.md glob)
```

**Never delete KEEP files. Never delete AGENT_STATE.json.**

## Step 8 — Print session close confirmation

```
SESSION CLOSED — [date]

Committed: [sha]
Updated:   SESSION_HANDOFF | CURRENT_STATE | MILESTONE_REGISTRY [or skipped]
Scratch:   SCRATCHPAD deleted | AGENT_STATE preserved

NEXT SESSION — start with:
  /start        -> loads context + shows IMMEDIATE NEXT TASK
  /work [task]  -> begins multi-agent orchestration
```
