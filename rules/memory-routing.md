# Memory Routing Rules

## Content Routing — Required Destinations

| Content type | MUST go to |
|---|---|
| Project decisions, deadlines, active status | `.claude/memory/STATUS.md` |
| Goals, milestones, targets | `.claude/memory/goals.md` |
| Financial numbers, income events | vault (never git) — confirm with user |
| Contacts, people, relationships | vault (never git) — confirm with user |
| User preferences, work style | `.claude/memory/preferences.md` |
| Project context — decisions, status, key people | `knowledge/projects/[name].md` |
| Product ideas, MVP logs | `knowledge/indie/` or `knowledge/[domain]/` |
| Research findings, market data | `knowledge/research/` or `knowledge/wiki/` |
| External resource IDs (Sheet, Notion, Vercel, Supabase) | `~/.claude/projects/[dir]/memory/reference_[name].md` |
| Open items, blockers, pending decisions | `.claude/status/SESSION_HANDOFF.md` OPEN ITEMS |

**RULE**: No decision, deadline, or actionable insight lives in conversation only.

## Vault vs. Repo — Hard Boundary

**Vault files** (outside the project repo) — NEVER committed to git:
- `finances.md` or equivalent — all financial numbers, income, portfolio
- `network.md` or equivalent — contacts, people, relationships

**Before writing any financial or contact data**: confirm with user. Print `⚠️ Vault write — confirm?` and wait.

## Project Files — Financial Content Strictly Banned

`knowledge/projects/[name].md` files contain ONLY strategy, context, decisions, and deliverables. Never financial amounts inline.

In project files, replace amounts with: `see vault finances section ([ProjectName])`

## External Resource Capture — Immediate Write

**RULE**: When any tool confirms creation or retrieval of an external resource (spreadsheet, doc, script, deployment URL, database), write the ID or URL to a reference memory file **immediately** — do NOT defer to session end.

Use `/lock [resource name] [ID or URL]` — this routes to the reference file automatically.

**Why**: External IDs buried in SESSION_HANDOFF are destroyed by compaction within 2–3 sessions.

## Capture Protocol

- For single items: `/capture [note]` — auto-routes to the right file
- For bulk dumps: `/dump [text]` — classifies and routes all pieces
- For ambiguous routing: ask before writing — always ask rather than guess wrong
- Prefer appending to existing files over creating new ones

## Scratch File Lifecycle

`.claude/scratch/` files are intra-session working memory only — NEVER committed:
- `AGENT_STATE.json` — session state managed by hooks, do not edit manually
- `WORKORDER.json` — created and deleted within each /work call, never persists
- `SCRATCHPAD.md` — intra-session notes, clear at end
