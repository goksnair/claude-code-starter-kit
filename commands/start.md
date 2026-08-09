---
description: "Session start — 7-check health gate, loads SESSION_HANDOFF context, creates SCRATCHPAD, prints briefing"
argument-hint: ""
---

# /start

Session start sequence. Run this first every session.

## Step 1 — Health gate (7 checks)

```bash
python3 -c "
import json, os, subprocess
from datetime import datetime

today = datetime.now().date()
proj = subprocess.check_output(['git','rev-parse','--show-toplevel'], text=True).strip()
results = []

def age(path):
    try: return (today - datetime.fromtimestamp(os.path.getmtime(path)).date()).days
    except: return 999

# SH-01: SESSION_HANDOFF freshness
d = age(f'{proj}/.claude/status/SESSION_HANDOFF.md')
s = 'GREEN' if d==0 else 'YELLOW' if d==1 else 'RED'
results.append((s,'SH-01','SESSION_HANDOFF.md',f'{d}d old','Update .claude/status/SESSION_HANDOFF.md' if s=='RED' else ''))

# SH-02: CURRENT_STATE freshness
d = age(f'{proj}/.claude/status/CURRENT_STATE.md')
s = 'GREEN' if d==0 else 'YELLOW' if d<=1 else 'RED'
results.append((s,'SH-02','CURRENT_STATE.md',f'{d}d old','Update .claude/status/CURRENT_STATE.md' if s=='RED' else ''))

# SH-03: MILESTONE_REGISTRY freshness
d = age(f'{proj}/.claude/status/MILESTONE_REGISTRY.json')
s = 'GREEN' if d<=7 else 'YELLOW' if d<=14 else 'RED'
results.append((s,'SH-03','MILESTONE_REGISTRY.json',f'{d}d old','Update .claude/status/MILESTONE_REGISTRY.json' if s=='RED' else ''))

# SH-04: Git branch vs expected
branch = subprocess.check_output(['git','-C',proj,'branch','--show-current'],text=True).strip()
expected = None
try:
    with open(f'{proj}/.claude/scratch/AGENT_STATE.json') as f:
        expected = json.load(f).get('expected_branch')
except: pass
if not branch: s,msg = 'RED','git checkout [branch]'
elif expected and branch != expected: s,msg = 'YELLOW',f'Expected {expected}, on {branch}'
else: s,msg = 'GREEN',''
results.append((s,'SH-04',f'Branch: {branch}',f'expected:{expected or \"any\"}',msg))

# SH-05: AGENT_STATE integrity
try:
    with open(f'{proj}/.claude/scratch/AGENT_STATE.json') as f:
        d = json.load(f)
    status = d.get('active_task',{}).get('status','')
    if status == 'in_progress': s,msg = 'YELLOW','Orphaned task — update status or complete it'
    elif '_schema_version' not in d: s,msg = 'YELLOW','Missing schema_version field'
    else: s,msg = 'GREEN',''
except: s,msg = 'YELLOW','AGENT_STATE.json missing or invalid'
results.append((s,'SH-05','AGENT_STATE.json','',msg))

# SH-06: SSOT drift
try:
    import glob as glb
    ssot_candidates = glb.glob(f'{proj}/knowledge/**/*.md', recursive=True)
    drifted = [os.path.basename(f) for f in ssot_candidates if age(f) < 2]
    s = 'YELLOW' if drifted else 'GREEN'
    results.append((s,'SH-06','SSOT drift',f'{len(drifted)} recently modified','Read updated SSOTs before work' if drifted else ''))
except: results.append(('GREEN','SH-06','SSOT drift','n/a',''))

# SH-07: Scratch hygiene
try: n = len([x for x in os.listdir(f'{proj}/.claude/scratch') if not x.startswith('.')])
except: n = 0
s = 'GREEN' if n<=5 else 'YELLOW' if n<=10 else 'RED'
results.append((s,'SH-07','Scratch files',f'{n} files','Run /end to clean scratch' if s=='RED' else ''))

# Print report
reds = [r for r in results if r[0]=='RED']
yellows = [r for r in results if r[0]=='YELLOW']
print()
for status,check,item,detail,fix in results:
    icon = 'GREEN' if status=='GREEN' else 'YELLOW' if status=='YELLOW' else 'RED'
    print(f'  [{icon}] {check}: {item} ({detail})')
    if fix and status in ('YELLOW','RED'): print(f'     -> {fix}')

if reds:
    print()
    print('RED items detected — resolve before domain work:')
    for r in reds: print(f'   {r[1]}: {r[4]}')
elif yellows:
    print()
    print('YELLOW warnings — can proceed but address today')
else:
    print()
    print('All checks GREEN — proceed to domain work')
"
```

Evaluate each check:

