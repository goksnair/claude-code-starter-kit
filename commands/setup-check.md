# /setup-check — Post-install self-verification

Run this after completing the 3 customization steps (infra-config.json, CLAUDE.md, goals.md).
Claude Code verifies the entire setup end-to-end and reports what's working, what's missing, and what to fix.

## What this checks

12 items across 4 layers: files, hooks, commands, and memory.

## Step 1 — File layer

Check these files exist and are not empty:

| File | Path | Check |
|------|------|-------|
| CLAUDE.md | ./CLAUDE.md | Exists + no {{PROJECT_NAME}} placeholder remaining |
| infra-config.json | ./infra-config.json | Exists + brand_name is not "{{BRAND_NAME}}" |
| settings.json | .claude/settings.json | Exists + has "hooks" key |
| AGENT_STATE.json | .claude/scratch/AGENT_STATE.json | Exists + valid JSON |
| goals.md | .claude/memory/goals.md | Exists + has content beyond the placeholder lines |
| SESSION_HANDOFF.md | .claude/status/SESSION_HANDOFF.md | Exists |

For each: print ✅ PASS or ❌ FAIL [reason].

## Step 2 — Hook layer

Run the benchmark script if available:

```bash
bash score-starter-kit.sh
```

If score-starter-kit.sh not present, check manually:
- Count files in .claude/hooks/ — should be 20+
- Run: `python3 .claude/hooks/memory-validator.py` with echo '{"tool_name":"Write","tool_input":{"file_path":"/tmp/x.md","content":"test"}}' — should exit 0
- Run: `python3 .claude/hooks/stale-template-check.py` — should exit 0

Print: ✅ Hook layer: [N] hooks present, runtime check passed
Or:    ❌ Hook layer: [specific issue]

## Step 3 — Command layer

Check these command files exist in .claude/commands/:

- work.md, start.md, checkpoint.md, recall.md, query.md, pivot.md, copy-check.md, humanize.md, capture.md

For each missing: ❌ Missing command: [name]
If all present: ✅ Command layer: all core commands present

## Step 4 — Memory layer

Check:
1. `.claude/memory/goals.md` — does it contain the word "(fill in)" still? If yes → ⚠️ goals.md not filled in yet
2. `knowledge/claude-ops/deferred-triggers.md` exists → ✅
3. `knowledge/wiki/claude-ops.md` exists → ✅
4. Run `/recall build` to confirm session index can be built:
   ```bash
   python3 .claude/scripts/session-index.py build
   ```
   Exit 0 → ✅ | Error → ❌ with error message

## Step 5 — Print final report

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SETUP CHECK — {{PROJECT_NAME}}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
File layer:     [✅ PASS / ❌ N issues]
Hook layer:     [✅ PASS / ❌ issue]
Command layer:  [✅ PASS / ❌ N missing]
Memory layer:   [✅ PASS / ⚠️ goals not filled / ❌ issue]

Overall: [READY ✅ / NEEDS ATTENTION ⚠️]

Issues to fix:
  [list each ❌ with one-line fix instruction]

Next: run /start to begin your first real session.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## When to run

- After completing the 3 customization steps for the first time
- After upgrading the starter kit (re-run install.sh on existing project)
- Any time something feels off — hooks not firing, commands missing, memory not loading
