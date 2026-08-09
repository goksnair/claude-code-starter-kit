# Claude Code Starter Kit

## What it is

Claude Code Starter Kit gives any Claude user a production-ready AI workspace in under 5 minutes. It installs a 23-hook automation system, 50+ slash commands, 10 specialist agents, and a structured memory architecture — so Claude remembers context across sessions, enforces quality, and routes tasks to the right specialist automatically.

Works with Claude Code in terminal, VS Code, Cursor, JetBrains, or any IDE with the Claude extension.

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

Before you start, make sure you have these installed:

### 1. Claude Code CLI

```bash
npm install -g @anthropic-ai/claude-code
```

Don't have npm? Install Node.js first from [nodejs.org](https://nodejs.org) (LTS version). npm comes with it.

### 2. Python 3.8+

Check if you have it:

```bash
python3 --version
```

If not installed: [python.org/downloads](https://www.python.org/downloads/)

### 3. git

Check if you have it:

```bash
git --version
```

If not installed: [git-scm.com/downloads](https://git-scm.com/downloads)

---

## Install — Step by Step

### Step 1 — Download the kit

Open your terminal (Terminal on Mac, Command Prompt or PowerShell on Windows) and run:

```bash
cd ~
git clone https://github.com/goksnair/claude-code-starter-kit
cd claude-code-starter-kit
```

This downloads the kit into a folder called `claude-code-starter-kit` in your home directory.

### Step 2 — Run the installer

```bash
bash install.sh PersonalOS ~/personal-os "Your Name"
```

Replace `"Your Name"` with your actual name (e.g. `"Jane Smith"`).

What this does:

- Creates a new folder at `~/personal-os` with the full directory structure
- Copies all files and replaces placeholders with your name and project name
- Sets up 6 memory files so Claude has context from the first session

You should see output like:

```text
Installing Claude Code Starter Kit
  Project name : PersonalOS
  Project path : /Users/yourname/personal-os
  User name    : Jane Smith

  ✓ commands/work.md
  ✓ hooks/memory-validator.py
  ...
INSTALLATION COMPLETE — PersonalOS
```

### Step 3 — Clean up the installer (optional)

The `claude-code-starter-kit` folder you cloned is no longer needed. You can delete it:

```bash
cd ~
rm -rf claude-code-starter-kit
```

Everything has been copied to `~/personal-os`.

### Step 4 — Open your project in Claude

**Terminal:**

```bash
cd ~/personal-os
claude
```

**VS Code / Cursor / JetBrains:** Open the folder `~/personal-os` in your IDE, then open the Claude panel.

**First thing to type inside Claude:**

```text
/start
```

This loads your memory files and prints your morning briefing. You're ready to go.

---

## Verify the install worked

Run this from inside `~/personal-os`:

```bash
bash score-starter-kit.sh
```

You should see a score of **98/100**. If any dimension scores below 8, something didn't install correctly — re-run the installer on a clean path.

After completing the 3 customization steps below, run this inside Claude Code for a full end-to-end human-readable verification:

```text
/setup-check
```

This checks all 12 items across files, hooks, commands, and memory — and tells you exactly what to fix if anything is missing.

---

## Customize before your first real session

Edit these 3 files after install — everything else can wait:

**1. `infra-config.json`** — find the `brand_name` and `brand_voice` fields, replace the placeholders:

```json
"brand_name": "Jane's OS",
"brand_voice": "direct, practical, no fluff"
```

**2. `CLAUDE.md`** — open this file and read through it. Remove any sections that don't apply to your use case.

**3. `.claude/memory/goals.md`** — fill in what you're actually trying to achieve. Claude reads this at every session start.

---

## What to set up next (optional plugins)

The starter kit works out of the box. These plugins unlock additional capabilities when you're ready:

### graphify — Knowledge graph over your codebase

Lets you run `/graphify query "how does X work?"` to explore relationships across files.

```bash
npm install -g graphify-cli
graphify init .
```

### last30days — Market and signal research

Powers the `/research` command — pulls Reddit, X, YouTube, HackerNews signals for any topic from the last 30 days.

```bash
claude plugins install mvanhorn/last30days-skill
```

### autoresearch — Scheduled research loops

Runs research automatically on a schedule and surfaces results at session start.

```bash
claude plugins install uditgoenka/autoresearch
```

These are pre-registered in `knowledge/claude-ops/deferred-triggers.md` — Claude will surface them at the right moment.

---

## Memory architecture

Claude remembers things across sessions through 5 files:

| File | Location | What to put in it |
|------|----------|--------------------|
| STATUS.md | .claude/memory/ | What you're actively working on, decisions pending |
| goals.md | .claude/memory/ | Your goals — 1 month, 1 year, long term |
| SESSION_HANDOFF.md | .claude/status/ | Auto-updated at session end — don't edit manually |
| CURRENT_STATE.md | .claude/status/ | Auto-updated — project intelligence summary |
| AGENT_STATE.json | .claude/scratch/ | Auto-managed — don't edit manually |

---

## Hook event map

| Event | Hooks | What they catch |
|-------|-------|-----------------|
| SessionStart | session-start.py, context-load.py | Deadline warnings, stale memory |
| UserPromptSubmit | bash-tool-guard.py, large-file-guard.py | Tool discipline, context budget |
| PreToolUse | memory-validator.py, content-output-guard.py | Wrong-path writes, output cap |
| PostToolUse | doc-governance.py, wiki-lint-check.py, git-recent-wins.py | Doc quality, wiki drift, wins log |
| Stop | session-persist.py, work-pipeline-guard.py, learn-rule-extractor.py | Turn count, pipeline audit, rule extraction |
| PreCompact | pre-compact-backup.py, stale-template-check.py | Backup, template drift |

---

## Command list

| Command | What it does |
|---------|--------------|
| `/start` | Morning briefing — loads memory, surfaces deadlines |
| `/work [directive]` | Runs any task through the full agent pipeline |
| `/checkpoint` | End-of-session save + handoff update |
| `/end` | Full session close |
| `/status` | Full dashboard — decisions, deadlines, open items |
| `/week` | Weekly review — goal alignment + next-week priorities |
| `/capture [note]` | Quick note auto-routed to the right memory file |
| `/dump [text]` | Bulk capture — routes all pieces to the right files |
| `/lock [fact]` | Lock a confirmed fact/decision into memory immediately |
| `/copy-check` | Scores outbound copy before you send it |
| `/humanize` | Strips AI-patterns from generated content |
| `/recall [query]` | Search past sessions by topic |
| `/query [topic]` | Search the knowledge wiki |
| `/pivot project:<name>` | Load a project context |
| `/setup-check` | Verify the entire setup is working end-to-end |

---

## /work pipeline

The `/work` command routes every task through a structured pipeline: (1) Prompt Engineer agent reads your directive and produces a structured WorkOrder; (2) the WorkOrder is validated against hard-stop rules; (3) the right specialist agent executes it; (4) a GATE-2 review confirms the work meets done criteria before committing. This prevents ad-hoc execution and ensures every task has verifiable output.

---

## License

MIT. Built for personal use — adapt freely.
