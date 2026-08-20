---
description: "First-run setup — install, discover use case, populate memory, verify. Run once on a fresh clone. After it completes, run /start."
argument-hint: "[--from-project <path>] [--questionnaire] [--dry-run]"
---

# /onboard

First-run setup command. Run this once when opening a fresh clone of the Claude Code Starter Kit.

**Do not run this on an already-configured project.** If setup is already complete, run `/start` instead.

---

## Flags

| Flag | Effect |
|------|--------|
| `--dry-run` | Print what would happen — no files written, no installs |
| `--from-project <path>` | [optional] Scan an existing project at `<path>` to pre-populate memory |
| `--questionnaire` | [optional] Skip project scan, go straight to 10-question discovery |

If neither `--from-project` nor `--questionnaire` is given, Claude will auto-detect the best path (see Step 4).

---

## Step 0 — Dry-run (if --dry-run)

If `--dry-run` is passed:

1. Read `REPO_MAP.md` and `SETUP_PHASES.md`
2. Print the four phases and what each would do
3. Print: "Run /onboard without --dry-run to execute."
4. Stop

---

## Step 1 — Read the kit

Before doing anything else, read:
1. `REPO_MAP.md` — understand what this kit is and how it works
2. `SETUP_PHASES.md` — understand the four phases you are about to run

Print one line: "Kit architecture loaded. Starting setup."

---

## Step 2 — Detect state

```bash
python3 -c "
import os
proj = os.getcwd()
goals = f'{proj}/.claude/memory/goals.md'
handoff = f'{proj}/.claude/status/SESSION_HANDOFF.md'

if not os.path.exists(goals):
    print('not-installed')
elif '(fill in)' in open(goals).read() or open(goals).read().strip() == '':
    print('installed-not-configured')
elif os.path.exists(handoff) and 'project initialized' in open(handoff).read():
    print('installed-not-configured')
else:
    print('configured')
"
```

- `configured`: print "Setup already complete. Run /start to begin." and stop
- `not-installed`: proceed through all phases
- `installed-not-configured`: skip to Step 4 (discover)

---

## Step 3 — Install (not-installed only)

Ask:
1. Project name (e.g. `MyOS`)
2. Install path (default: `~/my-os`)
3. Your name

Then run:

```bash
bash install.sh --non-interactive "[name]" "[path]" "[user]"
```

Confirm `INSTALLATION COMPLETE` before continuing. If it errors, stop and show the full error.

After install, `cd` into the installed path and continue from there.

---

## Step 4 — Discover

Delegate to the onboarding-assistant agent with the appropriate mode:

- If `--from-project <path>` was passed: run Path A (existing project scan)
- If `--questionnaire` was passed: run Path B (10 questions)
- If neither:
  - Check for signs of an existing project: does the current directory have `README.md`, `package.json`, or `CLAUDE.md`?
  - If yes → default to Path A. Print: "I'll scan your current project at [pwd] — proceed with Path A? [Y/n]" Wait for confirmation. If user says n, fall back to Path B.
  - If no signs of an existing project → default to Path B. Print: "No existing project detected — I'll run the questionnaire (Path B). Proceed? [Y/n]" Wait for confirmation.

The onboarding-assistant handles the full discovery and memory population flow. It will ask questions, present drafts, and write files only after user confirmation.

---

## Step 5 — Verify

After the onboarding-assistant completes, run:

```bash
bash score-starter-kit.sh 2>/dev/null | grep -E "SCORE|FAIL|WARN" | head -10
```

Print the score. If below 95, list failing dimensions.

Then run `/setup-check` for the full 12-item verification.

---

## Step 6 — Handoff

Print:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SETUP COMPLETE — {{PROJECT_NAME}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Memory files populated. Hooks wired. Kit verified.

Run /start when you're ready to begin your first session.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Do not run `/start` automatically. Hand back to the user.

---

## Self-adversarial check (before completing)

1. Did the user confirm the memory file drafts before they were written?
2. Did score-starter-kit.sh run without errors?
3. Is there any `(fill in)` or `{{}}` placeholder remaining in any written file?

If any check fails: fix it before printing SETUP COMPLETE.

---

## Phase 4 — Orientation

After Step 6 completes successfully:

### Step 7 — Validate score

Run `bash score-starter-kit.sh --json` in the project directory. Parse the JSON output and confirm the `score` field is >= 95.

If score is below 95: list the `fail` items and fix them before continuing. Do not proceed until score >= 95.

### Step 8 — Present orientation

Read `CLAUDE_ONBOARDING.md` from the project root (it was copied during install). Present its full content to the user — this covers what was set up, daily commands, memory architecture, and troubleshooting.

### Step 9 — Hand off

Print:

```
Run /start when you're ready.
```
