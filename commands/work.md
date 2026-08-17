---
description: "{{PROJECT_NAME}} multi-step task dispatcher. Runs PE -> specialist -> GATE-2 pipeline inline. Use when task needs a specialist agent, produces 50+ lines of output, or requires GATE-2 review. NOT for direct file edits (<=5 tool calls) — do those inline."
argument-hint: "your task directive (optional — will ask if blank)"
---

I'm running the `/work` orchestration pipeline **inline in the main session**. The coordinator protocol lives at `.claude/agents/coordinator.md` — read it as a reference document, do not dispatch it via Task() (nested Task calls are not permitted).

## Step 1 — Collect directive

The user's directive is: $ARGUMENTS

If blank: ask exactly this and wait:
> "What would you like to work on?"

## Step 2 — Context check

Read `.claude/scratch/AGENT_STATE.json`. Print one line:
```
Turn [N] | Context: [GREEN (<=9) / YELLOW (10-14) / ORANGE (15-19) / RED (20+)]
```

If ORANGE or RED: `Context is heavy. Consider /compact before this task. Proceeding...`

If `active_task.status == "in_progress"`: STOP. Print orphan warning — instruct human to reset to `idle`.

## Step 3 — Dispatch prompt-engineer (Task)

```
Task(
  subagent_type="prompt-engineer",
  description="Draft WorkOrder for directive",
  prompt="""
Directive: [directive verbatim]

Working directory: {{PROJECT_PATH}}
AGENT_STATE path: .claude/scratch/AGENT_STATE.json

Produce WORKORDER.json per your spec at .claude/agents/prompt-engineer.md.
Classify directive complexity (simple vs deep) and produce structured_prompt accordingly.
Validate your own WorkOrder before writing (see Self-Validation section).
"""
)
```

## Step 4 — Validate WorkOrder (FIREWALLS)

After PE Task completes, verify `.claude/scratch/WORKORDER.json` exists.

**If missing**: STOP.
```
PE BYPASS DETECTED — WORKORDER.json not written
Re-dispatch PE once. If it fails again, stop and report to human.
```

**If exists**: Read and validate:

| Check | Rule |
|-------|------|
| Schema version | `$schema` starts with `{{PROJECT_NAME}}/workorder/v` |
| primary_agent | NOT in `["self", "inline", "direct", "coordinator", "general-purpose"]` |
| primary_agent | Must be in dispatch map in coordinator.md |
| framework | One of PSTAR / CLEAR / 4-Part / T7 |
| dispatch_mode | One of single / sequential / parallel / chained-review |
| structured_prompt | Non-empty, >=120 tokens |
| done_criteria | Array with >=2 verifiable conditions |
| complexity=deep | framework_reasoning, ambiguity_resolution, memory_excerpts all present and non-empty |

**If any check fails**: STOP. Print the specific violation. Re-dispatch PE ONCE with the violation noted. If it fails again: stop, print WorkOrder, ask human. NO INFINITE RETRY.

## Step 5 — Resolve specialist and dispatch

Look up `primary_agent` in the dispatch map at `.claude/agents/coordinator.md`. If not found: STOP with `DISPATCH BLOCKED — agent '[name]' not in dispatch map`.

Print routing decision:
```
ROUTING -> [agent] | [framework] | [dispatch_mode] | complexity=[simple|deep]
[one-line reason from WorkOrder]
Dispatching...
```

Dispatch based on `dispatch_mode`:
- **single**: one Task call with `structured_prompt` verbatim
- **sequential**: primary Task -> wait -> secondary Task with primary output path in prompt
- **parallel**: primary + secondary Task calls in the SAME response message
- **chained-review**: primary -> then reviewer agents on modified files

Prepend to every specialist prompt:
```
## Execution Constraints
- Respond in under 30 lines / 500 words. Verbose output goes to file.
- Read AGENT_SHARED_CONTEXT.md before starting.

## MANDATORY Pre-Question Gate

Before asking the user ANY question, verify it is a decision (only the user can make it), not a fact (findable in files). Check these sources first:

1. `.claude/memory/` — STATUS.md, goals.md, preferences.md
2. `knowledge/` — domain research, cost model, notes
3. `.claude/projects/[project]/memory/` — reference memory files
4. `.claude/scratch/AGENT_STATE.json` — active task and session context

Only ask if source(s) returned null OR the item is a genuine preference/decision.
When asking: cite which source you checked.
```

## Step 6 — Update AGENT_STATE + delete WorkOrder

After specialist(s) complete, update AGENT_STATE.json (set active_task to completed). Then:
```bash
rm .claude/scratch/WORKORDER.json
```

## Step 7 — GATE-2 summary

Print in this exact structure:
```
WORK COMPLETE — GATE-2 REVIEW

WorkOrder: [task_id] -> [agent] | [framework] | [dispatch_mode] | complexity=[simple|deep]

## DONE
[3-5 bullets from specialist output]

## VERIFIED
[file proof / git sha / runtime check — no vague "task complete"]

## SELF-ADVERSARIAL CHECK
- Unhandled edge cases: [what]
- Unverified assumptions: [what]
- 30-day fragility: [what breaks when X changes]

## UNRESOLVED
[gaps with named follow-up action]

## COMMIT MANIFEST
Files: [list]
Message: [suggested]

Turn [N] | Context: [color]
y = commit | n = skip
```

## Non-Negotiables
- PE runs on every /work call. WORKORDER.json must be written before dispatch.
- WorkOrder validation firewalls are hard stops, not warnings.
- Max 2 PE attempts per directive. If both fail, escalate to human.
- Nested Task() is banned — coordinator is a protocol doc, not a subagent.
