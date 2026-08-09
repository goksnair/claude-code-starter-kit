---
description: "Lightweight session close. Always updates SESSION_HANDOFF and commits. Conditionally updates CURRENT_STATE based on what actually happened. Skips full ceremony."
---

# /checkpoint — Lightweight Session Close

Use this instead of `/end` when the session had no major decisions requiring full ceremony.

**When to use `/checkpoint` vs `/end`**:

| Session type | Command |
|---|---|
| Audit, health check, system verification | `/checkpoint` |
| Research run, signal ingestion, knowledge update | `/checkpoint` |
| Implementation work, system changes | `/checkpoint` |
| Major decision locked, significant status change | `/end` |

---

## Step 0 — Mark session as closing

```python
import json, os
from datetime import datetime, timezone
from pathlib import Path

state_path = Path(os.path.expanduser("{{PROJECT_PATH}}")) / ".claude" / "scratch" / "AGENT_STATE.json"
try:
    with open(state_path) as f:
        state = json.load(f)
    version = state.get("_schema_version", "2.0")
    my_id = os.environ.get("CLAUDE_SESSION_ID", state.get("session_id", ""))
    if version == "2.1" and my_id in state.get("sessions", {}):
        state["sessions"][my_id]["active_task"]["status"] = "closing"
        state["sessions"][my_id]["active_task"]["started_at"] = datetime.now(timezone.utc).isoformat()
    elif version == "2.0":
        state["active_task"]["status"] = "closing"
    tmp = str(state_path) + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.rename(tmp, state_path)
    print(f"✓ Concurrent close guard: OK (schema {version})")
except Exception as e:
    print(f"(AGENT_STATE closing mark skipped: {e})")
```

---

## Step 1 — Identify uncommitted changes

```bash
git -C {{PROJECT_PATH}} status --short
git -C {{PROJECT_PATH}} log --oneline -3
```

---

## Step 2 — Update SESSION_HANDOFF.md

Edit `.claude/status/SESSION_HANDOFF.md`:

1. Update `**Last updated**` to today's date
2. Update `**Active work**` line — one sentence describing what this session did
3. Replace `## IMMEDIATE NEXT TASK` with the known next task (derive from context, do NOT ask the user)
4. Add a `## COMPLETED THIS SESSION ([date])` block with what was done

Do NOT touch OPEN ITEMS unless a new item was clearly created this session.

---

## Step 3 — Write immutable session record

After updating SESSION_HANDOFF.md, write a dated session record:

```python
import json, os
from datetime import datetime
from pathlib import Path

state_path = os.path.expanduser("{{PROJECT_PATH}}/.claude/scratch/AGENT_STATE.json")
try:
    with open(state_path) as f:
        state = json.load(f)
    session_id = state.get("session_id", datetime.now().strftime("%Y-%m-%d-xxxx"))
except Exception:
    session_id = datetime.now().strftime("%Y-%m-%d-xxxx")

sessions_dir = Path(os.path.expanduser("{{PROJECT_PATH}}")) / ".claude" / "sessions"
sessions_dir.mkdir(parents=True, exist_ok=True)
record_path = sessions_dir / f"{session_id}.md"
```

Write to that path:

```markdown
# Session Record — [YYYY-MM-DD] [session_id]

**Type**: checkpoint
**Date**: [YYYY-MM-DD]
**Session ID**: [session_id]

## COMPLETED

[The COMPLETED THIS SESSION block just written to SESSION_HANDOFF — copy verbatim]

## IMMEDIATE NEXT TASK

[The IMMEDIATE NEXT TASK line from SESSION_HANDOFF]
```

---

## Step 4 — Conditional: update CURRENT_STATE.md

**Update if any of these are true:**

- Implementation was confirmed working in a live system
- A system component was added, changed, or fixed (hook, script, command)
- A fact changed that the next session would act on incorrectly if stale

**Skip if:** session was pure research, reading, or planning with no confirmed state changes.

When updating: add a `### [date]` block under `## Completed Work` with 2–4 bullet points max.

---

## Step 5 — Conditional: knowledge capture

**Capture if:** a new fact, decision, or pattern was established that belongs in a knowledge file and is NOT already in SESSION_HANDOFF.

**Skip if:** no new queryable facts were produced.

Route per memory-routing rules. Write directly — do not defer.

---

## Step 6 — Commit

```bash
git -C {{PROJECT_PATH}} add .claude/status/SESSION_HANDOFF.md .claude/status/CURRENT_STATE.md
git -C {{PROJECT_PATH}} commit -m "chore(checkpoint): [date] — [summary]"
```

---

## Step 7 — Print close confirmation

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECKPOINT ✓ — [date]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Committed: [sha]
SESSION_HANDOFF: updated ✓
CURRENT_STATE: [updated ✓ | skipped — no state change]
Knowledge capture: [done — [what] | skipped — no new facts]

NEXT SESSION:
  /start → loads updated handoff
  First task: [one-line from IMMEDIATE NEXT TASK]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```
