---
description: "Voice-calibrated editing — makes Claude-drafted text sound like you wrote it."
---

Edit the specified text or file to match the project owner's writing voice.

## Usage
/humanize <file path or pasted text>

## Voice Calibration
First read 2 recent files the user actually wrote (adapt paths to this project):
- `.claude/memory/STATUS.md` — how they write about decisions (if exists)
- Any recent knowledge/ or deliverables/ file they authored

Extract voice fingerprint: sentence length, directness, punctuation habits, ratio of hedged to direct statements.

## Editing Rules
- Direct statements, not hedged ones ("This was hard" not "This presented challenges")
- Kill: "notably", "significantly", "leveraged", "facilitated", "it's worth noting that"
- Kill: passive voice where active is natural
- Kill: hedge stacking ("potentially", "arguably", "could be said")
- Match natural rhythm — fragments and dashes are fine if that's the voice

## Preserve Untouched
- All YAML frontmatter
- Tables (content can change, structure stays)
- Code blocks and file paths

## Output
Brief summary only:
- Tone shift: what changed overall
- 2-3 key before/after examples
- What was preserved and why

## Quality Gate (Required — not optional)

Voice calibration is step 1. After editing, **always run /copy-check** as step 2.

> "The humanize pass makes it sound human. The copy-check confirms it passes the gate.
> Neither is optional for copy going to a second person or public channel."

Run: `/copy-check` on the edited copy before it leaves the session.

$ARGUMENTS
