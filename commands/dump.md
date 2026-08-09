---
description: "Freeform capture — dump anything and I'll route it to the right memory or knowledge file."
---

Process the following freeform dump. For each distinct piece:

1. Classify: decision, financial update, product insight, project update, person/contact, or general note.

2. Route using the Content Routing table in CLAUDE.md:
   - Career decisions, deadlines → .claude/memory/career.md
   - Goals, milestones → .claude/memory/goals.md
   - Financial numbers → vault (never git) — confirm with user before writing
   - People, contacts → vault (never git) — confirm with user before writing
   - Project context → knowledge/projects/[name].md
   - Product insights → knowledge/indie/ or knowledge/[domain]/
   - Open items, blockers → .claude/status/SESSION_HANDOFF.md

3. Check if the target file already covers this. Prefer appending to existing over creating new.

4. For financial or people data: confirm with user before writing — these go to vault, not repo.

After processing, summarize:
- What was captured and where
- What needed vault (not repo) — why
- Anything you couldn't classify (ask first)

Content to process:
$ARGUMENTS
