# Claude Code Starter Kit

## What it is

Claude Code Starter Kit is a 55-file portable template library that gives any new project a production-ready Claude Code setup in under 5 minutes. Includes a 23-hook event system, 50+ slash commands, 10 specialist agents, and a structured memory architecture — everything you need to run Claude Code as a personal OS for solo projects and client engagements.

---

## What's included

| Category | Count | Purpose |
|----------|-------|---------|
| Hooks | 23 | Automate session hygiene, guard drift, enforce memory routing |
| Commands | 50+ | /work, /start, /pivot, /checkpoint, /copy-check, /humanize... |
| Agents | 10 | PE, coordinator, research, code-review, security, chief-of-staff... |
| Memory files | 5 | STATUS.md, goals.md, SESSION_HANDOFF.md, CURRENT_STATE.md, AGENT_STATE.json |
| Rules | 2 | execution.md, memory.md — behavioral constraints for Claude |
| Config | 2 | settings.json (hook wiring), infra-config.json (brand customization) |

---

## Prerequisites

- Claude Code CLI: `npm install -g @anthropic-ai/claude-code`
- Python 3.8+
- git

---

## Install

```bash
git clone https://github.com/goksnair/claude-code-starter-kit
cd claude-code-starter-kit
bash install.sh MyProject /path/to/my-project "Your Name"
```

Then: open Claude Code in `/path/to/my-project` and run `/start`.

---

## Memory architecture

| File | Location | Purpose |
|------|----------|---------|
| STATUS.md | .claude/memory/ | Active decisions + blockers |
| goals.md | .claude/memory/ | 1yr/3yr/10yr anchors |
| SESSION_HANDOFF.md | .claude/status/ | Cross-session continuity |
| CURRENT_STATE.md | .claude/status/ | Intelligence summary |
| AGENT_STATE.json | .claude/scratch/ | Agent task tracking |

---

## Hook event map

| Event | Hooks | Catches |
|-------|-------|---------|
| SessionStart | session-start.py, context-load.py | Deadline warnings, stale memory |
| UserPromptSubmit | bash-tool-guard.py, large-file-guard.py | Tool discipline, context budget |
| PreToolUse | memory-validator.py, content-output-guard.py | Wrong-path writes, output cap |
| PostToolUse | doc-governance.py, wiki-lint-check.py | Doc quality, wiki drift |
| Stop | session-persist.py | Turn count, handoff staleness |
| PreCompact | pre-compact-backup.py, stale-template-check.py | Backup, template drift |

---

## Command list

| Command | Purpose |
|---------|---------|
| `/start` | Morning briefing — load memory, surface deadlines, print decision dashboard |
| `/work [directive]` | Run any task through PE + specialist + GATE-2 pipeline |
| `/pivot [persona]` | Switch active persona context with HANDOFF checklist |
| `/checkpoint` | End-of-session commit + handoff update |
| `/end` | Full session close — write all open items before exiting |
| `/copy-check` | Score outbound copy against voice/quality rules before sending |
| `/humanize` | Strip AI-patterns from generated content before publishing |
| `/capture [note]` | Quick capture auto-routed to the correct memory file |
| `/compact` | Summarize context at turn 10-12 with focus instruction |

---

## /work pipeline

The `/work` command runs every task through a structured pipeline: (1) Prompt Engineer agent reads the directive and produces a WORKORDER.json with framework, routing, and done criteria; (2) /work validates the WorkOrder against hard-stop firewalls; (3) the named specialist agent executes the structured_prompt; (4) GATE-2 review confirms done criteria before committing. This prevents ad-hoc execution and ensures every task has verifiable output.

---

## Customization guide

Edit these first:
1. `infra-config.json` — set BRAND_NAME and BRAND_VOICE
2. `CLAUDE.md` — review persona system and remove inapplicable sections
3. `.claude/memory/goals.md` — fill in your actual goals

Leave `hooks/`, `settings.json`, and `agents/` untouched until you understand what each does.

---

## License

MIT. Built for personal use — adapt freely.
