# {{PROJECT_NAME}} — Claude Code System

## What This Is
You are an AI assistant operating in the {{PROJECT_NAME}} project. This system gives you structured orchestration, quality gates, and persistent memory so you produce consistent, reviewable output.

---

## Session Start

Every session: read these files before any task work:
1. `.claude/memory/STATUS.md` — current project status, active decisions, deadlines
2. `.claude/memory/goals.md` — project goals and milestones
3. `.claude/status/SESSION_HANDOFF.md` — IMMEDIATE NEXT TASK + OPEN ITEMS only

---

## Commands

| Command | When to use |
|---------|------------|
| `/start` | Every morning — project briefing + decision dashboard |
| `/work [directive]` | Multi-step tasks — dispatches to specialist agent via PE + GATE-2 |
| `/checkpoint` | End of session — commit + update handoff |
| `/health` | Weekly — verify hooks, state, and drift |
| `/copy-check` | Before sending any copy externally |
| `/humanize` | Before any AI-written content goes live |

---

## Non-Negotiables

1. Run `/start` at the beginning of every session
2. All decisions live in `.claude/memory/` — never in conversation only
3. `/compact` at turn 10-12 with focus instruction (e.g. `/compact keep only the plan and the diff`)
4. Every `/work` task goes through PE + specialist — no inline execution by main session
5. Read files with Read tool, edit with Edit tool — never use cat/sed/echo

---

## Tool Mapping

| Action | Tool | Never use |
|--------|------|-----------|
| Read files | Read tool | cat, head, tail |
| Edit files | Edit or Write tool | sed, awk, echo > |
| Search content | Grep tool | grep, rg |
| Find files | Glob tool | find, ls |
| Shell operations | Bash | — |

---

## Behavioral Rules

### Think Before Acting
Before any non-trivial task:
- State assumptions explicitly — if uncertain, ask rather than guess
- If multiple interpretations exist, present them; don't pick silently

### Self-Adversarial Check (required before declaring done)
1. What inputs or edge cases does this NOT handle?
2. What assumption am I making that I haven't verified?
3. What breaks this in 30 days when [X] changes?

Two valid responses when a gap is found:
1. Fix it immediately
2. Prove it cannot be fixed — state why AND name the exact follow-up action

### Surgical Changes
- Touch only what the task requires
- Remove only imports/variables/functions YOUR changes made unused
- Every changed line traces directly to the user's request

### Agent Delegation
Use an agent when:
- Output would be 50+ lines you don't need in main context
- Truly independent tasks can run in parallel
- Work requires multi-file exploration across unknown territory

Do NOT spawn agents for: reading 1-3 known files, surgical edits, single-step tasks with deterministic output.

---

## Memory Architecture

```
.claude/
  memory/
    STATUS.md        — current project status, active decisions, deadlines
    goals.md         — project goals and milestones
  scratch/
    AGENT_STATE.json — session state (managed by hooks, do not edit manually)
  status/
    SESSION_HANDOFF.md — cross-session continuity
    CURRENT_STATE.md   — project intelligence summary
```

**Rule**: No decision, deadline, or actionable insight lives in conversation only. Every session produces at least one write to a memory or knowledge file.

---

## /work Pipeline

Every `/work` task goes through:
1. **PE** (prompt-engineer) -> classifies complexity, selects framework, writes WORKORDER.json
2. **Specialist** -> executes task, writes output to `.claude/scratch/`
3. **GATE-2** -> self-adversarial check + commit manifest for human approval

Non-negotiables:
- WORKORDER.json must exist before specialist dispatch
- Max 2 PE retries then escalate to human
- Nested Task() is banned — coordinator is a protocol doc

---

**Last Updated**: {{DATE}}
