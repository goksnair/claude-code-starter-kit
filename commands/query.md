---
description: "Answer a question from the project wiki or memory. Routes to the right source."
---

Answer the following question. Route to the correct source.

## Step 1 — Hybrid search first

Run hybrid search before manual routing (if session-index.py is present):

```bash
{{PROJECT_PATH}}/scripts/session-index.py search "$ARGUMENTS" --top 5
```

If this returns results, use the top matches to locate the right file or section. Read the matched file at the indicated heading, then answer.

If the script is absent or returns no results, fall through to manual routing below.

## Step 2 — Manual routing fallback

Route to the appropriate source based on what the question is about:

- Project decisions, deadlines, active status → `.claude/memory/STATUS.md`
- Goals, milestones, targets → `.claude/memory/goals.md`
- Domain knowledge, research → `knowledge/` subdirectory matching the topic
- Project architecture, system design → `knowledge/` or top-level docs

Adapt this routing map to your project's actual knowledge structure.

## Step 3 — Answer

1. Read the matched source(s)
2. Answer — cite which files you read and which headings
3. If source is a stub: say so, suggest `/capture` or manual update with a specific source
4. If answer required new synthesis: offer to write it as a new knowledge file or memory update

Question:
$ARGUMENTS
