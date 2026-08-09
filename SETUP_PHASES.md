# Setup Phases — {{PROJECT_NAME}}

This document is read by `/onboard` and `onboarding-assistant`. It defines the four phases of a complete first-run setup.

---

## Phase 1 — Install

**Goal**: Kit files are on disk. No prompts hang. No errors.

Steps:
1. Confirm prerequisites: Python 3.8+, git, Claude Code CLI
2. Run `bash install.sh --non-interactive {{PROJECT_NAME}} {{PROJECT_PATH}} "{{USER_NAME}}"`
3. Confirm output: `INSTALLATION COMPLETE` with no errors
4. Confirm files: `CLAUDE.md`, `REPO_MAP.md`, `.claude/memory/goals.md` all exist

Pass condition: all four files present, no placeholder `{{}}` strings remain in CLAUDE.md.

---

## Phase 2 — Discover

**Goal**: Memory files reflect the user's actual situation — not template placeholders.

Two paths depending on user context:

**Path A — existing project** (`/onboard --from-project <path>`):
1. Read `<path>/README.md`, `package.json` or equivalent, `CLAUDE.md`, recent git log
2. Read `<path>/.claude/memory/*` if present — treat as flagged suggestions, not direct copies
3. Draft `goals.md`, `STATUS.md`, `SESSION_HANDOFF.md` from what you find
4. Present drafts to user for review before writing

**Path B — greenfield** (`/onboard --questionnaire`):
1. Ask the 10 discovery questions (see `onboarding-assistant.md`)
2. Map answers to memory file fields
3. Draft all three files, present to user
4. Write on confirmation

Pass condition: `goals.md` does not contain `(fill in)` and `STATUS.md` has at least one real decision or goal.

---

## Phase 3 — Verify

**Goal**: The setup is confirmed working end-to-end.

Steps:
1. Run `bash score-starter-kit.sh` — target 98/100
2. Run `/setup-check` — all 12 items green
3. Check hook wiring: `.claude/settings.json` references hooks that exist in `.claude/hooks/`
4. Check memory routing: confirm no `{{}}` placeholders remain in any bootstrapped file

Pass condition: score ≥ 95, `/setup-check` green, no remaining placeholders.

---

## Phase 4 — Handoff

**Goal**: User is oriented and ready to begin their first real session.

Steps:
1. Print a summary of what was set up
2. Show the populated memory file contents (brief)
3. Explain the daily workflow: `/start` → `/work` → `/checkpoint` → `/end`
4. Print: `Setup complete. Run /start when ready.`

Pass condition: user has been shown their memory file contents and knows the next command.

---

## Quick reference

| Phase | Command | Pass condition |
|-------|---------|----------------|
| Install | `bash install.sh --non-interactive ...` | Files on disk, no errors |
| Discover | `/onboard --from-project` or `--questionnaire` | goals.md populated |
| Verify | `bash score-starter-kit.sh` + `/setup-check` | Score ≥ 95, all green |
| Handoff | — | User knows to run `/start` |
