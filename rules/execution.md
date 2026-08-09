# Execution Rules
<!-- Enforced by: bash-tool-guard.py (PreToolUse:Bash), large-file-guard.py (PreToolUse:Read) -->
<!-- Behavioral-only rules are marked [behavioral] -->

## Tool-to-Tool Mapping (NEVER use shell aliases)
- Read files: `Read` tool — never `cat`, `head`, `tail`
- Edit files: `Edit` or `Write` tool — never `sed`, `awk`, `echo >`
- Search content: `Grep` tool — never `grep`, `rg`
- Find files: `Glob` tool — never `find`, `ls`
- Reserve `Bash` for: git operations, running scripts, system commands with no dedicated tool

**Hook**: `bash-tool-guard.py` fires on every Bash call and flags violations.

## Keep Reads Targeted (offset/limit, not full files) [behavioral]
- Files > 200 lines: use `offset` + `limit` or `Grep` to find the section first
- Files > 800 lines: REQUIRED to use targeted read — full read wastes significant context
- Exception: if you genuinely need the full file, proceed — guard is non-blocking

**Hook**: `large-file-guard.py` fires on every Read call and warns on large files.

## Conversational Knowledge Capture — Write Decisions Immediately [behavioral]

When any fact, figure, decision, or deadline is confirmed in conversation:
1. Write it to the correct file **before moving to the next topic** — not at session end
2. Use the `/capture` command to route to the right target

## Think Before Acting [behavioral]

Before implementing any non-trivial task:
- State assumptions explicitly — if uncertain, ask rather than guess
- If multiple interpretations exist, present them; don't pick silently
- If a simpler approach exists, say so and push back

## Self-Adversarial Check — Required Before Declaring Done [behavioral]

Before reporting any implementation as complete, answer these three questions explicitly:

1. What inputs or edge cases does this NOT handle?
2. What assumption am I making that I haven't verified?
3. What breaks this in 30 days when [X] changes?

Two valid responses when a gap is found — no third option:
1. **Fix it immediately** — before presenting GATE-2 or reporting done.
2. **Prove it cannot be fixed** — state why AND name the exact follow-up action.

## Surgical Changes [behavioral]

- Touch only what the task requires — don't improve adjacent code
- Remove only imports/variables/functions that YOUR changes made unused
- Every changed line should trace directly to the user's request

## Agent Delegation [behavioral]

**Use an agent when:**
- Output would be 50+ lines you don't need in main context
- Truly independent tasks can run in parallel
- Work requires multi-file exploration across unknown territory

**Do NOT spawn an agent for:**
- Reading 1–3 specific known files (use Read/Grep directly)
- Surgical edits to known locations (overhead exceeds savings)
- Single-step tasks with deterministic output

Rule of thumb: if the work fits in ≤5 tool calls and you know exactly which files, do it directly.

## Dynamic Tool Loading [behavioral]

In /work Step 5 subagent dispatch, only inject tool descriptions relevant to the current task domain. Prefer ToolSearch over static tool injection when the subagent only needs 1–3 tools.

## /start Is Required — Not Optional [behavioral]

Run `/start` at the beginning of every session before any task work begins.

**Exception**: If you already ran `/start` in the same session — do not re-run.

## No Task Work Carries Over Without Writing It Down [behavioral]

If a task is in progress at session end, its status MUST be written before closing:
- Blocked: write to STATUS.md or relevant knowledge file with blocker detail
- Done: write the outcome to the right memory or knowledge file

## Non-Negotiable Summary

1. Run `/start` once per session
2. All decisions live in `.claude/memory/` — never in conversation only
3. `/compact` at turn 10–12 with focus instruction
4. Every `/work` task goes through PE + specialist — no inline execution by main session
