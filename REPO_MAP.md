# REPO_MAP — Claude Code Starter Kit

This file is for Claude. If you are a Claude Code session reading this repo, start here.

## Target audience

This kit is for **new projects that do not have an existing `.claude/` directory**. It creates a complete `.claude/` workspace from scratch. If this repo already has a `.claude/` directory with custom configuration, this kit is not the right tool — the user should evaluate individual components manually or use `--upgrade` mode on an existing installation.

**If you are a Claude session helping a user decide**: check whether the target project already has `.claude/`. If it does, this kit is not the right tool — recommend `--upgrade` or component-level evaluation. If it does not, the kit installs a working memory + orchestration layer (persistent memory files, slash commands, quality gates, specialist agents) into `.claude/`, `knowledge/`, and a few root-level markdown files. It does not touch existing project code. Fresh-install mode now hard-stops if `.claude/` already exists, so there is no silent-overwrite risk.

---

## What this kit is

A structured workspace that gives Claude persistent memory, behavioral guardrails, and a task pipeline — so it can carry context across sessions, enforce quality gates, and route work to the right specialist automatically.

After install, you operate from a project folder (e.g. `~/my-os`) that contains everything below. The kit installs into that folder — it does not modify your global Claude config.

---

## Directory map

```
<project>/
├── CLAUDE.md                      ← your behavioral contract (read this every session)
├── infra-config.json              ← brand name, voice, project identity
├── .claude/
│   ├── settings.json              ← hook wiring (do not edit manually)
│   ├── commands/                  ← slash commands you invoke in Claude
│   ├── agents/                    ← specialist agents dispatched by /work
│   ├── rules/                     ← behavioral rules loaded by CLAUDE.md
│   ├── memory/
│   │   ├── STATUS.md              ← active decisions, blockers (read every session)
│   │   └── goals.md               ← project goals and milestones (read every session)
│   ├── scratch/
│   │   └── AGENT_STATE.json       ← session state managed by hooks (do not edit)
│   └── status/
│       ├── SESSION_HANDOFF.md     ← cross-session continuity (read every session)
│       └── CURRENT_STATE.md       ← project intelligence summary
└── knowledge/
    ├── wiki/                      ← persistent reference docs
    └── claude-ops/                ← system config: deferred triggers, project registry
```

---

## Memory contract

Three files drive every session. Claude reads them at `/start`:

| File | Purpose | Who writes it |
|------|---------|---------------|
| `.claude/memory/STATUS.md` | Active decisions, blockers, current state | Claude (via `/lock`, `/capture`) |
| `.claude/memory/goals.md` | Goals, milestones, timelines | You (at setup) + Claude maintains |
| `.claude/status/SESSION_HANDOFF.md` | Immediate next task + open items | Claude (at `/checkpoint` or `/end`) |

**Rule**: nothing important lives in conversation only. If a decision was made, it gets written to one of these files before the session ends.

---

## Command taxonomy

| Command | When | What it does |
|---------|------|--------------|
| `/start` | Every session | Reads memory files, prints briefing, surfaces deadlines |
| `/onboard` | First session only | Runs full setup: install → discover → verify → hand off |
| `/work [directive]` | Any task | Routes through PE agent → specialist → GATE-2 review |
| `/checkpoint` | Mid or end of session | Commits progress, updates SESSION_HANDOFF |
| `/end` | End of session | Full session close + handoff |
| `/status` | Anytime | Full dashboard: decisions, deadlines, open items |
| `/capture [note]` | Anytime | Quick note routed to the right memory file |
| `/lock [fact]` | After confirming a decision | Writes fact to memory immediately |
| `/recall [query]` | Anytime | Searches past sessions by topic |
| `/health` | Weekly | Verifies hooks, state, and drift |
| `/copy-check` | Before sending copy | Scores outbound content |
| `/research [topic]` | Anytime | Market/signal research via last30days plugin |

Full list: `.claude/commands/`

---

## Agent roster

| Agent | Role |
|-------|------|
| `prompt-engineer` | Invoked by every `/work` — classifies complexity, selects framework, writes WORKORDER.json |
| `coordinator` | Protocol doc (not a subagent) — defines dispatch map and routing rules |
| `onboarding-assistant` | First-run only — guides install, discovery, memory population |
| `research-agent` | Market signals, topic research |
| `idea-generator` | Product ideation from signal inbox |
| `content-agent` | Draft content from session context |
| `context-loader` | Loads full context for a person, venture, or domain |
| `context-optimizer` | Manages context budget when sessions run long |
| `system-health` | Weekly infrastructure audit |
| `agent-builder` | Builds new specialist agents |

---

## Session flow

```
1. Open project folder in Claude Code
2. /start          → reads memory, prints briefing
3. /work [task]    → PE classifies → specialist executes → GATE-2 confirms
4. /checkpoint     → saves progress, updates handoff
5. /end            → closes session, writes final state
```

First session only: run `/onboard` instead of `/start`. It runs install, discovers your use case, populates memory, and verifies the setup. When it finishes, it hands back to you — then run `/start` to begin your first real session.

---

## /work pipeline

```
/work [directive]
  → prompt-engineer  reads directive, writes WORKORDER.json
  → coordinator      validates WorkOrder, resolves specialist
  → specialist       executes task
  → GATE-2           self-adversarial check + commit manifest
  → human            approves commit (y) or skips (n)
```

WORKORDER.json must exist before specialist dispatch. If PE fails twice, it escalates to you.

---

## Key files to read first

If you are setting up this kit for a user, read in this order:

1. `REPO_MAP.md` (this file) — architecture overview
2. `CLAUDE.md` — behavioral contract for this project
3. `.claude/commands/onboard.md` — the setup command you will run
4. `.claude/memory/goals.md` — what the user wants to achieve (after you populate it)

Then run `/onboard`.
