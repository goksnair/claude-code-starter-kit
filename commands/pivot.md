# /pivot — Switch active context

Switches focus to a different project or work mode.

## Usage

```
/pivot project:<name>     # load a project context
```

## Steps

### For `/pivot project:<name>`

1. Check `~/projects/<name>/CONTEXT.md` exists. If not:
   ```
   ❌ No CONTEXT.md found at ~/projects/<name>/CONTEXT.md
      Run: /work "create CONTEXT.md for <name>" to initialize it.
   ```
   Stop.

2. Read `~/projects/<name>/CONTEXT.md` (limit 100 lines).
   Read `~/projects/<name>/RULES.md` if it exists (limit 50 lines).

3. Read `knowledge/claude-ops/PROJECT_REGISTRY.md` — check status for this project.

4. Print pivot confirmation:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   PROJECT → <name>
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [2-3 lines: current phase, what's active, what's overdue]
   [Next deadline or action]

   Use /work [task] to dispatch — or describe your task.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

5. Hold this context for the rest of the session. All /work tasks go to this project's output folder.

## Notes

- Project files live at `~/projects/<name>/`
- CONTEXT.md = phase, status, key people, immediate next action
- RULES.md = constraints specific to this project (optional)
- Output goes to `~/projects/<name>/outputs/`
- Run /checkpoint before switching to a different project
