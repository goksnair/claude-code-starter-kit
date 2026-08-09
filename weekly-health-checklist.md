# Weekly Infra Health Checklist
**Estimated total time: ~15 min**
**Run every Sunday or Monday morning**

---

## A. Hook Health (~5 min)

- [ ] Count hook files: compare `.claude/hooks/*.py` against entries in `.claude/settings.json` — no orphans, no phantoms
- [ ] Cross-reference: every `.py` in hooks/ is referenced in settings.json
- [ ] Every settings.json hook command points to a file that exists
- [ ] Check `.claude/logs/` for any ERROR lines from past 7 days (if logging is enabled)
- [ ] Verify any new hooks added this week are wired in settings.json

```bash
# Quick hook inventory check
python3 -c "
import json, os
from pathlib import Path

proj = Path('{{PROJECT_PATH}}')
hooks_dir = proj / '.claude' / 'hooks'
settings_path = proj / '.claude' / 'settings.json'

hook_files = {f.name for f in hooks_dir.glob('*.py')} if hooks_dir.exists() else set()

with open(settings_path) as f:
    settings = json.load(f)

referenced = set()
for event, matchers in settings.get('hooks', {}).items():
    for m in matchers:
        for h in m.get('hooks', []):
            cmd = h.get('command', '')
            for word in cmd.split():
                if word.endswith('.py'):
                    referenced.add(Path(word).name)

orphans = hook_files - referenced
phantoms = {r for r in referenced if r not in hook_files}

print(f'Hook files: {len(hook_files)} | Referenced: {len(referenced)}')
if orphans: print(f'ORPHANS (in hooks/, not in settings): {orphans}')
if phantoms: print(f'PHANTOMS (in settings, not in hooks/): {phantoms}')
if not orphans and not phantoms: print('OK — all hooks matched')
"
```

---

## B. Memory Routing (~3 min)

- [ ] No sensitive files accidentally committed: `git ls-files | grep -E 'finances\.md|secrets\.md|\.env'` — should return empty
- [ ] No hardcoded usernames in tracked files: `grep -r 'Users/' knowledge/ .claude/memory/ | grep -v .git` — should return empty
- [ ] SESSION_HANDOFF.md is ≤ 80 lines (check with `wc -l .claude/status/SESSION_HANDOFF.md`)
- [ ] STATUS.md `last_updated` field is within 7 days

---

## C. SDLC Gate (~3 min)

- [ ] Check post-commit-sdlc-audit log — last 5 entries all PASS (no VIOLATION lines)
- [ ] If violations exist: create plan docs and/or test fixtures for flagged hooks
- [ ] No bootstrap-exempt fixtures added this week without a plan doc

```bash
# Check recent SDLC audit entries (if log exists)
if [ -f "{{PROJECT_PATH}}/.claude/logs/sdlc-audit.log" ]; then
  tail -20 "{{PROJECT_PATH}}/.claude/logs/sdlc-audit.log"
else
  echo "No sdlc-audit.log found — hook may not be wired yet"
fi
```

---

## D. Memory Freshness / Silent Drift Detection (~5 min)

Docs claiming things that no longer exist. Run this weekly for the rest.

- [ ] STATUS.md — every open decision still reflects reality
- [ ] goals.md — milestone dates are still current
- [ ] SESSION_HANDOFF.md — IMMEDIATE NEXT TASK is still the right next task (not stale from 2 weeks ago)
- [ ] `.claude/agents/` dispatch map — every agent resolves to a file or plugin that exists
- [ ] `.claude/commands/` — no commands reference scripts or files that have been renamed/deleted
- [ ] `.claude/hooks/` — no hooks reference paths that have been moved

```bash
# Check for references to files that no longer exist
python3 -c "
import os, re
from pathlib import Path

proj = Path('{{PROJECT_PATH}}')
issues = []

for md_file in proj.glob('.claude/**/*.md'):
    text = md_file.read_text(errors='ignore')
    # Find path-like references
    for match in re.finditer(r'{{PROJECT_PATH}}/([^\s\`\'\"]+)', text):
        ref = proj / match.group(1)
        if not ref.exists() and not str(ref).endswith('*'):
            issues.append(f'{md_file.relative_to(proj)}: references missing {match.group(1)}')

if issues:
    print('DRIFT DETECTED:')
    for i in issues[:10]:
        print(f'  {i}')
else:
    print('OK — no obvious drift detected')
"
```

---

## E. Scratch Hygiene (~2 min)

- [ ] `.claude/scratch/` — no stale scratchpads older than 7 days
- [ ] Only `AGENT_STATE.json` and `SCRATCHPAD.md` should be present between sessions
- [ ] `git status` — no surprise untracked files in sensitive dirs (`.claude/memory/`, `knowledge/`)

```bash
# Check scratch directory
python3 -c "
import os
from pathlib import Path
from datetime import datetime, timedelta

scratch = Path('{{PROJECT_PATH}}/.claude/scratch')
if not scratch.exists():
    print('Scratch dir not found')
else:
    stale = []
    for f in scratch.iterdir():
        if f.is_file():
            age = datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)
            if age > timedelta(days=7) and f.name not in ('AGENT_STATE.json', 'SCRATCHPAD.md'):
                stale.append(f'{f.name} ({age.days}d old)')
    if stale:
        print('STALE SCRATCH FILES:')
        for s in stale: print(f'  {s}')
    else:
        print('OK — scratch is clean')
"
```

---

## Weekly Sign-off

Date: ____  Checked by: {{USER_NAME}}  Status: OK / ISSUES FOUND: ____
