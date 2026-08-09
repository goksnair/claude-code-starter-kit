# /pivot — Switch active context

Switches focus to a different project, client engagement, or work mode.

## Usage

```
/pivot engagement:<name>     # load a client engagement
/pivot project:<name>        # load a project context
```

## Steps

### For /pivot engagement:<name>

1. Check `~/engagements/<name>/CONTEXT.md` exists. If not:
   ```
   ❌ No CONTEXT.md found at ~/engagements/<name>/CONTEXT.md
      Run: /work "create CONTEXT.md for <name>" to initialize it.
   ```
   Stop.

2. Read `~/engagements/<name>/CONTEXT.md` (limit 100 lines).
   Read `~/engagements/<name>/RULES.md` if it exists (limit 50 lines).

3. Read `knowledge/claude-ops/ENGAGEMENT_REGISTRY.md` — check status for this engagement.

4. Print pivot confirmation:
   ```
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ENGAGEMENT → <name>
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   [2-3 lines: current phase, what's active, what's overdue]
   [Next deadline or action]

   Use /work [task] to dispatch — or describe your task.
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ```

5. Hold this context for the rest of the session. All /work tasks go to this engagement's output folder.

## Notes

- Engagement files live at `~/engagements/<name>/`
- CONTEXT.md = phase, status, key people, immediate next action
- RULES.md = constraints specific to this engagement (optional)
- Output goes to `~/engagements/<name>/outputs/`
- Run /checkpoint before switching to a different engagement
