# {{PROJECT_NAME}} — Post-Onboarding Orientation

You have completed `/onboard`. This document explains what was set up and how to use it.

---

## What Was Set Up

`install.sh` created the following structure in your project:

- `.claude/commands/` — slash commands (`/start`, `/work`, `/checkpoint`, `/health`, etc.)
- `.claude/hooks/` — automated guards (memory-validator, session-start, stale-template-check)
- `.claude/agents/` — specialist agent definitions for `/work` dispatch
- `.claude/rules/` — behavioral rules Claude follows automatically
- `.claude/memory/` — persistent memory files (`goals.md`, `STATUS.md`)
- `.claude/status/` — session handoff and project state (`SESSION_HANDOFF.md`, `CURRENT_STATE.md`)
- `.claude/scratch/` — temporary working memory (never committed)
- `knowledge/` — wiki pages, project registry, deferred triggers
- `CLAUDE.md` — main system prompt loaded every session
- `score-starter-kit.sh` — health check script

Memory files were populated with your project name and bootstrapped with starter content. Hooks were wired via `.claude/settings.json`.

---

## Daily Use

| Command | When | Example |
|---------|------|---------|
| `/start` | Beginning of every session | Just type `/start` — it reads memory files, shows active decisions and deadlines |
| `/pivot` | Switching to a different project or context | `/pivot project:backend-api` loads that project's context |
| `/work` | Any multi-step task | `/work refactor the auth module to use JWT` — dispatches to specialist agent with quality gates |
| `/week` | End of week | `/week` — generates weekly summary, tracks wins and blockers, plans next week |

---

## Memory Files

| File | Contains |
|------|----------|
| `.claude/memory/STATUS.md` | Active decisions, deadlines, current blockers |
| `.claude/memory/goals.md` | Project goals and milestones |
| `.claude/status/SESSION_HANDOFF.md` | What to pick up next session — immediate task + open items |
| `.claude/status/CURRENT_STATE.md` | Intelligence summary — broad project state |

**The rule**: No decision, deadline, or actionable insight lives in conversation only. If it matters, it gets written to a memory file before the topic changes.

---

## If Something Seems Off

1. Run `/setup-check` — the 12-item verification that confirms hooks, memory files, and commands are intact
2. Run `bash score-starter-kit.sh` — quick numeric score of kit health
3. If score is below 95 or checks fail: re-run `/health` which diagnoses and suggests fixes

Common issues:
- Hook not firing: check `.claude/settings.json` has the hook registered
- Memory file empty: re-run `/onboard --questionnaire` to re-populate
- Stale handoff: update `SESSION_HANDOFF.md` manually or run `/checkpoint`

---

## Keeping Memory Current

Memory files drift if not maintained. Two habits prevent this:

**After any decision or deadline is confirmed in conversation**, use:
- `/lock [fact]` — writes a single fact to the correct memory file immediately
- `/capture [note]` — auto-routes a note to the right file when the destination is ambiguous

**Weekly maintenance**:
- Review `goals.md` — update milestone statuses, add new goals, mark completed ones
- Review `STATUS.md` — clear resolved decisions, add new blockers
- Run `/health` — catches drift before it compounds

---

<!-- Last Updated: {{DATE}} -->
