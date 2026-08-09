# Memory Routing Rules
<!-- Enforced by: memory-validator.py (PreToolUse:Write/Edit) -->
<!-- Behavioral-only rules are marked [behavioral] -->

## Memory Directory — Single Source

All project memory lives in `.claude/memory/`. These files are committed to the repo and form the persistent knowledge layer:

- `.claude/memory/STATUS.md` — current project status, active decisions, deadlines
- `.claude/memory/goals.md` — project goals and milestones
- `.claude/memory/preferences.md` — working preferences, style decisions

**RULE**: No decision, deadline, or actionable insight lives in conversation only. Every session produces at least one write to a memory or knowledge file, or nothing of consequence happened.

## Content Routing — Required Destinations

| Content type | MUST go to |
|---|---|
| Active decisions, deadlines, project status | `.claude/memory/STATUS.md` |
| Goals, milestones, targets | `.claude/memory/goals.md` |
| Working preferences, style decisions | `.claude/memory/preferences.md` |
| Domain knowledge, research findings | `knowledge/[domain]/` |
| External resource IDs, URLs, tool references | `knowledge/RESOURCE_INBOX.md` or a dedicated reference file |

Adapt this routing table to your project's actual directory structure.

## Knowledge Files — Sensitive Data Strictly Controlled

**RULE**: `knowledge/` files contain ONLY strategy, context, decisions, and deliverables. Never credentials, never personal financial data, never private contact details.

If sensitive data must be referenced: note its location in an external vault or secrets manager — do not inline it.

**Hook**: `memory-validator.py` scans Write/Edit content for sensitive patterns and warns.

## External Resource Capture — Immediate Write [behavioral]

**RULE**: When any MCP tool confirms creation or retrieval of an external resource, write the ID or URL to a reference file **immediately** — do NOT defer to session end.

This includes: `spreadsheetId`, `fileId`, `scriptId`, `pageId`, `projectId`, portal URLs, deployment URLs.

Use `/capture [resource name] [ID or URL]` to route correctly.

**Why**: External IDs buried in SESSION_HANDOFF are lost at compaction. Reference files survive indefinitely.

## Capture Protocol [behavioral]

- For single items: `/capture [note]` — auto-routes to the right file
- For bulk captures: classify each item and route individually
- Prefer appending to existing files over creating new ones

## Scratch File Lifecycle [behavioral]

`.claude/scratch/` files are intra-session working memory only — NEVER committed:
- `SCRATCHPAD.md` — intra-session working notes, cleared at session end
- `AGENT_STATE.json` — session state managed by hooks, do not edit manually

## Memory Files Must Be Current Before Acting [behavioral]

Never make a recommendation on a domain without verifying the relevant memory file first:
- Any "what should I do" → read `.claude/memory/STATUS.md` Active Decisions first
- Any goal-related decision → read `.claude/memory/goals.md` first
- Any domain work → read the relevant `knowledge/` file first