- **SH-01**: GREEN=today, YELLOW=yesterday, RED=2+ days — **hard block** (see below)
- **SH-02**: GREEN=today/yesterday, RED=2+ days
- **SH-03**: GREEN=within 7 days, YELLOW=8–14 days, RED=15+ days
- **SH-04**: GREEN=on expected branch, YELLOW=mismatch, RED=detached HEAD
- **SH-05**: GREEN=valid schema, YELLOW=orphaned task or missing field, RED=file missing/invalid
- **SH-06**: GREEN=no recent SSOT changes, YELLOW=files changed today (re-read before work)
- **SH-07**: GREEN=0–5 files, YELLOW=6–10, RED=11+

**SH-01 RED — hard block:**

If SESSION_HANDOFF.md is 2+ days old, print this and STOP:

```text
SESSION HANDOFF STALE — [N] days since last update
SESSION_HANDOFF.md was last updated [date].

Before continuing, choose:
  A) type "acknowledge" — load stale context and proceed (context risk accepted)
  B) type "update handoff" — reconstruct from git log before loading

Waiting for your response.
```

- If user types `acknowledge`: proceed to Step 2, note stale context in SCRATCHPAD.md
- If user types `update handoff`: run `git log --oneline -20`, reconstruct the COMPLETED THIS SESSION block from commits, write to SESSION_HANDOFF.md, then proceed to Step 2

## Step 2 — Load session context (parallel reads)

Read simultaneously:
1. `.claude/status/SESSION_HANDOFF.md` (full file)
2. Run `git log --oneline -5`

## Step 2b — Wiki gap check (MANDATORY — every session open)

After reading SESSION_HANDOFF.md in Step 2, scan the most recent COMPLETED THIS SESSION block for any confirmed facts (figures, rates, vendor decisions, locked assumptions, timeline dates, policy changes) that do NOT already appear in a `knowledge/wiki/` page.

These are facts that survived to SESSION_HANDOFF but may have been lost from the wiki if the previous session ended mid-compaction or /end Step 4b was incomplete.

For each orphaned fact:
1. Identify the correct wiki page (routing table in CLAUDE.md / memory-routing.md)
2. Write it there immediately
3. Print: `✓ Wiki gap fixed: [fact] → [wiki page]`

If no gaps: print `✓ Wiki gap check: COMPLETED block fully reflected in wiki`

**Why**: /end Step 4b catches facts from the live context. This step catches anything that slipped through — facts named in the COMPLETED block but never written to the queryable knowledge layer. Running it at session open means every session self-heals before work begins.

## Step 3 — Create SCRATCHPAD.md

Write `.claude/scratch/SCRATCHPAD.md`:

```markdown
# SCRATCHPAD — [YYYY-MM-DD]
*Intra-session working memory. Deleted by /end. Never committed.*

## Files Read
<!-- Add: [path] — [key finding] -->

## Decisions Made
<!-- Add: [decision] — [rationale] -->

## Current Task
<!-- Update as you progress -->

## Next Step
<!-- What to do next if session interrupted -->
```

## Step 4 — Update AGENT_STATE.json

```bash
python3 -c "
import json, random, string, subprocess
from datetime import datetime
proj = subprocess.check_output(['git','rev-parse','--show-toplevel'], text=True).strip()
state_file = f'{proj}/.claude/scratch/AGENT_STATE.json'
try:
    with open(state_file) as f: state = json.load(f)
except: state = {'_schema_version': '1.0', 'completed_tasks': []}

branch = subprocess.check_output(['git','-C',proj,'branch','--show-current'], text=True).strip()
suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
state['session_id'] = f\"{datetime.now().strftime('%Y-%m-%d')}-{suffix}\"
state['expected_branch'] = branch
state['session_turn_count'] = 0
if 'completed_tasks' not in state: state['completed_tasks'] = []
if state.get('active_task', {}).get('status') == 'idle' or not state.get('active_task'):
    state['active_task'] = {'agent': None, 'task_type': None, 'started_at': None,
        'status': 'idle', 'input_file': None, 'output_file': None,
        'human_gate': None, 'human_approval_note': None, 'commit_sha': None, 'routing_log': None}

with open(state_file + '.tmp', 'w') as f: json.dump(state, f, indent=2)
import shutil; shutil.move(state_file + '.tmp', state_file)
"
```

## Step 5 — Print session briefing

```
SESSION START — [YYYY-MM-DD] | [branch] | [health status]

WHERE WE LEFT OFF
[Summarize the most recent COMPLETED THIS SESSION block from SESSION_HANDOFF.md — 3-4 bullets]

IMMEDIATE NEXT TASK
[Copy exact IMMEDIATE NEXT TASK from SESSION_HANDOFF.md verbatim]

OPEN ITEMS (top 3 by priority)
[Top 3 open items — highest priority first]

SCRATCHPAD ready. Recent commits:
[git log --oneline -5 output]

Type /work [task] to begin — or /health for full diagnostic.
```

Working directory: detected automatically via git rev-parse
