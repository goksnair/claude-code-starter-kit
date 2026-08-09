---
description: "Quick capture — routes any note, idea, or update to the right memory file automatically. Usage: /capture [note]"
argument-hint: "[note or idea to capture]"
---

# /capture [note] — Quick Capture Router

## Step 1 — Classify the input

Read the note and classify it into one of these categories:

| Category | Route to | Examples |
|----------|---------|---------|
| External resource (URL, repo, article, tool) | `knowledge/RESOURCE_INBOX.md` | Links, tools to evaluate, articles to read |
| Project decision / deadline | `.claude/memory/STATUS.md` | "Meeting rescheduled to [date]", "Decision locked on X" |
| Product or feature idea | `knowledge/ideas/idea-vault.md` | "Idea: X for Y problem", "Saw a gap in Z" |
| Research finding | `knowledge/research/` | Market data, competitive intel, discovery notes |
| Goal update | `.claude/memory/goals.md` | "Revised target to X", "Milestone hit" |
| Personal preference | `.claude/memory/preferences.md` | "Realized I work best doing X" |

Adapt the routing table to your project's actual knowledge directory structure.

## Step 2 — Append to the target file

**If routing to `knowledge/RESOURCE_INBOX.md`:**

Add a new row to the Inbox table with:

- Date: today's date
- Type: `url` / `repo` / `article` / `tool` (infer from the resource)
- Resource: the URL or description
- Domain: infer from context
- Intent: one-line description of what this might be for
- Status: `inbox`

**All other destinations:**

Read the target file, append the capture at the bottom with a date stamp:

```text
<!-- Captured [YYYY-MM-DD] -->
[content]
```

## Step 3 — Confirm

Print: `✓ Captured to [file path]`

If classification is ambiguous, print two options and ask which one before writing.
