---
name: onboard-discover
description: "Discover user context via existing project scan or questionnaire. Populates memory files. Called by onboarding-assistant Step 3 — not invoked directly."
---

## Mode A — `--from-project <path>`

### Step 1 — Scan existing project

Read these files from `<path>` in order:

1. `README.md`
2. `package.json` (or `pyproject.toml` or `Cargo.toml`)
3. `CLAUDE.md`
4. Run `git log --oneline -10` via Bash
5. `.claude/memory/goals.md`, `.claude/memory/STATUS.md`, `.claude/status/SESSION_HANDOFF.md`

### Step 2 — Flag stale memory

For any existing memory file found in Step 1.5: flag as potentially stale. Extract intent and reframe as a suggestion:

> "Based on your existing goals.md, I think your primary goal is [X]. Does that still hold?"

Do not copy content verbatim. Reframe discovered intent as a confirmation question.

### Step 3 — Draft memory files

Draft all three memory files from discovered content:

- `goals.md` — project purpose, primary goal, key milestones
- `STATUS.md` — current focus, active decisions, blockers
- `SESSION_HANDOFF.md` — immediate next task, open items

Present each draft to the user before writing. Wait for confirmation on each.

### Step 4 — Write after confirmation

Write each file only after the user explicitly confirms the draft.

---

## Mode B — `--questionnaire`

Present exactly these 10 questions, one at a time. Wait for each answer before asking the next.

1. What is your role? (e.g. founder, developer, consultant, researcher, student)
2. What is this project for? Describe it in one sentence.
3. What is the single most important outcome you want in the next 3 months?
4. Is there a hard deadline coming up? If yes, what is it and when?
5. What are the 2-3 key deliverables you are working toward?
6. Are you working alone or with a team? If team, how many people and what are their roles?
7. What tools do you use day-to-day? (e.g. VS Code, Notion, GitHub, Linear, Figma)
8. How often do you plan to use Claude on this project? (daily / a few times a week / ad hoc)
9. What is the biggest thing blocking you right now?
10. Anything else Claude should know about you or this project before we start?

After all 10 answers, state the mapping before drafting:

> "Based on your answers, here is what I will write:
> - `goals.md` <- answers 2, 3, 5
> - `STATUS.md` <- answers 4, 6, 9
> - `SESSION_HANDOFF.md` <- answer 3 as immediate next task"

Draft each file. Present to the user. Write only after confirmation on each.

---

## Rules

- Never write `(fill in)` or `{{VARIABLE}}` placeholders into user memory files
- Never copy financial figures, credentials, or API keys from a scanned project
- If a memory file already exists AND does not contain `<!-- CLAUDE:TEMPLATE -->` sentinel: do NOT overwrite. Print: `[filename] already contains user content — skipping.`
- Stale memory from Mode A must be presented as suggestions, not copied verbatim
