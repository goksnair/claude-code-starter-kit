---
description: "Lock a confirmed fact, decision, or deadline into the correct memory file. Usage: /lock [confirmed fact]"
argument-hint: "[fact — e.g. 'Sprint 2 scope locked, delivery due Sep 15']"
---

# /lock [fact] — Confirmed Knowledge → Persistent Memory

Use when a fact, figure, decision, or deadline is confirmed in conversation and must survive session compaction.

## Step 1 — Classify and route

| Fact type | Target file |
|-----------|-------------|
| Career decision, active deadline, path fork | `.claude/memory/career.md` |
| Goal milestone, target update | `.claude/memory/goals.md` |
| Work style preference, tool preference | `.claude/memory/preferences.md` |
| Financial number, income event | vault (confirm with user before writing) |
| Contact, person, relationship | vault (confirm with user before writing) |
| Project context, decision | `knowledge/projects/[name].md` |
| Product idea, revenue event | `knowledge/indie/` or `knowledge/[domain]/` |
| External resource ID — Sheet, Script, Notion, portal URL, Supabase, Vercel | `~/.claude/projects/[project-dir]/memory/reference_[name].md` |
| Open item, blocker, pending decision | `.claude/status/SESSION_HANDOFF.md` OPEN ITEMS table |

**Vault files (finances, network)**: Always confirm with user before writing. Print: `⚠️ Vault write — confirm?` and wait.

If ambiguous between two targets: print both options and wait for user to choose.

## Step 2 — Write to target file

Read the target file (targeted read — use offset/limit or Grep if large).

Find the most relevant section. Append or update in place:
- Tables: add/update the relevant row
- Prose sections: append a bullet with `*(locked [YYYY-MM-DD])*`
- OPEN ITEMS in SESSION_HANDOFF: add row with priority + due date if known

**Do not rewrite surrounding content** — targeted edit only.

## Step 3 — Confirm

Print:
```
✓ Locked: [fact]
→ [target file] § [section]
```

Then continue the conversation without breaking flow.
